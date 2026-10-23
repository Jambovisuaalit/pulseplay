import datetime as dt
import ast
import csv
import json
import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workers"))

from build_validation_set import baseline_label, priority_score
from delivery_safety import attachment_status, deadline_status, delivery_decision
from hard_gate_engine import evaluate_gate, evaluate_tender
from score_validation import calculate
from simulate_delivery import simulate
from prepare_independent_review import prepare, title_fingerprint
from freeze_ai_silver_review import freeze
from score_ai_silver import compare
from simulate_ai_silver_delivery import run as simulate_ai_silver


class DeliveryP0Tests(unittest.TestCase):
    NOW = dt.datetime(2026, 10, 19, 12, tzinfo=dt.timezone.utc)

    def test_expired_timezone_and_date_only_deadlines(self):
        self.assertEqual(deadline_status("2026-10-18", self.NOW), "EXPIRED")
        self.assertEqual(deadline_status("2026-10-19", self.NOW), "UNKNOWN")
        self.assertEqual(deadline_status("2026-10-20", self.NOW), "OPEN")
        self.assertEqual(deadline_status("2026-10-19T11:00:00Z", self.NOW), "EXPIRED")
        self.assertEqual(deadline_status("2026-10-19T13:00:00Z", self.NOW), "OPEN")
        self.assertEqual(deadline_status("2026-10-19T14:00:00", self.NOW), "UNKNOWN")
        self.assertEqual(deadline_status("invalid", self.NOW), "UNKNOWN")

    def test_expired_overrides_positive_source(self):
        tender = {"deadline": "2026-10-18", "go_no_go_suositus": "GO",
                  "attachment_review_status": "COMPLETE", "attachment_review_evidence": "Checked all annexes at source"}
        self.assertEqual(delivery_decision(tender, "GO", self.NOW)["delivery_decision"], "EXPIRED")

    def test_cancelled_title_overrides_future_deadline_and_positive_source(self):
        tender = {"title": "KESKEYTETTY Maunulan kirkon tekninen peruskorjausurakka",
                  "deadline": "2026-10-27T10:00:00Z", "go_no_go_suositus": "GO",
                  "attachment_review_status": "COMPLETE", "attachment_review_evidence": "All annexes checked"}
        self.assertEqual(delivery_decision(tender, "GO", self.NOW)["delivery_decision"], "CANCELLED")
        tender["title"] = "  Peruttu: pienkorjausurakka"
        self.assertEqual(delivery_decision(tender, "GO", self.NOW)["delivery_decision"], "CANCELLED")
        tender["title"] = "Keskeytyksetön pintaremontti"
        self.assertEqual(delivery_decision(tender, "GO", self.NOW)["delivery_decision"], "GO")

    def test_source_metadata_is_not_a_positive_or_conditional_eligibility_assessment(self):
        notice = {"deadline": "2026-11-01T12:00:00+02:00"}
        self.assertEqual(delivery_decision(notice, "CONDITIONAL_GO", self.NOW)["delivery_decision"], "NOT_EVALUATED")

    def test_unverified_annexes_never_clear_go(self):
        tender = {"deadline": "2026-11-01T12:00:00+02:00", "go_no_go_suositus": "GO"}
        self.assertEqual(attachment_status(tender), "UNKNOWN")
        self.assertEqual(delivery_decision(tender, "GO", self.NOW)["delivery_decision"], "CONDITIONAL_GO")
        tender.update(attachment_review_status="COMPLETE")
        self.assertEqual(attachment_status(tender), "UNKNOWN")
        tender["attachment_review_evidence"] = "All named source annexes checked 19.10.2026"
        self.assertEqual(delivery_decision(tender, "GO", self.NOW)["delivery_decision"], "GO")

    def test_hard_gate_requires_dual_source_evidence(self):
        profile = {"profile_status": "ACTIVE", "capabilities": ["maalaus"], "verification_evidence": {}}
        gate = {"id": "x", "type": "capability", "label": "Maalaus", "required_value": "maalaus"}
        self.assertEqual(evaluate_gate(gate, profile)["status"], "UNKNOWN")
        gate["evidence"] = "Original source shows painting work"
        self.assertEqual(evaluate_gate(gate, profile)["status"], "UNKNOWN")
        profile["verification_evidence"]["capabilities"] = "Signed service inventory, 2026-10-19"
        self.assertEqual(evaluate_gate(gate, profile)["status"], "PASS")
        self.assertEqual(evaluate_tender({"id": "1", "hard_gates": [gate]}, profile)["profile_decision"], "GO")
        gate["required_value"] = "sähkötyöt"
        self.assertEqual(evaluate_gate(gate, profile)["status"], "FAIL")

    def test_unknown_hard_gate_never_passes(self):
        profile = {"profile_status": "ACTIVE", "capabilities": ["maalaus"], "verification_evidence": {}}
        gate = {"id": "x", "type": "capability", "label": "Maalaus", "required_value": "maalaus", "evidence": "Tender text"}
        self.assertEqual(evaluate_tender({"id": "x", "hard_gates": [gate]}, profile)["profile_decision"], "CONDITIONAL_GO")

    def test_frozen_100_are_actual_unique_source_ids(self):
        payload = json.loads((ROOT / "data/validation/snapshot_2026-10-19/hilma_raw.json").read_text(encoding="utf-8"))
        notices = payload["notices"]
        self.assertEqual(len(notices), 100)
        self.assertEqual(len({str(row["id"]) for row in notices}), 100)
        self.assertEqual(sum(bool(row.get("deadline")) for row in notices), 100)

    def test_test_profile_stays_unverified_and_exactly_five_municipalities(self):
        profile = json.loads((ROOT / "data/validation/simulation_ai_2026-10-19/yritysprofiili.json").read_text(encoding="utf-8"))
        self.assertEqual(profile["profile_status"], "UNCONFIGURED")
        self.assertEqual(set(profile["regions"]), {"Helsinki", "Espoo", "Vantaa", "Kauniainen", "Kirkkonummi"})
        self.assertEqual(len(profile["regions"]), 5)
        self.assertIsNone(profile["turnover_eur"])
        self.assertIsNone(profile["can_provide_financial_guarantee"])
        self.assertNotIn("verification_evidence", profile)

    def test_ingest_cpv_seeds_target_construction_not_lvi_maintenance(self):
        tree = ast.parse((ROOT / "workers/fetch_hilma.py").read_text(encoding="utf-8"))
        constants = [node.value for node in tree.body if isinstance(node, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == "CPV_CODES" for t in node.targets)]
        self.assertEqual(ast.literal_eval(constants[0]), ["45000000", "45200000", "45400000", "45450000"])


