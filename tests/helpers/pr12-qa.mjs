import assert from 'node:assert/strict';
import { emptyState } from '../../lib/domain/model.ts';
import { command } from '../../lib/domain/commands.ts';
import { contentHash, snapshot } from '../../lib/domain/workflow.ts';

export const PROJECT_REF = 'kzcmzelxydrhxxhcmmua';
const arrays = ['clients', 'profiles', 'notices', 'assessments', 'digests', 'events'];

export function verifyPreviewTarget(deployment, status, origin) {
  assert.ok(deployment.environment === 'Preview – tenderpulse', 'Refusing any environment other than the selected tenderpulse Preview');
  assert.ok(/^[a-f0-9]{40}$/.test(deployment.sha || ''), 'Missing deployment source commit');
  assert.ok(status.state === 'success' && status.environment_url === origin, 'Preview URL must match the successful GitHub deployment');
}

export function supabaseConfig(env = process.env) {
  const origin = env.TP_SUPABASE_URL;
  const key = env.TP_SUPABASE_SECRET_KEY;
  assert.ok(origin === `https://${PROJECT_REF}.supabase.co`, 'Use only the documented Urakkaluotsi Preview project');
  // Proxy-backed credentials may be placeholders; do not inspect or log them.
  assert.ok(typeof key === 'string' && key.length > 0, 'Missing Preview Supabase server-key binding');
  return { origin, key };
}

export function dataApi(config, fetcher = fetch) {
  return async (workspace, method = 'GET', row) => {
    assert.ok(/^[a-z0-9][a-z0-9_-]{2,79}$/.test(workspace), 'Invalid isolated workspace');
    const query = method === 'GET' ? `?workspace_id=eq.${workspace}&select=workspace_id,storage_version,state` : '';
    let response;
    try {
      response = await fetcher(`${config.origin}/rest/v1/urakkaluotsi_ops_state${query}`, {
        method, redirect: 'error', cache: 'no-store', signal: AbortSignal.timeout(20_000),
        headers: { apikey: config.key, 'content-type': 'application/json', Prefer: 'return=representation' },
        ...(row === undefined ? {} : { body: JSON.stringify(row) }),
      });
    } catch { throw new Error(`Preview Data API ${method} transport failed; details omitted`); }
    assert.ok(response.ok, `Preview Data API ${method} failed (HTTP ${response.status}); response body omitted`);
    let rows;
    try { rows = await response.json(); }
    catch { throw new Error(`Preview Data API ${method} returned invalid JSON; response body omitted`); }
    assert.ok(Array.isArray(rows) && rows.length <= 1, 'Unexpected Preview Data API acknowledgement');
    return rows[0] ?? null;
  };
}

export async function cleanupWorkspace(config, workspace, runId, version, fetcher = fetch, allowAbsent = false) {
  let response;
  try {
    response = await fetcher(`${config.origin}/rest/v1/rpc/urakkaluotsi_cleanup_e2e`, {
      method: 'POST', redirect: 'error', signal: AbortSignal.timeout(20_000),
      headers: { apikey: config.key, 'content-type': 'application/json' },
      body: JSON.stringify({ p_workspace: workspace, p_run: runId, p_version: version }),
    });
  } catch { throw new Error('Scoped Preview cleanup transport failed; details omitted'); }
  assert.ok(response.ok, `Scoped Preview cleanup failed (HTTP ${response.status}); apply the test-only cleanup SQL or resolve the ownership/version conflict`);
  let removed;
  try { removed = await response.json(); }
  catch { throw new Error('Scoped Preview cleanup returned invalid JSON; response body omitted'); }
  assert.ok(removed === true || (allowAbsent && removed === false), 'Scoped cleanup did not acknowledge deletion');
  return removed;
}

export function validateRow(row) {
  assert.ok(row && Number.isSafeInteger(row.storage_version) && row.storage_version > 0, 'Invalid stored version');
  const state = row.state;
  assert.ok(state?.schema_version === 1 && state.mode === 'SIMULATION', 'Only simulation snapshots are allowed');
  assert.ok(Number.isSafeInteger(state.revision) && state.revision >= 0 && arrays.every(key => Array.isArray(state[key])), 'Invalid workflow snapshot');
  return row;
}

