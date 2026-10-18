from __future__ import annotations

import csv
import json
from pathlib import Path

INPUT_PATH = Path("data/validation/hilma_100_luokiteltavaksi.csv")
OUTPUT_PATH = Path("data/validation/metrics.json")
VALID_LABELS = {"Relevantti", "Mahdollinen", "Epärelevantti"}
REQUIRED_COUNT = 100
TOP_K = 30


def score_rows(rows: list[dict]) -> dict:
    ranked = sorted(rows, key=lambda row: int(row["rank"]))
    ids = [row.get("notice_id", "") for row in ranked]
    ranks = [int(row["rank"]) for row in ranked]
    if not all(ids) or len(set(ids)) != len(ids):
        raise ValueError("Notice IDs must be non-empty and unique")
    if ranks != list(range(1, len(rows) + 1)):
        raise ValueError("Ranking must be complete, consecutive and unique")

    labeled = [row for row in ranked if row.get("manual_label") in VALID_LABELS]
    top = ranked[:TOP_K]
    top_complete = len(top) == TOP_K and all(
        row.get("manual_label") in VALID_LABELS for row in top
    )
    full_complete = len(rows) == REQUIRED_COUNT and len(labeled) == REQUIRED_COUNT

    # Never shrink the denominator to the subset that happens to be labeled.
    precision = (
        sum(row["manual_label"] == "Relevantti" for row in top) / TOP_K
        if top_complete else None
    )
    return {
        "rows_total": len(rows),
        "rows_labeled": len(labeled),
        "top30_count": len(top),
        "top30_labeled": sum(row.get("manual_label") in VALID_LABELS for row in top),
        "top30_precision": round(precision, 4) if precision is not None else None,
        "ready_for_100_notice_gate": full_complete,
        "target_top30_precision": 0.80,
        "gate_pass": bool(full_complete and precision is not None and precision >= 0.80),
        "status": "PASS" if full_complete and precision is not None and precision >= 0.80 else "NOT_VALIDATED",
    }


def main() -> None:
    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    metrics = score_rows(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
