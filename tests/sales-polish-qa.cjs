// QA-only Playwright supplied by the execution environment, never a runtime dependency.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const next = require('next');
const results = [];
const origin = 'http://localhost:3190';
const valid = {company:'Synteettinen Testi Oy',name:'Testaaja',email:'qa@example.invalid',region:'Uusimaa',work:'Korjausrakentaminen'};
const pass = name => {results.push({name,status:'PASS'});console.log('PASS',name);};
async function main(){
 fs.mkdirSync('qa-output',{recursive:true});
 delete process.env.RESEND_API_KEY;delete process.env.URAKKALUOTSI_CONTACT_FROM;delete process.env.URAKKALUOTSI_CONTACT_TO;
 const app=next({dev:false,dir:process.cwd(),hostname:'localhost',port:3190});await app.prepare();
 const server=http.createServer(app.getRequestHandler());await new Promise(r=>server.listen(3190,'127.0.0.1',r));
 const realFetch=global.fetch;let providerMode='accepted',providerCalls=0;
 global.fetch=async (url,options)=>{
  if(String(url)==='https://api.resend.com/emails'){
   providerCalls++;assert.equal(JSON.parse(options.body).reply_to,valid.email);
   if(providerMode==='throw')throw new Error('Synthetic network failure');
   if(providerMode==='reject')return Response.json({error:'Synthetic rejection'},{status:422});
   if(providerMode==='invalid')return Response.json({id:null});
   return Response.json({id:'synthetic-acceptance'});
  }
  return realFetch(url,options);
 };
 const post=(body,headers={})=>realFetch(origin+'/esittely/api/contact',{method:'POST',headers:{origin,'content-type':'application/json',...headers},body:JSON.stringify(body),redirect:'manual'});
 let browser;
 try{
  assert.equal((await post(valid)).status,503);pass('Public contact API: missing configuration gives 503, no login redirect');
  assert.equal((await post({...valid,email:'bad'})).status,400);pass('Server field validation runs even without provider configuration');
  assert.equal((await post(valid,{origin:'https://example.invalid'})).status,403);
  assert.equal((await post(valid,{'content-type':'text/plain'})).status,415);
  assert.equal((await post({...valid,work:'x'.repeat(6000)})).status,413);
  pass('Server rejects cross-origin, incorrect content type and oversized requests');
  process.env.RESEND_API_KEY='synthetic-not-a-key';process.env.URAKKALUOTSI_CONTACT_FROM='test@example.invalid';process.env.URAKKALUOTSI_CONTACT_TO='qa@example.invalid';
  assert.equal((await post({...valid,website:'bot'})).status,400);assert.equal(providerCalls,0);pass('Honeypot never reports success or contacts provider');
  for(const mode of ['reject','invalid','throw']){providerMode=mode;const r=await post(valid);assert.equal(r.status,502);assert.notEqual((await r.json()).success,true);}
  providerMode='accepted';assert.equal((await post(valid)).status,202);pass('Provider rejection / malformed receipt / network failure / acceptance (mocked, no emails sent)');
  delete process.env.RESEND_API_KEY;
  browser=await chromium.launch({headless:true, ...(process.env.CHROME_PATH ? {executablePath:process.env.CHROME_PATH} : {}), args:['--no-sandbox']});
  const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const width of [375,390,768,1440]){
   await page.setViewportSize({width,height:900});await page.goto(origin+'/esittely');
   await page.locator('.ul-form button').waitFor();
   assert.equal(await page.locator('h1').count(),1);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   assert.equal(await page.locator('.ul-price').innerText(),'249 € / 30 päivää\nLopullinen hinta. Myyjä ei kuulu ALV-rekisteriin.');
   assert.equal(await page.locator('link[rel=canonical]').count(),0);
   assert.equal(await page.locator('meta[property="og:url"]').count(),0);
   assert((await page.locator('meta[property="og:image"]').getAttribute('content')).endsWith('/urakkaluotsi/og.png'));
   await page.locator('.ul-nav-cta').click();assert.equal(new URL(page.url()).hash,'#hakemus');
   for(const href of ['#toiminta','#esimerkki','#pilotti']){await page.locator(`nav a[href="${href}"]`).click();assert.equal(new URL(page.url()).hash,href);}
   await page.locator('.ul-form button').click();assert.equal(await page.locator('[aria-invalid=true]').count(),5);assert.equal(await page.evaluate(()=>document.activeElement.name),'company');
   for(const [name,value] of Object.entries({...valid,email:'invalid'}))await page.locator(`[name=${name}]`).fill(value);
   await page.locator('.ul-form button').click();assert.equal(await page.evaluate(()=>document.activeElement.name),'email');
   await page.locator('[name=email]').fill(valid.email);await page.locator('.ul-form button').click();await page.getByRole('status').filter({hasText:'Lähetys ei ole vielä käytössä'}).waitFor();
   assert.equal(await page.locator('[name=company]').inputValue(),valid.company);
   await page.screenshot({path:`qa-output/polish-${width}.png`,fullPage:true});
   await page.evaluate(()=>document.documentElement.style.fontSize='200%');assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth), JSON.stringify(await page.evaluate(()=>Array.from(document.querySelectorAll('.ul-site *')).filter(el=>el.getBoundingClientRect().right>innerWidth).map(el=>({tag:el.tagName,cls:el.className,width:el.getBoundingClientRect().width,right:el.getBoundingClientRect().right})))));
   await page.evaluate(()=>document.documentElement.style.fontSize='');
   pass(`${width}px: no overflow, one H1, metadata, all anchors, validation, unavailable state, 200% text resize`);
  }
  await page.goto(origin+'/esittely');await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.textContent),'Siirry sisältöön');await page.keyboard.press('Enter');assert.equal(await page.evaluate(()=>document.activeElement.id),'alku');
  await page.locator('[name=company]').focus();
  for(const name of ['company','name','email','region','work']){assert.equal(await page.evaluate(()=>document.activeElement.name),name);assert.equal(await page.evaluate(()=>getComputedStyle(document.activeElement).outlineStyle),'solid');await page.keyboard.press('Tab');}
  await page.locator('summary').first().focus();await page.keyboard.press('Enter');assert(await page.locator('details').first().getAttribute('open')!==null);pass('Keyboard skip link, form order, visible focus and FAQ');
  await page.emulateMedia({reducedMotion:'reduce'});assert.equal(await page.locator('.ul-btn').first().evaluate(el=>getComputedStyle(el).transitionDuration),'0s');pass('Reduced motion respected');
  await page.setViewportSize({width:720,height:450});await page.goto(origin+'/esittely');assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));pass('200% browser zoom equivalent: 1440 to 720 CSS pixel reflow');
  // Deterministic delayed server response checks duplicate submission and pending UI.
  let browserPosts=0;
  await page.route('**/esittely/api/contact',async route=>{browserPosts++;await new Promise(r=>setTimeout(r,500));await route.fulfill({status:202,contentType:'application/json',body:JSON.stringify({success:true})});});
  for(const [name,value] of Object.entries(valid))await page.locator(`[name=${name}]`).fill(value);
  await page.evaluate(()=>{const form=document.querySelector('form');form.requestSubmit();form.requestSubmit();});
  assert(await page.locator('.ul-form button').isDisabled());await page.getByRole('status').filter({hasText:'Kiitos yhteydenotosta.'}).waitFor();assert.equal(browserPosts,1);assert.equal(await page.locator('[name=company]').inputValue(),'');pass('Mocked acceptance shows requested success copy; pending button and synchronous duplicate guard');
  await page.unroute('**/esittely/api/contact');
  await page.route('**/esittely/api/contact',route=>route.fulfill({status:502,contentType:'text/html',body:'Upstream error'}));
  for(const [name,value] of Object.entries(valid))await page.locator(`[name=${name}]`).fill(value);
  await page.locator('.ul-form button').click();await page.getByRole('status').filter({hasText:'Viestin lähetys epäonnistui.'}).waitFor();pass('Non-JSON upstream failure is not shown as success');
  assert.equal(await page.evaluate(()=>localStorage.length),0);assert.equal(errors.length,0);pass('No localStorage contact data and no browser runtime exceptions');
  const nojs=await browser.newContext({javaScriptEnabled:false});const p=await nojs.newPage();await p.goto(origin+'/esittely');assert.equal(await p.locator('.ul-form-fields').isVisible(),false);assert(await p.locator('noscript a').isVisible());await nojs.close();pass('No JavaScript fallback');
  await page.goto(origin+'/esittely/tietosuoja');assert.equal(await page.locator('h1').innerText(),'Tietosuojaseloste');pass('Direct privacy page');
  for(const resource of ['/urakkaluotsi/logo-primary.svg','/urakkaluotsi/mark-white.svg','/urakkaluotsi/og.png'])assert.equal((await realFetch(origin+resource)).status,200);
  const pdf=await realFetch(origin+'/urakkaluotsi/esimerkkikooste.pdf');assert.equal(pdf.status,200);assert(pdf.headers.get('content-type').includes('application/pdf'));const bytes=Buffer.from(await pdf.arrayBuffer());assert(bytes.equals(fs.readFileSync('public/urakkaluotsi/esimerkkikooste.pdf')));fs.writeFileSync('qa-output/esimerkkikooste.pdf',bytes);assert.equal((bytes.toString('latin1').match(/\/Type\s*\/Page\b/g)||[]).length,4);pass('Public PDF HTTP 200, four pages and byte-identical supplied original; logo and OG available');
  for(const path of ['/','/ops','/api/ops'])assert.equal((await realFetch(origin+path,{redirect:'manual'})).status,307);pass('Dashboard and operator routes remain protected');
 }finally{
  fs.writeFileSync('qa-output/sales-polish-results.json',JSON.stringify(results,null,2));
  if(browser)await browser.close();global.fetch=realFetch;server.closeAllConnections();await new Promise(r=>server.close(r));await app.close();
 }
}
main().then(()=>process.exit(0)).catch(e=>{console.error(e);process.exit(1);});
