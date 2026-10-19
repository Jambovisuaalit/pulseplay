"""Independent review acceptance-gate regression tests. Synthetic cases only."""
from __future__ import annotations

import unittest

from workers.independent_validation import report, validate_frozen, make_blind_rows


def ranked_rows():
    return [{"rank": str(i), "notice_id": f"H{i:03d}"} for i in range(1, 101)]


def reviewed_rows():
    result = []
    for i in range(1, 101):
        relevant = i <= 24 or i >= 91
        result.append({
            "notice_id": f"H{i:03d}",
            "manual_label": "Relevantti" if relevant else "Epärelevantti",
            "manual_reason": "Human source assessment",
            "source_evidence": "Saved notice description",
            "reviewer_id": "reviewer-one",
            "independent_attestation": "kyllä",
            "error_type": "" if relevant else "scope_mismatch",
        })
    return result


class IndependentValidationTests(unittest.TestCase):
    def test_24_of_30_passes_with_false_positive_and_false_negative_counts(self):
        metrics = report(validate_frozen(ranked_rows()), reviewed_rows())
        self.assertEqual(metrics["status"], "PASS")
        self.assertEqual(metrics["precision_at_30"], .8)
        self.assertEqual(metrics["true_positives_top30"], 24)
        self.assertEqual(metrics["false_positives_top30"], 6)
        self.assertEqual(metrics["false_negatives_below30_within100"], 10)
        self.assertEqual(metrics["error_types_top30"], {"scope_mismatch": 6})

    def test_23_of_30_fails_not_passes(self):
        reviews = reviewed_rows()
        reviews[23]["manual_label"] = "Epärelevantti"
        reviews[23]["error_type"] = "scale_mismatch"
        metrics = report(ranked_rows(), reviews)
        self.assertEqual(metrics["status"], "FAIL")
        self.assertEqual(metrics["precision_at_30"], round(23 / 30, 4))

    def test_missing_label_never_passes_even_if_top30_complete(self):
        reviews = reviewed_rows()
        reviews[-1].update({
            "manual_label": "", "manual_reason": "", "source_evidence": "",
            "reviewer_id": "", "independent_attestation": "", "error_type": "",
        })
        metrics = report(ranked_rows(), reviews)
        self.assertEqual(metrics["status"], "NOT_VALIDATED")
        self.assertEqual(metrics["reviewed"], 99)
        self.assertIsNotNone(metrics["precision_at_30"])

    def test_ambiguous_top30_blocks_precision(self):
        reviews = reviewed_rows()
        reviews[0]["manual_label"] = "Mahdollinen"
        metrics = report(ranked_rows(), reviews)
        self.assertEqual(metrics["status"], "NOT_VALIDATED")
        self.assertIsNone(metrics["precision_at_30"])
        self.assertEqual(metrics["ambiguous_top30"], 1)

    def test_missing_independence_attestation_is_rejected(self):
        reviews = reviewed_rows()
        reviews[0]["independent_attestation"] = ""
        with self.assertRaises(ValueError):
            report(ranked_rows(), reviews)

    def test_missing_evidence_is_rejected(self):
        reviews = reviewed_rows()
        reviews[0]["source_evidence"] = ""
        with self.assertRaises(ValueError):
            report(ranked_rows(), reviews)

    def test_duplicate_review_id_is_rejected(self):
        reviews = reviewed_rows()
        reviews[0]["notice_id"] = reviews[1]["notice_id"]
        with self.assertRaises(ValueError):
            report(ranked_rows(), reviews)

    def test_blinded_template_contains_no_score_or_rank(self):
        ranked = ranked_rows()
        raw = {"notices": [
            {"id": f"H{i:03d}", "title": f"Notice {i}", "description": f"Description {i}"}
            for i in range(1, 101)
        ]}
        blind = make_blind_rows(ranked, raw)
        self.assertEqual(len(blind), 100)
        self.assertNotIn("rank", blind[0])
        self.assertNotIn("priority_score", blind[0])
        self.assertEqual({row["notice_id"] for row in blind},
                         {row["notice_id"] for row in ranked})


if __name__ == "__main__":
    unittest.main()
