import { scrypt, timingSafeEqual } from "node:crypto";
import { promisify } from "node:util";
import { sessionConfigured } from "./session.ts";
const derive = promisify(scrypt);
export function credentialsConfigured() {
  return Boolean(process.env.TP_AUTH_USERNAME && /^[a-f0-9]{32}:[a-f0-9]{128}$/i.test(process.env.TP_AUTH_PASSWORD_SCRYPT ?? "") && sessionConfigured());
}
export async function verifyCredentials(username: string, password: string) {
  if (!credentialsConfigured() || password.length < 16 || password.length > 256 || username.length > 128) return false;
  const [salt, expected] = process.env.TP_AUTH_PASSWORD_SCRYPT!.split(":");
  const actual = await derive(password, salt, 64) as Buffer;
  const a = Buffer.from(username), b = Buffer.from(process.env.TP_AUTH_USERNAME!);
  const validPassword = timingSafeEqual(actual, Buffer.from(expected, "hex"));
  return a.length === b.length && timingSafeEqual(a, b) && validPassword;
}
// Best-effort per-instance throttle. A distributed limit is required with managed auth.
const attempts = new Map<string, { count: number; reset: number }>();
export function allowLogin(ip: string, now = Date.now()) {
  for (const [key, value] of attempts) if (value.reset <= now) attempts.delete(key);
  if (attempts.size >= 10000 && !attempts.has(ip)) return false;
  const state = attempts.get(ip) ?? { count: 0, reset: now + 60000 };
  state.count++; attempts.set(ip, state);
  return state.count <= 5;
}
export function sameOrigin(request: Request) {
  return request.headers.get("origin") === new URL(request.url).origin;
}
