"""Read-only eForms XML verification helpers. No network requests.

BT-131 is tender receipt; BT-1311 is participation-request receipt. These
must never be interchanged. An XML URL is a document lead, not proof that
the complete tender-attachment set has been downloaded.
"""
from __future__ import annotations

import datetime as dt
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(?:Z|[+-]\d{2}:\d{2})?$")
TIME_RE = re.compile(r"^\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2})$")


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def children(parent: ET.Element, name: str) -> list[ET.Element]:
    return [node for node in parent if local_name(node.tag) == name]


def child_text(parent: ET.Element, name: str) -> str | None:
    for node in children(parent, name):
        if node.text and node.text.strip():
            return node.text.strip()
    return None


def combine_deadline(date: str | None, time: str | None) -> str | None:
    if not date or not time or not DATE_RE.fullmatch(date) or not TIME_RE.fullmatch(time):
        return None
    # Date may carry an offset in UBL. The time's explicit offset is used,
    # and conflicting date/time offsets are rejected instead of guessed.
    date_base = date[:10]
    date_offset = date[10:]
    time_offset_match = re.search(r"(Z|[+-]\d{2}:\d{2})$", time)
    if not time_offset_match:
        return None
    time_offset = time_offset_match.group(1)
    if date_offset and date_offset != time_offset:
        return None
    iso = f"{date_base}T{time}"
    try:
        parsed = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return None
        return iso
    except ValueError:
        return None


def audit_eforms_xml(xml_text: str) -> dict:
    if "<!DOCTYPE" in xml_text.upper() or "<!ENTITY" in xml_text.upper():
        raise ValueError("DTD ja XML-entiteetit eivät ole sallittuja.")
    root = ET.fromstring(xml_text)
    entries: list[dict] = []
    tender_lot_ids: list[str | None] = []
    for lot in root.iter():
        if local_name(lot.tag) != "ProcurementProjectLot":
            continue
        lot_id_node = next(iter(children(lot, "ID")), None)
        # eForms can also contain groups of lots and parts. Only schemeName=Lot
        # represents an individual lot; absent schemes remain conservative.
        if lot_id_node is not None and lot_id_node.get("schemeName") in {"LotsGroup", "Part"}:
            continue
        lot_id = child_text(lot, "ID")
        tender_lot_ids.append(lot_id)
        # eForms BT-131 and BT-1311 are located under cac:TenderingProcess,
        # not cac:TenderingTerms (the latter contains other tender conditions).
        for terms in children(lot, "TenderingProcess"):
            for period_name, kind in (
                ("TenderSubmissionDeadlinePeriod", "tender"),
                ("ParticipationRequestReceptionPeriod", "participation_request"),
            ):
                for period in children(terms, period_name):
                    date = child_text(period, "EndDate")
                    time = child_text(period, "EndTime")
                    iso = combine_deadline(date, time)
                    entries.append({
                        "lot_id": lot_id,
                        "kind": kind,
                        "date_raw": date,
                        "time_raw": time,
                        "deadline_iso": iso,
                        "valid": iso is not None,
                    })

    # A procurement portal link is not an attachment manifest. Only audit
    # explicitly named URL nodes; never crawl all URLs from arbitrary prose.
    document_leads = []
    for node in root.iter():
        if local_name(node.tag) not in {"AccessToolsURI", "DocumentURI", "WebsiteURI"}:
            continue
        url = (node.text or "").strip()
        if urlparse(url).scheme in {"http", "https"} and urlparse(url).netloc:
            document_leads.append(url)

    return {
        "deadlines": entries,
        "tender_lot_ids": tender_lot_ids,
        "document_leads": list(dict.fromkeys(document_leads)),
        "documents_status": "unknown",
        "documents_verified": False,
    }


def compare_index_deadline(index_value: str | None, audit: dict) -> dict:
    tenders = [row for row in audit["deadlines"] if row["kind"] == "tender"]
    if not tenders or any(not row["valid"] for row in tenders):
        return {"verified": False, "reason": "Tarjousten määräaika puuttuu tai on puutteellinen XML:ssä."}
    # One valid deadline cannot verify a notice if another individual lot has
    # no BT-131 at all. Do not silently substitute the search-index deadline.
    lots = audit.get("tender_lot_ids", [])
    if not lots or any(not any(row["lot_id"] == lot_id for row in tenders) for lot_id in lots):
        return {"verified": False, "reason": "Vähintään yhden osakohteen tarjousmääräaika puuttuu XML:stä."}
    try:
        indexed = dt.datetime.fromisoformat((index_value or "").replace("Z", "+00:00"))
        if indexed.tzinfo is None:
            raise ValueError("Timezone missing")
        source_dates = [dt.datetime.fromisoformat(row["deadline_iso"].replace("Z", "+00:00")) for row in tenders]
    except ValueError:
        return {"verified": False, "reason": "Indeksin tai XML:n ajankohta on epäselvä."}
    if len(set(source_dates)) != 1:
        return {"verified": False, "reason": "Eri osakokonaisuuksilla on eri määräajat; yksi yleinen deadline ei riitä."}
    if indexed != source_dates[0]:
        return {"verified": False, "reason": "Indeksin ja XML:n määräajat eroavat."}
    return {"verified": True, "reason": "Indeksiaika vastaa XML:n kaikkia tarjousmääräaikoja."}
