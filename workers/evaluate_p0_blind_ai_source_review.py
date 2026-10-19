"""AI-assisted, source-cited blind review gate (no human reviewer required).

AI labels are SILVER, not independently human-adjudicated GOLD.
The ranking must be frozen before reviews; only reviewed, evidenced cases
with complete original tender documents can be scored conclusively.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

LABELS={"RELEVANT","NOT_RELEVANT","UNKNOWN"}
REQUIRED=("worksite","scope","deadline","contract_value","eligibility")
def digest(obj):
    return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def freeze(ranked: list[dict])->dict:
    ids=[str(x["notice_id"]) for x in ranked]
    if len(ids)<30 or len(ids)!=len(set(ids)):raise ValueError("Need >=30 unique frozen ranking entries")
    # Input is explicitly a ranked sequence from the scoring algorithm;
    # no AI review decisions are used to select or reorder these IDs.
    top=ids[:30]
    return {"ranked_id_sha256":digest(ids),"top30_ids":top,
            "top30_sha256":digest(top),"sample_size":30,
            "selection":"MODEL_RANKED_BEFORE_REVIEW","labels_visible_during_freeze":False}

def grade(frozen:dict,reviews:list[dict])->dict:
    top=frozen["top30_ids"]
    if len(top)!=30 or frozen["top30_sha256"]!=digest(top):
        raise ValueError("Invalid or altered frozen top30")
    seen=set()
    result={}
    for r in reviews:
        ident=str(r.get("notice_id",""))
        if ident not in top or ident in seen:raise ValueError("Foreign or repeated reviewed ID")
        seen.add(ident)
        evidence=r.get("evidence") or {}
        sources_complete=all(isinstance(evidence.get(k),dict)
            and evidence[k].get("source_url")
            and evidence[k].get("source_excerpt")
            and evidence[k].get("access_status")=="ORIGINAL_SOURCE_VERIFIED"
            for k in REQUIRED)
        is_ai=(r.get("reviewer_type")=="AI_BLINDED_SOURCE_REVIEW"
            and not r.get("rank_seen") and not r.get("model_prediction_seen"))
        complete=is_ai and sources_complete and r.get("label") in {"RELEVANT","NOT_RELEVANT"}\
            and r.get("independent_source_check") is True
        result[ident]={"label":r.get("label"),"complete":complete}
    complete30=len(result)==30 and all(x["complete"] for x in result.values())
    positives=sum(result[k]["label"]=="RELEVANT" for k in top) if complete30 else None
    return {"metric":"AI_SOURCE_REVIEWED_PRECISION_AT_30",
       "reviewer_category":"AI_SILVER_NOT_HUMAN_GOLD",
       "top30_hash":frozen["top30_sha256"],
       "labels_submitted":len(result),
       "fully_evidenced_ai_reviews":sum(x["complete"] for x in result.values()),
       "missing_or_incomplete":30-sum(x["complete"] for x in result.values()),
       "ai_precision_at_30":positives/30 if complete30 else None,
       "ai_80_percent_gate":"PASS" if complete30 and positives>=24 else "FAIL" if complete30 else "NOT_MEASURED",
       "human_gold_precision_at_30":None,
       "customer_eligibility_confirmed":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ranked",type=Path,required=True)
    p.add_argument("--reviews",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    frozen=freeze(json.loads(a.ranked.read_text(encoding="utf-8"))["ranked"])
    reviews=json.loads(a.reviews.read_text(encoding="utf-8"))["reviews"]
    report={"frozen":frozen,"evaluation":grade(frozen,reviews)}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report["evaluation"],ensure_ascii=False))
if __name__=="__main__":main()
