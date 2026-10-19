"""Deterministic offline regression tests; never imports live credentials."""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gate_engine = module_from_path("gate_engine", ROOT / "workers/hard_gate_engine.py")
ingest = module_from_path("ingest", ROOT / "workers/fetch_hilma.py")
xml_audit = module_from_path("xml_audit", ROOT / "workers/eforms_document_audit.py")
live_probe = module_from_path("live_probe", ROOT / "workers/live_xml_probe.py")


def fixture_xml(tender_time="12:00:00+03:00", other_time=None):
    second_lot = "" if other_time is None else f"""
      <cac:ProcurementProjectLot><cbc:ID schemeName="Lot">LOT-002</cbc:ID><cac:TenderingProcess>
      <cac:TenderSubmissionDeadlinePeriod><cbc:EndDate>2026-10-31+03:00</cbc:EndDate>
      <cbc:EndTime>{other_time}</cbc:EndTime></cac:TenderSubmissionDeadlinePeriod>
      </cac:TenderingProcess></cac:ProcurementProjectLot>"""
    return f"""<ContractNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
      xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
      <cac:ProcurementProjectLot><cbc:ID schemeName="Lot">LOT-001</cbc:ID><cac:TenderingProcess>
      <cac:TenderSubmissionDeadlinePeriod><cbc:EndDate>2026-10-31+03:00</cbc:EndDate>
      <cbc:EndTime>{tender_time}</cbc:EndTime></cac:TenderSubmissionDeadlinePeriod>
      <cac:ParticipationRequestReceptionPeriod><cbc:EndDate>2026-10-12+03:00</cbc:EndDate>
      <cbc:EndTime>09:00:00+03:00</cbc:EndTime></cac:ParticipationRequestReceptionPeriod>
      </cac:TenderingProcess></cac:ProcurementProjectLot>
      {second_lot}
      <cbc:DocumentURI>https://example.invalid/portal</cbc:DocumentURI>
      </ContractNotice>"""


