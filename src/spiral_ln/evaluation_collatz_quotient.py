"""Exact basin and quotient feedback oracle for the three-branch map."""
from collections import Counter, defaultdict, deque
from fractions import Fraction
from math import gcd, lcm


def step(n, d):
    if n % 2 == 0:
        return n // 2
    return 3*n+d if n % 4 == 1 else n+d


def odd_step(n, d):
    x = step(n, d)
    period = 1
    while x % 2 == 0:
        x //= 2
        period += 1
    return x, period


def atlas(d):
    """Return odd-region basin labels and exact full-step cycle periods."""
    if d < 1 or d % 4 != 1 or gcd(d, 6) != 1:
        raise ValueError('require positive d = 1 mod 4, coprime to 6')
    labels, periods = {}, {}
    for start in range(1, d+1, 2):
        path, pos = [], {}
        n = start
        while n not in labels and n not in pos:
            pos[n] = len(path)
            path.append(n)
            n, _ = odd_step(n, d)
            assert 1 <= n <= d and n % 2 == 1
        if n in labels:
            label = labels[n]
        else:
            cycle = path[pos[n]:]
            label = min(cycle)
            periods[label] = sum(odd_step(x, d)[1] for x in cycle)
        for x in path:
            labels[x] = label
    return labels, periods


def basin(n, d, labels):
    if n < 1:
        raise ValueError('positive input required')
    while n % 2 == 0:
        n //= 2
    while n > d:
        n, _ = odd_step(n, d)
    return labels[n]


def full_oracle(n, d):
    """Independent unaccelerated walk; cycle label and full period."""
    path, pos = [], {}
    while n not in pos:
        pos[n] = len(path)
        path.append(n)
        n = step(n, d)
    cycle = path[pos[n]:]
    return min(cycle), len(cycle)


def quotient(d):
    """Canonical label for each residue's orbit under multiplication by 2,3."""
    labels = {}
    for r in range(d):
        if r in labels:
            continue
        labels[r] = r
        todo = [r]
        while todo:
            x = todo.pop()
            for k in (2, 3):
                y = k*x % d
                if y not in labels:
                    labels[y] = r
                    todo.append(y)
                else:
                    assert labels[y] == r
    return labels


def feedback(d):
    """Exact Bayes ceiling on the declared uniform odd-lift population 1..2d-1."""
    labels, periods = atlas(d)
    q = quotient(d)
    counts = defaultdict(Counter)
    for n in range(1, 2*d, 2):
        counts[q[n % d]][basin(n, d, labels)] += 1
    return {
        'cycles': len(periods), 'quotient_classes': len(counts),
        'coprime_cycles': sum(gcd(c, d) == 1 for c in periods),
        'coprime_classes': sum(gcd(r, d) == 1 for r in counts),
        'collision_classes': sum(len(v) > 1 for v in counts.values()),
        'accuracy': str(Fraction(sum(max(v.values()) for v in counts.values()), d)),
        'coprime_accuracy': str(Fraction(sum(max(v.values()) for r,v in counts.items() if gcd(r,d)==1), sum(sum(v.values()) for r,v in counts.items() if gcd(r,d)==1))),
        'fibres': {str(r): dict(sorted(v.items())) for r,v in sorted(counts.items()) if len(v)>1},
    }


def order2(m):
    if m == 1:
        return 1
    x, k = 2 % m, 1
    while x != 1:
        x = 2*x % m
        k += 1
    return k


def inverse_a(n, d, k):
    # n -> 2**k*n - d is an inverse path using the n+d branch.
    assert k >= 2
    if (n << k) <= d:
        raise ValueError('exponent too small for positive predecessor')
    return (n << k)-d


def align(n, d, target):
    """Lift n backwards within its basin to the target residue mod d."""
    start = n % d
    inv3 = pow(3, -1, d) if d > 1 else 0
    prev = {start: None}
    todo = deque([start])
    while target not in prev and todo:
        x = todo.popleft()
        for op, y in ((2, 2*x % d), (3, inv3*x % d)):
            if y not in prev:
                prev[y] = (x, op)
                todo.append(y)
    if target not in prev:
        raise ValueError('target outside residue orbit')
    ops, x = [], target
    while prev[x] is not None:
        x, op = prev[x]
        ops.append(op)
    period = order2(d)
    def large(k, modulus):
        while k < 2 or (n << k) <= 3*d:
            k += modulus
        return k
    for op in reversed(ops):
        if op == 2:
            n = inverse_a(n, d, large(1, period))
        else:
            if n % 3 == 0:
                n = inverse_a(n, d, large(period, period))
            k = large(2 if n % 3 == d % 3 else 3, 2)
            n = ((n << k)-d)//3
            assert n % 4 == 1 and n > 0
            n = inverse_a(n, d, large((-k) % period, period))
    assert n % d == target
    return n


def collision(d, a, b, modulus):
    """Construct distinct-basin inputs congruent modulo any positive modulus.

    Intended for small moduli: witness bit lengths can grow rapidly.
    """
    if modulus < 1:
        raise ValueError('positive modulus required')
    labels, _ = atlas(d)
    q = quotient(d)
    assert basin(a, d, labels) != basin(b, d, labels)
    assert q[a % d] == q[b % d]
    x, y = a, align(b, d, a % d)
    m, e = modulus, 0
    while m % 2 == 0:
        m //= 2
        e += 1
    L = lcm(m, d)
    k = order2(L)
    while k < max(2, e) or (min(x,y) << k) <= d:
        k += order2(L)
    # First inverse-a step gives both odd inputs the same low e bits.
    x, y = inverse_a(x, d, k), inverse_a(y, d, k)
    # Translation by -d modulo L, align y to x.
    for _ in range(((y-x)//d) % (L//d)):
        y = inverse_a(y, d, k)
    assert x % modulus == y % modulus
    assert basin(x,d,labels) == basin(a,d,labels)
    assert basin(y,d,labels) == basin(b,d,labels)
    return x,y
