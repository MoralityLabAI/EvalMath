"""Independent audit of CFH-16 completed receipt, no rerun of the policy."""
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path


def check(r):
    groups = defaultdict(list)
    for x in r['records']:
        groups[x['deck'], x['cap'], x['arm']].append(x)
    for (_, cap, _), rows in groups.items():
        assert len(rows) == 90
        assert {x['hidden'] for x in rows} == set(range(90))
        for x in rows:
            assert 0 <= x['used'] <= cap
            assert sum(x['ledger'].values()) == x['used']
            assert all(type(v) is int and v >= 0 for v in x['ledger'].values())
            assert 0 <= x['queries'] <= 2
            assert x['hit'] == (x['remaining'] == 1)
    for d in r['decisions']:
        assert 0 <= d['retained'] <= d['new_cells']
        assert d['fuel'] >= 0
        if not d['committed'] and d['arm'] != 'checkpoint_retry':
            assert d['retained'] == 0
        if d['committed']:
            assert d['retained'] == d['new_cells']
    return len(groups), len(r['records']), len(r['decisions'])


if __name__ == '__main__':
    p = Path(sys.argv[1]); raw = p.read_bytes()
    r = json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)
    print(check(r), 'groups, outcomes, transactions checked')
