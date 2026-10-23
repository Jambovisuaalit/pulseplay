"""Fail-closed Uusimaa tender package coverage queue.

The coverage report is about document availability, NOT eligibility, gold
labels or Precision@30. A URL to a portal is not a downloaded document.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

def assess(row: dict) -> dict:
    docs = row.get("source_documents") or []
    verified = [d for d in docs if d.get("access") == "VERIFIED_FULL_TEXT"
                and d.get("sha256") and d.get("retrieved_at") and d.get("source_url")]
    kinds = {d["type"] for d in verified}
    required = set(row["required_documents"])
    missing = sorted(required-kinds)
    complete = not missing and row.get("verified_single_contract_value") is True \
        and row.get("verified_company_eligibility") is True
    return {"case_id":row["case_id"],"region":row["region"],
            "source_verified_document_count":len(verified),
            "required_document_count":len(required),
            "missing_document_types":missing,
            "individual_contract_value_verified":row.get("verified_single_contract_value") is True,
            "company_eligibility_verified":row.get("verified_company_eligibility") is True,
            "complete_source_package":complete,
            "source_gold_label":"UNREVIEWED",
            "positive_gold_count_increment":0,
            "blocker":row.get("blocker","")}

def evaluate(data: dict) -> dict:
    rows = data["candidates"]
    ids=[r["case_id"] for r in rows]
    if len(ids)!=len(set(ids)):
        raise ValueError("Duplicate case IDs")
    reports=[assess(r) for r in rows]
    return {"candidates":len(reports),
            "complete_packages":sum(r["complete_source_package"] for r in reports),
            "source_gold_positives":0,"precision_at_30":None,
            "review_queue":reports}

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--queue",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=evaluate(json.loads(args.queue.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
