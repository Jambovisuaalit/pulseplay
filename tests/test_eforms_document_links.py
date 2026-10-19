import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"workers"))
from extract_eforms_document_links import extract,category

PUB="https://cdn.hankintailmoitukset.fi/public-attachments/d190a8a2-2d9f-442d-60d6-08dd523d1dff"
PORTAL="https://tarjouspalvelu.fi/UX/TP/SiirryTarjouspyyntoon/?tpId=631619"

class DocumentLinkTests(unittest.TestCase):
    def test_original_document_ref_with_provenance(self):
        x=extract(f"<Notice><TenderDocumentReference><URI>{PUB}</URI></TenderDocumentReference></Notice>",
            notice_id="59188",source_pointer="notice/59188.xml")
        self.assertEqual(x["counts"]["DIRECT_PUBLIC_DOCUMENT"],1)
        self.assertIn("TenderDocumentReference[1]/URI[1]",x["links"][0]["source_pointer"])
        self.assertEqual(len(x["source_xml_sha256"]),64)
        self.assertFalse(x["links"][0]["access_verified"])

    def test_portal_link_not_direct_pdf(self):
        x=extract(f"<Notice><TenderingTerms><WebsiteURI>{PORTAL}</WebsiteURI></TenderingTerms></Notice>",
            notice_id="59375",source_pointer="notice/59375.xml")
        self.assertEqual(x["counts"]["PUBLIC_PORTAL"],1)
        self.assertFalse(x["package_complete"])

    def test_buyer_homepage_does_not_become_document_link(self):
        x=extract("<Notice><ContractingParty><WebsiteURI>https://tarjouspalvelu.fi</WebsiteURI></ContractingParty></Notice>",
            notice_id="59375",source_pointer="notice/59375.xml")
        self.assertEqual(x["links"],[])

    def test_unrelated_or_http_links_fail_closed(self):
        self.assertEqual(category("http://tarjouspalvelu.fi/test"),"ACCESS_RESTRICTED_OR_UNKNOWN")
        self.assertEqual(category("https://example.org/a.pdf"),"ACCESS_RESTRICTED_OR_UNKNOWN")

    def test_original_eforms_document_access_separate_from_submission(self):
        xml = """<ContractNotice><ProcurementProjectLot><TenderingTerms>
            <CallForTendersDocumentReference><Attachment><ExternalReference>
            <URI>https://tarjouspalvelu.fi/espoo</URI>
            </ExternalReference></Attachment></CallForTendersDocumentReference>
            <TenderRecipientParty><EndpointID>https://tarjouspalvelu.fi/espoo</EndpointID></TenderRecipientParty>
            </TenderingTerms></ProcurementProjectLot></ContractNotice>"""
        x=extract(xml,notice_id="59375",source_pointer="original/59375.xml")
        self.assertEqual(x["counts"]["PUBLIC_PORTAL"],1)
        self.assertEqual(len(x["submission_endpoints"]),1)
        self.assertEqual(x["submission_endpoints"][0]["kind"],"TENDER_SUBMISSION_ENDPOINT")
        self.assertEqual(x["links"][0]["kind"],"PUBLIC_PORTAL")

    def test_no_links_is_not_a_positive(self):
        x=extract("<Notice><Name>Espoo saneeraus</Name></Notice>",notice_id="59188",source_pointer="xml")
        self.assertEqual(x["links"],[])
        self.assertEqual(x["gold_label"],"UNREVIEWED")
        self.assertIsNone(x["precision_at_30"])

if __name__=="__main__": unittest.main()
