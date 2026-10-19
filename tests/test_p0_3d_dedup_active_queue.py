import json
import sys
import unittest
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"workers"))
from build_p0_3d_dedup_active_queue import build
INPUT=ROOT/"data/validation/p0_3d_30_metadata_review_2026-10-19.json"
OUTPUT=ROOT/"data/validation/p0_3d_dedup_active_review_queue_2026-10-19.json"
class P03dActiveQueueTests(unittest.TestCase):
    def test_frozen_reproducible_queue(self):
        derived=build(json.loads(INPUT.read_text(encoding="utf-8")),audit_now=datetime.fromisoformat("2026-10-19T07:35:00+00:00"))
        checked=json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(derived,checked)
        self.assertEqual(checked["input_total"],30)
        self.assertEqual(checked["active_candidate_count"],9)
    def test_no_false_gold_or_eligibility(self):
        x=json.loads(OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(x["verified_active_eligible_jobs"],0)
        self.assertIsNone(x["precision_at_30"])
        self.assertTrue(all(not r["reviewed_complete_annexes"] and not r["actual_live_status_verified"] and r["independent_gold_label"]=="UNREVIEWED" for r in x["rows"]))
    def test_cancelled_expired_outside_region_not_active(self):
        x=json.loads(OUTPUT.read_text(encoding="utf-8"))
        row={r["notice_id"]:r for r in x["rows"]}
        for ident in ("59352","58430","57598"):
            self.assertFalse(row[ident]["decision"].startswith("REVIEW_"))
        self.assertEqual(row["59352"]["decision"],"EXCLUDED_CANCELLED")
        self.assertNotIn("58430",x["candidate_notice_ids"])
        self.assertIn("59464",x["candidate_notice_ids"])
    def test_only_one_per_potential_duplicate_group_is_retained(self):
        x=json.loads(OUTPUT.read_text(encoding="utf-8"))
        kept=[r for r in x["rows"] if r["decision"].startswith("REVIEW_")]
        for group in x["possible_duplicate_groups_pending_official_cross_reference"]:
            self.assertLessEqual(sum(r["possible_same_procurement_group"]==group for r in kept),1)
if __name__=="__main__": unittest.main()
