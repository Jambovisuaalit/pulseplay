from __future__ import annotations

import csv
import datetime as dt
import json
import re
from pathlib import Path

RAW_PATH = Path("data/hilma_raw.json")
OUTPUT_PATH = Path("data/validation/hilma_100_luokiteltavaksi.csv")
VALID_LABELS = {"Relevantti", "Mahdollinen", "Epärelevantti"}

# Renovation-first pilot. These are ranking hints, not validated eligibility rules.
POSITIVE_TERMS = {
    "huoneisto": 5, "saneeraus": 5, "korjausrakent": 5,
    "vuosikorja": 5, "pintakorja": 5, "rakennustyö": 4,
    "peruskorja": 4, "maalaus": 3, "lattia": 3,
    "toimitila": 3, "rakennusurak": 3, "korjaustyö": 4,
}
NEGATIVE_TERMS = {
    "ajoneuvo": 5, "lentokone": 5, "laiva": 5,
    "lääkintä": 4, "laboratorio": 4,
}


def load_existing_labels() -> dict[str, tuple[str, str]]:
    if not OUTPUT_PATH.exists():
        return {}
    labels = {}
    with OUTPUT_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            notice_id = row.get("notice_id", "")
            label = row.get("manual_label", "")
            reason = row.get("manual_reason", "")
            if notice_id and label in VALID_LABELS:
                labels[notice_id] = (label, reason)
    return labels


CANCELLED_TERMS = ("keskeytetty", "peruttu", "cancelled", "withdrawn")
OUTSIDE = ("mäntyharju", "kaarina", "salo", "lapua", "raisio", "alavus", "joroinen", "kokkola", "kaustinen", "savukoski", "kalajoki", "joensuu", "nakkila", "suonenjoki", "tampere", "kuopio", "pori", "leppävirta", "parainen", "oulu", "mikkeli", "enontekiö", "kontiolahti")
INSIDE = ("helsinki", "espoo", "vantaa", "hyvinkää", "mäntsälä", "sipoo", "tuusula", "lohja", "porvoo", "kerava", "järvenpää", "kirkkonummi", "nurmijärvi")

def is_cancelled(notice: dict) -> bool:
    title = str(notice.get("title") or "").casefold()
    status = str(notice.get("status") or "").casefold()
    return any(term in title for term in CANCELLED_TERMS) or status in {"cancelled", "withdrawn"}

def location_adjustment(notice: dict) -> int:
    text = " ".join(str(notice.get(k) or "") for k in ("title", "description", "municipality")).casefold()
    if any(place in text for place in OUTSIDE):
        return -40
    if any(place in text for place in INSIDE):
        return 10
    return 0

def normalize_cpv(value) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return "|".join(str(item.get("code") or item.get("cpvCode") or "") if isinstance(item, dict) else str(item) for item in value)
    return ""


def priority_score(notice: dict) -> int:
    text = " ".join([
        str(notice.get("title") or ""),
        str(notice.get("description") or ""),
    ]).casefold()
    return location_adjustment(notice) + sum(weight for term, weight in POSITIVE_TERMS.items() if term in text) - sum(
        weight for term, weight in NEGATIVE_TERMS.items() if term in text
    )


def parse_deadline(value: str | None) -> dt.datetime | None:
    if not value or not isinstance(value, str):
        return None
    # Date-only values lack a verified cutoff hour: fail closed.
    if not re.search(r"T\d{2}:\d{2}", value):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else None
    except ValueError:
        return None


def is_active(notice: dict, as_of: dt.datetime) -> bool:
    deadline = parse_deadline(notice.get("deadline"))
    return not is_cancelled(notice) and deadline is not None and deadline > as_of


def main() -> None:
    payload = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    notices = payload.get("notices") or []
    existing = load_existing_labels()
    # Snapshot timing prevents historical offline reruns from using today's date.
    retrieved = payload.get("retrievedAt")
    as_of = dt.datetime.fromisoformat(str(retrieved).replace("Z", "+00:00"))
    if as_of.tzinfo is None:
        raise ValueError("retrievedAt must contain an explicit timezone")

    active = [notice for notice in notices if is_active(notice, as_of)]
    unique = {}
    for notice in active:
        notice_id = str(notice.get("id") or "")
        if notice_id and notice_id not in unique:
            unique[notice_id] = notice
    ranked = sorted(
        unique.values(),
        key=lambda item: (priority_score(item), item.get("publishedAt") or "", str(item.get("id"))),
        reverse=True,
    )[:100]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "rank", "notice_id", "title", "organisation", "published_at",
        "deadline", "cpv_codes", "priority_score", "manual_label", "manual_reason",
    ]
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for rank, notice in enumerate(ranked, start=1):
            notice_id = str(notice["id"])
            label, reason = existing.get(notice_id, ("", ""))
            writer.writerow({
                "rank": rank, "notice_id": notice_id,
                "title": notice.get("title") or "",
                "organisation": notice.get("organisation") or "",
                "published_at": notice.get("publishedAt") or "",
                "deadline": notice.get("deadline") or "",
                "cpv_codes": normalize_cpv(notice.get("cpv_codes")),
                "priority_score": priority_score(notice),
                "manual_label": label, "manual_reason": reason,
            })
    print(f"Wrote {len(ranked)} active, unique rows to {OUTPUT_PATH}; snapshot {as_of.isoformat()}")


if __name__ == "__main__":
    main()
