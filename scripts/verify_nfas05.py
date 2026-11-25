"""NFAS-05: exploratory independent-value stopping games; exact rational optimality checks."""
from fractions import Fraction as F
from itertools import product, permutations
from math import prod
from random import Random
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from scipy.optimize import linprog, milp, Bounds, LinearConstraint

ORDERS = tuple(permutations(range(3)))

def check(ok, label):
    if not ok:
        raise AssertionError(label)

def solve(sizes, worlds):
    # worlds are (observations, effective payoff vector, unnormalized integer mass).
    first = [(i, j) for i, n in enumerate(sizes) for j in range(n)]
    keys = first + [a + b for a in first for b in first if a[0] != b[0]]
    idx = {k: i for i, k in enumerate(keys)}
    n = len(keys)
    N = n + len(worlds)
    A, b = [], []
    for j, h in enumerate(keys):
        row = [0] * N; row[j] = 1
        if len(h) == 4:
            row[idx[h[:2]]] = 1
        A.append(row); b.append(1)
    for wi, (y, g, mass) in enumerate(worlds):
        for i, j, k in ORDERS:
            row = [0] * N; row[n + wi] = 1
            row[idx[i, y[i]]] = g[k] - g[i]
            row[idx[i, y[i], j, y[j]]] = g[k] - g[j]
            A.append(row); b.append(g[k])
    c = [0] * n + [m for _, _, m in worlds]
    A_np, b_np, c_np = np.array(A), np.array(b), -np.array(c)
    lp = linprog(c_np, A_ub=A_np, b_ub=b_np, bounds=(0, None), method="highs")
    check(lp.success, "LP discovery failed")
    # Reconstruct the basic dual using exact elimination on its numerical support.
    approx = -lp.ineqlin.marginals
    support = [i for i,v in enumerate(approx) if v > 1e-7]
    k = len(support)
    slack = A_np.T @ approx - np.array(c)
    rows = [[F(A[i][j]) for i in support]+[F(c[j])]
            for j in range(N) if abs(slack[j]) < 1e-6]
    pivots = []; r = 0
    for col in range(k):
        pivot = next((i for i in range(r,len(rows)) if rows[i][col]),None)
        if pivot is None: continue
        rows[r],rows[pivot] = rows[pivot],rows[r]
        v=rows[r][col]; rows[r]=[x/v for x in rows[r]]
        for i in range(r+1,len(rows)):
            if rows[i][col]:
                v=rows[i][col]; rows[i]=[x-v*y for x,y in zip(rows[i],rows[r])]
        pivots.append(col);r+=1
    check(r==k,"dual support not uniquely reconstructed")
    sol=[F(0)]*k
    for i,col in reversed(list(enumerate(pivots))):
        sol[col]=rows[i][-1]-sum(rows[i][j]*sol[j] for j in range(col+1,k) if rows[i][j])
    dual=[F(0)]*len(b)
    for i,q in zip(support,sol):dual[i]=q
    check(all(q >= 0 for q in dual), "dual sign")
    for j, goal in enumerate(c):
        check(sum((q * row[j] for q, row in zip(dual, A) if q and row[j]), F(0)) >= goal, "dual feasibility")
    upper = sum((q * rhs for q, rhs in zip(dual, b) if q and rhs), F(0))
    def score(policy):
        check(all(v in (0, 1) for v in policy), "policy integrality")
        for j, h in enumerate(keys):
            if len(h) == 4:
                check(policy[j] + policy[idx[h[:2]]] <= 1, "policy flow")
        total = 0
        for y, g, mass in worlds:
            vals = []
            for i, j, k in ORDERS:
                a = policy[idx[i, y[i]]]; z = policy[idx[i, y[i], j, y[j]]]
                vals.append(a*g[i] + z*g[j] + (1-a-z)*g[k])
            total += mass * min(vals)
        return total
    policy = [round(float(v)) for v in lp.x[:n]]
    # Rounded LP values may violate realization constraints; use MILP in that case.
    feasible = all(policy[j] + policy[idx[h[:2]]] <= 1 for j, h in enumerate(keys) if len(h) == 4)
    lower = score(policy) if feasible else None
    used_milp = lower != upper
    if used_milp:
        m = milp(c_np, integrality=[1]*n+[0]*len(worlds),
                 bounds=Bounds(np.zeros(N), np.r_[np.ones(n), [np.inf]*len(worlds)]),
                 constraints=LinearConstraint(A_np, -np.inf, b_np),
                 options={"time_limit": 15, "mip_rel_gap": 0})
        check(m.x is not None, "deterministic discovery failed")
        policy = [round(float(v)) for v in m.x[:n]]
        lower = score(policy)
    # Only this exact equality authorizes a no-gap claim. Floating solver status is insufficient.
    check(lower == upper, "unclosed exact certificate")
    mass = sum(w for _, _, w in worlds)
    offline = F(sum(m*max(g) for _, g, m in worlds), mass)
    return F(lower, mass), offline, used_milp

