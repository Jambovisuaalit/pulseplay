import http from 'node:http';

// Node fetch does not use the cloud's credential-substituting proxy by default.
// Configure it before any request, retaining NO_PROXY and normal TLS checks.
export function configurePreviewNetwork(env = process.env) {
  if (!['HTTPS_PROXY', 'HTTP_PROXY', 'https_proxy', 'http_proxy'].some(name => env[name])) return;
  if (typeof http.setGlobalProxyFromEnv !== 'function') {
    throw new Error('Hosted QA proxy support requires Node.js 24.14 or newer');
  }
  try { http.setGlobalProxyFromEnv(env); }
  catch { throw new Error('Hosted QA proxy configuration failed; values omitted'); }
}
