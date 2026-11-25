"""CFH-13: cold-call targeted and vector coefficient algorithms.
No global coefficient/result caches. Memoization lives inside each acquisition.
"""
from functools import cache
from itertools import combinations
from math import comb
from statistics import median
from time import thread_time_ns


def adjacency(g, inv):
    n, edges = g
    full = (1 << n) - 1
    adj = [0] * n
    for i, j in edges:
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    if inv == 'clique':
        adj = [full ^ (1 << i) ^ a for i, a in enumerate(adj)]
    return n, full, adj


def targeted(g, inv, ks):
    """Return requested coefficients only, with shared per-call scalar DP."""
    n, full, adj = adjacency(g, inv)
    ks = tuple(ks)
    if any(not 0 <= k <= n for k in ks):
        raise ValueError('coefficient index')
    if inv in ('independence', 'clique', 'matching'):
        matching = inv == 'matching'
        @cache
        def count(s, k):
            if k == 0:
                return 1
            if k < 0 or s.bit_count() < k * (2 if matching else 1):
                return 0
            if not matching and k == 1:
                return s.bit_count()
            bit = s & -s
            v = bit.bit_length() - 1
            rest = s ^ bit
            total = count(rest, k)
            if matching:
                nbr = adj[v] & rest
                while nbr:
                    u = nbr & -nbr
                    nbr ^= u
                    total += count(rest ^ u, k-1)
            else:
                total += count(rest & ~adj[v], k-1)
            return total
        return tuple(count(full, k) for k in ks)
    if inv == 'domination':
        closed = [a | (1 << i) for i, a in enumerate(adj)]
        def count(k):
            total = 0
            for subset in combinations(closed, k):
                cover = 0
                for a in subset:
                    cover |= a
                    if cover == full:
                        total += 1
                        break
            return total + int(k == 0 and n == 0)
        return tuple(count(k) for k in ks)
    if inv == 'chromatic':
        # Proper partitions into j independent color classes. For high target
        # degree, only partitions with >= target blocks can contribute.
        @cache
        def independent(s):
            if not s:
                return True
            b = s & -s
            return not (adj[b.bit_length()-1] & (s ^ b)) and independent(s ^ b)
        @cache
        def parts(s, j):
            if not s:
                return int(j == 0)
            size = s.bit_count()
            if j <= 0 or j > size:
                return 0
            if j == size:
                return 1
            if j == 1:
                return int(independent(s))
            b = s & -s
            available = (s ^ b) & ~adj[b.bit_length()-1]
            u = available
            total = 0
            while True:
                if u.bit_count() <= size-j and independent(u):
                    total += parts(s ^ (b | u), j-1)
                if not u:
                    break
                u = (u-1) & available
            return total
        @cache
        def stir(j, k):
            if j == 0:
                return int(k == 0)
            if not 0 <= k <= j:
                return 0
            return stir(j-1, k-1) - (j-1)*stir(j-1,k)
        return tuple(sum(stir(j,k)*parts(full,j) for j in range(k,n+1)) for k in ks)
    raise ValueError(inv)


def vector(g, inv):
    """Strong full-polynomial baseline with invariant-specific shared work."""
    n, full, adj = adjacency(g, inv)
    if inv in ('independence', 'clique', 'matching'):
        matching = inv == 'matching'
        @cache
        def rec(s):
            if not s:
                return (1,)
            b = s & -s
            v = b.bit_length()-1
            rest = s ^ b
            a = list(rec(rest))
            children = []
            if matching:
                nbr = adj[v] & rest
                while nbr:
                    u = nbr & -nbr
                    nbr ^= u
                    children.append(rest ^ u)
            else:
                children.append(rest & ~adj[v])
            for child in children:
                p = rec(child)
                a.extend([0] * max(0, len(p)+1-len(a)))
                for i, val in enumerate(p):
                    a[i+1] += val
            return tuple(a)
        ans = rec(full)
        return ans + (0,) * (n+1-len(ans))
    if inv == 'domination':
        closed = [a | (1 << i) for i, a in enumerate(adj)]
        cover = [0] * (full+1)
        ans = [0] * (n+1)
        for s in range(1, full+1):
            b = s & -s
            cover[s] = cover[s ^ b] | closed[b.bit_length()-1]
            if cover[s] == full:
                ans[s.bit_count()] += 1
        ans[0] = int(n == 0)
        return tuple(ans)
    if inv == 'chromatic':
        independent = [True] + [False] * full
        for s in range(1, full+1):
            b = s & -s
            independent[s] = independent[s ^ b] and not (adj[b.bit_length()-1] & (s ^ b))
        @cache
        def parts(s):
            if not s:
                return (1,)
            b = s & -s
            available = (s ^ b) & ~adj[b.bit_length()-1]
            u = available
            a = [0] * (s.bit_count()+1)
            while True:
                if independent[u]:
                    for j, val in enumerate(parts(s ^ (u|b))):
                        a[j+1] += val
                if not u:
                    break
                u = (u-1) & available
            return tuple(a)
        result = [0] * (n+1)
        fall = [1]
        for k, c in enumerate(parts(full)):
            for j, v in enumerate(fall):
                result[j] += c*v
            nxt = [0] * (len(fall)+1)
            for j, v in enumerate(fall):
                nxt[j] -= k*v
                nxt[j+1] += v
            fall = nxt
        return tuple(result)
    raise ValueError(inv)


def timed(fn, args, expected, repeats=5, inner=3):
    """Median per-call thread CPU nanoseconds, no persistent result cache."""
    assert fn(*args) == expected
    samples = []
    for _ in range(repeats):
        t = thread_time_ns()
        for _ in range(inner):
            result = fn(*args)
        elapsed = thread_time_ns() - t
        assert result == expected
        samples.append((elapsed+inner-1)//inner)
    return int(median(samples)), samples
