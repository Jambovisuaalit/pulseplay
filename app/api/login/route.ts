import { NextRequest, NextResponse } from "next/server";
import { allowLogin, credentialsConfigured, sameOrigin, verifyCredentials } from "@/lib/login-auth";
import { createSession, SESSION_COOKIE, SESSION_SECONDS } from "@/lib/session";
export const runtime = "nodejs";
export async function POST(request: NextRequest) {
  if (!sameOrigin(request)) return new NextResponse(null, { status: 403 });
  if (!credentialsConfigured()) return NextResponse.redirect(new URL("/login?config=1", request.url), 303);
  // Vercel supplies this header; do not trust arbitrary forwarded headers on other hosts.
  const ip = process.env.VERCEL ? request.headers.get("x-vercel-forwarded-for") ?? "unknown" : "local";
  if (!allowLogin(ip)) return new NextResponse("Liian monta yritystä. Yritä minuutin kuluttua.", { status: 429, headers: { "Retry-After": "60" } });
  const size = Number(request.headers.get("content-length"));
  if (size > 4096) return new NextResponse(null, { status: 413 });
  let form: FormData;
  try { form = await request.formData(); } catch { return new NextResponse(null, { status: 400 }); }
  const username = form.get("username"), password = form.get("password");
  if (typeof username !== "string" || typeof password !== "string" || !(await verifyCredentials(username, password))) {
    return NextResponse.redirect(new URL("/login?error=1", request.url), 303);
  }
  const response = NextResponse.redirect(new URL("/", request.url), 303);
  response.cookies.set(SESSION_COOKIE, await createSession(), {
    httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", path: "/", maxAge: SESSION_SECONDS,
  });
  response.headers.set("Cache-Control", "no-store");
  return response;
}
