"""Positive/negative fixtures for source extraction. Synthetic: NOT accuracy gold."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workers"))
from extract_eforms_evidence import parse_xml_evidence
from relevance_v2 import classify_notice

XML = """<ContractNotice xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
<cac:ContractingParty><cac:Party><cac:PostalAddress><cbc:CityName>Tampere</cbc:CityName></cac:PostalAddress></cac:Party></cac:ContractingParty>
<cac:ProcurementProjectLot>
 <cbc:ID>LOT-001</cbc:ID>
 <cac:ProcurementProject>
  <cbc:Description>Huoneistojen pintaremontti ja maalaustyöt</cbc:Description>
  <cac:RealizedLocation><cac:Address><cbc:CityName>Espoo</cbc:CityName></cac:Address></cac:RealizedLocation>
  <cbc:EstimatedOverallContractAmount currencyID="EUR">80000</cbc:EstimatedOverallContractAmount>
 </cac:ProcurementProject>
</cac:ProcurementProjectLot>
</ContractNotice>"""


class SourceEvidenceTests(unittest.TestCase):
    def test_positive_lot_evidence_but_no_unverified_go(self):
        data = parse_xml_evidence(XML, "saved-test.xml")
        self.assertEqual(data["lot_count"], 1)
        lot = data["lots"][0]
        self.assertEqual(lot["worksite_municipality"], "espoo")
        self.assertEqual(lot["estimated_lot_value_text"], "80000")
        self.assertFalse(lot["verified_single_contract_value"])
        self.assertFalse(data["customer_go_verified"])
        self.assertEqual(lot["source_pointer"], "saved-test.xml#ProcurementProjectLot[1]")

    def test_buyer_address_not_worksite(self):
        xml = XML.replace("<cbc:CityName>Espoo</cbc:CityName>", "")
        lot = parse_xml_evidence(xml, "saved-test.xml")["lots"][0]
        self.assertIsNone(lot["worksite_municipality"])
        self.assertEqual(lot["location_status"], "UNKNOWN")

    def test_missing_value_never_verified(self):
        xml = XML.replace('<cbc:EstimatedOverallContractAmount currencyID="EUR">80000</cbc:EstimatedOverallContractAmount>', "")
        lot = parse_xml_evidence(xml, "saved-test.xml")["lots"][0]
        self.assertEqual(lot["size_status"], "UNKNOWN")

    def test_synthetic_positive_and_negative_classifier_controls(self):
        good = {"id": "SYNTH-POS-1", "title": "Huoneistojen pintaremontti",
                "description": "Urakkakohde sijaitsee Espoossa. Huoneistojen maalaustyöt. Urakan arvo on 80 000 euroa.",
                "estimated_value": 80000, "verified_single_contract_value": True,
                "contract_value_evidence": "Urakan arvo on 80 000 euroa."}
        self.assertEqual(classify_notice(good)["model_label"], "Relevantti")
        wrong_city = dict(good, description="Urakkakohde sijaitsee Lohjalla. Huoneistojen maalaustyöt.")
        self.assertEqual(classify_notice(wrong_city)["model_label"], "Epärelevantti")
        missing_value_proof = dict(good, verified_single_contract_value=False)
        self.assertEqual(classify_notice(missing_value_proof)["model_label"], "Mahdollinen")
        # These controls exercise logic, not accuracy on actual Hilma positives.


if __name__ == "__main__":
    unittest.main()
