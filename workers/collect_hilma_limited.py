"""Single Hilma search call, maximum 200 results, zero follow-up calls or attachments."""
import datetime as dt
import json
import os
from pathlib import Path
import requests

CODES = ("45000000", "45200000", "45400000", "45450000")
URL = "https://api.hankintailmoitukset.fi/avp/eformnotices/docs/search"

def main():
    key = os.environ["HILMA_API_KEY"]
    now = dt.datetime.now(dt.timezone.utc)
    cutoff = (now - dt.timedelta(days=30)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    cpv = "(" + " or ".join("search.ismatch('%s', 'cpvCodes')" % code for code in CODES) + ")"
    fields = ("noticeId,titleFi,organisationNameFi,descriptionFi,cpvCodes,"
              "datePublished,expirationDate,estimatedValue,procedureId")
    body = {
        "search": "*", "top": 200, "skip": 0, "count": True,
        "orderby": "datePublished desc", "searchMode": "any",
        "queryType": "simple", "select": fields,
        "filter": f"datePublished ge {cutoff} and mainType eq 'ContractNotices' and {cpv}",
    }
    # No retries. Exactly one API call even if the server returns an error.
    response = requests.post(URL, json=body, headers={
        "Accept": "application/json", "Ocp-Apim-Subscription-Key": key,
    }, timeout=60)
    audit = {
        "retrievedAt": now.isoformat(), "api_calls": 1,
        "http_status": response.status_code, "max_results": 200,
        "xml_requests": 0, "attachment_requests": 0, "cpv_codes": list(CODES),
    }
    audit_path = Path("data/validation/hilma_collection_audit.json")
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    if not response.ok:
        audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
        response.raise_for_status()
    result = response.json()
    notices = [{
        "id": str(row.get("noticeId") or ""),
        "title": row.get("titleFi"), "description": row.get("descriptionFi"),
        "organisation": row.get("organisationNameFi"),
        "publishedAt": row.get("datePublished"), "deadline": row.get("expirationDate"),
        "cpv_codes": row.get("cpvCodes") or [], "estimated_value": row.get("estimatedValue"),
        "procedure_id": row.get("procedureId"),
    } for row in result.get("value") or []]
    payload = {
        "retrievedAt": now.isoformat(), "publishedAfter": cutoff,
        "count": len(notices), "cpvCodes": list(CODES), "notices": notices,
        "collectionMode": "single-search-only",
    }
    Path("data/hilma_raw.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    audit["returned_count"] = len(notices)
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit))

if __name__ == "__main__":
    main()
