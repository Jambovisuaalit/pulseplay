import { test } from 'node:test';import assert from 'node:assert/strict';
import { emptyState } from '../lib/domain/model.ts';import { command } from '../lib/domain/commands.ts';import { metrics } from '../lib/domain/metrics.ts';import { contentHash,snapshot } from '../lib/domain/workflow.ts';
const now=Date.now();
function fixture(){const s=emptyState();s.clients=[{id:'c',name:'Synthetic',delivery_email:'x@example.invalid'}];s.events=[{id:'e',digest_id:'d',content_hash:'a'.repeat(64),type:'EXPORTED',actor:'test',occurred_at:new Date(now).toISOString(),reference:'x.pdf',snapshot:{schema_version:1,mode:'SIMULATION',client:s.clients[0],profile:{},template_version:'urakkaluotsi-1.1',items:[{assessment_id:'i'}]}}];return s;}
function run(s,input,time=now){return command(s,{...input,expected_revision:s.revision},'test',time);}
test('timers separate onboarding, paused delivery work and unknown human time',()=>{
 const s=fixture();assert.equal(metrics(s).active_delivery_seconds,null);
 run(s,{action:'timer_start',client_id:'c',phase:'ONBOARDING'});run(s,{action:'timer_stop',session_id:s.measurements.work_sessions[0].id},now+60000);
 run(s,{action:'timer_start',client_id:'c',phase:'DELIVERY'},now+120000);assert.throws(()=>run(s,{action:'timer_start',client_id:'c',phase:'DELIVERY'},now+121000));
 assert.equal(metrics(s).open_timers,1);assert.equal(metrics(s).active_delivery_seconds,null);
 run(s,{action:'timer_stop',session_id:s.measurements.work_sessions[1].id},now+240000);
 assert.equal(metrics(s).active_delivery_seconds,120);assert.equal(metrics(s).onboarding_seconds,60);assert.equal(metrics(s).active_seconds_per_client_day,120);
});
test('duplicate formats and revised versions do not inflate delivered final-item denominator',()=>{
 const s=fixture();s.events.push({...s.events[0],id:'e2',reference:'x.html'});assert.equal(metrics(s).delivery_count,1);assert.equal(metrics(s).internal_feedback.final_items,1);
 run(s,{action:'feedback',digest_id:'d',content_hash:'a'.repeat(64),assessment_id:'i',source:'INTERNAL_SIMULATION',label:'USEFUL',reason:'Fixture judgment'});
 assert.equal(metrics(s).internal_feedback.useful,1);
 s.events.push({...s.events[0],id:'e3',content_hash:'b'.repeat(64)});
 assert.equal(metrics(s).exported_versions,2);assert.equal(metrics(s).internal_feedback.useful,0);assert.equal(metrics(s).internal_feedback.pending,1);
});
test('customer claims, unrelated items and duplicate corrections rejected',()=>{
 const s=fixture(),base={digest_id:'d',content_hash:'a'.repeat(64)};
 assert.throws(()=>run(s,{...base,action:'feedback',source:'CUSTOMER',assessment_id:'i',label:'USEFUL',reason:'bad'}));
 assert.throws(()=>run(s,{...base,action:'feedback',source:'INTERNAL_SIMULATION',assessment_id:'other',label:'USEFUL',reason:'bad'}));
 run(s,{...base,action:'correction',category:'CONTENT',reason:'Synthetic injected defect'});assert.throws(()=>run(s,{...base,action:'correction',category:'CONTENT',reason:'Synthetic injected defect'}));
 assert.equal(metrics(s).correction_events,1);assert.equal(metrics(s).correction_rate,1);assert.equal(metrics(s).customer_usefulness.precision,null);
});
test('latest explicit feedback replaces earlier judgment and preserves UNKNOWN',()=>{
 const s=fixture(),base={action:'feedback',digest_id:'d',content_hash:'a'.repeat(64),assessment_id:'i',source:'INTERNAL_SIMULATION',reason:'Fixture only'};
 run(s,{...base,label:'USEFUL'});run(s,{...base,label:'UNKNOWN'});
 assert.equal(metrics(s).internal_feedback.useful,0);assert.equal(metrics(s).internal_feedback.unknown,1);assert.equal(metrics(s).internal_feedback.useful_share_assessed,null);
 assert.equal(metrics(s,'other').delivery_count,0);
});
test('locked multi-day workflow passes the same clock to approval invalidation',()=>{
 const s=emptyState(),future=now+86400000*10;
 function apply(input){command(s,{...input,expected_revision:s.revision},'test',future);}
 apply({action:'client',name:'Synthetic',delivery_email:'x@example.invalid'});const client=s.clients[0].id;
 apply({action:'profile',client_id:client,services:[],regions:[],facts:[]});apply({action:'compose',client_id:client,assessment_ids:[]});
 const notice={action:'notice',notice_id:'123',title:'Future fixture',buyer:'Synthetic',source_url:'https://example.invalid',deadline:new Date(future+86400000*5).toISOString(),checked_at:new Date(future-1000).toISOString(),evidence:'Synthetic',missing:[],cancelled:false};
 apply(notice);apply({action:'review',client_id:client,notice_version_id:s.notices[0].id,summary:'Synthetic',next_action:'Review',coverage:'COMPLETE',missing:[]});
 apply({action:'compose',client_id:client,assessment_ids:[s.assessments[0].id]});const d=s.digests.at(-1);
 apply({action:'approve',digest_id:d.id,expected_hash:contentHash(snapshot(s,d))});assert.equal(d.status,'APPROVED');
});
