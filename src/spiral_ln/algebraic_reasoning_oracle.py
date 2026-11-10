"""ARG-01: independent finite integer formal-series program-verification oracle.

No neural imports. The input/output demonstrations, topology, and fresh query
are public. Hidden source programs and future outputs are scoring-only.
Equality through a finite coefficient horizon is never a proof of an infinite
formal-series identity.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
from itertools import product
import argparse
import json
import random
from pathlib import Path
from typing import Sequence

OPS = ("I", "N", "S", "R")
TOPOLOGIES = ("fork", "cascade", "additive", "hadamard")
PROGRAMS = tuple(product(OPS, repeat=3))
SEED = 2026111027
PREFIX = 12
FUTURE = 32
CAL_FAMILIES = ("signed", "product", "sparse")
OOD_FAMILIES = ("rational", "squared", "twisted_product", "lacunary")
ALL_FAMILIES = CAL_FAMILIES + OOD_FAMILIES
VERSION = "arg01.oracle.v1"


def check_series(values: Sequence[int], *, degree: int | None = None) -> tuple[int, ...]:
    if not isinstance(values, (tuple, list)) or not values or values[0] != 1:
        raise ValueError("expected integer unit series")
    if any(type(x) is not int for x in values):
        raise ValueError("noninteger coefficient")
    if degree is not None and len(values) != degree + 1:
        raise ValueError("incorrect coefficient horizon")
    return tuple(values)


def convolution(a: Sequence[int], b: Sequence[int]) -> tuple[int, ...]:
    a = check_series(a)
    b = check_series(b, degree=len(a)-1)
    return tuple(sum(a[i]*b[n-i] for i in range(n+1)) for n in range(len(a)))


def reciprocal(a: Sequence[int]) -> tuple[int, ...]:
    a = check_series(a)
    result = [1]
    for n in range(1,len(a)):
        result.append(-sum(a[k]*result[n-k] for k in range(1,n+1)))
    return tuple(result)


def unary(a: Sequence[int], op: str) -> tuple[int, ...]:
    a=check_series(a)
    if op == "I":return a
    if op == "N":return tuple((-v if n%2 else v) for n,v in enumerate(a))
    if op == "S":return tuple(a[n//2] if n%2==0 else 0 for n in range(len(a)))
    if op == "R":return reciprocal(a)
    raise ValueError("unknown unary operator")


def execute(a: Sequence[int], topology: str, graph: Sequence[str]) -> tuple[int, ...]:
    a=check_series(a)
    graph=tuple(graph)
    if topology not in TOPOLOGIES or graph not in PROGRAMS:
        raise ValueError("unknown graph or topology")
    left = unary(a,graph[0])
    right = unary(left if topology=="cascade" else a,graph[1])
    if topology=="additive":
        mixed = (1,) + tuple(left[i]+right[i] for i in range(1,len(a)))
    elif topology=="hadamard":
        mixed = (1,) + tuple(left[i]*right[i] for i in range(1,len(a)))
    else:
        mixed = convolution(left,right)
    return unary(mixed,graph[2])


def first_error(a: Sequence[int], b: Sequence[int]) -> int | None:
    if len(a)!=len(b):raise ValueError("comparison length differs")
    return next((i for i,(x,y) in enumerate(zip(a,b)) if x!=y),None)


@dataclass(frozen=True)
class Case:
    identifier: str
    split: str
    family: str
    topology: str
    demos: tuple[tuple[tuple[int,...],tuple[int,...]],...]
    query: tuple[int,...]
    future: tuple[int,...]
    source_graph: tuple[str,str,str] | None
    pair_id: str | None = None

    @property
    def public(self) -> dict:
        return {
            "case_id":self.identifier,"topology":self.topology,
            "observed_degree":PREFIX,
            "demos":[{"input":list(f[:PREFIX+1]),"output":list(y[:PREFIX+1])}
                     for f,y in self.demos],
            "query":list(self.query[:PREFIX+1]),
        }

    @property
    def signature(self) -> str:
        return sha256(json.dumps({k:v for k,v in self.public.items() if k!="case_id"},sort_keys=True,separators=(',',':')).encode()).hexdigest()


def source(rng: random.Random, family: str, degree: int = FUTURE) -> tuple[int,...]:
    if degree < 1:raise ValueError("degree >=1 required")
    if family == "signed":
        return (1,) + tuple(rng.randint(-2,2) for _ in range(degree))
    if family == "sparse":
        return (1,) + tuple(rng.choice((-2,-1,1,2)) if rng.randrange(5)==0 else 0 for _ in range(degree))
    if family in ("product", "twisted_product"):
        modulus=rng.choice((3,4,5,6,7,9,11))
        mask={j for j in range(modulus) if rng.randrange(2)==1}
        if not mask:mask={rng.randrange(modulus)}
        f=[1]+[0]*degree
        for part in range(1,degree+1):
            if part%modulus in mask:
                for i in range(part,degree+1):
                    f[i]+=f[i-part]
        return unary(tuple(f),"N") if family=="twisted_product" else tuple(f)
    if family == "rational":
        return reciprocal(source(rng,"sparse",degree))
    if family == "squared":
        base=source(rng,"sparse",degree)
        return convolution(base,base)
    if family == "lacunary":
        base=source(rng,"signed",degree)
        return tuple(base[i//3] if i%3==0 else 0 for i in range(degree+1))
    raise ValueError("unknown generator family")


def make_case(rng: random.Random, *, split:str, family:str, topology:str,
              graph:tuple[str,str,str], identifier:str, mutate_observed:bool=False,
              pair_id:str|None=None) -> Case:
    demos=[]
    for _ in range(2):
        f=source(rng,family)
        y=execute(f,topology,graph)
        demos.append((f,y))
    if mutate_observed:
        f,y=demos[-1]
        yy=list(y)
        yy[7]+=rng.choice((-3,-2,-1,1,2,3))
        demos[-1]=(f,tuple(yy))
    q=source(rng,family)
    return Case(identifier,split,family,topology,tuple(demos),q,
                execute(q,topology,graph),graph,pair_id)


def roster(*, calibration_per_family:int=12, test_per_family:int=24,
           negative:int=12, collision_pairs:int=6, include_test:bool=True) -> dict[str,list[Case]]:
    if min(calibration_per_family,test_per_family,negative,collision_pairs)<1:
        raise ValueError("roster counts must be positive")
    output={"calibration":[]}
    if include_test:
        output.update({family:[] for family in ALL_FAMILIES})
        output["negative"]=[]
        output["collision"]=[]
    observed:set[str]=set()
    def insert(key:str,item:Case,*,duplicate:bool=False)->bool:
        if item.signature in observed and not duplicate:return False
        observed.add(item.signature)
        output[key].append(item)
        return True
    def fill(key:str,family:str,count:int,seed:int)->None:
        rng=random.Random(seed)
        trials=0
        while len([item for item in output[key] if item.family==family])<count:
            trials+=1
            if trials>count*500:raise RuntimeError("unfillable roster")
            topology=rng.choice(TOPOLOGIES)
            graph=rng.choice(PROGRAMS)
            item=make_case(rng,split=key,family=family,topology=topology,graph=graph,
                           identifier=f"{key}:{family}:{trials:05d}")
            insert(key,item)
    for i,family in enumerate(CAL_FAMILIES):
        fill("calibration",family,calibration_per_family,SEED+101+i*137)
    if not include_test:return output
    for i,family in enumerate(ALL_FAMILIES):
        fill(family,family,test_per_family,SEED+2001+i*137)
    rng=random.Random(SEED+991)
    tries=0
    while len(output["negative"])<negative:
        tries+=1
        if tries>negative*1000:raise RuntimeError("negative roster exhaustion")
        family=rng.choice(ALL_FAMILIES)
        topology=rng.choice(TOPOLOGIES)
        graph=rng.choice(PROGRAMS)
        item=make_case(rng,split="negative",family=family,topology=topology,
                       graph=graph,identifier=f"negative:{tries:05d}",mutate_observed=True)
        if item.signature in observed:continue
        if full_search(item)["graph"] is None:insert("negative",item)
    rng=random.Random(SEED+992)
    for i in range(collision_pairs):
        for j in range(10000):
            family=OOD_FAMILIES[i%len(OOD_FAMILIES)]
            item=make_case(rng,split="collision",family=family,topology=rng.choice(TOPOLOGIES),
                           graph=rng.choice(PROGRAMS),identifier=f"collision:{2*i}",pair_id=f"pair:{i}")
            if insert("collision",item):break
        else:raise RuntimeError("collision roster exhaustion")
        edited=list(item.future)
        edited[PREFIX+3]+=1 if i%2 else -1
        duplicate=replace(item,identifier=f"collision:{2*i+1}",future=tuple(edited),source_graph=None)
        assert insert("collision",duplicate,duplicate=True)
    return output


def check_candidate(case:Case,graph:Sequence[str]) -> dict:
    """Finite two-demo exact certificate, returned only after paid execution."""
    graph=tuple(graph)
    if graph not in PROGRAMS:raise ValueError("bad program")
    faults=[]
    exact=True
    for f,y in case.demos:
        prediction=execute(f[:PREFIX+1],case.topology,graph)
        mismatch=first_error(prediction,y[:PREFIX+1])
        faults.append(mismatch)
        exact &= mismatch is None
    return {"accepted":bool(exact),"first_faults":faults,"compared_coefficients":2*(PREFIX+1)}


def query_cost(case:Case,graph:Sequence[str],degree:int=PREFIX)->dict:
    """Auditable proxy for arithmetic, separate from neural MACs/elapsed time."""
    graph=tuple(graph)
    if graph not in PROGRAMS:raise ValueError("bad program")
    triangular=degree*(degree+1)//2
    unary_units=sum(triangular if op=="R" else degree+1 for op in graph)
    join=degree+1 if case.topology in ("hadamard","additive") else (degree+1)*(degree+2)//2
    return {"demo_executions":2,"primitive_calls":8,
            "integer_loop_proxy":2*(unary_units+join)}


def search(case:Case,order:Sequence[Sequence[str]],budget:int=12)->dict:
    if budget<1:raise ValueError("budget must be positive")
    seen=set()
    tested=[]
    first_fault=[]
    graph=None
    ops=0
    for item in order:
        if len(tested)>=budget:break
        candidate=tuple(item)
        if candidate not in PROGRAMS:raise ValueError("unknown candidate")
        if candidate in seen:continue
        seen.add(candidate)
        checked=check_candidate(case,candidate)
        tested.append(candidate)
        first_fault.append(checked["first_faults"])
        ops+=query_cost(case,candidate)["integer_loop_proxy"]
        if checked["accepted"]:
            graph=candidate
            break
    return {"graph":graph,"trace":tuple(tested),"queries":len(tested),
            "faults":first_fault,"integer_loop_proxy":ops}


def full_search(case:Case)->dict:
    return search(case,PROGRAMS,len(PROGRAMS))


def grade(case:Case,found:dict)->dict:
    """Future values are used here ONLY, after all candidate-selection steps."""
    graph=found["graph"]
    accepted=graph is not None
    if accepted and not check_candidate(case,graph)["accepted"]:
        raise AssertionError("unchecked acceptance")
    future=bool(accepted and execute(case.query,case.topology,graph)==case.future)
    return {"accepted":int(accepted),"future_correct":int(future),
            "false_future_acceptance":int(accepted and not future)}


def hash_roster(cases:Sequence[Case])->str:
    payload=[(c.identifier,c.split,c.family,c.topology,c.demos,c.query,c.future,c.source_graph,c.pair_id) for c in cases]
    return sha256(json.dumps(payload,separators=(',',':')).encode()).hexdigest()


def manifest(rosters:dict[str,list[Case]])->dict:
    result={"schema":VERSION,"seed":SEED,"prefix":PREFIX,"future":FUTURE,
            "dsl_programs":len(PROGRAMS),"per_split":{},"overall":{}}
    total=0
    for name,cases in rosters.items():
        total+=len(cases)
        accepted=correct=false_future=queries=0
        for case in cases:
            result_case=full_search(case)
            quality=grade(case,result_case)
            accepted+=quality["accepted"]
            correct+=quality["future_correct"]
            false_future+=quality["false_future_acceptance"]
            queries+=result_case["queries"]
        result["per_split"][name]={"cases":len(cases),"roster_sha256":hash_roster(cases),
                                   "accepted":accepted,"future_correct":correct,
                                   "false_future":false_future,"queries":queries}
    result["overall"]={"cases":total,"inference_target":"finite_coefficients",
                       "integer_arithmetic":"exact","public_model_fields":["topology","demos","query"]}
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    result=manifest(roster())
    rendered=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.check:
        if args.out is None or not args.out.is_file() or args.out.read_text()!=rendered:
            raise SystemExit("ARG-01 reference manifest absent or stale")
        print("ARG-01 EvalMath exact manifest verified")
    elif args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(rendered)
        print("saved",args.out)
    else:print(rendered,end="")

if __name__=="__main__":main()
