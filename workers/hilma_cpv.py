"""Derive exact CPV terms from the official main-vocabulary tree."""
from __future__ import annotations

import re
from hilma_http import HilmaError

TIER1 = ('45000000', '50700000', '71300000', '71500000')


def groups(tree: object) -> dict[str, list[str]]:
    index = {}

    def visit(nodes):
        if not isinstance(nodes, list):
            raise HilmaError('CPV children: expected list')
        for node in nodes:
            if not isinstance(node, dict):
                raise HilmaError('CPV node: expected object')
            code = node.get('id')
            if not isinstance(code, str) or not re.fullmatch(r'\d{8}', code):
                raise HilmaError('CPV id: expected eight digits')
            if not isinstance(node.get('label'), str):
                raise HilmaError('CPV label: expected string')
            if code in index:
                raise HilmaError('CPV id: duplicate')
            index[code] = node
            if 'children' in node:
                visit(node['children'])
    visit(tree)

    def descendants(node):
        result = [node['id']]
        for child in node.get('children', []):
            result.extend(descendants(child))
        return result

    for code in TIER1:
        if code not in index:
            raise HilmaError('CPV id: tier 1 missing')
    return {code: sorted(descendants(index[code])) for code in TIER1}


def search_expression(group_codes: dict[str, list[str]]) -> str:
    # Exact terms avoid assumptions about zero padding and tree/prefix equivalence.
    codes = sorted({code for values in group_codes.values() for code in values})
    return ' OR '.join(codes)
