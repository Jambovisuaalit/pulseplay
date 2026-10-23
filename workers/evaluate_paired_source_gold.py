"""Strict paired evaluation against independently adjudicated, source-cited labels.

No automatic gold creation. Unknown labels, incomplete sources and duplicate
cases are excluded and counted. Precision@30 requires >=30 evaluated ranked
predictions, source-gold coverage, and nonzero predicted positives.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

GOLD = {"POSITIVE", "NEGATIVE"}
PRED_POS = {"Relevantti", "Mahdollinen"}
PRED_NEG = {"Ei priorisoitu", "Epärelevantti"}

def evaluate(rows: list[dict]) -> dict:
    ids = [r["case_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate case_id")
    verified = [r for r in rows if r.get("gold_label") in GOLD
                and r.get("source_review_status") == "VERIFIED"
                and r.get("source_quote") and r.get("source_url")
                and r.get("baseline_label") in PRED_POS | PRED_NEG
                and r.get("enhanced_label") in PRED_POS | PRED_NEG]
    excluded = len(rows) - len(verified)
    def counts(version):
        c = Counter()
        for r in verified:
            prediction = r[version] in PRED_POS
            actual = r["gold_label"] == "POSITIVE"
            c["TP" if prediction and actual else "FP" if prediction else "FN" if actual else "TN"] += 1
        positives = c["TP"] + c["FP"]
        return {"tp":c["TP"],"fp":c["FP"],"fn":c["FN"],"tn":c["TN"],
                "precision":c["TP"]/positives if positives else None,
                "recall":c["TP"]/(c["TP"]+c["FN"]) if c["TP"]+c["FN"] else None}
    baseline = counts("baseline_label")
    enhanced = counts("enhanced_label")
    # These are not a rank-ordered 30-item sample. Do not extrapolate.
    return {"total_cases":len(rows),"paired_source_verified":len(verified),
            "excluded_unknown_or_incomplete":excluded,
            "verified_gold_positives":sum(r["gold_label"]=="POSITIVE" for r in verified),
            "verified_gold_negatives":sum(r["gold_label"]=="NEGATIVE" for r in verified),
            "baseline":baseline,"enhanced":enhanced,
            "paired_precision_difference":enhanced["precision"]-baseline["precision"]
               if baseline["precision"] is not None and enhanced["precision"] is not None else None,
            "precision_at_30":None,
            "precision_at_30_status":"NOT_MEASURED_REQUIRES_INDEPENDENT_RANKED_30_WITH_GOLD",
            "improvement_verified":False}

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--cases",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    data=json.loads(a.cases.read_text(encoding="utf-8"))
    result=evaluate(data["cases"])
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
