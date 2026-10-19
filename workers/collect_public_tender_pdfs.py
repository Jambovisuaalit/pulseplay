"""Bounded, allowlisted, public PDF acquisition for Urakkaluotsi validation.

No search crawling, portal login, cookies, email, or customer delivery.
Only URLs explicitly frozen in the input manifest. Every downloaded byte is
SHA-256 fingerprinted; extracted text is evidence, never eligibility GO.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from pypdf import PdfReader
from extract_public_pdf_requirements import leads_by_page

MAX_DOCUMENTS = 12
MAX_BYTES = 12 * 1024 * 1024
MAX_PAGES = 80
ALLOWED_HOSTS = frozenset({"web28.aanekoski.fi", "tarjouspalvelu.fi", "cdn.hankintailmoitukset.fi"})
PDF_HEADER = b"%PDF-"

class GuardedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        host = urllib.parse.urlsplit(newurl).hostname
        if host not in ALLOWED_HOSTS or urllib.parse.urlsplit(newurl).scheme != "https":
            raise ValueError("Redirect target outside allowlist")
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def validate_url(url: str) -> None:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_HOSTS:
        raise ValueError("Only explicitly allowlisted HTTPS public PDF hosts are accepted")
    if parsed.username or parsed.password or parsed.port:
        raise ValueError("URL credentials and custom ports prohibited")
    if not (parsed.path.lower().endswith(".pdf") or
            (parsed.hostname == "tarjouspalvelu.fi" and parsed.path.startswith("/Julkiset/AvaaViesTied/")) or
            (parsed.hostname == "cdn.hankintailmoitukset.fi" and
             re.fullmatch(r"/public-attachments/[0-9a-fA-F-]{36}", parsed.path))):
        raise ValueError("Manifest must point to an allowlisted public PDF endpoint")

def fetch_pdf(url: str, opener=None) -> bytes:
    validate_url(url)
    opener = opener or urllib.request.build_opener(GuardedRedirect)
    req = urllib.request.Request(url, headers={"User-Agent":"Urakkaluotsi-PublicEvidencePilot/1.0","Accept":"application/pdf"})
    with opener.open(req, timeout=25) as response:
        content_length = response.headers.get("Content-Length")
        if content_length and int(content_length) > MAX_BYTES:
            raise ValueError("PDF exceeds size cap")
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES or not data.startswith(PDF_HEADER):
        raise ValueError("Not a PDF or PDF too large")
    return data

def extract_pdf_text(data: bytes) -> tuple[str, int]:
    reader = PdfReader(io.BytesIO(data), strict=False)
    if reader.is_encrypted or len(reader.pages) > MAX_PAGES:
        raise ValueError("Encrypted or excessive PDF pages")
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        pages.append(f"[[PAGE {index}]]\n{page.extract_text(extraction_mode='plain') or ''}")
    return "\n\n".join(pages), len(reader.pages)

def collect(manifest: dict, out: Path) -> dict:
    docs = manifest.get("documents") or []
    if not 0 < len(docs) <= MAX_DOCUMENTS:
        raise ValueError("Manifest must contain 1..12 documents")
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for entry in docs:
        ident = entry["document_id"]
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", ident):
            raise ValueError("Unsafe document ID")
        url = entry["url"]
        item = {"document_id": ident, "candidate_id": entry["candidate_id"],
                "source_url": url, "source_status": "NOT_EVALUATED"}
        try:
            data = fetch_pdf(url)
            item["sha256"] = hashlib.sha256(data).hexdigest()
            item["retrieved_at"] = datetime.now(timezone.utc).isoformat()
            item["bytes"] = len(data)
            (out / f"{ident}.pdf").write_bytes(data)
            text, pages = extract_pdf_text(data)
            (out / f"{ident}.txt").write_text(text, encoding="utf-8")
            lead_report = leads_by_page(text, url)
            (out / f"{ident}.requirements.json").write_text(json.dumps(lead_report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            item["requirement_lead_counts"] = {k:len(v) for k,v in lead_report["categories"].items()}
            item["pages"] = pages
            item["text_characters"] = len(text)
            item["source_status"] = "VERIFIED_FULL_TEXT" if len(text.strip()) >= 250 else "PDF_TEXT_INSUFFICIENT"
            item["source_type"] = entry["type"]
            item["document_coverage"] = "SINGLE_DOCUMENT_ONLY_NOT_COMPLETE_PACKAGE"
        except (ValueError, OSError, urllib.error.URLError, Exception) as exc:
            item["source_status"] = "FETCH_OR_PARSE_FAILED"
            item["error_type"] = type(exc).__name__
        results.append(item)
    report = {"schema_version":"1","selection_policy":manifest.get("selection"),
              "total":len(results),
              "full_text_documents":sum(x["source_status"]=="VERIFIED_FULL_TEXT" for x in results),
              "complete_tender_packages":0,
              "source_review_ready":0,
              "independent_gold_positives":0,
              "official_precision_at_30":None,
              "results":results}
    (out / "acquisition.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(collect(json.loads(a.manifest.read_text(encoding="utf-8")),a.output),ensure_ascii=False,indent=2))
