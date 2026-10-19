import json
import sys
import unittest
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"workers"))
from guard_p0_notice_versions import guard
from build_p0_full_source_universe import build
from evaluate_p0_independent_acceptance import assess

class P0NextStagesTests(unittest.TestCase):
 def test_version_guard_expiration_and_no_go(self):
  data=json.loads((ROOT/"data/validation/p0_3d_nine_live_source_gates_2026-10-19.json").read_text(encoding="utf-8"))
  a=guard(data,datetime.fromisoformat("2026-10-19T07:35:00+00:00"))
  self.assertEqual(a["cases"],9)
  self.assertEqual(a["customer_go_count"],0)
  self.assertIsNone(a["precision_at_30"])
  self.assertTrue(all(r["hold_reasons"] for r in a["rows"]))
  later=guard(data,datetime.fromisoformat("2026-12-01T00:00:00+00:00"))
  self.assertEqual(later["expired"],9)
 def test_full_frozen_universe_not_30_verified_jobs(self):
  src=[]
  for rel in ("snapshot_2026-10-19/hilma_raw.json","holdout_52_2026-10-19/holdout_raw.json"):
   p=ROOT/"data/validation"/rel
   src.append((rel,json.loads(p.read_text(encoding="utf-8"))["notices"]))
  a=build(src)
  self.assertEqual(a["real_unique_notices"],152)
  self.assertEqual(a["verified_uusimaa_renovation_jobs"],0)
  self.assertIsNone(a["precision_at_30"])
  self.assertEqual(len({r["notice_id"] for r in a["rows"]}),152)
 def test_independent_review_not_invented(self):
  src=build([("mock",[{"id":"10"},{"id":"11"}])])
  x=assess(src,[])
  self.assertEqual(x["independently_adjudicated"],0)
  self.assertIsNone(x["precision_at_30"])
  with self.assertRaises(ValueError):assess(src,[{"notice_id":"404"}])
if __name__=="__main__":unittest.main()
