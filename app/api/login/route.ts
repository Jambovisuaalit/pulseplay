import { createHash, timingSafeEqual } from "crypto";
import { NextRequest, NextResponse } from "next/server";

const USERNAME = "asiakas";
const PASSWORD_SHA256 =
  "e1c5542fc93e1e2fcf1db991bfa2d852606e57851730c28c47e9dd468aee6cdc";
const SESSION_TOKEN =
  "7c141be1f3d8381cc58961458abf6e679f96b514fc26bb012130f78e60a0377a";

function sha256(value: string) {
  return createHash("sha256").update(value).digest("hex");
}

function equalText(left: string, right: string) {
  const a = Buffer.from(left);
  const b = Buffer.from(right);
  return a.length === b.length && timingSafeEqual(a, b);
}

export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const username = String(formData.get("username") ?? "");
  const password = String(formData.get("password") ?? "");

  if (
    !equalText(username, USERNAME) ||
    !equalText(sha256(password), PASSWORD_SHA256)
  ) {
    return NextResponse.redirect(new URL("/login?error=1", request.url), 303);
  }

  const response = NextResponse.redirect(new URL("/", request.url), 303);

  response.cookies.set("tp_session", SESSION_TOKEN, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 12,
  });

  return response;
}
