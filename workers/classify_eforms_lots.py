"""Connect saved XML lot evidence to ICP V2 without turning estimates into GO.

Each lot is scored independently. Explicit lot location and description are
kept separate from the contracting party. The original notice title is used
only for cancellation detection, never as evidence for a different lot's scope.
"""
from __future__ import annotations

import re
from relevance_v2 import classify_notice


def classify_lots(notice: dict, extraction: dict) -> list[dict]:
    if not isinstance(extraction, dict) or not isinstance(extraction.get("lots"), list):
        raise ValueError("Expected extracted eForms lot evidence")
    outputs = []
    for lot in extraction["lots"]:
        if not isinstance(lot, dict) or not lot.get("source_pointer") or not lot.get("lot_id"):
            raise ValueError("Lot must have source provenance and ID")
        description = str(lot.get("primary_scope_text") or "")
        municipality = lot.get("worksite_municipality")
        worksite = str(lot.get("worksite_city_text") or "")
        # Explicit location evidence is sourced only from lot ProcurementProject.
        if municipality and lot.get("location_status") == "SOURCE_LOT_LOCATION" and worksite:
            description += "\nUrakkakohde sijaitsee " + worksite + "."
        amount = lot.get("estimated_lot_value_text")
        currency = lot.get("estimated_lot_value_currency")
        if currency == "EUR" and amount and re.fullmatch(r"\d+(?:\.\d+)?", str(amount)):
            estimate = float(amount)
        else:
            estimate = None
        source_notice_title = str(notice.get("title") or "")
        cancelled = bool(re.search(r"^\s*(?:keskeytetty|peruttu)\b", source_notice_title, re.I))
        # Lot-specific text, never the broader notice's incidental repair words.
        # Preserve cancellation as a hard gate.
        candidate = {
            "id": str(notice.get("id") or "") + "#" + str(lot["lot_id"]),
            "title": "Keskeytetty " + description if cancelled else description,
            "description": description,
            "estimated_value": estimate,
            "verified_single_contract_value": False,
            "_source_pointer": lot["source_pointer"],
        }
        decision = classify_notice(candidate)
        decision["notice_id"] = str(notice.get("id") or "")
        decision["lot_id"] = str(lot["lot_id"])
        decision["eforms_location_status"] = lot.get("location_status", "UNKNOWN")
        decision["eforms_size_status"] = lot.get("size_status", "UNKNOWN")
        decision["source_xml_evidence_only"] = "YES"
        decision["customer_go_verified"] = "NO"
        outputs.append(decision)
    return outputs
