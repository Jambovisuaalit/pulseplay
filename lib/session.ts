// Web Crypto keeps verification identical in Edge middleware and Node handlers.
export const SESSION_COOKIE = "tp_session";
export const SESSION_SECONDS = 3600;
const encoder = new TextEncoder();
function secret() {
  const value = process.env.TP_SESSION_SECRET;
  return value && /^[a-f0-9]{64,128}$/i.test(value) ? value : null;
}
function hex(bytes: ArrayBuffer) {
  return Array.from(new Uint8Array(bytes), byte => byte.toString(16).padStart(2, "0")).join("");
}
async function key() {
  const value = secret();
  if (!value) return null;
  return crypto.subtle.importKey("raw", encoder.encode(value), { name: "HMAC", hash: "SHA-256" }, false, ["sign", "verify"]);
}
export function sessionConfigured() { return secret() !== null; }
export async function createSession(now = Date.now()) {
  const signingKey = await key();
  if (!signingKey) throw new Error("Authentication not configured");
  const nonce = hex(crypto.getRandomValues(new Uint8Array(16)).buffer);
  const payload = `v1.${Math.floor(now / 1000) + SESSION_SECONDS}.${nonce}`;
  const signature = await crypto.subtle.sign("HMAC", signingKey, encoder.encode(payload));
  return `${payload}.${hex(signature)}`;
}
export async function verifySession(token: string | undefined, now = Date.now()) {
  if (!token || token.length > 256) return false;
  const signingKey = await key();
  if (!signingKey) return false;
  const match = /^v1\.(\d{10})\.([a-f0-9]{32})\.([a-f0-9]{64})$/.exec(token);
  if (!match) return false;
  const expires = Number(match[1]), seconds = Math.floor(now / 1000);
  if (expires <= seconds || expires > seconds + SESSION_SECONDS) return false;
  const signature = Uint8Array.from(match[3].match(/../g)!, pair => parseInt(pair, 16));
  return crypto.subtle.verify("HMAC", signingKey, signature, encoder.encode(token.slice(0, token.lastIndexOf("."))));
}
