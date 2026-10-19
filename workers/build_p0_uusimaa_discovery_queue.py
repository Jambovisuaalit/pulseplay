"""P0.3 frozen Hilma metadata triage; NOT a gold or eligibility cohort.

Keep the original notice universe stable and document what evidence is still
missing. Municipality name in title/description is only an AI review lead:
it is NOT proof of worksite (could refer to contracting authority).
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

REGIONS = ("helsinki", "espoo", "vantaa", "kauniainen", "kirkkonummi")
CONSTRUCTION = re.compile(r"korjaus|saneeraus|remont|perusparann|maalaus|sisäilma|muutostyö", re.I)
OUT_SCOPE = re.compile(r"sillan|väylä|rataurak|maanrakennus|tieurak|huleves|putkilinja", re.I)

def triage(row: dict) -> dict:
    title = str(row.get("title") or "")
    description = str(row.get("description") or "")
    content = f"{title}\n{description}"
    # First-stage lead only. Company addresses and buyer city are NEVER a worksite.
    named = [city for city in REGIONS if re.search(r"(?<!\w)" + city + r"(?!\w)", content, re.I)]
    scope_lead = bool(CONSTRUCTION.search(content))
    out_scope_lead = bool(OUT_SCOPE.search(content))
    return {
        "notice_id": str(row["id"]),
        "title": title,
        "publication_time": row.get("publishedAt"),
        "deadline": row.get("deadline"),
        "procedure_id": row.get("procedure_id"),
        "location_text_leads": named,
        "location_status": "REQUIRES_ORIGINAL_LOT_WORKSITE_EVIDENCE",
        "scope_keyword_lead": scope_lead,
        "outside_scope_keyword_lead": out_scope_lead,
        "scope_status": "REQUIRES_ORIGINAL_TENDER_SCOPE",
        "estimated_value_metadata": row.get("estimated_value"),
        "individual_contract_value_verified": False,
        "document_access": "NOT_ASSESSED",
        "eligibility": "CONDITIONAL_SOURCE_INCOMPLETE",
        "gold_label": "UNREVIEWED",
        "queue_priority": 1 if named and scope_lead and not out_scope_lead else 2 if named else 3,
    }

def build(snapshot: dict) -> dict:
    notices = snapshot["notices"]
    ids = [str(x["id"]) for x in notices]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate source notice IDs")
    cases = [triage(x) for x in notices]
    cases.sort(key=lambda x: (x["queue_priority"], x["notice_id"]))
    # This is an exhaustive frozen-universe triage, not cherry-picked ranked results.
    return {
        "schema_version": "p0-3-frozen-universe-v1",
        "sample_policy": "ALL_FROZEN_NOTICES_NO_POSITIVE_LABELS",
        "snapshot_retrieved_at": snapshot.get("retrievedAt"),
        "source_count": len(cases),
        "textual_uusimaa_location_leads": sum(bool(x["location_text_leads"]) for x in cases),
        "priority_1_preliminary_leads": sum(x["queue_priority"] == 1 for x in cases),
        "verified_uusimaa_worksites": 0,
        "complete_tender_packages": 0,
        "independent_gold_positives": 0,
        "precision_at_30": None,
        "cases": cases,
    }

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--snapshot",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    report=build(json.loads(a.snapshot.read_text(encoding="utf-8")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="cases"},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
