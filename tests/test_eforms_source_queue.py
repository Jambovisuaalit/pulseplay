"""Regression checks for the saved-XML evidence queue. No live calls."""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workers"))
from build_eforms_source_queue import build_queue

XML = """<ContractNotice xmlns:cbc="urn:cbc" xmlns:cac="urn:cac">
<cac:ContractingParty><cac:Party><cac:PostalAddress><cbc:CityName>Helsinki</cbc:CityName></cac:PostalAddress></cac:Party></cac:ContractingParty>
<cac:ProcurementProjectLot><cbc:ID>LOT-1</cbc:ID><cac:ProcurementProject>
<cbc:Description>Huoneistojen pintaremontti</cbc:Description>
<cac:RealizedLocation><cac:Address><cbc:CityName>Espoo</cbc:CityName></cac:Address></cac:RealizedLocation>
<cbc:EstimatedOverallContractAmount currencyID="EUR">80000</cbc:EstimatedOverallContractAmount>
</cac:ProcurementProject></cac:ProcurementProjectLot></ContractNotice>"""


class SourceQueueTests(unittest.TestCase):
    def test_saved_xml_preserves_source_and_never_fills_gold(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            source = base / "xml"
            source.mkdir()
            (source / "59188.xml").write_text(XML, encoding="utf-8")
            result = build_queue(source, base / "out")
            self.assertEqual(result["lot_count"], 1)
            self.assertEqual(result["independent_gold_count"], 0)
            with (base / "out/source_review_queue.csv").open(encoding="utf-8-sig", newline="") as f:
                row = list(csv.DictReader(f))[0]
            self.assertEqual(row["worksite_municipality"], "espoo")
            self.assertEqual(row["review_status"], "NOT_EVALUATED")
            self.assertEqual(row["gold_label"], "")
            self.assertIn("VERIFIED_SINGLE_CONTRACT_VALUE", row["missing_fields"])
            self.assertEqual((source / "59188.xml").read_text(), XML)

    def test_missing_xml_is_hard_failure(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            (base / "xml").mkdir()
            with self.assertRaisesRegex(ValueError, "No saved XML"):
                build_queue(base / "xml", base / "out")

    def test_duplicate_lot_ids_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            (base / "xml").mkdir()
            (base / "xml/a.xml").write_text(XML.replace(
                "</cac:ProcurementProjectLot>",
                "</cac:ProcurementProjectLot>" + XML.split("<cac:ProcurementProjectLot>", 1)[1].split("</cac:ProcurementProjectLot>", 1)[0].join(["<cac:ProcurementProjectLot>", "</cac:ProcurementProjectLot>"])
            ), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Duplicate lot"):
                build_queue(base / "xml", base / "out")


if __name__ == "__main__":
    unittest.main()
