// Protected Preview only. Credentials stay in environment bindings and headers.
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { supabaseConfig, dataApi, validateRow, verifyRace, verifyPreviewTarget } from './helpers/pr12-qa.mjs';

async function main() {
  const origin = (process.env.PREVIEW_E2E_URL || '').replace(/\/$/, '');
  const username = process.env.PREVIEW_E2E_USERNAME;
  const password = process.env.PREVIEW_E2E_PASSWORD;
  const bypass = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;
  const workspace = process.env.PREVIEW_E2E_WORKSPACE;
  const deploymentId = process.env.PREVIEW_E2E_DEPLOYMENT_ID;
  assert.ok(/^https:\/\/[a-z0-9-]+\.vercel\.app$/.test(origin) && username && password && bypass,
    'Missing protected Preview URL or E2E credential bindings');
  assert.ok(/^[a-z0-9][a-z0-9_-]{2,79}$/.test(workspace || '') && /preview|pr12|test/.test(workspace), 'Explicit isolated Preview workspace required');
  assert.ok(process.env.PREVIEW_E2E_PERSIST_SYNTHETIC === 'yes', 'Explicit opt-in required for persistent synthetic Preview records');
  assert.ok(/^\d+$/.test(deploymentId || ''), 'Explicit GitHub Preview deployment ID required');
  const database = dataApi(supabaseConfig());
  const deploymentApi = `https://api.github.com/repos/Jambovisuaalit/pulseplay/deployments/${deploymentId}`;
  async function metadata(url) {
    const response = await fetch(url, { redirect: 'error', cache: 'no-store', signal: AbortSignal.timeout(20_000), headers: { Accept: 'application/vnd.github+json', 'User-Agent': 'Urakkaluotsi-PR12-QA' } });
    assert.ok(response.ok, `GitHub deployment metadata unavailable (HTTP ${response.status})`);
    return response.json();
  }
  const deployment = await metadata(deploymentApi), statusesMetadata = await metadata(deploymentApi + '/statuses');
  verifyPreviewTarget(deployment, statusesMetadata[0] || {}, origin);
  const sourceCheck = spawnSync('git', ['diff', '--quiet', deployment.sha, '--', 'app', 'lib', 'middleware.ts', 'next.config.ts', 'package.json', 'package-lock.json', 'public', 'data', 'tsconfig.json'], { encoding: 'utf8' });
  assert.ok(sourceCheck.status === 0, 'Deployment source is missing locally or differs from the current application; verify/fetch the exact commit before testing');
  const runnerHead = spawnSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' });
  assert.ok(runnerHead.status === 0, 'Cannot record test runner source revision');
  const request = (path, init = {}) => fetch(origin + path, {
    ...init, redirect: 'manual', cache: 'no-store', signal: AbortSignal.timeout(20_000),
    headers: { 'x-vercel-protection-bypass': bypass, ...init.headers },
  });
  const runId = randomUUID(), markers = ['A', 'B'].map(label => `E2E-SYNTHETIC-${runId}-${label}`);
  // Keep partial/failed runs traceable without exposing authentication material.
  console.log('Hosted Preview synthetic test run:', runId);
  const checks = [];
  const pass = name => checks.push({ name, status: 'PASS' });
  assert.ok([401, 303, 307, 308].includes((await request('/api/ops')).status), 'Unauthenticated API access must be blocked');
  assert.equal((await request('/api/login', {
    method: 'POST', headers: { origin: 'https://evil.invalid', 'content-type': 'application/x-www-form-urlencoded' },
    body: 'username=unknown&password=unknown',
  })).status, 403, 'Cross-origin login must be blocked');
  pass('unauthenticated access and cross-origin login denied');

  async function login() {
    const response = await request('/api/login', {
      method: 'POST', headers: { origin, 'content-type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username, password }).toString(),
    });
    assert.equal(response.status, 303, 'Genuine Preview login must succeed');
    const raw = response.headers.get('set-cookie') || '';
    // Boolean assertions must not include cookies in failure output.
    assert.ok(/^tp_session=[^;]+;/.test(raw) && /HttpOnly/i.test(raw) && /SameSite=Lax/i.test(raw) && /Secure/i.test(raw), 'Missing secure operator session cookie');
    return raw.split(';')[0];
  }
  const cookies = [await login(), await login()];
  assert.ok(cookies[0] !== cookies[1], 'Concurrency test requires two independently issued sessions');
  pass('two separate authenticated Secure/HttpOnly/SameSite sessions');
  async function read(cookie) {
    const response = await request('/api/ops', { headers: { cookie } });
    assert.equal(response.status, 200, 'Authenticated state read failed');
    assert.ok((response.headers.get('cache-control') || '').includes('no-store'), 'Private state must not be cached');
    const state = await response.json();
    assert.ok(state.mode === 'SIMULATION' && Number.isSafeInteger(state.revision) && Array.isArray(state.clients), 'Expected a simulation workspace');
    return state;
  }
  const before = await read(cookies[0]);
  assert.equal((await read(cookies[1])).revision, before.revision, 'Both sessions must start with the same revision');
  const storedBefore = await database(workspace);
  if (storedBefore) validateRow(storedBefore);
  assert.equal(storedBefore?.state.revision ?? 0, before.revision, 'Preview app and expected Supabase workspace disagree');
  pass('authenticated Preview reads match the hosted Supabase workspace');

  const payloads = markers.map((name, index) => ({
    action: 'client', name, delivery_email: `preview-e2e-${runId}-${index}@example.invalid`, expected_revision: before.revision,
  }));
  const post = index => request('/api/ops', {
    method: 'POST', headers: { cookie: cookies[index], origin, 'content-type': 'application/json' },
    body: JSON.stringify(payloads[index]),
  });
  const responses = await Promise.all([post(0), post(1)]);
  const statuses = responses.map(response => response.status);
  const after = await read(cookies[0]);
  const { loser } = verifyRace(before, after, markers, statuses);
  verifyRace(before, await read(cookies[1]), markers, statuses);
  pass('two-session HTTP race: one 200, one 409, one revision, no lost clients');
  const storedAfter = validateRow(await database(workspace));
  assert.equal(storedAfter.storage_version, (storedBefore?.storage_version ?? 0) + 1, 'Hosted storage version must advance exactly once');
  verifyRace(before, storedAfter.state, markers, statuses);
  pass('winning HTTP write verified directly in hosted Supabase');
  assert.equal((await post(loser)).status, 409, 'Replaying the stale losing command must remain a conflict');
  assert.equal((await database(workspace)).storage_version, storedAfter.storage_version, 'Rejected stale command must not write');
  pass('stale replay rejected without a storage-version change');
  assert.equal((await request('/api/ops', {
    method: 'POST', headers: { cookie: cookies[0], origin: 'https://evil.invalid', 'content-type': 'application/json' },
    body: JSON.stringify(payloads[0]),
  })).status, 403, 'Cross-origin write must be blocked');
  assert.equal((await database(workspace)).storage_version, storedAfter.storage_version, 'Cross-origin rejection must not write');
  pass('cross-origin write denied without a database change');
  const report = {
    status: 'PASS', scope: 'hosted-preview-http-and-supabase', run_id: runId, completed_at: new Date().toISOString(),
    deployment_id: deployment.id, deployment_sha: deployment.sha, runner_head_sha: runnerHead.stdout.trim(),
    preview_origin: origin, workspace, checks, persistent_synthetic_markers: markers.filter((_, index) => statuses[index] === 200),
    race_statuses: statuses, revision_before: before.revision, revision_after: after.revision,
    storage_version_before: storedBefore?.storage_version ?? null, storage_version_after: storedAfter.storage_version,
    backup_restore: 'NOT_RUN_BY_THIS_SCRIPT', vercel_restart_persistence: 'NOT_RUN_BY_THIS_SCRIPT',
  };
  await mkdir('qa-output', { recursive: true });
  const reportPath = `qa-output/pr12-hosted-e2e-${runId}.json`;
  await writeFile(reportPath, JSON.stringify(report, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
  console.log(`PASS hosted Preview E2E: ${checks.length} check groups; evidence: ${reportPath}`);
}
main().catch(error => { console.error('FAIL hosted Preview E2E:', error.message); process.exitCode = 1; });
