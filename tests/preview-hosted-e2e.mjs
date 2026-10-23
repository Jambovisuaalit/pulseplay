// Remote Preview-only E2E test. Requires the operator's own test credentials and
// Vercel Automation Bypass, provided through secrets. Never prints secrets.
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';

const origin = (process.env.PREVIEW_E2E_URL || '').replace(/\/$/, '');
const username = process.env.PREVIEW_E2E_USERNAME;
const password = process.env.PREVIEW_E2E_PASSWORD;
const bypass = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;
if (!/^https:\/\/[a-z0-9-]+\.vercel\.app$/.test(origin) ||
    !username || !password || !bypass) {
  throw new Error('Missing protected Preview URL or E2E secrets; refusing to run');
}
if (!process.env.PREVIEW_E2E_PERSIST_SYNTHETIC || process.env.PREVIEW_E2E_PERSIST_SYNTHETIC !== 'yes') {
  throw new Error('Explicit opt-in required: test creates identifiable synthetic data in Preview workspace');
}
const bypassHeaders = {'x-vercel-protection-bypass':bypass};
const request = (path,init={}) => fetch(origin+path,{
  redirect:'manual',cache:'no-store',signal:AbortSignal.timeout(20000),...init,
  headers:{...bypassHeaders,...init.headers}
});
const noSession = await request('/api/ops');
assert.ok([401,303,307,308].includes(noSession.status), 'Unauthenticated GET must be blocked');
const wrongOrigin = await request('/api/login',{
  method:'POST',headers:{origin:'https://evil.invalid','content-type':'application/x-www-form-urlencoded'},
  body:'username=unknown&password=unknown'
});
assert.equal(wrongOrigin.status,403,'Cross-origin login must be blocked');
const login = await request('/api/login',{
  method:'POST',headers:{origin,'content-type':'application/x-www-form-urlencoded'},
  body:new URLSearchParams({username,password}).toString()
});
assert.equal(login.status,303,'Login must return a redirect');
const rawCookie=login.headers.get('set-cookie')||'';
assert.match(rawCookie,/tp_session=/);
assert.match(rawCookie,/HttpOnly/i);
assert.match(rawCookie,/SameSite=Lax/i);
assert.match(rawCookie,/Secure/i);
const cookie=rawCookie.split(';')[0];
const authHeaders={cookie};
async function read() {
 const r=await request('/api/ops',{headers:authHeaders});
 assert.equal(r.status,200,'Authenticated state read failed');
 const state=await r.json();
 assert.equal(state.mode,'SIMULATION');
 return state;
}
let state=await read();
const testId=randomUUID();
const marker='E2E-SYNTHETIC-'+testId;
const payload={
  action:'client',name:marker,
  delivery_email:'preview-e2e-'+testId+'@example.invalid',
  expected_revision:state.revision
};
const post=()=>request('/api/ops',{
  method:'POST',headers:{...authHeaders,origin,'content-type':'application/json'},
  body:JSON.stringify(payload)
});
const [a,b]=await Promise.all([post(),post()]);
assert.deepEqual([a.status,b.status].sort((x,y)=>x-y),[200,409],
 'Exactly one concurrent identical-revision write should succeed');
state=await read();
assert.equal(state.clients.filter(c=>c.name===marker).length,1,'Persisted synthetic record must occur once');
const again=await read();
assert.equal(again.clients.filter(c=>c.name===marker).length,1,'Second independent read must retain record');
const blocked=await request('/api/ops',{method:'POST',headers:{...authHeaders,origin:'https://evil.invalid','content-type':'application/json'},body:JSON.stringify(payload)});
assert.equal(blocked.status,403,'Cross-origin write must be forbidden');
console.log('PASS hosted Preview E2E: login, cookie, authorization, CAS race (200/409), persistence, CSRF');
console.log('Persistent synthetic marker:',marker);
