"""Check complete CFH-15 outcome coverage and deterministic ledger accounting."""
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path


def read(path):
    p = Path(path)
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)


def check(receipt):
    grouped = defaultdict(list)
    for row in receipt['records']:
        grouped[row['deck'], row['cap'], row['arm']].append(row)
    for (_, cap, _), rows in grouped.items():
        assert len(rows) == 90
        assert {x['hidden'] for x in rows} == set(range(90))
        for x in rows:
            assert 0 <= x['used'] <= cap
            assert sum(x['ledger'].values()) == x['used']
            assert all(type(v) is int and v >= 0 for v in x['ledger'].values())
            assert 0 <= x['queries'] <= 2
            assert x['hit'] == (x['remaining'] == 1)
            if x['reason'] == 'setup_exhausted':
                assert x['queries'] == 0 and x['remaining'] == 90
    return len(grouped)


if __name__ == '__main__':
    print(sum(check(read(path)) for path in sys.argv[1:]), 'complete outcome groups passed')
