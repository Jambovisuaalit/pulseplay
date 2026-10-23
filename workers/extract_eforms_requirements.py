"""Auditable selection/contract-value evidence from saved eForms XML.

Search only specific source XML nodes. Keyword hits are evidence leads, never
verified requirements or customer eligibility. XML excludes annex contents.
"""
from __future__ import annotations
import re
import xml.etree.ElementTree as ET

TERMS = {
    "references": re.compile(r"referens|reference|kokemus|experience", re.I),
    "turnover": re.compile(r"liikevaih|turnover|annual revenue", re.I),
    "guarantee": re.compile(r"vakuus|takuuajan vakuus|performance bond|guarantee", re.I),
    "insurance": re.compile(r"vakuut|insurance", re.I),
    "qualification": re.compile(r"soveltuv|kelpoisu|selection criter|technical ability|financial standing", re.I),
    "contract_value": re.compile(r"ennakoitu arvo|arvonlisäveroton arvo|estimated value|contract amount", re.I),
}
CANDIDATE_TAGS = {
    "Description", "Name", "Criterion", "Requirement", "SelectionCriterion",
    "EconomicOperatorShortList", "EconomicAndFinancialStanding",
    "TechnicalAndProfessionalAbility", "EstimatedOverallContractAmount",
    "MaximumValue", "TotalAmount", "Amount", "Text", "Note", "QualificationApplicationTypeCode",
}

def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]

def extract_requirement_leads(xml_text: str, source_pointer: str) -> dict:
    root = ET.fromstring(xml_text)
    findings = {k: [] for k in TERMS}
    # Keep exact XML element position (local-name and occurrence) and original text.
    # Do not scan all ancestors: a matching free-text phrase is not a verified gate.
    occurrences = {}
    for node in root.iter():
        tag = local(node.tag)
        occurrences[tag] = occurrences.get(tag, 0) + 1
        if tag not in CANDIDATE_TAGS:
            continue
        value = (node.text or "").strip()
        if not value:
            continue
        for category, pattern in TERMS.items():
            if pattern.search(value) and len(findings[category]) < 20:
                findings[category].append({
                    "pointer": f"{source_pointer}#//{tag}[{occurrences[tag]}]",
                    "xml_tag": tag,
                    "exact_excerpt": value[:650],
                    "truncated": len(value) > 650,
                })
    return {
        "source_pointer": source_pointer,
        "document_type": local(root.tag),
        "requirements": {k: {"status": "UNVERIFIED_SOURCE_LEADS" if v else "UNKNOWN",
                             "evidence_leads": v} for k, v in findings.items()},
        "annexes_reviewed": False,
        "individual_contract_value_verified": False,
        "supplier_eligibility_verified": False,
        "gold_label": "UNREVIEWED",
    }
