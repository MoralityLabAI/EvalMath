"""VAD-09D: value of identifying the reliability mode versus learning the observation law (exact, H<=3).

Latent state s=(mode m, law l). Mode 0 = cues as the nominal channel, mode 1 = reversed cues; mode flips with
hazard eta each family. Law l=0 nominal strength, l=1 weak strength (cue probabilities moved halfway to 1/2);
the law never changes. Menu actions are VAD-09A policies plus two priced probes that spend utility c and
reveal the mode or the law while taking the safe cutoff-2 action. All values are exact Fractions.
"""
import argparse
import json
from collections import defaultdict
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path

import verify_vad_meta as m
import verify_vad_stopping as a

HERE = Path(__file__).resolve().parent
ETA = F(1, 20)
MENU = ("cut0", "cut2", "cut8", "cut24", "p0", "p50", "p100")
STATES = [(mo, lw) for lw in (0, 1) for mo in (0, 1)]  # index = 2*law + mode


def weak(ch):
    return tuple((c + F(1, 2)) / 2 for c in ch)


CHANNELS = {(0, 0): m.Q[0], (1, 0): m.Q[1], (0, 1): weak(m.Q[0]), (1, 1): weak(m.Q[1])}


def build(prior=m.W, probe_cost=F(1)):
    acts = {}
    for name in MENU:
        act = m.action(name)
        ds = [m.distribution(prior, CHANNELS[s], act) for s in STATES]
        r = tuple(sum(p * m.utility(rec) for rec, p in d.items()) for d in ds)
        groups = defaultdict(lambda: [F(0)] * 4)
        for i, d in enumerate(ds):
            for rec, p in d.items():
                groups[rec][i] += p
        cnt = defaultdict(int)
        for v in groups.values():
            cnt[tuple(v)] += 1
        # outcomes with identical likelihood vectors carry the same posterior update: merge them
        outs = tuple(tuple(x * c for x in vec) for vec, c in cnt.items())
        assert all(sum(o[i] for o in outs) == 1 for i in range(4))
        acts[name] = (r, outs)
    c = probe_cost
    safe = acts["cut2"][0]
    acts["probe_mode"] = (tuple(x - c for x in safe), tuple(tuple(F(1) if STATES[i][0] == v else F(0) for i in range(4)) for v in (0, 1)))
    acts["probe_law"] = (tuple(x - c for x in safe), tuple(tuple(F(1) if STATES[i][1] == v else F(0) for i in range(4)) for v in (0, 1)))
    return acts


def transition(belief, eta):
    """Mode flips with hazard eta; the law is static."""
    out = [F(0)] * 4
    for i, b in enumerate(belief):
        if not b:
            continue
        mo, lw = STATES[i]
        out[2 * lw + mo] += b * (1 - eta)
        out[2 * lw + 1 - mo] += b * eta
    return tuple(out)


class Planner:
    def __init__(self, acts, eta=ETA, names=None):
        self.acts = {k: v for k, v in acts.items() if names is None or k in names}
        self.eta = eta
        self.memo = {}
        self.qevals = 0

    def branches(self, belief, name):
        r, outs = self.acts[name]
        imm = sum(b * x for b, x in zip(belief, r))
        res = []
        for o in outs:
            z = sum(b * x for b, x in zip(belief, o))
            if z:
                post = tuple(b * x / z for b, x in zip(belief, o))
                res.append((z, transition(post, self.eta)))
        return imm, res

    def q(self, belief, name, h):
        self.qevals += 1
        imm, res = self.branches(belief, name)
        return imm + (sum(z * self.value(nb, h - 1) for z, nb in res) if h > 1 else 0)

    def value(self, belief, h):
        if h <= 0:
            return F(0)
        key = (belief, h)
        if key not in self.memo:
            self.memo[key] = max(self.q(belief, k, h) for k in self.acts)
        return self.memo[key]

    def choose(self, belief, h):
        best = max(self.acts, key=lambda k: (self.q(belief, k, h), -list(self.acts).index(k)))
        return best

    def run_policy(self, belief, H, chooser):
        """Exact expected utility of a policy given by chooser(belief, remaining)->action."""
        if H == 0:
            return F(0)
        name = chooser(belief, H)
        imm, res = self.branches(belief, name)
        return imm + sum(z * self.run_policy(nb, H - 1, chooser) for z, nb in res)


def prior_belief(p_rev, p_weak):
    return tuple((p_rev if mo else 1 - p_rev) * (p_weak if lw else 1 - p_weak) for mo, lw in STATES)


