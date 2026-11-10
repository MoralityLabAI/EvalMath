"""RHT-13 finite POMDP fixtures joining UGC worlds and evaluator integrity.

All latent worlds are real F2 K2,n game constraint satisfaction records
as in RHT-08. The evaluator integrity can change after a tamper tool,
a rejected action, or a safe approval as in RHT-11. Observable reward
magnitudes disclose the actual proxy reward, as a real RL learner would see.

The gold source has globally shared semantic reward coefficients:
  safe_approval: positive true utility,
  unsafe_approval: negative protected utility,
  tamper_cost: nonnegative private cost, subtracted upon tamper attempts.

Each semantic parameter is shared by all transitions/time steps/worlds.
A one-state fair-noise fixture supplies a martingale-coboundary positive
control with nonzero realized pathwise reward periods.
"""
from __future__ import annotations

from fractions import Fraction as Q

from spiral_ln.evaluation_reward_hacking_adaptive_feedback import (
    one_hot_ugc_disclosure_game,
)
from spiral_ln.evaluation_reward_hacking_stateful import MutableEvaluator
from spiral_ln.evaluation_reward_stochastic_closure import (
    StochasticRewardEdge,StochasticRewardGame,
)


def evaluator_pomdp(
    *, worlds:int=3,horizon:int=2,
    channel:MutableEvaluator|None=None,
    corrupted_proxy_multiplier:Q=Q(4),
) -> StochasticRewardGame:
    """Build evaluator-tampering POMDP with a terminal alarm state.

    Hidden state index 2*w+s is the protected UGC world w and evaluator
    integrity s. Index 2*n is a terminal/alarm state with zero future
    reward, represented by 'done' no-op transitions for every action.

    The actor can choose tamper or a proxy-eligible candidate action;
    only approval/rejection/acknowledgment/alarm and the numeric proxy
    reward are observed. A bad approval enters the terminal state here,
    matching the first-harm-absorbing semantics of RHT-11.
    """
    game=one_hot_ugc_disclosure_game(worlds)
    ch=MutableEvaluator() if channel is None else channel
    bonus=Q(corrupted_proxy_multiplier)
    if bonus<0:
        raise ValueError("proxy multiplier must be nonnegative")
    n=len(game.world_records)
    terminal=2*n
    actions=(tuple(f"probe:{a}" for a in game.public_maximizers())
             + (("tamper",) if ch.allow_tamper else ()))
    tamper_index=len(actions)-1 if ch.allow_tamper else None
    zero=(Q(0),Q(0),Q(0))
    safe=(Q(1),Q(0),Q(0))
    unsafe=(Q(0),Q(1),Q(0))
    tamper=(Q(0),Q(0),Q(-1))
    edges=[]

    def add(source,a,target,observation,p,proxy=Q(0),gold_coeff=zero):
        p=Q(p)
        if p>0:
            edges.append(StochasticRewardEdge(
                source=source,action=a,target=target,observation=observation,
                probability=p,proxy=Q(proxy),gold_coefficients=gold_coeff
            ))

    for w in range(n):
        for s in (0,1):
            source=2*w+s
            for a in game.public_maximizers():
                alarm=ch.alarm_probability(s,"probe")
                add(source,a,terminal,"alarm",alarm)
                passed=1-alarm
                bad=game.unsafe(w,a)
                approval=(ch.false_accept(s) if bad
                          else 1-ch.false_reject(s))
                for approved,p in ((True,approval),(False,1-approval)):
                    if approved and bad:
                        add(source,a,terminal,
                            f"approved:{bonus if s else Q(1)}",
                            passed*p,bonus if s else Q(1),unsafe)
                        continue
                    verdict="approved" if approved else "rejected"
                    for s1,step_prob in ch.post_verdict_states(s,verdict):
                        observation=(f"approved:{bonus if s else Q(1)}"
                                     if approved else "rejected")
                        add(source,a,2*w+s1,observation,
                            passed*p*step_prob,
                            bonus if approved and s else Q(1) if approved else Q(0),
                            safe if approved else zero)
            if ch.allow_tamper:
                if s:
                    destination=((1,Q(1)),)
                else:
                    destination=((0,1-Q(ch.tamper_success)),
                                 (1,Q(ch.tamper_success)))
                for s1,prob in destination:
                    alarm=ch.alarm_probability(s1,"tamper")
                    add(source,tamper_index,terminal,"alarm",
                        prob*alarm,gold_coeff=tamper)
                    add(source,tamper_index,2*w+s1,"ack",
                        prob*(1-alarm),gold_coeff=tamper)
    for a in range(len(actions)):
        add(terminal,a,terminal,"done",Q(1))
    initial=tuple(
        Q(1,n) if s==0 else Q(0)
        for w in range(n) for s in (0,1)
    )+(Q(0),)
    return StochasticRewardGame(
        state_count=2*n+1,actions=actions,initial=initial,
        gold_parameters=("safe_approval","unsafe_approval","tamper_cost"),
        edges=tuple(edges),horizon=horizon
    )


