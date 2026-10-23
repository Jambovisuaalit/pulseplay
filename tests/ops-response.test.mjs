import test from 'node:test';
import assert from 'node:assert/strict';
import { opsJson, checkOpsResponse, opsErrorMessage } from '../lib/domain/ops-response.ts';

test('storage outages and expired sessions have readable messages without upstream HTML', async () => {
 await assert.rejects(opsJson(new Response('<html>upstream</html>',{status:503}),'fallback'), /Tallennuksen tilaa ei voitu varmistaa/);
 await assert.rejects(opsJson(new Response('<html>login</html>',{status:307}),'fallback'), /Kirjaudu uudelleen/);
 await assert.rejects(opsJson(new Response('<html>broken gateway</html>',{status:200}),'Työtilan lataus epäonnistui'), /^Error: Työtilan lataus epäonnistui$/);
 assert.throws(()=>checkOpsResponse(new Response('conflict',{status:409}),'fallback'), /toisessa istunnossa/);
 assert.match(opsErrorMessage(new TypeError('Failed to fetch')),/Yhteys katkesi/);
 assert.match(opsErrorMessage(new SyntaxError('Unexpected token')),/Tarkista kentät/);
});
test('field validation remains useful and malformed successful data is rejected', async () => {
 await assert.rejects(opsJson(Response.json({error:'Hyväksy kooste ennen vientiä'},{status:422}),'fallback'), /Hyväksy kooste/);
 await assert.rejects(opsJson(Response.json({unexpected:true}),'Työtilan lataus epäonnistui'), /Työtilan lataus epäonnistui/);
 assert.equal((await opsJson(Response.json({revision:1,clients:[]}),'fallback')).revision,1);
});
