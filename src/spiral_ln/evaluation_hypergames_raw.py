"""HG-07 exact F2 raw-state parity observability and synthetic baseline.

All arithmetic is integer/rational.  This module exposes no labels from held-out
splits to fitting. Pivots are most-significant set bits and encode a rowspace
basis with the corresponding XOR of observed target labels.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as Q
from math import comb
from spiral_ln.evaluation_hypergames_rank import rank, deficiency


def sparse_collision_union_bound(d: int, width: int, n: int) -> Q:
    """Union bound for any incorrect fixed width-sparse parity matching n labels.

    Returns an upper bound truncated to probability one. It is not a tight
    probability and makes no claim about a neural algorithm.
    """
    if not all(type(v) is int for v in (d,width,n)) or d < 1 or not (0 <= width <= d) or n < 0:
        raise ValueError('invalid sparse class or training budget')
    return min(Q(1), Q(max(0, comb(d,width)-1), 2**n))


def parity_mask(x: int, mask: int) -> int:
    if type(x) is not int or type(mask) is not int or min(x,mask) < 0:
        raise ValueError('nonnegative integer binary masks required')
    return (x & mask).bit_count() & 1


@dataclass(frozen=True)
class F2Rowspace:
    dimension: int
    pivot_rows: tuple[tuple[int,int], ...]
    rank: int
    output_rank: int

    def predict_if_identified(self, x: int) -> int | None:
        if type(x) is not int or x < 0 or x >> self.dimension:
            raise ValueError('query vector outside the world')
        code=0
        for row,value in self.pivot_rows:
            pivot=1 << (row.bit_length()-1)
            if x & pivot:
                x ^= row
                code ^= value
        return code if x==0 else None


def fit_raw_system(inputs: tuple[int, ...], labels: tuple[int, ...], dimension: int, outputs: int) -> F2Rowspace:
    """Exact Gaussian elimination; no test or calibration labels accepted here."""
    if (type(dimension) is not int or dimension<1 or type(outputs) is not int or outputs<1
            or len(inputs)!=len(labels) or any(type(x) is not int or x<0 or x >> dimension for x in inputs)
            or any(type(y) is not int or y<0 or y >> outputs for y in labels)):
        raise ValueError('invalid linear system')
    pivot_dict={}
    for row,y in zip(inputs,labels):
        while row:
            pivot=row.bit_length()-1
            if pivot in pivot_dict:
                other,other_y=pivot_dict[pivot]
                row ^= other
                y ^= other_y
            else:
                pivot_dict[pivot]=(row,y)
                break
        if not row and y:
            raise ValueError('inconsistent parity labels')
    pivots=tuple(pivot_dict[k] for k in sorted(pivot_dict,reverse=True))
    # Predictive output rank concerns observed outputs, not model-class rank.
    return F2Rowspace(dimension,pivots,len(pivots),rank(tuple(y for _,y in pivots),outputs))


def observation_goal_floor(observation_rows:tuple[int,...],goal_rows:tuple[int,...],dimension:int)->Q:
    """Exact optimal joint goal success given Cx for uniform x and fixed P."""
    return Q(1,2**deficiency(observation_rows,goal_rows,dimension))


def design_posterior_cardinality(observation_rows:tuple[int,...],dimension:int,outputs:int=1)->int:
    """Number of unrestricted parity matrices consistent with one labelled design."""
    if type(outputs) is not int or outputs<1:
        raise ValueError('positive output count required')
    return 1 << ((dimension-rank(observation_rows,dimension))*outputs)


def identified_fraction_uniform_query(observation_rows: tuple[int,...], dimension: int) -> Q:
    """Fraction of all future x whose parity label is uniquely determined by design."""
    return Q(1,1 << (dimension-rank(observation_rows,dimension)))


def independent_fit_predict(inputs:tuple[int,...],labels:tuple[int,...],queries:tuple[int,...],d:int,k:int):
    """Exhaustive independent linear-combination reference for <=16 examples."""
    if len(inputs)>16: raise ValueError('independent checker limited to 16 examples')
    if len(inputs)!=len(labels):raise ValueError('length mismatch')
    table={0:0}
    for x,y in zip(inputs,labels):
        nxt=dict(table)
        for u,v in table.items():
            w=u^x; z=v^y
            if w in nxt and nxt[w]!=z:raise ValueError('inconsistent')
            nxt[w]=z
        table=nxt
    return tuple(table.get(x) for x in queries)
