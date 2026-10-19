"""Boundary and anti-overclaim regressions for the separately versioned ICP v2."""
import json
import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workers"))

from relevance_v2 import ALLOWED_MUNICIPALITIES, MIN_EUR, MAX_EUR, area_signal, size_signal, scope_signal, classify_notice, classify_snapshot
from prepare_holdout import prepare
from freeze_holdout_ai import freeze
from evaluate_holdout_v2 import evaluate


class V2RelevanceTests(unittest.TestCase):
    def site(self, **updates):
        item = {
            "id": "fixture",
            "title": "Huoneistosaneeraus ja maalaustyöt",
            "description": "Urakkakohde sijaitsee Espoossa osoitteessa Testikatu 1. Sisätilojen pintaremontti.",
            "estimated_value": 80000,
        }
        item.update(updates)
        return item

    def test_exactly_the_five_allowed_cities(self):
        self.assertEqual(ALLOWED_MUNICIPALITIES, {"helsinki", "espoo", "vantaa", "kauniainen", "kirkkonummi"})

    def test_outside_area_blocks_despite_strong_renovation(self):
        for city in ("Sipoossa", "Mäntsälässä", "Tuusulassa", "Hyvinkäällä", "Lohjalla", "Mäntyharjulla"):
            item = self.site(description=f"Urakkakohde sijaitsee {city}. Asuntojen pintaremontti.")
            self.assertEqual(classify_notice(item)["model_label"], "Epärelevantti", city)

    def test_buyer_city_never_proves_worksite(self):
        item = self.site(description="Pintaremontti rakennuksessa.", organisation="Helsingin kaupunki")
        self.assertEqual(area_signal(item).status, "UNKNOWN")
        self.assertEqual(classify_notice(item)["model_label"], "Mahdollinen")
        item["title"] = "Helsingin kaupungin huoneistosaneeraus"
        self.assertEqual(area_signal(item).status, "UNKNOWN")

    def test_worksite_overrides_buyer_location_but_requires_verbatim_evidence(self):
        item = self.site(organisation="Tampereen kaupunki")
        self.assertEqual(area_signal(item).status, "IN")
        item.update(worksite_municipality="Sipoo", worksite_location_evidence="NOT IN SOURCE")
        self.assertEqual(area_signal(item).status, "IN")
        item.update(worksite_municipality="Sipoo", worksite_location_evidence="Urakkakohde sijaitsee Espoossa")
        self.assertEqual(area_signal(item).status, "UNKNOWN")
        self.assertEqual(area_signal(item).reason, "WORKSITE_FIELD_CONTRADICTS_EVIDENCE")

    def test_value_boundaries_and_unverified_estimate(self):
        self.assertEqual((MIN_EUR, MAX_EUR), (10000, 250000))
        for outside in (9999, 250001, 800000):
            self.assertEqual(size_signal(self.site(estimated_value=outside)).status, "OUT")
        for inside in (10000, 250000):
            self.assertEqual(size_signal(self.site(estimated_value=inside)).status, "UNKNOWN")
        verified = self.site(estimated_value=250000, verified_single_contract_value=True,
                             contract_value_evidence="Original document confirms this single contract")
        self.assertEqual(size_signal(verified).status, "IN")
        self.assertEqual(classify_notice(verified)["model_label"], "Relevantti")

    def test_framework_total_never_confused_with_job_size(self):
        big = self.site(title="Pintaremonttien puitejärjestely", estimated_value=860000)
        self.assertEqual(size_signal(big).reason, "TOTAL_NOT_SINGLE_CONTRACT")
        self.assertEqual(classify_notice(big)["model_label"], "Mahdollinen")
        small = self.site(title="Pintaremonttien puitesopimuksen hankinta", estimated_value=90000)
        self.assertEqual(size_signal(small).status, "UNKNOWN")
        lots = self.site(description="Urakkakohde sijaitsee Espoossa. Hankinta on jaettu kolmeen osaan.", estimated_value=900000)
        self.assertEqual(size_signal(lots).status, "UNKNOWN")

    def test_zero_missing_and_invalid_estimates_fail_closed(self):
        for value in (None, 0, -1, "not disclosed"):
            result = classify_notice(self.site(estimated_value=value))
            self.assertEqual(result["size_status"], "UNKNOWN")
            self.assertNotEqual(result["model_label"], "Relevantti")

    def test_renovation_word_does_not_override_main_excluded_contract(self):
        bad_titles = (
            "Uudisrakennushanke ja pintaremontti",
            "Ikkunoiden uusiminen ja huoneistokorjaukset",
            "Kerrostalon purku-urakka ja korjaustyöt",
            "Kattourakka ja maalaustyöt",
            "Siltaurakka ja saneeraus",
            "Lattianostimien peruskorjausurakka",
            "Sprinkleriurakka ja pintaremontti",
        )
        for title in bad_titles:
            self.assertEqual(scope_signal(self.site(title=title)).status, "OUT", title)

    def test_technical_whole_must_not_be_renovation_positive(self):
        item = self.site(title="Heka peruskorjaus kokonaisurakka",
                         description="Kohde sijaitsee Helsingissä. Kokonaisurakkaan kuuluvat kaikki LVISA-työt.")
        self.assertEqual(scope_signal(item).reason, "MIXED_TECHNICAL_WHOLE")
        self.assertEqual(classify_notice(item)["model_label"], "Epärelevantti")

    def test_new_partition_walls_are_not_new_build(self):
        item = self.site(description="Kohde sijaitsee Espoossa. Rakennetaan uusi väliseinä ja tehdään pintaremontti.")
        self.assertEqual(scope_signal(item).status, "MATCH")

    def test_cancelled_even_with_verified_values(self):
        item = self.site(title="KESKEYTETTY Huoneistosaneeraus", verified_single_contract_value=True,
                         contract_value_evidence="Source annex verification")
        self.assertEqual(classify_notice(item)["model_label"], "Epärelevantti")

    def test_unknown_source_never_positive(self):
        self.assertNotEqual(classify_notice(self.site(title="", description="", estimated_value=80000))["model_label"], "Relevantti")

    def test_legacy_100_preserved_and_disjoint_from_holdout(self):
        old = json.loads((ROOT / "data/validation/snapshot_2026-10-19/hilma_raw.json").read_text(encoding="utf-8"))
        holdout = json.loads((ROOT / "data/validation/holdout_52_2026-10-19/holdout_raw.json").read_text(encoding="utf-8"))
        combined = {"retrievedAt": holdout["retrievedAt"], "notices": old["notices"] + holdout["notices"]}
        # The preparer expects a 152-notice source and must reproduce 52 rows.
        split, _ = prepare(old, combined)
        self.assertEqual([x["id"] for x in split["notices"]], [x["id"] for x in holdout["notices"]])

    def test_holdout_predictions_are_separate_from_frozen_ai_annotations(self):
        root = ROOT / "data/validation/holdout_52_2026-10-19"
        source = json.loads((root / "holdout_raw.json").read_text(encoding="utf-8"))
        with (root / "ai_silver_labels.csv").open(encoding="utf-8-sig", newline="") as h:
            ai_rows = list(csv.DictReader(h))
        metrics, detail = evaluate(source, ai_rows)
        self.assertEqual(len(detail), 52)
        self.assertEqual(metrics["legacy_provisional_ai_metrics"]["fp"], 6)
        self.assertEqual(metrics["v2_provisional_ai_metrics"]["fp"], 0)
        self.assertEqual(metrics["v2_provisional_ai_metrics"]["predicted_positive"], 0)
        self.assertIsNone(metrics["v2_provisional_ai_metrics"]["precision"])
        self.assertEqual(metrics["official_relevance_gate"], "NOT MEASURED")
        self.assertEqual(metrics["human_gold_count"], 0)

    def test_ai_holdout_quotes_are_source_grounded_and_not_model_decisions(self):
        root = ROOT / "data/validation/holdout_52_2026-10-19"
        source = json.loads((root / "holdout_raw.json").read_text(encoding="utf-8"))
        with (root / "ai_source_only_seed.tsv").open(encoding="utf-8", newline="") as h:
            seed = list(csv.DictReader(h, delimiter="\t"))
        rows = freeze(source, seed, "test", "2026-10-19T00:00:00Z")
        self.assertEqual(len(rows), 52)
        self.assertNotIn("model_label", rows[0])
        self.assertTrue(all(r["needs_external_adjudication"] == "YES" for r in rows))
        seed[0]["source_phrase"] = "invented quotation"
        with self.assertRaises(ValueError):
            freeze(source, seed, "test", "2026-10-19T00:00:00Z")

    def test_snapshot_rejects_duplicate_ids(self):
        notices = [self.site(id="1"), self.site(id="1")]
        with self.assertRaises(ValueError):
            classify_snapshot({"notices": notices}, "test.json")


if __name__ == "__main__":
    unittest.main()