def evaluate_structure(acts, H, p_rev=F(1, 2), p_weak=F(1, 2), eta=ETA):
    b0 = transition(prior_belief(p_rev, p_weak), F(0))
    full = Planner(acts, eta)
    out = {}
    out["blind_fixed_action"] = max(full.run_policy(b0, H, lambda b, h, k=k: k) for k in acts if not k.startswith("probe"))
    out["fixed_safe_cutoff"] = max(full.run_policy(b0, H, lambda b, h, k=k: k) for k in MENU if k.startswith("cut"))
    greedy = lambda b, h: max(full.acts, key=lambda k: (full.q(b, k, 1), -list(full.acts).index(k)))
    out["myopic_filter_menu"] = full.run_policy(b0, H, greedy)
    nopr = Planner(acts, eta, names=MENU)
    out["myopic_no_probes"] = nopr.run_policy(b0, H, lambda b, h: max(nopr.acts, key=lambda k: (nopr.q(b, k, 1), -list(nopr.acts).index(k))))
    out["finite_horizon_no_probes"] = nopr.value(b0, H)
    out["finite_horizon_with_probes"] = full.value(b0, H)
    if H >= 3:
        out["receding_h2"] = full.run_policy(b0, H, lambda b, h: full.choose(b, min(2, h)))
    out["first_action_optimal"] = full.choose(b0, H)
    out["first_action_optimal_no_probes"] = nopr.choose(b0, H)
    out["qevals_optimal"] = full.qevals
    return out, full


def oracle_values(acts, H, p_rev, p_weak, eta):
    """Privileged information structures: expected sum over periods of the best action given known state parts."""
    pi = {s: (p_rev if s[0] else 1 - p_rev) * (p_weak if s[1] else 1 - p_weak) for s in STATES}
    cand = [k for k in acts if not k.startswith("probe")]
    best = lambda i: max(acts[k][0][i] for k in cand)
    # mode distribution at period t given prior and hazard (law independent of the mode chain)
    pm = [1 - p_rev, p_rev]
    total = {"both_known": F(0), "mode_known_law_unknown": F(0)}
    for t in range(H):
        pm_t = pm
        for mo in (0, 1):
            for lw in (0, 1):
                w = pm_t[mo] * (p_weak if lw else 1 - p_weak)
                total["both_known"] += w * best(2 * lw + mo)
            # mode known, law unknown: best single action against law mixture at known mode
            mix = max(sum((p_weak if lw else 1 - p_weak) * acts[k][0][2 * lw + mo] for lw in (0, 1)) for k in cand)
            total["mode_known_law_unknown"] += pm_t[mo] * mix
        pm = [pm[0] * (1 - eta) + pm[1] * eta, pm[1] * (1 - eta) + pm[0] * eta]
    return total


def laws_known_dynamic(acts, H, p_rev, eta):
    """Law known, mode unknown: exact two-state planning with the true law, averaged over the law prior."""
    res = {}
    for lw in (0, 1):
        sub = {k: (tuple(v[0][2 * lw + mo] for mo in (0, 1)) + (F(0), F(0)),
                   tuple(tuple(o[2 * lw + mo] for mo in (0, 1)) + (F(0), F(0)) for o in v[1])) for k, v in acts.items()}
        pl = Planner(sub, eta)
        # ensure belief indices >=2 carry no mass: build belief on states 0,1 only (STATES order is mode-fastest)
        b0 = (1 - p_rev, p_rev, F(0), F(0))
        # transition() acts on STATES indices; remap by treating law 0 block only
        res[lw] = pl.value(b0, H)
    return res


def run(H=3):
    acts = build()
    r = {"protocol": "VAD-09D", "evidence": "exact finite menu control; no learned model",
         "source_sha256": {n: sha256((HERE / n).read_bytes()).hexdigest() for n in ("verify_vad_voi.py",)}, "H": H, "eta": str(ETA)}
    base, planner = evaluate_structure(acts, H)
    r["nominal"] = {k: (str(v) if not isinstance(v, int) else v) for k, v in base.items()}
    r["nominal_float"] = {k: float(v) for k, v in base.items() if not isinstance(v, (str, int))}
    r["oracles"] = {k: str(v) for k, v in oracle_values(acts, H, F(1, 2), F(1, 2), ETA).items()}
    r["law_known_dynamic"] = {k: str(v) for k, v in laws_known_dynamic(acts, H, F(1, 2), ETA).items()}
    r["law_known_dynamic_average"] = str(sum(v for v in laws_known_dynamic(acts, H, F(1, 2), ETA).values()) / 2)
    return r


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--horizon", type=int, default=3)
    a_ = p.parse_args()
    res = run(a_.horizon)
    a_.out.write_text(json.dumps(res, indent=2, sort_keys=True) + "\n")
    print(json.dumps(res, indent=1))
