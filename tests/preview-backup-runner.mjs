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
  } finally {
    // These are exclusively local synthetic fixtures; never retain mock-hosted reports.
    await rm(directory, { recursive: true, force: true });
  }
});
