from __future__ import annotations

import csv
import json
from pathlib import Path

RAW_PATH = Path("data/hilma_raw.json")
OUTPUT_PATH = Path("data/validation/hilma_100_luokiteltavaksi.csv")
VALID_LABELS = {"Relevantti", "Mahdollinen", "Epärelevantti"}


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
    text = " ".join(
        [
            str(notice.get("title") or ""),
            str(notice.get("description") or ""),
            " ".join(notice.get("cpv_codes") or []),
        ]
    ).lower()

    positives = [
        "lvi",
        "lvia",
        "sähkö",
        "kiinteistö",
        "huolto",
        "kunnossapito",
        "lämpö",
        "jäähdy",
        "putki",
    ]
    negatives = [
        "ajoneuvo",
        "lentokone",
        "laiva",
        "ase",
        "laboratorio",
        "medical",
    ]

    return sum(2 for word in positives if word in text) - sum(
        3 for word in negatives if word in text
    )


def main() -> None:
    payload = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    notices = payload.get("notices") or []
    existing = load_existing_labels()

    ranked = sorted(
        notices,
        key=lambda item: (priority_score(item), item.get("publishedAt") or ""),
        reverse=True,
    )[:100]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    fields = [
        "rank",
        "notice_id",
        "title",
        "organisation",
        "published_at",
        "deadline",
        "cpv_codes",
        "priority_score",
        "manual_label",
        "manual_reason",
    ]

    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()

        for rank, notice in enumerate(ranked, start=1):
            notice_id = str(notice.get("id") or "")
            label, reason = existing.get(notice_id, ("", ""))
            writer.writerow(
                {
                    "rank": rank,
                    "notice_id": notice_id,
                    "title": notice.get("title") or "",
                    "organisation": notice.get("organisation") or "",
                    "published_at": notice.get("publishedAt") or "",
                    "deadline": notice.get("deadline") or "",
                    "cpv_codes": "|".join(notice.get("cpv_codes") or []),
                    "priority_score": priority_score(notice),
                    "manual_label": label,
                    "manual_reason": reason,
                }
            )

    print(f"Wrote {len(ranked)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
