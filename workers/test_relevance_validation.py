import datetime as dt
import unittest

from workers.build_validation_set import is_active, priority_score, normalize_cpv
from workers.score_validation import score_rows


class RelevanceValidationTests(unittest.TestCase):
    def test_renovation_beats_unrelated_maintenance(self):
        self.assertGreater(
            priority_score({"title": "Huoneistojen saneeraus ja vuosikorjaukset"}),
            priority_score({"title": "Ajoneuvojen huolto"}),
        )

    def test_deadlines_fail_closed(self):
        as_of = dt.datetime.fromisoformat("2026-10-19T12:00:00+03:00")
        self.assertTrue(is_active({"deadline": "2026-10-20T12:00:00+03:00"}, as_of))
        self.assertFalse(is_active({"deadline": "2026-10-18T12:00:00+03:00"}, as_of))
        self.assertFalse(is_active({"deadline": "2026-10-20"}, as_of))
        self.assertFalse(is_active({"deadline": None}, as_of))

    def test_precision_uses_frozen_top30(self):
        rows = [
            {
                "rank": str(i),
                "notice_id": str(i),
                "manual_label": "Relevantti" if i <= 24 else "Epärelevantti",
            }
            for i in range(1, 101)
        ]
        result = score_rows(rows)
        self.assertEqual(result["top30_precision"], 0.8)
        self.assertTrue(result["gate_pass"])

        rows[0]["manual_label"] = ""
        result = score_rows(rows)
        self.assertIsNone(result["top30_precision"])
        self.assertFalse(result["gate_pass"])

    def test_cancelled_notice_excluded(self):
        as_of = dt.datetime.fromisoformat("2026-10-19T12:00:00+03:00")
        self.assertFalse(is_active({"title": "KESKEYTETTY Maunulan kirkko", "deadline": "2026-11-01T12:00:00+03:00"}, as_of))

    def test_region_ranking(self):
        self.assertGreater(priority_score({"title": "Korjaustyöt Espoo"}), priority_score({"title": "Korjaustyöt Kaarina"}))
        self.assertEqual(priority_score({"title": "Korjaustyöt"}), 4)

    def test_cpv_serialization(self):
        self.assertEqual(normalize_cpv("45450000"), "45450000")
        self.assertEqual(normalize_cpv(["45450000", "45200000"]), "45450000|45200000")

    def test_duplicate_id_rejected(self):
        rows = [
            {"rank": "1", "notice_id": "same", "manual_label": "Relevantti"},
            {"rank": "2", "notice_id": "same", "manual_label": "Relevantti"},
        ]
        with self.assertRaises(ValueError):
            score_rows(rows)


if __name__ == "__main__":
    unittest.main()
