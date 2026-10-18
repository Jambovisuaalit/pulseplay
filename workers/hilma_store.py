from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from hilma_http import HilmaError


def atomic_bytes(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=path.name + '.')
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def save_json(path: Path, value):
    atomic_bytes(path, json.dumps(value, ensure_ascii=False, indent=2).encode('utf-8'))


def upsert(path: Path, notices: list[dict], metadata: dict) -> dict:
    old = json.loads(path.read_text()) if path.exists() else {'notices': []}
    if not isinstance(old, dict) or not isinstance(old.get('notices'), list):
        raise HilmaError('stored notices: expected list')
    indexed = {}
    for item in old['notices']:
        if not isinstance(item, dict) or not isinstance(item.get('id'), str):
            raise HilmaError('stored id: expected string')
        if item['id'] in indexed:
            raise HilmaError('stored id: duplicate')
        indexed[item['id']] = item
    new = skipped = 0
    for item in notices:
        previous = indexed.get(item['id'])
        if previous is None:
            new += 1
        elif previous['raw_json'] == item['raw_json']:
            skipped += 1
            continue
        indexed[item['id']] = item
    save_json(path, {**metadata, 'count': len(indexed), 'notices': list(indexed.values())})
    return {'fetched': len(notices), 'new': new, 'skipped': skipped, 'failed': 0}
