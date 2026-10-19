"""Extract source-pathed tender-document access references from saved eForms XML.

Links are evidence leads, not proof of access, verified attachments, notice
eligibility or independent gold. Ignore generic organisation and unrelated URLs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

TENDER_NODES = frozenset({
    "TenderDocumentReference", "AccessTools", "AccessTool", "ProcurementDocuments",
    "ProcurementDocument", "TenderingTerms", "CallForTendersDocumentReference",
    "DocumentReference", "DocumentLocation", "URI", "WebsiteURI", "EndpointURI",
})
LINK_RE = re.compile(r"https?://[^\s<>\"']+", re.I)
PORTAL_HOSTS = ("tarjouspalvelu.fi", "hankintailmoitukset.fi", "cloudia.fi")
PUBLIC_HILMA = "cdn.hankintailmoitukset.fi"

def local(tag: str) -> str:
    return tag.rsplit("}",1)[-1]

def category(url: str) -> str:
    try:
        u = urllib.parse.urlsplit(url)
        if u.scheme != "https" or not u.hostname or u.username or u.password:
            return "ACCESS_RESTRICTED_OR_UNKNOWN"
        host = u.hostname.lower()
        if host == PUBLIC_HILMA and re.fullmatch(r"/public-attachments/[0-9a-fA-F-]{36}",u.path) and not u.query:
            return "DIRECT_PUBLIC_DOCUMENT"
        if any(host == h or host.endswith("."+h) for h in PORTAL_HOSTS):
            return "PUBLIC_PORTAL"
        return "ACCESS_RESTRICTED_OR_UNKNOWN"
    except ValueError:
        return "ACCESS_RESTRICTED_OR_UNKNOWN"

def extract(xml: str, *, notice_id: str, source_pointer: str) -> dict:
    if not re.fullmatch(r"\d{1,12}", notice_id):
        raise ValueError("Invalid notice ID")
    root=ET.fromstring(xml)
    sha=hashlib.sha256(xml.encode("utf-8")).hexdigest()
    leads=[]
    seen=set()
    def visit(node: ET.Element, path: str, context: tuple[str,...]) -> None:
        tag=local(node.tag)
        next_context=context+(tag,)
        # Only actual procurement/tender document contexts count; generic
        # WebsiteURI of an organisation is NOT necessarily document access.
        relevant=any(n in {"TenderDocumentReference","AccessTools","AccessTool","ProcurementDocuments",
            "ProcurementDocument","CallForTendersDocumentReference","DocumentReference",
            "DocumentLocation"} for n in next_context) or (
            "TenderingTerms" in next_context and tag in {"URI","WebsiteURI","EndpointURI","DocumentLocation"})
        if relevant:
            fields=[("text",node.text or "")]+[("@"+local(k),v) for k,v in node.attrib.items()]
            for field,raw in fields:
                for m in LINK_RE.finditer(raw):
                    url=m.group(0).rstrip(".,;)]}")
                    key=(path,field,url)
                    if key in seen: continue
                    seen.add(key)
                    leads.append({"url":url,"kind":category(url),"notice_id":notice_id,
                                  "source_pointer":f"{source_pointer}#{path}/{field}",
                                  "source_xml_sha256":sha,
                                  "access_verified":False,"document_complete":False,
                                  "evidence_status":"SOURCE_LINK_ONLY"})
        counts={}
        for child in node:
            child_tag=local(child.tag)
            counts[child_tag]=counts.get(child_tag,0)+1
            visit(child,f"{path}/{child_tag}[{counts[child_tag]}]",next_context)
    visit(root,"/"+local(root.tag)+"[1]",())
    return {"notice_id":notice_id,"source_pointer":source_pointer,"source_xml_sha256":sha,
            "links":leads,"counts":{k:sum(r["kind"]==k for r in leads) for k in
                ("DIRECT_PUBLIC_DOCUMENT","PUBLIC_PORTAL","ACCESS_RESTRICTED_OR_UNKNOWN")},
            "package_complete":False,"gold_label":"UNREVIEWED","precision_at_30":None}

def audit_url_fields(xml: str) -> dict:
    """Enumerate XML URL locations for coverage diagnosis; do not output full URLs or query strings.

    This is not a claim of document access. Hostname and local XML tag paths
    are structural diagnostics, not download requests.
    """
    root=ET.fromstring(xml)
    rows=[]
    def walk(node: ET.Element, path: str) -> None:
        fields=[("text",node.text or "")]+[("@"+local(k),v) for k,v in node.attrib.items()]
        for field,raw in fields:
            for m in LINK_RE.finditer(raw):
                u=m.group(0).rstrip(".,;)]}")
                try:
                    p=urllib.parse.urlsplit(u)
                    host=p.hostname.lower() if p.hostname else ""
                except ValueError:
                    host=""
                rows.append({"xml_path":path+"/"+field,"host":host,
                             "url_class":category(u),
                             "document_context_candidate":any(s in path for s in (
                                 "Tender", "Document", "AccessTools", "ExternalReference"))})
        counts={}
        for child in node:
            tag=local(child.tag)
            counts[tag]=counts.get(tag,0)+1
            walk(child,path+"/"+tag+f"[{counts[tag]}]")
    walk(root,"/"+local(root.tag)+"[1]")
    return {"url_field_count":len(rows),"url_fields":rows[:100],
            "truncated":len(rows)>100}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--xml-dir",type=Path,required=True)
    p.add_argument("--notice-ids",nargs="+",required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if len(a.notice_ids)>10 or len(set(a.notice_ids))!=len(a.notice_ids):
        p.error("At most ten unique IDs")
    results=[]
    for ident in a.notice_ids:
        path=a.xml_dir / f"{ident}.xml"
        results.append(extract(path.read_text(encoding="utf-8"),notice_id=ident,source_pointer=f"original_hilma_notice/{ident}.xml"))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps({"notices":results,"gold_positives":0,
        "precision_at_30":None},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"notices":len(results),"links":sum(len(x["links"]) for x in results),
        "gold_positives":0,"precision_at_30":None},ensure_ascii=False))

if __name__=="__main__": main()