function createArtifact(row, runId, format) {
  validateRow(row);
  assert.ok(row.workspace_id === `pr12-e2e-source-${runId}`, 'Back up only this run’s synthetic source workspace');
  const backup = {
    format, project_ref: PROJECT_REF,
    run_id: runId, created_at: new Date().toISOString(),
    source_workspace: row.workspace_id, target_workspace: `pr12-e2e-restore-${runId}`,
    row: structuredClone(row),
  };
  return { ...backup, sha256: contentHash(backup) };
}

export const createBackup = (row, runId) => createArtifact(row, runId, 'urakkaluotsi-pr12-backup-v1');
export const createRecovery = (row, runId) => createArtifact(row, runId, 'urakkaluotsi-pr12-recovery-v1');

function validateArtifact(value, format) {
  assert.ok(value && typeof value === 'object' && !Array.isArray(value), 'Invalid backup document');
  const { sha256, ...backup } = value;
  assert.ok(typeof sha256 === 'string' && sha256 === contentHash(backup), 'Backup checksum mismatch');
  assert.ok(backup.format === format && backup.project_ref === PROJECT_REF, 'Unexpected backup format or project');
  assert.ok(/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/.test(backup.run_id), 'Invalid backup run identifier');
  assert.ok(backup.source_workspace === `pr12-e2e-source-${backup.run_id}` && backup.target_workspace === `pr12-e2e-restore-${backup.run_id}`, 'Restore target must be a separate synthetic workspace');
  validateRow(backup.row);
  assert.ok(backup.row.workspace_id === backup.source_workspace, 'Backup source mismatch');
  return value;
}

export const validateBackup = value => validateArtifact(value, 'urakkaluotsi-pr12-backup-v1');
export const validateRecovery = value => validateArtifact(value, 'urakkaluotsi-pr12-recovery-v1');

export function restoredRow(backup) {
  validateBackup(backup);
  return { ...structuredClone(backup.row), workspace_id: backup.target_workspace };
}

export function verifyRestoredRow(backup, actual) {
  const expected = restoredRow(backup);
  validateRow(actual);
  // Canonical hashes tolerate JSONB key ordering but include every field.
  assert.ok(contentHash(actual) === contentHash(expected), 'Restored snapshot/version differs from the independent backup');
}

export function verifyRace(before, after, markers, statuses) {
  assert.deepEqual([...statuses].sort((a, b) => a - b), [200, 409], 'Exactly one same-revision HTTP writer must succeed');
  assert.ok(after.revision === before.revision + 1, 'Race must advance the workflow revision exactly once');
  assert.ok(after.clients.length === before.clients.length + 1, 'Race must persist exactly one new client');
  const winner = statuses.indexOf(200), loser = 1 - winner;
  assert.ok(after.clients.filter(client => client.name === markers[winner]).length === 1, 'Winning write missing or duplicated');
  assert.ok(after.clients.every(client => client.name !== markers[loser]), 'Losing write unexpectedly persisted');
  assert.ok(before.clients.every(client => after.clients.some(current => contentHash(current) === contentHash(client))), 'Race lost or changed a pre-existing client');
  return { winner, loser };
}

export function syntheticBackupState(runId, now = Date.now()) {
  const state = emptyState();
  const run = input => command(state, { ...input, expected_revision: state.revision }, 'PR12-SYNTHETIC', now);
  run({ action: 'client', name: `E2E-SYNTHETIC-BACKUP-${runId}`, delivery_email: 'backup-test@example.invalid' });
  const client_id = state.clients[0].id;
  run({ action: 'profile', client_id, services: ['Synthetic refurbishment'], regions: ['Uusimaa'], facts: [] });
  run({ action: 'notice', notice_id: '999999999', title: 'Synthetic backup fixture', buyer: 'Synthetic buyer', source_url: 'https://example.invalid/pr12-backup', deadline: new Date(now + 3 * 86400000).toISOString(), checked_at: new Date(now - 1000).toISOString(), cancelled: false, evidence: 'Synthetic fixture; not a real notice', missing: [] });
  run({ action: 'review', client_id, notice_version_id: state.notices[0].id, summary: 'Synthetic assessment', next_action: 'Synthetic review only', missing: ['Not a real tender'], coverage: 'PARTIAL' });
  run({ action: 'compose', client_id, assessment_ids: [state.assessments[0].id] });
  run({ action: 'approve', digest_id: state.digests[0].id, expected_hash: contentHash(snapshot(state, state.digests[0])) });
  run({ action: 'timer_start', client_id, phase: 'DELIVERY' });
  run({ action: 'timer_stop', session_id: state.measurements.work_sessions[0].id });
  return state;
}
