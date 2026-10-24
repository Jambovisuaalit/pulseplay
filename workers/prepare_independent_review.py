"""Prepare source-only evidence cues for a *separate* independent adjudicator.

This tool never reads predictions, assigns relevance labels, or writes gold labels.
Search-index snippets are not equivalent to complete tender documents.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


ROOT = Path("data/validation/independent_100")
SOURCE = Path("data/validation/snapshot_2026-10-19/hilma_raw.json")
OUT_CSV = ROOT / "source_evidence_queue.csv"
OUT_JSON = ROOT / "source_preflight.json"
OUT_MD = ROOT / "LAHDETARKASTUKSEN_TILANNE.md"
TEST_MARK = "SISÄINEN TESTI – KUVITTEELLINEN YRITYS – EI ASIAKASTOIMITUS"

# Source cues, not criteria for a relevance verdict. The adjudicator must check
# the actual geographic area, contract scope, annexes, and buyer requirements.
SERVICE_CUES = (
    "huoneisto", "pintakorja", "pintaremont", "maalaus", "maalau", "lattia",
    "kaluste", "sisäilmakorja", "korjaustyö", "vuosikorja", "pienurakka",
    "pienkorja", "saneeraus", "toimitila", "peruskorja", "sisäpuol",
)
EXCLUSION_CUES = (
    "uudisrakent", "purku-urak", "purkaminen", "vesikatt", "kattourakka",
    "kattotyö", "ikkunoiden uusimi", "ikkuna- ja ovi", "ikkunoiden ja ovien",
    "lvi-urakka", "lvij-urakka", "sähköurakka", "sähkötyö", "talotekniikka",
    "lämpöteknis", "lämmitysjärjestelmä", "maarakennus", "maanrakennus",
    "laituri", "tiehank", "sillan", "ruoppau", "suunnittelutyö",
)
AREA_CUES = (
    "helsinki", "helsingin", "espoo", "espoon", "vantaa", "vantaan",
    "kauniainen", "kauniaisten", "kirkkonummi", "kirkkonummen",
    "hyvinkää", "riihimäki", "nakkila", "joensuu", "mäntyharju",
    "kalajoki", "pori", "savukoski", "tampere", "lahti", "lohja",
)


def title_fingerprint(title: str) -> str:
    value = unicodedata.normalize("NFKC", title).casefold().strip()
    value = re.sub(r"^keskeytetty\s+", "", value)
    return re.sub(r"[^\w]+", " ", value).strip()


def cues(text: str, terms: tuple[str, ...]) -> str:
    """Return exact short quotes around matching words, no inferred assertion."""
    lowered = text.casefold()
    found = []
    for term in terms:
        pos = lowered.find(term)
        if pos < 0:
            continue
        left = max(0, pos - 32)
        right = min(len(text), pos + len(term) + 50)
        quote = " ".join(text[left:right].split())
        if quote not in found:
            found.append(quote)
        if len(found) == 3:
            break
    return " | ".join(found)


def prepare(payload: dict, source_sha256: str) -> tuple[dict, list[dict]]:
    notices = payload.get("notices")
    if not isinstance(notices, list) or len(notices) != 100:
        raise ValueError("Exactly 100 saved notices are required")
    ids = [str(item.get("id") or "").strip() for item in notices]
    if not all(ids) or len(set(ids)) != 100:
        raise ValueError("Duplicate or missing source notice IDs")

    fingerprints = defaultdict(list)
    for item in notices:
        fingerprint = title_fingerprint(str(item.get("title") or ""))
        if fingerprint:
            fingerprints[fingerprint].append(str(item["id"]))
    possible_duplicates = [sorted(v) for v in fingerprints.values() if len(v) > 1]
    possible_duplicates.sort()

    rows = []
    for item in sorted(notices, key=lambda x: str(x["id"])):
        title = str(item.get("title") or "")
        description = str(item.get("description") or "")
        text = title + "\n" + description
        # An organisation's seat is not evidence of a worksite's location.
        fp = title_fingerprint(title)
        peers = sorted(set(fingerprints.get(fp, [])) - {str(item["id"])}) if fp else []
        rows.append({
            "notice_id": str(item["id"]),
            "title": title,
            "buyer": str(item.get("organisation") or ""),
            "published_at_utc": str(item.get("publishedAt") or ""),
            "tender_deadline_utc": str(item.get("deadline") or ""),
            "estimated_value_source": item.get("estimated_value") if item.get("estimated_value") is not None else "",
            "service_cue_quote_not_verdict": cues(text, SERVICE_CUES),
            "exclusion_cue_quote_not_verdict": cues(text, EXCLUSION_CUES),
            "area_name_quote_not_verified_worksite": cues(text, AREA_CUES),
            "possible_duplicate_notice_ids": "|".join(peers),
            "title_says_cancelled": "YES" if re.search(r"^\s*KESKEYTETTY\b", title, flags=re.I) else "NO",
            "description_present": "YES" if description.strip() else "NO",
            "full_notice_checked": "NO",
            "tender_annexes_checked": "NO",
            "independent_gold_review": "PENDING",
            "source_pointer": f"{SOURCE}#id={item['id']}",
        })

    # Lack of a standalone metadata field does not mean that the corresponding
    # fact is absent from the official complete notice.
    field_presence = lambda key: sum(item.get(key) not in (None, "") for item in notices)
    audit = {
        "test_marking": TEST_MARK,
        "source_sha256": source_sha256,
        "source_retrieved_at": payload.get("retrievedAt"),
        "review_prepared_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "unique_notice_ids": len(set(ids)),
        "notices_total": len(notices),
        "description_present": field_presence("description"),
        "published_at_present": field_presence("publishedAt"),
        "tender_deadline_present": field_presence("deadline"),
        "estimated_value_present": field_presence("estimated_value"),
        "standalone_worksite_location_fields": 0,
        "standalone_questions_deadline_fields": 0,
        "fully_checked_annexes": 0,
        "independent_gold_labels": 0,
        "possible_duplicate_title_groups": possible_duplicates,
        "cancelled_in_title_ids": [row["notice_id"] for row in rows if row["title_says_cancelled"] == "YES"],
        "precision": "NOT MEASURED",
        "false_positives": "NOT MEASURED",
        "false_negatives": "NOT MEASURED",
        "unreviewed_count": 100,
        "review_status": "SOURCE-ONLY PRECHECK — NOT INDEPENDENT GOLD",
        "boundary": "Cues are verbatim excerpts for a blind reviewer, not autonomous classification or eligibility.",
    }
    return audit, rows


def main() -> None:
    raw = SOURCE.read_bytes()
    audit, rows = prepare(json.loads(raw), hashlib.sha256(raw).hexdigest())
    ROOT.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    OUT_JSON.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    duptext = ", ".join("/".join(group) for group in audit["possible_duplicate_title_groups"]) or "Ei havaittu"
    report = f"""# Urakkaluotsi – 100 ilmoituksen riippumattoman tarkastuksen tilanne

