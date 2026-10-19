"""Urakkaluotsi ICP v2: evidence-bound *triage*, never a tender GO decision.

The legacy keyword baseline remains frozen in build_validation_set.py for audit.
Missing worksite, contract *unit* value or source annexes cannot yield 'Relevantti'.
"""
from __future__ import annotations

import re
import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

ALLOWED_MUNICIPALITIES = frozenset({"helsinki", "espoo", "vantaa", "kauniainen", "kirkkonummi"})
MIN_EUR, MAX_EUR = 10_000, 250_000

# The source index has no structured worksite location. These are high-confidence
# place-name variants, not an exhaustive Finnish gazetteer. Unrecognised -> UNKNOWN.
CITY_FORMS: dict[str, tuple[str, ...]] = {
    "helsinki": ("helsinki", "helsingissä", "helsingin", "helsinkiin"),
    "espoo": ("espoo", "espoossa", "espoon", "espooseen"),
    "vantaa": ("vantaa", "vantaalla", "vantaan", "vantaalle"),
    "kauniainen": ("kauniainen", "kauniaisissa", "kauniaisten"),
    "kirkkonummi": ("kirkkonummi", "kirkkonummella", "kirkkonummen"),
    "mäntyharju": ("mäntyharju", "mäntyharjun", "mäntyharjulla"),
    "kaarina": ("kaarina", "kaarinassa", "kaarinan"),
    "rovaniemi": ("rovaniemi", "rovaniemellä", "rovaniemen"),
    "riihimäki": ("riihimäki", "riihimäellä", "riihimäen"),
    "alavus": ("alavus", "alavudella", "alavuden"),
    "hyvinkää": ("hyvinkää", "hyvinkäällä", "hyvinkään"),
    "lohja": ("lohja", "lohjan", "lohjalla"),
    "mäntsälä": ("mäntsälä", "mäntsälän", "mäntsälässä"),
    "sipoo": ("sipoo", "sipoon", "sipoossa", "etelä-sipoossa"),
    "tuusula": ("tuusula", "tuusulan", "tuusulassa"),
}


@dataclass(frozen=True)
class Signal:
    status: str
    reason: str
    source_excerpt: str


def _match(pattern: str, text: str) -> re.Match | None:
    return re.search(pattern, text, flags=re.IGNORECASE)


def _text(notice: dict) -> tuple[str, str]:
    return str(notice.get("title") or ""), str(notice.get("description") or "")


def _municipalities(text: str) -> set[str]:
    names = set()
    for city, forms in CITY_FORMS.items():
        if any(re.search(r"(?<!\w)" + re.escape(form) + r"(?!\w)", text, re.I) for form in forms):
            names.add(city)
    return names


def area_signal(notice: dict) -> Signal:
    # A buyer's registered municipality is deliberately never a worksite.
    explicit = str(notice.get("worksite_municipality") or "").strip().casefold()
    evidence = str(notice.get("worksite_location_evidence") or "").strip()
    title, description = _text(notice)
    if explicit and evidence and evidence.casefold() in (title + "\n" + description).casefold():
        if explicit in _municipalities(evidence):
            return Signal("IN" if explicit in ALLOWED_MUNICIPALITIES else "OUT", "STRUCTURED_WORKSITE", evidence)
        return Signal("UNKNOWN", "WORKSITE_FIELD_CONTRADICTS_EVIDENCE", evidence)
    if not title and not description:
        return Signal("UNKNOWN", "MISSING_SOURCE_TEXT", "")
    # Only sentences / clauses which explicitly designate worksite count.
    # Buyer names and generic city mentions alone are not sufficient.
    lines = re.split(r"[\n.;]", description)
    site_evidence = []
    for segment in lines:
        s = segment.strip()
        if re.search(r"\b(?:kohde|rakennuspaikka|työmaa|urakka-alue|urakkakohde|kiinteistö|osoitteessa|sijaitse\w*)\b", s, re.I):
            if re.search(r"\b(?:sijaitse\w*|osoitteessa|urakkakohde|rakennuspaikka|työmaa)\b", s, re.I):
                site_evidence.append(s[:300])
    # Explicit worksite phrasing in a title is also source evidence.
    if _match(r"\\b(?:urakkakohde|työmaa|rakennuspaikka|osoitteessa|sijaitse\\w*)\\b", title):
        site_evidence.append(title[:300])
    # Title city treated as site only in explicit "Helsinki, <project>" form,
    # NOT "Helsingin kaupunki pyytää ..." or buyer metadata.
    if _match(r"\b(?:helsinki|espoo|vantaa|kauniainen|kirkkonummi|sipoo|mäntsälä|tuusula|hyvinkää|lohja)\s*[,;:]\s*\S", title):
        site_evidence.append(title)
    names = set().union(*(_municipalities(s) for s in site_evidence)) if site_evidence else set()
    if len(names) > 1:
        return Signal("UNKNOWN", "MULTIPLE_WORKSITE_MUNICIPALITIES", " | ".join(site_evidence)[:230])
    if names:
        city = next(iter(names))
        return Signal("IN" if city in ALLOWED_MUNICIPALITIES else "OUT", f"WORKSITE_{city.upper()}", " | ".join(site_evidence)[:230])
    return Signal("UNKNOWN", "WORKSITE_NOT_VERIFIED", "")


