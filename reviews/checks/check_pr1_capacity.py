"""Independent audit of PR #1 (`paper/leak_capacity.md`): the capacity criterion, the uniform-prior
collision law, the sparse certificate, and the 193-support exhaustive check.  Brute force only; nothing
imported from spiral_ln.

Checks:
 1. 193 coordinate-surjective supports of the 2x2x2 grid.
 2. For three maps observed separately: rational kernel dimension > 0 in 99; a 0/1 record collision at
    unit capacity in 91 (brute force over all 2^|P| x 2^|P| pairs of 0/1 cell vectors); the other 8
    collide at uniform capacity 2 (brute force over 3^|P| count vectors).
 3. Five-cell witness: unit capacity ratio 1; sizes (1,2,1,1,1): joint collision 3/128, separate 49/2048,
    ratio 49/48, by direct enumeration of all 4^6 ordered record pairs.
 4. Proposition 3: for every support with positive kernel, the RREF-style certificate obeys
    ||z||_inf <= max |r x r minor| <= r^{r/2}; and how far max|z| is from the true minimal
    sup-norm of a nonzero integer kernel vector (shortest vector by brute force in a box).
 5. Collision law (Theorem 2) against direct record enumeration on random supports with random sizes.

Run:  python reviews/checks/check_pr1_capacity.py
"""
from __future__ import annotations

import itertools
import random
from fractions import Fraction
from math import comb, gcd, prod


def margin_rows(cells, faces):
    cl = sorted(cells)
    rows = []
    for S in faces:
        groups = sorted({tuple(c[j] for j in S) for c in cl})
        for g in groups:
            rows.append([1 if tuple(c[j] for j in S) == g else 0 for c in cl])
    return cl, rows


def rref_kernel(rows, ncol):
    M = [[Fraction(v) for v in r] for r in rows]
    pivots = []
    r = 0
    for c in range(ncol):
        piv = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        M[r] = [v / M[r][c] for v in M[r]]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        pivots.append(c)
        r += 1
        if r == len(M):
            break
    free = [c for c in range(ncol) if c not in pivots]
    basis = []
    for f in free:
        v = [Fraction(0)] * ncol
        v[f] = Fraction(1)
        for i, pc in enumerate(pivots):
            v[pc] = -M[i][f]
        basis.append(v)
    return basis, len(pivots)


