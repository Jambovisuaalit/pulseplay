import { NextRequest, NextResponse } from "next/server";

const SESSION_TOKEN =
  "7c141be1f3d8381cc58961458abf6e679f96b514fc26bb012130f78e60a0377a";

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (
    pathname === "/login" ||
    pathname === "/api/login" ||
    pathname.startsWith("/_next/") ||
    pathname === "/favicon.ico"
  ) {
    return NextResponse.next();
  }

  const actual = request.cookies.get("tp_session")?.value;

  if (actual !== SESSION_TOKEN) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image).*)"],
};
