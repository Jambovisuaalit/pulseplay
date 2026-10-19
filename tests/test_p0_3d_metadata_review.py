import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"data/validation/p0_3d_30_metadata_review_2026-10-19.json"
class ReviewTests(unittest.TestCase):
    def test_all_unique_no_gold(self):
        x=json.loads(FILE.read_text(encoding="utf-8"))
        rows=x["records"]
        self.assertEqual(len(rows),30)
        self.assertEqual(len(set(r["notice_id"] for r in rows)),30)
        self.assertEqual(x["summary"]["gold_positive"],0)
        self.assertIsNone(x["summary"]["precision_at_30"])
        self.assertTrue(all(not r["document_package_complete"] and not r["offer_eligibility_verified"] and r["gold_label"]=="UNREVIEWED" for r in rows))
    def test_cancelled_and_version_groups_are_exposed(self):
        x=json.loads(FILE.read_text(encoding="utf-8"))
        by={r["notice_id"]:r for r in x["records"]}
        self.assertEqual(by["59352"]["cancellation_status"],"EXPLICITLY_CANCELLED_IN_TITLE")
        self.assertEqual(by["59352"]["potential_same_procurement_group"],by["59399"]["potential_same_procurement_group"])
        self.assertEqual(by["58430"]["potential_same_procurement_group"],by["59464"]["potential_same_procurement_group"])
    def test_expired_and_outside_region_not_silently_included(self):
        x=json.loads(FILE.read_text(encoding="utf-8"))
        self.assertEqual(x["summary"]["expired_by_saved_deadline"],sum(r["deadline_status_at_audit"]=="EXPIRED_BY_METADATA_DEADLINE" for r in x["records"]))
        self.assertEqual(x["summary"]["outside_uusimaa"],1)
        self.assertTrue(all(not r["worksite_verified_from_complete_original_tender"] for r in x["records"]))
    def test_portal_notice_e3_and_e4_not_confused(self):
        x=json.loads(FILE.read_text(encoding="utf-8"))
        by={r["notice_id"]:r for r in x["records"]}
        self.assertEqual(by["59464"]["version_review"]["portal_publication_id"],"632664")
        self.assertEqual(by["59464"]["version_review"]["notice_type"],"COMPETITION_E3")
        self.assertEqual(by["59464"]["version_review"]["other_same_named_result_notice"]["type"],"RESULT_E4")
        self.assertEqual(by["59352"]["version_review"]["delivery_state"],"EXCLUDE_CANCELLED")
        self.assertEqual(by["58430"]["version_review"]["delivery_state"],"EXCLUDE_EXPIRED")
if __name__=="__main__":unittest.main()
