import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"workers"))
from build_p0_uusimaa_discovery_queue import build,triage

class FrozenUusimaaDiscoveryTests(unittest.TestCase):
    def test_textual_location_not_verified_worksite(self):
        x=triage({"id":"1","title":"Helsinki saneeraus","description":"", "estimated_value":100000})
        self.assertEqual(x["queue_priority"],1)
        self.assertEqual(x["location_status"],"REQUIRES_ORIGINAL_LOT_WORKSITE_EVIDENCE")
        self.assertFalse(x["individual_contract_value_verified"])
        self.assertEqual(x["gold_label"],"UNREVIEWED")

    def test_infrastructure_lead_does_not_rank_first(self):
        x=triage({"id":"2","title":"Espoo sillan korjaus","description":"",})
        self.assertNotEqual(x["queue_priority"],1)

    def test_frozen_100_is_not_false_independent_gold(self):
        p=Path(__file__).resolve().parents[1]/"data/validation/snapshot_2026-10-19/hilma_raw.json"
        result=build(json.loads(p.read_text(encoding="utf-8")))
        self.assertEqual(result["source_count"],100)
        self.assertEqual(result["independent_gold_positives"],0)
        self.assertIsNone(result["precision_at_30"])
        self.assertEqual(result["verified_uusimaa_worksites"],0)
        self.assertEqual(len({x["notice_id"] for x in result["cases"]}),100)

    def test_duplicates_rejected(self):
        with self.assertRaises(ValueError):
            build({"notices":[{"id":"2"},{"id":"2"}]})

if __name__=="__main__": unittest.main()
