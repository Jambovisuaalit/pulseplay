import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workers"))
from extract_public_pdf_requirements import leads_by_page

class PublicPDFRequirementTests(unittest.TestCase):
    def test_page_provenance_and_no_gold(self):
        text="[[PAGE 1]]\nTarjouspyyntö\n[[PAGE 2]]\nKaksi referenssiä vaaditaan\nPakollinen kohdekäynti"
        r=leads_by_page(text,"https://example.org/file.pdf")
        self.assertEqual(r["categories"]["references"][0]["page"],2)
        self.assertEqual(r["categories"]["site_visit"][0]["page"],2)
        self.assertFalse(r["verified_eligibility"])
        self.assertEqual(r["gold_label"],"UNREVIEWED")

    def test_no_lead_is_unknown_not_zero_requirement(self):
        r=leads_by_page("[[PAGE 1]]\nRakennusurakka", "https://example.org")
        self.assertEqual(r["categories"]["turnover"],[])
        self.assertFalse(r["verified_single_contract_value"])

if __name__=="__main__":
    unittest.main()
