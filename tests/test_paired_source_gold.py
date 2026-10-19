import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workers"))
from evaluate_paired_source_gold import evaluate

class PairedMetricsTests(unittest.TestCase):
    def test_unknown_is_excluded_and_no_precision_at_30(self):
        rows=[{"case_id":"a","gold_label":"UNREVIEWED","source_review_status":"PENDING",
               "baseline_label":"Relevantti","enhanced_label":"Relevantti"}]
        r=evaluate(rows)
        self.assertEqual(r["paired_source_verified"],0)
        self.assertIsNone(r["precision_at_30"])
        self.assertIsNone(r["baseline"]["precision"])

    def test_real_source_gold_counts_fp_and_tp(self):
        def row(i,g,b,e):
            return {"case_id":i,"gold_label":g,"source_review_status":"VERIFIED",
                    "source_quote":"Exact excerpt", "source_url":"https://example.org",
                    "baseline_label":b,"enhanced_label":e}
        rows=[row("p","POSITIVE","Mahdollinen","Relevantti"),
              row("n","NEGATIVE","Mahdollinen","Epärelevantti")]
        r=evaluate(rows)
        self.assertEqual(r["baseline"]["tp"],1)
        self.assertEqual(r["baseline"]["fp"],1)
        self.assertEqual(r["enhanced"]["tn"],1)
        self.assertEqual(r["paired_precision_difference"],0.5)
        self.assertIsNone(r["precision_at_30"])
        self.assertFalse(r["improvement_verified"])

    def test_duplicate_case_rejected(self):
        with self.assertRaises(ValueError):
            evaluate([{"case_id":"x"},{"case_id":"x"}])

if __name__ == "__main__":
    unittest.main()
