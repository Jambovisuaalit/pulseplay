// Explicit PGlite integration suite. This does not satisfy the hosted release gate.
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, readdir, rm, stat, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

test('backup CLI restores a committed snapshot across three processes and refuses overwrite', async () => {
  assert.ok(process.env.PGLITE_MODULE, 'Supply the isolated CI PGlite installation');
  const directory = await mkdtemp(path.join(tmpdir(), 'urakkaluotsi-pr12-runner-'));
  const backupFile = path.join(directory, 'private', 'backup.json');
  const runner = fileURLToPath(new URL('./preview-backup-restore.mjs', import.meta.url));
  const preload = new URL('./helpers/pr12-pglite-transport.mjs', import.meta.url).href;
  const env = {
    ...process.env, TP_SUPABASE_URL: 'https://kzcmzelxydrhxxhcmmua.supabase.co',
    TP_SUPABASE_SECRET_KEY: 'synthetic-local-runner-only', PREVIEW_E2E_PERSIST_SYNTHETIC: 'yes',
    PREVIEW_E2E_BACKUP_FILE: backupFile, PR12_QA_DATABASE_DIRECTORY: path.join(directory, 'postgres'),
  };
  const run = action => spawnSync(process.execPath, ['--experimental-strip-types', '--import', preload, runner, action], { env, cwd: directory, encoding: 'utf8', timeout: 60000 });
  try {
    for (const action of ['backup', 'restore', 'verify']) {
      const result = run(action);
      assert.equal(result.status, 0, `Synthetic ${action} runner failed: ${result.error?.message || ''}\n${result.stdout}\n${result.stderr}`);
    }
    assert.equal((await stat(backupFile)).mode & 0o077, 0);
    const original = await readFile(backupFile, 'utf8'), backup = JSON.parse(original);
    assert.notEqual(run('backup').status, 0, 'A new backup must not overwrite an existing private artifact');
    assert.equal(await readFile(backupFile, 'utf8'), original);
    const reports = await readdir(path.join(directory, 'qa-output'));
    assert.equal(reports.length, 1);
    const report = JSON.parse(await readFile(path.join(directory, 'qa-output', reports[0]), 'utf8'));
    assert.equal(report.status, 'PASS');
    assert.equal(report.counts.events, 1);
    assert.equal(report.history_and_measurements_exact, true);
    assert.equal(report.vercel_restart_persistence, 'NOT_TESTED');
    assert.equal(run('verify').status, 0, 'A fresh read-only verification must be repeatable');
    assert.equal((await readdir(path.join(directory, 'qa-output'))).length, 2);
    const duplicate = run('restore');
    assert.notEqual(duplicate.status, 0);
    assert.match(duplicate.stderr, /already exists/);
    backup.row.state.revision++;
    await writeFile(backupFile, JSON.stringify(backup));
    const corrupt = run('restore');
    assert.notEqual(corrupt.status, 0);
    assert.match(corrupt.stderr, /checksum mismatch/);
    await writeFile(backupFile,original);
    const cleanup=run('cleanup');
    assert.equal(cleanup.status,0,`Owned cleanup failed: ${cleanup.stderr}`);
    const {PGlite}=await import(process.env.PGLITE_MODULE),db=new PGlite(env.PR12_QA_DATABASE_DIRECTORY);
    try{assert.equal((await db.query('select count(*)::int as n from public.urakkaluotsi_ops_state')).rows[0].n,0);}finally{await db.close();}
  } finally {
    // These are exclusively local synthetic fixtures; never retain mock-hosted reports.
    await rm(directory, { recursive: true, force: true });
  }
});

