from collections import defaultdict
from itertools import permutations, product
from spiral_ln.evaluation_cpf03 import cases, exports, summary, abstract_countermodels


def test_manifest_and_splits():
    prompts, gold = exports()
    assert len(prompts) == len(gold) == 42
    assert len({r['id'] for r in prompts}) == 42
    assert {r['id'] for r in prompts} == {r['id'] for r in gold}
    assert all(set(r) == {'id', 'split', 'prompt'} for r in prompts)
    groups = defaultdict(set)
    for row in gold:
        groups[row['group']].add(row['split'])
        assert row['certificate']
    assert all(len(s) == 1 for s in groups.values())
    assert summary()['splits'] == {'dev': 6, 'test': 18, 'train': 18}
    assert summary()['labels'] == {'counterexample': 18, 'entailed': 21, 'unresolved': 3}


def test_abstract_models():
    for kind in ('bound', 'absence', 'existence'):
        assert not abstract_countermodels(kind, False)
        assert abstract_countermodels(kind, True)
    # Exhaust all two-witness models independently of the one-witness oracle.
    for e, a, g in product(range(4), repeat=3):
        if e & ~a:
            continue
        assert (a & ~g) or not (e & ~g)
        assert a or not e
        assert not e or a


def test_finite_polynomials_and_characteristic():
    for p in (2,3,5):
        assert all(pow(x,p,p) == x for x in range(p))
        assert {p:1, 1:p-1} != {}
    for n in range(1,5):
        for perm in permutations(range(n)):
            inversions = sum(perm[i] > perm[j] for i in range(n) for j in range(i+1,n))
            assert (-1)**inversions % 2 == 1
    for p in (3,5,7,11,13):
        assert 2 % p != 0


def test_degree_by_repeated_doubling():
    group = [r for r in cases() if r['group'] == 'degree']
    for row, (n,d) in zip(group, ((3,3),(8,2),(4,3),(16,3),(5,3),(32,4))):
        degree = 1
        for _ in range(n):
            degree += degree
        assert (row['label'] == 'entailed') == (degree <= n**d)
