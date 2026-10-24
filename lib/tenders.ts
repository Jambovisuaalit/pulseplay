import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { SESSION_COOKIE, verifySession } from "@/lib/session";
import rawData from "@/data/hilma_analysoitu.json";
import type { Tender } from "@/types/tender";
import { safeSourceDecision } from "@/lib/deliverySafety";

export type NormalizedTender = Tender & {
  _key: string;
  _title: string;
  _buyer: string;
  _revenue: number | null;
  _decision: string;
  _sourceDecision: string;
  _safetyNotes: string[];
};

export function normalizeTender(item: Tender, index = 0): NormalizedTender {
  const safety = safeSourceDecision(item);
  const organisationName =
    typeof item.organisation === "object" && item.organisation
      ? item.organisation.name
      : typeof item.organisation === "string"
        ? item.organisation
        : undefined;

  const rawRevenue = item.liikevaihto_vaatimus_eur;

  return {
    ...item,
    _key: String(item.id ?? item.notice_id ?? index),
    _title: item.title ?? item.hankinta ?? "Ei otsikkoa",
    _buyer: item.ostaja ?? item.buyer ?? organisationName ?? "Ei ilmoitettu",
    _revenue:
      typeof rawRevenue === "number" && Number.isFinite(rawRevenue)
        ? rawRevenue
        : null,
    _decision: safety.decision,
    _sourceDecision: String(item.go_no_go_suositus ?? "EI ARVIOITU").toUpperCase(),
    _safetyNotes: safety.reasons,
  };
}

export async function getTenders(): Promise<NormalizedTender[]> {
  if (!(await verifySession((await cookies()).get(SESSION_COOKIE)?.value))) redirect("/login");
  const notices = (Array.isArray(rawData)
    ? rawData
    : (rawData as { notices?: Tender[] }).notices ?? []) as Tender[];

  return notices.map((item, index) => normalizeTender(item, index));
}

export async function getTenderById(id: string): Promise<NormalizedTender | undefined> {
  return (await getTenders()).find((item) => item._key === id);
}

export function formatEuro(value: number | null | undefined) {
  return typeof value === "number"
    ? new Intl.NumberFormat("fi-FI", {
        style: "currency",
        currency: "EUR",
        maximumFractionDigits: 0,
      }).format(value)
    : "Ei löydetty";
}
