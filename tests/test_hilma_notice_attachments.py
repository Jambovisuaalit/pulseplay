import io
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workers"))
from collect_hilma_notice_attachments import (
    collect, discover, fetch_attachment, validate_public_url,
)

URL = "https://cdn.hankintailmoitukset.fi/public-attachments/d190a8a2-2d9f-442d-60d6-08dd523d1dff"
XML = f"<Notice><ID>59188</ID><DocumentURL>{URL}</DocumentURL></Notice>"

class NoticeAttachmentTests(unittest.TestCase):
    def test_notice_id_and_original_xml_provenance(self):
        record = discover(XML, "59188", verified_endpoint=True)
        self.assertEqual(record["attachment_count"], 1)
        self.assertEqual(record["attachments"][0]["notice_id"], "59188")
        self.assertEqual(record["gold_label"], "UNREVIEWED")
        self.assertFalse(record["complete_package"])

    def test_wrong_source_hash_fails(self):
        with self.assertRaises(ValueError):
            discover(XML, "59188", "0"*64)

    def test_no_arbitrary_or_signed_attachment_url(self):
        for bad in [
            "http://cdn.hankintailmoitukset.fi/public-attachments/d190a8a2-2d9f-442d-60d6-08dd523d1dff",
            "https://cdn.hankintailmoitukset.fi/private-attachments/d190a8a2-2d9f-442d-60d6-08dd523d1dff",
            URL+"?sig=secret",
            "https://evil.example/public-attachments/d190a8a2-2d9f-442d-60d6-08dd523d1dff",
        ]:
            with self.subTest(url=bad), self.assertRaises(ValueError):
                validate_public_url(bad)

    def test_unrelated_text_does_not_invent_attachment(self):
        record = discover("<Notice><Title>Uspenskin katedraali</Title></Notice>", "123")
        self.assertEqual(record["attachment_count"], 0)

    def test_fake_fetch_and_no_gold(self):
        record = discover(XML, "59188", verified_endpoint=True)
        with tempfile.TemporaryDirectory() as temp:
            report = collect([record], Path(temp), fetcher=lambda _: (b"%PDF-1.4\nmock", "PDF"))
            self.assertEqual(report["downloaded"], 1)
            self.assertEqual(report["complete_tender_packages"], 0)
            self.assertIsNone(report["precision_at_30"])
            self.assertTrue((Path(temp)/"notice_59188_attachment_1.pdf").exists())

    def test_reject_zip_path_traversal(self):
        out=io.BytesIO()
        with zipfile.ZipFile(out,"w") as z:
            z.writestr("../outside.txt", "evil")
        class Response:
            headers={}
            def __enter__(self): return self
            def __exit__(self,*args): pass
            def read(self,n): return out.getvalue()
        class Opener:
            def open(self,*args,**kwargs): return Response()
        with self.assertRaises(ValueError):
            fetch_attachment(URL, opener=Opener())

    def test_unverified_local_xml_cannot_download(self):
        record=discover(XML, "59188")
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                collect([record], Path(temp), fetcher=lambda _: (b"%PDF-1.4", "PDF"))

    def test_reject_wrong_notice_link_binding(self):
        record=discover(XML, "59188", verified_endpoint=True)
        record["attachments"][0]["notice_id"]="59375"
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                collect([record], Path(temp), fetcher=lambda _: (b"%PDF-1.4", "PDF"))

if __name__ == "__main__":
    unittest.main()
