"""Validate PBI references and dependency order without assuming completion."""

import json
from pathlib import Path

PBIS = Path(__file__).resolve().parents[1] / 'docs' / 'pbis.json'


def validate_pbis(pbis):
    if not isinstance(pbis, list) or not pbis:
        raise ValueError('Expected a nonempty PBI list')
    by_key, numbers = {}, set()
    for pbi in pbis:
        if not isinstance(pbi, dict):
            raise ValueError('PBI must be an object')
        key = pbi.get('key')
        epic = pbi.get('epic')
        if not isinstance(key, str) or type(epic) is not int or not 1 <= epic <= 9:
            raise ValueError('Invalid PBI key or epic')
        if key.count('.') != 1 or not key.startswith(f'{epic:02d}.') or not key.split('.')[1].isdigit():
            raise ValueError('PBI key does not match epic')
        if key in by_key:
            raise ValueError('Duplicate PBI key')
        number = pbi.get('number')
        if type(number) is not int or number <= 0 or number in numbers:
            raise ValueError('Invalid or duplicate Issue number')
        for field in ('title', 'value'):
            if not isinstance(pbi.get(field), str) or not pbi[field].strip():
                raise ValueError(f'Missing {field}')
        criteria = pbi.get('criteria')
        if not isinstance(criteria, list) or not criteria or any(
            not isinstance(item, str) or not item.strip() for item in criteria
        ):
            raise ValueError('Missing acceptance criteria')
        deps = pbi.get('deps')
        if not isinstance(deps, list) or any(not isinstance(dep, str) for dep in deps):
            raise ValueError('Invalid dependency list')
        if len(set(deps)) != len(deps):
            raise ValueError('Duplicate dependency')
        by_key[key] = pbi
        numbers.add(number)
    for pbi in pbis:
        if any(dep not in by_key for dep in pbi['deps']):
            raise ValueError('Unknown dependency')
    visiting, visited, order = set(), set(), []

    def visit(key):
        if key in visiting:
            raise ValueError('Dependency cycle')
        if key in visited:
            return
        visiting.add(key)
        for dep in by_key[key]['deps']:
            visit(dep)
        visiting.remove(key)
        visited.add(key)
        order.append(key)

    for key in by_key:
        visit(key)
    return order


def main():
    pbis = json.loads(PBIS.read_text(encoding='utf-8'))
    order = validate_pbis(pbis)
    print(f'PASS: {len(order)} PBIs; unique Issues, valid references, no dependency cycles')
    print('Dependency order: ' + ', '.join(order))
    print('Not evaluated: requirement agreement, Issue completion, implementation readiness')


if __name__ == '__main__':
    main()
