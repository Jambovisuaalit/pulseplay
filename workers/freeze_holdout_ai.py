"""Freeze source-only AI-silver labels before generating V2 predictions.

No scoring module or prediction file may be read here. This is NOT gold truth.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path("data/validation/holdout_52_2026-10-19")
TYPES = {"AREA", "SCOPE", "SIZE", "MIXED", "UNRESOLVED", "NO_SOURCE"}
LABELS = {"Epärelevantti", "Relevantti", "Mahdollinen", ""}


def freeze(source: dict, seed: list[dict], source_sha: str, timestamp: str) -> list[dict]:
    notices = {str(item["id"]): item for item in source["notices"]}
    ledger = {row["notice_id"]: row for row in seed}
    if len(notices) != 52 or len(seed) != 52 or len(ledger) != 52 or set(ledger) != set(notices):
        raise ValueError("Frozen AI ledger must match exactly 52 distinct source IDs")
    result = []
    for ident in sorted(ledger):
        row, notice = ledger[ident], notices[ident]
        ai_label, reason, phrase = (row[k].strip() for k in ("ai_label", "reason_code", "source_phrase"))
        if ai_label not in LABELS or reason not in TYPES:
            raise ValueError(f"Invalid AI-silver class/reason for {ident}")
        content = (str(notice.get("title") or "") + "\n" + str(notice.get("description") or ""))
        if reason == "NO_SOURCE":
            if ai_label or phrase or content.strip():
                raise ValueError(f"Unsupported NO_SOURCE for {ident}")
        elif not phrase or phrase.casefold() not in content.casefold():
            raise ValueError(f"Source quote not found for {ident}: {phrase!r}")
        if ai_label == "" and reason != "NO_SOURCE":
            raise ValueError(f"Missing class requires NO_SOURCE for {ident}")
        result.append({
            "notice_id": ident, "ai_label_not_gold": ai_label,
            "reason_code": reason, "verbatim_source_quote": phrase,
            "review_note": row["review_note"],
            "adjudicator": "AI_SOURCE_ONLY_BLIND_HOLDOUT_V1_NOT_HUMAN_GOLD",
            "reviewed_at_utc": timestamp,
            "source_sha256": source_sha,
            "source_pointer": f"holdout_raw.json#id={ident}",
            "full_notice_and_annexes_checked": "NO",
            "needs_external_adjudication": "YES",
        })
    return result


def main() -> None:
    raw = (ROOT / "holdout_raw.json").read_bytes()
    seed_bytes = (ROOT / "ai_source_only_seed.tsv").read_bytes()
    seed = list(csv.DictReader(seed_bytes.decode("utf-8" ).splitlines(), delimiter="\t"))
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    rows = freeze(json.loads(raw), seed, hashlib.sha256(raw).hexdigest(), now)
    target = ROOT / "ai_silver_labels.csv"
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "review_type": "AI_SILVER_SOURCE_ONLY_BLIND_HOLDOUT_NOT_HUMAN_GOLD",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "seed_sha256": hashlib.sha256(seed_bytes).hexdigest(),
        "ai_silver_labels_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "frozen_at_utc": now,
        "count": len(rows),
        "prediction_file_read": False,
        "human_gold_count": 0,
        "full_annex_reviews": 0,
        "usable_for_official_precision": False,
    }
    (ROOT / "ai_silver_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"count": len(rows), "ai_counts": dict(Counter(r["ai_label_not_gold"] or "NOT_EVALUATED" for r in rows)), "manifest": manifest}, ensure_ascii=False))


if __name__ == "__main__":
    main()
