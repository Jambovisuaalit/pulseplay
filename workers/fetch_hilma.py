from __future__ import annotations

import base64
import datetime as dt
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests

API_BASE = "https://api.hankintailmoitukset.fi"
SEARCH_URL = f"{API_BASE}/avp/eformnotices/docs/search"
FULL_NOTICE_URL = f"{API_BASE}/avp-eforms/external-read/v1/notice"

CPV_CODES = ["50000000", "50700000", "50710000", "50720000"]
LOOKBACK_DAYS = 30
PAGE_SIZE = 100
TIMEOUT = 60

DATA_DIR = Path("data")
RAW_PATH = DATA_DIR / "hilma_raw.json"
ATTACHMENT_DIR = Path("/tmp/attachments")
FULL_NOTICE_DIR = Path("/tmp/full_notices")

for directory in (DATA_DIR, ATTACHMENT_DIR, FULL_NOTICE_DIR):
    directory.mkdir(parents=True, exist_ok=True)

api_key = os.getenv("HILMA_API_KEY")
if not api_key:
    raise RuntimeError(
        "HILMA_API_KEY puuttuu. Luo maksuton AVP-Read-tilaus Hilman API-portaalissa "
        "ja tallenna avain ympäristömuuttujaan / GitHub Secretiin."
    )

session = requests.Session()
session.headers.update(
    {
        "Accept": "application/json",
        "User-Agent": "TenderPulse-MVP/0.2",
        "Ocp-Apim-Subscription-Key": api_key,
    }
)


def cutoff_iso() -> str:
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=LOOKBACK_DAYS)
    return cutoff.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def request_with_retry(method: str, url: str, *, retries: int = 4, **kwargs):
    for attempt in range(retries):
        response = session.request(method, url, timeout=TIMEOUT, **kwargs)
        if response.status_code == 429 or response.status_code >= 500:
            if attempt == retries - 1:
                response.raise_for_status()
            retry_after = response.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else min(2 ** (attempt + 1), 20)
            time.sleep(delay)
            continue
        response.raise_for_status()
        return response
    raise RuntimeError(f"Request failed: {method} {url}")


def cpv_filter() -> str:
    parts = [f"search.ismatch('{code}', 'cpvCodes')" for code in CPV_CODES]
    return "(" + " or ".join(parts) + ")"


def fetch_search_notices() -> list[dict]:
    cutoff = cutoff_iso()
    select_fields = ",".join(
        [
            "noticeId",
            "titleFi",
            "organisationNameFi",
            "organisationNationalRegistrationNumber",
            "descriptionFi",
            "cpvCodes",
            "mainType",
            "datePublished",
            "expirationDate",
            "nutsCodes",
            "procedureType",
            "procurementTypeCode",
            "estimatedValue",
            "eFormsId",
            "procedureId",
            "procurementDocumentsUrl",
            "sendingSystem",
        ]
    )

    filter_expr = (
        f"datePublished ge {cutoff} and "
        "mainType eq 'ContractNotices' and "
        f"{cpv_filter()}"
    )

    notices: list[dict] = []
    skip = 0

    while True:
        body = {
            "search": "*",
            "top": PAGE_SIZE,
            "skip": skip,
            "count": True,
            "orderby": "datePublished desc",
            "searchMode": "any",
            "queryType": "simple",
            "select": select_fields,
            "filter": filter_expr,
        }

        response = request_with_retry("POST", SEARCH_URL, json=body)
        payload = response.json()
        page = payload.get("value") or []
        notices.extend(page)

        if len(page) < PAGE_SIZE:
            break

        skip += PAGE_SIZE

        # Azure Search has practical skip limits; 30 päivän MVP-aineistolle tämä
        # yläraja estää hallitsemattoman haun broad CPV 50000000:lla.
        if skip >= 1000:
            break

    return notices


def _find_xml_candidate(value) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith("<"):
            return stripped
        try:
            decoded = base64.b64decode(stripped, validate=True).decode("utf-8")
            if "<" in decoded and ">" in decoded:
                return decoded
        except Exception:
            return None

    if isinstance(value, dict):
        for child in value.values():
            found = _find_xml_candidate(child)
            if found:
                return found

    if isinstance(value, list):
        for child in value:
            found = _find_xml_candidate(child)
            if found:
                return found

    return None


