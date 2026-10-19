import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
F=ROOT/"data/validation/p0_3d_nine_live_source_gates_2026-10-19.json"
class NineSourceGateTests(unittest.TestCase):
 def test_nine_distinct_real_candidates(self):
  x=json.loads(F.read_text(encoding="utf-8"))
  self.assertEqual(len(x["rows"]),9)
  self.assertEqual(len({r["notice_id"] for r in x["rows"]}),9)
  self.assertEqual(x["individual_lot_values_verified"],0)
  self.assertEqual(x["complete_eligibility_reviews"],0)
  self.assertIsNone(x["precision_at_30"])
 def test_all_lot_values_and_eligibility_fail_closed(self):
  for r in json.loads(F.read_text(encoding="utf-8"))["rows"]:
   self.assertIsNone(r["estimated_individual_lot_value_eur"])
   self.assertFalse(r["full_tender_annexes_verified"])
   self.assertFalse(r["company_eligibility_verified"])
   self.assertEqual(r["independent_gold_label"],"UNREVIEWED")
 def test_version_risks_and_special_conditions(self):
  rs={r["notice_id"]:r for r in json.loads(F.read_text(encoding="utf-8"))["rows"]}
  self.assertIn("59352",rs["59399"]["notices_with_related_versions"])
  self.assertIn("58430",rs["59464"]["notices_with_related_versions"])
  self.assertIn("mandatory_site_visit_before_offer",rs["59375"]["eligibility_conditions_publicly_visible"])
if __name__=="__main__":unittest.main()
