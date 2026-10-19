"""Source-based mandatory site visit blocks customer GO without attendance evidence."""
import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workers"))
from delivery_safety import delivery_decision

NOW = dt.datetime(2026, 10, 19, 12, 0, tzinfo=dt.timezone.utc)

class MandatoryVisitTests(unittest.TestCase):
    def base(self):
        return {"title": "Kastevuoren päiväkodin korjaustyöt",
                "deadline": "2026-10-30T12:00:00+02:00",
                "attachment_review_status": "COMPLETE",
                "attachment_review_evidence": "synthetic attachment audit",
                "go_no_go_suositus": "GO",
                "mandatory_site_visit_required": True}

    def test_no_attendance_is_never_go(self):
        result = delivery_decision(self.base(), "GO", NOW)
        self.assertEqual(result["delivery_decision"], "CONDITIONAL_GO")
        self.assertEqual(result["mandatory_site_visit_status"], "UNVERIFIED")

    def test_attendance_boolean_without_evidence_is_insufficient(self):
        t = self.base()
        t["mandatory_site_visit_attended"] = True
        self.assertEqual(delivery_decision(t, "GO", NOW)["mandatory_site_visit_status"], "UNVERIFIED")

    def test_documented_attendance_unblocks_only_visit_gate(self):
        t = self.base()
        t["mandatory_site_visit_attended"] = True
        t["mandatory_site_visit_evidence"] = "synthetic signed attendance confirmation"
        result = delivery_decision(t, "GO", NOW)
        self.assertEqual(result["mandatory_site_visit_status"], "VERIFIED")
        self.assertEqual(result["delivery_decision"], "GO")

    def test_expired_deadline_still_blocks_even_with_attendance(self):
        t = self.base()
        t["deadline"] = "2026-10-18T12:00:00+03:00"
        t["mandatory_site_visit_attended"] = True
        t["mandatory_site_visit_evidence"] = "synthetic confirmation"
        self.assertEqual(delivery_decision(t, "GO", NOW)["delivery_decision"], "EXPIRED")

if __name__ == "__main__":
    unittest.main()
