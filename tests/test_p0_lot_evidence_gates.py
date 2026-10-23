import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"workers"))
from build_p0_lot_evidence_gates import build
SRC=ROOT/"data/validation/p0_3d_nine_live_source_gates_2026-10-19.json"
class LotGateTests(unittest.TestCase):
 def test_nine_notice_placeholders_are_not_verified_lots(self):
  result=build(json.loads(SRC.read_text(encoding="utf-8")))
  self.assertEqual(result["input_notice_count"],9)
  self.assertEqual(result["official_lots_verified"],0)
  self.assertEqual(result["customer_go_count"],0)
  self.assertIsNone(result["precision_at_30"])
  self.assertTrue(all(not n["lot_count_verified"] and n["delivery_decision"]=="HOLD_NO_GO" for n in result["rows"]))
 def test_nine_properties_do_not_become_nine_lots(self):
  x=build(json.loads(SRC.read_text(encoding="utf-8")))
  item=next(n for n in x["rows"] if n["notice_id"]=="59464")
  self.assertEqual(len(item["lots"]),1)
  self.assertIsNone(item["lots"][0]["lot_id"])
  self.assertEqual(item["lots"][0]["lot_separation_status"],"MULTIPLE_LOCATIONS_NOT_PROOF_OF_SEPARATE_LOTS")
 def test_no_artificial_lot_value(self):
  x=build(json.loads(SRC.read_text(encoding="utf-8")))
  self.assertTrue(all(lot["individual_lot_value_eur"] is None and lot["value_within_target_icp"]=="UNKNOWN" for n in x["rows"] for lot in n["lots"]))
 def test_non_source_pass_rejected(self):
  src=json.loads(SRC.read_text(encoding="utf-8"))
  src["rows"][0]["estimated_individual_lot_value_eur"]=100000
  with self.assertRaises(ValueError):build(src)
if __name__=="__main__":unittest.main()
