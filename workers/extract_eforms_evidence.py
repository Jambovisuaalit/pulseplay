"""Conservative extraction of source evidence from saved UBL/eForms XML.

This is an *evidence queue*, not eligibility verification. Unknown XML layouts
stay UNKNOWN. Never infer a worksite from buyer address or contract size from
a framework-wide total.
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from relevance_v2 import _municipalities


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def direct(parent: ET.Element, name: str):
    return next((c for c in parent if local(c.tag) == name), None)


def children(parent: ET.Element, name: str):
    return [c for c in parent if local(c.tag) == name]


def descendant(parent: ET.Element, *path: str):
    current = parent
    for name in path:
        current = direct(current, name) if current is not None else None
    return current


def value(node: ET.Element | None) -> str:
    return (node.text or "").strip() if node is not None else ""


def parse_xml_evidence(xml_text: str, source_pointer: str) -> dict:
    """Read only explicit project/lot fields; preserve their XML provenance.

    Do not silently map Organisation/ContractingParty addresses to worksite.
    A lot-level estimated amount is still an *estimate*, not a confirmed
    individual job value or a guarantee of customer eligibility.
    """
    root = ET.fromstring(xml_text)
    lots = [node for node in root.iter() if local(node.tag) == "ProcurementProjectLot"]
    results = []
    for index, lot in enumerate(lots):
        project = direct(lot, "ProcurementProject")
        lot_id = value(descendant(lot, "ID")) or str(index + 1)
        location = descendant(project, "RealizedLocation", "Address", "CityName") if project is not None else None
        city = value(location)
        city_matches = _municipalities(city)
        description = value(descendant(project, "Description")) if project is not None else ""
        amount_node = direct(project, "EstimatedOverallContractAmount") if project is not None else None
        amount = value(amount_node)
        currency = amount_node.attrib.get("currencyID", "") if amount_node is not None else ""
        # A lot's project is not necessarily one standalone work contract.
        # A framework can cover many orders and years.
        lot_result = {
            "lot_id": lot_id,
            "source_pointer": f"{source_pointer}#ProcurementProjectLot[{index + 1}]",
            "worksite_city_text": city,
            "worksite_municipality": next(iter(city_matches)) if len(city_matches) == 1 else None,
            "worksite_location_evidence": city if len(city_matches) == 1 else "",
            "location_status": "SOURCE_LOT_LOCATION" if len(city_matches) == 1 else "UNKNOWN",
            "primary_scope_text": description,
            "scope_status": "SOURCE_LOT_DESCRIPTION" if description else "UNKNOWN",
            "estimated_lot_value_text": amount,
            "estimated_lot_value_currency": currency,
            "size_status": "ESTIMATE_NOT_VERIFIED_SINGLE_CONTRACT" if amount else "UNKNOWN",
            "verified_single_contract_value": False,
            "contract_value_evidence": "",
            "annexes_checked": False,
        }
        results.append(lot_result)
    return {"source_pointer": source_pointer, "lot_count": len(lots), "lots": results,
            "customer_go_verified": False, "source_type": "SAVED_XML_NOT_FULL_TENDER_REVIEW"}


def extract_file(source: Path, output: Path) -> None:
    payload = parse_xml_evidence(source.read_text(encoding="utf-8"), str(source))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    extract_file(args.input, args.output)
