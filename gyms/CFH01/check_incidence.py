"""Independent incidence-algebra replay of the CFH-01 flag oracle."""
from functools import cache
from math import comb
from cfh01 import audit, gamma


def incidence(q, m, b):
    @cache
    def gaussian(d, i):
        if not 0 <= i <= d:
            return 0
        if d == 0:
            return 1
        return gaussian(d-1, i-1) + q**i*gaussian(d-1, i)

    def add(p, f, length, weight):
        for i, c in enumerate(f):
            for j in range(length):
                p[i+j] += weight*c

    @cache
    def F(d, t):
        r = d+t
        if not r:
            return (1,)
        result = [0]*(r+1)
        for i in range(d+1):
            for j in range(t+1):
                c = r-i-j
                if c:
                    add(result, F(i, j), c+1,
                        (-1)**(c+1)*gaussian(d, i)*comb(t, j))
        return tuple(result)

    def trunc(d, t, r):
        H, A = [0]*r, [0]*(r+1)
        for i in range(min(d, r-1)+1):
            for j in range(min(t, r-1-i)+1):
                c = r-i-j
                w = (-1)**(c+1)*gaussian(d, i)*comb(t, j)
                add(H, F(i, j), c, w)
                add(A, F(i, j), c+1, w)
        return H, A

    H, A = trunc(8, m, 5)
    for i, (v, u, w) in enumerate(zip(trunc(4, 1, 4)[1], F(4, 0), F(3, 1))):
        delta = b*(v-u-gaussian(4, 3)*w)
        H[i] += delta
        A[i] += delta
        A[i+1] += delta
    return H, A


def expand(g, degree):
    return [sum(g[j]*comb(degree-2*j, k-j) for j in range(3)
                if j <= k <= degree-j) for k in range(degree+1)]


def check():
    worlds = {}
    for row in audit()['rows']:
        q, m = row['q'], row['m']
        bs = worlds.setdefault((q, m), {0, q**16//2, q**16})
        t = row['minimum_b']
        if t is not None:
            bs.update((t, max(0, t-1)))
    count = 0
    for (q, m), bs in worlds.items():
        for b in bs:
            H, A = incidence(q, m, b)
            assert H == expand(gamma(q, m, b), 4)
            assert A == expand(gamma(q, m, b, True), 5)
            count += 2
    return count


if __name__ == '__main__':
    print(f'{check()} exact polynomial comparisons passed')
