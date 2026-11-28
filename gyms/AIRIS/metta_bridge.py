"""Native Hyperon causal-memory adapter with independent exact checks."""
from dataclasses import dataclass
from fractions import Fraction as F
from hashlib import sha256
from importlib.metadata import version
from itertools import product
import json
from pathlib import Path
from hyperon import Environment, MeTTa
from partial import (MODELS, SCHEDULES, SCALE, prior, observed, enumerate_channel,
                     masses, greedy_choice, branch_weights, map_mass)

RULES = Path(__file__).with_name("causal_memory.metta")
PIN = "0.2.10"
BITS = tuple(product(range(2), repeat=3))
DIFFS = tuple(product(range(2), repeat=2))


def a_atom(a):
    if a not in SCHEDULES:
        raise ValueError("unknown action schedule")
    return "A"+"".join(map(str,a))


def y_atom(y):
    if y not in BITS:
        raise ValueError("invalid raw observation")
    return "(Y "+" ".join(map(str,y))+")"


def d_atom(d):
    if d not in DIFFS:
        raise ValueError("invalid temporal statistic")
    return "(D "+" ".join(map(str,d))+")"


@dataclass(frozen=True)
class Event:
    event_id: int
    schedule: tuple
    raw: tuple

    def __post_init__(self):
        if type(self.event_id) is not int or not 0<=self.event_id<1024:
            raise ValueError("event ID outside bounded interface")
        a_atom(self.schedule)
        y_atom(self.raw)

    @property
    def symbol(self):
        return f"E{self.event_id}"

    def atom(self):
        return f"(Evidence {self.symbol} {a_atom(self.schedule)} {y_atom(self.raw)})"


def checked_events(events):
    events=tuple(events)
    if len(events)>8 or any(not isinstance(e,Event) for e in events):
        raise ValueError("invalid history")
    ids=[e.event_id for e in events]
    if len(set(ids))!=len(ids):
        raise ValueError("duplicate evidence identity")
    return events


def independent_weights(regime,events):
    weights=list(prior(regime))
    for e in checked_events(events):
        for i,(r,t) in enumerate(MODELS):
            p=enumerate_channel(e.schedule,r,t,"full").get(e.raw,F(0))
            # Full observations have an independent fair initial bit. Rescale
            # to the declared difference likelihood denominator.
            f=2*SCALE*p
            if f.denominator!=1:
                raise ValueError("nonintegral oracle likelihood")
            weights[i]*=int(f)
    return tuple(weights)


