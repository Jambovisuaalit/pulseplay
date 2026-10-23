// Run backup, restore and verify as three separate Node processes. No DELETE/PATCH.
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { mkdir, open, readFile, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { contentHash } from '../lib/domain/workflow.ts';
import { createDatabaseStore } from '../lib/server/ops-database.ts';
import { PROJECT_REF, supabaseConfig, dataApi, createBackup, validateBackup, restoredRow, verifyRestoredRow, syntheticBackupState, cleanupWorkspace } from './helpers/pr12-qa.mjs';

async function loadBackup(filename) {
  assert.ok(((await stat(filename)).mode & 0o077) === 0, 'Backup file must be owner-only');
  return validateBackup(JSON.parse(await readFile(filename, 'utf8')));
}

async function main() {
  const action = process.argv[2], filename = process.env.PREVIEW_E2E_BACKUP_FILE;
  assert.ok(['backup', 'restore', 'verify', 'cleanup'].includes(action) && filename, 'Use backup|restore|verify|cleanup with PREVIEW_E2E_BACKUP_FILE');
  assert.ok(process.env.PREVIEW_E2E_PERSIST_SYNTHETIC === 'yes', 'Explicit opt-in required for two persistent synthetic workspaces');
  const config = supabaseConfig(), database = dataApi(config);
  await mkdir('qa-output', { recursive: true });
  if (action === 'backup') {
    await mkdir(path.dirname(filename), { recursive: true, mode: 0o700 });
    // Reserve the artifact before creating remote data; never overwrite it.
    const file = await open(filename, 'wx', 0o600);
    try {
      const runId = randomUUID(), state = syntheticBackupState(runId), workspace = `pr12-e2e-source-${runId}`;
      await cleanupWorkspace(config,`preview-e2e-probe-${runId}`,runId,1,fetch,true);
      const source = { workspace_id: workspace, storage_version: 1, state };
      const written = await database(workspace, 'POST', source);
      assert.ok(contentHash(written) === contentHash(source), 'Synthetic source insert acknowledgement mismatch');
      const row = await database(workspace);
      assert.ok(contentHash(row) === contentHash(source), 'Synthetic source readback mismatch');
      const backup = createBackup(row, runId);
      await file.writeFile(JSON.stringify(backup, null, 2) + '\n');
      await file.sync();
      console.log(`PASS separate backup artifact; run ${runId}; source ${workspace}`);
    } finally { await file.close(); }
    return;
  }
  const backup = await loadBackup(filename);
  if(action==='cleanup'){
    for(const workspace of [backup.target_workspace,backup.source_workspace]){
      const row=await database(workspace);
      if(row){
        const expected=workspace===backup.source_workspace?backup.row:restoredRow(backup);
        assert.ok(contentHash(row)===contentHash(expected),'Cleanup refuses a changed workspace');
        await cleanupWorkspace(config,workspace,backup.run_id,row.storage_version);
      }
      assert.ok(await database(workspace)===null,'Owned backup workspace must be absent after cleanup');
    }
    await writeFile(`qa-output/pr12-backup-cleanup-${backup.run_id}.json`,JSON.stringify({status:'PASS',run_id:backup.run_id,owned_workspaces_removed:[backup.source_workspace,backup.target_workspace]},null,2)+'\n',{flag:'wx',mode:0o600});
    console.log('PASS scoped cleanup of this backup run only');return;
  }
  if (action === 'restore') {
    assert.ok(await database(backup.target_workspace) === null, 'Restore target already exists; refusing to overwrite');
    const source = await database(backup.source_workspace);
    assert.ok(contentHash(source) === contentHash(backup.row), 'Source changed after backup; isolate the run before retrying');
    // Separate committed INSERT, not a rollback exercise or in-place repair.
    verifyRestoredRow(backup, await database(backup.target_workspace, 'POST', restoredRow(backup)));
    verifyRestoredRow(backup, await database(backup.target_workspace));
    console.log(`PASS committed restore from disk into ${backup.target_workspace}; start verify in a new process`);
    return;
  }
  verifyRestoredRow(backup, await database(backup.target_workspace));
  const store = createDatabaseStore({ ...config, workspace: backup.target_workspace });
  const loaded = await store.readState();
  assert.ok(contentHash(loaded) === contentHash(backup.row.state), 'Fresh application adapter did not load the exact restored state');
  assert.ok(contentHash(await database(backup.source_workspace)) === contentHash(backup.row), 'Restore unexpectedly changed the source');
  const verificationId = randomUUID();
  const report = {
    status: 'PASS', scope: 'hosted-separate-backup-and-committed-restore', run_id: backup.run_id,
    verification_id: verificationId,
    completed_at: new Date().toISOString(), project_ref: PROJECT_REF, source_workspace: backup.source_workspace,
    target_workspace: backup.target_workspace, backup_sha256: backup.sha256, state_sha256: contentHash(loaded),
    storage_version: backup.row.storage_version, revision: loaded.revision,
    counts: Object.fromEntries(['clients', 'profiles', 'notices', 'assessments', 'digests', 'events'].map(key => [key, loaded[key].length])),
    history_and_measurements_exact: true, fresh_node_process_and_adapter_read: true,
    vercel_restart_persistence: 'NOT_TESTED', full_project_disaster_recovery: 'NOT_TESTED',
    synthetic_workspaces_verified: 2,cleanup:'REQUIRES_SEPARATE_CLEANUP_COMMAND',
  };
  const reportPath = `qa-output/pr12-backup-restore-${backup.run_id}-${verificationId}.json`;
  await writeFile(reportPath, JSON.stringify(report, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
  console.log(`PASS fresh-process restore verification; evidence: ${reportPath}`);
}
main().catch(error => { console.error('FAIL Preview backup/restore:', error.message); process.exitCode = 1; });
