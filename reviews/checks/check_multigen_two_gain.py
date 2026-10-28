"""Independent re-derivation of multigen §6: the two-gain counterexample to Prop 10's hypothesis (A),
and a stress test of Prop 10 itself on random abstract chains.

Written from the note's definitions only; nothing is imported from spiral_ln.

Chain (drift chain, multigen §6): state (c, i); each generation draws K candidates i.i.d.; each
candidate draws a gain mu from the gain law, then a count ~ Bin(n, p(min(top, i+mu))). M = max count.
The accepted candidate's gain has posterior q_mu Bin(n, p(i+mu))(M) / mix(M). Rule t accepts iff
M > c + t(c) (t may depend on the level); on acceptance the state becomes (M, min(top, i+mu)).

Run:  python reviews/checks/check_multigen_two_gain.py
"""
from __future__ import annotations

import itertools
import random
import sys
from fractions import Fraction as Fr
from math import comb


def binom_pmf(n, p):
    return [comb(n, j) * p**j * (1 - p) ** (n - j) for j in range(n + 1)]


def best_of_k_joint(n, K, levels, i, gains):
    """Law of (M, gain of the kept candidate) from level i. gains: dict mu -> prob."""
    top = len(levels) - 1
    per = {}
    for mu, q in gains.items():
        pm = binom_pmf(n, levels[min(top, i + mu)])
        for j in range(n + 1):
            per[(j, mu)] = per.get((j, mu), 0) + q * pm[j]
    mix = [sum(per.get((j, mu), 0) for mu in gains) for j in range(n + 1)]
    F = [sum(mix[: j + 1]) for j in range(n + 1)]
    law = {}
    for j in range(n + 1):
        pM = F[j] ** K - (F[j - 1] ** K if j > 0 else 0)
        if pM == 0:
            continue
        for mu in gains:
            w = per.get((j, mu), 0)
            if w:
                law[(j, mu)] = pM * w / mix[j]
    return law


def step(dist, n, K, levels, gains, rule):
    """One generation; rule(c, i) -> threshold t (integer >= 0)."""
    top = len(levels) - 1
    out = {}
    cache = {}
    for (c, i), mass in dist.items():
        if mass == 0:
            continue
        if i not in cache:
            cache[i] = best_of_k_joint(n, K, levels, i, gains)
        t = rule(c, i)
        stay = mass
        for (j, mu), pr in cache[i].items():
            if j > c + t:
                st = (j, min(top, i + mu))
                out[st] = out.get(st, 0) + mass * pr
                stay -= mass * pr
        out[(c, i)] = out.get((c, i), 0) + stay
    return out


def run(n, K, levels, gains, rule, horizon, start=(0, 0)):
    dist = {start: Fr(1)}
    hist = [dist]
    for _ in range(horizon):
        dist = step(dist, n, K, levels, gains, rule)
        hist.append(dist)
    return hist


def stats(dist, n, levels):
    pc = sum(m for (c, i), m in dist.items() if c == n)
    ec = sum(c * m for (c, i), m in dist.items())
    ep = sum(levels[i] * m for (c, i), m in dist.items())
    return pc, ec, ep


def limit_level(n, K, levels, gains, rule, start=(0, 0)):
    """Exact limiting E[p(i_inf)] by solving the absorbing chain: states where nothing can be accepted
    are absorbing; otherwise solve linear equations for the expected absorbed level value."""
    top = len(levels) - 1
    states = [(c, i) for c in range(n + 1) for i in range(top + 1)]
    kernels = {}
    for (c, i) in states:
        law = best_of_k_joint(n, K, levels, i, gains)
        t = rule(c, i)
        moves = {}
        for (j, mu), pr in law.items():
            if j > c + t:
                st = (j, min(top, i + mu))
                moves[st] = moves.get(st, 0) + pr
        kernels[(c, i)] = moves
    # value v(s) = E[level value at absorption]; absorbing iff moves empty
    # v(s) = (sum_{s'} P(s->s') v(s')) / (1 - P(stay)) for transient s; transitions are upward in c
    # strictly or level-raising, so solve by reverse order on (c, i) with a fixpoint on self-loops.
    order = sorted(states, key=lambda s: (-s[0], -s[1]))
    v = {}
    for s in order:
        moves = kernels[s]
        if not moves:
            v[s] = Fr(levels[s[1]])
            continue
        stay = 1 - sum(moves.values())
        # all moves go to states with larger c (j > c), hence already solved
        v[s] = sum(pr * v[s2] for s2, pr in moves.items()) / (1 - stay)
    return v[start]


def naive(c, i):
    return 0


