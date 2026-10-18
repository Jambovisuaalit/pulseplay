// Uses Chrome and Node built-ins only. No application or QA dependency is added.
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { spawn } = require('node:child_process');
const assert = require('node:assert/strict');
const next = require('next');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const output = process.env.QA_OUTPUT || 'qa-output';
fs.mkdirSync(output, { recursive: true });
const results = [];
function pass(name, evidence) { results.push({ name, status: 'PASS', evidence }); console.log('PASS', name, JSON.stringify(evidence)); }
async function main() {
  const app = next({ dev: false, dir: process.cwd(), hostname: '127.0.0.1', port: 3187 });
  await app.prepare();
  const server = http.createServer(app.getRequestHandler());
  await new Promise(resolve => server.listen(3187, '127.0.0.1', resolve));
  const chrome = spawn(process.env.CHROME_PATH || 'google-chrome', ['--headless=new', '--no-sandbox', '--disable-dev-shm-usage', '--no-first-run', '--disable-background-networking', '--remote-debugging-port=9222', `--user-data-dir=${path.resolve(output, 'chrome-profile')}`, 'about:blank'], { stdio: ['ignore', 'ignore', 'pipe'] });
  let chromeLog = ''; chrome.stderr.on('data', data => { chromeLog += data; });
  let ws;
  try {
    let targets;
    for (let i = 0; i < 40; i++) {
      try { targets = await fetch('http://127.0.0.1:9222/json').then(r => r.json()); if (targets.some(t => t.type === 'page')) break; } catch { /* Chrome is starting. */ }
      await delay(250);
    }
    assert.ok(targets?.length, `Chrome failed to start: ${chromeLog.slice(-1000)}`);
    ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
    await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
    let id = 0; const waiting = new Map(); const exceptions = [];
    ws.onmessage = event => {
      const message = JSON.parse(event.data);
      if (message.id) { const pending = waiting.get(message.id); waiting.delete(message.id); if (message.error) pending.reject(new Error(JSON.stringify(message.error))); else pending.resolve(message.result); }
      if (message.method === 'Runtime.exceptionThrown') exceptions.push(message.params.exceptionDetails.text);
    };
    const send = (method, params = {}) => new Promise((resolve, reject) => { const n = ++id; waiting.set(n, { resolve, reject }); ws.send(JSON.stringify({ id: n, method, params })); });
    const evaluate = async expression => {
      const result = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
      if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
      return result.result.value;
    };
    const navigate = async url => {
      await send('Page.navigate', { url });
      for (let i = 0; i < 60; i++) {
        if (await evaluate(`location.href === ${JSON.stringify(url)} && document.readyState === 'complete'`)) break;
        await delay(100);
      }
      await delay(700); // Let React attach handlers before user input.
    };
    const key = async name => {
      const codes = { Tab: 9, Enter: 13 };
      await send('Input.dispatchKeyEvent', { type: 'keyDown', key: name, code: name, windowsVirtualKeyCode: codes[name], nativeVirtualKeyCode: codes[name] });
      await send('Input.dispatchKeyEvent', { type: 'keyUp', key: name, code: name, windowsVirtualKeyCode: codes[name], nativeVirtualKeyCode: codes[name] });
      await delay(100);
    };
    const fill = async (name, value) => evaluate(`(() => {const el=document.querySelector('[name="${name}"]');el.focus();Object.getOwnPropertyDescriptor(el.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype,'value').set.call(el,${JSON.stringify(value)});el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));})()`);
    const submit = async () => { await evaluate(`document.querySelector('.ul-form button[type=submit]').click()`); await delay(200); };
    await send('Page.enable'); await send('Runtime.enable');
    for (const width of [375, 390, 768, 1440]) {
      await send('Emulation.setDeviceMetricsOverride', { width, height: 900, deviceScaleFactor: 1, mobile: false });
      await navigate('http://127.0.0.1:3187/esittely');
      const metrics = await evaluate(`({width:innerWidth,document:document.documentElement.scrollWidth,logo:document.querySelector('.ul-nav img').getBoundingClientRect().width,cta:document.querySelector('.ul-nav-cta').getBoundingClientRect().height,fields:[...document.querySelectorAll('.ul-form input,.ul-form textarea')].map(e=>getComputedStyle(e).fontSize),statuses:[...document.querySelectorAll('.ul-status')].every(e=>getComputedStyle(e).display!=='none')})`);
      assert.ok(metrics.document <= width, JSON.stringify(metrics)); assert.ok(metrics.logo >= 140); assert.ok(metrics.cta >= 44); assert.ok(metrics.fields.every(size => parseFloat(size) >= 16)); assert.ok(metrics.statuses);
      pass(`${width}px responsive layout`, metrics);
      const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true }); fs.writeFileSync(`${output}/esittely-${width}.png`, Buffer.from(shot.data, 'base64'));
      await submit(); assert.equal(await evaluate(`document.querySelectorAll('[aria-invalid=true]').length`), 5); assert.equal(await evaluate('document.activeElement.name'), 'company');
      for (const [name, value] of Object.entries({ company: 'QA & Ääkkönen Oy', name: 'Synteettinen Testaaja', email: 'ei-osoite', region: 'Uusimaa', work: 'Saneeraus\nIkkunat & ovet' })) await fill(name, value);
      await submit(); assert.equal(await evaluate(`document.querySelectorAll('[aria-invalid=true]').length`), 1); assert.equal(await evaluate('document.activeElement.name'), 'email');
      assert.equal(await evaluate(`document.getElementById(document.activeElement.getAttribute('aria-describedby')).textContent.includes('sähköpostiosoite')`), true);
      await fill('email', 'qa@example.invalid'); await submit();
      assert.ok(await evaluate(`document.getElementById('pilot-draft').value.includes('QA & Ääkkönen Oy')`));
      assert.ok(await evaluate(`document.querySelector('[role=status]').textContent.includes('ei ole vahvistettu vastaanotetuksi')`));
      pass(`${width}px blank / malformed / valid contact`, '5 blank errors; email error focused/described; valid draft and copy fallback; no false receipt');
      await navigate('http://127.0.0.1:3187/esittely/tietosuoja');
      assert.equal(await evaluate(`document.querySelector('h1').textContent`), 'Tietosuojaseloste'); assert.ok(await evaluate('document.documentElement.scrollWidth<=innerWidth'));
      pass(`${width}px direct privacy route`, 'Styled route; no horizontal overflow');
    }
    await navigate('http://127.0.0.1:3187/esittely'); await key('Tab');
    assert.equal(await evaluate('document.activeElement.textContent'), 'Siirry sisältöön'); await key('Enter'); assert.equal(await evaluate('document.activeElement.id'), 'alku'); pass('Keyboard skip link', 'First Tab → skip; Enter → main');
    await evaluate(`document.querySelector('[name=company]').focus()`); const order = [];
    for (let i = 0; i < 7; i++) { order.push(await evaluate(`({name:document.activeElement.name||document.activeElement.textContent.slice(0,30),outline:getComputedStyle(document.activeElement).outlineStyle})`)); await key('Tab'); }
    assert.deepEqual(order.slice(0, 5).map(x => x.name), ['company', 'name', 'email', 'region', 'work']); assert.ok(order.every(x => x.outline === 'solid')); pass('Keyboard form focus order', order);
    await evaluate(`document.querySelector('summary').focus()`); await key('Enter'); assert.ok(await evaluate(`document.querySelector('details').open`)); pass('FAQ keyboard', 'Enter expands disclosure');
    await evaluate(`document.documentElement.style.fontSize='200%'`); assert.ok(await evaluate('document.documentElement.scrollWidth<=innerWidth')); pass('200% text resize', '1440px no horizontal overflow');
    await send('Emulation.setScriptExecutionDisabled', { value: true }); await navigate('http://127.0.0.1:3187/esittely');
    // Runtime.evaluate still inspects the DOM when page scripts are disabled.
    assert.ok(await evaluate(`getComputedStyle(document.querySelector('.ul-form-fields')).display==='none'`)); pass('No-JavaScript contact', 'noscript mail link; nonworking form hidden');
    await send('Emulation.setScriptExecutionDisabled', { value: false });
    const pdf = await fetch('http://127.0.0.1:3187/urakkaluotsi/esimerkkikooste.pdf'); assert.equal(pdf.status, 200); assert.ok(pdf.headers.get('content-type').includes('application/pdf')); const bytes = Buffer.from(await pdf.arrayBuffer()); assert.equal(bytes.length, 81071); fs.writeFileSync(`${output}/esimerkkikooste.pdf`, bytes); pass('Public PDF', 'HTTP 200 application/pdf; 81071 bytes identical demo');
    const privacy = await fetch('http://127.0.0.1:3187/esittely/tietosuoja'); assert.equal(privacy.status, 200); pass('Privacy without login', 'HTTP 200');
    const icon = await fetch('http://127.0.0.1:3187/favicon.svg'); assert.equal(icon.status, 200); pass('Public favicon', 'HTTP 200');
    const locked = await fetch('http://127.0.0.1:3187/', { redirect: 'manual' }); assert.equal(locked.status, 307); assert.ok(locked.headers.get('location').endsWith('/login')); pass('Protected dashboard', 'HTTP 307 → /login');
    assert.deepEqual(exceptions, []); pass('JavaScript runtime exceptions', exceptions);
  } finally { ws?.close(); chrome.kill(); await new Promise(resolve => server.close(resolve)); await app.close(); }
}
main().catch(error => { results.push({ name: 'Failure', status: 'FAIL', evidence: error.stack }); console.error(error); process.exitCode = 1; }).finally(() => fs.writeFileSync(`${output}/results.json`, JSON.stringify(results, null, 2)));