def primitive(v):
    den = 1
    for x in v:
        den = den * x.denominator // gcd(den, x.denominator)
    ints = [int(x * den) for x in v]
    g = 0
    for x in ints:
        g = gcd(g, abs(x))
    return [x // g for x in ints]


def in_kernel(rows, z):
    return all(sum(a * b for a, b in zip(r, z)) == 0 for r in rows)


def unit_collision(rows, ncell):
    """Does some pair of distinct 0/1 cell vectors share margins?"""
    seen = {}
    for x in itertools.product((0, 1), repeat=ncell):
        m = tuple(sum(a * b for a, b in zip(r, x)) for r in rows)
        if m in seen:
            return True
        seen[m] = x
    return False


def capacity_collision(rows, sizes):
    seen = {}
    for x in itertools.product(*(range(s + 1) for s in sizes)):
        m = tuple(sum(a * b for a, b in zip(r, x)) for r in rows)
        if m in seen:
            return True
        seen[m] = x
    return False


def min_sup_norm_kernel(rows, ncell, box=4):
    best = None
    for z in itertools.product(range(-box, box + 1), repeat=ncell):
        if any(z) and in_kernel(rows, z):
            s = max(abs(v) for v in z)
            if best is None or s < best:
                best = s
    return best


def max_minor(rows, r):
    """max |det| over r x r submatrices (brute force; small)."""
    best = 0
    nrow, ncol = len(rows), len(rows[0])
    for ri in itertools.combinations(range(nrow), r):
        for ci in itertools.combinations(range(ncol), r):
            sub = [[Fraction(rows[i][j]) for j in ci] for i in ri]
            # determinant by elimination
            d = Fraction(1)
            M = [row[:] for row in sub]
            for c in range(r):
                piv = next((i for i in range(c, r) if M[i][c] != 0), None)
                if piv is None:
                    d = Fraction(0)
                    break
                if piv != c:
                    M[c], M[piv] = M[piv], M[c]
                    d = -d
                d *= M[c][c]
                for i in range(c + 1, r):
                    f = M[i][c] / M[c][c]
                    M[i] = [a - f * b for a, b in zip(M[i], M[c])]
            best = max(best, abs(d))
    return best


def record_collisions(cells, faces, sizes):
    """Direct: items are independent fair bits; return (P[X=X'], P[MX=MX']) exactly."""
    cl, rows = margin_rows(cells, faces)
    # weight of a count vector = prod C(s_c, x_c); P[X=X'] = sum w^2 / 4^S ; margins grouped
    S = sum(sizes)
    joint = 0
    groups = {}
    for x in itertools.product(*(range(s + 1) for s in sizes)):
        w = prod(comb(s, v) for s, v in zip(sizes, x))
        joint += w * w
        m = tuple(sum(a * b for a, b in zip(r, x)) for r in rows)
        groups[m] = groups.get(m, 0) + w
    obs = sum(g * g for g in groups.values())
    return Fraction(joint, 4**S), Fraction(obs, 4**S)


def lattice_sum(cells, faces, sizes):
    """Theorem 2's kernel-lattice sum, brute force over the box."""
    cl, rows = margin_rows(cells, faces)
    S = sum(sizes)
    tot = 0
    for z in itertools.product(*(range(-s, s + 1) for s in sizes)):
        if in_kernel(rows, z):
            tot += prod(comb(2 * s, s + v) for s, v in zip(sizes, z))
    return Fraction(tot, 4**S)


def main():
    sep = [(0,), (1,), (2,)]
    grid = list(itertools.product(range(2), repeat=3))
    supports = [s for r in range(1, 9) for s in itertools.combinations(grid, r)
                if all({c[j] for c in s} == {0, 1} for j in range(3))]
    print(f"coordinate-surjective supports of 2x2x2: {len(supports)}  [{'OK' if len(supports) == 193 else 'FAIL'}]")
    pos = strict = silent = 0
    silent_cap2 = 0
    prop3_ok = 0
    prop3_cases = 0
    loose = []
    for s in supports:
        cells = {c: None for c in s}
        cl, rows = margin_rows(cells, sep)
        basis, r = rref_kernel(rows, len(cl))
        if not basis:
            continue
        pos += 1
        if unit_collision(rows, len(cl)):
            strict += 1
        else:
            silent += 1
            if capacity_collision(rows, (2,) * len(cl)):
                silent_cap2 += 1
        # Proposition 3 on the RREF certificate (first free coordinate)
        z = primitive(basis[0])
        mm = max_minor(rows, r)
        bound = Fraction(r) ** Fraction(r, 2) if r else 1
        hadamard_ok = max(abs(v) for v in z) <= mm <= r ** (r / 2) + 1e-9
        support_ok = sum(1 for v in z if v) <= r + 1
        prop3_cases += 1
        prop3_ok += hadamard_ok and support_ok and in_kernel(rows, z)
        truth = min_sup_norm_kernel(rows, len(cl))
        loose.append((max(abs(v) for v in z), truth, int(mm)))
    print(f"separate observation: positive rational kernel {pos} (PR: 99); unit-capacity collisions {strict} (PR: 91); silent {silent} (PR: 8); silent ones colliding at capacity 2: {silent_cap2} (PR: 8)")
    print(f"  [{'OK' if (pos, strict, silent, silent_cap2) == (99, 91, 8, 8) else 'FAIL'}] counts reproduce")
    print(f"Proposition 3 on {prop3_cases} certificates: ||z||_inf <= max minor <= r^(r/2), support <= r+1, in kernel: {prop3_ok} hold  [{'OK' if prop3_ok == prop3_cases else 'FAIL'}]")
    worst = max(loose, key=lambda t: t[0] - t[1])
    print(f"  certificate sup-norm vs true minimal sup-norm of a nonzero integer kernel vector: distribution of (cert, min, maxminor): {sorted(set(loose))}")
    print(f"  the RREF certificate equals the true minimum in {sum(1 for a, b, _ in loose if a == b)} of {len(loose)} supports")

    print("\nFive-cell witness (000),(001),(011),(101),(110):")
    five = {(0, 0, 0): None, (0, 0, 1): None, (0, 1, 1): None, (1, 0, 1): None, (1, 1, 0): None}
    j1, o1 = record_collisions(five, sep, (1, 1, 1, 1, 1))
    j2, o2 = record_collisions(five, sep, (1, 2, 1, 1, 1))
    print(f"  unit: joint {j1}, separate {o1}, ratio {o1/j1}   [{'OK' if o1 == j1 else 'FAIL'}] ratio 1")
    print(f"  (1,2,1,1,1): joint {j2}, separate {o2}, ratio {o2/j2}   [{'OK' if (j2, o2, o2/j2) == (Fraction(3,128), Fraction(49,2048), Fraction(49,48)) else 'FAIL'}] 3/128, 49/2048, 49/48")
    print(f"  Theorem 2 lattice sum at (1,2,1,1,1): {lattice_sum(five, sep, (1,2,1,1,1))}  [{'OK' if lattice_sum(five, sep, (1,2,1,1,1)) == o2 else 'FAIL'}]")

    print("\nTheorem 2 (collision law) vs direct enumeration on random supports/sizes/patterns:")
    rng = random.Random(2026)
    bad = 0
    trials = 0
    patterns = [sep, [(0, 1), (2,)], [(0, 2), (1,)], [(1, 2), (0,)], [(0, 1), (1, 2)], [(0, 1), (0, 2), (1, 2)]]
    while trials < 60:
        s = rng.choice(supports)
        if len(s) > 6:
            continue
        sizes = tuple(rng.randint(1, 3) for _ in s)
        if sum(sizes) > 10:
            continue
        faces = rng.choice(patterns)
        cells = {c: None for c in s}
        j, o = record_collisions(cells, faces, sizes)
        ls = lattice_sum(cells, faces, sizes)
        trials += 1
        if ls != o:
            bad += 1
    print(f"  {trials} random cases, mismatches {bad}  [{'OK' if bad == 0 else 'FAIL'}]")

    # Pair-joint/third-separate: positive kernel => unit collision (bipartite incidence)
    print("\nPair-joint + third separate: rational kernel > 0 implies a unit-capacity collision?")
    bad = 0
    tot = 0
    for s in supports:
        cells = {c: None for c in s}
        for j in range(3):
            faces = [tuple(i for i in range(3) if i != j), (j,)]
            cl, rows = margin_rows(cells, faces)
            basis, r = rref_kernel(rows, len(cl))
            tot += 1
            if basis and not unit_collision(rows, len(cl)):
                bad += 1
    print(f"  {tot} cases, violations {bad}  [{'OK' if bad == 0 else 'FAIL'}]")


if __name__ == "__main__":
    main()
