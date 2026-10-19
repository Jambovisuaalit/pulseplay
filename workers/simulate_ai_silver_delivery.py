"""Second offline delivery simulation using a frozen, non-gold AI source review.

Never promotes an AI label into a verified customer GO or official precision KPI.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from simulate_delivery import NOTICE, simulate

ROOT = Path("data/validation/independent_100")
SOURCE = Path("data/validation/snapshot_2026-10-19/hilma_raw.json")
OUTPUT = Path("data/validation/simulation_ai_2026-10-19")


def run(payload: dict, labels: list[dict], metrics: dict, manifest: dict, source_bytes: bytes,
        label_bytes: bytes) -> tuple[dict, list[dict]]:
    if hashlib.sha256(source_bytes).hexdigest() != manifest["source_sha256"]:
        raise ValueError("Frozen source hash changed")
    if hashlib.sha256(label_bytes).hexdigest() != manifest["ai_labels_sha256"]:
        raise ValueError("Frozen AI label hash changed")
    if metrics["frozen_ai_review_sha256"] != manifest["ai_labels_sha256"]:
        raise ValueError("AI metrics no longer match frozen labels")
    if metrics["official_independent_precision_gate"] != "NOT MEASURED":
        raise ValueError("AI silver must never satisfy official acceptance gate")
    result, raw_rows = simulate(payload)
    by_id = {row["notice_id"]: row for row in labels}
    if len(by_id) != 100 or len(labels) != 100:
        raise ValueError("AI review does not contain 100 unique rows")
    if set(by_id) != {row["notice_id"] for row in raw_rows}:
        raise ValueError("Source and AI review IDs do not match")

    rows = []
    for raw in raw_rows:
        ai = by_id[raw["notice_id"]]
        label = ai["ai_label"] or "NOT_EVALUATED"
        if ai["requires_independent_confirmation"] != "YES" or ai["metadata_only_no_annexes"] != "YES":
            raise ValueError("An AI row incorrectly claims full/independent source review")
        if label == "Relevantti":
            next_action = "Varmista tarjousasiakirjat, kohderajaus, urakkakoko ja yrityksen soveltuvuus."
        elif label == "Mahdollinen":
            next_action = "Tarkista avoin tieto alkuperäisestä ilmoituksesta ja liitteistä ennen nostoa."
        elif label == "Epärelevantti":
            next_action = "Ei asiakasnostoa AI-seulonnan perusteella; varmista hylkäys tarvittaessa."
        elif label == "NOT_EVALUATED":
            next_action = "Hanki puuttuva ilmoitusteksti; älä luokittele tai nosta."
        else:
            raise ValueError(f"Unrecognised AI label: {label}")
        rows.append({
            **raw,
            "ai_silver_label_not_gold": label,
            "ai_source_reason_code": ai["reason_code"],
            "ai_source_quote": ai["exact_source_phrase"],
            "next_action": next_action,
            "source_eligibility_verified": "NO",
            "full_annexes_checked": "NO",
        })
    decisions = Counter(row["delivery_decision"] for row in rows)
    if decisions.get("GO", 0) or any(row["delivery_decision"] == "GO" for row in rows):
        raise ValueError("Unknown company eligibility or annexes must not produce GO")
    if any(row["delivery_decision"] != "CANCELLED" for row in rows
           if row["notice_id"] == "59352"):
        raise ValueError("Known cancelled source notice was not blocked")

    result.update({
        "simulation_round": "AI_SILVER_SECOND_OFFLINE_DRY_RUN",
        "ai_review_type": manifest["review_type"],
        "ai_review_label_counts": dict(Counter(row["ai_silver_label_not_gold"] for row in rows)),
        "ai_review_source_sha256": manifest["source_sha256"],
        "ai_review_label_sha256": manifest["ai_labels_sha256"],
        "ai_review_metrics": {
            "observed_tp": metrics["ai_observed_true_positives"],
            "observed_fp": metrics["ai_observed_false_positives"],
            "observed_fn": metrics["ai_observed_false_negatives"],
            "fp_range": metrics["ai_based_false_positive_range"],
            "fn_range": metrics["ai_based_false_negative_range"],
            "precision_range": [metrics["ai_based_full_precision_lower_bound"], metrics["ai_based_full_precision_upper_bound"]],
            "known_positive_precision": metrics["ai_decisive_precision_only"],
        },
        "delivery_decision_counts": dict(decisions),
        "independent_gold_reviews": 0,
        "relevance_precision": None,
        "first_customer_delivery_ready": False,
        "decision": "CONDITIONAL PASS – offline technical safety; relevance and customer readiness not proven",
    })
    result["critical_qa"].update({
        "cancelled_recommended_as_GO": "PASS" if all(row["delivery_decision"] != "GO" for row in rows if row["notice_id"] == "59352") else "FAIL",
        "ai_review_never_claims_gold": "PASS" if result["relevance_precision"] is None and result["independent_gold_reviews"] == 0 else "FAIL",
        "source_label_and_metric_hashes": "PASS",
        "annexes_actually_reviewed": "NOT TESTED",
        "company_eligibility_actually_confirmed": "NOT TESTED",
        "unverified_worksite_location": "NOT TESTED",
        "published_or_sent": "NOT TESTED (explicitly prohibited)",
    })
    return result, rows


def main() -> None:
    source_bytes = SOURCE.read_bytes()
    payload = json.loads(source_bytes)
    label_bytes = (ROOT / "ai_silver_labels.csv").read_bytes()
    labels = list(csv.DictReader(label_bytes.decode("utf-8-sig").splitlines()))
    metrics = json.loads((ROOT / "ai_silver_metrics.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "ai_silver_manifest.json").read_text(encoding="utf-8"))
    summary, rows = run(payload, labels, metrics, manifest, source_bytes, label_bytes)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (OUTPUT / "classified_notices.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    report = f"""# Urakkaluotsi – AI-silver-uusintatoimitussimulaatio

