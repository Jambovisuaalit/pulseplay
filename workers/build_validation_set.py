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


def priority_score(notice: dict) -> int:
    text = " ".join([
        str(notice.get("title") or ""),
        str(notice.get("description") or ""),
    ]).casefold()
    return sum(weight for term, weight in POSITIVE_TERMS.items() if term in text) - sum(
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
    return deadline is not None and deadline > as_of


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
                "cpv_codes": "|".join(notice.get("cpv_codes") or []),
                "priority_score": priority_score(notice),
                "manual_label": label, "manual_reason": reason,
            })
    print(f"Wrote {len(ranked)} active, unique rows to {OUTPUT_PATH}; snapshot {as_of.isoformat()}")


if __name__ == "__main__":
    main()
