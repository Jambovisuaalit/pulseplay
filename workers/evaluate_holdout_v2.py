"""Compare V2 and *frozen legacy* baseline on untouched, ID-disjoint 52 notices.

The AI-silver ledger is frozen before this script is run. Its labels are NOT
gold truth; absent predicted positives yield undefined precision, never 100%.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from build_validation_set import baseline_label, priority_score
from relevance_v2 import classify_notice
from score_ai_silver import compare

ROOT = Path("data/validation/holdout_52_2026-10-19")


def evaluate(source: dict, silver: list[dict]) -> tuple[dict, list[dict]]:
    by_silver = {r["notice_id"]: r for r in silver}
    if len(by_silver) != 52 or len(silver) != 52:
        raise ValueError("AI silver ledger missing or duplicated IDs")
    new_preds, legacy_preds, detail = [], [], []
    for notice in source["notices"]:
        ident = str(notice["id"])
        if ident not in by_silver:
            raise ValueError("Source notice absent from frozen AI-silver labels")
        newer = classify_notice({**notice, "_source_pointer": f"holdout_raw.json#id={ident}"})
        legacy_score = priority_score(notice)
        new_preds.append({"notice_id": ident, "model_label": newer["model_label"],
                          "priority_score": newer["priority_hint_not_probability"]})
        legacy_preds.append({"notice_id": ident, "model_label": baseline_label(legacy_score),
                             "priority_score": legacy_score})
        ai = by_silver[ident]
        detail.append({
            **newer,
            "legacy_model_label": baseline_label(legacy_score),
            "legacy_priority_hint": legacy_score,
            "ai_silver_label_not_gold": ai["ai_label_not_gold"] or "NOT_EVALUATED",
            "ai_silver_reason": ai["reason_code"],
            "ai_source_quote": ai["verbatim_source_quote"],
            "needs_independent_confirmation": "YES",
        })
    ai = [{
        "notice_id": r["notice_id"], "ai_label": r["ai_label_not_gold"],
        "adjudicator": r["adjudicator"], "reason_code": r["reason_code"],
        "exact_source_phrase": r["verbatim_source_quote"], "source_pointer": r["source_pointer"],
    } for r in silver]
    v2, _ = compare(new_preds, ai, expected_size=52, topk=30)
    legacy, _ = compare(legacy_preds, ai, expected_size=52, topk=30)
    ai_counts = Counter(r["ai_silver_label_not_gold"] for r in detail)
    new_counts = Counter(r["model_label"] for r in detail)
    changes = Counter((r["legacy_model_label"], r["model_label"]) for r in detail)
    metrics = {
        "evaluation_status": "ID_DISJOINT_HOLDOUT_AI_SILVER_NOT_INDEPENDENT_GOLD",
        "source_notices": 52,
        "old_100_notice_overlap": 0,
        "ai_silver_class_counts": dict(ai_counts),
        "legacy_class_counts": legacy["baseline_counts"],
        "v2_class_counts": dict(new_counts),
        "class_migrations": [{"from": before, "to": after, "count": count}
                             for (before, after), count in sorted(changes.items())],
        "legacy_provisional_ai_metrics": {
            "tp": legacy["ai_observed_true_positives"], "fp": legacy["ai_observed_false_positives"],
            "fn": legacy["ai_observed_false_negatives"],
            "predicted_positive": legacy["baseline_predicted_positive"],
            "precision": legacy["ai_decisive_precision_only"],
            "fp_range": legacy["ai_based_false_positive_range"],
            "fn_range": legacy["ai_based_false_negative_range"],
        },
        "v2_provisional_ai_metrics": {
            "tp": v2["ai_observed_true_positives"], "fp": v2["ai_observed_false_positives"],
            "fn": v2["ai_observed_false_negatives"],
            "predicted_positive": v2["baseline_predicted_positive"],
            "precision": v2["ai_decisive_precision_only"],
            "fp_range": v2["ai_based_false_positive_range"],
            "fn_range": v2["ai_based_false_negative_range"],
            "precision_undefined_because_no_positive_predictions": v2["baseline_predicted_positive"] == 0,
        },
        "v2_deferred_count": new_counts["Ei priorisoitu"],
        "v2_actionable_conditional_count": new_counts["Mahdollinen"],
        "v2_deferred_by_ai_class": dict(Counter(r["ai_silver_label_not_gold"] for r in detail if r["model_label"] == "Ei priorisoitu")),
        "deferred_is_not_a_verified_negative": True,
        "v2_conditional_candidates_by_ai_class": dict(Counter(
            r["ai_silver_label_not_gold"] for r in detail if r["model_label"] == "Mahdollinen"
        )),
        "official_precision": None,
        "official_relevance_gate": "NOT MEASURED",
        "official_false_negative_count": None,
        "all_ai_silver_labels_from_frozen_source_before_scoring": True,
        "human_gold_count": 0,
        "annexes_fully_checked": 0,
        "source_limitation": "Search-index metadata, same calendar date as old sample; no true independent temporal holdout",
    }
    return metrics, sorted(detail, key=lambda r: (-r["priority_hint_not_probability"], r["notice_id"]))


def main() -> None:
    raw = (ROOT / "holdout_raw.json").read_bytes()
    silver_raw = (ROOT / "ai_silver_labels.csv").read_bytes()
    m = json.loads((ROOT / "ai_silver_manifest.json").read_text(encoding="utf-8"))
    snapshot = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    if hashlib.sha256(raw).hexdigest() != m["source_sha256"] or m["source_sha256"] != snapshot["holdout_raw_sha256"]:
        raise ValueError("Source snapshot changed since blind AI annotation freeze")
    if hashlib.sha256(silver_raw).hexdigest() != m["ai_silver_labels_sha256"]:
        raise ValueError("Blind AI annotations altered after freeze")
    if m["human_gold_count"] != 0 or m["prediction_file_read"] is not False:
        raise ValueError("Blinding provenance violated")
    with (ROOT / "ai_silver_labels.csv").open(encoding="utf-8-sig", newline="") as handle:
        labels = list(csv.DictReader(handle))
    metrics, detail = evaluate(json.loads(raw), labels)
    metrics.update({
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "ai_silver_labels_sha256": hashlib.sha256(silver_raw).hexdigest(),
        "model_version": "ICP_V2_FAIL_CLOSED_2026_10_19",
        "classifier_code_sha256": hashlib.sha256(Path("workers/relevance_v2.py").read_bytes()).hexdigest(),
    })
    (ROOT / "v2_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (ROOT / "v2_predictions_and_errors.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, list(detail[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(detail)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
