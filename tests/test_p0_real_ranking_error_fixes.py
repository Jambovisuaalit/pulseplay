import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"workers"))
from relevance_v2 import classify_notice, size_signal, area_signal
F=ROOT/"data/validation/snapshot_2026-10-19/hilma_raw.json"
class ActualRankingFixTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.data={str(r["id"]):r for r in json.loads(F.read_text(encoding="utf-8"))["notices"]}
 def test_cancelled_maunula_stays_excluded(self):
  x=classify_notice(self.data["59352"])
  self.assertEqual(x["model_label"],"Epärelevantti")
  self.assertIn("CANCELLED_SOURCE_STATUS",x["reasons"])
  self.assertEqual(x["priority_hint_not_probability"],0)
 def test_framework_mantyharju_excluded_without_lot_total(self):
  n=self.data["59573"]
  x=classify_notice(n)
  self.assertEqual(x["area_status"],"OUT")
  self.assertEqual(x["model_label"],"Epärelevantti")
  self.assertEqual(size_signal(n).reason,"TOTAL_NOT_SINGLE_CONTRACT")
  self.assertEqual(x["priority_hint_not_probability"],0)
 def test_new_competition_not_auto_cancelled(self):
  n=self.data["59399"]
  x=classify_notice(n)
  self.assertNotIn("CANCELLED_SOURCE_STATUS",x["reasons"])
 def test_expired_at_explicit_snapshot_time(self):
  n={**self.data["59399"],"evaluation_time_utc":"2026-12-01T00:00:00Z"}
  x=classify_notice(n)
  self.assertEqual(x["model_label"],"Epärelevantti")
  self.assertIn("EXPIRED_AT_EVALUATION_TIME",x["reasons"])
 def test_no_unverified_single_contract_value_from_framework(self):
  n={"id":"t1","title":"Huoneistoremonttien puitejärjestely","description":"Kohde sijaitsee Espoossa",
    "estimated_value":200000,"verified_single_contract_value":True,"contract_value_evidence":"claimed"}
  self.assertEqual(size_signal(n).reason,"TOTAL_NOT_SINGLE_CONTRACT")
if __name__=="__main__":unittest.main()
