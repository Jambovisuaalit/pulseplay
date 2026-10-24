"""Bounded official-API collection; no attachment, LLM or email actions."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
from pathlib import Path

from hilma_detail import decode_detail
from hilma_cpv import TIER1, groups, search_expression
from hilma_http import CPV_TREE, NOTICE, SEARCH, Client, HilmaError, utc_now
from hilma_store import atomic_bytes, save_json, upsert

ROOT = Path(__file__).resolve().parents[1]
SELECT = 'noticeId,cpvCodes,datePublished,mainType,titleFi,organisationNameFi,descriptionFi,expirationDate'
CPV_CODES = ['45000000', '45200000', '45400000', '45450000']


def construction_query_groups(tree):
    # Use the official construction subtree; maintenance and consulting roots
    # remain available to the vocabulary validator but are not acquisition seeds.
    return {'45000000': groups(tree)['45000000']}


def timestamp(value, field):
    if not isinstance(value, str) or not re.search(r'(Z|[+-]\d{2}:\d{2})$', value):
        raise HilmaError(f'{field}: timezone required')
    try:
        return dt.datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(dt.timezone.utc)
    except ValueError:
        raise HilmaError(f'{field}: invalid timestamp') from None


def validate_notice(item, start, end):
    if not isinstance(item, dict):
        raise HilmaError('value item: expected object')
    notice_id = item.get('noticeId')
    if isinstance(notice_id, bool) or not isinstance(notice_id, (str, int)) or not re.fullmatch(r'\d+', str(notice_id)):
        raise HilmaError('noticeId: expected numeric id')
    if not isinstance(item.get('cpvCodes'), str):
        raise HilmaError('cpvCodes: expected string')
    if item.get('mainType') != 'ContractNotices':
        raise HilmaError('mainType: unexpected value')
    published = timestamp(item.get('datePublished'), 'datePublished')
    if not start <= published <= end:
        raise HilmaError('datePublished: outside locked window')
    for field in ('titleFi', 'organisationNameFi', 'descriptionFi', 'expirationDate'):
        if field not in item or (item[field] is not None and not isinstance(item[field], str)):
            raise HilmaError(f'{field}: expected string or null')
    if item['expirationDate'] is not None:
        timestamp(item['expirationDate'], 'expirationDate')
    codes = re.findall(r'(?<!\d)\d{8}(?!\d)', item['cpvCodes'])
    if not codes:
        raise HilmaError('cpvCodes: no recognized codes')
    return str(notice_id), codes


def collect(client, expression, start_iso, end_iso, run):
    start, end = timestamp(start_iso, 'start'), timestamp(end_iso, 'end')
    notices = {}
    count = None
    skip = 0
    while True:
        if skip >= 100000:
            raise HilmaError('skip limit reached before completion')
        body = {'search': expression, 'searchFields': 'cpvCodes', 'queryType': 'full',
                'searchMode': 'any', 'filter': f"datePublished ge {start_iso} and datePublished le {end_iso} and mainType eq 'ContractNotices'",
                'count': True, 'top': 100, 'skip': skip, 'select': SELECT,
                'orderby': 'datePublished desc,noticeId asc'}
        save_json(run / f'search-{skip}.request.json', body)
        raw = client.request(SEARCH, body)
        atomic_bytes(run / f'search-{skip}.response.json', raw)
        payload = json.loads(raw)
        if not isinstance(payload, dict) or not isinstance(payload.get('value'), list):
            raise HilmaError('value: expected list')
        current = payload.get('@odata.count')
        if isinstance(current, bool) or not isinstance(current, int) or current < 0:
            raise HilmaError('@odata.count: expected nonnegative integer')
        if count is not None and current != count:
            raise HilmaError('@odata.count: changed during pagination')
        count = current
        page = payload['value']
        if len(page) > 100:
            raise HilmaError('value: oversized page')
        for item in page:
            notice_id, codes = validate_notice(item, start, end)
            if notice_id in notices:
                raise HilmaError('noticeId: repeated across pages; pagination unstable')
            notices[notice_id] = {'id': notice_id, 'title': item['titleFi'],
                'description': item['descriptionFi'], 'organisation': item['organisationNameFi'],
                'publishedAt': item['datePublished'], 'deadline': item['expirationDate'],
                'cpv_codes': codes, 'raw_json': item, 'fetched_at': utc_now()}
        skip += len(page)
        if len(page) < 100:
            if len(notices) != count:
                raise HilmaError('@odata.count: differs from collected unique noticeIds')
            break
    return list(notices.values()), count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--measure', action='store_true', help='Collect metadata and measurement; do not update ingestion store')
    parser.add_argument('--verify-detail', action='store_true', help='Preserve one real notice detail response without guessing its schema')
    args = parser.parse_args()
    client = Client(os.environ.get('HILMA_API_KEY', ''))
    end = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    end_iso = end.isoformat().replace('+00:00', 'Z')
    start_iso = (end - dt.timedelta(days=30)).isoformat().replace('+00:00', 'Z')
    run = ROOT / 'data' / 'hilma-runs' / end.strftime('%Y%m%dT%H%M%SZ')
    if run.exists():
        raise HilmaError('run directory already exists')
    run.mkdir(parents=True)
    raw_tree = client.request(CPV_TREE)
    atomic_bytes(run / 'cpv.response.json', raw_tree)
    tree = json.loads(raw_tree)
    group_codes = construction_query_groups(tree)
    save_json(ROOT / 'fixtures/cpv-main.json', {'source': CPV_TREE, 'fetched_at': utc_now(), 'tree': tree})
    expression = search_expression(group_codes)
    notices, count = collect(client, expression, start_iso, end_iso, run)
    metadata = {'retrievedAt': utc_now(), 'publishedAfter': start_iso, 'publishedBefore': end_iso,
                'cpvCodes': CPV_CODES, 'api_count': count, 'unique_notice_ids': len(notices),
                'group_vocabulary_sizes': {key: len(value) for key, value in group_codes.items()},
                'group_notice_counts': {key: sum(bool(set(n['cpv_codes']) & set(value)) for n in notices)
                                       for key, value in group_codes.items()},
                'count_note': 'Notice IDs, not unique procurement procedures. Group counts overlap.',
                'count_accuracy': 'API count accuracy not independently audited.'}
    save_json(run / 'measurement.json', metadata)
    save_json(run / 'notices.json', {'notices': notices})
    if args.verify_detail and notices:
        detail = client.request(NOTICE + notices[0]['id'])
        atomic_bytes(run / 'detail.response', detail)
        xml = decode_detail(detail, notices[0]['id'])
        atomic_bytes(run / 'detail.xml', xml)
        save_json(run / 'detail.metadata.json', {'noticeId': notices[0]['id'], 'bytes': len(detail),
                                                'schema_status': 'id and base64 ContractNotice XML verified'})
    counts = {'fetched': len(notices), 'new': 0, 'skipped': 0, 'failed': 0}
    if not args.measure:
        counts = upsert(ROOT / 'data/hilma_raw.json', notices, metadata)
    print(json.dumps(counts))


if __name__ == '__main__':
    try:
        main()
    except HilmaError as exc:
        print(json.dumps({'failed': 1, 'error_field': str(exc)}))
        raise SystemExit(1)
