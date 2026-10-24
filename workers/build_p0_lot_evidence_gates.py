"""Normalize nine source-gated notices into explicitly unverified work-package leads.

Only an explicit original notice/annex lot ID may establish a separate lot.
Never split multiple addresses or nine properties into nine independently
priced lots. This module makes no network requests or customer decisions.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

def build(source: dict) -> dict:
    notices=source["rows"]
    if len(notices)!=9 or len({x["notice_id"] for x in notices})!=9:
        raise ValueError("Expected exactly nine distinct original notices")
    rows=[]
    for item in notices:
        if item.get("estimated_individual_lot_value_eur") is not None or item.get("company_eligibility_verified"):
            raise ValueError("Source data unexpectedly claims verified price or eligibility")
        multi=item["notice_id"]=="59464"
        lot={
            "lot_key":f"{item['notice_id']}:UNALLOCATED_WORK_PACKAGE",
            "lot_id":None,
            "lot_identity_status":"NOT_VERIFIED_FROM_ORIGINAL_NOTICE",
            "lot_separation_status":"MULTIPLE_LOCATIONS_NOT_PROOF_OF_SEPARATE_LOTS" if multi else "UNKNOWN_SINGLE_OR_MULTIPLE_LOTS",
            "source_notice_id":item["notice_id"],
            "source_original_lot_xpath":None,
            "scope_description_lead":item["scope"],
            "individual_lot_value_eur":None,
            "value_source_url":None,
            "value_source_status":"MISSING_OR_UNVERIFIED",
            "value_within_target_icp":"UNKNOWN",
            "tender_documents_complete":False,
            "eligibility_terms_complete":False,
            "required_evidence_checks":[
                "FULL_ORIGINAL_NOTICE_AND_REVISIONS",
                "OFFICIAL_LOT_IDENTIFIERS_AND_SEPARATE_SCOPE",
                "SOURCE_VERIFIED_LOT_PRICE_OR_PRICE_BAND",
                "BIDDER_TURNOVER_INSURANCE_REFERENCES",
                "MANDATORY_SITE_VISITS_IF_APPLICABLE",
                "COMPLETE_TENDER_ANNEXES",
            ],
            "decision":"CONDITIONAL_SOURCE_INCOMPLETE",
            "gold_label":"UNREVIEWED",
        }
        rows.append({
            "notice_id":item["notice_id"],
            "title":item["title"],
            "portal_url":item["portal_url"],
            "last_known_deadline_local":item["last_known_deadline_local"],
            "deadline_live_verified":False,
            "latest_official_version_verified":item["current_version_authoritative_chain_verified"],
            "related_notice_ids":item["notices_with_related_versions"],
            "worksite_region_metadata":item["location"],
            "public_eligibility_leads":item["eligibility_conditions_publicly_visible"],
            "bidder_eligibility_verified":False,
            "lots":[lot],
            "lot_count_verified":False,
            "multiple_lot_aggregation_permitted":False,
            "delivery_decision":"HOLD_NO_GO",
        })
    return {
        "schema_version":"p0-lot-gates-v1",
        "input_notice_count":len(rows),
        "work_package_placeholders":sum(len(x["lots"]) for x in rows),
        "official_lots_verified":0,
        "complete_packages":0,
        "bidder_eligibility_passes":0,
        "customer_go_count":0,
        "independent_gold_positives":0,
        "precision_at_30":None,
        "rows":rows,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=build(json.loads(args.input.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="rows"},ensure_ascii=False))

if __name__=="__main__":main()
