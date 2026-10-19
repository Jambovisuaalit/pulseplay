"""Build a source-only, auditable lot review queue from SAVED eForms XML.

No API calls, predictions, or gold labels. Source XML is never rewritten.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from extract_eforms_evidence import parse_xml_evidence

FIELDS = (
    "source_file", "source_sha256", "notice_id", "lot_id", "source_pointer",
    "worksite_city_text", "worksite_municipality", "location_status",
    "primary_scope_text", "scope_status", "estimated_lot_value_text",
    "estimated_lot_value_currency", "size_status", "missing_fields",
    "review_status", "reviewer_evidence", "gold_label",
)


def build_queue(input_dir: Path, output_dir: Path) -> dict:
    if not input_dir.is_dir():
        raise ValueError("Input directory does not exist")
    sources = sorted(p for p in input_dir.rglob("*.xml") if p.is_file())
    if not sources:
        raise ValueError("No saved XML files found; do not fabricate source records")
    rows = []
    seen = set()
    manifests = []
    for source in sources:
        raw = source.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        relative = source.relative_to(input_dir).as_posix()
        try:
            extracted = parse_xml_evidence(raw.decode("utf-8-sig"), relative)
        except Exception as exc:
            raise ValueError(f"Unable to parse saved XML {relative}: {exc}") from exc
        if not extracted["lots"]:
            raise ValueError(f"No ProcurementProjectLot in {relative}")
        manifests.append({"source_file": relative, "sha256": digest, "lot_count": len(extracted["lots"])})
        for lot in extracted["lots"]:
            key = (relative, str(lot["lot_id"]))
            if key in seen:
                raise ValueError(f"Duplicate lot ID in source: {key}")
            seen.add(key)
            missing = []
            if lot["location_status"] == "UNKNOWN":
                missing.append("WORKSITE_LOCATION")
            if lot["scope_status"] == "UNKNOWN":
                missing.append("PRIMARY_SCOPE")
            if lot["size_status"] != "VERIFIED_SINGLE_CONTRACT_VALUE":
                missing.append("VERIFIED_SINGLE_CONTRACT_VALUE")
            missing.extend(("ANNEXES", "ELIGIBILITY_REQUIREMENTS", "DEADLINE"))
            rows.append({
                "source_file": relative,
                "source_sha256": digest,
                "notice_id": source.stem,
                "lot_id": lot["lot_id"],
                "source_pointer": lot["source_pointer"],
                "worksite_city_text": lot["worksite_city_text"],
                "worksite_municipality": lot["worksite_municipality"] or "",
                "location_status": lot["location_status"],
                "primary_scope_text": lot["primary_scope_text"],
                "scope_status": lot["scope_status"],
                "estimated_lot_value_text": lot["estimated_lot_value_text"],
                "estimated_lot_value_currency": lot["estimated_lot_value_currency"],
                "size_status": lot["size_status"],
                "missing_fields": ";".join(missing),
                "review_status": "NOT_EVALUATED",
                "reviewer_evidence": "",
                "gold_label": "",
            })
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "source_review_queue.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "input_source_count": len(sources),
        "lot_count": len(rows),
        "source_files": manifests,
        "independent_gold_count": 0,
        "precision": "NOT MEASURED",
        "source_only": True,
        "new_holdout": False,
        "customer_go_verified": False,
    }
    (output_dir / "source_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(build_queue(args.input_dir, args.output_dir), ensure_ascii=False))
