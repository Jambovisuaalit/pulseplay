"""Version/deadline fail-closed delivery filter for saved Hilma notices.

Only positive live status from a dedicated current-source verification
could authorize release; this worker intentionally produces REVIEW/HOLD only.
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path

def guard(data: dict,now: datetime)->dict:
    if now.tzinfo is None: raise ValueError("timezone-aware now required")
    rows=[]
    for r in data["rows"]:
        deadline=datetime.fromisoformat(r["last_known_deadline_local"])
        related=r.get("notices_with_related_versions",[])
        reasons=[]
        if deadline<=now.astimezone(deadline.tzinfo):reasons.append("DEADLINE_EXPIRED")
        if related: reasons.append("VERSION_RELATION_REQUIRES_SOURCE_VERIFICATION")
        if not r.get("current_version_authoritative_chain_verified"):reasons.append("LATEST_VERSION_UNVERIFIED")
        if not r.get("full_tender_annexes_verified"):reasons.append("ANNEXES_INCOMPLETE")
        if not r.get("company_eligibility_verified"):reasons.append("BIDDER_ELIGIBILITY_UNVERIFIED")
        if r.get("estimated_individual_lot_value_eur") is None:reasons.append("INDIVIDUAL_LOT_VALUE_UNVERIFIED")
        rows.append({"notice_id":r["notice_id"],"deadline_local":r["last_known_deadline_local"],
          "related_notice_ids":related,"hold_reasons":reasons,"customer_go":False,
          "decision":"EXCLUDE_EXPIRED" if "DEADLINE_EXPIRED" in reasons else "CONDITIONAL_REVIEW",
          "independent_gold_label":"UNREVIEWED"})
    return {"cases":len(rows),"expired":sum(x["decision"]=="EXCLUDE_EXPIRED" for x in rows),
            "customer_go_count":0,"precision_at_30":None,"rows":rows}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--as-of",required=True)
    a=p.parse_args()
    report=guard(json.loads(a.input.read_text(encoding="utf-8")),
                 datetime.fromisoformat(a.as_of.replace("Z","+00:00")))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"cases":report["cases"],"expired":report["expired"],
        "customer_go_count":0,"precision_at_30":None}))

if __name__=="__main__":main()
