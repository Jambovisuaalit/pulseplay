import { NextRequest, NextResponse } from "next/server";
import { sameOrigin } from "@/lib/login-auth";
import { SESSION_COOKIE } from "@/lib/session";
export async function POST(request: NextRequest) {
  if (!sameOrigin(request)) return new NextResponse(null, { status: 403 });
  const response = NextResponse.redirect(new URL("/login", request.url), 303);
  response.cookies.set(SESSION_COOKIE, "", { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax", path: "/", maxAge: 0 });
  response.headers.set("Cache-Control", "no-store");
  return response;
}
