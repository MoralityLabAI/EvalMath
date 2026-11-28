"""AIRIS-04: hidden Markov driver, sufficient history and exact acquisition."""
from collections import defaultdict
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

# Model index = (noise regime, target); target bits are alpha,beta.
RATES = (F(0), F(1,4), F(1,2))
MODELS = tuple(product(range(3), range(4)))
PULSE = (0,1,0)
PASSIVE = (0,0,0)
SCHEDULES = (PULSE,) + tuple(a for a in product(range(2), repeat=3) if a != PULSE)
MODES = ("difference", "one_difference", "last")
ARMS = ("pulse_history", "pulse_one_difference", "pulse_last", "passive_history",
        "greedy_history", "optimal_history")
SCALE = 16


def parity(x):
    return x.bit_count() % 2


def design(a):
    a0,a1,a2 = a
    return ((a0 ^ a1) | (a0 << 1),
            (a1 ^ a2) | ((a0 ^ a1) << 1))


def observed(y, mode):
    if mode == "full":
        return tuple(y)
    if mode == "difference":
        return (y[0]^y[1], y[1]^y[2])
    if mode == "one_difference":
        return (y[0]^y[1],)
    if mode == "last":
        return (y[2],)
    raise ValueError("unknown readout")


def enumerate_channel(a, regime, target, mode):
    """Independent literal simulator: sum over unobserved initial bit/flips."""
    if a not in SCHEDULES or (regime,target) not in MODELS:
        raise ValueError("outside finite domain")
    alpha, beta = target&1, (target>>1)&1
    p = RATES[regime]
    result = defaultdict(F)
    for u0,f1,f2 in product(range(2), repeat=3):
        prob = F(1,2)*(p if f1 else 1-p)*(p if f2 else 1-p)
        u = (u0, u0^f1, u0^f1^f2)
        y = tuple((alpha*x) ^ (beta*prev) ^ n
                  for x,prev,n in zip(a,(0,*a[:2]),u))
        result[observed(y,mode)] += prob
    return {o:p for o,p in result.items() if p}


@lru_cache(None)
def channel(a, mode):
    """Integer likelihood rows, denominator SCALE, from the difference law."""
    if a not in SCHEDULES or mode not in MODES:
        raise ValueError("invalid probe")
    width = 2 if mode == "difference" else 1
    out = []
    r1,r2 = design(a)
    for o in product(range(2), repeat=width):
        row = []
        for regime,t in MODELS:
            p = RATES[regime]
            if mode == "last":
                prob = F(1,2)
            else:
                bits = (parity(t&r1),parity(t&r2))[:width]
                prob = F(1)
                for v,b in zip(o,bits):
                    prob *= 1-p if v==b else p
            n = prob*SCALE
            assert n.denominator==1
            row.append(int(n))
        out.append((o,tuple(row)))
    return tuple(out)


def prior(regime):
    if regime is not None and regime not in range(3):
        raise ValueError("unknown regime")
    return tuple(int(regime is None or r==regime) for r,t in MODELS)


def posterior(weights, likelihood):
    return tuple(w*l for w,l in zip(weights,likelihood))


def masses(weights):
    return tuple(sum(weights[i] for i in range(t,len(MODELS),4)) for t in range(4))


def map_mass(weights):
    return max(masses(weights))


def certified_mass(weights):
    return sum(weights) if sum(x>0 for x in masses(weights))==1 else 0


def branch_weights(weights,a,mode):
    return tuple(p for _,l in channel(a,mode) if any(p:=posterior(weights,l)))


@lru_cache(None)
def greedy_choice(weights):
    return max(SCHEDULES, key=lambda a: sum(map_mass(p)
                                           for p in branch_weights(weights,a,"difference")))


@lru_cache(None)
def optimal_value(weights,remaining):
    if not remaining:
        return map_mass(weights)
    return max(sum(optimal_value(p,remaining-1)
                   for p in branch_weights(weights,a,"difference")) for a in SCHEDULES)


@lru_cache(None)
def value(weights,remaining,arm,endpoint="map"):
    if endpoint not in ("map","certified") or arm not in ARMS or remaining<0:
        raise ValueError("invalid evaluation")
    if not remaining:
        return map_mass(weights) if endpoint=="map" else certified_mass(weights)
    if arm=="optimal_history":
        # Freeze MAP-optimal action selection for both endpoints.
        if endpoint=="map":
            return optimal_value(weights,remaining)
        a = max(SCHEDULES,key=lambda a:sum(optimal_value(p,remaining-1)
                                          for p in branch_weights(weights,a,"difference")))
        mode = "difference"
    elif arm=="greedy_history":
        a,mode = greedy_choice(weights),"difference"
    elif arm=="passive_history":
        a,mode = PASSIVE,"difference"
    else:
        a = PULSE
        mode = {"pulse_history":"difference","pulse_one_difference":"one_difference",
                "pulse_last":"last"}[arm]
    return sum(value(p,remaining-1,arm,endpoint) for p in branch_weights(weights,a,mode))


def score(regime,episodes,arm,endpoint="map"):
    w = prior(regime)
    return F(value(w,episodes,arm,endpoint),sum(w)*SCALE**episodes)


def receipt():
    return {
        "experiment":"AIRIS-04",
        "evidence":"exact finite synthetic development; no native or neural learning result",
        "model_count":len(MODELS),"regimes":[str(p) for p in RATES],
        "action_schedules":len(SCHEDULES),"episode_transition_cost":3,
        "hidden_driver":"unobserved; starts fair each episode; flips independently",
        "priors":"uniform target; known regime or uniform mixture of three regimes",
        "max_episodes":3,
        "scores":{
            f"{'unknown' if r is None else str(RATES[r])}:episodes{n}":{
                arm:{k:str(score(r,n,arm,k)) for k in ("map","certified")} for arm in ARMS}
            for r in (0,1,2,None) for n in range(4)},
        "channel_rows":{
            "".join(map(str,a)):{mode:[{"observation":o,"likelihood_numerators":l}
                                      for o,l in channel(a,mode)] for mode in MODES}
            for a in SCHEDULES},
        "likelihood_denominator":SCALE,"model_order":MODELS,
        "source_sha256":{name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                         for name in ("partial.py","test_partial.py","PARTIAL.md")}
    }


if __name__=="__main__":
    print(json.dumps(receipt(),sort_keys=True,indent=2))