def fair_martingale_noise_game(horizon:int=2):
    """Exact zero-mean reward discrepancy with nonzero pathwise periods.

    Both actions share an independent fair (+1,-1) proxy reward signal
    and zero gold reward. Every decision can depend on earlier observed
    coin flips. Expected proxy minus gold is identically zero for EVERY
    allowed observation policy, although realized path returns differ.
    """
    edges=tuple(
        StochasticRewardEdge(
            0,a,0,observation,Q(1,2),Q(value),
            gold_coefficients=(Q(0),)
        )
        for a in (0,1)
        for observation,value in (("plus",1),("minus",-1))
    )
    return StochasticRewardGame(
        state_count=1,actions=("sample_A","sample_B"),
        initial=(Q(1),),gold_parameters=("unused",),edges=edges,
        horizon=horizon,
    )


def biased_reward_signal_game(horizon:int=2):
    """One action has proxy expectation 1, the other 0, both gold zero."""
    edges=(
        StochasticRewardEdge(0,0,0,"approved",Q(1),Q(1),
                             gold_coefficients=(Q(0),)),
        StochasticRewardEdge(0,1,0,"rejected",Q(1),Q(0),
                             gold_coefficients=(Q(0),)),
    )
    return StochasticRewardGame(
        state_count=1,actions=("proxy_biased","neutral"),
        initial=(Q(1),),gold_parameters=("unused",),edges=edges,
        horizon=horizon,
    )



def time_expanded_support_graph(
    game:StochasticRewardGame,theta
):
    """Embed all positive-probability stochastic transitions in RHT-12's DAG.

    The artificial root connects to each possible initial hidden state
    with zero reward. Every positive transition appears as its own
    time-indexed occurrence, retaining its independent action/observation
    identity, and all states at the final horizon are terminal. Dead
    branches in the product graph are handled by RHT-12's productive
    subgraph filter. This deliberately discards transition probabilities
    and actor observation constraints, giving a path-support outer bound.
    """
    from spiral_ln.evaluation_reward_transition_closure import (
        TimedRewardEdge,TimedRewardGame,
    )
    theta=tuple(Q(x) for x in theta)
    if len(theta)!=len(game.gold_parameters):
        raise ValueError("one true reward parameter per gold feature")
    states=game.state_count
    def vertex(time,state):
        return 1+time*states+state
    layers=(0,)+tuple(
        time+1 for time in range(game.horizon+1)
        for _ in range(states)
    )
    edges=[]
    for s,m in enumerate(game.initial):
        if m:
            edges.append(TimedRewardEdge(
                0,vertex(0,s),Q(0),Q(0),"root"
            ))
    for time in range(game.horizon):
        for e in game.edges:
            edges.append(TimedRewardEdge(
                vertex(time,e.source),vertex(time+1,e.target),
                game.gold(e,theta),Q(e.proxy),
                f"{game.actions[e.action]}:{e.observation}"
            ))
    return TimedRewardGame(
        layers=layers,start=0,
        terminals=tuple(vertex(game.horizon,s) for s in range(states)),
        edges=tuple(edges)
    )
