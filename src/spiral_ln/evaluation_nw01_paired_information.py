"""NW-01 exact paired-world information and Brier floors.

Under equal-prior binary clean/hidden worlds with identical public
observations, every deterministic public-only readout gets exactly one
correct per paired root. A probabilistic readout p has average Brier loss
1/4+(p-1/2)^2. Iterating a state transition that sees only the same public
observation cannot distinguish its worlds.

Authenticated true-coefficient residuals offer an *additional* observation
and can distinguish clean=0 from hidden beta != 0; a source-matched sham
residual identical in both paired worlds cannot. This is exact finite
arithmetic on declared hypothetical feedback, not neural-model evidence.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence


@dataclass(frozen=True)
class PairedWorld:
    root: str
    public_signal: tuple[int,...]
    hidden_beta: int


def validate(roots:Sequence[PairedWorld])->tuple[PairedWorld,...]:
    rows=tuple(roots)
    if not rows or len({r.root for r in rows})!=len(rows):
        raise ValueError("need nonempty distinct source pairs")
    if any(not isinstance(r.root,str) or not r.root
           or not isinstance(r.public_signal,tuple)
           or not r.public_signal
           or any(type(v) is not int for v in r.public_signal)
           or type(r.hidden_beta) is not int
           or r.hidden_beta==0 for r in rows):
        raise ValueError("invalid paired-world input or zero hidden suffix")
    return rows


def brier_on_pair(p:Fraction)->Fraction:
    """Equal prior: average over y=0 and y=1 for ONE source root."""
    if not 0<=p<=1:raise ValueError("posterior outside [0,1]")
    return (p*p+(1-p)*(1-p))/2


def exact_brier_excess(p:Fraction)->Fraction:
    return brier_on_pair(p)-Fraction(1,4)


def equal_prior_public_only_summary(probs:Sequence[Fraction]):
    ps=tuple(probs)
    if not ps:raise ValueError("at least one public source root required")
    if any(not isinstance(p,Fraction) or not 0<=p<=1 for p in ps):
        raise ValueError("use exact rational posterior probabilities")
    losses=tuple(brier_on_pair(p) for p in ps)
    return {
        "source_pairs":len(ps),"world_cases":2*len(ps),
        "exact_argmax_accuracy":Fraction(1,2),
        "exact_equal_prior_brier_floor":Fraction(1,4),
        "mean_brier":sum(losses,Fraction())/len(losses),
        "mean_brier_excess":sum((p-Fraction(1,2))**2 for p in ps)/len(ps),
        "same_world_input_per_root":True
    }


def balanced_pair_predictions(public_labels:Sequence[int]):
    """One predicted binary label per root, repeated in both true worlds."""
    labels=tuple(public_labels)
    if not labels or any(type(v) is not int or v not in (0,1) for v in labels):
        raise ValueError("binary deterministic decisions required")
    correct=sum(int(v==0)+int(v==1) for v in labels)
    assert correct==len(labels)
    return Fraction(correct,2*len(labels))


def hypothetical_true_witness(root:PairedWorld,world:int):
    validate((root,))
    if world not in (0,1):raise ValueError("world must be 0 clean or 1 hidden")
    return root.hidden_beta if world else 0


def witness_classification_responses(roots:Sequence[PairedWorld]):
    rows=validate(roots)
    correct=0
    for r in rows:
        for world in (0,1):
            delta=hypothetical_true_witness(r,world)
            guess=int(delta!=0)
            correct+=int(guess==world)
    return Fraction(correct,2*len(rows))


def source_matched_sham_accuracy(roots:Sequence[PairedWorld],
                                 sham_residuals:Sequence[int]):
    rows=validate(roots)
    shams=tuple(sham_residuals)
    if len(shams)!=len(rows) or any(type(v) is not int for v in shams):
        raise ValueError("need one label-independent sham per root")
    correct=0
    for value in shams:
        # Even if a sham looks exactly like a valid witness, its value is
        # identical in both clean and hidden worlds of the paired source.
        guess=int(value!=0)
        correct+=int(guess==0)+int(guess==1)
    return Fraction(correct,2*len(rows))


def shared_deterministic_recurrence(public:tuple[int,...],steps:int,
                                    initial:int=0):
    """A finite public-only recurrence, equal for both paired worlds."""
    if steps<0 or not public or any(type(v) is not int for v in public):
        raise ValueError("bad public recurrence input")
    value=initial
    out=[]
    for _ in range(steps):
        value=(3*value+sum(public))%65521
        out.append(value)
    return tuple(out)


def finite_world_check(roots:Sequence[PairedWorld],steps:int=8):
    rows=validate(roots)
    for root in rows:
        public_a=shared_deterministic_recurrence(root.public_signal,steps)
        public_b=shared_deterministic_recurrence(root.public_signal,steps)
        if public_a!=public_b:
            raise AssertionError("identical public roots diverged under deterministic recurrence")
    assert witness_classification_responses(rows)==1
    assert source_matched_sham_accuracy(rows,[0]*len(rows))==Fraction(1,2)
    return {
        "independent_source_roots":len(rows),"paired_world_cases":2*len(rows),
        "public_only_accuracy":"1/2",
        "hypothetical_true_witness_accuracy":"1",
        "source_matched_sham_accuracy":"1/2",
        "public_recurrent_depth":steps,
        "equal_public_trajectories_proved_by_deterministic_replay":True
    }