def main():
    print("== two-gain counterexample (multigen §6): n=3, K=1, levels (0,1/4,1/4,3/4), gains {0,1,3} w.p. (3/5,1/5,1/5)")
    n, K = 3, 1
    levels = [Fr(0), Fr(1, 4), Fr(1, 4), Fr(3, 4)]
    gains = {0: Fr(3, 5), 1: Fr(1, 5), 3: Fr(1, 5)}
    gate = lambda c, i: 1 if c == 0 else 0  # t = (1,0,0,0)
    H = 80
    hn = run(n, K, levels, gains, naive, H)
    hg = run(n, K, levels, gains, gate, H)
    ahead_pc = [k for k in range(H + 1) if stats(hg[k], n, levels)[0] > stats(hn[k], n, levels)[0]]
    ahead_ec = [k for k in range(H + 1) if stats(hg[k], n, levels)[1] > stats(hn[k], n, levels)[1]]
    ahead_ep = [k for k in range(H + 1) if stats(hg[k], n, levels)[2] > stats(hn[k], n, levels)[2]]
    print("gate ahead in P(c=3) at k =", ahead_pc[:3], "...", ahead_pc[-3:], "count", len(ahead_pc))
    print("gate ahead in E[c]   at k =", ahead_ec[:3], "...", ahead_ec[-3:], "count", len(ahead_ec))
    print("gate ahead in E[p]   at k =", ahead_ep[:3], "...", ahead_ep[-3:], "count", len(ahead_ep))
    k = 34
    pg, pn = stats(hg[k], n, levels)[0], stats(hn[k], n, levels)[0]
    print(f"k=34: P(c=3) gate {float(pg):.5f} naive {float(pn):.5f}")
    lg = limit_level(n, K, levels, gains, gate)
    ln_ = limit_level(n, K, levels, gains, naive)
    print("limit E[p]: gate", lg, "=", float(lg), " naive", ln_, "=", float(ln_))
    claims = {
        "P(c=3) ahead exactly at k=28..80": ahead_pc == list(range(28, 81)),
        "E[c] ahead exactly at k=39..80": ahead_ec == list(range(39, 81)),
        "E[p] ahead exactly at k=19..80": ahead_ep == list(range(19, 81)),
        "limit gate = 2909/3968": lg == Fr(2909, 3968),
        "limit naive = 8058689/11073200": ln_ == Fr(8058689, 11073200),
        "k=34 values 0.99090 / 0.99045": (round(float(pg), 5), round(float(pn), 5)) == (0.99090, 0.99045),
    }
    for kcl, v in claims.items():
        print(f"  [{'OK' if v else 'FAIL'}] {kcl}")

    print("\n== second witness: n=4, levels (0,1/4,3/4), gains {0,1,2} w.p. (3/7,1/7,3/7), same rule")
    n, K = 4, 1
    levels = [Fr(0), Fr(1, 4), Fr(3, 4)]
    gains = {0: Fr(3, 7), 1: Fr(1, 7), 2: Fr(3, 7)}
    hn = run(n, K, levels, gains, naive, H)
    hg = run(n, K, levels, gains, gate, H)
    ahead_pc = [k for k in range(H + 1) if stats(hg[k], n, levels)[0] > stats(hn[k], n, levels)[0]]
    ahead_ec = [k for k in range(H + 1) if stats(hg[k], n, levels)[1] > stats(hn[k], n, levels)[1]]
    ahead_ep = [k for k in range(H + 1) if stats(hg[k], n, levels)[2] > stats(hn[k], n, levels)[2]]
    print("ahead P(c=4):", (ahead_pc[0], ahead_pc[-1], len(ahead_pc)) if ahead_pc else None)
    print("ahead E[c]  :", (ahead_ec[0], ahead_ec[-1], len(ahead_ec)) if ahead_ec else None)
    print("ahead E[p]  :", (ahead_ep[0], ahead_ep[-1], len(ahead_ep)) if ahead_ep else None)
    print("  [%s] note: P(c=4), E[c] ahead at k=31..80; E[p] at k=15..80" % (
        "OK" if ahead_pc == list(range(31, 81)) and ahead_ec == list(range(31, 81)) and ahead_ep == list(range(15, 81)) else "FAIL"))

    print("\n== hand witness: n=3, K=1, levels (0,1/2,1), gains {0,1,2} w.p. (2/3,1/6,1/6), t(0)=2")
    levels = [Fr(0), Fr(1, 2), Fr(1)]
    gains = {0: Fr(2, 3), 1: Fr(1, 6), 2: Fr(1, 6)}
    gate2 = lambda c, i: 2 if c == 0 else 0
    lg = limit_level(3, 1, levels, gains, gate2)
    ln_ = limit_level(3, 1, levels, gains, naive)
    print("limit E[p]: gate", lg, "naive", ln_, " [%s] note: 17/18 vs 139/150" % ("OK" if (lg, ln_) == (Fr(17, 18), Fr(139, 150)) else "FAIL"))

    # ---- Stress test of Proposition 10 on random ABSTRACT chains (not binomial).
    # Hypotheses: (A) from level i the best candidate is (J, i') with i' in {i, i+}, law pi_i free of c;
    # (B) for the count statement, H_m(i) = pi_i(J >= m) non-decreasing in i for every m.
    # Statement: for every threshold rule (level-dependent allowed), state, horizon, nondecreasing psi/phi:
    #   E^t[psi(c_g)] <= E^0[psi(c_g)]  (needs A+B),  E^t[phi(i_g)] <= E^0[phi(i_g)]  (needs A only).
    print("\n== Prop 10 stress test on random abstract chains satisfying (A) (and (B) for counts)")
    rng = random.Random(20261026)

    def abstract_step(dist, n, top, laws, rule):
        out = {}
        for (c, i), mass in dist.items():
            if mass == 0:
                continue
            t = rule(c, i)
            stay = mass
            for (j, ip), pr in laws[i].items():
                if j > c + t:
                    out[(j, ip)] = out.get((j, ip), 0) + mass * pr
                    stay -= mass * pr
            out[(c, i)] = out.get((c, i), 0) + stay
        return out

    def random_laws(n, top, force_B):
        laws = []
        for i in range(top + 1):
            ip = min(top, i + 1)
            # random masses on (j, i) and (j, ip)
            w = {}
            for j in range(n + 1):
                for lev in {i, ip}:
                    w[(j, lev)] = Fr(rng.randint(0, 6))
            tot = sum(w.values())
            if tot == 0:
                w[(0, i)] = Fr(1); tot = Fr(1)
            laws.append({k: v / tot for k, v in w.items() if v})
        if force_B:
            # enforce H_m(i) nondecreasing by replacing the count marginal with a sorted
            # family of CDFs: take a random "base" per level then make tails monotone via max.
            tails = []
            for i in range(top + 1):
                tails.append([sum(pr for (j, ip), pr in laws[i].items() if j >= m) for m in range(n + 2)])
            # mono-ize: tail_i(m) := max_{i' <= i} tail_{i'}(m); rebuild count marginal, keep gain split
            for i in range(top + 1):
                mono = [max(tails[i2][m] for i2 in range(i + 1)) for m in range(n + 2)]
                # pmf from monotone tail; ensure valid (mono is nonincreasing in m automatically since each tail is)
                pmf = [mono[m] - mono[m + 1] for m in range(n + 1)]
                ip = min(top, i + 1)
                gainshare = {}
                for j in range(n + 1):
                    a = laws[i].get((j, i), Fr(0)); b = laws[i].get((j, ip), Fr(0))
                    gainshare[j] = (a / (a + b)) if (a + b) else Fr(1, 2)
                new = {}
                for j in range(n + 1):
                    if pmf[j]:
                        if ip == i:
                            new[(j, i)] = pmf[j]
                        else:
                            if gainshare[j]: new[(j, i)] = pmf[j] * gainshare[j]
                            if 1 - gainshare[j]: new[(j, ip)] = pmf[j] * (1 - gainshare[j])
                laws[i] = new
                tails[i] = mono
        return laws

    def check_B(laws, n, top):
        for m in range(n + 1):
            prev = None
            for i in range(top + 1):
                h = sum(pr for (j, ip), pr in laws[i].items() if j >= m)
                if prev is not None and h < prev:
                    return False
                prev = h
        return True

    violations = {"count": 0, "level": 0}
    cells = 0
    rules_checked = 0
    for trial in range(400):
        n = rng.randint(1, 4)
        top = rng.randint(1, 3)
        force_B = rng.random() < 0.7
        laws = random_laws(n, top, force_B)
        hasB = check_B(laws, n, top)
        cells += 1
        horizon = 6
        # enumerate all level-dependent threshold rules t(c,i) in {0..n} for c<n (c=n is absorbing anyway)
        keys = [(c, i) for c in range(n) for i in range(top + 1)]
        choices = [range(0, n - c + 1) for (c, i) in keys]  # t(c) > n-c-1 is "reject all"
        if n >= 3 and top >= 2:
            # too many rules: sample
            rule_iter = (dict(zip(keys, (rng.choice(list(ch)) for ch in choices))) for _ in range(60))
        else:
            rule_iter = (dict(zip(keys, combo)) for combo in itertools.product(*choices))
        naive_hist = None
        for start in [(0, 0), (rng.randint(0, n - 1), rng.randint(0, top))]:
            d0 = {start: Fr(1)}
            nh = [d0]
            d = d0
            for _ in range(horizon):
                d = abstract_step(d, n, top, laws, lambda c, i: 0)
                nh.append(d)
            for tr in rule_iter if start == (0, 0) else []:
                rules_checked += 1
                rule = lambda c, i, tr=tr: tr.get((c, i), 0)
                d = d0
                for g in range(1, horizon + 1):
                    d = abstract_step(d, n, top, laws, rule)
                    # compare all tail indicators
                    for m in range(1, n + 1):
                        if hasB and sum(ms for (c, i), ms in d.items() if c >= m) > sum(ms for (c, i), ms in nh[g].items() if c >= m):
                            violations["count"] += 1
                            print("COUNT VIOLATION", n, top, laws, tr, start, g, m)
                    for l in range(1, top + 1):
                        if sum(ms for (c, i), ms in d.items() if i >= l) > sum(ms for (c, i), ms in nh[g].items() if i >= l):
                            violations["level"] += 1
                            print("LEVEL VIOLATION", n, top, laws, tr, start, g, l)
    print(f"random abstract cells: {cells}; rule-cell pairs checked: {rules_checked}; horizon {horizon}")
    print("violations:", violations)
    print("  [%s] Prop 10 survives the abstract stress test" % ("OK" if not any(violations.values()) else "FAIL"))


if __name__ == "__main__":
    main()