class NativeMemory:
    def __init__(self,regime=None):
        if version("hyperon")!=PIN:
            raise ValueError("receipt requires Hyperon "+PIN)
        self.regime=regime
        self.runtime=MeTTa(env_builder=Environment.custom_env(create_config=False,is_test=True))
        self.source=RULES.read_text(encoding="utf-8")
        if self.runtime.run(self.source):
            raise ValueError("unexpected eager MeTTa command")
        self.space=self.runtime.space()
        # The public model grammar is fixed. Generate likelihood facts from
        # AIRIS-04's design-row formula; check native inference separately
        # against literal hidden-path enumeration.
        from partial import channel
        facts=[f"(Prior H{i} {w})" for i,w in enumerate(prior(regime))]
        for a in SCHEDULES:
            for d,ls in channel(a,"difference"):
                facts.extend(f"(Likelihood {a_atom(a)} {d_atom(d)} H{i} {l})"
                             for i,l in enumerate(ls))
        self.static_facts=tuple(facts)
        self.runtime.run("\n".join(facts))
        self.base_count=self.space.atom_count()
        self.events=()
        self.atoms=[]
        self.calls=0

    def query(self,expression):
        self.calls+=1
        (answers,)=self.runtime.run("!"+expression)
        return [str(a) for a in answers]

    def integer(self,expression):
        answers=self.query(expression)
        if len(answers)!=1 or not answers[0].isascii() or not answers[0].isdigit():
            raise ValueError(f"expected single integer for {expression}: {answers}")
        return int(answers[0])

    def load(self,events):
        events=checked_events(events)
        if events==self.events:
            return
        for atom in reversed(self.atoms):
            self.space.remove_atom(atom)
        if self.space.atom_count()!=self.base_count:
            raise ValueError("stale evidence survived removal")
        self.atoms=list(self.runtime.parse_all("\n".join(e.atom() for e in events)))
        for atom in self.atoms:
            self.space.add_atom(atom)
        if self.space.atom_count()!=self.base_count+len(events):
            raise ValueError("evidence insertion mismatch")
        self.events=events

    def code(self,raw):
        ans=self.query(f"(TemporalCode {y_atom(raw)})")
        expected=d_atom(observed(raw,"difference"))
        if ans!=[expected]:
            raise ValueError("native temporal code mismatch")
        return ans[0]

    def weights(self,events):
        self.load(events)
        ids=" ".join(e.symbol for e in self.events)
        actual=tuple(self.integer(f"(PosteriorWeight H{i} ({ids}))") for i in range(len(MODELS)))
        if actual!=independent_weights(self.regime,self.events):
            raise ValueError("native posterior differs from independent hidden-path oracle")
        if not any(actual):
            raise ValueError("zero-likelihood history")
        return actual

    def factor_table(self):
        result={}
        for a in SCHEDULES:
            for d in DIFFS:
                ls=tuple(self.integer(f"(LikelihoodFor {a_atom(a)} {d_atom(d)} H{i})")
                         for i in range(len(MODELS)))
                expected=tuple(int(SCALE*enumerate_channel(a,r,t,"difference").get(d,0))
                               for r,t in MODELS)
                if ls!=expected:
                    raise ValueError("native likelihood mismatch")
                result[a,d]=ls
        return result

    def propose(self,events,table):
        w=self.weights(events)
        scores={}
        for a in SCHEDULES:
            # Use verified native posterior and native likelihood rows. Exact
            # integer target reduction and argmax are host orchestration.
            scores[a]=sum(max(masses(tuple(x*l for x,l in zip(w,table[a,d]))))
                          for d in DIFFS)
        expected={a:sum(map_mass(p) for p in branch_weights(w,a,"difference")) for a in SCHEDULES}
        choice=max(SCHEDULES,key=scores.__getitem__)
        if scores!=expected or choice!=greedy_choice(w):
            raise ValueError("native-derived proposal differs from AIRIS-04 oracle")
        return {"schedule":choice,"scores":{"".join(map(str,a)):str(F(v,sum(w)*SCALE))
                                             for a,v in scores.items()},
                "weights":w,"target_masses":masses(w)}

    def digest(self,events):
        # Public evidence content and declared model grammar, no secret root.
        return sha256("\n".join((self.source,*self.static_facts,
                                 *(e.atom() for e in checked_events(events)))).encode()).hexdigest()


def census():
    native=NativeMemory()
    for raw in BITS:
        native.code(raw)
    table=native.factor_table()
    rows=[]
    # All 64 one-episode public input/output pairs under mixed prior.
    for a,raw in product(SCHEDULES,BITS):
        events=(Event(0,a,raw),)
        rows.append({"events":[events[0].atom()],"result":native.propose(events,table),
                     "input_sha256":native.digest(events)})
    # Evidence lifecycle: a second observation, revoke one source, amend
    # another source, and clear. Distinct events with identical contents
    # remain distinct independent episodes.
    e0=Event(0,(0,1,0),(0,1,1))
    e1=Event(1,(0,1,0),(0,1,1))
    amend=Event(1,(0,1,0),(0,0,0))
    histories=((e0,),(e0,e1),(e1,),(amend,),(e0,amend),())
    lifecycle=[]
    for events in histories:
        lifecycle.append({"events":[e.atom() for e in events],
                          "result":native.propose(events,table),
                          "input_sha256":native.digest(events)})
    if lifecycle[0]["result"]["weights"]!=lifecycle[2]["result"]["weights"]:
        raise AssertionError("same evidence contents differ after revocation")
    if lifecycle[0]["result"]["weights"]==lifecycle[1]["result"]["weights"]:
        raise AssertionError("independent duplicate content did not contribute")
    if lifecycle[-1]["result"]["weights"]!=prior(None):
        raise AssertionError("clear did not restore prior")
    return {"experiment":"AIRIS-05","evidence":"native MeTTa finite wiring and inference verification",
            "hyperon_version":version("hyperon"),"public_single_episode_cases":len(rows),
            "lifecycle_cases":len(lifecycle),"native_queries":native.calls,
            "rows":rows,"lifecycle":lifecycle,
            "source_sha256":{name:sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
                             for name in ("metta_bridge.py","causal_memory.metta","partial.py",
                                          "test_metta_bridge.py","METTA.md")}}


if __name__=="__main__":
    print(json.dumps(census(),indent=2,sort_keys=True))
