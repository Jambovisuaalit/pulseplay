import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { emptyState } from '../lib/domain/model.ts';
import { contentHash } from '../lib/domain/workflow.ts';
import { createBackup, validateBackup, restoredRow, verifyRestoredRow, verifyRace, dataApi, supabaseConfig, syntheticBackupState, verifyPreviewTarget } from './helpers/pr12-qa.mjs';

test('hosted runner rejects production deployments and unrelated Preview URLs', () => {
  const deployment = { environment: 'Preview – tenderpulse', sha: 'a'.repeat(40) };
  const origin = 'https://synthetic-preview.vercel.app';
  const status = { state: 'success', environment_url: origin };
  verifyPreviewTarget(deployment, status, origin);
  assert.throws(() => verifyPreviewTarget({ ...deployment, environment: 'Production – tenderpulse' }, status, origin), /Preview/);
  assert.throws(() => verifyPreviewTarget(deployment, status, 'https://other-preview.vercel.app'), /match/);
  assert.throws(() => verifyPreviewTarget(deployment, { ...status, state: 'failure' }, origin), /successful/);
});

test('independent backup preserves JSONB snapshot, history and measurements', () => {
  const runId = randomUUID(), state = syntheticBackupState(runId);
  assert.equal(state.digests[0].status, 'APPROVED');
  assert.equal(state.events[0].type, 'APPROVED');
  assert.ok(state.measurements.work_sessions[0].ended_at);
  const backup = createBackup({ workspace_id: `pr12-e2e-source-${runId}`, storage_version: 3, state }, runId);
  const fromDisk = validateBackup(JSON.parse(JSON.stringify(backup)));
  const restored = restoredRow(fromDisk);
  restored.state = Object.fromEntries(Object.entries(restored.state).reverse());
  verifyRestoredRow(fromDisk, restored);
  assert.notEqual(restored.workspace_id, backup.source_workspace);
  assert.equal(contentHash(restored.state), contentHash(state));
  restored.state.events.length = 0;
  assert.throws(() => verifyRestoredRow(fromDisk, restored), /differs/);
});

test('backup corruption and retargeting cannot silently change the restored data', () => {
  const runId = randomUUID();
  const backup = createBackup({ workspace_id: `pr12-e2e-source-${runId}`, storage_version: 1, state: emptyState() }, runId);
  const corrupted = structuredClone(backup); corrupted.row.state.revision++;
  assert.throws(() => validateBackup(corrupted), /checksum/);
  const retargeted = structuredClone(backup); retargeted.target_workspace = 'production-workspace';
  const { sha256: _old, ...unsigned } = retargeted;
  retargeted.sha256 = contentHash(unsigned);
  assert.throws(() => validateBackup(retargeted), /separate synthetic/);
  const wrongProject = structuredClone(backup); wrongProject.project_ref = 'different-project';
  const { sha256: _other, ...otherUnsigned } = wrongProject;
  wrongProject.sha256 = contentHash(otherUnsigned);
  assert.throws(() => validateBackup(wrongProject), /project/);
});

test('HTTP race evidence rejects lost clients, duplicate writes and wrong revisions', () => {
  const before = { revision: 4, clients: [{ id: 'existing', name: 'Existing' }] };
  const after = { revision: 5, clients: [...before.clients, { id: 'new', name: 'writer-B' }] };
  assert.equal(verifyRace(before, after, ['writer-A', 'writer-B'], [409, 200]).winner, 1);
  assert.throws(() => verifyRace(before, after, ['writer-A', 'writer-B'], [200, 200]));
  assert.throws(() => verifyRace(before, { ...after, revision: 6 }, ['writer-A', 'writer-B'], [409, 200]), /exactly once/);
  assert.throws(() => verifyRace(before, { ...after, clients: [{ id: 'different', name: 'Changed' }, after.clients[1]] }, ['writer-A', 'writer-B'], [409, 200]), /pre-existing/);
});

test('Preview Data API scopes reads and forbids redirect credential forwarding', async () => {
  const config = supabaseConfig({ TP_SUPABASE_URL: 'https://kzcmzelxydrhxxhcmmua.supabase.co', TP_SUPABASE_SECRET_KEY: 'synthetic-proxy-binding' });
  let calls = 0;
  const database = dataApi(config, async (url, init) => {
    calls++;
    assert.equal(new URL(url).searchParams.get('workspace_id'), 'eq.pr12-test');
    assert.equal(init.redirect, 'error'); assert.equal(init.cache, 'no-store');
    assert.equal(init.headers.apikey, 'synthetic-proxy-binding');
    return Response.json([]);
  });
  assert.equal(await database('pr12-test'), null);
  await assert.rejects(database('pr12-test&select=*'));
  assert.equal(calls, 1);
  assert.throws(() => supabaseConfig({ TP_SUPABASE_URL: 'https://other-project.supabase.co', TP_SUPABASE_SECRET_KEY: 'synthetic' }), /Preview project/);
});
