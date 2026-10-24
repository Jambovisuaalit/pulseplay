// Protected Preview only. Credentials stay in environment bindings and headers.
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import { spawnSync } from 'node:child_process';
import { contentHash } from '../lib/domain/workflow.ts';
import { supabaseConfig, dataApi, validateRow, verifyRace, verifyPreviewTarget, cleanupWorkspace } from './helpers/pr12-qa.mjs';
import { configurePreviewNetwork } from './helpers/preview-network.mjs';

async function main() {
  configurePreviewNetwork();
  const origin = (process.env.PREVIEW_E2E_URL || '').replace(/\/$/, '');
  const username = process.env.PREVIEW_E2E_USERNAME;
  const password = process.env.PREVIEW_E2E_PASSWORD;
  const bypass = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;
  const workspace = process.env.PREVIEW_E2E_WORKSPACE;
  const deploymentId = process.env.PREVIEW_E2E_DEPLOYMENT_ID;
  assert.ok(/^https:\/\/[a-z0-9-]+\.vercel\.app$/.test(origin) && username && password && bypass,
    'Missing protected Preview URL or E2E credential bindings');
  assert.ok(/^(preview-e2e-|pr12-e2e-)[a-z0-9_-]{1,60}$/.test(workspace || ''), 'An empty dedicated E2E workspace is required');
  assert.ok(process.env.PREVIEW_E2E_PERSIST_SYNTHETIC === 'yes', 'Explicit opt-in required for persistent synthetic Preview records');
  assert.ok(/^\d+$/.test(deploymentId || ''), 'Explicit GitHub Preview deployment ID required');
  const config = supabaseConfig(), database = dataApi(config);
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
  assert.equal(await cleanupWorkspace(config,`preview-e2e-probe-${runId}`,runId,1,fetch,true),false,'Cleanup prerequisite probe must not remove a row');
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
  assert.ok(storedBefore === null && before.clients.length === 0, 'Refusing to modify any pre-existing workspace');
  assert.equal(before.storage_mode,'persistent','Preview must use durable storage');
  assert.equal(storedBefore?.state.revision ?? 0, before.revision, 'Preview app and expected Supabase workspace disagree');
  pass('authenticated Preview reads match the hosted Supabase workspace');
  let report;
  try {
  const payloads = markers.map((name, index) => ({
    action: 'client', name, delivery_email: `preview-e2e-${runId}-${index}@example.invalid`, expected_revision: before.revision,
  }));
  const post = index => request('/api/ops', {
    method: 'POST', headers: { cookie: cookies[index], origin, 'content-type': 'application/json' },
    body: JSON.stringify(payloads[index]),
  });
  const attempts = await Promise.allSettled([post(0), post(1)]);
  assert.ok(attempts.every(attempt=>attempt.status==='fulfilled'),'A concurrent request failed at the transport layer; inspect this run before retrying');
  const responses = attempts.map(attempt => attempt.value);
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
  let state = await read(cookies[0]);
  const clientId = state.clients[0].id, name = state.clients[0].name + '-EDITED';
  async function send(input) {
    const response = await request('/api/ops',{method:'POST',headers:{cookie:cookies[0],origin,'content-type':'application/json'},body:JSON.stringify({...input,expected_revision:state.revision})});
    assert.equal(response.status,200,'Hosted workflow command failed');
    state = await response.json();
  }
  await send({action:'client',client_id:clientId,name,delivery_email:'edited@example.invalid'});
  assert.equal((await read(cookies[0])).clients[0].name,name,'Edited client must survive reload');
  const thirdCookie = await login();
  assert.ok(!cookies.includes(thirdCookie),'Fresh login must issue a new session');cookies[0]=thirdCookie;
  state=await read(thirdCookie);assert.equal(state.clients[0].name,name,'Edited client must survive new session');
  pass('create, edit, reload and fresh-session persistence');
  await send({action:'profile',client_id:clientId,services:['Synthetic refurbishment'],regions:['Espoo'],facts:[]});
  const checked = Date.now();
  await send({action:'notice',notice_id:'999999999',title:'Synthetic E2E notice',buyer:'Synthetic buyer',source_url:`https://example.invalid/${runId}`,deadline:new Date(checked+3*86400000).toISOString(),checked_at:new Date(checked-1000).toISOString(),cancelled:false,evidence:'Synthetic source excerpt',missing:['Not a real tender']});
  await send({action:'review',client_id:clientId,notice_version_id:state.notices[0].id,summary:'Synthetic review',next_action:'Verify synthetic evidence',missing:['Not a real tender'],coverage:'PARTIAL'});
  await send({action:'compose',client_id:clientId,assessment_ids:[state.assessments[0].id]});
  const digestId=state.digests[0].id;
  await send({action:'approve',digest_id:digestId,expected_hash:state.digests[0].current_hash});
  for(const format of ['pdf','json']){
    const exported=await request('/api/ops',{method:'POST',headers:{cookie:thirdCookie,origin,'content-type':'application/json'},body:JSON.stringify({action:'export',digest_id:digestId,format,expected_revision:state.revision})});
    assert.equal(exported.status,200,'Approved export must succeed');
    if(format==='pdf')assert.ok(Buffer.from(await exported.arrayBuffer()).subarray(0,5).toString()==='%PDF-','Expected a real PDF');
    else {const delivered=await exported.json();assert.equal(delivered.items[0].source_url,`https://example.invalid/${runId}`);assert.ok(delivered.items[0].missing.length>0);assert.ok(delivered.items[0].deadline);}
    state=await read(thirdCookie);
  }
  pass('profile, source review, compose, approve, PDF/JSON export with source/deadline/missing fields');
  const historyHash=contentHash(state.events);
  await send({action:'profile',client_id:clientId,services:['Changed synthetic service'],regions:['Espoo'],facts:[]});
  assert.equal(state.profiles.length,2,'Both profile versions must be retained');
  assert.equal(state.digests[0].status,'NEEDS_REVIEW','Changed basis must invalidate approval');
  assert.ok(contentHash(state.events)===historyHash,'Approved delivery history must remain immutable');
  const blockedExport=await request('/api/ops',{method:'POST',headers:{cookie:thirdCookie,origin,'content-type':'application/json'},body:JSON.stringify({action:'export',digest_id:digestId,format:'pdf',expected_revision:state.revision})});
  assert.equal(blockedExport.status,409,'Invalidated approval must prevent export');
  const finalStored=validateRow(await database(workspace));
  assert.ok(contentHash(finalStored.state.events)===historyHash && finalStored.state.profiles.length===2,'Profile versions and history must be durably stored');
  pass('profile version persistence and approval invalidation without changing history');
  report = {
    status: 'PASS', scope: 'hosted-preview-http-and-supabase', run_id: runId, completed_at: new Date().toISOString(),
    deployment_id: deployment.id, deployment_sha: deployment.sha, runner_head_sha: runnerHead.stdout.trim(),
    preview_origin: origin, workspace, checks, synthetic_markers: markers,
    final_revision:state.revision,profile_versions:state.profiles.length,delivery_events:state.events.length,
    race_statuses: statuses, revision_before: before.revision, revision_after: after.revision,
    storage_version_before: storedBefore?.storage_version ?? null, storage_version_after: storedAfter.storage_version,
    backup_restore: 'NOT_RUN_BY_THIS_SCRIPT', vercel_restart_persistence: 'NOT_RUN_BY_THIS_SCRIPT',
  };
  } finally {
    const owned = await database(workspace);
    if(owned)await cleanupWorkspace(config,workspace,runId,owned.storage_version);
    assert.ok(await database(workspace)===null,'This run’s synthetic workspace must be removed');
  }
  report.cleanup='PASS: owned workspace removed';
  await mkdir('qa-output', { recursive: true });
  const reportPath = `qa-output/pr12-hosted-e2e-${runId}.json`;
  await writeFile(reportPath, JSON.stringify(report, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
  console.log(`PASS hosted Preview E2E: ${checks.length} check groups; evidence: ${reportPath}`);
}
main().catch(error => { console.error('FAIL hosted Preview E2E:', error.message); process.exitCode = 1; });