def observed(values, probs):
    sizes = tuple(map(len, values))
    worlds = [(y, tuple(values[i][j] for i,j in enumerate(y)), prod(probs[i][j] for i,j in enumerate(y)))
              for y in product(*(range(n) for n in sizes))]
    return solve(sizes, worlds)

def hidden(values, probs, eps, sensitivity, price):
    # Integer effective payoff = 4*verified utility + 4*price*expected detected failures.
    # Fixed payoff offset -4*price*E(total failures) does not affect the optimizer.
    states = tuple(product(range(2), repeat=3)); worlds=[]
    for x, y in product(states, repeat=2):
        h = sum(a != b for a,b in zip(x,y)); m=prod(probs[i][b] for i,b in enumerate(x))*eps**h*(4-eps)**(3-h)
        if m:
            g = tuple(4*v*(1-b)+price*sensitivity*b for v,b in zip(values,x))
            worlds.append((y,g,m))
    return solve((2,2,2), worlds)

def cases():
    binary=[(((0,1),(0,2),(0,4)),((1,1),)*3),(((1,3),(1,3),(1,3)),((1,1),)*3),(((1,4),(2,5),(3,6)),((1,1),)*3),(((1,5),(2,6),(3,7)),((1,1),)*3)]
    r=Random(33)
    for _ in range(120):
        v=tuple(tuple(sorted(r.sample(range(13),2))) for _ in range(3)); p=tuple(tuple(r.randint(1,3) for _ in range(2)) for _ in range(3)); binary.append((v,p))
    r=Random(601); ternary=[]
    for _ in range(60):
        v=tuple(tuple(sorted(r.sample(range(15),3))) for _ in range(3)); p=tuple(tuple(r.randint(1,3) for _ in range(3)) for _ in range(3)); ternary.append((v,p))
    r=Random(76); imperfect=[]
    for _ in range(100):
        v=tuple(r.randint(1,8) for _ in range(3)); p=tuple(tuple(r.randint(1,3) for _ in range(2)) for _ in range(3)); e=r.choice([1,2]); s=r.choice([1,2,3,4]); l=r.randint(1,9); imperfect.append((v,p,e,s,l))
    return (("observed_binary",observed,binary),("observed_ternary",observed,ternary),("hidden_imperfect_audit",hidden,imperfect))

def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path); args=p.parse_args()
    summary={}; all_results=[]
    for label, fn, grid in cases():
        records=[]; fallbacks=0
        for case in grid:
            value, offline, fallback=fn(*case); fallbacks+=fallback
            records.append({"instance":case,"value":str(value),"offline":str(offline)})
        raw=json.dumps(records,sort_keys=True,separators=(",",":")).encode()
        min_ratio=min(F(r["value"])/F(r["offline"]) for r in records if F(r["offline"])>0)
        summary[label]={"cases":len(records),"exact_no_gap_certificates":len(records),"minimum_effective_payoff_ratio":str(min_ratio),"values_sha256":hashlib.sha256(raw).hexdigest()}
        print(label,summary[label],"MILP discovery fallbacks",fallbacks)
        all_results.extend(records)
    result={"schema":"nfas-05-v1","source_sha256":{"scripts/verify_nfas05.py":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},"checks":{"all_exact_no_gap_certificates":True},"summary":summary}
    if args.output: args.output.write_text(json.dumps(result,indent=2)+"\n")
    else: print(json.dumps(result,indent=2))
if __name__=="__main__": main()