{TEST_MARK}

Aineisto: 100 jäädytettyä Hilma-hakutulosta, haettu {audit['source_retrieved_at']}.
Lähteen SHA-256: `{audit['source_sha256']}`. **Hakumetadata ei sisällä tarjousliitteitä.**

## Valmiit tarkastukset

- 100/100 uniikkia ilmoitustunnistetta. Määräaika {audit['tender_deadline_present']}/100, julkaisuaika {audit['published_at_present']}/100.
- Kuvaus {audit['description_present']}/100; arvioitu arvo {audit['estimated_value_present']}/100.
- Omaa työmaakohteen sijaintikenttää 0/100, kysymysten määräaikakenttää 0/100.
- Mahdolliset samannimiset / keskeytyksellä merkityt ilmoitukset: {duptext}.
- Otsikossa keskeytetyksi ilmoitetut: {', '.join(audit['cancelled_in_title_ids']) or 'ei havaittu'}.
- `source_evidence_queue.csv` sisältää kaikki 100 ilmoitusta sekä lähdetekstin sanatarkat
  poiminnat **ilman automaattisen ennusteen sarakkeita ja ilman lopullisia luokkia**.

## Hyväksynnän estävä vaihe

**Riippumaton lähdetarkistus: 0/100.** Tämä agentti voi poimia näyttövihjeet, mutta se
ei ole riippumaton tuomari oman koodinsa luokittelulle. Tarkastaja tarvitsee vähintään
alkuperäisen ilmoituksen ja hankinnan alue-/kokotiedot. Ratkaisevat liitteet ja
yrityksen referenssit/pätevyydet puuttuvat. Vasta todellisen, sokkoutetun tarkastajan
perustelemat ja allekirjoittamat luokat syötetään `gold_labels.csv`-tiedostoon.

**Precision, FP ja FN: NOT MEASURED. Arvioimatta 100/100.** Tekninen CI-testi ei
korvaa riippumatonta arviointia. Uusi *arviointiin perustuva* toimitussimulaatio
ja kaupallinen hyväksyntä ovat odotustilassa, kunnes tämä portti täyttyy.
"""
    OUT_MD.write_text(report, encoding="utf-8")
    print(json.dumps({k: audit[k] for k in ("notices_total", "description_present", "estimated_value_present", "possible_duplicate_title_groups", "cancelled_in_title_ids", "unreviewed_count")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
