"""Freeze source-only blind review rows and a separate heuristic baseline.

No model decision is ever copied to the independent gold labels.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
from pathlib import Path

DEFAULT_RAW = Path("data/validation/snapshot_2026-10-19/hilma_raw.json")
DEFAULT_OUTPUT = Path("data/validation/independent_100")
SEED = 20261019
POSITIVE_TERMS = {
    "huoneisto": 6, "saneeraus": 5, "korjausrakent": 6,
    "vuosikorja": 5, "pintakorja": 6, "pintaremont": 6,
    "peruskorja": 4, "maalaus": 4, "lattia": 4,
    "toimitila": 3, "sisäpuolis": 4, "pienkorja": 5,
    "korjaustyö": 4, "rakennustyö": 2,
}
NEGATIVE_TERMS = {
    "uudisrakent": 8, "kattourak": 8, "vesikatt": 7,
    "ikkunoiden uusimin": 8, "ikkunoiden vaiht": 8,
    "ovien kokonais": 8, "talotekninen kokonais": 9,
    "maanrakennus": 6, "tiehank": 6, "sillanrak": 6,
    "ajoneuvo": 8, "lentokone": 8, "laboratorio": 8,
}


def priority_score(notice: dict) -> int:
    """Unvalidated renovation-first ranking hint, *not* ground truth."""
    content = " ".join([str(notice.get("title") or ""), str(notice.get("description") or "")]).casefold()
    return sum(w for term, w in POSITIVE_TERMS.items() if term in content) - sum(
        w for term, w in NEGATIVE_TERMS.items() if term in content
    )


def baseline_label(score: int) -> str:
    return "Relevantti" if score >= 5 else "Mahdollinen" if score > 0 else "Epärelevantti"


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build(raw_path: Path, output_dir: Path, sample_size: int = 100) -> dict:
    raw_bytes = raw_path.read_bytes()
    payload = json.loads(raw_bytes)
    notices = payload.get("notices")
    if not isinstance(notices, list):
        raise ValueError("Source is missing notices array")
    ids = [str(item.get("id") or "").strip() for item in notices]
    if any(not notice_id for notice_id in ids) or len(set(ids)) != len(ids):
        raise ValueError("Missing or duplicate notice IDs: fix source before sampling")
    if len(notices) < sample_size:
        raise ValueError(f"Only {len(notices)} authentic notices; {sample_size} required")

    # Uniform seeded sampling, never sample by a score that will be evaluated.
    ordered = sorted(notices, key=lambda item: str(item["id"]))
    selected = sorted(random.Random(SEED).sample(ordered, sample_size), key=lambda item: str(item["id"]))
    provenance = f"Saved source {raw_path} / sha256 {hashlib.sha256(raw_bytes).hexdigest()}"
    blind_rows, prediction_rows, gold_rows = [], [], []
    for notice in selected:
        notice_id = str(notice["id"])
        cpvs = notice.get("cpv_codes") or []
        cpvs = "|".join(map(str, cpvs)) if isinstance(cpvs, list) else str(cpvs)
        blind_rows.append({
            "notice_id": notice_id, "title": notice.get("title") or "",
            "organisation": notice.get("organisation") or "",
            "description": re.sub(r"[ \t]+(?=\r?\n|$)", "", notice.get("description") or ""),
            "published_at": notice.get("publishedAt") or "",
            "deadline": notice.get("deadline") or "",
            "cpv_codes": cpvs,
            "estimated_value": notice.get("estimated_value") if notice.get("estimated_value") is not None else "",
            "procedure_id": notice.get("procedure_id") or "",
            "source_provenance": provenance,
        })
        score = priority_score(notice)
        prediction_rows.append({"notice_id": notice_id, "priority_score": score, "model_label": baseline_label(score)})
        gold_rows.append({
            "notice_id": notice_id, "reviewer_id": "", "reviewed_at": "",
            "manual_label": "", "manual_reason": "", "source_evidence": "", "source_checked": "",
            "error_type": "",
        })

    output_dir.mkdir(parents=True, exist_ok=True)
    # Check before touching any existing output: preserve human annotations.
    gold_path = output_dir / "gold_labels.csv"
    if gold_path.exists():
        with gold_path.open("r", encoding="utf-8-sig", newline="") as handle:
            existing_ids = {row.get("notice_id") for row in csv.DictReader(handle)}
        if existing_ids != set(ids):
            raise ValueError("Existing human gold belongs to a different source set; do not mix snapshots")
    write_csv(output_dir / "blind_review.csv", list(blind_rows[0]), blind_rows)
    write_csv(output_dir / "predictions.csv", list(prediction_rows[0]), prediction_rows)
    if not gold_path.exists():
        write_csv(gold_path, list(gold_rows[0]), gold_rows)
    manifest = {
        "source_file": str(raw_path), "source_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "source_retrieved_at": payload.get("retrievedAt"),
        "source_notice_count": len(notices), "selected_notice_count": sample_size,
        "sampling": "uniform_without_replacement_sorted_ids_seed_20261019",
        "blind_review": "blind_review.csv excludes model predictions",
        "predictions": "predictions.csv is an UNVALIDATED heuristic baseline",
        "independent_gold": "gold_labels.csv is blank pending an independent reviewer",
        "attachment_coverage": "NOT VERIFIED; no tender annexes downloaded",
        "blind_text_normalization": "trailing whitespace removed from source description lines; original JSON preserved",
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(build(args.input, args.output_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
