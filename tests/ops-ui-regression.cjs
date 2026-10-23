const assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs');
module.exports=async function({origin,cookie}){
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try{
  const context=await browser.newContext();
  await context.addCookies([{name:'tp_session',value:cookie.slice(cookie.indexOf('=')+1),url:origin,httpOnly:true}]);
  const page=await context.newPage();
  await page.goto(origin+'/ops');await page.locator('.ops section').first().waitFor();
  const state=await (await page.request.get(origin+'/api/ops')).json();
  const first=page.locator('.ops form').first();
  await first.locator('select').selectOption(state.clients[0].id);
  assert.equal(await first.locator('[name=name]').inputValue(),state.clients[0].name);
  assert.equal(await first.locator('[name=email]').inputValue(),state.clients[0].delivery_email);
  let posts=0;
  await page.route('**/api/ops',async route=>{
   if(route.request().method()!=='POST')return route.continue();
   posts++;await new Promise(r=>setTimeout(r,200));
   await route.fulfill({status:503,contentType:'text/html',body:'<html>private upstream failure</html>'});
  });
  await page.evaluate(()=>{const f=document.querySelector('.ops form');f.requestSubmit();f.requestSubmit();});
  await page.getByRole('alert').filter({hasText:'Tallennuksen tilaa ei voitu varmistaa'}).waitFor();
  assert.equal(posts,1,'Synchronous duplicate submit must be blocked');
  assert(!((await page.locator('.ops-error').innerText()).includes('upstream')));
  await page.unroute('**/api/ops');
  // A genuine UI edit, followed by reload, exercises the client form end to end.
  await first.locator('[name=name]').fill('Synteettinen Selainmuokkaus Oy');
  await first.getByRole('button',{name:'Tallenna asiakas'}).click();
  await page.getByRole('button',{name:'Tallenna asiakas'}).isEnabled();
  await page.waitForFunction(()=>[...document.querySelectorAll('select option')].some(o=>o.textContent==='Synteettinen Selainmuokkaus Oy'));
  await page.reload();await page.locator('.ops section').first().waitFor();
  assert(await page.locator('select option').filter({hasText:'Synteettinen Selainmuokkaus Oy'}).count()>0);
  // Mock only the approved view to isolate export error UX; no database writes.
  const exportView=structuredClone(state);
  for(const d of exportView.digests){d.qa=[];d.approved_hash='a'.repeat(64);d.current_hash='a'.repeat(64);}
  let downloads=0;page.on('download',()=>downloads++);
  await page.route('**/api/ops',async route=>{
   if(route.request().method()==='GET')return route.fulfill({json:exportView});
   return route.fulfill({status:502,contentType:'text/html',body:'<html>not a PDF</html>'});
  });
  await page.getByRole('button',{name:'Päivitä tila'}).click();
  await page.getByRole('button',{name:'PDF',exact:true}).first().click();
  await page.getByRole('alert').filter({hasText:'Tallennuksen tilaa ei voitu varmistaa'}).waitFor();
  assert.equal(downloads,0,'Failed export must not download an HTML error page');
  await page.unroute('**/api/ops');
  await page.route('**/api/ops',route=>route.fulfill({status:307,headers:{location:'/login'}}));
  await page.getByRole('button',{name:'Päivitä tila'}).click();
  await page.getByRole('alert').filter({hasText:'Kirjaudu uudelleen'}).waitFor();
  fs.mkdirSync('qa-output',{recursive:true});fs.writeFileSync('qa-output/ops-ui-regressions.json',JSON.stringify({status:'PASS',scope:'LOCAL_BROWSER',checks:['client edit and reload','duplicate guard','non-JSON save failure','non-JSON export failure','expired session']},null,2));
  console.log('PASS ops UI regressions: edit/reload, duplicate guard, HTML save/export failure, expired session');
 }finally{await browser.close();}
};
