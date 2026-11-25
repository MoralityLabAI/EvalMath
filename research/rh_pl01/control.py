"""Exact finite Horn-proof controls for RH-PL-01. Standard library only."""
from fractions import Fraction
from itertools import combinations
import json


def instance(k):
    # Three sources per block, each covers two of its three elements.
    # Every inference (including an axiom) has unit cost.
    sources = [f's{b}_{i}' for b in range(k) for i in range(3)]
    elements = [f'e{b}_{i}' for b in range(k) for i in range(3)]
    cover = {e: tuple(sources[3*b+j] for j in range(3) if j != i)
             for b in range(k) for i, e in enumerate(elements[3*b:3*b+3])}
    rules = [((), s) for s in sources]
    rules += [((s,), e) for e in elements for s in cover[e]]
    rules += [(tuple(elements), 'g')]
    return sources, elements, cover, rules


def exact_cover(sources, elements, cover):
    for n in range(len(sources)+1):
        for chosen in combinations(sources, n):
            if all(set(chosen).intersection(cover[e]) for e in elements):
                return len(elements)+1+n, chosen
    raise AssertionError('unreachable')


def bfs(sources, elements, rules):
    idx = {a: 1 << i for i, a in enumerate(sources+elements+['g'])}
    compiled = [(sum(idx[a] for a in pre), idx[out]) for pre, out in rules]
    frontier, seen, depth = {0}, {0}, 0
    while frontier:
        if any(s & idx['g'] for s in frontier):
            return depth
        frontier = {s | out for s in frontier for pre, out in compiled
                    if s & pre == pre and not s & out} - seen
        seen |= frontier
        depth += 1
    raise AssertionError('unreachable')


def dual_certificate(elements, cover):
    cuts = [(frozenset({'g'}), Fraction(1))]
    for e in elements:
        cuts.append((frozenset({'g', e}), Fraction(1)))
        cuts.append((frozenset({'g', e, *cover[e]}), Fraction(1, 2)))
    return cuts


def check_dual(rules, cuts):
    assert all('g' in u and w >= 0 for u, w in cuts)
    loads = [sum((w for u, w in cuts if out in u and not u.intersection(pre)),
                 Fraction(0)) for pre, out in rules]
    assert all(load <= 1 for load in loads)
    return sum((w for _, w in cuts), Fraction(0))


def check_fractional_upper(sources, elements, rules):
    # Feasible fractional cover of ALL cuts (enumerated for small k).
    # This upper-bounds the optimum of the cut-packing relaxation.
    nodes = sources+elements
    idx = {a: 1 << i for i, a in enumerate(nodes+['g'])}
    compiled = [(sum(idx[a] for a in pre), idx[out], 2 if out == 'g' else 1)
                for pre, out in rules]
    for mask in range(1 << len(nodes)):
        u = mask | idx['g']
        assert sum(w for pre, out, w in compiled if u & out and not u & pre) >= 2
    return Fraction(sum(w for _, _, w in compiled), 2)


def main():
    receipt = []
    for k in range(1, 5):
        sources, elements, cover, rules = instance(k)
        exact, chosen = exact_cover(sources, elements, cover)
        lower = check_dual(rules, dual_certificate(elements, cover))
        independent = bfs(sources, elements, rules) if k <= 2 else None
        fractional = check_fractional_upper(sources, elements, rules) if k <= 2 else None
        assert exact == 5*k+1 and lower == Fraction(9*k, 2)+1
        assert independent is None or independent == exact
        assert fractional is None or fractional == lower
        receipt.append({'blocks': k, 'exact': exact, 'dual': str(lower),
                        'ceil_dual': -(-lower.numerator//lower.denominator),
                        'bfs': independent, 'all_cuts_fractional': str(fractional) if fractional is not None else None,
                        'witness_sources': chosen})
    # Reject an overweight certificate.
    _, elements, cover, rules = instance(1)
    try:
        check_dual(rules, [(frozenset({'g'}), Fraction(2))])
    except AssertionError:
        pass
    else:
        raise AssertionError('accepted overweight certificate')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
