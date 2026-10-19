const assert=require('node:assert/strict');const http=require('node:http');const next=require('next');
async function main(){
 const app=next({dev:false,dir:process.cwd(),hostname:'localhost',port:3191});await app.prepare();const server=http.createServer(app.getRequestHandler());await new Promise(r=>server.listen(3191,'127.0.0.1',r));
 let checks=0;const get=(path,host)=>new Promise((resolve,reject)=>{const req=http.request({hostname:'127.0.0.1',port:3191,path,headers:{host}},res=>{let body='';res.on('data',chunk=>body+=chunk);res.on('end',()=>resolve({status:res.statusCode,text:async()=>body}));});req.on('error',reject);req.end();});
 try{
  for(const host of ['urakkaluotsi.fi','www.urakkaluotsi.fi']){
   const root=await get('/',host);assert.equal(root.status,200);assert((await root.text()).includes('Mitkä julkiset urakat'));checks++;
   for(const path of ['/ops','/api/ops','/tender/123']){assert.equal((await get(path,host)).status,307);checks++;}
  }
  assert.equal((await get('/','tenderpulse-neon.vercel.app')).status,307);checks++;
  assert.equal((await get('/','urakkaluotsi.fi.example.invalid')).status,307);checks++;
  assert.equal((await get('/urakkaluotsi/esimerkkikooste.pdf','urakkaluotsi.fi')).status,200);checks++;
  console.log(`PASS confirmed domain routing and protected portal: ${checks} HTTP checks`);
 }finally{server.closeAllConnections();await new Promise(r=>server.close(r));await app.close();}
}
main().then(()=>process.exit(0)).catch(e=>{console.error(e.message);process.exit(1);});