{NOTICE}

Kuvitteellinen Uudenmaan Korjausrakentajat Oy. Tämä on *yksi* jäädytetty 100
ilmoituksen **offline-toimitusharjoitus**, ei 30 päivän toteutunut seuranta eikä
todellisen asiakkaan toimitus. Aineisto kerätty: {summary['source_retrieved_at']} UTC.

## Toimituksen määrätilanne

- Lähteestä yksilöityjä ilmoituksia: {summary['notices_checked']} / 100.
- Määräaika avoin lähdehetkellä: {summary['deadline_status_counts'].get('OPEN',0)};
  päättynyt {summary['deadline_status_counts'].get('EXPIRED',0)}.
- Nimenomaan keskeytetyiksi merkittyjä päätöksiä: {summary['delivery_decision_counts'].get('CANCELLED',0)}.
- AI-silver-lähdearvio: {summary['ai_review_label_counts']}.
- **Vahvistetut asiakasnostot ja turvallisuusportin GO: {summary['verified_customer_recommendations']}**.
- Tarjousliitteitä täysin tarkistettu: **0 / 100**. Yrityksen kelpoisuuksia
  vahvistettu: **0**. Ulkoisia gold-luokituksia: **0 / 100**.

## AI-virheanalyysi – vain kehityskäyttöön

Sokkoutetun AI-arvion perusteella baseline-seulonnassa alustavia TP/FP/FN:
{summary['ai_review_metrics']['observed_tp']} / {summary['ai_review_metrics']['observed_fp']} /
{summary['ai_review_metrics']['observed_fn']} ratkaistuissa tapauksissa.
FP:n epävarmuusväli {summary['ai_review_metrics']['fp_range']}, FN:n epävarmuusväli
{summary['ai_review_metrics']['fn_range']} ja precisionin koko positiivisen
joukon vaihteluväli {summary['ai_review_metrics']['precision_range']}.

**Virallinen precision >= 80 %: NOT MEASURED.** Tekoälyn arviot eivät ole
riippumattoman arvioijan vahvistamia oikeita luokkia. Algoritmin ja AI:n yhteinen
mahdollinen virhe sekä hakumetadatan aukot jäävät avoimiksi.

## Mahdollinen jatkoselvityskohde – ei tarjoussuositus

- Hilma ID **59188**: *Koy Espoon Tietotie 1, BIZ vuokralaismuutos*;
  ilmoituksessa kuvataan tilojen pintaremonttia Espoossa, mutta myös ilmanvaihto-,
  valaistus- ja muita LVIS-muutoksia. Alkuperäisten asiakirjojen urakkakoko,
  laajuus, vastuunjako, kelpoisuusehdot ja yrityksen soveltuvuus ovat **avoinna**.
  Metadata ilmoittaa tarjousmääräajaksi **2026-11-04T10:00:00Z**; tarkista se
  alkuperäisestä lähteestä ennen mitään toimenpidettä. Ei automaattista GO:ta.
- AI-arviossa lisäksi seitsemän *Mahdollinen*-luokkaa, joita ei ole riittävällä
  lähdevarmuudella osoitettu sopiviksi.
- Kohde `59352` sisältää sanan **KESKEYTETTY** vaikka hakumetadatan määräaika
  on tuleva: turvaportti antaa `CANCELLED` eikä GO.

## QA

{chr(10).join('- ' + k + ': **' + v + '**' for k, v in summary['critical_qa'].items())}

Toimituspäätökset, lähdetunnisteet, AI-luokat, avoimet seikat ja seuraavat
toimet löytyvät `classified_notices.csv`-taulukosta. PDF on tuotettu olemassa
olevalla Urakkaluotsin koostepohjalla. Asiakassähköpostia **ei lähetetä**.

**Johtopäätös:** tekninen turvaportti **CONDITIONAL PASS**, mutta ensimmäinen
maksava asiakastoimitus **EI HYVÄKSYTTY**. Puuttuva itsenäinen totuus,
tarjousasiakirjat, asiakaskelpoisuus ja AI-havainnoissa näkyvä heikko osuvuus
estävät valmiusväitteen. PR #4 ja #8 pysyvät yhdistämättä.
"""
    (OUTPUT / "delivery_report.md").write_text(report, encoding="utf-8")
    print(json.dumps({"counts": summary["delivery_decision_counts"], "qa": summary["critical_qa"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
