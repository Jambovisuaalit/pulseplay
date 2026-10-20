import copy
import csv
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workers"))
from evaluate_holdout_v2 import OLD, ROOT, evaluate, validate_provenance


class HoldoutProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (ROOT / "holdout_raw.json").read_bytes()
        cls.source = json.loads(raw)
        cls.old = json.loads(OLD.read_bytes())
        cls.sha = hashlib.sha256(raw).hexdigest()
        with (ROOT / "ai_silver_labels.csv").open(encoding="utf-8-sig", newline="") as handle:
            cls.labels = list(csv.DictReader(handle))

    def test_real_frozen_sources_are_disjoint_but_do_not_prove_accuracy(self):
        result = validate_provenance(self.source, self.old, self.labels, self.sha)
        self.assertEqual(result["id_overlap"], 0)
        self.assertEqual(result["procedure_id_overlap"], 0)
        self.assertEqual(result["normalised_title_overlap"], 0)
        self.assertEqual(result["source_quotes_checked"], 52)
        self.assertFalse(result["independent_accuracy_proven"])

    def test_duplicate_source_cannot_hide_behind_complete_label_count(self):
        source = copy.deepcopy(self.source)
        source["notices"][1] = source["notices"][0]
        with self.assertRaises(ValueError):
            evaluate(source, self.labels)

    def test_overlap_is_recomputed_even_if_old_manifest_claimed_zero(self):
        for field in ("id", "procedure_id", "title"):
            old = copy.deepcopy(self.old)
            candidate = next(n for n in self.source["notices"] if n.get(field))
            old["notices"][0][field] = candidate[field]
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "contamination"):
                validate_provenance(self.source, old, self.labels, self.sha)

    def test_wrong_snapshot_quote_pointer_or_gold_claim_is_rejected(self):
        row = next(i for i, r in enumerate(self.labels) if r["ai_label_not_gold"])
        for field, value in (("source_sha256", "another-snapshot"),
                             ("verbatim_source_quote", "fabricated source text"),
                             ("source_pointer", "holdout_raw.json#id=other"),
                             ("full_notice_and_annexes_checked", "YES"),
                             ("needs_external_adjudication", "NO")):
            labels = copy.deepcopy(self.labels)
            labels[row][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_provenance(self.source, self.old, labels, self.sha)


if __name__ == "__main__":
    unittest.main()
