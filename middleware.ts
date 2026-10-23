import { NextRequest, NextResponse } from "next/server";

import { salesEntryPath } from "@/lib/public-site";
import { verifySession } from "@/lib/session";

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const publicPath = salesEntryPath(request.headers.get("host"), pathname);
  if (publicPath) {
    const target = request.nextUrl.clone();
    target.pathname = publicPath;
    return NextResponse.rewrite(target);
  }

  if (
    pathname === "/login" ||
    pathname === "/api/login" ||
    pathname === "/esittely" ||
    pathname === "/esittely/api/contact" ||
    pathname === "/esittely/tietosuoja" ||
    /^\/esittely\/[^/]+$/.test(pathname) ||
    pathname === "/urakkaluotsi/esimerkkikooste.pdf" ||
    pathname.startsWith("/urakkaluotsi/") ||
    pathname.startsWith("/_next/") ||
    pathname === "/favicon.ico" ||
    pathname === "/favicon.svg"
  ) {
    return NextResponse.next();
  }

  const actual = request.cookies.get("tp_session")?.value;

  if (!(await verifySession(actual))) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  const response = NextResponse.next();
  response.headers.set("Cache-Control", "private, no-store");
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image).*)"],
};