def size_signal(notice: dict) -> Signal:
    title, desc = _text(notice)
    content = title + "\n" + desc
    # Framework ceilings and multi-lot totals are *not* individual job sizes.
    aggregate = bool(_match(r"\b(?:puite(?:sopim\w*|järjestely\w*)|jaettu\s+(?:\w+\s+){0,2}(?:osiin|osaan)|osa-alue\w*|eri\s+urakkaa)\b", content))
    raw = notice.get("estimated_value")
    if raw is None or raw == "":
        return Signal("UNKNOWN", "ESTIMATED_VALUE_MISSING", "")
    try:
        amount = float(raw)
    except (TypeError, ValueError):
        return Signal("UNKNOWN", "INVALID_VALUE", str(raw))
    if not (amount > 0 and amount < float("inf")):
        return Signal("UNKNOWN", "NON_POSITIVE_OR_NONFINITE_ESTIMATE", str(raw))
    if aggregate:
        return Signal("UNKNOWN", "TOTAL_NOT_SINGLE_CONTRACT", str(raw))
    if amount < MIN_EUR or amount > MAX_EUR:
        return Signal("OUT", "ESTIMATED_SINGLE_CONTRACT_OUTSIDE_RANGE", str(raw))
    # Search-index estimate supports conditional prioritisation only. Actual
    # lot/value-kind/equipment exclusions need original notice/annex evidence.
    if notice.get("verified_single_contract_value") is True and notice.get("contract_value_evidence"):
        return Signal("IN", "VERIFIED_SINGLE_CONTRACT_VALUE", str(raw))
    return Signal("UNKNOWN", "VALUE_KIND_NOT_VERIFIED", str(raw))


def scope_signal(notice: dict) -> Signal:
    title, desc = _text(notice)
    if not (title.strip() or desc.strip()):
        return Signal("UNKNOWN", "MISSING_SOURCE_TEXT", "")
    normalized_title = title.casefold()
    content = (title + "\n" + desc).casefold()

    # Clear *primary works*, not incidental mention of new doors, walls or LVI.
    forbidden_primary = [
        (r"\b(?:uudisrakenn\w*|uudisrakent\w*|uuden\s+(?:päiväkodin|koulun|liikuntahallin|aseman|rakennuksen|saunan|jäteaseman)\s+rakentami\w*)", "NEW_BUILD"),
        (r"\b(?:purku-urakka|kerrostalon\s+purku|rakennusten\s+purkaminen)\b", "DEMOLITION"),
        (r"\b(?:ikkunoiden\s+(?:uusimin\w*|vaiht\w*)|ovien\s+kokonaisvaiht\w*)", "WINDOW_DOOR"),
        (r"\b(?:vesikattourakka|kattourakka|vesikattojen\s+korjaushanke)\b", "ROOF"),
        (r"\b(?:silta\w*|alikulkukäytävä|katu\w*|tieurakka|maanrakennus|metsätien|golfkentän|laiturin|pienvenelaituri|uimapaikka|alueleikkipaikka|hulevesilinjan)\b", "INFRA"),
        (r"\b(?:sprinkleriurakka|paloilmoittimen\s+saneeraus|hissi\w*\s+(?:vaihe|uusimi)|lattianostim\w*)\b", "SPECIALIST"),
        (r"\b(?:vuokramallilla|vuokrasopimus|konetyöpalvelut|talvikunnossapito|katuvalaisinten\s+vaihdot|peltisepänt\w*)\b", "NOT_OFFERED"),
    ]
    for pattern, reason in forbidden_primary:
        m = _match(pattern, normalized_title)
        if m:
            return Signal("OUT", reason, title[max(0, m.start()-22):m.end()+45])
    if _match(r"(?:kokonaisurakka|pääurakka|urakkakohde|peruskorjaus)", content) and _match(
        r"\b(?:kaikki\s+lv(?:i|ia|is|isa|ias|iasj)|lvi(?:as|asj|as?)\s*[-–]?\s*(?:linja|urakka)|taloteknisten\s+järjestelmien\s+uusiminen)\b", content
    ):
        return Signal("OUT", "MIXED_TECHNICAL_WHOLE", "LVI-/talotekninen kokonaisuus lähdetekstissä")
    # Standalone technical systems are not surface refurbishment.
    if _match(r"\b(?:sprinkleriurakka|paloilmoitin\w*|linjasaneeraus|taloteknisten\s+järjestelmien)\b", normalized_title):
        return Signal("OUT", "TECHNICAL_SYSTEM", title[:180])
    matching = _match(r"\b(?:huoneisto(?:saneer\w*|remont\w*|korj\w*)|pintaremont\w*|pintakorj\w*|maalaus\w*|maalausty\w*|lattia(?:päällyste\w*|remont\w*|korj\w*|työ\w*)|sisäpuoli\w*|tilamuut\w*|peruskorj\w*|rakennusteknis\w*\s+(?:muutos|korjaus)|korjausty\w*)\b", content)
    if matching:
        return Signal("MATCH", "REPAIR_SERVICE_CUE", content[max(0, matching.start()-35):matching.end()+80])
    return Signal("UNKNOWN", "SERVICE_SCOPE_NOT_PROVEN", "")


