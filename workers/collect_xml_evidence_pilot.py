"""Bounded original eForms retrieval and lot-level comparison, no attachments.

Fetch only preselected notice IDs from frozen samples. Uses HILMA_API_KEY.
No search endpoint, no PDF links, no customer contact. Saves original XML
privately as an Actions artifact, plus machine-readable results.
"""
from __future__ import annotations
import hashlib
import json
import os
import sys
from pathlib import Path
import requests
from extract_eforms_evidence import parse_xml_evidence
from classify_eforms_lots import classify_lots
from relevance_v2 import classify_notice

IDS = ["59188", "59230", "59375", "58444", "160596", "54620"]
ROOT = Path("data/validation")
OUT = Path("/tmp/urakkaluotsi_xml_eval")
URL = "https://api.hankintailmoitukset.fi/avp-eforms/external-read/v1/notice/"
MAX_CALLS = 6

def source_rows():
    result = {}
    for rel in ["snapshot_2026-10-19/hilma_raw.json", "holdout_52_2026-10-19/holdout_raw.json"]:
        for row in json.loads((ROOT / rel).read_text(encoding="utf-8"))["notices"]:
            if str(row.get("id")) in IDS:
                result[str(row["id"])] = row
    if len(result) != len(IDS):
        raise RuntimeError("Frozen sources do not contain all target IDs")
    return result

def main():
    key = os.environ.get("HILMA_API_KEY")
    if not key:
        raise RuntimeError("Missing HILMA_API_KEY")
    OUT.mkdir(parents=True, exist_ok=True)
    source = source_rows()
    result = []
    calls = 0
    for ident in IDS:
        calls += 1
        assert calls <= MAX_CALLS
        r = requests.get(URL + ident, headers={
            "Ocp-Apim-Subscription-Key": key, "Accept": "*/*",
            "User-Agent": "Urakkaluotsi-source-evidence-test/1.0",
        }, timeout=35, allow_redirects=False)
        entry = {"notice_id": ident, "http_status": r.status_code,
                 "metadata_label": classify_notice(source[ident])["model_label"]}
        if r.status_code != 200:
            entry["source_status"] = "FETCH_FAILED"
            result.append(entry)
            continue
        text = r.text
        if not text.lstrip().startswith("<"):
            try:
                from fetch_hilma import _find_xml_candidate
                text = _find_xml_candidate(r.json()) or ""
            except (ValueError, TypeError):
                text = ""
        if not text.startswith("<"):
            entry["source_status"] = "NO_XML_FOUND"
            result.append(entry)
            continue
        xml_path = OUT / (ident + ".xml")
        xml_path.write_text(text, encoding="utf-8")
        entry["source_xml_sha256"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        try:
            extracted = parse_xml_evidence(text, f"original_eforms_notice/{ident}.xml")
            classified = classify_lots(source[ident], extracted)
            entry["source_status"] = "PARSED"
            entry["lot_count"] = len(classified)
            entry["lots"] = [
                {"lot_id": d["lot_id"], "model_label": d["model_label"],
                 "area_status": d["area_status"], "scope_status": d["scope_status"],
                 "size_status": d["size_status"], "area_reason": d["area_reason"],
                 "scope_reason": d["scope_reason"], "source_pointer": d["source_pointer"],
                 "eforms_location_status": d["eforms_location_status"],
                 "eforms_size_status": d["eforms_size_status"],
                 "estimated_lot_value_eur_unverified": d["estimated_lot_value_eur_unverified"]}
                for d in classified]
        except Exception as exc:
            entry["source_status"] = "PARSE_FAILED"
            entry["parse_error_type"] = type(exc).__name__
        result.append(entry)
    summary = {"requested_ids": IDS, "api_calls": calls,
               "http_200": sum(x["http_status"] == 200 for x in result),
               "xml_parsed": sum(x.get("source_status") == "PARSED" for x in result),
               "real_source_gold_labels": 0,
               "official_precision": None, "official_recall": None,
               "no_customer_deliveries": True, "no_attachments": True,
               "results": result}
    (OUT / "source_comparison.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
