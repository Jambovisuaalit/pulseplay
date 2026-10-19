"""Evaluate saved source XML against metadata-only predictions, without live calls.

Only evaluate actual source XML files supplied in --xml-dir, named <notice_id>.xml.
Missing XML is NOT evaluated, never a negative or a correct classification.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from classify_eforms_lots import classify_lots
from extract_eforms_evidence import parse_xml_evidence
from relevance_v2 import classify_notice


def evaluate(notices: list[dict], xml_dir: Path) -> dict:
    rows = []
    for notice in notices:
        ident = str(notice.get("id") or "")
        if not ident:
            raise ValueError("Notice without ID")
        source = xml_dir / f"{ident}.xml"
        old = classify_notice(notice)
        if not source.is_file():
            rows.append({"notice_id": ident, "source_xml_status": "NOT_EVALUATED",
                         "metadata_label": old["model_label"], "lot_labels": [],
                         "change": "NOT_MEASURED"})
            continue
        extracted = parse_xml_evidence(source.read_text(encoding="utf-8"), str(source))
        decisions = classify_lots(notice, extracted)
        rows.append({"notice_id": ident, "source_xml_status": "PARSED",
                     "metadata_label": old["model_label"],
                     "lot_labels": [{"lot_id": x["lot_id"], "label": x["model_label"],
                                     "area": x["area_status"], "size": x["size_status"],
                                     "scope": x["scope_status"],
                                     "source_pointer": x["source_pointer"]}
                                    for x in decisions],
                     "change": "LOT_EVIDENCE_ADDED" if decisions else "NO_LOTS_FOUND"})
    covered = sum(r["source_xml_status"] == "PARSED" for r in rows)
    return {
        "notices_total": len(rows), "source_xml_coverage": covered,
        "missing_source_xml": len(rows) - covered,
        "source_xml_lot_label_counts": dict(Counter(lot["label"] for r in rows for lot in r["lot_labels"])),
        "metadata_label_counts": dict(Counter(r["metadata_label"] for r in rows)),
        "rows": rows, "human_gold_count": 0,
        "official_precision": None, "official_recall": None,
        "accuracy_improvement_verified": False,
        "evaluation_status": "SOURCE_XML_COVERAGE_ONLY_NOT_GOLD",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", type=Path, required=True)
    p.add_argument("--xml-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    payload = json.loads(args.snapshot.read_text(encoding="utf-8"))
    result = evaluate(payload["notices"], args.xml_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "rows"}, ensure_ascii=False))

if __name__ == "__main__":
    main()
