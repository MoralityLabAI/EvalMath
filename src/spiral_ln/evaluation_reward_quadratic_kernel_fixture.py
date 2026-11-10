"""RHT-18: parabolic proxy-policy switching on globally shared p,q kernels.

A two-step protected action uses a first Bernoulli(p) event. In a hidden
proxy-reference state, its second Bernoulli(p) event emits proxy reward
with expected score p**2 after averaging state mass. In the independent
protected-gold state, a Bernoulli(q) failure awards gold theta*p*(1-q).
A competing proxy-only action earns q and zero protected gold.

One p and one q are reused throughout the entire trajectory. An external
UGC variant identifies the gold state with a genuinely safe F2 K2,2
constraint outcome, while the other hidden world does not qualify.
"""
from __future__ import annotations

from fractions import Fraction as Q
from spiral_ln.evaluation_reward_two_kernel import TwoKernelEdge,TwoKernelGame
from spiral_ln.evaluation_reward_hacking_adaptive_feedback import one_hot_ugc_disclosure_game


def quadratic_parabola_goodhart_fixture(
    *,ugc_worlds:bool=False,extra_tangent_policy:bool=False,
    p_interval=(Q(0),Q(1)),q_interval=(Q(0),Q(1))
):
    """Proxy scores p² and q; protected expected gold theta*p*(1-q).

    The hidden prior is 50/50 over two worlds. World 0 supplies proxy
    p², world 1 supplies true gold. With UGC grounding, world 1 is the
    protected-safe reference and the gold reward is halved by the prior.

    Optional third candidate gets proxy (p²+q)/2 and true gold zero,
    becoming proxy-optimal only on the parabolic boundary q=p².
    """
    ugc=one_hot_ugc_disclosure_game(2) if ugc_worlds else None
    if ugc is not None and not (
        ugc.unsafe(0,0) and not ugc.unsafe(1,0)
    ):
        raise AssertionError("UGC gold reference worlds changed")
    actions=("protected_gold","inflated_proxy")
    if extra_tangent_policy:
        actions+=("parabolic_tie_only",)
    # 0,1 initial hidden worlds; 2 proxy p-success; 3 gold p-success;
    # 4 terminal; 5 optional mixed-policy proxy p-success.
    edges=[]
    def add(s,a,t,obs,b=0,dp=0,dq=0,proxy=0,gold=0):
        edges.append(TwoKernelEdge(
            s,a,t,obs,Q(b),Q(dp),Q(dq),Q(proxy),Q(0),(Q(gold),)
        ))
    for a in range(len(actions)):
        for world in (0,1):
            if a==0:
                add(world,a,2+world,"protected:first-pass",dp=1)
                add(world,a,4,"protected:first-fail",b=1,dp=-1)
            elif a==1:
                add(world,a,4,"proxy:paid",dq=1,proxy=1)
                add(world,a,4,"proxy:zero",b=1,dq=-1)
            elif world==0:
                add(world,a,5,"mixed:first-pass",dp=1)
                add(world,a,4,"mixed:first-fail",b=1,dp=-1)
            else:
                add(world,a,4,"mixed:q-paid",dq=1,proxy=1)
                add(world,a,4,"mixed:q-zero",b=1,dq=-1)
        add(2,a,4,"proxy:second-pass",dp=1,proxy=2)
        add(2,a,4,"proxy:second-fail",b=1,dp=-1)
        multiplier=1 if ugc_worlds else 2
        add(3,a,4,"protected:second-pass",b=1,dq=-1,gold=multiplier)
        add(3,a,4,"protected:second-fail",dq=1)
        add(4,a,4,"done",b=1)
        if extra_tangent_policy:
            add(5,a,4,"mixed:second-pass",dp=1,proxy=1)
            add(5,a,4,"mixed:second-fail",b=1,dp=-1)
    return TwoKernelGame(
        state_count=6 if extra_tangent_policy else 5,
        actions=actions,
        initial=(Q(1,2),Q(1,2))+(
            (Q(0),)*4 if extra_tangent_policy else (Q(0),)*3
        ),
        gold_parameters=("protected_gold_success",),
        p_interval=p_interval,q_interval=q_interval,
        edges=tuple(edges),horizon=2,
    )
