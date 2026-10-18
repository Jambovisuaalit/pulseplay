import { test } from 'node:test';
import assert from 'node:assert/strict';
import { scryptSync } from 'node:crypto';
import { createSession, verifySession, sessionConfigured, SESSION_SECONDS } from '../lib/session.ts';
import { verifyCredentials, credentialsConfigured, sameOrigin, allowLogin } from '../lib/login-auth.ts';
const now = 1792360000000;
test('authentication fails closed without configuration', async () => {
 delete process.env.TP_SESSION_SECRET; delete process.env.TP_AUTH_PASSWORD_SCRYPT;
 assert.equal(sessionConfigured(), false); assert.equal(credentialsConfigured(), false);
 assert.equal(await verifySession('legacy-static-token', now), false);
 assert.equal(await verifyCredentials('a','anything'), false);
 await assert.rejects(createSession(now));
});
test('signed sessions are unique, expire, reject forgery and key rotation', async () => {
 process.env.TP_SESSION_SECRET = 'a'.repeat(64);
 const a = await createSession(now), b = await createSession(now);
 assert.notEqual(a,b); assert.equal(await verifySession(a,now),true);
 assert.equal(await verifySession(a,now+SESSION_SECONDS*1000),false);
 assert.equal(await verifySession(a,now-1000),false);
 assert.equal(await verifySession(a.slice(0,-1)+(a.endsWith('0')?'1':'0'),now),false);
 assert.equal(await verifySession('bad',now),false);
 process.env.TP_SESSION_SECRET = 'b'.repeat(64);
 assert.equal(await verifySession(a,now),false);
});
test('scrypt credentials require configured username and correct password', async () => {
 const password = 'synthetic-only-password-123'; const salt='c'.repeat(32);
 process.env.TP_AUTH_USERNAME='operator';
 process.env.TP_AUTH_PASSWORD_SCRYPT=salt+':'+scryptSync(password,salt,64).toString('hex');
 assert.equal(await verifyCredentials('operator',password),true);
 assert.equal(await verifyCredentials('other',password),false);
 assert.equal(await verifyCredentials('operator','incorrect-password-123'),false);
 assert.equal(await verifyCredentials('operator','x'.repeat(257)),false);
});
test('POST origin guard and bounded per-instance throttle', () => {
 assert.equal(sameOrigin(new Request('https://app.test/api/login',{headers:{origin:'https://evil.test'}})),false);
 assert.equal(sameOrigin(new Request('https://app.test/api/login')),false);
 assert.equal(sameOrigin(new Request('https://app.test/api/login',{headers:{origin:'https://app.test'}})),true);
 for(let i=0;i<5;i++) assert.equal(allowLogin('synthetic',now),true);
 assert.equal(allowLogin('synthetic',now),false);
 assert.equal(allowLogin('synthetic',now+60001),true);
});
