"""Notice-ID-bound, fail-closed discovery of ORIGINAL public Hilma attachments.

Only exact public-attachments UUID URLs *present in the original notice XML*
are eligible for collection. Do not infer links from names, search snippets,
similar projects, old SAS tokens or unrelated documents. No portal login.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path

PUBLIC_HOST = "cdn.hankintailmoitukset.fi"
PUBLIC_PATH = re.compile(r"/public-attachments/[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}")
NOTICE_ID = re.compile(r"[0-9]{1,12}")
MAX_NOTICES = 10
MAX_ATTACHMENTS = 24
MAX_BYTES = 20 * 1024 * 1024
MAX_ZIP_FILES = 100
MAX_ZIP_UNCOMPRESSED = 80 * 1024 * 1024
URL_RE = re.compile(r"https://[^\s<>\"']+", re.I)

def validate_public_url(url: str) -> str:
    p = urllib.parse.urlsplit(url)
    if (p.scheme != "https" or p.hostname != PUBLIC_HOST or p.username or
            p.password or p.port or not PUBLIC_PATH.fullmatch(p.path) or p.query or p.fragment):
        raise ValueError("Not a canonical original Hilma public attachment URL")
    return url

def discover(xml: str, notice_id: str, source_sha256: str | None = None) -> dict:
    if not NOTICE_ID.fullmatch(notice_id):
        raise ValueError("Invalid notice ID")
    root = ET.fromstring(xml)
    # XML may contain explicit text links, including escaped XML entities.
    # Attribute values also count as original-source evidence.
    urls: set[str] = set()
    for node in root.iter():
        for raw in [node.text or "", *(node.attrib.values())]:
            for m in URL_RE.finditer(raw):
                candidate = m.group(0).rstrip(".,;)]}")
                try:
                    urls.add(validate_public_url(candidate))
                except ValueError:
                    continue
    xml_sha = hashlib.sha256(xml.encode("utf-8")).hexdigest()
    if source_sha256 is not None and source_sha256 != xml_sha:
        raise ValueError("Original notice XML SHA-256 mismatch")
    return {
        "notice_id": notice_id, "xml_sha256": xml_sha,
        "association": "LINK_EXPLICITLY_PRESENT_IN_ORIGINAL_NOTICE_XML",
        "attachment_count": len(urls),
        "attachments": [
            {"source_url": u, "notice_id": notice_id, "link_provenance": "ORIGINAL_XML",
             "source_status": "DISCOVERED_NOT_DOWNLOADED", "type": "UNKNOWN"}
            for u in sorted(urls)
        ],
        "complete_package": False, "verified_individual_contract_value": False,
        "eligibility": "CONDITIONAL_SOURCE_INCOMPLETE", "gold_label": "UNREVIEWED",
    }

class PublicRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_public_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def fetch_attachment(url: str, opener=None) -> tuple[bytes, str]:
    validate_public_url(url)
    opener = opener or urllib.request.build_opener(PublicRedirects)
    req = urllib.request.Request(url, headers={
        "User-Agent": "Urakkaluotsi-Hilma-NoticeAttachments/1.0",
        "Accept": "application/pdf,application/zip,application/octet-stream",
    })
    with opener.open(req, timeout=25) as resp:
        length = resp.headers.get("Content-Length")
        if length is not None and int(length) > MAX_BYTES:
            raise ValueError("Attachment exceeds byte cap")
        data = resp.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Attachment exceeds byte cap")
    if data.startswith(b"%PDF-"):
        return data, "PDF"
    if zipfile.is_zipfile(io.BytesIO(data)):
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            infos = z.infolist()
            if len(infos) > MAX_ZIP_FILES:
                raise ValueError("ZIP has too many entries")
            if sum(i.file_size for i in infos) > MAX_ZIP_UNCOMPRESSED:
                raise ValueError("ZIP decompression budget exceeded")
            for i in infos:
                name = i.filename.replace("\\", "/")
                if (name.startswith("/") or re.match(r"^[A-Za-z]:", name) or
                        ".." in name.split("/") or i.flag_bits & 1):
                    raise ValueError("Unsafe or encrypted ZIP entry")
        # Preserve ZIP intact; never extract its entries automatically.
        return data, "ZIP_UNEXTRACTED"
    raise ValueError("Unknown attachment format (not PDF or ZIP)")

def collect(records: list[dict], output: Path, *, fetcher=fetch_attachment) -> dict:
    if not 0 < len(records) <= MAX_NOTICES:
        raise ValueError("Notice count outside allowed range")
    output.mkdir(parents=True, exist_ok=True)
    seen: set[str] = set()
    count = 0
    results = []
    for record in records:
        notice_id = record["notice_id"]
        if not NOTICE_ID.fullmatch(notice_id) or notice_id in seen:
            raise ValueError("Invalid or duplicate notice ID")
        seen.add(notice_id)
        if record.get("association") != "LINK_EXPLICITLY_PRESENT_IN_ORIGINAL_NOTICE_XML":
            raise ValueError("Missing explicit original notice provenance")
        if not re.fullmatch(r"[0-9a-f]{64}", record.get("xml_sha256", "")):
            raise ValueError("Invalid original XML SHA-256")
        attachments = record.get("attachments") or []
        if len(attachments) > MAX_ATTACHMENTS:
            raise ValueError("Too many attachments in notice")
        for index, a in enumerate(attachments):
            count += 1
            if count > MAX_ATTACHMENTS:
                raise ValueError("Total attachment cap exceeded")
            url = validate_public_url(a["source_url"])
            if a.get("notice_id") != notice_id or a.get("link_provenance") != "ORIGINAL_XML":
                raise ValueError("Attachment lacks original notice ID binding")
            item = {"notice_id": notice_id, "source_xml_sha256": record["xml_sha256"],
                    "source_url": url, "link_provenance": "ORIGINAL_XML"}
            try:
                data, kind = fetcher(url)
                item.update({"format": kind, "sha256": hashlib.sha256(data).hexdigest(),
                             "bytes": len(data), "retrieved_at": datetime.now(timezone.utc).isoformat(),
                             "source_status": "VERIFIED_ORIGINAL_BYTES"})
                (output / f"notice_{notice_id}_attachment_{index + 1}.{ 'pdf' if kind == 'PDF' else 'zip'}").write_bytes(data)
            except Exception as exc:
                item.update({"source_status": "FETCH_FAILED", "error_type": type(exc).__name__})
            results.append(item)
    summary = {"notices": len(records), "attachment_urls_from_original_xml": count,
               "downloaded": sum(x["source_status"] == "VERIFIED_ORIGINAL_BYTES" for x in results),
               "complete_tender_packages": 0, "gold_positives": 0, "precision_at_30": None,
               "results": results}
    (output / "notice_attachments.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return summary

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--xml-dir", type=Path, required=True)
    p.add_argument("--notice-ids", nargs="+", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--download", action="store_true", help="Fetch only exact XML-linked public PDFs/ZIPs")
    args = p.parse_args()
    if not 0 < len(args.notice_ids) <= MAX_NOTICES or len(set(args.notice_ids)) != len(args.notice_ids):
        p.error("Provide 1..10 distinct notice IDs")
    records = []
    for ident in args.notice_ids:
        if not NOTICE_ID.fullmatch(ident):
            p.error("Invalid notice ID")
        path = args.xml_dir / f"{ident}.xml"
        if not path.is_file():
            p.error(f"Missing saved original XML: {ident}")
        records.append(discover(path.read_text(encoding="utf-8"), ident))
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {"selection_policy": "NOTICE_ID_ORIGINAL_XML_ONLY",
                "notices": records, "complete_tender_packages": 0,
                "gold_positives": 0, "precision_at_30": None}
    (args.output / "notice_link_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    if args.download:
        print(json.dumps(collect(records, args.output), ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"notice_ids": args.notice_ids,
                          "public_attachment_urls": sum(x["attachment_count"] for x in records),
                          "downloaded": 0, "complete_tender_packages": 0,
                          "gold_positives": 0, "precision_at_30": None}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
