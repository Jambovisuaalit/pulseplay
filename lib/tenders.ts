import rawData from "@/data/hilma_analysoitu.json";
import type { Tender } from "@/types/tender";

export type NormalizedTender = Tender & {
  _key: string;
  _title: string;
  _buyer: string;
  _revenue: number | null;
  _decision: string;
};

export function normalizeTender(item: Tender, index = 0): NormalizedTender {
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
    _decision: String(item.go_no_go_suositus ?? "EI ARVIOITU").toUpperCase(),
  };
}

export function getTenders(): NormalizedTender[] {
  const notices = (Array.isArray(rawData)
    ? rawData
    : (rawData as { notices?: Tender[] }).notices ?? []) as Tender[];

  return notices.map((item, index) => normalizeTender(item, index));
}

export function getTenderById(id: string): NormalizedTender | undefined {
  return getTenders().find((item) => item._key === id);
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
