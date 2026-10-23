"""Compare V2 and *frozen legacy* baseline on untouched, ID-disjoint 52 notices.

The AI-silver ledger is frozen before this script is run. Its labels are NOT
gold truth; absent predicted positives yield undefined precision, never 100%.
"""
from __future__ import annotations

import csv
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from build_validation_set import baseline_label, priority_score
from relevance_v2 import classify_notice, MODEL_VERSION
from score_ai_silver import compare
from prepare_independent_review import title_fingerprint

ROOT = Path("data/validation/holdout_52_2026-10-19")
OLD = Path("data/validation/snapshot_2026-10-19/hilma_raw.json")


def validate_provenance(source: dict, old: dict, labels: list[dict], source_sha: str) -> dict:
    """Recheck separation from actual records, not a manifest's claimed zeroes."""
    notices, previous = source["notices"], old["notices"]
    ids = [str(n["id"]) for n in notices]
    label_ids = [r["notice_id"] for r in labels]
    if len(notices) != 52 or len(set(ids)) != 52 or any(not x.strip() for x in ids):
        raise ValueError("Holdout must contain exactly 52 unique source IDs")
    if len(previous) != 100 or len({str(n["id"]) for n in previous}) != 100:
        raise ValueError("Original frozen sample must contain 100 unique IDs")
    if len(label_ids) != 52 or len(set(label_ids)) != 52 or set(label_ids) != set(ids):
        raise ValueError("AI ledger must match every source ID exactly once")
    checks = {
        "id_overlap": set(ids) & {str(n["id"]) for n in previous},
        "procedure_id_overlap": {str(n["procedure_id"]) for n in notices if n.get("procedure_id")}
            & {str(n["procedure_id"]) for n in previous if n.get("procedure_id")},
        "normalised_title_overlap": {title_fingerprint(n["title"]) for n in notices if n.get("title")}
            & {title_fingerprint(n["title"]) for n in previous if n.get("title")},
    }
    for name, overlap in checks.items():
        if overlap:
            raise ValueError(f"Holdout contamination: {name}")
    by_id = {str(n["id"]): n for n in notices}
    for label in labels:
        notice = by_id[label["notice_id"]]
        content = str(notice.get("title") or "") + "\n" + str(notice.get("description") or "")
        quote = label.get("verbatim_source_quote") or ""
        if label.get("source_sha256") != source_sha:
            raise ValueError("AI row refers to another source snapshot")
        if label.get("source_pointer") != f"holdout_raw.json#id={label['notice_id']}":
            raise ValueError("AI row source pointer does not match the notice")
        if label.get("ai_label_not_gold") not in ("Relevantti", "Mahdollinen", "Epärelevantti", ""):
            raise ValueError("Invalid AI source label")
        if label["ai_label_not_gold"]:
            if not quote.strip() or quote.casefold() not in content.casefold():
                raise ValueError("AI evidence quote is absent from this source notice")
        elif content.strip() or quote or label.get("reason_code") != "NO_SOURCE":
            raise ValueError("Unreviewed NO_SOURCE row contradicts source content")
        if label.get("full_notice_and_annexes_checked") != "NO" or label.get("needs_external_adjudication") != "YES":
            raise ValueError("Metadata-only AI review must not claim complete or gold review")
    return {**{name: len(value) for name, value in checks.items()},
            "source_ids_checked": len(ids), "source_quotes_checked": len(labels),
            "independent_accuracy_proven": False}


def evaluate(source: dict, silver: list[dict]) -> tuple[dict, list[dict]]:
    source_ids = [str(n["id"]) for n in source["notices"]]
    if len(source_ids) != 52 or len(set(source_ids)) != 52:
        raise ValueError("Holdout source IDs missing or duplicated")
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
        "evaluation_status": "REGRESSION_REPLAY_AI_SILVER_NOT_INDEPENDENT_GOLD",
        "independent_temporal_holdout": False,
        "independent_gold_labels": False,
        "evaluation_use": "Previously inspected cases; regression only, never new acceptance evidence",
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, default=ROOT)
    output = parser.parse_args().output_dir
    output.mkdir(parents=True, exist_ok=True)
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
    old_raw = OLD.read_bytes()
    if hashlib.sha256(old_raw).hexdigest() != snapshot["old_100_sha256"]:
        raise ValueError("Original sample changed since holdout selection")
    provenance = validate_provenance(json.loads(raw), json.loads(old_raw), labels, m["source_sha256"])
    metrics, detail = evaluate(json.loads(raw), labels)
    metrics.update({
        "provenance_rechecked_from_actual_sources": provenance,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "ai_silver_labels_sha256": hashlib.sha256(silver_raw).hexdigest(),
        "model_version": MODEL_VERSION,
        "classifier_code_sha256": hashlib.sha256(Path("workers/relevance_v2.py").read_bytes()).hexdigest(),
    })
    (output / "v2_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (output / "v2_predictions_and_errors.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, list(detail[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(detail)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
