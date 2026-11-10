"""RHT-16 finite bivariate game-space reward hacking controls.

Two independent *global* Bernoulli kernel parameters p and q are reused
across their appropriate transition events. A protected task succeeds
when first-stage p succeeds and second-stage q fails: p*(1-q).
One action is proxy-optimal when p>=q, the other when q>=p.
The worst protected-regret when the proxy selects the second action
occurs on the switching diagonal at p=q=1/2.

UGC control ties protected true reward to one of two genuinely reachable
F2 K2,2 constraint-satisfaction worlds. A separate degenerate winner
control makes a third proxy policy eligible ONLY on the diagonal.
"""
from __future__ import annotations

from dataclasses import replace
from fractions import Fraction as Q

from spiral_ln.evaluation_reward_hacking_adaptive_feedback import (
    one_hot_ugc_disclosure_game,
)
from spiral_ln.evaluation_reward_two_kernel import (
    TwoKernelEdge,TwoKernelGame,
)


def two_parameter_goodhart_fixture(*,
    p_interval=(Q(0),Q(1)),q_interval=(Q(0),Q(1))
):
    """Strict switching line p=q with gold event p*(1-q)."""
    edges=[]
    def add(s,a,t,o,base,slope_p=0,slope_q=0,proxy=0,gold=0):
        edges.append(TwoKernelEdge(
            s,a,t,o,Q(base),Q(slope_p),Q(slope_q),
            Q(proxy),Q(0),(Q(gold),)
        ))
    for a in (0,1):
        if a==0:
            add(0,a,1,"A:first-fail",1,-1)
            add(0,a,2,"A:first-pass",0,1,proxy=1)
        else:
            add(0,a,3,"B:chosen",1)
        add(1,a,4,"idle",1)
        add(2,a,4,"A:second-fail",1,0,-1,gold=1)
        add(2,a,4,"A:second-pass",0,0,1)
        add(3,a,4,"B:second-pass",0,0,1,proxy=1)
        add(3,a,4,"B:second-fail",1,0,-1)
        add(4,a,4,"terminal",1)
    return TwoKernelGame(
        state_count=5,
        actions=("protected_gold","proxy_only"),
        initial=(Q(1),Q(0),Q(0),Q(0),Q(0)),
        gold_parameters=("gold_safe_success",),
        p_interval=p_interval,q_interval=q_interval,
        edges=tuple(edges),horizon=2
    )


def ugc_two_parameter_goodhart_fixture(*,
    p_interval=(Q(0),Q(1)),q_interval=(Q(0),Q(1))
):
    """Actual K2,2 UGC gold-world labels condition protected success."""
    ugc=one_hot_ugc_disclosure_game(2)
    assert ugc.unsafe(0,0) and not ugc.unsafe(1,0)
    edges=[]
    def add(s,a,t,o,base,slope_p=0,slope_q=0,proxy=0,gold=0):
        edges.append(TwoKernelEdge(
            s,a,t,o,Q(base),Q(slope_p),Q(slope_q),
            Q(proxy),Q(0),(Q(gold),)
        ))
    for a in (0,1):
        for w in (0,1):
            if a==0:
                add(w,a,5,"A:first-fail",1,-1)
                add(w,a,2+w,"A:first-pass",0,1,proxy=1)
            else:
                add(w,a,4,"B:chosen",1)
        for w in (0,1):
            add(2+w,a,5,"A:second-fail",1,0,-1,
                gold=int(not ugc.unsafe(w,0)))
            add(2+w,a,5,"A:second-pass",0,0,1)
        add(4,a,5,"B:second-pass",0,0,1,proxy=1)
        add(4,a,5,"B:second-fail",1,0,-1)
        add(5,a,5,"terminal",1)
    return TwoKernelGame(
        state_count=6,
        actions=("UGC_protected_gold","proxy_only"),
        initial=(Q(1,2),Q(1,2),Q(0),Q(0),Q(0),Q(0)),
        gold_parameters=("UGC_safe_success",),
        p_interval=p_interval,q_interval=q_interval,
        edges=tuple(edges),horizon=2
    )


def proxy_aligned_two_parameter_fixture():
    """True reward is a single positive multiple of the proxy per action."""
    base=two_parameter_goodhart_fixture()
    edges=tuple(replace(
        e,gold_coefficients=(Q(e.proxy),)
    ) for e in base.edges)
    return replace(base,edges=edges,
                   gold_parameters=("globally_shared_proxy_gold",))


def nonlinear_proxy_two_parameter_fixture():
    """Proxy policy P_A=p*q exceeds certified affine-proxy grammar."""
    base=two_parameter_goodhart_fixture()
    changes=[]
    for e in base.edges:
        if e.source==0 and e.action==0 and e.observation=="A:first-pass":
            changes.append(replace(e,proxy=Q(0)))
        elif e.source==2 and e.observation=="A:second-pass":
            changes.append(replace(e,proxy=Q(1)))
        else:
            changes.append(e)
    return replace(base,edges=tuple(changes))


def nonmultiaffine_gold_two_parameter_fixture():
    """Gold p*(1-p) repeats p and violates the bilinear parameter budget."""
    base=two_parameter_goodhart_fixture()
    updates=[]
    for e in base.edges:
        if e.source==2 and e.observation=="A:second-fail":
            updates.append(replace(e,probability_p=Q(-1),probability_q=Q(0)))
        elif e.source==2 and e.observation=="A:second-pass":
            updates.append(replace(e,probability_p=Q(1),probability_q=Q(0)))
        else:
            updates.append(e)
    return replace(base,edges=tuple(updates))


def diagonal_only_proxy_tie_fixture():
    """Third affine proxy policy wins only on diagonal p=q, with gold zero."""
    edges=[]
    def add(a,o,base,slope_p=0,slope_q=0,proxy=0,gold=0):
        edges.append(TwoKernelEdge(
            0,a,0,o,Q(base),Q(slope_p),Q(slope_q),
            Q(proxy),Q(gold),(Q(0),)
        ))
    add(0,"A:paid",0,1,proxy=1,gold=1)
    add(0,"A:unpaid",1,-1,gold=1)
    add(1,"B:paid",0,0,1,proxy=1,gold=1)
    add(1,"B:unpaid",1,0,-1,gold=1)
    add(2,"C:p-paid",0,Q(1,2),proxy=1)
    add(2,"C:p-unpaid",Q(1,2),Q(-1,2))
    add(2,"C:q-paid",0,0,Q(1,2),proxy=1)
    add(2,"C:q-unpaid",Q(1,2),0,Q(-1,2))
    return TwoKernelGame(
        1,("A","B","C"),(Q(1),),("unused",),
        (Q(0),Q(1)),(Q(0),Q(1)),tuple(edges),1
    )
