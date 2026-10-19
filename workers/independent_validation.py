"""Blinded, independent Hilma relevance review and Precision@30 audit.

No model-generated classification may be imported as ground truth.
Prepare against the frozen ranked snapshot and saved raw Hilma material.
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path

LABELS = {"Relevantti", "Epärelevantti", "Mahdollinen"}
ERROR_TYPES = {
    "scope_mismatch", "geography_mismatch", "scale_mismatch",
    "expired_or_invalid", "insufficient_details", "duplicate", "other",
}
REVIEW_FIELDS = [
    "notice_id", "title", "organisation", "description", "deadline",
    "cpv_codes", "manual_label", "manual_reason", "error_type",
    "source_evidence", "reviewer_id", "independent_attestation",
]
TOP_K = 30
REQUIRED_COUNT = 100


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_frozen(rows: list[dict]) -> list[dict]:
    if len(rows) != REQUIRED_COUNT:
        raise ValueError(f"Expected exactly 100 frozen rows, found {len(rows)}")
    try:
        sorted_rows = sorted(rows, key=lambda row: int(row["rank"]))
        ranks = [int(row["rank"]) for row in sorted_rows]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Missing or invalid integer rank") from exc
    ids = [row.get("notice_id", "").strip() for row in sorted_rows]
    if ranks != list(range(1, REQUIRED_COUNT + 1)):
        raise ValueError("Frozen ranking is not unique and consecutive 1..100")
    if not all(ids) or len(set(ids)) != REQUIRED_COUNT:
        raise ValueError("Frozen notice IDs must be unique and nonempty")
    return sorted_rows


def snapshot_sha256(ranked: list[dict]) -> str:
    payload = "\n".join(f'{r["rank"]},{r["notice_id"]}' for r in ranked)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_blind_rows(ranked: list[dict], raw: dict) -> list[dict]:
    notices = {str(n.get("id")): n for n in raw.get("notices", [])}
    missing = [row["notice_id"] for row in ranked if row["notice_id"] not in notices]
    if missing:
        raise ValueError(f"Missing raw Hilma notices for {len(missing)} frozen IDs")
    result = []
    for row in ranked:
        n = notices[row["notice_id"]]
        result.append({
            "notice_id": row["notice_id"],
            "title": n.get("title") or "",
            "organisation": n.get("organisation") or "",
            "description": n.get("description") or "",
            "deadline": n.get("deadline") or "",
            "cpv_codes": "|".join(n.get("cpv_codes") or []),
            "manual_label": "", "manual_reason": "", "error_type": "",
            "source_evidence": "", "reviewer_id": "",
            "independent_attestation": "",
        })
    # Blind assessors to priority score and rank; notice ID is the join key.
    return sorted(result, key=lambda row: row["notice_id"])


def validate_reviews(ranked: list[dict], reviews: list[dict]) -> dict[str, dict]:
    ids = [str(row.get("notice_id", "")).strip() for row in reviews]
    expected = {row["notice_id"] for row in ranked}
    if len(ids) != REQUIRED_COUNT or len(set(ids)) != REQUIRED_COUNT or set(ids) != expected:
        raise ValueError("Review IDs must match exactly the 100 frozen IDs, once each")
    for row in reviews:
        label = row.get("manual_label", "").strip()
        if label and label not in LABELS:
            raise ValueError(f"Invalid label for {row['notice_id']}: {label}")
        if label:
            if not all(row.get(col, "").strip() for col in
                       ("manual_reason", "source_evidence", "reviewer_id")):
                raise ValueError(f"Missing independent review evidence for {row['notice_id']}")
            if row.get("independent_attestation", "").strip().casefold() != "kyllä":
                raise ValueError(f"Independent attestation missing for {row['notice_id']}")
            if label == "Epärelevantti" and row.get("error_type", "") not in ERROR_TYPES:
                raise ValueError(f"Missing error type for {row['notice_id']}")
        elif any(row.get(col, "").strip() for col in
                 ("manual_reason", "error_type", "source_evidence", "reviewer_id", "independent_attestation")):
            raise ValueError(f"Partially filled review for {row['notice_id']}")
    return dict(zip(ids, reviews))


def report(ranked: list[dict], reviews: list[dict]) -> dict:
    by_id = validate_reviews(ranked, reviews)
    top = [by_id[row["notice_id"]] for row in ranked[:TOP_K]]
    lower = [by_id[row["notice_id"]] for row in ranked[TOP_K:]]
    counts = collections.Counter(row.get("manual_label", "") for row in reviews)
    top_counts = collections.Counter(row.get("manual_label", "") for row in top)
    tp = top_counts["Relevantti"]
    fp = top_counts["Epärelevantti"]
    possible_top = top_counts["Mahdollinen"]
    fn = sum(row.get("manual_label") == "Relevantti" for row in lower)
    top_complete = sum(top_counts[label] for label in LABELS) == TOP_K
    fully_reviewed = sum(counts[label] for label in LABELS) == REQUIRED_COUNT
    # "Mahdollinen" does not silently count as either true or false.
    unambiguous = possible_top == 0
    precision = tp / TOP_K if top_complete and unambiguous else None
    error_counts = collections.Counter(
        row["error_type"] for row in top
        if row.get("manual_label") == "Epärelevantti"
    )
    completed = fully_reviewed and unambiguous
    passed = completed and precision is not None and precision >= .80
    return {
        "source": "independent_human_review_required",
        "frozen_ranking_sha256": snapshot_sha256(ranked),
        "population": REQUIRED_COUNT, "top_k": TOP_K,
        "reviewed": sum(counts[label] for label in LABELS),
        "unreviewed": counts[""], "ambiguous_top30": possible_top,
        "true_positives_top30": tp if top_complete else None,
        "false_positives_top30": fp if top_complete else None,
        "false_negatives_below30_within100": fn if fully_reviewed else None,
        "error_types_top30": dict(sorted(error_counts.items())),
        "precision_at_30": round(precision, 4) if precision is not None else None,
        "target_precision": .80, "gate_pass": passed,
        "status": "PASS" if passed else ("FAIL" if completed else "NOT_VALIDATED"),
        "limitations": [
            "Reviewer attestation and source evidence require external verification.",
            "False negatives are relevant items ranked 31..100, not notices outside the retrieval sample.",
            "Indeterminate top-30 labels prevent an accepted precision estimate.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "score"))
    parser.add_argument("--ranked", type=Path,
                        default=Path("data/validation/hilma_100_luokiteltavaksi.csv"))
    parser.add_argument("--raw", type=Path, default=Path("data/hilma_raw.json"))
    parser.add_argument("--reviews", type=Path,
                        default=Path("data/validation/hilma_100_blind_review.csv"))
    parser.add_argument("--output", type=Path,
                        default=Path("data/validation/independent_precision_at_30.json"))
    args = parser.parse_args()
    ranked = validate_frozen(read_csv(args.ranked))
    if args.mode == "prepare":
        raw = json.loads(args.raw.read_text(encoding="utf-8"))
        rows = make_blind_rows(ranked, raw)
        if args.reviews.exists():
            raise FileExistsError(f"Refusing to overwrite reviewer work: {args.reviews}")
        args.reviews.parent.mkdir(parents=True, exist_ok=True)
        with args.reviews.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=REVIEW_FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Prepared {len(rows)} blind review rows; snapshot {snapshot_sha256(ranked)}")
    else:
        output = report(ranked, read_csv(args.reviews))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False),
                               encoding="utf-8")
        print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
