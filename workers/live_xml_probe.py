"""One-shot Hilma XML probe: strictly <=3 HTTP requests, no attachments."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path

from eforms_document_audit import audit_eforms_xml, compare_index_deadline
from fetch_hilma import SEARCH_URL, FULL_NOTICE_URL, _find_xml_candidate

MAX_REQUESTS = 3
OUT = Path("data/validation/hilma_live_xml_probe.json")


class LimitedProbe:
    def __init__(self, session, api_key: str):
        if not api_key:
            raise RuntimeError("HILMA_API_KEY missing; no requests made")
        self.session = session
        self.headers = {"Ocp-Apim-Subscription-Key": api_key}
        self.attempted = 0

    def call(self, method: str, url: str, **kwargs):
        if self.attempted >= MAX_REQUESTS:
            raise RuntimeError("Hard budget exceeded: three total HTTP attempts")
        self.attempted += 1  # Counts failures, timeouts and 3xx too.
        response = self.session.request(
            method, url, headers=self.headers, timeout=20,
            allow_redirects=False, **kwargs,
        )
        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code} on request {self.attempted}")
        return response

    def run(self) -> dict:
        result = {"request_limit": MAX_REQUESTS, "requests_attempted": 0,
                  "xml_success_count": 0, "records": [], "status": "INCOMPLETE"}
        try:
            response = self.call("POST", SEARCH_URL, json={
                "search": "*", "top": 2, "skip": 0, "count": False,
                "orderby": "datePublished desc", "searchMode": "any",
                "queryType": "simple", "select": "noticeId,titleFi,datePublished,expirationDate",
                "filter": "mainType eq 'ContractNotices' and datePublished ge 2026-10-01T00:00:00Z",
            })
            notices = response.json().get("value") or []
            if not isinstance(notices, list):
                raise RuntimeError("Unexpected search response")
            seen: set[str] = set()
            selected = []
            for notice in notices:
                notice_id = str(notice.get("noticeId") or "").strip()
                if notice_id and notice_id not in seen:
                    seen.add(notice_id)
                    selected.append(notice)
                if len(selected) == 2:
                    break
            for notice in selected:
                if self.attempted >= MAX_REQUESTS:
                    break
                notice_id = str(notice["noticeId"])
                record = {"notice_id": notice_id, "indexed_deadline": notice.get("expirationDate"),
                          "xml_retrieved": False, "deadline_verified": False}
                result["records"].append(record)
                try:
                    response = self.call("GET", f"{FULL_NOTICE_URL}/{notice_id}")
                    if response.text.lstrip().startswith("<"):
                        xml_text = response.text
                    else:
                        xml_text = _find_xml_candidate(response.json())
                    if not xml_text:
                        raise ValueError("XML not present in response")
                    audit = audit_eforms_xml(xml_text)
                    comparison = compare_index_deadline(notice.get("expirationDate"), audit)
                    record.update({
                        "xml_retrieved": True,
                        "xml_sha256": hashlib.sha256(xml_text.encode("utf-8")).hexdigest(),
                        "deadline_verified": comparison["verified"],
                        "deadline_reason": comparison["reason"],
                        "xml_lot_deadlines": audit["deadlines"],
                        "document_links_seen": len(audit["document_leads"]),
                        "documents_status": "unknown",
                    })
                    result["xml_success_count"] += 1
                except Exception as exc:
                    record["error"] = str(exc)[:240]
            result["status"] = "COMPLETED" if len(selected) == 2 else "INCOMPLETE"
        except Exception as exc:
            result["error"] = str(exc)[:240]
        finally:
            result["requests_attempted"] = self.attempted
        return result


def main() -> None:
    import requests
    key = os.getenv("HILMA_API_KEY", "")
    if not key:
        raise RuntimeError("HILMA_API_KEY missing")
    session = requests.Session()
    probe = LimitedProbe(session, key)
    result = probe.run()
    result["completed_at_utc"] = dt.datetime.now(dt.timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "COMPLETED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
