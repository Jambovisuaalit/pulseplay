"""Guard against presenting geographical text leads as source-verified worksites."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
QUEUE=ROOT/"data/validation/p0_3d_uusimaa_30_candidate_review_queue_2026-10-19.json"

class P03dFrozenReviewQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.queue=json.loads(QUEUE.read_text(encoding="utf-8"))

    def test_30_unique_actual_source_ids(self):
        q=self.queue
        self.assertEqual(len(q["records"]),30)
        ids=[r["notice_id"] for r in q["records"]]
        self.assertEqual(len(set(ids)),30)
        sources=[]
        for rel in ("snapshot_2026-10-19/hilma_raw.json","holdout_52_2026-10-19/holdout_raw.json"):
            x=json.loads((ROOT/"data/validation"/rel).read_text(encoding="utf-8"))
            sources.extend(str(n["id"]) for n in x["notices"])
        self.assertTrue(set(ids).issubset(set(sources)))

    def test_no_implied_verified_worksite_or_gold(self):
        q=self.queue
        self.assertEqual(q["verified_uusimaa_worksites"],0)
        self.assertEqual(q["gold_positives"],0)
        self.assertIsNone(q["precision_at_30"])
        for r in q["records"]:
            self.assertIsNone(r["worksite_municipality_verified"])
            self.assertFalse(r["full_tender_documents_verified"])
            self.assertFalse(r["individual_lot_value_verified"])
            self.assertFalse(r["bidder_eligibility_verified"])
            self.assertEqual(r["source_gold_label"],"UNREVIEWED")
            self.assertEqual(r["eligibility_status"],"CONDITIONAL_SOURCE_INCOMPLETE")

    def test_negative_controls_not_erased(self):
        labels={r["provisional_scope_lead"] for r in self.queue["records"]}
        self.assertIn("CANCELLED_NOTICE",labels)
        self.assertIn("LIKELY_OUTSIDE_RENOVATION_SCOPE",labels)

if __name__=="__main__": unittest.main()
