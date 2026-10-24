import test from 'node:test';
import assert from 'node:assert/strict';
import http from 'node:http';
import net from 'node:net';
import { spawn } from 'node:child_process';

test('hosted QA fetch uses the configured proxy and preserves NO_PROXY', async () => {
  let proxyRequests = 0, directRequests = 0;
  const tunnels = new Set();
  const proxiedTarget = http.createServer((request, response) => {
    assert.equal(request.url, '/read-only');
    response.setHeader('Connection', 'close');
    response.end('proxied');
  });
  const proxy = http.createServer();
  proxy.on('connect', (request, client, head) => {
    proxyRequests++;
    assert.equal(request.url, 'preview-network-test.invalid:80');
    const upstream = net.connect(proxiedTarget.address().port, '127.0.0.1', () => {
      client.write('HTTP/1.1 200 Connection Established\r\n\r\n');
      if (head.length) upstream.write(head);
      client.pipe(upstream).pipe(client);
    });
    for (const socket of [client, upstream]) {
      tunnels.add(socket);
      socket.on('close', () => tunnels.delete(socket));
      socket.on('error', () => { client.destroy(); upstream.destroy(); });
    }
  });
  const direct = http.createServer((_request, response) => { directRequests++; response.end('direct'); });
  await new Promise(resolve => proxy.listen(0, '127.0.0.1', resolve));
  await new Promise(resolve => direct.listen(0, '127.0.0.1', resolve));
  await new Promise(resolve => proxiedTarget.listen(0, '127.0.0.1', resolve));
  try {
    const proxyUrl = `http://127.0.0.1:${proxy.address().port}`;
    const directUrl = `http://127.0.0.1:${direct.address().port}/read-only`;
    const helper = new URL('./helpers/preview-network.mjs', import.meta.url).href;
    const script = `
      import { configurePreviewNetwork } from ${JSON.stringify(helper)};
      configurePreviewNetwork();
      const proxied = await fetch('http://preview-network-test.invalid/read-only');
      const direct = await fetch(${JSON.stringify(directUrl)});
      console.log(JSON.stringify({proxied:await proxied.text(),direct:await direct.text()}));
    `;
    const child = spawn(process.execPath, ['--input-type=module', '-e', script], {
      timeout: 15000,
      env: { ...process.env, NODE_USE_ENV_PROXY: '0', HTTP_PROXY: proxyUrl, http_proxy: proxyUrl,
        HTTPS_PROXY: proxyUrl, https_proxy: proxyUrl, NO_PROXY: '127.0.0.1', no_proxy: '127.0.0.1' },
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '', stderr = '';
    child.stdout.on('data', value => { stdout += value; });
    child.stderr.on('data', value => { stderr += value; });
    const code = await new Promise((resolve, reject) => { child.once('error', reject); child.once('close', resolve); });
    assert.equal(code, 0, `Local proxy child failed: ${stderr}`);
    assert.deepEqual(JSON.parse(stdout), { proxied: 'proxied', direct: 'direct' });
    assert.equal(proxyRequests, 1);
    assert.equal(directRequests, 1);
  } finally {
    for (const socket of tunnels) socket.destroy();
    for (const server of [proxy, direct, proxiedTarget]) {
      server.closeAllConnections();
      await new Promise(resolve => server.close(resolve));
    }
  }
});
