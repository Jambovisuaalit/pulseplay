"""Synthetic fixtures only. No network or LLM calls."""
import base64
import datetime as dt
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'workers'))
from hilma_http import Client, HilmaError, NoRedirect, SEARCH
from hilma_cpv import TIER1, groups, search_expression
from hilma_store import upsert
from hilma_detail import decode_detail
from fetch_hilma import collect, timestamp

START = '2026-09-18T19:00:00Z'
END = '2026-10-18T19:00:00Z'


def item(n):
    return {'noticeId': n, 'cpvCodes': '45211341', 'datePublished': END,
            'mainType': 'ContractNotices', 'titleFi': 'Synthetic',
            'organisationNameFi': None, 'descriptionFi': None, 'expirationDate': None}


def response(items, count):
    return json.dumps({'value': items, '@odata.count': count}).encode()


class IngestTests(unittest.TestCase):
    def test_host_allowlist_before_request(self):
        opener = Mock()
        client = Client('synthetic-secret', opener)
        for url in ['http://api.hankintailmoitukset.fi/x', 'https://evil.test/x',
                    'https://api.hankintailmoitukset.fi.evil.test/x',
                    'https://api.hankintailmoitukset.fi@evil.test/x']:
            with self.assertRaises(HilmaError):
                client.request(url)
        opener.open.assert_not_called()

    def test_redirects_disabled(self):
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, '', {}, 'https://evil.test'))
        opener = Mock()
        opener.open.side_effect = urllib.error.HTTPError(SEARCH, 302, '', {}, None)
        with self.assertRaises(HilmaError):
            Client('test', opener).request(SEARCH)
        self.assertEqual(opener.open.call_count, 1)

    def test_three_attempts(self):
        opener, sleep = Mock(), Mock()
        opener.open.side_effect = urllib.error.HTTPError(SEARCH, 503, '', {}, None)
        with self.assertRaises(HilmaError):
            Client('test', opener, sleep).request(SEARCH)
        self.assertEqual(opener.open.call_count, 3)
        self.assertEqual([c.args[0] for c in sleep.call_args_list], [2, 4])

    def test_timezone_required(self):
        with self.assertRaisesRegex(HilmaError, 'timezone'):
            timestamp('2026-10-18T19:00:00', 'datePublished')
        self.assertEqual(timestamp(END, 'datePublished').tzinfo, dt.timezone.utc)

    def test_tree_descendants_not_padding(self):
        tree = [{'id': code, 'label': 'Synthetic'} for code in TIER1]
        tree[0]['children'] = [{'id': '45211341', 'label': 'Synthetic child'}]
        result = groups(tree)
        self.assertEqual(result[TIER1[0]], ['45000000', '45211341'])
        self.assertIn('45211341', search_expression(result))
        with self.assertRaises(HilmaError):
            groups(tree[:-1])
        tree[0]['children'] = None
        with self.assertRaisesRegex(HilmaError, 'children'):
            groups(tree)

    def test_pagination_and_raw_bytes(self):
        client = Mock()
        first = response([item(n) for n in range(1, 101)], 101)
        client.request.side_effect = [first, response([item(101)], 101)]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            notices, count = collect(client, '45211341', START, END, path)
            self.assertEqual((len(notices), count), (101, 101))
            self.assertEqual((path / 'search-0.response.json').read_bytes(), first)
            self.assertEqual(client.request.call_args_list[1].args[1]['skip'], 100)
            self.assertEqual(notices[0]['raw_json'], item(1))

    def test_schema_count_and_duplicates_fail(self):
        invalid = item(1)
        invalid['cpvCodes'] = []
        cases = [[response([invalid], 1)], [response([item(1)], 2)],
                 [response([item(1), item(1)], 2)],
                 [json.dumps({'value': [], '@odata.count': True}).encode()]]
        for pages in cases:
            with self.subTest(pages=len(pages)), tempfile.TemporaryDirectory() as directory:
                client = Mock()
                client.request.side_effect = pages
                with self.assertRaises(HilmaError):
                    collect(client, 'x', START, END, Path(directory))

    def test_detail_contract_and_id(self):
        xml = b'<ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"/>'
        raw = json.dumps({'id': 1, 'eForm': base64.b64encode(xml).decode()}).encode()
        self.assertEqual(decode_detail(raw, '1'), xml)
        with self.assertRaisesRegex(HilmaError, 'id'):
            decode_detail(raw, '2')
        with self.assertRaisesRegex(HilmaError, 'base64 XML'):
            decode_detail(b'{"id":1,"eForm":"invalid"}', '1')

    def test_second_run_upsert_and_update(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'store.json'
            one = {'id': '1', 'raw_json': item(1), 'fetched_at': END}
            self.assertEqual(upsert(path, [one], {})['new'], 1)
            self.assertEqual(upsert(path, [one], {})['skipped'], 1)
            changed = {**one, 'raw_json': {**item(1), 'titleFi': 'Changed'}}
            upsert(path, [changed], {})
            saved = json.loads(path.read_text())
            self.assertEqual(saved['count'], 1)
            self.assertEqual(saved['notices'][0]['raw_json']['titleFi'], 'Changed')


if __name__ == '__main__':
    unittest.main()
