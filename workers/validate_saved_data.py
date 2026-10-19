"""Offline QA for saved Urakkaluotsi notice datasets; no Hilma API calls.

Usage:
  python -m workers.validate_saved_data --input data/hilma_analysoitu.json --as-of 2026-10-19T00:00:00+03:00
  python -m workers.validate_saved_data --input data/hilma_raw.json --labels data/validation/hilma_100_luokiteltavaksi.csv
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import time
from pathlib import Path

from workers.build_validation_set import parse_deadline, priority_score
from workers.score_validation import score_rows


def analyze(payload: object, as_of: dt.datetime) -> dict:
    if as_of.tzinfo is None:
        raise ValueError("as_of must include timezone")
    records = payload if isinstance(payload, list) else payload.get("notices", [])
    if not isinstance(records, list):
        raise ValueError("notices must be a list")
    unique: set[str] = set()
    duplicates = 0
    invalid_deadline = 0
    expired = 0
    active: list[dict] = []
    for notice in records:
        notice_id = str(notice.get("id") or "")
        if not notice_id or notice_id in unique:
            duplicates += 1
            continue
        unique.add(notice_id)
        deadline = parse_deadline(notice.get("deadline"))
        if deadline is None:
            invalid_deadline += 1
        elif deadline <= as_of:
            expired += 1
        else:
            active.append(notice)
    ranked = sorted(
        active,
        key=lambda n: (priority_score(n), n.get("publishedAt") or "", str(n.get("id"))),
        reverse=True,
    )
    return {
        "records_total": len(records),
        "distinct_ids": len(unique),
        "duplicate_or_missing_ids": duplicates,
        "deadline_invalid_or_ambiguous": invalid_deadline,
        "expired": expired,
        "active": len(active),
        "top30_available": min(len(ranked), 30),
        "top30_ids": [str(n["id"]) for n in ranked[:30]],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--labels", type=Path)
    parser.add_argument("--as-of", help="ISO timestamp with timezone; defaults to snapshot retrievedAt, then current UTC")
    args = parser.parse_args()
    start = time.perf_counter()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    recorded_at = payload.get("retrievedAt") if isinstance(payload, dict) else None
    as_of_text = args.as_of or recorded_at
    as_of = (
        dt.datetime.fromisoformat(as_of_text.replace("Z", "+00:00"))
        if as_of_text else dt.datetime.now(dt.timezone.utc)
    )
    report = {
        "input": str(args.input),
        "as_of": as_of.isoformat(),
        "qa": analyze(payload, as_of),
    }
    if args.labels:
        with args.labels.open("r", encoding="utf-8-sig", newline="") as handle:
            report["precision"] = score_rows(list(csv.DictReader(handle)))
    else:
        report["precision"] = {
            "status": "NOT_VALIDATED",
            "reason": "No frozen 100-row, human-reviewed labels CSV supplied",
        }
    report["processing_seconds"] = round(time.perf_counter() - start, 6)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