class BlindEvaluationTests(unittest.TestCase):
    def test_silver_metrics_do_not_claim_human_precision(self):
        predictions = [
            {"notice_id": str(i), "priority_score": str(5-i),
             "model_label": "Relevantti" if i < 2 else "Epärelevantti"}
            for i in range(4)
        ]
        labels = [
            {"notice_id": str(i), "ai_label": label, "reason_code": "SCOPE",
             "exact_source_phrase": "literal", "source_pointer": "archive#id=" + str(i),
             "adjudicator": "AI_SOURCE_ONLY_BLIND_V1_NOT_HUMAN_GOLD"}
            for i, label in enumerate(("Relevantti", "Epärelevantti", "Relevantti", "Mahdollinen"))
        ]
        m, rows = compare(predictions, labels, expected_size=4, topk=2)
        self.assertEqual((m["ai_observed_true_positives"], m["ai_observed_false_positives"],
                          m["ai_observed_false_negatives"]), (1, 1, 1))
        self.assertEqual(m["ai_based_false_positive_range"], [1, 1])
        self.assertEqual(m["ai_based_false_negative_range"], [1, 2])
        self.assertEqual(m["official_independent_precision_gate"], "NOT MEASURED")
        self.assertEqual(m["topk_ai_precision_range"], [0.5, 0.5])
        self.assertEqual(len(rows), 4)
        labels[0]["notice_id"] = "2"
        with self.assertRaises(ValueError):
            compare(predictions, labels, expected_size=4, topk=2)

    def test_ai_silver_review_is_blinded_and_source_quotes_exist(self):
        source = json.loads((ROOT / "data/validation/snapshot_2026-10-19/hilma_raw.json").read_text(encoding="utf-8"))
        with (ROOT / "data/validation/independent_100/ai_blind_seed.tsv").open(encoding="utf-8", newline="") as handle:
            seed = list(csv.DictReader(handle, delimiter="\t"))
        by_id = {str(item["id"]): item for item in source["notices"]}
        unsupported = []
        for row in seed:
            item = by_id[row["notice_id"]]
            phrase = row["source_phrase"]
            text = (str(item.get("title") or "") + "\n" + str(item.get("description") or ""))
            if row["reason_code"] not in {"SIZE", "NO_SOURCE"} and phrase.casefold() not in text.casefold():
                unsupported.append((row["notice_id"], phrase))
        self.assertEqual(unsupported, [])
        result = freeze(source, seed, "2026-10-19T00:00:00+00:00", "test-sha")
        self.assertEqual(len(result), 100)
        self.assertTrue(all("AI_" in row["adjudicator"] and row["requires_independent_confirmation"] == "YES"
                            for row in result))
        self.assertNotIn("model_label", result[0])

    def test_ai_silver_second_simulation_fails_closed_and_hashes_are_locked(self):
        import hashlib
        source_path = ROOT / "data/validation/snapshot_2026-10-19/hilma_raw.json"
        labels_path = ROOT / "data/validation/independent_100/ai_silver_labels.csv"
        source_bytes = source_path.read_bytes()
        label_bytes = labels_path.read_bytes()
        payload = json.loads(source_bytes)
        labels = list(csv.DictReader(label_bytes.decode("utf-8-sig").splitlines()))
        metrics = json.loads((ROOT / "data/validation/independent_100/ai_silver_metrics.json").read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "data/validation/independent_100/ai_silver_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256(source_bytes).hexdigest(), manifest["source_sha256"])
        summary, rows = simulate_ai_silver(payload, labels, metrics, manifest, source_bytes, label_bytes)
        self.assertEqual(len(rows), 100)
        self.assertEqual(summary["verified_customer_recommendations"], 0)
        self.assertEqual(summary["relevance_precision"], None)
        self.assertEqual(summary["delivery_decision_counts"].get("CANCELLED"), 1)
        self.assertEqual(next(row for row in rows if row["notice_id"] == "59352")["delivery_decision"], "CANCELLED")
        self.assertEqual(next(row for row in rows if row["notice_id"] == "59188")["ai_silver_label_not_gold"], "Relevantti")
        with self.assertRaises(ValueError):
            simulate_ai_silver(payload, labels, metrics, manifest, source_bytes + b" ", label_bytes)
        with self.assertRaises(ValueError):
            simulate_ai_silver(payload, labels, metrics, manifest, source_bytes, label_bytes + b" ")

    def make_rows(self):
        predictions, labels = [], []
        for i in range(100):
            notice_id = str(1000 + i)
            predictions.append({"notice_id": notice_id, "priority_score": str(100 - i),
                                "model_label": "Relevantti" if i < 30 else "Epärelevantti"})
            truth = "Relevantti" if i < 24 or 30 <= i < 40 else "Epärelevantti"
            labels.append({"notice_id": notice_id, "reviewer_id": "human-A", "reviewed_at": "2026-10-19",
                           "manual_label": truth, "manual_reason": "Checked original description",
                           "source_evidence": "Source quote and ID", "source_checked": "YES", "error_type": "palvelu"})
        return predictions, labels

    def test_confusion_and_exact_80_percent_boundary(self):
        predictions, labels = self.make_rows()
        metrics = calculate(predictions, labels)
        self.assertEqual(metrics["precision"], 0.8)
        self.assertEqual(metrics["top30_precision"], 0.8)
        self.assertEqual(metrics["false_positives"], 6)
        self.assertEqual(metrics["false_negatives"], 10)
        self.assertEqual(metrics["true_positives"], 24)
        self.assertEqual(metrics["rows_unreviewed"], 0)
        self.assertEqual(metrics["relevance_gate"], "PASS")

    def test_unreviewed_top30_not_removed_from_denominator(self):
        predictions, labels = self.make_rows()
        labels[0]["manual_label"] = ""
        metrics = calculate(predictions, labels)
        self.assertIsNone(metrics["precision"])
        self.assertIsNone(metrics["top30_precision"])
        self.assertEqual(metrics["top30_gold_reviewed"], 29)
        self.assertEqual(metrics["rows_unreviewed"], 1)
        self.assertEqual(metrics["relevance_gate"], "NOT MEASURED")

    def test_model_claim_cannot_be_gold(self):
        predictions, labels = self.make_rows()
        labels[0]["reviewer_id"] = "model"
        metrics = calculate(predictions, labels)
        self.assertEqual(metrics["rows_unreviewed"], 1)
        self.assertEqual(len(metrics["invalid_label_claims"]), 1)

    def test_duplicate_and_id_mismatch_fail_closed(self):
        predictions, labels = self.make_rows()
        predictions[1]["notice_id"] = predictions[0]["notice_id"]
        with self.assertRaises(ValueError):
            calculate(predictions, labels)

    def test_renovation_ranks_above_lvi(self):
        renovation = priority_score({"title": "Helsingin huoneistojen saneeraus ja maalaus"})
        technical = priority_score({"title": "Laaja LVI- ja sähkötekninen kokonaisurakka"})
        self.assertGreater(renovation, technical)
        self.assertEqual(baseline_label(renovation), "Relevantti")

    def test_new_delivery_simulation_blocks_unknown_annexes(self):
        notices = [
            {"id": str(i), "title": "Huoneistosaneeraus", "deadline": "2026-11-30T12:00:00+02:00"}
            for i in range(100)
        ]
        stats, rows = simulate({"retrievedAt": "2026-10-19T00:12:27+00:00", "notices": notices})
        self.assertEqual(stats["verified_customer_recommendations"], 0)
        self.assertEqual(len(rows), 100)
        self.assertTrue(all(row["attachment_status"] == "UNKNOWN" for row in rows))

    def test_blind_source_preflight_never_claims_gold_or_reads_predictions(self):
        payload = json.loads((ROOT / "data/validation/snapshot_2026-10-19/hilma_raw.json").read_text(encoding="utf-8"))
        audit, rows = prepare(payload, "snapshot-sha")
        self.assertEqual(audit["unreviewed_count"], 100)
        self.assertEqual(audit["estimated_value_present"], 35)
        self.assertEqual(len(rows), 100)
        self.assertEqual(len({row["notice_id"] for row in rows}), 100)
        self.assertTrue(all(row["independent_gold_review"] == "PENDING" for row in rows))
        self.assertTrue(all(row["full_notice_checked"] == "NO" for row in rows))
        self.assertNotIn("model_label", rows[0])
        self.assertNotIn("priority_score", rows[0])
        self.assertNotIn("manual_label", rows[0])
        self.assertIn(["58430", "59464"], audit["possible_duplicate_title_groups"])
        self.assertIn(["59352", "59399"], audit["possible_duplicate_title_groups"])
        self.assertIn("59352", audit["cancelled_in_title_ids"])

    def test_source_preflight_excerpts_are_verbatim_and_not_verdicts(self):
        sample = {"retrievedAt": "2026-10-19T00:12:27Z", "notices": [
            {"id": str(i), "title": "Helsingin huoneistoremontti", "description": "Pintaremontti Helsingissä."}
            for i in range(100)
        ]}
        audit, rows = prepare(sample, "test-sha")
        self.assertEqual(audit["independent_gold_labels"], 0)
        self.assertTrue(all("Pintaremontti" in row["service_cue_quote_not_verdict"]
                            or "huoneisto" in row["service_cue_quote_not_verdict"].lower() for row in rows))
        self.assertTrue(all(row["area_name_quote_not_verified_worksite"] for row in rows))
        self.assertEqual(title_fingerprint("KESKEYTETTY Maunulan kirkon tekninen peruskorjausurakka"),
                         title_fingerprint("Maunulan kirkon tekninen peruskorjausurakka"))


if __name__ == "__main__":
    unittest.main()
