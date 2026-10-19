"""Two-call live Hilma original XML -> notice-bound public attachments pilot.

Only notice IDs preapproved in code. No portal logins, no arbitrary URL discovery,
no customer deliveries. Requires HILMA_API_KEY GitHub secret.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import requests
from collect_hilma_notice_attachments import discover, collect
from extract_eforms_document_links import extract as extract_document_links, audit_url_fields

IDS = ("59188", "59375")
URL = "https://api.hankintailmoitukset.fi/avp-eforms/external-read/v1/notice/"
MAX_API_CALLS = 2

def unwrap_xml(response: requests.Response) -> str:
    body = response.text.strip()
    if body.startswith("<"):
        return body
    try:
        from fetch_hilma import _find_xml_candidate
        return _find_xml_candidate(response.json()) or ""
    except (ValueError, TypeError, KeyError):
        return ""

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--download",action="store_true")
    args=p.parse_args()
    key=os.environ.get("HILMA_API_KEY")
    if not key:
        raise RuntimeError("HILMA_API_KEY secret required")
    args.output.mkdir(parents=True,exist_ok=True)
    records=[]
    responses=[]
    document_links=[]
    xml_url_field_audits=[]
    calls=0
    for notice_id in IDS:
        calls+=1
        assert calls<=MAX_API_CALLS
        try:
            response=requests.get(URL+notice_id,headers={
                "Ocp-Apim-Subscription-Key":key,
                "Accept":"*/*",
                "User-Agent":"Urakkaluotsi-NoticeBoundAttachments/1.0",
            },timeout=35,allow_redirects=False)
            entry={"notice_id":notice_id,"http_status":response.status_code}
            if response.status_code==200:
                xml=unwrap_xml(response)
                if xml.startswith("<"):
                    record=discover(xml,notice_id,verified_endpoint=True)
                    records.append(record)
                    document_links.append(extract_document_links(xml, notice_id=notice_id, source_pointer=f'original_hilma_notice/{notice_id}.xml'))
                    xml_url_field_audits.append({'notice_id':notice_id, **audit_url_fields(xml)})
                    entry.update({"source_status":"ORIGINAL_XML_PARSED",
                                  "original_xml_sha256":record["xml_sha256"],
                                  "explicit_public_attachment_links":record["attachment_count"]})
                else:
                    entry["source_status"]="NO_XML"
            else:
                entry["source_status"]="HTTP_ERROR"
        except (requests.RequestException,ValueError) as exc:
            entry={"notice_id":notice_id,"source_status":"FETCH_OR_PARSE_FAILED",
                   "error_type":type(exc).__name__}
        responses.append(entry)
    manifest={"source":"ORIGINAL_HILMA_EFORMS_XML","api_calls":calls,"max_api_calls":MAX_API_CALLS,
              "notices":records,"requests":responses,"document_link_evidence":document_links,
              "xml_url_field_audits":xml_url_field_audits,"complete_tender_packages":0,
              "gold_positives":0,"precision_at_30":None}
    (args.output/"notice_discovery.json").write_text(
        json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if args.download and records and sum(r["attachment_count"] for r in records):
        acquisition=collect(records,args.output)
        manifest["attachment_acquisition"]=acquisition
    else:
        manifest["attachment_acquisition"]={"downloaded":0,"reason":"NO_ORIGINAL_XML_LINKS_OR_DISCOVERY_ONLY"}
    (args.output/"notice_discovery.json").write_text(
        json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"api_calls":calls,"xml_parsed":len(records),
                      "public_attachment_links":sum(r["attachment_count"] for r in records),
                      "downloaded":manifest["attachment_acquisition"].get("downloaded",0),
                      "eforms_document_access_leads":sum(len(x["links"]) for x in document_links),
                      "xml_url_field_count":sum(x["url_field_count"] for x in xml_url_field_audits),
                      "complete_tender_packages":0,"gold_positives":0,
                      "precision_at_30":None},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
