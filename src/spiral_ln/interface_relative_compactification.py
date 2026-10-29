"""IRC-02: exact finite timed partially observed interface reference.

The public state consists of interface mode and a positive integer time budget.
Reward is observable feedback. Every kernel uses exact fractions.Fraction.
This is an exact *finite* reference, not a neural-model performance claim.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as F


@dataclass(frozen=True)
class Branch:
    probability: F
    signal: str
    reward: int
    duration: int
    next_state: str
    next_mode: str
    done: bool


@dataclass
class Machine:
    states: tuple[str, ...]
    modes: tuple[str, ...]
    actions: dict[str, tuple[str, ...]]
    kernels: dict[tuple[str, str, str], tuple[Branch, ...]]

    def __post_init__(self) -> None:
        if not self.states or not self.modes or len(set(self.states)) != len(self.states) or len(set(self.modes)) != len(self.modes):
            raise ValueError("invalid state set")
        if set(self.actions) != set(self.modes) or any(len(set(a)) != len(a) for a in self.actions.values()):
            raise ValueError("missing mode action definitions or duplicate actions")
        expected = {(s, m, a) for s in self.states for m in self.modes for a in self.actions[m]}
        if set(self.kernels) != expected:
            raise ValueError("missing or extra kernels")
        for (s, m, a), rows in self.kernels.items():
            if not rows or any(type(r.probability) is not F for r in rows):
                raise ValueError("non-rational or empty kernel")
            if sum((r.probability for r in rows), F(0)) != 1:
                raise ValueError("unnormalized kernel")
            for r in rows:
                if (type(r.probability) is not F or r.probability <= 0
                    or type(r.duration) is not int or r.duration <= 0
                    or type(r.reward) is not int or r.next_state not in self.states
                    or r.next_mode not in self.modes or type(r.done) is not bool
                    or type(r.signal) is not str):
                    raise ValueError("invalid timed branch")

    def admissible(self, mode: str, remaining: int) -> tuple[str, ...]:
        if mode not in self.actions or type(remaining) is not int or remaining < 0:
            raise ValueError("invalid public mode or remaining time")
        # Robust legal-action check against *all* hidden states, even prior zero-mass ones.
        return tuple(a for a in self.actions[mode]
                     if max(r.duration for s in self.states for r in self.kernels[s, mode, a]) <= remaining)


def normalize(prior: dict[str, F], states: tuple[str, ...]) -> tuple[F, ...]:
    if set(prior) != set(states) or any(type(p) is not F or p < 0 for p in prior.values()) or sum(prior.values(), F(0)) != 1:
        raise ValueError("invalid belief")
    return tuple(prior[s] for s in states)


def successors(machine: Machine, belief: tuple[F, ...], mode: str, time: int, action: str):
    if len(belief) != len(machine.states) or any(type(b) is not F or b < 0 for b in belief) or sum(belief, F(0)) != 1:
        raise ValueError("invalid belief")
    if action not in machine.admissible(mode, time):
        raise ValueError("illegal action or missed deadline")
    weights = {}
    for state, mass in zip(machine.states, belief):
        for r in machine.kernels[state, mode, action]:
            if not mass:
                continue
            event = (r.signal, r.reward, r.duration, r.next_mode, r.done)
            key = (event, r.next_state)
            weights[key] = weights.get(key, F(0)) + mass*r.probability
    grouped = {}
    for (event, next_state), mass in weights.items():
        row = grouped.setdefault(event, dict.fromkeys(machine.states, F(0)))
        row[next_state] += mass
    result = []
    for event, state_masses in sorted(grouped.items()):
        p = sum(state_masses.values(), F(0))
        post = tuple(state_masses[s]/p for s in machine.states)
        result.append((event, p, post))
    if sum((p for _,p,_ in result), F(0)) != 1:
        raise RuntimeError("posterior normalization invariant failed")
    return tuple(result)


def predictive_signature(machine: Machine, belief: tuple[F, ...], mode: str, time: int):
    """Canonical all-tests suffix signature. Each action is expanded adaptively."""
    if time == 0:
        return ()
    nodes = []
    for a in machine.admissible(mode, time):
        branches = []
        for event, p, post in successors(machine, belief, mode, time, a):
            signal, reward, dt, next_mode, done = event
            future = () if done else predictive_signature(machine, post, next_mode, time-dt)
            branches.append((event, p, future))
        nodes.append((a,tuple(branches)))
    return tuple(nodes)


def independent_cylinder_law(machine: Machine, belief: tuple[F, ...], mode: str, time: int):
    """Independent forward enumerator of ALL action/feedback cylinder probabilities.

    A cylinder is a fixed feasible action/feedback sequence; adaptive policies
    select among these cylinders based on their feedback histories.
    """
    out = {}
    def visit(b, q, d, prefix, mass):
        for a in machine.admissible(q,d):
            for event,p,next_b in successors(machine,b,q,d,a):
                path = prefix + ((a,event),)
                out[path] = mass*p
                if not event[-1]:
                    visit(next_b, event[3], d-event[2], path, mass*p)
    visit(belief,mode,time,(),F(1))
    return out



def direct_world_cylinders(machine: Machine, belief: tuple[F, ...], mode: str, time: int):
    """Independent exact enumerator over hidden-state transition branches.

    Does not call the posterior updater or recursive predictive signature.
    Carries joint source-state weights, including event-branch probability.
    """
    out = {}
    def visit(masses, q, d, prefix):
        for a in machine.admissible(q, d):
            by_event = {}
            for s, p in zip(machine.states, masses):
                for r in machine.kernels[s,q,a]:
                    if not p:
                        continue
                    event = (r.signal,r.reward,r.duration,r.next_mode,r.done)
                    state_mass = by_event.setdefault(event, dict.fromkeys(machine.states, F(0)))
                    state_mass[r.next_state] += p*r.probability
            for event, state_mass in by_event.items():
                path=prefix+((a,event),)
                out[path] = sum(state_mass.values(), F(0))
                if not event[-1]:
                    visit(tuple(state_mass[s] for s in machine.states),event[3],d-event[2],path)
    visit(belief,mode,time,())
    return out


def expected_value(machine: Machine, belief: tuple[F,...], mode: str, time: int) -> F:
    """Exact Bellman value with reward on every transition; option to stop for zero."""
    options = [F(0)]
    for a in machine.admissible(mode,time):
        score = F(0)
        for event,p,post in successors(machine,belief,mode,time,a):
            future = F(0) if event[-1] else expected_value(machine,post,event[3],time-event[2])
            score += p*(event[1]+future)
        options.append(score)
    return max(options)


def feedback_machine(probe_accuracy: F=F(3,4), probe_duration: int=1) -> Machine:
    states=("0","1")
    modes=("q",)
    acts={"q":("probe","guess0","guess1")}
    kernels={}
    for x in states:
        kernels[x,"q","probe"] = tuple(Branch(probe_accuracy if y==x else 1-probe_accuracy,
                    "y"+y,0,probe_duration,x,"q",False) for y in states)
        for guess in states:
            kernels[x,"q","guess"+guess]=(Branch(F(1),"terminal",int(x==guess),1,x,"q",True),)
    return Machine(states,modes,acts,kernels)


def switch_machine() -> Machine:
    states=("x",);modes=("left","right")
    acts={"left":("hit",),"right":("switch",)}
    kernels={
        ("x","left","hit"):(Branch(F(1),"hit",1,1,"x","left",True),),
        ("x","right","switch"):(Branch(F(1),"switched",0,1,"x","left",False),),
    }
    return Machine(states,modes,acts,kernels)


def class_count(machine: Machine, beliefs: tuple[tuple[F,...], ...], mode: str, time: int) -> int:
    return len({predictive_signature(machine,b,mode,time) for b in beliefs})


def shortest_distinguishing_cylinder(machine: Machine, left: tuple[F,...], right: tuple[F,...], mode: str, time: int):
    x=independent_cylinder_law(machine,left,mode,time)
    y=independent_cylinder_law(machine,right,mode,time)
    for key in sorted(set(x)|set(y),key=lambda z:(len(z),repr(z))):
        if x.get(key,F(0))!=y.get(key,F(0)):
            return (key,x.get(key,F(0)),y.get(key,F(0)))
    return None


def witnessing_policy(machine: Machine, left: tuple[F, ...], right: tuple[F, ...],
                      mode: str, time: int):
    """Return an on-support distinguishing cylinder and a legal adaptive policy.

    The policy continues only on the witness feedback path. It stops on every
    other observed branch, so its leaf trace law distinguishes the beliefs.
    """
    witness = shortest_distinguishing_cylinder(machine, left, right, mode, time)
    if witness is None:
        return None
    path, p_left, p_right = witness
    def build(index, q, d):
        if index == len(path):
            return None
        action, chosen = path[index]
        if action not in machine.admissible(q, d):
            raise AssertionError("witness action violated deadline")
        events = sorted({(r.signal, r.reward, r.duration, r.next_mode, r.done)
                         for s in machine.states for r in machine.kernels[s,q,action]})
        branches = []
        for event in events:
            child = (build(index+1,event[3],d-event[2])
                     if event == chosen and not event[-1] else None)
            branches.append((event, child))
        return (action, tuple(branches))
    return (build(0,mode,time), path, p_left, p_right)
