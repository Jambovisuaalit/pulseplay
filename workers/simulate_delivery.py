"""Offline internal delivery dry-run on the frozen 100-item Hilma snapshot."""
from __future__ import annotations

import csv
import datetime as dt
import json
from collections import Counter
from pathlib import Path

from build_validation_set import baseline_label, priority_score
from delivery_safety import delivery_decision

SOURCE = Path("data/validation/snapshot_2026-10-19/hilma_raw.json")
OUTPUT = Path("data/validation/simulation_2026-10-19")
NOTICE = "SISÄINEN TESTI – KUVITTEELLINEN YRITYS – EI ASIAKASTOIMITUS"


def simulate(payload: dict) -> tuple[dict, list[dict]]:
    notices = payload.get("notices") or []
    if len(notices) != 100 or len({str(item.get("id")) for item in notices}) != 100:
        raise ValueError("The frozen simulation requires 100 unique authentic notice IDs")
    as_of = dt.datetime.fromisoformat(payload["retrievedAt"].replace("Z", "+00:00"))
    if as_of.tzinfo is None:
        raise ValueError("Source timestamp must include timezone")
    rows = []
    for item in notices:
        # Raw search metadata has NO source recommendation, no verified customer
        # profile, and no complete tender annex audit. Therefore no affirmative GO.
        safety = delivery_decision(item, "CONDITIONAL_GO", now=as_of)
        rows.append({
            "notice_id": str(item["id"]), "title": item.get("title") or "",
            "buyer": item.get("organisation") or "",
            "deadline_source": item.get("deadline") or "",
            "deadline_status": safety["deadline_status"],
            "attachment_status": safety["attachment_status"],
            "baseline_relevance_not_gold": baseline_label(priority_score(item)),
            "delivery_decision": safety["delivery_decision"],
            "open_checks": "; ".join(safety["delivery_reasons"]),
            "source_pointer": f"snapshot_2026-10-19/hilma_raw.json#id={item['id']}",
        })
    decisions = Counter(row["delivery_decision"] for row in rows)
    deadlines = Counter(row["deadline_status"] for row in rows)
    heuristic = Counter(row["baseline_relevance_not_gold"] for row in rows)
    stats = {
        "test_marking": NOTICE,
        "company": "Uudenmaan Korjausrakentajat Oy (kuvitteellinen)",
        "source_retrieved_at": payload["retrievedAt"],
        "notices_checked": len(rows),
        "unique_source_ids": len(rows),
        "deadline_status_counts": dict(deadlines),
        "delivery_decision_counts": dict(decisions),
        "heuristic_classes_not_gold": dict(heuristic),
        "annexes_fully_checked": 0,
        "verified_customer_eligibilities": 0,
        "independent_gold_reviews": 0,
        "verified_customer_recommendations": decisions.get("GO", 0),
        "source_coverage": "Search-index metadata only; no tender annexes or full notices",
        "relevance_precision": None,
        "first_customer_delivery_ready": False,
        "decision": "CONDITIONAL PASS – technical blocking checks work; client delivery not validated",
        "critical_qa": {
            "expired_recommended_as_GO": "PASS" if all(row["delivery_decision"] != "GO" for row in rows if row["deadline_status"] == "EXPIRED") else "FAIL",
            "unreviewed_annexes_recommended_as_GO": "PASS" if all(row["delivery_decision"] != "GO" for row in rows if row["attachment_status"] != "COMPLETE") else "FAIL",
            "all_source_ids_traceable": "PASS" if all(row["source_pointer"] for row in rows) else "FAIL",
            "independent_precision_gate": "NOT TESTED",
            "actual_customer_eligibility": "NOT TESTED",
            "customer_send": "NOT TESTED (prohibited for internal pilot)",
        },
    }
    return stats, rows


def main() -> None:
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    stats, rows = simulate(payload)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "summary.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    with (OUTPUT / "classified_notices.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    report = f"""# Urakkaluotsi – uusi sisäinen toimitussimulaatio

{NOTICE}

Testiyritys: Uudenmaan Korjausrakentajat Oy, kuvitteellinen. Aikaleima:
{stats['source_retrieved_at']} (UTC). Tämä ei ole 30 päivän toteutunut seuranta.

## Tulos

- Aidot, uniikit hakumetadatan ilmoitukset: **{stats['notices_checked']}**.
- Avoin määräaika snapshot-hetkellä: **{stats['deadline_status_counts'].get('OPEN', 0)}**.
- Päättynyt määräaika snapshot-hetkellä: **{stats['deadline_status_counts'].get('EXPIRED', 0)}**.
- Automaattisen saneerauspainotuksen alustavat osumat: **{stats['heuristic_classes_not_gold'].get('Relevantti', 0)}**.
- Automaattisesti ehdolliset osumat: **{stats['heuristic_classes_not_gold'].get('Mahdollinen', 0)}**.
- **Vahvistettuja asiakasnostoja: {stats['verified_customer_recommendations']}**.
- Riippumattomia arviointiluokkia: **0/100**; precision, FP ja FN: **NOT MEASURED**.

Kaikkien 100 rivin tunniste ja alkuperäistä hakutietoa vastaava viite ovat
`classified_notices.csv`-taulukossa. Automatiikan luokat eivät ole vertailutotuus.

## Estävät avoimet asiat

1. Täyttä tarjousasiakirja- ja liiteaineistoa ei ole haettu eikä tarkistettu.
2. Kuvitteellisen yrityksen referenssejä, taloutta, pätevyyksiä eikä kapasiteettia ole vahvistettu.
3. 100 riippumatonta lähdetarkistukseen perustuvaa luokittelua puuttuu.
4. Ilmoituksen hakumetadata ei yksin osoita hankkeen toteutusaluetta, kokoa,
   kelpoisuutta, kysymysten määräaikaa tai mahdollisia keskeytyksiä.

## QA ja hyväksyntä

- Päättyneiden ilmoitusten positiivisen noston esto: **{stats['critical_qa']['expired_recommended_as_GO']}**.
- Tarkistamattomien liitteiden positiivisen noston esto: **{stats['critical_qa']['unreviewed_annexes_recommended_as_GO']}**.
- Ilmoitustunnisteiden jäljitettävyys: **{stats['critical_qa']['all_source_ids_traceable']}**.
- Riippumaton relevanssimittaus: **NOT TESTED**.
- Oikean asiakkaan toimituskelpoisuus: **NOT TESTED**.

**CONDITIONAL PASS vain tekniselle turvaportille.** Ensimmäisen maksavan asiakkaan
toimitusvalmius **EI HYVÄKSYTTY** ennen 100 riippumatonta luokkaa,
tarjousliitteiden tarkistuksia ja yritystietojen vahvistusta. Sähköpostia ei lähetetty.
"""
    (OUTPUT / "delivery_report.md").write_text(report, encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
