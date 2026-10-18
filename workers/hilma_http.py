"""Official-host-only transport; response bodies and credentials never enter logs."""
from __future__ import annotations

import datetime as dt
import email.utils
import json
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit

HOST = 'api.hankintailmoitukset.fi'
BASE = f'https://{HOST}'
SEARCH = BASE + '/avp/eformnotices/docs/search'
CPV_TREE = BASE + '/avp-notice/api/cpv/cpvtree?contractType=0&lang=FI'
NOTICE = BASE + '/avp-eforms/external-read/v1/notice/'


class HilmaError(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace('+00:00', 'Z')


class Client:
    def __init__(self, key: str, opener=None, sleep=time.sleep):
        if not key:
            raise HilmaError('HILMA_API_KEY puuttuu')
        self.key = key
        self.opener = opener or urllib.request.build_opener(NoRedirect())
        self.sleep = sleep

    def request(self, url: str, body: dict | None = None) -> bytes:
        parsed = urlsplit(url)
        if (parsed.scheme != 'https' or parsed.netloc != HOST
                or parsed.username or parsed.password or parsed.fragment):
            raise HilmaError('Disallowed API host')
        data = None if body is None else json.dumps(body).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={
            'Ocp-Apim-Subscription-Key': self.key,
            'Accept': 'application/json', 'Content-Type': 'application/json',
        })
        for attempt in range(3):
            try:
                with self.opener.open(req, timeout=60) as response:
                    return response.read()
            except urllib.error.HTTPError as exc:
                retry = exc.code == 429 or 500 <= exc.code <= 599
                if not retry or attempt == 2:
                    raise HilmaError(f'API HTTP {exc.code}') from None
                delay = 2 ** (attempt + 1)
                value = exc.headers.get('Retry-After')
                if value:
                    try:
                        delay = max(delay, float(value))
                    except ValueError:
                        try:
                            when = email.utils.parsedate_to_datetime(value)
                            delay = max(delay, (when - dt.datetime.now(dt.timezone.utc)).total_seconds())
                        except (TypeError, ValueError):
                            raise HilmaError('Retry-After schema') from None
                if delay > 60:
                    raise HilmaError('Retry-After exceeds 60 seconds; retry later')
                self.sleep(delay)
            except (urllib.error.URLError, TimeoutError, OSError):
                if attempt == 2:
                    raise HilmaError('API transport failed after 3 attempts') from None
                self.sleep(2 ** (attempt + 1))
        raise HilmaError('API retries exhausted')
