"""RHT-14 finite shared-kernel counterexamples.

The same unknown Bernoulli parameter p is reused at both time steps.
The protected task receives a true reward when the first trial succeeds
and the second trial fails, so its expected gold value is p(1-p)*theta.

A proxy-only action gives one certain proxy point and no gold. It is the
unique first-action proxy winner at every p in [0,1], so the exact robust
regret has an INTERIOR maximum at p=1/2.

A second fixture uses literal K2,2 Unique Games satisfaction worlds
from RHT-08 to ground the source-world/target-action distinction. Only
one of two latent UGC worlds judges the protected probe safe, making its
expected gold gain one-half of the generic fixture's value.
"""
from __future__ import annotations

from fractions import Fraction as Q

from spiral_ln.evaluation_reward_hacking_adaptive_feedback import (
    one_hot_ugc_disclosure_game,
)
from spiral_ln.evaluation_reward_shared_kernel import (
    SharedTransitionEdge,SharedTransitionGame,
)


def interior_transition_hack_fixture(
    *,interval=(Q(0),Q(1)),horizon=2
):
    """Seven-state exact quadratic regret witness with one global gold feature."""
    if horizon!=2:
        raise ValueError("the two-trial interior witness requires two calls")
    edges=[]
    def add(s,a,t,o,base,slope=0,proxy=0,gold=0):
        edges.append(SharedTransitionEdge(
            s,a,t,o,Q(base),Q(slope),Q(proxy),
            gold_coefficients=(Q(gold),)
        ))
    for a in (0,1):
        # A = actor's proxy-maximal action; B = protected gold action.
        initial_zero,initial_one=((1,2) if a==0 else (3,4))
        add(0,a,initial_zero,"first:0",1,-1,1 if a==0 else 0)
        add(0,a,initial_one,"first:1",0,1,1 if a==0 else 0)
        for state in (1,2,3,5,6):
            add(state,a,state,"idle",1)
        add(4,a,5,"second:0",1,-1,gold=1)
        add(4,a,6,"second:1",0,1)
    return SharedTransitionGame(
        state_count=7,
        actions=("proxy_hack","protected_task"),
        initial=(Q(1),)+(Q(0),)*6,
        gold_parameters=("protected_success_value",),
        parameter_interval=interval,
        edges=tuple(edges),horizon=horizon
    )


def ugc_coupled_shared_transition_fixture(*,interval=(Q(0),Q(1))):
    """The protected task can succeed only in a gold-safe UGC reference world.

    States 0 and 1 refer to two genuinely reachable F2 K2,2 one-hot
    satisfaction worlds. Action index 0 in the original UGC roster is
    unsafe in world 0 and safe in world 1. The protected action first
    needs a p-success and then a (1-p)-success. A proxy-tamper action
    receives one certain proxy point and zero protected utility.
    """
    ugc=one_hot_ugc_disclosure_game(2)
    assert ugc.unsafe(0,0) and not ugc.unsafe(1,0)
    edges=[]
    def add(s,a,t,o,base,slope=0,proxy=0,gold=0):
        edges.append(SharedTransitionEdge(
            s,a,t,o,Q(base),Q(slope),Q(proxy),
            gold_coefficients=(Q(gold),),
        ))
    for a in (0,1):
        for w in (0,1):
            if a==0:
                add(w,a,4,"proxy:ack",1,proxy=1)
            else:
                add(w,a,4,"first:0",1,-1)
                add(w,a,2+w,"first:1",0,1)
        for w in (0,1):
            add(2+w,a,4,"second:0",1,-1,gold=int(
                not ugc.unsafe(w,0)
            ))
            add(2+w,a,4,"second:1",0,1)
        add(4,a,4,"terminal",1)
    return SharedTransitionGame(
        state_count=5,
        actions=("proxy_tamper","UGC_protected_probe_0"),
        initial=(Q(1,2),Q(1,2),Q(0),Q(0),Q(0)),
        gold_parameters=("UGC_safe_reward",),
        parameter_interval=interval,edges=tuple(edges),horizon=2,
    )


def proxy_switching_fixture():
    """The proxy winner switches across p, violating uniform-winner contract."""
    edges=[]
    for a in (0,1):
        good_base,good_slope=((0,1) if a==0 else (1,-1))
        edges.append(SharedTransitionEdge(
            0,a,0,"good",Q(good_base),Q(good_slope),
            proxy=Q(1),gold_coefficients=(Q(0),)
        ))
        edges.append(SharedTransitionEdge(
            0,a,0,"bad",1-Q(good_base),-Q(good_slope),
            proxy=Q(0),gold_coefficients=(Q(0),)
        ))
    return SharedTransitionGame(
        state_count=1,actions=("p_favored","one_minus_p_favored"),
        initial=(Q(1),),gold_parameters=("unused",),
        parameter_interval=(Q(1,4),Q(3,4)),
        edges=tuple(edges),horizon=2,
    )
