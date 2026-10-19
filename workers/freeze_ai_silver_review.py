"""Freeze a blinded AI source-content review, not a human or verified gold set.

The input contains ONLY archived Hilma search metadata and an independently
authored source-phrase decision ledger. This script must not read predictions.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
from pathlib import Path


SOURCE = Path("data/validation/snapshot_2026-10-19/hilma_raw.json")
LEDGER = Path("data/validation/independent_100/ai_blind_seed.tsv")
OUTPUT = Path("data/validation/independent_100/ai_silver_labels.csv")
MANIFEST = Path("data/validation/independent_100/ai_silver_manifest.json")
LABELS = {"Relevantti", "Mahdollinen", "Epärelevantti", "NOT_EVALUATED"}
EXPLANATIONS = {
    "AREA": "Ilmoitettu kohde tai palvelualue on viiden sallitun kunnan ulkopuolella.",
    "SCOPE": "Ilmoitettu työn kohde ei kuulu yrityksen korjaus- ja sisätyöpalveluihin.",
    "SIZE": "Ilmoitettu urakan euromäärä ylittää 250 000 euron tavoiterajan; tarkista arvolaji ennen lopullista päätöstä.",
    "NEW_BUILD": "Hankinnan pääsisältö on uudisrakentaminen.",
    "DEMOLITION": "Hankinnan pääsisältö on rakennusten purkaminen.",
    "ROOF": "Hankinnan pääsisältöön kuuluu poisrajattu kattourakka.",
    "WINDOW_DOOR": "Hankinnan pääsisältö on poisrajattu ikkuna-/ovivaihtourakka.",
    "HVAC": "Hankinnan pääsisältö on rakennusyrityksen palveluihin kuulumaton talotekninen erikois- tai kokonaisurakka.",
    "CANCELLED": "Tallennetun otsikon mukaan hankinta on keskeytetty; uusin tilanne on tarkistettava.",
    "CLEAR_SCOPE_AREA": "Huoneisto-/pintaremontin sisältö ja Espoon toteutusalue ilmenevät hakutekstistä. Koko ja ehdot avoimia.",
    "UNKNOWN_AREA": "Työn laji voi sopia, mutta toteutusalue ei selviä luotettavasti tästä hakumetadatasta.",
    "UNKNOWN_SCOPE": "Kohde sijaitsee mahdollisesti toiminta-alueella, mutta urakan tarkka sisältö tai erikoisvaatimukset puuttuvat.",
    "UNKNOWN_SIZE": "Työn sisältö ja alue näyttävät mahdollisilta, mutta pääurakan koko tai talotekninen osuus jää epäselväksi.",
    "NO_SOURCE": "Ilmoituksesta puuttuvat sekä nimi että kuvaus. Sopivuutta ei voi arvioida.",
}


def freeze(payload: dict, seed: list[dict], timestamp: str, sha: str) -> list[dict]:
    notices = {str(item["id"]): item for item in payload["notices"]}
    if len(notices) != 100 or len(seed) != 100:
        raise ValueError("Both archive and blinded ledger must have exactly 100 rows")
    by_seed = {row["notice_id"]: row for row in seed}
    if len(by_seed) != 100 or set(by_seed) != set(notices):
        raise ValueError("Blind AI ledger must match all 100 unique archived notice IDs")
    rows = []
    for notice_id, notice in sorted(notices.items()):
        entry = by_seed[notice_id]
        label, reason, phrase = (entry[k].strip() for k in ("ai_label", "reason_code", "source_phrase"))
        if label not in LABELS or reason not in EXPLANATIONS:
            raise ValueError(f"Invalid class or reason code for {notice_id}")
        text = "\n".join((str(notice.get("title") or ""), str(notice.get("description") or "")))
        if label == "NOT_EVALUATED":
            if reason != "NO_SOURCE" or text.strip() or phrase:
                raise ValueError(f"Cannot mark {notice_id} unreviewed when source text exists")
            field, quote = "none", ""
        elif reason == "SIZE":
            amount = notice.get("estimated_value")
            if amount is None or str(int(float(amount))) != phrase or float(amount) <= 250000:
                raise ValueError(f"Estimated value is not a supported >250k claim for {notice_id}")
            field, quote = "estimated_value", phrase
        else:
            if not phrase or phrase.casefold() not in text.casefold():
                raise ValueError(f"Missing exact source-phrase evidence for {notice_id}: {phrase!r}")
            field, quote = "title_or_description", phrase
        if reason == "CLEAR_SCOPE_AREA" and "espoo" not in text.casefold():
            raise ValueError(f"No source-supported service-area match for {notice_id}")
        rows.append({
            "notice_id": notice_id,
            "ai_label": "" if label == "NOT_EVALUATED" else label,
            "adjudicator": "AI_SOURCE_ONLY_BLIND_V1_NOT_HUMAN_GOLD",
            "reviewed_at_utc": timestamp,
            "reason_code": reason,
            "reason_text": EXPLANATIONS[reason],
            "source_field": field,
            "exact_source_phrase": quote,
            "source_id_verified": "YES",
            "metadata_only_no_annexes": "YES",
            "requires_independent_confirmation": "YES",
            "source_sha256": sha,
            "source_pointer": f"{SOURCE}#id={notice_id}",
        })
    return rows


def main() -> None:
    raw = SOURCE.read_bytes()
    with LEDGER.open(encoding="utf-8", newline="") as handle:
        seed = list(csv.DictReader(handle, delimiter="\t"))
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat()
    sha = hashlib.sha256(raw).hexdigest()
    rows = freeze(json.loads(raw), seed, timestamp, sha)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    output_sha = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    manifest = {
        "review_type": "AI_SILVER_SOURCE_REVIEW_NOT_HUMAN_GOLD",
        "source_sha256": sha,
        "ai_labels_sha256": output_sha,
        "ledger_sha256": hashlib.sha256(LEDGER.read_bytes()).hexdigest(),
        "created_at_utc": timestamp,
        "rows": len(rows),
        "source_is_search_index_only": True,
        "model_predictions_seen_during_labelling": False,
        "human_gold_updated": False,
        "publication_or_customer_delivery_authorised": False,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    from collections import Counter
    print(json.dumps({"status": manifest["review_type"], "rows": len(rows), "ai_classes": dict(Counter(row["ai_label"] or "NOT_EVALUATED" for row in rows)), "sha256": output_sha}, ensure_ascii=False))


if __name__ == "__main__":
    main()
