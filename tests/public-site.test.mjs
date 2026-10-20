import { test } from 'node:test';
import assert from 'node:assert/strict';
import { salesEntryPath, confirmedPublicOrigin } from '../lib/public-site.ts';
test('only confirmed marketing domains expose public root',()=>{
 for(const host of ['urakkaluotsi.fi','www.urakkaluotsi.fi','URAKKALUOTSI.FI','urakkaluotsi.fi:443'])assert.equal(salesEntryPath(host,'/'),'/esittely');
 for(const host of [null,'localhost:3000','tenderpulse-neon.vercel.app','urakkaluotsi.fi.example.invalid','noturakkaluotsi.fi'])assert.equal(salesEntryPath(host,'/'),null);
});
test('operator, tender, login and API paths never become public through the domain mapping',()=>{
 for(const path of ['/ops','/api/ops','/tender/123','/login','/api/login','/esittely/api/contact'])assert.equal(salesEntryPath('urakkaluotsi.fi',path),null);
});
test('canonical origin requires explicit exact deployment configuration',()=>{
 assert.equal(confirmedPublicOrigin('https://urakkaluotsi.fi'),'https://urakkaluotsi.fi');
 for(const value of [undefined,'http://urakkaluotsi.fi','https://example.invalid','https://urakkaluotsi.fi.evil.invalid','https://urakkaluotsi.fi/path'])assert.equal(confirmedPublicOrigin(value),undefined);
});
