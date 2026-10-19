"""Independent P0 acceptance gate: never score metadata or AI-silver as gold."""
import argparse,json
from pathlib import Path

def assess(source_universe:dict, gold_reviews:list[dict]) ->dict:
    ids={r["notice_id"] for r in source_universe["rows"]}
    seen=set()
    for g in gold_reviews:
        i=g.get("notice_id")
        if i not in ids or i in seen:raise ValueError("Foreign or duplicated review case")
        seen.add(i)
    independently_complete=[g for g in gold_reviews if g.get("independent_reviewer") and
        g.get("source_document_url") and g.get("source_excerpt") and
        g.get("label") in {"POSITIVE","NEGATIVE"} and
        g.get("review_status")=="ADJUDICATED"]
    return {"source_universe_size":len(ids),"independently_adjudicated":len(independently_complete),
      "reviewed_ranked_top30":0,"precision_at_30":None,
      "acceptance_80_percent":"NOT_MEASURED",
      "reason":"Frozen ranked top-30 source-adjudicated labels missing; do not promote metadata or AI judgments"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--universe",type=Path,required=True)
    p.add_argument("--reviews",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    report=assess(json.loads(a.universe.read_text(encoding="utf-8")),
         json.loads(a.reviews.read_text(encoding="utf-8"))["reviews"])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))
if __name__=="__main__":main()
