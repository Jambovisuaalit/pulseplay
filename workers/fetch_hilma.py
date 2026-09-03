from __future__ import annotations

import datetime as dt
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import unquote, urlparse

import requests

GRAPHQL_URL = os.getenv(
    "HILMA_GRAPHQL_URL",
    "https://hankintailmoitukset.fi/api/graphql",
)
CPV_CODES = [
    "50000000-5",
    "50700000-2",
    "50710000-5",
    "50720000-8",
]
LOOKBACK_DAYS = 30
PAGE_SIZE = 100
TIMEOUT = 60

DATA_DIR = Path("data")
RAW_PATH = DATA_DIR / "hilma_raw.json"
ATTACHMENT_DIR = Path("/tmp/attachments")

DATA_DIR.mkdir(parents=True, exist_ok=True)
ATTACHMENT_DIR.mkdir(parents=True, exist_ok=True)

QUERY = """
query GetNotices(
  $cpvCodes: [String!]
  $publishedAfter: DateTime!
  $first: Int!
  $after: String
) {
  searchNotices(
    first: $first
    after: $after
    filter: {
      cpvCodes: $cpvCodes
      publishedAfter: $publishedAfter
    }
  ) {
    pageInfo {
      hasNextPage
      endCursor
    }
    edges {
      node {
        id
        title
        description
        publishedAt
        organisation {
          name
        }
        links {
          attachments
        }
      }
    }
  }
}
"""

session = requests.Session()
session.headers.update(
    {
        "Accept": "application/json",
        "User-Agent": "TenderPulse-MVP/0.1",
    }
)


def cutoff_iso() -> str:
    now = dt.datetime.now(dt.timezone.utc)
    return (now - dt.timedelta(days=LOOKBACK_DAYS)).isoformat()


def graphql_request(variables: dict, retries: int = 3) -> dict:
    for attempt in range(1, retries + 1):
        response = session.post(
            GRAPHQL_URL,
            json={"query": QUERY, "variables": variables},
            timeout=TIMEOUT,
        )

        if response.status_code == 429 or response.status_code >= 500:
            if attempt == retries:
                response.raise_for_status()
            time.sleep(2**attempt)
            continue

        response.raise_for_status()
        payload = response.json()

        if payload.get("errors"):
            raise RuntimeError(
                "Hilma GraphQL schema/endpoint error: "
                + json.dumps(payload["errors"], ensure_ascii=False)
            )

        return payload

    raise RuntimeError("Hilma request failed")


def extract_urls(value) -> list[str]:
    urls: list[str] = []

    if isinstance(value, str):
        if value.startswith(("https://", "http://")):
            urls.append(value)
    elif isinstance(value, list):
        for item in value:
            urls.extend(extract_urls(item))
    elif isinstance(value, dict):
        for item in value.values():
            urls.extend(extract_urls(item))

    return list(dict.fromkeys(urls))


def safe_filename(value: str) -> str:
    value = unquote(value)
    value = re.sub(r"[^\w.\-]+", "_", value, flags=re.UNICODE)
    return value[:160] or "attachment.pdf"


def download_pdf(url: str, notice_id: str, index: int) -> dict:
    result = {
        "url": url,
        "downloaded": False,
        "local_path": None,
        "error": None,
    }

    try:
        response = session.get(
            url,
            timeout=TIMEOUT,
            stream=True,
            allow_redirects=True,
        )
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").lower()
        final_url = response.url.lower()

        if ".pdf" not in final_url and "application/pdf" not in content_type:
            return result

        basename = Path(urlparse(response.url).path).name
        basename = safe_filename(basename or "attachment.pdf")
        if not basename.lower().endswith(".pdf"):
            basename += ".pdf"

        path = ATTACHMENT_DIR / f"{notice_id}_{index}_{basename}"

        with path.open("wb") as handle:
            for chunk in response.iter_content(256 * 1024):
                if chunk:
                    handle.write(chunk)

        result["downloaded"] = True
        result["local_path"] = str(path)
        return result
    except Exception as exc:
        result["error"] = str(exc)
        return result


def fetch_all() -> list[dict]:
    cursor = None
    notices: list[dict] = []
    published_after = cutoff_iso()

    while True:
        payload = graphql_request(
            {
                "cpvCodes": CPV_CODES,
                "publishedAfter": published_after,
                "first": PAGE_SIZE,
                "after": cursor,
            }
        )

        search_data = payload.get("data", {}).get("searchNotices")
        if not search_data:
            raise RuntimeError(
                "data.searchNotices missing. Verify the current Hilma GraphQL schema."
            )

        for edge in search_data.get("edges", []):
            node = edge.get("node")
            if node:
                notices.append(node)

        page_info = search_data.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break

        cursor = page_info.get("endCursor")
        if not cursor:
            break

    return notices


def main() -> None:
    notices = fetch_all()

    for notice in notices:
        notice_id = str(notice.get("id", "unknown"))
        attachments = (notice.get("links") or {}).get("attachments")
        urls = extract_urls(attachments)
        notice["downloadedAttachments"] = [
            download_pdf(url, notice_id, index)
            for index, url in enumerate(urls, start=1)
        ]

    output = {
        "retrievedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "publishedAfter": cutoff_iso(),
        "cpvCodes": CPV_CODES,
        "count": len(notices),
        "notices": notices,
    }

    RAW_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {len(notices)} notices to {RAW_PATH}")


if __name__ == "__main__":
    main()
