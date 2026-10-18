import datetime as dt
import json
import sys
import tempfile
import unittest
from email import policy
from email.parser import BytesParser
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'workers'))
from hilma_draft import build_draft
from hilma_http import HilmaError
from hilma_screen import screen

NOW=dt.datetime(2026,10,18,20,tzinfo=dt.timezone.utc)
PROFILE={'name':'Synthetic','allowed_regions':['FI1B1'],'service_terms':['korjaus'],'client_confirmed':False}


def row(**changes):
    value={'noticeId':1,'titleFi':'Huoneistojen korjaus','datePublished':'2026-10-18T10:00:00Z',
           'expirationDate':'2026-11-11T08:00:00Z','nutsCodes':'FI1B1','cpvCodes':'45211341','mainType':'ContractNotices'}
    return {**value,**changes}


class DraftTests(unittest.TestCase):
    def test_triage_is_not_a_relevance_prediction(self):
        result=screen(row(),PROFILE,NOW)
        self.assertEqual(result['state'],'CANDIDATE')
        self.assertIsNone(result['relevance'])
        self.assertIsNone(result['win_probability_estimate'])

    def test_repair_construction_is_not_new_construction(self):
        self.assertEqual(screen(row(titleFi="Korjausrakentaminen, vuosisopimus"),PROFILE,NOW)["state"],"CANDIDATE")

    def test_unknown_area_is_not_rejected_as_wrong_area(self):
        result=screen(row(nutsCodes='FI'),PROFILE,NOW)
        self.assertEqual(result['state'],'CANDIDATE')
        self.assertIn('Toteutusalue',result['reasons'][1])

    def test_expired_and_cancellation_are_blocked(self):
        self.assertEqual(screen(row(expirationDate='2026-10-17T08:00:00Z'),PROFILE,NOW)['state'],'EXCLUDED_DEADLINE')
        self.assertEqual(screen(row(titleFi='KESKEYTETTY korjaus'),PROFILE,NOW)['state'],'EXCLUDED_CANCELLED_SIGNAL')

    def test_bad_schema_does_not_silently_fallback(self):
        with self.assertRaises(HilmaError):screen(row(nutsCodes=[]),PROFILE,NOW)
        with self.assertRaises(HilmaError):screen(row(expirationDate='2026-10-19T10:00:00'),PROFILE,NOW)

    def test_send_is_always_blocked(self):
        with tempfile.TemporaryDirectory() as path:
            with self.assertRaisesRegex(HilmaError,'SEND_DISABLED'):
                build_draft(Path(path),PROFILE,[],'2026-10-18',send=True)
            self.assertEqual(list(Path(path).iterdir()),[])

    def test_same_draft_is_unchanged_and_has_no_addressee(self):
        card={'title':'Synthetic','buyer':'Synthetic','deadline_helsinki':'11.11.2026 klo 10',
              'summary':'Synthetic','risks':['Synthetic'],'next_action':'Review',
              'documents_url':'https://example.invalid','source_hash':'synthetic','agent_source_review_complete':True}
        with tempfile.TemporaryDirectory() as path:
            directory=Path(path)
            first=build_draft(directory,PROFILE,[card],'2026-10-18')
            before=(directory/'kooste.eml').read_bytes()
            second=build_draft(directory,PROFILE,[card],'2026-10-18')
            self.assertFalse(first['unchanged']);self.assertTrue(second['unchanged'])
            self.assertEqual(before,(directory/'kooste.eml').read_bytes())
            msg=BytesParser(policy=policy.default).parsebytes(before)
            self.assertIsNone(msg['To']);self.assertIsNone(msg['From'])
            self.assertEqual(msg['X-TenderPulse-Mode'],'DRY_RUN')
            self.assertEqual(second['sent'],0)

    def test_legacy_approval_is_not_agent_source_review(self):
        card={'source_hash':'synthetic','reviewer_approved':True}
        with tempfile.TemporaryDirectory() as path:
            with self.assertRaisesRegex(HilmaError,'agent source review'):
                build_draft(Path(path),PROFILE,[card],'2026-10-18')

    def test_unreviewed_or_unsourced_cards_rejected(self):
        with tempfile.TemporaryDirectory() as path:
            with self.assertRaises(HilmaError):build_draft(Path(path),PROFILE,[{}],'2026-10-18')
            with self.assertRaises(HilmaError):build_draft(Path(path),PROFILE,[{}]*4,'2026-10-18')


if __name__=='__main__':unittest.main()
