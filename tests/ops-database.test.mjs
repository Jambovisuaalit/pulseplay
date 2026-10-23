import test from 'node:test';
import assert from 'node:assert/strict';
import { createDatabaseStore, databaseConfig } from '../lib/server/ops-database.ts';
import { emptyState } from '../lib/domain/model.ts';
import { readState as selectedState } from '../lib/server/ops-store.ts';
import { command } from '../lib/domain/commands.ts';
import { snapshot, contentHash } from '../lib/domain/workflow.ts';

const config={origin:'https://abcdefghijklmnopqrst.supabase.co',key:'sb_secret_synthetic',workspace:'pilot-simulation'};
function backend() {
 let row=null;
 const calls=[];
 const fetcher=async(url,init)=>{
  calls.push({url,init});
  assert.equal(init.headers.apikey,config.key);
  assert.equal(init.cache,'no-store');assert.equal(init.redirect,'error');
  if(init.method==='GET')return Response.json(row?[structuredClone(row)]:[]);
  const input=JSON.parse(init.body);
  if(init.method==='POST'&&row)return Response.json({message:'duplicate'}, {status:409});
  if(init.method==='PATCH'&&new URL(url).searchParams.get('storage_version')!==`eq.${row?.storage_version}`)return Response.json([]);
  row={...row,...input};
  // JSONB may reorder object keys. Order must not affect acknowledgement.
  row.state=Object.fromEntries(Object.entries(row.state).reverse());
  return Response.json([structuredClone(row)]);
 };
 return {fetcher,calls,get row(){return row;},set row(value){row=value;}};
}
test('persistent state survives fresh store instances', async()=>{
 const db=backend(),first=createDatabaseStore(config,db.fetcher);
 assert.equal((await first.readState()).revision,0);assert.equal(db.row,null);
 await first.transaction(s=>{s.clients.push({id:'client-1',name:'Synthetic',delivery_email:'test@example.invalid'});s.revision++;return 'saved';});
 const second=createDatabaseStore(config,db.fetcher);
 assert.equal((await second.readState()).clients[0].id,'client-1');
 await second.transaction(s=>{s.revision++;});
 assert.equal(db.row.storage_version,2);assert.equal((await first.readState()).revision,2);
});
test('approval history survives persisted assessment changes and requires reapproval',async()=>{
 const db=backend(),store=createDatabaseStore(config,db.fetcher),now=Date.now();
 await store.transaction(s=>{
  const run=input=>command(s,{...input,expected_revision:s.revision},'synthetic',now);
  run({action:'client',name:'Synthetic',delivery_email:'test@example.invalid'});const client_id=s.clients[0].id;
  run({action:'profile',client_id,services:['Saneeraus'],regions:['Uusimaa'],facts:[]});
  run({action:'notice',notice_id:'999999',title:'Synthetic refurbishment',buyer:'Test',source_url:'https://example.invalid/notice',deadline:new Date(now+86400000*3).toISOString(),checked_at:new Date(now-1000).toISOString(),cancelled:false,evidence:'Synthetic evidence',missing:[]});
  run({action:'review',client_id,notice_version_id:s.notices[0].id,summary:'Check suitability',next_action:'Verify references',missing:['References not verified'],coverage:'PARTIAL'});
  run({action:'compose',client_id,assessment_ids:[s.assessments[0].id]});
  run({action:'approve',digest_id:s.digests[0].id,expected_hash:contentHash(snapshot(s,s.digests[0]))});
 });
 const another=createDatabaseStore(config,db.fetcher),approved=await another.readState();
 assert.equal(approved.digests[0].status,'APPROVED');assert.equal(approved.events.length,1);
 await another.transaction(s=>command(s,{action:'review',expected_revision:s.revision,client_id:s.clients[0].id,notice_version_id:s.notices[0].id,summary:'Changed assessment',next_action:'Review again',missing:['References not verified'],coverage:'PARTIAL'},'synthetic',now));
 const changed=await store.readState();
 assert.equal(changed.digests[0].status,'NEEDS_REVIEW');assert.equal(changed.digests[0].approved_hash,null);
 assert.deepEqual(changed.events,approved.events);
});
test('concurrent inserts and updates accept one writer and reject the stale writer',async()=>{
 for(const initialized of [false,true]){
  const db=backend(),a=createDatabaseStore(config,db.fetcher),b=createDatabaseStore(config,db.fetcher);
  if(initialized)await a.transaction(s=>{s.revision++;});
  let entered;const waiting=new Promise(r=>{entered=r;});let release;const block=new Promise(r=>{release=r;});
  const losing=a.transaction(async s=>{entered();await block;s.revision++;s.clients.push({id:'lost'});});
  await waiting;await b.transaction(s=>{s.revision++;s.clients.push({id:'winner'});});release();
  await assert.rejects(losing,e=>e.status===409);
  assert.deepEqual((await a.readState()).clients,[{id:'winner'}]);
 }
});
test('command failure never writes; malformed persisted state never resets to empty',async()=>{
 const db=backend(),store=createDatabaseStore(config,db.fetcher);
 await assert.rejects(store.transaction(()=>{throw new Error('invalid command');}));assert.equal(db.row,null);
 db.row={storage_version:1,state:{schema_version:2}};
 await assert.rejects(store.readState(),e=>e.status===503);
 assert.equal(db.calls.filter(c=>c.init.method!=='GET').length,0);
});
test('outage, redirects, broken acknowledgements and unsafe configuration fail closed',async()=>{
 for(const response of [()=>{throw new Error(config.key);},()=>new Response('private database detail',{status:500}),()=>Response.json({bad:true})]){
  await assert.rejects(createDatabaseStore(config,response).readState(),e=>e.status===503&&!e.message.includes(config.key)&&!e.message.includes('private database detail'));
 }
 await assert.rejects(createDatabaseStore(config,async(_url,init)=>init.method==='GET'?Response.json([]):Response.json([{storage_version:2,state:emptyState()}])).transaction(()=>{}),e=>e.status===503);
 const env={TP_SUPABASE_URL:config.origin,TP_SUPABASE_SECRET_KEY:config.key,TP_OPS_WORKSPACE:config.workspace};
 assert.deepEqual(databaseConfig(env),config);
 for(const patch of [{TP_SUPABASE_URL:'http://localhost'},{TP_SUPABASE_SECRET_KEY:'sb_publishable_test'},{TP_OPS_WORKSPACE:'x&select=*'},{TP_SUPABASE_URL:config.origin+'/redirect'}])assert.throws(()=>databaseConfig({...env,...patch}),e=>e.status===503);
});
test('production never falls back to a local file on missing or broken configuration',async()=>{
 const original={...process.env};
 try{
  process.env.NODE_ENV='production';process.env.TP_OPS_LOCAL_ENABLED='true';delete process.env.TP_OPS_STORE;
  await assert.rejects(selectedState(),e=>e.status===503);
  process.env.TP_OPS_STORE='supabase';delete process.env.TP_SUPABASE_URL;
  await assert.rejects(selectedState(),e=>e.status===503);
 }finally{for(const key of Object.keys(process.env))if(!(key in original))delete process.env[key];Object.assign(process.env,original);}
});

test('a lost write acknowledgement does not falsely claim that committed data was not saved',async()=>{
 const db=backend();
 const failing=async(url,init)=>{
  const result=await db.fetcher(url,init);
  if(init.method==='POST')throw new Error('synthetic acknowledgement timeout after commit');
  return result;
 };
 await assert.rejects(createDatabaseStore(config,failing).transaction(s=>{s.clients.push({id:'committed',name:'Synthetic',delivery_email:'qa@example.invalid'});s.revision++;}),e=>e.status===503&&!e.message.includes('Tietoja ei tallennettu'));
 const recovered=await createDatabaseStore(config,db.fetcher).readState();
 assert.equal(recovered.clients[0].id,'committed');
 assert.equal(recovered.revision,1);
});
