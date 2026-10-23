import type { Tender } from "@/types/tender";

export type DeadlineStatus = "OPEN" | "EXPIRED" | "UNKNOWN";
export type DeliveryDecision = "GO" | "NO-GO" | "CONDITIONAL_GO" | "EXPIRED" | "CANCELLED" | "NOT_EVALUATED";

export function deadlineStatus(value: string | null | undefined, now = new Date()): DeadlineStatus {
  if (!value || !Number.isFinite(now.getTime())) return "UNKNOWN";
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const parsed = new Date(`${value}T12:00:00Z`);
    if (Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== value) return "UNKNOWN";
    const today = new Intl.DateTimeFormat("en-CA", {
      timeZone: "Europe/Helsinki", year: "numeric", month: "2-digit", day: "2-digit",
    }).format(now);
    return value < today ? "EXPIRED" : value > today ? "OPEN" : "UNKNOWN";
  }
  if (!/(Z|[+-]\d\d:\d\d)$/i.test(value)) return "UNKNOWN";
  const instant = new Date(value);
  if (Number.isNaN(instant.getTime())) return "UNKNOWN";
  return instant <= now ? "EXPIRED" : "OPEN";
}

export function attachmentStatus(tender: Tender): "COMPLETE" | "INCOMPLETE" | "UNKNOWN" {
  if (tender.attachment_review_status === "COMPLETE" && tender.attachment_review_evidence?.trim()) {
    return "COMPLETE";
  }
  return tender.attachment_review_status === "INCOMPLETE" ? "INCOMPLETE" : "UNKNOWN";
}

export function safeSourceDecision(tender: Tender, now = new Date()): {
  decision: DeliveryDecision; deadline: DeadlineStatus; attachments: string; reasons: string[];
} {
  const deadline = deadlineStatus(tender.deadline, now);
  const attachments = attachmentStatus(tender);
  const sourceDecision = tender.go_no_go_suositus;
  const reasons: string[] = [];
  if (/^\s*(KESKEYTETTY|PERUTTU)(\b|\s|:|-)/i.test(tender.title ?? tender.hankinta ?? "")) {
    return { decision: "CANCELLED", deadline, attachments, reasons: ["Ilmoituksen otsikko ilmaisee keskeytyksen tai peruutuksen; tarkista lähteestä."] };
  }
  if (deadline === "EXPIRED") {
    return { decision: "EXPIRED", deadline, attachments, reasons: ["Tarjousmääräaika on päättynyt."] };
  }
  if (!sourceDecision) {
    return { decision: "NOT_EVALUATED", deadline, attachments, reasons: ["Asiakassoveltuvuutta ei ole vielä arvioitu."] };
  }
  if (sourceDecision === "NO-GO") {
    return { decision: "NO-GO", deadline, attachments, reasons };
  }
  if (deadline !== "OPEN") reasons.push("Tarjousmääräaikaa ei ole vahvistettu avoimeksi.");
  if (attachments !== "COMPLETE") reasons.push("Tarjousliitteiden tarkistus puuttuu tai on kesken.");
  return {
    decision: sourceDecision === "GO" && reasons.length === 0 ? "GO" : "CONDITIONAL_GO",
    deadline, attachments, reasons,
  };
}