test('a lost insert acknowledgement leaves a durable recovery journal for scoped cleanup', async () => {
  assert.ok(process.env.PGLITE_MODULE, 'Supply the isolated CI PGlite installation');
  const directory = await mkdtemp(path.join(tmpdir(), 'urakkaluotsi-pr12-recovery-'));
  const backupFile = path.join(directory, 'private', 'backup.json');
  const runner = fileURLToPath(new URL('./preview-backup-restore.mjs', import.meta.url));
  const preload = new URL('./helpers/pr12-pglite-transport.mjs', import.meta.url).href;
  const env = {
    ...process.env, TP_SUPABASE_URL: 'https://kzcmzelxydrhxxhcmmua.supabase.co',
    TP_SUPABASE_SECRET_KEY: 'synthetic-local-runner-only', PREVIEW_E2E_PERSIST_SYNTHETIC: 'yes',
    PREVIEW_E2E_BACKUP_FILE: backupFile, PR12_QA_DATABASE_DIRECTORY: path.join(directory, 'postgres'),
  };
  const run = (action, extra = {}) => spawnSync(process.execPath,
    ['--experimental-strip-types', '--import', preload, runner, action],
    { env: { ...env, ...extra }, cwd: directory, encoding: 'utf8', timeout: 60000 });
  try {
    const failed = run('backup', { PR12_QA_LOSE_INSERT_ACK: 'yes' });
    assert.notEqual(failed.status, 0);
    const recoveryFile = backupFile + '.recovery.json';
    const original = await readFile(recoveryFile, 'utf8'), recovery = JSON.parse(original);
    assert.equal((await stat(recoveryFile)).mode & 0o077, 0, 'Recovery intent must remain private');
    assert.ok(failed.stdout.includes(recovery.run_id), 'The failed run must remain traceable');
    assert.ok(!failed.stderr.includes('synthetic-sensitive-transport-detail'), 'Transport details must not enter logs');
    assert.equal(await readFile(backupFile, 'utf8'), '', 'An unconfirmed source is not a successful backup');
    const { PGlite } = await import(process.env.PGLITE_MODULE);
    let db = new PGlite(env.PR12_QA_DATABASE_DIRECTORY);
    try {
      const rows = (await db.query('select workspace_id,state from public.urakkaluotsi_ops_state')).rows;
      assert.equal(rows.length, 1, 'The source insert really committed before its acknowledgement was lost');
      assert.equal(rows[0].workspace_id, recovery.source_workspace);
      await db.query('insert into public.urakkaluotsi_ops_state values ($1,1,$2)', ['unrelated-workspace', rows[0].state]);
    } finally { await db.close(); }
    await writeFile(backupFile, original);
    assert.notEqual(run('restore').status, 0, 'A recovery intent must never be accepted as a confirmed backup');
    await writeFile(backupFile, '');
    await writeFile(recoveryFile, 'synthetic-sensitive-transport-detail');
    const malformed = run('cleanup-recovery');
    assert.notEqual(malformed.status, 0);
    assert.ok(!malformed.stderr.includes('synthetic-sensitive-transport-detail'));
    recovery.row.state.revision++;
    await writeFile(recoveryFile, JSON.stringify(recovery));
    const corrupt = run('cleanup-recovery');
    assert.notEqual(corrupt.status, 0);
    assert.match(corrupt.stderr, /checksum mismatch/);
    await writeFile(recoveryFile, original);
    db = new PGlite(env.PR12_QA_DATABASE_DIRECTORY);
    try {
      await db.query("update public.urakkaluotsi_ops_state set state=jsonb_set(state,'{revision}',to_jsonb((state->>'revision')::int+1)) where workspace_id=$1", [recovery.source_workspace]);
    } finally { await db.close(); }
    const changed = run('cleanup-recovery');
    assert.notEqual(changed.status, 0);
    assert.match(changed.stderr, /changed workspace/);
    db = new PGlite(env.PR12_QA_DATABASE_DIRECTORY);
    try {
      await db.query('update public.urakkaluotsi_ops_state set state=$2 where workspace_id=$1', [recovery.source_workspace, JSON.parse(original).row.state]);
    } finally { await db.close(); }
    const cleanup = run('cleanup-recovery');
    assert.equal(cleanup.status, 0, `Recovery cleanup failed: ${cleanup.stderr}`);
    db = new PGlite(env.PR12_QA_DATABASE_DIRECTORY);
    try {
      assert.deepEqual((await db.query('select workspace_id from public.urakkaluotsi_ops_state')).rows,
        [{ workspace_id: 'unrelated-workspace' }]);
    } finally { await db.close(); }
  } finally { await rm(directory, { recursive: true, force: true }); }
});