def classify_notice(notice: dict) -> dict:
    title, desc = _text(notice)
    area = area_signal(notice)
    size = size_signal(notice)
    scope = scope_signal(notice)
    cancelled = bool(_match(r"^\s*(?:keskeytetty|peruttu)\b", title))
    reasons = [f"AREA_{area.reason}", f"SIZE_{size.reason}", f"SCOPE_{scope.reason}"]
    if cancelled:
        label = "Epärelevantti"
        reasons.insert(0, "CANCELLED_TITLE")
    elif "OUT" in (area.status, size.status, scope.status):
        label = "Epärelevantti"
    elif (area.status, size.status, scope.status) == ("IN", "IN", "MATCH"):
        label = "Relevantti"
    elif area.status == "IN" and scope.status == "MATCH":
        label = "Mahdollinen"
    else:
        label = "Ei priorisoitu"
        reasons.append("INSUFFICIENT_POSITIVE_EVIDENCE_FOR_REVIEW_QUEUE")
    # A priority hint is never a probability or positive eligibility verdict.
    rank = (100 if label == "Relevantti" else
            25 + 6 * (scope.status == "MATCH") + 4 * (area.status == "IN") if label == "Mahdollinen" else 0)
    return {
        "notice_id": str(notice.get("id") or ""),
        "title": title, "model_version": "ICP_V2_FAIL_CLOSED_2026_10_19",
        "model_label": label, "priority_hint_not_probability": rank,
        "area_status": area.status, "area_reason": area.reason, "area_evidence": area.source_excerpt,
        "size_status": size.status, "size_reason": size.reason, "estimated_value_eur": notice.get("estimated_value"),
        "scope_status": scope.status, "scope_reason": scope.reason, "scope_evidence": scope.source_excerpt,
        "reasons": "; ".join(reasons),
        "review_queue": "YES" if label == "Mahdollinen" else "NO",
        "deferred_due_to_missing_evidence": "YES" if label == "Ei priorisoitu" else "NO",
        "full_tender_reviewed": "NO",
        "customer_go_verified": "NO",
        "source_pointer": notice.get("_source_pointer") or f"source_metadata#id={notice.get('id')}",
    }


def classify_snapshot(source: dict, provenance: str) -> list[dict]:
    notices = source.get("notices")
    if not isinstance(notices, list) or not notices:
        raise ValueError("Missing or empty notices array")
    ids = [str(item.get("id") or "") for item in notices]
    if not all(ids) or len(set(ids)) != len(ids):
        raise ValueError("Missing or duplicate source IDs")
    return [classify_notice({**item, "_source_pointer": f"{provenance}#id={item['id']}"})
            for item in notices]


def main() -> None:
    parser = argparse.ArgumentParser(description="Versioned, metadata-only ICP triage; NEVER an eligibility GO")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source_bytes = args.input.read_bytes()
    rows = classify_snapshot(json.loads(source_bytes), str(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({
        "model_version": "ICP_V2_FAIL_CLOSED_2026_10_19",
        "count": len(rows), "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "class_counts": {name: sum(r["model_label"] == name for r in rows)
                         for name in ("Relevantti", "Mahdollinen", "Ei priorisoitu", "Epärelevantti")},
        "official_precision": "NOT MEASURED",
        "customer_go_verified": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
