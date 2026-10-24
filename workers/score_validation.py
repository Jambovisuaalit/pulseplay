"""Measure relevance against source-reviewed labels, never the ranking's own decisions."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

DEFAULT_DIR = Path("data/validation/independent_100")
VALID_LABELS = {"Relevantti", "Mahdollinen", "Epärelevantti"}
VALID_PREDICTIONS = VALID_LABELS


def read_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def unique_by_id(rows: list[dict], source: str) -> dict[str, dict]:
    indexed = {}
    for row in rows:
        notice_id = (row.get("notice_id") or "").strip()
        if not notice_id or notice_id in indexed:
            raise ValueError(f"{source}: duplicate or empty notice_id: {notice_id!r}")
        indexed[notice_id] = row
    return indexed


def is_independently_reviewed(row: dict) -> bool:
    reviewer = (row.get("reviewer_id") or "").strip().casefold()
    if reviewer in {"model", "llm", "gpt", "assistant", "auto", "automated"}:
        return False
    return (
        row.get("manual_label") in VALID_LABELS
        and all((row.get(key) or "").strip() for key in (
            "reviewer_id", "reviewed_at", "manual_reason", "source_evidence"
        ))
        and (row.get("source_checked") or "").upper() == "YES"
    )


def calculate(predictions: list[dict], gold: list[dict], expected_size: int = 100) -> dict:
    by_prediction = unique_by_id(predictions, "predictions")
    by_gold = unique_by_id(gold, "gold")
    if set(by_prediction) != set(by_gold):
        raise ValueError("Frozen predictions and independent gold IDs must match exactly")
    if len(by_prediction) != expected_size:
        raise ValueError(f"Expected {expected_size} distinct notices, got {len(by_prediction)}")
    for row in predictions:
        if row.get("model_label") not in VALID_PREDICTIONS:
            raise ValueError(f"Invalid baseline prediction for {row['notice_id']}")

    # Freeze rank across ALL rows before inspecting any labels. No coverage bias.
    ranked = sorted(predictions, key=lambda row: (-int(row.get("priority_score") or 0), row["notice_id"]))
    top30 = ranked[:30]
    reviewed = {notice_id: row for notice_id, row in by_gold.items() if is_independently_reviewed(row)}
    invalid_claims = [
        notice_id for notice_id, row in by_gold.items()
        if row.get("manual_label") and notice_id not in reviewed
    ]
    ambiguous = sum(row["manual_label"] == "Mahdollinen" for row in reviewed.values())
    counts = Counter()
    error_types = Counter()
    for notice_id, row in reviewed.items():
        if row["manual_label"] == "Mahdollinen":
            continue
        is_relevant = row["manual_label"] == "Relevantti"
        predicted_positive = by_prediction[notice_id]["model_label"] == "Relevantti"
        if predicted_positive and is_relevant:
            counts["tp"] += 1
        elif predicted_positive and not is_relevant:
            counts["fp"] += 1
            error_types[row.get("error_type") or "määrittämätön"] += 1
        elif not predicted_positive and is_relevant:
            counts["fn"] += 1
            error_types[row.get("error_type") or "ohitettu relevantti"] += 1
        else:
            counts["tn"] += 1

    top30_reviewed = [by_gold[row["notice_id"]] for row in top30 if row["notice_id"] in reviewed]
    all_reviewed = len(reviewed) == expected_size and len(invalid_claims) == 0
    definitive = all_reviewed and ambiguous == 0
    top30_complete = len(top30_reviewed) == len(top30) and all(
        row["manual_label"] != "Mahdollinen" for row in top30_reviewed
    )
    denom = counts["tp"] + counts["fp"]
    predicted_positive_total = sum(row["model_label"] == "Relevantti" for row in predictions)
    return {
        "rows_total": len(predictions), "rows_independently_reviewed": len(reviewed),
        "rows_unreviewed": expected_size - len(reviewed),
        "invalid_label_claims": invalid_claims,
        "gold_ambiguous_count": ambiguous,
        "model_conditional_count": sum(row["model_label"] == "Mahdollinen" for row in predictions),
        "predicted_positive_count": predicted_positive_total,
        "false_positive_possible_range_without_gold": [0, predicted_positive_total] if not definitive else None,
        "false_negative_possible_range_without_gold": [0, expected_size - predicted_positive_total] if not definitive else None,
        "top30_frozen_ids": [row["notice_id"] for row in top30],
        "top30_gold_reviewed": len(top30_reviewed),
        "top30_precision": (round(sum(row["manual_label"] == "Relevantti" for row in top30_reviewed) / len(top30), 4)
                            if top30_complete else None),
        "precision": round(counts["tp"] / denom, 4) if definitive and denom else None,
        "false_positives": counts["fp"] if definitive else None,
        "false_negatives": counts["fn"] if definitive else None,
        "true_positives": counts["tp"] if definitive else None,
        "true_negatives": counts["tn"] if definitive else None,
        "partial_observed_counts_not_final": {name: counts[name] for name in ("tp", "fp", "fn", "tn")},
        "partial_error_types_not_final": dict(error_types),
        "relevance_gate": "PASS" if definitive and denom and counts["tp"] / denom >= 0.8 and top30_complete
                          and sum(row["manual_label"] == "Relevantti" for row in top30_reviewed) / 30 >= 0.8
                          else "FAIL" if definitive else "NOT MEASURED",
        "independence_note": "Only separately source-reviewed, attributed labels count; source documentation completeness is not assumed.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DIR)
    args = parser.parse_args()
    metrics = calculate(read_rows(args.data_dir / "predictions.csv"), read_rows(args.data_dir / "gold_labels.csv"))
    (args.data_dir / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
