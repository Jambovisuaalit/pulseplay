import json
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"workers"))
from evaluate_uusimaa_document_coverage import assess,evaluate

class UusimaaCoverageTests(unittest.TestCase):
    def test_portal_url_does_not_count_as_source_document(self):
        r=assess({"case_id":"X","region":"IN","required_documents":["tender_request"],
                  "notice_url":"https://example.org/tender","source_documents":[]})
        self.assertEqual(r["source_verified_document_count"],0)
        self.assertFalse(r["complete_source_package"])
        self.assertEqual(r["source_gold_label"],"UNREVIEWED")

    def test_verified_document_without_value_and_eligibility_is_incomplete(self):
        r=assess({"case_id":"X","region":"IN","required_documents":["tender_request"],
                  "source_documents":[{"type":"tender_request","access":"VERIFIED_FULL_TEXT",
                  "sha256":"abcd","retrieved_at":"2026-10-19T00:00:00Z","source_url":"https://example.org/a.pdf"}]})
        self.assertEqual(r["source_verified_document_count"],1)
        self.assertFalse(r["complete_source_package"])

    def test_current_espoo_queue_has_no_gold(self):
        p=Path(__file__).resolve().parents[1]/"data/validation/uusimaa_document_coverage_queue_2026-10-19.json"
        report=evaluate(json.loads(p.read_text(encoding="utf-8")))
        self.assertEqual(report["candidates"],2)
        self.assertEqual(report["complete_packages"],0)
        self.assertEqual(report["source_gold_positives"],0)
        self.assertIsNone(report["precision_at_30"])

if __name__=="__main__":
    unittest.main()
