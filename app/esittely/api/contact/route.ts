import { NextRequest, NextResponse } from "next/server";
import { validateContact, contactFields } from "../../contact";

export const runtime = "nodejs";
const MAX_BODY_BYTES = 5000;
const EMAIL_API = "https://api.resend.com/emails";

export async function POST(request: NextRequest) {
  const contentLength = Number(request.headers.get("content-length") || 0);
  if (contentLength > MAX_BODY_BYTES) return NextResponse.json({ error: "Viesti on liian pitkä." }, { status: 413 });
  const origin = request.headers.get("origin");
  if (!origin || origin !== request.nextUrl.origin) return NextResponse.json({ error: "Lähetys estetty." }, { status: 403 });
  if (!request.headers.get("content-type")?.startsWith("application/json")) return NextResponse.json({ error: "Virheellinen tietomuoto." }, { status: 415 });
  let data: Record<string, unknown>;
  try {
    const body = await request.text();
    if (Buffer.byteLength(body, "utf8") > MAX_BODY_BYTES) return NextResponse.json({ error: "Viesti on liian pitkä." }, { status: 413 });
    data = JSON.parse(body);
    if (!data || typeof data !== "object" || Array.isArray(data)) throw new Error("Invalid data");
  } catch { return NextResponse.json({ error: "Virheellinen viesti." }, { status: 400 }); }
  if (typeof data.website === "string" && data.website.trim()) return NextResponse.json({ error: "Lähetys estetty." }, { status: 400 });
  const form = new FormData();
  for (const field of contactFields) if (typeof data[field.name] === "string") form.set(field.name, data[field.name] as string);
  const { values, errors } = validateContact(form);
  if (Object.keys(errors).length) return NextResponse.json({ error: "Tarkista kentät.", errors }, { status: 400 });
  const apiKey = process.env.RESEND_API_KEY;
  const from = process.env.URAKKALUOTSI_CONTACT_FROM;
  const to = process.env.URAKKALUOTSI_CONTACT_TO;
  // Fail closed until provider, sender-domain and receiving inbox are configured and verified.
  if (!apiKey || !from || !to) return NextResponse.json({ error: "Lähetys ei ole vielä käytössä. Ota yhteyttä sähköpostilla." }, { status: 503 });
  const lines = contactFields.map(f => `${f.label}: ${values[f.name]}`).join("\n");
  try {
    const response = await fetch(EMAIL_API, { method: "POST", headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" }, body: JSON.stringify({
      from, to: [to], subject: `Urakkaluotsi – pilottihakemus: ${values.company}`,
      text: `Uusi pilottiyhteydenotto\n\n${lines}`,
      reply_to: values.email,
    }), signal: AbortSignal.timeout(8000), cache: "no-store" });
    if (!response.ok) return NextResponse.json({ error: "Viestin toimitusta ei voitu vahvistaa. Lähetä sähköpostia suoraan." }, { status: 502 });
    const result: unknown = await response.json();
    if (!result || typeof result !== "object" || !("id" in result) || typeof (result as { id?: unknown }).id !== "string" || !(result as { id: string }).id.trim()) return NextResponse.json({ error: "Lähetystä ei voitu vahvistaa." }, { status: 502 });
    // Provider acceptance is not proof of final delivery to the inbox.
    return NextResponse.json({ success: true, message: "Viestisi on vastaanotettu lähetyspalveluun. Otamme yhteyttä." }, { status: 202 });
  } catch {
    return NextResponse.json({ error: "Lähetys epäonnistui. Kokeile suoraa sähköpostiyhteyttä." }, { status: 502 });
  }
}
