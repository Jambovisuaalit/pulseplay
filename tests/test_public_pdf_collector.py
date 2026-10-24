import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "workers"))
from collect_public_tender_pdfs import validate_url, fetch_pdf

class PublicPDFCollectorTests(unittest.TestCase):
    def test_allowlisted_original(self):
        validate_url("https://web28.aanekoski.fi/dynasty10/vhp/202643420.43423.PDF")

    def test_allowlisted_hilma_public_attachment(self):
        validate_url("https://cdn.hankintailmoitukset.fi/public-attachments/d190a8a2-2d9f-442d-60d6-08dd523d1dff")
        with self.assertRaises(ValueError):
            validate_url("https://cdn.hankintailmoitukset.fi/private-attachments/d190a8a2-2d9f-442d-60d6-08dd523d1dff")

    def test_block_other_host_and_http(self):
        for url in ["http://web28.aanekoski.fi/a.pdf","https://example.com/a.pdf",
                    "https://web28.aanekoski.fi:8080/a.pdf",
                    "https://user:pass@web28.aanekoski.fi/a.pdf"]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_url(url)

    def test_non_pdf_bytes_rejected(self):
        class Response:
            headers={}
            def __enter__(self): return self
            def __exit__(self,*a): return False
            def read(self,n): return b"<html>Not a PDF</html>"
        class Opener:
            def open(self,*a,**kw): return Response()
        with self.assertRaises(ValueError):
            fetch_pdf("https://web28.aanekoski.fi/a.pdf",Opener())

if __name__ == "__main__":
    unittest.main()
