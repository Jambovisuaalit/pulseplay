"""Exactly two known Hilma eForms reads, no search, attachments or retries.

The index deadlines come from the preceding 2026-10-19 bounded search,
so a match confirms agreement with that saved snapshot, not live freshness.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path

from eforms_document_audit import audit_eforms_xml, compare_index_deadline
from fetch_hilma import FULL_NOTICE_URL, _find_xml_candidate

TARGETS = (
    ("59709", "2026-11-20T10:00:00Z"),
    ("59708", "2026-11-16T10:00:00Z"),
)
OUT = Path("data/validation/hilma_known_xml")


def verify(session, api_key: str, output_dir: Path = OUT) -> dict:
    if not api_key:
        raise RuntimeError("HILMA_API_KEY missing; zero calls")
    output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "request_limit": 2,
        "requests_attempted": 0,
        "source_index_snapshot": "2026-10-19 initial 3-call probe",
        "records": [],
        "status": "INCOMPLETE",
    }
    try:
        for notice_id, indexed_deadline in TARGETS:
            record = {"notice_id": notice_id, "indexed_deadline": indexed_deadline,
                      "xml_retrieved": False, "deadline_verified": False,
                      "documents_status": "unknown"}
            result["records"].append(record)
            # Count BEFORE the request. No redirection or retry may expand it.
            if result["requests_attempted"] >= 2:
                raise RuntimeError("Two-request hard limit exceeded")
            result["requests_attempted"] += 1
            try:
                response = session.request(
                    "GET", f"{FULL_NOTICE_URL}/{notice_id}",
                    headers={"Ocp-Apim-Subscription-Key": api_key},
                    timeout=20, allow_redirects=False,
                )
                if response.status_code != 200:
                    raise ValueError(f"HTTP {response.status_code}")
                xml = (response.text if response.text.lstrip().startswith("<")
                       else _find_xml_candidate(response.json()))
                if not xml:
                    raise ValueError("XML missing from eForms response")
                audit = audit_eforms_xml(xml)
                comparison = compare_index_deadline(indexed_deadline, audit)
                # Preserve a byte-for-byte UTF-8 record of the parsed XML for offline re-audit.
                # Never retrieve any URL found within the XML document.
                xml_bytes = xml.encode("utf-8")
                xml_name = f"notice_{notice_id}.xml"
                (output_dir / xml_name).write_bytes(xml_bytes)
                record.update({
                    "xml_retrieved": True,
                    "xml_filename": xml_name,
                    "xml_sha256": hashlib.sha256(xml_bytes).hexdigest(),
                    "xml_lot_deadlines": audit["deadlines"],
                    "deadline_verified": comparison["verified"],
                    "deadline_reason": comparison["reason"],
                    "document_links_seen": len(audit["document_leads"]),
                })
            except Exception as exc:
                record["error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
        result["status"] = "COMPLETED"
    finally:
        result["completed_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
        (output_dir / "result.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    return result


def main() -> None:
    import requests
    result = verify(requests.Session(), os.environ.get("HILMA_API_KEY", ""))
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "COMPLETED" or any(not row["xml_retrieved"] for row in result["records"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
