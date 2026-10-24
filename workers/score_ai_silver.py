"""Exploratory confusion against blinded AI-silver annotations, never human gold.

The algorithm's frozen predictions are joined only *after* the source-only AI
annotations were written and hashed. All ambiguous cases stay in the denominator
of published uncertainty bounds. Do not use this report for the 80% KPI gate.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

DATA = Path("data/validation/independent_100")
PRED = DATA / "predictions.csv"
SILVER = DATA / "ai_silver_labels.csv"
MANIFEST = DATA / "ai_silver_manifest.json"
METRICS = DATA / "ai_silver_metrics.json"
COMPARISONS = DATA / "ai_silver_error_analysis.csv"
REPORT = DATA / "AI_SILVER_METRICS.md"


def csv_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def unique(rows: list[dict], key: str, source: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in rows:
        item = (row.get(key) or "").strip()
        if not item or item in out:
            raise ValueError(f"{source}: missing or duplicate ID {item!r}")
        out[item] = row
    return out


def compare(predictions: list[dict], ai_labels: list[dict], expected_size: int = 100,
            topk: int = 30) -> tuple[dict, list[dict]]:
    p, a = unique(predictions, "notice_id", "baseline"), unique(ai_labels, "notice_id", "AI silver")
    if len(p) != expected_size or set(p) != set(a):
        raise ValueError("Frozen baseline and AI-silver source IDs must match exactly")
    if not 0 < topk <= expected_size:
        raise ValueError("Invalid frozen top-k denominator")
    if any(row.get("model_label") not in ("Relevantti", "Mahdollinen", "Ei priorisoitu", "Epärelevantti") for row in p.values()):
        raise ValueError("Invalid baseline model label")
    if any(row.get("ai_label") not in ("Relevantti", "Mahdollinen", "Epärelevantti", "") for row in a.values()):
        raise ValueError("Invalid AI silver label")
    if any("AI_SOURCE_ONLY_BLIND" not in (row.get("adjudicator") or "") for row in a.values()):
        raise ValueError("Expected distinct, explicitly AI-marked blinded annotation provenance")

    ranked = sorted(predictions, key=lambda row: (-int(row.get("priority_score") or 0), row["notice_id"]))
    top = ranked[:topk]
    count = Counter()
    ai_class = Counter()
    model_class = Counter()
    causes_fp, causes_fn = Counter(), Counter()
    comparison_rows = []
    for row in ranked:
        notice_id = row["notice_id"]
        lab = a[notice_id]
        label = lab["ai_label"] or "NOT_EVALUATED"
        model = row["model_label"]
        ai_class[label] += 1
        model_class[model] += 1
        ppos = model == "Relevantti"
        if label in ("Mahdollinen", "NOT_EVALUATED"):
            outcome = "AMBIGUOUS" if label == "Mahdollinen" else "UNREVIEWABLE"
            count["unknown_predicted_positive" if ppos else "unknown_predicted_nonpositive"] += 1
        elif ppos and label == "Relevantti":
            outcome = "TP_AI"
            count["tp"] += 1
        elif ppos and label == "Epärelevantti":
            outcome = "FP_AI"
            count["fp"] += 1
            causes_fp[lab["reason_code"]] += 1
        elif not ppos and label == "Relevantti":
            outcome = "FN_AI"
            count["fn"] += 1
            causes_fn[lab["reason_code"]] += 1
        else:
            outcome = "TN_AI"
            count["tn"] += 1
        comparison_rows.append({
            "notice_id": notice_id,
            "priority_score_unvalidated": row["priority_score"],
            "model_label": model,
            "ai_silver_label_not_gold": label,
            "provisional_binary_outcome": outcome,
            "ai_reason_code": lab["reason_code"],
            "verbatim_metadata_evidence": lab["exact_source_phrase"],
            "source_pointer": lab["source_pointer"],
            "human_gold_verified": "NO",
        })

    top_labels = [a[row["notice_id"]]["ai_label"] for row in top]
    top_known_relevant = sum(label == "Relevantti" for label in top_labels)
    top_unknown = sum(label in ("Mahdollinen", "") for label in top_labels)
    predicted_positives = model_class["Relevantti"]
    known_positive_denominator = count["tp"] + count["fp"]
    metrics = {
        "status": "EXPLORATORY_AI_SILVER_NOT_INDEPENDENT_HUMAN_GOLD",
        "rows_total": expected_size,
        "ai_decisive_reviewed": ai_class["Relevantti"] + ai_class["Epärelevantti"],
        "ai_ambiguous_count": ai_class["Mahdollinen"],
        "unreviewed_count": ai_class["NOT_EVALUATED"],
        "ai_label_counts": dict(ai_class),
        "baseline_counts": dict(model_class),
        "baseline_predicted_positive": predicted_positives,
        "known_binary_count": sum(count[key] for key in ("tp", "fp", "fn", "tn")),
        "ai_observed_true_positives": count["tp"],
        "ai_observed_false_positives": count["fp"],
        "ai_observed_false_negatives": count["fn"],
        "ai_observed_true_negatives": count["tn"],
        "potentially_positive_uncertain": count["unknown_predicted_positive"],
        "potentially_missed_uncertain": count["unknown_predicted_nonpositive"],
        "ai_decisive_precision_only": round(count["tp"] / known_positive_denominator, 4)
            if known_positive_denominator else None,
        "ai_based_full_precision_lower_bound": round(count["tp"] / predicted_positives, 4)
            if predicted_positives else None,
        "ai_based_full_precision_upper_bound": round((count["tp"] + count["unknown_predicted_positive"]) / predicted_positives, 4)
            if predicted_positives else None,
        "ai_based_false_positive_range": [count["fp"], count["fp"] + count["unknown_predicted_positive"]],
        "ai_based_false_negative_range": [count["fn"], count["fn"] + count["unknown_predicted_nonpositive"]],
        "ai_false_positive_reasons": dict(causes_fp),
        "ai_false_negative_reasons": dict(causes_fn),
        "topk": topk,
        "topk_ai_known_relevant": top_known_relevant,
        "topk_ai_ambiguous_or_unreviewed": top_unknown,
        "topk_ai_precision_range": [round(top_known_relevant / topk, 4), round((top_known_relevant + top_unknown) / topk, 4)],
        "official_independent_precision": None,
        "official_independent_precision_gate": "NOT MEASURED",
        "human_independent_gold_review_count": 0,
        "note": "All confusion counts and bounds are provisional AI-vs-heuristic comparisons using only search metadata; not independent accuracy ground truth.",
    }
    return metrics, comparison_rows


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    actual_sha = hashlib.sha256(SILVER.read_bytes()).hexdigest()
    if manifest.get("ai_labels_sha256") != actual_sha:
        raise ValueError("Frozen blinded AI labels changed: do not score until re-frozen")
    metrics, rows = compare(csv_rows(PRED), csv_rows(SILVER))
    metrics["frozen_ai_review_sha256"] = actual_sha
    metrics["baseline_predictions_sha256"] = hashlib.sha256(PRED.read_bytes()).hexdigest()
    METRICS.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    with COMPARISONS.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    top_lo, top_hi = metrics["topk_ai_precision_range"]
    lo, hi = metrics["ai_based_full_precision_lower_bound"], metrics["ai_based_full_precision_upper_bound"]
    report = f"""# Urakkaluotsi – 100 ilmoituksen alustava AI-osuvuusanalyysi

