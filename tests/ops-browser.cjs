const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');const {spawn}=require('node:child_process');
const delay=ms=>new Promise(r=>setTimeout(r,ms));
module.exports=async function({origin,cookie}){
 fs.mkdirSync('qa-output',{recursive:true});
 const chrome=spawn(process.env.CHROME_PATH||'google-chrome',['--headless=new','--no-sandbox','--disable-dev-shm-usage','--remote-debugging-port=9223',`--user-data-dir=${path.resolve('qa-output/ops-chrome')}`,'about:blank'],{stdio:'ignore'});
 let ws;const results=[];
 try{
  let targets;for(let i=0;i<40;i++){try{targets=await fetch('http://localhost:9223/json').then(r=>r.json());if(targets.length)break;}catch{}await delay(250);}
  assert.ok(targets?.length,'Chrome startup');ws=new WebSocket(targets.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
  let id=0;const pending=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);if(m.error)p.reject(new Error(m.error.message));else p.resolve(m.result);}};
  const send=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,{resolve,reject});ws.send(JSON.stringify({id:n,method,params}));});
  const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
  await send('Network.enable');await send('Network.setCookie',{name:'tp_session',value:cookie.slice(cookie.indexOf('=')+1),url:origin,path:'/'});await send('Page.enable');await send('Runtime.enable');
  await send('Page.navigate',{url:origin+'/ops'});for(let i=0;i<100;i++){if(await evaluate(`document.querySelector('.ops section')!==null`))break;await delay(200);}
  for(const width of [375,390,768,1440]){
   await send('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:false});await delay(200);
   const metrics=await evaluate(`({overflow:document.documentElement.scrollWidth>innerWidth,labels:[...document.querySelectorAll('input,textarea,select')].every(e=>e.labels.length>0),fields:[...document.querySelectorAll('input,textarea,select')].every(e=>parseFloat(getComputedStyle(e).fontSize)>=16),buttons:[...document.querySelectorAll('button')].every(e=>e.getBoundingClientRect().height>=44)})`);
   assert.equal(metrics.overflow,false);assert.equal(metrics.labels,true);assert.equal(metrics.fields,true);assert.equal(metrics.buttons,true);
   results.push({test:width+'px layout, labels and controls',status:'PASS'});
   const image=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});fs.writeFileSync(`qa-output/ops-${width}.png`,Buffer.from(image.data,'base64'));
  }
  assert.equal(await evaluate(`[...document.querySelectorAll('[data-export-actions] button')].every(e=>e.disabled)`),true);results.push({test:'invalidated approval disables all exports',status:'PASS'});
  // Exercise a real browser form, not a direct API call.
  await evaluate(`(()=>{const form=document.querySelector('.ops form');form.querySelector('select').value='';for(const [name,value] of [['name','Synteettinen selainasiakas'],['email','browser@example.invalid']]){const e=form.elements.namedItem(name);Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(e,value);e.dispatchEvent(new Event('input',{bubbles:true}));}form.querySelector('button').click();})()`);
  for(let i=0;i<50;i++){if(await evaluate(`document.querySelector('.ops').textContent.includes('Synteettinen selainasiakas')`))break;await delay(100);}
  assert.equal(await evaluate(`document.querySelector('.ops').textContent.includes('Synteettinen selainasiakas')`),true);results.push({test:'browser client form saves persistent state',status:'PASS'});
  await evaluate(`document.querySelector('.ops button').focus()`);const focus=await evaluate(`getComputedStyle(document.activeElement).outlineWidth`);assert.equal(focus,'3px');results.push({test:'visible keyboard focus',status:'PASS'});
  fs.writeFileSync('qa-output/ops-browser.json',JSON.stringify(results,null,2));console.log(`PASS ops browser: ${results.length} checks`);
 }finally{ws?.close();chrome.kill('SIGTERM');}
};
