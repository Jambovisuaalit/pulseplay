import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"workers"))
from evaluate_p0_blind_ai_source_review import freeze,grade
RANK=ROOT/"data/validation/p0_frozen_ranked_100_2026-10-19.json"
REVIEW=ROOT/"data/validation/p0_blind_ai_silver_reviews_2026-10-19.json"
class ActualThirtyAISourceReviewTests(unittest.TestCase):
 def test_all_top30_unique_and_reviewed(self):
  f=freeze(json.loads(RANK.read_text(encoding="utf-8"))["ranked"])
  data=json.loads(REVIEW.read_text(encoding="utf-8"))
  ids=[r["notice_id"] for r in data["reviews"]]
  self.assertEqual(len(ids),30)
  self.assertEqual(set(ids),set(f["top30_ids"]))
 def test_fail_closed_with_missing_original_documents(self):
  f=freeze(json.loads(RANK.read_text(encoding="utf-8"))["ranked"])
  reviews=json.loads(REVIEW.read_text(encoding="utf-8"))["reviews"]
  result=grade(f,reviews)
  self.assertEqual(result["labels_submitted"],30)
  self.assertEqual(result["fully_evidenced_ai_reviews"],0)
  self.assertIsNone(result["ai_precision_at_30"])
  self.assertEqual(result["ai_80_percent_gate"],"NOT_MEASURED")
  self.assertIsNone(result["human_gold_precision_at_30"])
 def test_no_positive_without_source(self):
  rows=json.loads(REVIEW.read_text(encoding="utf-8"))["reviews"]
  self.assertEqual(sum(r["label"]=="NOT_RELEVANT" for r in rows),20)
  self.assertEqual(sum(r["label"]=="UNKNOWN" for r in rows),10)
  self.assertFalse(any(r["independent_source_check"] for r in rows))
  self.assertTrue(all(r["review_status"]=="PRELIMINARY_METADATA_ONLY" for r in rows))
if __name__=="__main__":unittest.main()
