"""Build a fail-closed, deduplicated review queue from 30 real Hilma notices.

This is a *source-description-based* queue, not an independently reviewed
relevance gold set. It must never mark eligibility or full documents verified.
No API calls and no customer deliveries.
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

UUSIMAA = frozenset({"Helsinki", "Espoo", "Vantaa", "Kauniainen", "Kirkkonummi"})
# The service ICP is small building-renovation firms: specialized lifts,
# infrastructure, parks, all-new buildings and multi-year street frameworks
# do not count as confirmed target jobs merely because they are in Uusimaa.
TARGET_SCOPE = frozenset({
    "BUILDING_MEP_ROOF_RENOVATION_COMPLEX",
    "RESIDENTIAL_FULL_RENOVATION_LARGE",
    "INTERIOR_ACOUSTICS_RENOVATION",
    "SECURITY_CLASSIFIED_COMPLEX_RENOVATION",
    "INTERIOR_CONVERSION_RENOVATION",
    "OFFICE_CONVERSION_RENOVATION",
    "DAYCARE_FULL_RENOVATION_SITE_VISIT_RESTRICTION",
    "CHURCH_TECHNICAL_RENOVATION",
})
CONDITIONAL_SPECIALIST = frozenset({
    "MULTISITE_HEATING_SPECIALIST",
    "ELEVATOR_REPLACEMENT_SPECIALIST",
})
# Some source-scope categories are potential positives but exceed likely
# capacity; review eligibility and lot values rather than marking them GO.
POTENTIAL_GROUPS = frozenset({"ESPOO_9_HEATING_WORKS","MAUNULA_CHURCH_TECH_RENOVATION"})

def build(data: dict, *, audit_now: datetime) -> dict:
    if audit_now.tzinfo is None:
        raise ValueError("audit_now requires timezone")
    records=data.get("records") or []
    if len(records) != 30 or len({r["notice_id"] for r in records}) != 30:
        raise ValueError("Expected 30 unique frozen source cases")
    output=[]
    for row in records:
        deadline=datetime.fromisoformat(row["deadline_utc"].replace("Z","+00:00"))
        cancelled=(row["cancellation_status"]=="EXPLICITLY_CANCELLED_IN_TITLE"
            or (row.get("version_review") or {}).get("delivery_state")=="EXCLUDE_CANCELLED")
        expired=deadline <= audit_now.astimezone(timezone.utc)
        region=row["worksite_municipality_metadata_review"]
        strength=row["worksite_evidence_strength"]
        location_explicit=strength.startswith("EXPLICIT")
        scope=row["scope_metadata_review"]
        version=row.get("version_review") or {}
        possible_group=row.get("potential_same_procurement_group")
        if cancelled:
            state="EXCLUDED_CANCELLED"
        elif expired:
            state="EXCLUDED_EXPIRED_SNAPSHOT_DEADLINE"
        elif region not in UUSIMAA:
            state="EXCLUDED_OUTSIDE_UUSIMAA"
        elif not location_explicit:
            state="HOLD_LOCATION_NOT_EXPLICIT"
        elif scope in TARGET_SCOPE:
            state="REVIEW_BUILDING_RENOVATION"
        elif scope in CONDITIONAL_SPECIALIST:
            state="REVIEW_SPECIALIST_SCOPE"
        else:
            state="EXCLUDED_NON_TARGET_SCOPE"
        output.append({
            "notice_id":row["notice_id"],"title":row["title"],
            "metadata_worksite_municipality":region,
            "metadata_location_evidence":row["worksite_description_metadata_review"],
            "metadata_location_strength":strength,
            "scope_description_class":scope,
            "source_excerpt":row["description_evidence_excerpt"],
            "deadline_utc":row["deadline_utc"],"snapshot_deadline_expired":expired,
            "cancelled_in_saved_notice":cancelled,
            "possible_same_procurement_group":possible_group,
            "official_cross_notice_version_link_verified":False,
            "portal_evidence_url":version.get("portal_notice_url"),
            "decision":state,
            "reviewed_original_full_eforms":False,
            "reviewed_complete_annexes":False,
            "individual_contract_value_verified":False,
            "bidder_eligibility_verified":False,
            "actual_live_status_verified":False,
            "independent_gold_label":"UNREVIEWED",
            "source_type":"SAVED_REAL_HILMA_NOTICE_DESCRIPTION",
        })
    output.sort(key=lambda r:(0 if r["decision"]=="REVIEW_BUILDING_RENOVATION" else 1 if r["decision"]=="REVIEW_SPECIALIST_SCOPE" else 2, r["notice_id"]))
    kept=[r for r in output if r["decision"].startswith("REVIEW_")]
    counts={state:sum(x["decision"]==state for x in output) for state in sorted({r["decision"] for r in output})}
    return {
        "schema_version":"p0.3d-dedup-review-queue-v1",
        "audit_as_of_utc":audit_now.astimezone(timezone.utc).isoformat(),
        "input_total":len(records),"unique_notice_count":len(records),
        "active_candidate_count":len(kept),
        "decision_counts":counts,
        "candidate_notice_ids":[r["notice_id"] for r in kept],
        "possible_duplicate_groups_pending_official_cross_reference": sorted(set(
            r["possible_same_procurement_group"] for r in output if r["possible_same_procurement_group"] in POTENTIAL_GROUPS)),
        "current_state_gate":"SNAPSHOT_ACTIVE_ONLY_NOT_LIVE_VERIFIED",
        "verified_active_eligible_jobs":0,
        "verified_complete_packages":0,
        "independent_gold_positives":0,
        "precision_at_30":None,
        "rows":output,
    }

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--as-of-utc",required=True)
    a=p.parse_args()
    asof=datetime.fromisoformat(a.as_of_utc.replace("Z","+00:00"))
    report=build(json.loads(a.input.read_text(encoding="utf-8")),audit_now=asof)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="rows"},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
