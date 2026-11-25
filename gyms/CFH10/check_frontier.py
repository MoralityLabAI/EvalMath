"""Audit CFH-10 integer regret, budgets and finite price-frontier consistency."""
from collections import defaultdict
from pathlib import Path
import gzip
import json
import sys


def load(path):
    p = Path(path)
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)


def grouped(r):
    rows, decisions = defaultdict(list), defaultdict(list)
    for name, dest in [('records', rows), ('decisions', decisions)]:
        for x in r[name]:
            dest[x['deck'], x['cap'], x['price'], x['arm'], x.get('seed', 0)].append(x)
    return rows, decisions


def totals(rows, price, scale):
    hits = sum(x['hit'] for x in rows)
    cost = sum(x['cost'] for x in rows)
    return hits, cost, scale * hits - price * cost


def audit(primary, extra):
    scale = primary['scale']
    exact, _ = grouped(primary)
    count = 0
    for receipt in (primary, extra):
        rows, decisions = grouped(receipt)
        for (deck, cap, p, arm, seed), rr in rows.items():
            assert len(rr) == 90 and len({x['hidden'] for x in rr}) == 90
            assert all(x['cost'] <= cap and x['queries'] <= 2 for x in rr)
            assert all(x['hit'] == (x['remaining'] == 1) for x in rr)
            _, _, val = totals(rr, p, scale)
            _, _, opt = totals(exact[deck, cap, p, 'exact', 0], p, scale)
            regret = sum(d['regret'] for d in decisions[deck, cap, p, arm, seed])
            assert regret >= 0 and opt - val == regret
            count += 1
    prices = primary['prices']
    frontier_count = 0
    for deck, cap in sorted({(k[0], k[1]) for k in exact}):
        seq = [totals(exact[deck, cap, p, 'exact', 0], p, scale) for p in prices]
        for x, y in zip(seq, seq[1:]):
            assert all(a >= b for a, b in zip(x, y))
        for i in range(len(prices) - 2):
            v0, v1, v2 = (seq[j][2] for j in range(i, i + 3))
            p0, p1, p2 = prices[i:i + 3]
            assert (v1 - v0) * (p2 - p1) <= (v2 - v1) * (p1 - p0)
        frontier_count += 1
    assert all(x['prunes'] <= x['paid_candidates'] for x in extra['meta'])
    return count, frontier_count


if __name__ == '__main__':
    n, f = audit(load(sys.argv[1]), load(sys.argv[2]))
    print(n, 'integer regret and budget groups;', f, 'monotone convex price frontiers passed')
