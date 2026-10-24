"""Page-cited requirement leads from downloaded public tender PDF text.

A lead is a verbatim fragment for reviewer attention, not a verified tender
requirement, eligibility pass, or gold label. PDF bid comparisons may contain
quoted criteria but are not full original tender packages.
"""
from __future__ import annotations
import re

CUES = {
    "references": re.compile(r"referenss|vastaavasta hankinnasta", re.I),
    "turnover": re.compile(r"liikevaiht|turnover", re.I),
    "guarantee": re.compile(r"urakkavakuus|vakuuden määrä|suoritusvakuus|takuuaikainen vakuus", re.I),
    "insurance": re.compile(r"vastuuvakuut|toiminnan vakuut|vakuutusturva", re.I),
    "site_visit": re.compile(r"tutustumis|näyttötilaisuu|kohdekäynt|kohde-esittely|kohteen esittely|rakennuspaikkaan", re.I),
    "contract_price": re.compile(r"kokonaishinta|urakkahinta|tarjoushinta", re.I),
}

def leads_by_page(text: str, source_url: str, max_per_type: int = 8) -> dict:
    sections = re.split(r"\[\[PAGE (\d+)\]\]\s*", text)
    findings = {key: [] for key in CUES}
    for i in range(1,len(sections),2):
        page=int(sections[i])
        content=sections[i+1]
        lines=[x.strip() for x in content.splitlines() if x.strip()]
        for index,line in enumerate(lines):
            for category,pattern in CUES.items():
                if pattern.search(line) and len(findings[category]) < max_per_type:
                    excerpt=" ".join(lines[max(0,index-1):min(len(lines),index+2)])
                    findings[category].append({
                        "source_url":source_url,
                        "page":page,
                        "exact_pdf_text_excerpt":excerpt[:600],
                        "excerpt_truncated":len(excerpt)>600,
                        "status":"REVIEW_LEAD_ONLY",
                    })
    return {"categories":findings,"verified_eligibility":False,
            "verified_single_contract_value":False,"gold_label":"UNREVIEWED"}