SISÄINEN TESTI – KUVITTEELLINEN YRITYS – EI ASIAKASTOIMITUS

**Vertailu on AI-silver, ei riippumaton ihmisen gold.** Automaattinen algoritmi
ei kirjoittanut vertailuluokkia. AI-arviointi tehtiin jäädytetyn lähdemetadatan
perusteella sokkona ennen mallin pisteiden avaamista. Arkistosta ei tarkistettu
tarjousliitteitä, eikä todellista yrityskelpoisuutta ole osoitettu.

## Otos ja alustavat luokat

- 100 yksilöityä Hilma-hakutulosta.
- AI:n selvästi relevantiksi merkitsemiä: {metrics['ai_label_counts'].get('Relevantti', 0)}.
- AI:n poissulkemia: {metrics['ai_label_counts'].get('Epärelevantti', 0)}.
- AI:n ehdollisesti epäselviä: {metrics['ai_ambiguous_count']}.
- Lähdesisällön puuttuessa arvioimatta: {metrics['unreviewed_count']}.

## Virheanalyysi (alustava AI-vertailu)

- Mallin positiiviset nostot: {metrics['baseline_predicted_positive']}.
- Positiivinen ja AI:n perusteella relevantti: {metrics['ai_observed_true_positives']}.
- Väärä positiivinen AI-arvion perusteella: {metrics['ai_observed_false_positives']}.
- Väärä negatiivinen AI-arvion perusteella: {metrics['ai_observed_false_negatives']}.
- Oikea negatiivinen AI-arvion perusteella: {metrics['ai_observed_true_negatives']}.
- Epäselviä tai arvioimattomia otoksen rivejä: {metrics['ai_ambiguous_count'] + metrics['unreviewed_count']}.
- AI-pohjainen precision arvioitavissa oleville positiivisille: {metrics['ai_decisive_precision_only']}.
- Koko 100 rivin AI-pohjainen precision-raja: {lo}–{hi}.
- FP:n AI-pohjainen vaihteluväli: {metrics['ai_based_false_positive_range']}.
- FN:n AI-pohjainen vaihteluväli: {metrics['ai_based_false_negative_range']}.
- Top-{metrics['topk']} AI-pohjainen precision-väli: {top_lo}–{top_hi}.

## Päätös

**Virallinen 80 % precision -portti: NOT MEASURED.** AI-silver luokat eivät ole
riippumaton hyväksytty totuus. Tiedot ovat käyttökelpoisia algoritmin virheiden
diagnosointiin ja seuraavan sisäisen simulaation priorisointiin, eivät kaupalliseen
lupaukseen tai vahvistettuun asiakasnostoon. Ehdollisia rivejä ei poistettu
nimittäjistä: mahdolliset vaikutukset näkyvät vaihteluväleissä.

Lukitut lähteet: `ai_silver_manifest.json`, `ai_silver_labels.csv`,
`predictions.csv`; kohdekohtaiset vertailut: `ai_silver_error_analysis.csv`.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
