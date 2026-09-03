import { NextRequest, NextResponse } from "next/server";

async function sha256(value: string) {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest))
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (
    pathname === "/login" ||
    pathname === "/api/login" ||
    pathname.startsWith("/_next/") ||
    pathname === "/favicon.ico"
  ) {
    return NextResponse.next();
  }

  const username = process.env.TENDERPULSE_USERNAME;
  const password = process.env.TENDERPULSE_PASSWORD;

  if (!username || !password) {
    return NextResponse.redirect(new URL("/login?config=1", request.url));
  }

  const expected = await sha256(
    `${username}:${password}:tenderpulse-session-v1`,
  );

  const actual = request.cookies.get("tp_session")?.value;

  if (actual !== expected) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image).*)"],
};
