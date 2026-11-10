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



def rational_proxy_crossing_fixture(*,interval=(Q(0),Q(1))):
    """One-step p versus 1-p proxy crossing with gold regret at p=1/2.

    A receives proxy and protected gold on a Bernoulli(p) success.
    B receives proxy only on a Bernoulli(1-p) success. B is proxy best
    strictly below 1/2, A above; at the tie the adversary chooses B,
    whose true-gold return is zero.
    """
    edges=(
        SharedTransitionEdge(0,0,0,"A:win",Q(0),Q(1),Q(1),
                             gold_coefficients=(Q(1),)),
        SharedTransitionEdge(0,0,0,"A:lose",Q(1),Q(-1),
                             gold_coefficients=(Q(0),)),
        SharedTransitionEdge(0,1,0,"B:win",Q(1),Q(-1),Q(1),
                             gold_coefficients=(Q(0),)),
        SharedTransitionEdge(0,1,0,"B:lose",Q(0),Q(1),
                             gold_coefficients=(Q(0),)),
    )
    return SharedTransitionGame(
        state_count=1,actions=("gold_protected","proxy_only"),
        initial=(Q(1),),gold_parameters=("true_success_value",),
        parameter_interval=interval,edges=edges,horizon=1
    )


def irrational_proxy_crossing_fixture(*,interval=(Q(0),Q(1))):
    """p^2 vs (1-p) proxy crossing at p=(sqrt(5)-1)/2.

    Protected first action produces proxy+gold only when two Bernoulli(p)
    trials both succeed, so its expected gold/proxy is theta*p^2.
    Proxy-only first action receives score one with probability 1-p.
    Second action has no influence on either protocol.
    """
    edges=[]
    def add(s,a,t,obs,b,sl,proxy=0,gold=0):
        edges.append(SharedTransitionEdge(
            s,a,t,obs,Q(b),Q(sl),Q(proxy),
            gold_coefficients=(Q(gold),)
        ))
    for a in (0,1):
        if a==0:
            add(0,a,1,"A:first-fail",1,-1)
            add(0,a,2,"A:first-pass",0,1)
        else:
            add(0,a,3,"B:proxy-paid",1,-1,proxy=1)
            add(0,a,3,"B:proxy-empty",0,1)
        for state in (1,3,4):
            add(state,a,state,"idle",1,0)
        add(2,a,4,"A:second-pass",0,1,proxy=1,gold=1)
        add(2,a,4,"A:second-fail",1,-1)
    return SharedTransitionGame(
        state_count=5,actions=("two_step_gold","immediate_proxy"),
        initial=(Q(1),Q(0),Q(0),Q(0),Q(0)),
        gold_parameters=("shared_protected_gold",),
        parameter_interval=interval,
        edges=tuple(edges),horizon=2
    )


def isolated_tangent_proxy_tie_fixture(*,interval=(Q(0),Q(1))):
    """Proxy-only bad policy ties good policy ONLY at p=1/2.

    Good action immediately earns true gold 1 and proxy 1. Bad action
    earns proxy 3/4, and gets a second proxy point on an exactly
    p*(1-p) event. Thus its proxy is 1-(p-1/2)^2, with gold zero.
    The isolated tie at 1/2 admits a low-gold adversarial selection.
    """
    edges=[]
    def add(s,a,t,o,b,sl=0,proxy=0,gold=0):
        edges.append(SharedTransitionEdge(
            s,a,t,o,Q(b),Q(sl),Q(proxy),
            gold_coefficients=(Q(gold),)
        ))
    for a in (0,1):
        if a==0:
            add(0,a,3,"good",1,proxy=1,gold=1)
        else:
            add(0,a,1,"bad:first-pass",0,1,proxy=Q(3,4))
            add(0,a,3,"bad:first-fail",1,-1,proxy=Q(3,4))
        for state in (2,3):
            add(state,a,state,"idle",1)
        add(1,a,2,"bad:bonus",1,-1,proxy=1)
        add(1,a,2,"bad:no-bonus",0,1)
    return SharedTransitionGame(
        state_count=4,actions=("gold_good","isolated_proxy_tie"),
        initial=(Q(1),Q(0),Q(0),Q(0)),
        gold_parameters=("true_good",),
        parameter_interval=interval,edges=tuple(edges),horizon=2
    )
