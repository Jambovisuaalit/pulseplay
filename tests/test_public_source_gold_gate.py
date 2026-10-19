import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workers"))
from public_source_gold_gate import assess, evaluate_registry

class SourceGateTests(unittest.TestCase):
    def test_search_index_does_not_count_as_document(self):
        row = {"candidate_id":"A", "region_icp":"IN", "scope_icp":"MATCH",
               "individual_contract_value_verified":True, "eligibility_terms_reviewed":True,
               "evaluation_use":"HISTORICAL",
               "documents":[{"type":"tender_request", "access":"SEARCH_INDEX_ONLY",
                             "source_url":"https://example.com"}]}
        self.assertFalse(assess(row)["source_review_ready"])
        self.assertEqual(assess(row)["gold_label"], "UNREVIEWED")

    def test_complete_verified_sources_only_ready_for_review(self):
        types = ["tender_request","eligibility_terms","pricing_scope","annex_index"]
        row = {"candidate_id":"B", "region_icp":"IN", "scope_icp":"MATCH",
               "individual_contract_value_verified":True, "eligibility_terms_reviewed":True,
               "evaluation_use":"HISTORICAL",
               "documents":[{"type":x,"access":"VERIFIED_FULL_TEXT","sha256":"abc",
                             "retrieved_at":"2026-10-19T10:00:00Z",
                             "source_url":"https://example.com/"+x} for x in types]}
        result=assess(row)
        self.assertTrue(result["source_review_ready"])
        self.assertEqual(result["gold_label"], "UNREVIEWED")
        self.assertEqual(result["positive_gold_count_increment"], 0)

    def test_real_candidate_registry_is_not_gold(self):
        path=Path(__file__).resolve().parents[1]/"data/validation/public_tender_candidates_2026-10-19.json"
        result=evaluate_registry(path)
        self.assertEqual(result["total"],4)
        self.assertEqual(result["source_review_ready"],0)
        self.assertEqual(result["gold_positive"],0)

if __name__ == "__main__":
    unittest.main()
