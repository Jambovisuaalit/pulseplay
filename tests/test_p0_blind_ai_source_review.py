import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"workers"))
from evaluate_p0_blind_ai_source_review import freeze,grade,REQUIRED
class BlindAISourceTests(unittest.TestCase):
 def test_no_gold_when_missing_reviews(self):
  x=freeze([{"notice_id":str(i)} for i in range(35)])
  m=grade(x,[])
  self.assertIsNone(m["ai_precision_at_30"])
  self.assertIsNone(m["human_gold_precision_at_30"])
  self.assertEqual(m["ai_80_percent_gate"],"NOT_MEASURED")
 def test_ai_silver_24_out_of_30_only_when_evidence_complete(self):
  x=freeze([{"notice_id":str(i)} for i in range(30)])
  evidence={k:{"source_url":"https://example.org/original","source_excerpt":"quoted primary evidence","access_status":"ORIGINAL_SOURCE_VERIFIED"} for k in REQUIRED}
  reviews=[{"notice_id":str(i),"label":"RELEVANT" if i<24 else "NOT_RELEVANT",
   "reviewer_type":"AI_BLINDED_SOURCE_REVIEW","rank_seen":False,
   "model_prediction_seen":False,"independent_source_check":True,"evidence":evidence} for i in range(30)]
  m=grade(x,reviews)
  self.assertEqual(m["ai_precision_at_30"],0.8)
  self.assertEqual(m["ai_80_percent_gate"],"PASS")
  self.assertIsNone(m["human_gold_precision_at_30"])
  reviews[0]["model_prediction_seen"]=True
  self.assertIsNone(grade(x,reviews)["ai_precision_at_30"])
 def test_duplicate_and_partial_evidence_fail_closed(self):
  x=freeze([{"notice_id":str(i)} for i in range(30)])
  with self.assertRaises(ValueError):grade(x,[{"notice_id":"0"},{"notice_id":"0"}])
  m=grade(x,[{"notice_id":"0","label":"RELEVANT","reviewer_type":"AI_BLINDED_SOURCE_REVIEW"}])
  self.assertEqual(m["fully_evidenced_ai_reviews"],0)
if __name__=="__main__":unittest.main()