class OfflineSafetyTests(unittest.TestCase):
    def setUp(self):
        self.profile = {
            "profile_status": "ACTIVE",
            "capabilities": ["saneeraus"],
            "certifications": [],
            "regions": [],
        }

    def test_evidenceless_gate_never_passes(self):
        gate = {"id": "a", "type": "capability", "required_value": "saneeraus", "evidence": None}
        self.assertEqual(gate_engine.evaluate_gate(gate, self.profile)["status"], "UNKNOWN")
        self.assertEqual(gate_engine.evaluate_tender({"hard_gates": [gate]}, self.profile)["profile_decision"], "CONDITIONAL_GO")

    def test_evidenced_gate_with_active_profile(self):
        gate = {"id": "a", "type": "capability", "required_value": "saneeraus", "evidence": "Asiakirja 2, kohta 4", "evidence_verified": True}
        self.assertEqual(gate_engine.evaluate_tender({"hard_gates": [gate]}, self.profile)["profile_decision"], "GO")

    def test_unconfigured_profile_never_go(self):
        gate = {"id": "a", "type": "capability", "required_value": "saneeraus", "evidence": "Asiakirja 2, kohta 4"}
        self.assertEqual(gate_engine.evaluate_tender({"hard_gates": [gate]}, {"profile_status": "UNCONFIGURED"})["profile_decision"], "CONDITIONAL_GO")

    def test_unverified_evidence_never_passes(self):
        gate = {"id": "a", "type": "capability", "required_value": "saneeraus", "evidence": "Väitetty vaatimus"}
        self.assertEqual(gate_engine.evaluate_gate(gate, self.profile)["status"], "UNKNOWN")

    def test_dedup_latest_and_missing_id(self):
        rows = [
            {"noticeId": "42", "datePublished": "2026-10-01T10:00:00Z"},
            {"noticeId": "43", "datePublished": "2026-10-01T10:00:00Z"},
            {"noticeId": "42", "datePublished": "2026-10-02T10:00:00Z"},
        ]
        unique = ingest.deduplicate_notices(rows)
        self.assertEqual(len(unique), 2)
        self.assertEqual(unique[0]["datePublished"], "2026-10-02T10:00:00Z")
        with self.assertRaises(ValueError):
            ingest.deduplicate_notices([{}])

    def test_ingest_import_has_no_network_or_secret_requirement(self):
        self.assertIsNone(ingest.session)

    def test_pagination_records_truncation_and_duplicates(self):
        original = ingest.request_with_retry
        calls = []

        class FakeResponse:
            def __init__(self, payload):
                self.payload = payload

            def json(self):
                return self.payload

        def fake_request(method, url, **kwargs):
            skip = kwargs["json"]["skip"]
            calls.append(skip)
            rows = [{"noticeId": str(i), "datePublished": "2026-10-01T00:00:00Z"} for i in range(100)]
            return FakeResponse({"@odata.count": 1005, "value": rows})

        try:
            ingest.request_with_retry = fake_request
            rows, meta = ingest.fetch_search_notices()
            self.assertEqual(calls, list(range(0, 1000, 100)))
            self.assertEqual(len(rows), 100)
            self.assertEqual(meta["duplicates_removed"], 900)
            self.assertTrue(meta["truncated"])
            self.assertEqual(meta["reported_total"], 1005)
        finally:
            ingest.request_with_retry = original

    def test_stored_snapshot_is_not_delivery_ready(self):
        tenders = json.loads((ROOT / "data/hilma_analysoitu.json").read_text(encoding="utf-8"))
        self.assertEqual(len(tenders), 8)
        self.assertTrue(all(t.get("documents_status") != "verified" for t in tenders))

    def test_eforms_separates_tender_and_participation_deadlines(self):
        audit = xml_audit.audit_eforms_xml(fixture_xml())
        self.assertEqual([x["kind"] for x in audit["deadlines"]], ["tender", "participation_request"])
        self.assertEqual(audit["deadlines"][0]["deadline_iso"], "2026-10-31T12:00:00+03:00")
        self.assertEqual(audit["document_leads"], ["https://example.invalid/portal"])
        self.assertFalse(audit["documents_verified"])
        self.assertTrue(xml_audit.compare_index_deadline("2026-10-31T09:00:00Z", audit)["verified"])

    def test_independent_ted_sdk_example_matches_utc(self):
        """TED SDK source values, independently of our hand-built October cases."""
        xml = (ROOT / "tests/fixtures/ted_cn24_deadline_excerpt.xml").read_text(encoding="utf-8")
        audit = xml_audit.audit_eforms_xml(xml)
        self.assertEqual(audit["tender_lot_ids"], ["LOT-0000"])
        self.assertEqual(audit["deadlines"][0]["deadline_iso"], "2020-02-04T10:00:00+02:00")
        self.assertTrue(xml_audit.compare_index_deadline("2020-02-04T08:00:00Z", audit)["verified"])
        self.assertFalse(xml_audit.compare_index_deadline("2020-02-04T09:00:00Z", audit)["verified"])
        # Opening of tenders is a separate event; its date/time cannot overwrite BT-131.
        self.assertEqual(len(audit["deadlines"]), 1)
        self.assertEqual(audit["documents_status"], "unknown")
        self.assertFalse(audit["documents_verified"])

    def test_eforms_refuses_conflicting_lots_or_index(self):
        audit = xml_audit.audit_eforms_xml(fixture_xml(other_time="13:00:00+03:00"))
        self.assertFalse(xml_audit.compare_index_deadline("2026-10-31T09:00:00Z", audit)["verified"])
        audit = xml_audit.audit_eforms_xml(fixture_xml())
        self.assertFalse(xml_audit.compare_index_deadline("2026-10-31T10:00:00Z", audit)["verified"])

    def test_eforms_refuses_missing_or_conflicting_timezone(self):
        audit = xml_audit.audit_eforms_xml(fixture_xml(tender_time="12:00:00"))
        self.assertFalse(audit["deadlines"][0]["valid"])

    def test_eforms_does_not_use_deadline_under_wrong_section(self):
        malformed = fixture_xml().replace("TenderingProcess", "TenderingTerms")
        audit = xml_audit.audit_eforms_xml(malformed)
        self.assertEqual(audit["deadlines"], [])
        self.assertFalse(xml_audit.compare_index_deadline("2026-10-31T09:00:00Z", audit)["verified"])

    def test_eforms_does_not_confirm_participation_deadline_as_tender(self):
        xml = fixture_xml().replace("TenderSubmissionDeadlinePeriod", "UnrelatedPeriod")
        audit = xml_audit.audit_eforms_xml(xml)
        self.assertEqual([x["kind"] for x in audit["deadlines"]], ["participation_request"])
        self.assertFalse(xml_audit.compare_index_deadline("2026-10-12T06:00:00Z", audit)["verified"])

    def test_eforms_rejects_partial_period_even_if_index_matches(self):
        audit = xml_audit.audit_eforms_xml(fixture_xml().replace("<cbc:EndTime>12:00:00+03:00</cbc:EndTime>", ""))
        self.assertFalse(audit["deadlines"][0]["valid"])
        self.assertFalse(xml_audit.compare_index_deadline("2026-10-31T09:00:00Z", audit)["verified"])

    def test_eforms_refuses_unverified_second_lot(self):
        additional_lot = '<cac:ProcurementProjectLot><cbc:ID schemeName="Lot">LOT-002</cbc:ID></cac:ProcurementProjectLot>'
        audit = xml_audit.audit_eforms_xml(fixture_xml().replace("</ContractNotice>", additional_lot + "</ContractNotice>"))
        self.assertEqual(len(audit["deadlines"]), 2)
        self.assertFalse(xml_audit.compare_index_deadline("2026-10-31T09:00:00Z", audit)["verified"])

    def test_eforms_ignores_lot_groups_as_missing_deadlines(self):
        group = '<cac:ProcurementProjectLot><cbc:ID schemeName="LotsGroup">GLO-001</cbc:ID></cac:ProcurementProjectLot>'
        audit = xml_audit.audit_eforms_xml(fixture_xml().replace("</ContractNotice>", group + "</ContractNotice>"))
        self.assertTrue(xml_audit.compare_index_deadline("2026-10-31T09:00:00Z", audit)["verified"])
        audit = xml_audit.audit_eforms_xml(fixture_xml(tender_time="12:00:00+02:00"))
        self.assertFalse(audit["deadlines"][0]["valid"])

    def test_eforms_rejects_external_entities(self):
        with self.assertRaises(ValueError):
            xml_audit.audit_eforms_xml("<!DOCTYPE foo [<!ENTITY x SYSTEM 'file:///etc/passwd'>]><foo>&x;</foo>")

    def test_limited_probe_exactly_three_calls_without_attachments(self):
        class FakeResponse:
            status_code = 200

            def __init__(self, payload=None, text=""):
                self.payload, self.text = payload, text

            def json(self):
                return self.payload

        class FakeSession:
            def __init__(self):
                self.calls = []

            def request(self, method, url, **kwargs):
                self.calls.append((method, url, kwargs))
                if method == "POST":
                    return FakeResponse({"value": [
                        {"noticeId": "101", "expirationDate": "2026-10-31T09:00:00Z"},
                        {"noticeId": "102", "expirationDate": "2026-10-31T09:00:00Z"},
                    ]})
                return FakeResponse(text=fixture_xml())

        session = FakeSession()
        probe = live_probe.LimitedProbe(session, "test-placeholder")
        result = probe.run()
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["requests_attempted"], 3)
        self.assertEqual(result["xml_success_count"], 2)
        self.assertTrue(all(row["deadline_verified"] for row in result["records"]))
        self.assertEqual([entry[0] for entry in session.calls], ["POST", "GET", "GET"])
        self.assertTrue(all(entry[2]["allow_redirects"] is False for entry in session.calls))
        self.assertTrue(all("attachment" not in entry[1] for entry in session.calls))
        with self.assertRaises(RuntimeError):
            probe.call("GET", "https://example.invalid/extra")

    def test_limited_probe_counts_failures_without_retry(self):
        class FakeSession:
            def __init__(self):
                self.calls = 0

            def request(self, *args, **kwargs):
                self.calls += 1
                raise TimeoutError("synthetic timeout")

        session = FakeSession()
        result = live_probe.LimitedProbe(session, "test-placeholder").run()
        self.assertEqual(result["requests_attempted"], 1)
        self.assertEqual(session.calls, 1)
        self.assertEqual(result["status"], "INCOMPLETE")


if __name__ == "__main__":
    unittest.main()