def fetch_full_notice_xml(notice_id: str) -> tuple[str | None, str | None]:
    try:
        response = request_with_retry(
            "GET",
            f"{FULL_NOTICE_URL}/{notice_id}",
            headers={"Accept": "*/*"},
        )

        content_type = response.headers.get("Content-Type", "").lower()

        if "xml" in content_type and response.text.strip().startswith("<"):
            return response.text, None

        try:
            payload = response.json()
            xml = _find_xml_candidate(payload)
        except ValueError:
            xml = _find_xml_candidate(response.text)

        if not xml:
            return None, "Täyttä eForms XML:ää ei voitu tunnistaa vastauksesta."

        return xml, None
    except Exception as exc:
        return None, str(exc)


URL_RE = re.compile(r"https?://[^\s<>\"']+")


def extract_urls(*texts: str | None) -> list[str]:
    urls: list[str] = []
    for text in texts:
        if not text:
            continue
        urls.extend(URL_RE.findall(text))
    return list(dict.fromkeys(urls))


def safe_filename(value: str) -> str:
    value = unquote(value)
    value = re.sub(r"[^\w.\-]+", "_", value, flags=re.UNICODE)
    return value[:160] or "attachment.pdf"


def download_if_pdf(url: str, notice_id: str, index: int) -> dict:
    result = {"url": url, "downloaded": False, "local_path": None, "error": None}

    try:
        response = request_with_retry(
            "GET",
            url,
            stream=True,
            allow_redirects=True,
            headers={"Ocp-Apim-Subscription-Key": api_key}
            if url.startswith(API_BASE)
            else {},
        )

        content_type = response.headers.get("Content-Type", "").lower()
        final_url = response.url.lower()

        if ".pdf" not in final_url and "application/pdf" not in content_type:
            return result

        basename = Path(urlparse(response.url).path).name
        basename = safe_filename(basename or f"attachment_{index}.pdf")
        if not basename.lower().endswith(".pdf"):
            basename += ".pdf"

        path = ATTACHMENT_DIR / f"{notice_id}_{index}_{basename}"
        with path.open("wb") as handle:
            for chunk in response.iter_content(256 * 1024):
                if chunk:
                    handle.write(chunk)

        result["downloaded"] = True
        result["local_path"] = str(path)
    except Exception as exc:
        result["error"] = str(exc)

    return result


def normalize_notice(item: dict) -> dict:
    notice_id = str(item.get("noticeId") or "")
    full_xml, full_notice_error = fetch_full_notice_xml(notice_id)

    if full_xml:
        xml_path = FULL_NOTICE_DIR / f"{notice_id}.xml"
        xml_path.write_text(full_xml, encoding="utf-8")

    candidate_urls = extract_urls(
        item.get("procurementDocumentsUrl"),
        full_xml,
    )

    downloads = [
        download_if_pdf(url, notice_id, index)
        for index, url in enumerate(candidate_urls, start=1)
    ]

    return {
        "id": notice_id,
        "title": item.get("titleFi"),
        "description": item.get("descriptionFi"),
        "organisation": item.get("organisationNameFi"),
        "organisation_business_id": item.get(
            "organisationNationalRegistrationNumber"
        ),
        "publishedAt": item.get("datePublished"),
        "deadline": item.get("expirationDate"),
        "cpv_codes": item.get("cpvCodes") or [],
        "estimated_value": item.get("estimatedValue"),
        "procedure_type": item.get("procedureType"),
        "procurement_type": item.get("procurementTypeCode"),
        "documents_url": item.get("procurementDocumentsUrl"),
        "procedure_id": item.get("procedureId"),
        "eforms_id": item.get("eFormsId"),
        "sending_system": item.get("sendingSystem"),
        "full_notice_xml_path": (
            str(FULL_NOTICE_DIR / f"{notice_id}.xml") if full_xml else None
        ),
        "full_notice_error": full_notice_error,
        "attachment_candidates": candidate_urls,
        "downloadedAttachments": downloads,
    }


def main() -> None:
    search_results = fetch_search_notices()
    normalized: list[dict] = []

    for index, item in enumerate(search_results, start=1):
        print(f"[{index}/{len(search_results)}] {item.get('titleFi')}")
        normalized.append(normalize_notice(item))

    output = {
        "retrievedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "publishedAfter": cutoff_iso(),
        "cpvCodes": CPV_CODES,
        "count": len(normalized),
        "notices": normalized,
    }

    RAW_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {len(normalized)} notices to {RAW_PATH}")


if __name__ == "__main__":
    main()
