"""Validated AVP detail envelope observed on notice 59704, 2026-10-18."""
import base64
import binascii
import json
import xml.etree.ElementTree as ET

from hilma_http import HilmaError


def decode_detail(raw: bytes, notice_id: str) -> bytes:
    try:
        payload = json.loads(raw)
    except ValueError:
        raise HilmaError('detail: invalid JSON') from None
    if not isinstance(payload, dict) or type(payload.get('id')) is not int or str(payload['id']) != notice_id:
        raise HilmaError('detail id: does not match requested noticeId')
    if not isinstance(payload.get('eForm'), str):
        raise HilmaError('detail eForm: expected base64 string')
    try:
        xml = base64.b64decode(payload['eForm'], validate=True)
        root = ET.fromstring(xml)
    except (ValueError, binascii.Error, ET.ParseError):
        raise HilmaError('detail eForm: invalid base64 XML') from None
    if root.tag != '{urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2}ContractNotice':
        raise HilmaError('detail eForm: unexpected ContractNotice root')
    return xml
