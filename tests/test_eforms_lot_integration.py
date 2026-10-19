"""Regression controls for eForms -> relevance integration."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workers"))
from extract_eforms_evidence import parse_xml_evidence
from classify_eforms_lots import classify_lots

def xml(city="Espoo", amount="80000", desc="Huoneistojen pintaremontti ja maalaustyöt"):
    return f"""<ContractNotice xmlns:cbc="urn:cbc" xmlns:cac="urn:cac">
<cac:ContractingParty><cac:Party><cac:PostalAddress><cbc:CityName>Helsinki</cbc:CityName></cac:PostalAddress></cac:Party></cac:ContractingParty>
<cac:ProcurementProjectLot><cbc:ID>LOT-1</cbc:ID><cac:ProcurementProject>
<cbc:Description>{desc}</cbc:Description>
<cac:RealizedLocation><cac:Address><cbc:CityName>{city}</cbc:CityName></cac:Address></cac:RealizedLocation>
<cbc:EstimatedOverallContractAmount currencyID="EUR">{amount}</cbc:EstimatedOverallContractAmount>
</cac:ProcurementProject></cac:ProcurementProjectLot></ContractNotice>"""

class IntegrationTests(unittest.TestCase):
    def classify(self, **kwargs):
        return classify_lots({"id": "SYNTHETIC", "title": "Rakennustyöt"},
                             parse_xml_evidence(xml(**kwargs), "fixture.xml"))[0]

    def test_positive_is_conditional_not_customer_go(self):
        r = self.classify()
        self.assertEqual(r["model_label"], "Mahdollinen")
        self.assertEqual(r["area_status"], "IN")
        self.assertEqual(r["scope_status"], "MATCH")
        self.assertEqual(r["size_status"], "UNKNOWN")
        self.assertEqual(r["customer_go_verified"], "NO")

    def test_outside_site_blocks(self):
        self.assertEqual(self.classify(city="Lohja")["model_label"], "Epärelevantti")

    def test_buyer_city_does_not_count_as_site(self):
        self.assertEqual(self.classify(city="")["area_status"], "UNKNOWN")

    def test_ineligible_scope(self):
        self.assertEqual(self.classify(desc="Kerrostalon purku-urakka")["model_label"], "Epärelevantti")

    def test_lot_estimate_does_not_verify_unit(self):
        self.assertEqual(self.classify(amount="250000")["size_status"], "UNKNOWN")

    def test_high_lot_total_not_treated_as_individual_work_exclusion(self):
        result = self.classify(amount="900000")
        self.assertEqual(result["model_label"], "Mahdollinen")
        self.assertEqual(result["estimated_lot_value_eur_unverified"], 900000.0)
        self.assertEqual(result["size_status"], "UNKNOWN")

    def test_notice_cancelled_blocks(self):
        evidence = parse_xml_evidence(xml(), "fixture.xml")
        r = classify_lots({"id": "SYNTHETIC", "title": "Keskeytetty hankinta"}, evidence)[0]
        self.assertEqual(r["model_label"], "Epärelevantti")

if __name__ == "__main__":
    unittest.main()
