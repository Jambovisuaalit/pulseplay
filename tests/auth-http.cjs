// Runs against the production build with ephemeral synthetic credentials only.
const assert = require('node:assert/strict');
const http = require('node:http');
const { randomBytes, scryptSync } = require('node:crypto');
const next = require('next');
async function main() {
 const password=randomBytes(24).toString('hex'),salt=randomBytes(16).toString('hex');
 const missing=process.argv.includes('--missing');
 delete process.env.TP_SESSION_SECRET; delete process.env.TP_AUTH_PASSWORD_SCRYPT;
 if(!missing) {process.env.TP_SESSION_SECRET=randomBytes(32).toString('hex'); process.env.TP_AUTH_USERNAME='synthetic'; process.env.TP_AUTH_PASSWORD_SCRYPT=salt+':'+scryptSync(password,salt,64).toString('hex');}
 const app = next({dev:false,dir:process.cwd(),hostname:'localhost',port:3188});
 await app.prepare();
 const server = http.createServer(app.getRequestHandler());
 await new Promise(resolve=>server.listen(3188,'127.0.0.1',resolve));
 const origin='http://localhost:3188'; let checks=0;
 const check=(actual,expected)=>{assert.equal(actual,expected);checks++;};
 const get=(path,headers={})=>fetch(origin+path,{headers,redirect:'manual'});
 const post=(path,body,headers={})=>fetch(origin+path,{method:'POST',redirect:'manual',headers:{origin,'content-type':'application/x-www-form-urlencoded',...headers},body});
 try {
  check((await get('/')).status,307);
  check((await get('/esittely')).status,200);
  if(missing) {
   check((await post('/api/login','username=a&password=b')).headers.get('location'),origin+'/login?config=1');
   console.log(`PASS missing-config HTTP: ${checks} checks`); return;
  }
  check((await post('/api/login','',{origin:'https://evil.invalid'})).status,403);
  check((await post('/api/login','username=synthetic&password=incorrect-password')).headers.get('location'),origin+'/login?error=1');
  check((await get('/',{cookie:'tp_session=legacy-static-token'})).status,307);
  const response=await post('/api/login',new URLSearchParams({username:'synthetic',password}).toString());
  check(response.status,303);
  const cookie=response.headers.get('set-cookie'); assert.match(cookie,/HttpOnly/i);assert.match(cookie,/SameSite=lax/i);assert.match(cookie,/Secure/i);checks+=3;
  const authorized=await get('/',{cookie:cookie.split(';')[0]});check(authorized.status,200);check(authorized.headers.get('cache-control').includes('no-store'),true);
  const bypass=await get('/',{'x-middleware-subrequest':'middleware:middleware:middleware:middleware:middleware'}); check([303,307].includes(bypass.status),true);
  check((await post('/api/logout','',{cookie:cookie.split(';')[0]})).headers.get('set-cookie').includes('Max-Age=0'),true);
  check((await post('/api/login','')).status,303);
  check((await post('/api/login','')).status,303);
  check((await post('/api/login','')).status,303);
  check((await post('/api/login','')).status,429);
  console.log(`PASS auth HTTP: ${checks} checks`);
 } finally {await new Promise(resolve=>server.close(resolve)); await app.close();}
}
main().catch(e=>{console.error(e.message);process.exitCode=1;});
