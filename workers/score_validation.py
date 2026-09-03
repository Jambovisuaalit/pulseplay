from __future__ import annotations

import csv
import json
from pathlib import Path

INPUT_PATH = Path("data/validation/hilma_100_luokiteltavaksi.csv")
OUTPUT_PATH = Path("data/validation/metrics.json")
VALID_LABELS = {"Relevantti", "Mahdollinen", "Epärelevantti"}


def main() -> None:
    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    labeled = [row for row in rows if row.get("manual_label") in VALID_LABELS]
    relevant = [row for row in labeled if row["manual_label"] == "Relevantti"]

    top30 = sorted(
        labeled,
        key=lambda row: int(row.get("priority_score") or 0),
        reverse=True,
    )[:30]
    top30_relevant = [
        row for row in top30 if row["manual_label"] == "Relevantti"
    ]

    metrics = {
        "rows_total": len(rows),
        "rows_labeled": len(labeled),
        "relevant_count": len(relevant),
        "relevant_rate": (
            round(len(relevant) / len(labeled), 4) if labeled else None
        ),
        "top30_count": len(top30),
        "top30_relevant_count": len(top30_relevant),
        "top30_precision": (
            round(len(top30_relevant) / len(top30), 4) if top30 else None
        ),
        "ready_for_100_notice_gate": len(labeled) >= 100,
        "target_top30_precision": 0.80,
    }

    OUTPUT_PATH.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
