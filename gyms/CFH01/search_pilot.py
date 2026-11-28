"""CFH-01 public-development search policy pilot. Python 3.10+, NumPy.
Logical exact-discriminant queries, not latency or neural-mechanism evidence.
"""
import json
import math
import random
from fractions import Fraction
from statistics import NormalDist, mean, median
import numpy as np
from cfh01 import prime_power, gamma, disc, quadratic, boundary

BUDGETS = (3, 4, 8, 16, 32, 64)
DENOMS = (0, 512, 256, 128, 64, 32, 16)
POLICIES = ('full', 'uniform', 'bisection', 'static_prior', 'adaptive_prior', 'warm_bisection', 'guarded_prior', 'quadratic')
NORMAL = NormalDist()


def cases(qs):
    for q in qs:
        for k in DENOMS:
            m = q**4 + (q**4//k if k else 0)
            for aug in (False, True):
                yield (q, m, aug)


def features(case):
    q, m, aug = case
    x = 32/q
    e = 32*(m-q**4)/q**4
    return [1, x, x*x, x**3, math.log(q/32), e, e*x, float(aug)/q]


def fit(cases_):
    rows = [(c, boundary(*c)) for c in cases_]
    rows = [(c, t) for c, t in rows if t is not None]
    X = np.array([features(c) for c, _ in rows])
    y = np.array([t/c[0]**16 for c, t in rows])
    # Fixed ridge penalty. Do not tune on the evaluation parameter groups.
    w = np.linalg.solve(X.T@X + 1e-5*np.diag([0]+[1]*7), X.T@y)
    sigma = max(1e-4, float(np.sqrt(np.mean((X@w-y)**2))))
    return w, sigma, len(rows)


def cdf(x, mu, sigma):
    # Uniform mass ensures support over the entire feasible interval.
    z0, z1 = NORMAL.cdf((0-mu)/sigma), NORMAL.cdf((1-mu)/sigma)
    if z1-z0 < 1e-12:
        return x
    return 0.1*x + 0.9*(NORMAL.cdf((x-mu)/sigma)-z0)/(z1-z0)


def quantile(p, mu, sigma):
    lo, hi = 0., 1.
    for _ in range(53):
        mid = (lo+hi)/2
        if cdf(mid, mu, sigma) < p:
            lo = mid
        else:
            hi = mid
    return (lo+hi)/2


def vdc(n):
    a, b = 0., 1.
    while n:
        n, bit = divmod(n, 2)
        b /= 2
        a += b*bit
    return a


def integer_at(p, cap):
    a, b = p.as_integer_ratio()
    return a*cap//b


def exact_from_values(cap, mid, y0, ymid, ycap):
    a = (Fraction(ycap-y0, cap)-Fraction(ymid-y0, mid))/(cap-mid)
    b = Fraction(ymid-y0, mid)-a*mid
    assert a.denominator == b.denominator == 1
    a, b = int(a), int(b)
    assert max(b, 2*a*cap+b) < 0
    lo, hi = 0, cap
    while hi-lo > 1:
        t = (lo+hi)//2
        if (a*t+b)*t+y0 < 0:
            hi = t
        else:
            lo = t
    return hi


def run_case(case, w, sigma):
    q, m, aug = case
    cap = q**16
    a, b, c = quadratic(*case)
    assert max(b, 2*a*cap+b) < 0
    oracle = lambda x: (a*x+b)*x+c
    for x in (0, cap//2, cap):
        assert oracle(x) == disc(gamma(q, m, x, aug))
    target = boundary(*case)
    mu = float(np.dot(w, features(case)))
    results = []
    for policy in POLICIES:
        rng = random.Random(q*1000003+m*2+int(aug))
        queried = {}
        lo, hi = -1, cap+1
        def ask(x):
            nonlocal lo, hi
            assert 0 <= x <= cap and x not in queried
            y = oracle(x)
            queried[x] = y
            if y < 0:
                hi = min(hi, x)
            else:
                lo = max(lo, x)
            return y
        yc = ask(cap)
        y0 = None if yc >= 0 else ask(0)
        model_answer = None
        j = 0
        for budget in BUDGETS:
            if yc < 0 and y0 >= 0 and hi-lo > 1:
                while len(queried) < budget and hi-lo > 1 and policy != 'full':
                    j += 1
                    if policy == 'quadratic':
                        if model_answer is None:
                            mid = cap//2
                            ym = ask(mid)
                            model_answer = exact_from_values(cap, mid, y0, ym, yc)
                            assert model_answer == target
                        elif model_answer not in queried:
                            ask(model_answer)
                        elif model_answer-1 not in queried:
                            ask(model_answer-1)
                        else:
                            break
                        continue
                    if policy == 'uniform':
                        x = rng.randrange(1, cap)
                    elif policy == 'static_prior':
                        x = integer_at(quantile(vdc(j), mu, sigma), cap)
                    elif policy == 'bisection' or (policy == 'warm_bisection' and j > 1):
                        x = (lo+hi)//2
                    else:
                        p0 = cdf(lo/cap, mu, sigma)
                        p1 = cdf(hi/cap, mu, sigma)
                        x = integer_at(quantile((p0+p1)/2, mu, sigma), cap)
                        if not lo < x < hi or min(x-lo, hi-x)*1000 < hi-lo:
                            x = (lo+hi)//2
                        if policy == 'guarded_prior' and j > 1 and min(x-lo, hi-x)*4 < hi-lo:
                            x = (lo+hi)//2
                    if x in queried or not 0 < x < cap:
                        # Fixed policies skip duplicates without spending an oracle call.
                        if policy in ('uniform', 'static_prior'):
                            continue
                        raise AssertionError('invalid adaptive action')
                    ask(x)
            if target is None:
                assert yc >= 0
                gap = width = None
                exact = True
                direct = True
            else:
                candidate = model_answer if model_answer is not None else hi
                assert target <= candidate <= cap
                gap = Fraction(candidate-target, cap)
                width = Fraction(hi-lo, cap)
                direct = hi-lo == 1
                exact = direct or model_answer is not None
                if model_answer is not None:
                    width = Fraction(1, cap)  # implied by exact quadratic interpolation
            results.append(dict(policy=policy, budget=budget, calls=len(queried),
                                gap=None if gap is None else str(gap),
                                width=None if width is None else str(width),
                                exact=exact, direct=direct))
    return results


def main():
    qs = [q for q in range(17, 98) if prime_power(q)]
    train_q = [q for i, q in enumerate(qs) if i % 4 != 3]
    groups = {'interpolation': [q for i, q in enumerate(qs) if i % 4 == 3],
              'extrapolation': [q for q in range(101, 258) if prime_power(q)],
              'extra_development': [q for q in range(263, 510) if prime_power(q)]}
    w, sigma, n = fit(list(cases(train_q)))
    records = []
    for group, gqs in groups.items():
        for case in cases(gqs):
            for r in run_case(case, w, sigma):
                records.append(dict(group=group, q=case[0], m=case[1], aug=case[2], **r))
    summary = []
    for group in groups:
        for budget in BUDGETS:
            for policy in POLICIES:
                rows = [r for r in records if (r['group'],r['budget'],r['policy']) == (group,budget,policy)]
                feasible = [r for r in rows if r['gap'] is not None]
                gaps = [Fraction(r['gap']) for r in feasible]
                widths = [Fraction(r['width']) for r in feasible]
                summary.append(dict(group=group, budget=budget, policy=policy,
                                    cases=len(rows), feasible=len(feasible),
                                    mean_gap=float(mean(gaps)), median_gap=float(median(gaps)),
                                    mean_width=float(mean(widths)),
                                    within_1e_4=sum(g <= Fraction(1,10000) for g in gaps),
                                    exact=sum(r['exact'] for r in feasible),
                                    direct=sum(r['direct'] for r in feasible),
                                    mean_calls=mean(r['calls'] for r in feasible)))
    return dict(evidence='public development, one conjecture genealogy', train_q=train_q,
                groups=groups, positive_train_cases=n, weights=w.tolist(), residual_rms=sigma,
                summary=summary, records=records)


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
