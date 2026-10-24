"""Build broad, deduplicated REAL Hilma notice discovery universe for P0.3d.

This does not fabricate 30-50 verified Uusimaa renovation jobs. Keeps entire
152-real-notice universe including negative examples and missing evidence.
"""
import argparse,json
from pathlib import Path

def build(snapshots):
    observed={}
    for source_name,notices in snapshots:
        for n in notices:
            ident=str(n["id"])
            if ident not in observed:
                observed[ident]={"notice_id":ident,"title":n.get("title"),
                    "description":n.get("description"),"published_at":n.get("publishedAt"),
                    "deadline_utc":n.get("deadline"),"cpv_codes":n.get("cpv_codes"),
                    "procedure_id":n.get("procedure_id"),
                    "estimated_value_metadata":n.get("estimated_value"),
                    "sources":[source_name],"source_verified_as_real_metadata":True,
                    "verified_worksite_municipality":None,"verified_renovation_scope":False,
                    "latest_notice_version_verified":False,"annexes_complete":False,
                    "individual_lot_value_verified":False,"eligibility_verified":False,
                    "gold_label":"UNREVIEWED"}
            elif source_name not in observed[ident]["sources"]:
                observed[ident]["sources"].append(source_name)
    rows=sorted(observed.values(),key=lambda r:int(r["notice_id"]))
    return {"schema_version":"p0-full-source-universe-v1","real_unique_notices":len(rows),
       "verified_uusimaa_renovation_jobs":0,"independently_gold_reviewed":0,
       "precision_at_30":None,"sampling_method":"COMPLETE_FROZEN_SOURCE_UNIVERSE_NOT_SELECTED_GOLD_HOLDOUT",
       "rows":rows}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",action="append",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    snapshots=[(str(path),json.loads(path.read_text(encoding="utf-8"))["notices"]) for path in a.source]
    data=build(snapshots)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in data.items() if k!="rows"},ensure_ascii=False))
if __name__=="__main__":main()
