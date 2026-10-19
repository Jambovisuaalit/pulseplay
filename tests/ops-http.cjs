const assert=require('node:assert/strict');const http=require('node:http');const fs=require('node:fs');const os=require('node:os');const path=require('node:path');
const {randomBytes,scryptSync}=require('node:crypto');
async function main(){
 process.env.NODE_ENV='development';process.env.TP_OPS_LOCAL_ENABLED='true';
 const directory=fs.mkdtempSync(path.join(os.tmpdir(),'urakkaluotsi-ops-'));process.env.TP_OPS_LOCAL_DIRECTORY=directory;
 const password=randomBytes(24).toString('hex'),salt=randomBytes(16).toString('hex');process.env.TP_AUTH_USERNAME='test-operator';process.env.TP_AUTH_PASSWORD_SCRYPT=salt+':'+scryptSync(password,salt,64).toString('hex');process.env.TP_SESSION_SECRET=randomBytes(32).toString('hex');
 const app=require('next')({dev:true,dir:process.cwd(),hostname:'localhost',port:3189});await app.prepare();const server=http.createServer(app.getRequestHandler());await new Promise(resolve=>server.listen(3189,'127.0.0.1',resolve));const origin='http://localhost:3189';
 let checks=0,cookie='',state;const check=(value,expected,label)=>{assert.equal(value,expected,label);checks++;};
 async function read(){const r=await fetch(origin+'/api/ops',{headers:{cookie},redirect:'manual'});check(r.status,200,'read');state=await r.json();return state;}
 async function send(input,status=200){const r=await fetch(origin+'/api/ops',{method:'POST',headers:{cookie,origin,'content-type':'application/json'},body:JSON.stringify({...input,expected_revision:state.revision}),redirect:'manual'});check(r.status,status,`action ${input.action}: ${await r.clone().text()}`);const value=await r.json();if(status===200)state=value;return value;}
 try{
  check((await fetch(origin+'/api/ops',{redirect:'manual'})).status,307,'no session');
  const login=await fetch(origin+'/api/login',{method:'POST',headers:{origin,'content-type':'application/x-www-form-urlencoded'},body:new URLSearchParams({username:'test-operator',password}),redirect:'manual'});check(login.status,303,'login');cookie=login.headers.get('set-cookie').split(';')[0];await read();
  await send({action:'client',name:'Kuvitteellinen Saneeraus Oy',delivery_email:'test@example.invalid'});const client_id=state.clients[0].id;
  await send({action:'profile',client_id,services:['Saneeraus'],regions:['Uusimaa'],facts:[]});
  const notice={action:'notice',notice_id:'987654',title:'Synteettinen hankinta',buyer:'Testiostaja',source_url:'https://example.invalid/hankinta',deadline:new Date(Date.now()+172800000).toISOString(),checked_at:new Date(Date.now()-1000).toISOString(),evidence:'Synteettinen lähdeote',cancelled:false,missing:[]};await send(notice);
  const review={action:'review',client_id,notice_version_id:state.notices[0].id,summary:'Tarkistettava mahdollisuus',next_action:'Varmista referenssit',missing:['Referenssit vahvistamatta'],coverage:'PARTIAL'};await send(review);
  await send({action:'compose',client_id,assessment_ids:[state.assessments[0].id]});const id=state.digests[0].id;
  await send({action:'export',digest_id:id,format:'pdf'},409);
  await send({action:'approve',digest_id:id,expected_hash:state.digests[0].current_hash});
  for(const format of ['pdf','html','txt','eml','json']){
   const r=await fetch(origin+'/api/ops',{method:'POST',headers:{cookie,origin,'content-type':'application/json'},body:JSON.stringify({action:'export',digest_id:id,format,expected_revision:state.revision})});check(r.status,200,`export ${format}`);const bytes=Buffer.from(await r.arrayBuffer());check(bytes.length>100,true,'nonempty export');if(format==='pdf'){check(bytes.subarray(0,5).toString(),'%PDF-','PDF header');fs.mkdirSync('qa-output',{recursive:true});fs.writeFileSync('qa-output/ops-simulation.pdf',bytes);}await read();
  }
  const events=state.events.length;await send({...review,summary:'Arvio muuttui'});check(state.digests[0].status,'NEEDS_REVIEW','approval invalidated');check(state.events.length,events,'history unchanged');await send({action:'export',digest_id:id,format:'txt'},409);
  await send({action:'timer_start',client_id,phase:'DELIVERY'});const timer=state.measurements.work_sessions.at(-1).id;
  await send({action:'timer_start',client_id,phase:'DELIVERY'},409);await send({action:'timer_stop',session_id:timer});
  const version=state.events.find(e=>e.type==='EXPORTED').content_hash;
  await send({action:'correction',digest_id:id,content_hash:version,category:'CONTENT',reason:'Synthetic HTTP correction'});
  await send({action:'feedback',digest_id:id,content_hash:version,assessment_id:state.assessments[0].id,source:'CUSTOMER',label:'USEFUL',reason:'Not real'},400);
  await send({action:'feedback',digest_id:id,content_hash:version,assessment_id:state.assessments[0].id,source:'INTERNAL_SIMULATION',label:'USEFUL',reason:'Synthetic HTTP check'});
  check(state.metrics.correction_events,1,'correction metric');check(state.metrics.customer_usefulness.precision,null,'no fake precision');
  if(process.env.OPS_BROWSER_QA==='true')await require('./ops-browser.cjs')({origin,cookie});
  delete process.env.TP_OPS_LOCAL_ENABLED;
  const blocked=await fetch(origin+'/api/ops',{headers:{cookie}});check(blocked.status,503,'store disabled');
  console.log(`PASS ops HTTP complete workflow: ${checks} checks`);
 }finally{server.closeAllConnections();await new Promise(resolve=>server.close(resolve));await app.close();fs.rmSync(directory,{recursive:true,force:true});}
}
main().then(()=>process.exit(0)).catch(e=>{console.error(e.message);process.exit(1);});
