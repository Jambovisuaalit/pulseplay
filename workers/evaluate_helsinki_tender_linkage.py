"""Source-only gate for two historical Helsinki tender document packages.

Never infer notice IDs, ZIP download URLs, contract value or positive gold labels
from a document index or from a title match.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

TARGETS = {"HELSINKI_POHJOLA_4F_2020", "HELSINKI_USPENSKI_INTERIOR"}

def assess(row: dict) -> dict:
    docs = row.get("required_building_lot_documents") or []
    missing = [d["name"] for d in docs if d["status"] not in
               {"PUBLIC_FULL_TEXT_VERIFIED", "PUBLIC_FULL_TEXT_OBSERVED"}]
    notice_ok = row.get("notice_link_status") == "VERIFIED_ORIGINAL_NOTICE_ID" and bool(row.get("notice_id"))
    value = row.get("verified_individual_lot_value_eur")
    value_ok = type(value) in (int, float) and 10000 <= value <= 250000 and row.get("value_source_status") == "VERIFIED_PRIMARY_SOURCE"
    complete = not missing and notice_ok and value_ok
    return {
        "case_id": row["case_id"], "verified_original_notice_link": notice_ok,
        "missing_documents": missing, "verified_lot_value_eur": value if value_ok else None,
        "complete_package": complete, "eligibility_decision": "REQUIRES_INDEPENDENT_REVIEW" if complete else "CONDITIONAL_SOURCE_INCOMPLETE",
        "gold_label": "UNREVIEWED", "precision_at_30": None,
    }

def evaluate(data: dict) -> dict:
    targets = [x for x in data["candidates"] if x["case_id"] in TARGETS]
    if len(targets) != len(TARGETS):
        raise ValueError("Both Helsinki cases required")
    results = [assess(x) for x in targets]
    return {"cases": len(results), "complete_packages": sum(x["complete_package"] for x in results),
            "independent_gold_positives": 0, "precision_at_30": None, "results": results}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--registry", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(evaluate(json.loads(args.registry.read_text(encoding="utf-8"))), ensure_ascii=False, indent=2))
