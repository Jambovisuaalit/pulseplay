import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workers"))
from extract_eforms_requirements import extract_requirement_leads

class RequirementLeadTests(unittest.TestCase):
    def test_references_are_leads_not_verified(self):
        xml = "<root><Description>Tarjoajalta vaaditaan kaksi referenssiä.</Description><Name>Rakennusurakka</Name></root>"
        r = extract_requirement_leads(xml, "notice.xml")
        self.assertEqual(r["requirements"]["references"]["status"], "UNVERIFIED_SOURCE_LEADS")
        self.assertIn("kaksi referenssiä", r["requirements"]["references"]["evidence_leads"][0]["exact_excerpt"])
        self.assertEqual(r["gold_label"], "UNREVIEWED")
        self.assertFalse(r["supplier_eligibility_verified"])

    def test_absence_does_not_mean_no_requirement(self):
        r = extract_requirement_leads("<root><Name>Korjausurakka</Name></root>", "notice.xml")
        self.assertEqual(r["requirements"]["turnover"]["status"], "UNKNOWN")
        self.assertFalse(r["annexes_reviewed"])

    def test_nested_text_does_not_fake_direct_tag(self):
        r = extract_requirement_leads("<root><Other><Description>Vakuus vaaditaan</Description></Other></root>", "notice.xml")
        self.assertEqual(r["requirements"]["guarantee"]["status"], "UNVERIFIED_SOURCE_LEADS")

if __name__ == "__main__":
    unittest.main()
