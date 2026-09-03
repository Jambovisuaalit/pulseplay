import { createHash, timingSafeEqual } from "crypto";
import { NextRequest, NextResponse } from "next/server";

function tokenFor(username: string, password: string) {
  return createHash("sha256")
    .update(`${username}:${password}:tenderpulse-session-v1`)
    .digest("hex");
}

function equalText(left: string, right: string) {
  const a = Buffer.from(left);
  const b = Buffer.from(right);
  return a.length === b.length && timingSafeEqual(a, b);
}

export async function POST(request: NextRequest) {
  const expectedUser = process.env.TENDERPULSE_USERNAME;
  const expectedPassword = process.env.TENDERPULSE_PASSWORD;

  if (!expectedUser || !expectedPassword) {
    return NextResponse.redirect(new URL("/login?config=1", request.url), 303);
  }

  const formData = await request.formData();
  const username = String(formData.get("username") ?? "");
  const password = String(formData.get("password") ?? "");

  if (
    !equalText(username, expectedUser) ||
    !equalText(password, expectedPassword)
  ) {
    return NextResponse.redirect(new URL("/login?error=1", request.url), 303);
  }

  const response = NextResponse.redirect(new URL("/", request.url), 303);

  response.cookies.set("tp_session", tokenFor(expectedUser, expectedPassword), {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 12,
  });

  return response;
}
