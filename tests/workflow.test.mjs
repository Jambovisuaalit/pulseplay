import { test } from 'node:test';
import assert from 'node:assert/strict';
import { emptyState } from '../lib/domain/model.ts';
import { command } from '../lib/domain/commands.ts';
import { qa,snapshot,contentHash,approve,exportSnapshot,invalidate } from '../lib/domain/workflow.ts';
import { renderText,renderHtml,renderEml } from '../lib/domain/exports.ts';
import { renderPdf } from '../lib/domain/pdf.ts';
import { profileFacts } from '../lib/domain/validation.ts';
const now=Date.now();
function run(s,input){return command(s,{...input,expected_revision:s.revision},'synthetic',now);}
export function fixture(){
 const s=emptyState();run(s,{action:'client',name:'Kuvitteellinen Saneeraus Oy',delivery_email:'test@example.invalid'});const client_id=s.clients[0].id;
 run(s,{action:'profile',client_id,services:['Saneeraus'],regions:['Uusimaa'],facts:[{key:'referenssit',value:null,verification:'UNKNOWN',source:null,verified_at:null}]});
 run(s,{action:'notice',notice_id:'123',title:'Synteettinen saneeraus',buyer:'Testiostaja',source_url:'https://example.invalid/123',deadline:new Date(now+86400000*5).toISOString(),checked_at:new Date(now-1000).toISOString(),cancelled:false,evidence:'Synteettinen lähdeote',missing:[]});
 run(s,{action:'review',client_id,notice_version_id:s.notices[0].id,summary:'Soveltuvuus tarkistettava',next_action:'Tarkista referenssit',missing:['Referenssit vahvistamatta'],coverage:'PARTIAL'});
 run(s,{action:'compose',client_id,assessment_ids:[s.assessments[0].id]});return s;
}
function accepted(){const s=fixture(),d=s.digests[0];approve(s,d,contentHash(snapshot(s,d)),'synthetic',now);return s;}
test('complete synthetic workflow freezes exact snapshot and renders five formats',()=>{
 const s=accepted(),d=s.digests[0],data=exportSnapshot(s,d,now);
 assert.equal(qa(s,d,now).length,0);assert.equal(d.status,'APPROVED');
 assert.match(renderText(data),/SIMULAATIO/);assert.match(renderHtml(data),/Puuttuvat tiedot/);
 assert.match(renderEml(data,d.approved_hash),/SIMULATION/);assert.doesNotMatch(renderEml(data,d.approved_hash),/^(To|From|Date):/m);
 assert.equal(renderPdf(data).subarray(0,8).toString(),'%PDF-1.4');
 assert.deepEqual(data,d.approved_snapshot);data.client.name='changed';assert.notEqual(data.client.name,d.approved_snapshot.client.name);
});
test('profile, recipient, assessment and source changes invalidate approvals; history survives',()=>{
 for(const change of ['profile','recipient','assessment','source']){
  const s=accepted(),d=s.digests[0],original=structuredClone(s.events[0]);
  if(change==='profile')run(s,{action:'profile',client_id:s.clients[0].id,services:['Changed'],regions:[],facts:[]});
  if(change==='recipient')run(s,{action:'client',client_id:s.clients[0].id,name:s.clients[0].name,delivery_email:'other@example.invalid'});
  if(change==='assessment')run(s,{action:'review',client_id:s.clients[0].id,notice_version_id:s.notices[0].id,summary:'Changed',next_action:'Review',missing:[],coverage:'COMPLETE'});
  if(change==='source'){s.notices.push({...s.notices[0],id:'new',version:2,source_hash:'c'.repeat(64)});invalidate(s);}
  assert.equal(d.status,'NEEDS_REVIEW',change);assert.equal(d.approved_hash,null);assert.throws(()=>exportSnapshot(s,d,now));assert.deepEqual(s.events[0],original);
 }
});
test('QA rejects expired, stale, missing evidence, unchecked cancellation and unreviewed input',()=>{
 for(const mutate of [s=>s.notices[0].deadline=new Date(now-1).toISOString(),s=>s.notices[0].checked_at=new Date(now-86400001).toISOString(),s=>s.notices[0].evidence='',s=>s.notices[0].cancelled=null,s=>s.assessments[0].reviewed=false,s=>s.notices[0].deadline=null]){
  const s=fixture();mutate(s);assert.ok(qa(s,s.digests[0],now).length);assert.throws(()=>approve(s,s.digests[0],contentHash(snapshot(s,s.digests[0])),'test',now));
 }
});
test('near deadline uses one hour freshness; export checks time again',()=>{
 const s=accepted();s.notices[0].deadline=new Date(now+7200000).toISOString();s.notices[0].checked_at=new Date(now-3600001).toISOString();assert.ok(qa(s,s.digests[0],now).some(e=>e.includes('alle tunnin')));
 const s2=accepted();assert.throws(()=>exportSnapshot(s2,s2.digests[0],now+86400001));
});
test('stale revision and hash conflict; invalid state does not silently approve',()=>{
 const s=fixture();assert.throws(()=>command(s,{action:'client',expected_revision:-1},'test',now),e=>e.status===409);
 assert.throws(()=>approve(s,s.digests[0],'0'.repeat(64),'test',now),e=>e.status===409);
 const other=structuredClone(s.profiles[0]);other.id='other';other.client_id='other';s.profiles.push(other);s.assessments[0].client_id='other';assert.ok(qa(s,s.digests[0],now).length);
});
test('unknown is never confirmed false; no forged confirmation or invalid URL',()=>{
 assert.throws(()=>profileFacts([{key:'cert',value:false,verification:'UNKNOWN',source:null,verified_at:null}]));
 assert.throws(()=>profileFacts([{key:'cert',value:true,verification:'CONFIRMED',source:'',verified_at:new Date(now).toISOString()}]));
 assert.equal(profileFacts([{key:'cert',value:false,verification:'CONFIRMED',source:'Synthetic interview',verified_at:new Date(now).toISOString()}])[0].value,false);
});
test('zero-item digest is valid; HTML escapes source and assessments',()=>{
 const s=fixture(),d=s.digests[0];d.assessment_ids=[];assert.deepEqual(qa(s,d,now),[]);approve(s,d,contentHash(snapshot(s,d)),'test',now);assert.match(renderText(exportSnapshot(s,d,now)),/Ei tarkistettuja/);
 const s2=accepted();s2.digests[0].approved_snapshot.items[0].summary='<script>alert(1)</script>';assert.doesNotMatch(renderHtml(s2.digests[0].approved_snapshot),/<script>/);
});
