"""Deterministic release checks; source recommendations are never proof of eligibility."""

from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

HELSINKI = ZoneInfo("Europe/Helsinki")


def deadline_status(value: str | None, now: dt.datetime | None = None) -> str:
    """OPEN, EXPIRED or UNKNOWN. Date-only deadlines are not invented times."""
    now = now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    if not value or not isinstance(value, str):
        return "UNKNOWN"
    try:
        if len(value) == 10:
            day = dt.date.fromisoformat(value)
            today = now.astimezone(HELSINKI).date()
            return "EXPIRED" if day < today else "OPEN" if day > today else "UNKNOWN"
        when = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        if when.tzinfo is None:
            return "UNKNOWN"
        return "EXPIRED" if when <= now else "OPEN"
    except ValueError:
        return "UNKNOWN"


def attachment_status(tender: dict) -> str:
    """A full notice or one downloaded PDF does not prove all attachments were checked."""
    state = tender.get("attachment_review_status")
    evidence = tender.get("attachment_review_evidence")
    if state == "COMPLETE" and isinstance(evidence, str) and evidence.strip():
        return "COMPLETE"
    return "INCOMPLETE" if state == "INCOMPLETE" else "UNKNOWN"


def delivery_decision(tender: dict, profile_decision: str, now: dt.datetime | None = None) -> dict:
    deadline = deadline_status(tender.get("deadline"), now)
    attachments = attachment_status(tender)
    reasons = []
    if deadline == "EXPIRED":
        reasons.append("Tarjousmääräaika on päättynyt.")
        decision = "EXPIRED"
    elif tender.get("go_no_go_suositus") is None:
        decision = "NOT_EVALUATED"
        reasons.append("Lähdeilmoituksen asiakassoveltuvuutta ei ole arvioitu.")
    elif tender.get("go_no_go_suositus") == "NO-GO" or profile_decision == "NO-GO":
        decision = "NO-GO"
    elif deadline != "OPEN" or attachments != "COMPLETE" or profile_decision != "GO":
        decision = "CONDITIONAL_GO"
        if deadline != "OPEN":
            reasons.append("Tarjousmääräaikaa ei ole vahvistettu avoimeksi.")
        if attachments != "COMPLETE":
            reasons.append("Tarjousliitteiden täydellistä tarkistusta ei ole vahvistettu.")
        if profile_decision != "GO":
            reasons.append("Yrityksen soveltuvuutta ei ole vahvistettu.")
    else:
        decision = "GO" if tender.get("go_no_go_suositus") == "GO" else "CONDITIONAL_GO"
    return {
        "delivery_decision": decision,
        "deadline_status": deadline,
        "attachment_status": attachments,
        "delivery_reasons": reasons,
    }
