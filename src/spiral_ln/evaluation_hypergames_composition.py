"""HG-06: exact GF(2) fragment-cover and finite-label identification mathematics.

Algebraic claims concern uniform binary inputs, parity functions and a fixed
feature library, never real agents, quantum states or unsampled outcomes.
"""
from __future__ import annotations

from fractions import Fraction as Q
from itertools import combinations, product
from math import comb

from spiral_ln.evaluation_hypergames_rank import deficiency, exact_joint_success, rank


def fragment_weight_floor(target: int, max_feature_weight: int) -> int:
    """Necessary number of XOR summands with row weights <= max_feature_weight."""
    if type(target) is not int or target < 0 or type(max_feature_weight) is not int or max_feature_weight < 1:
        raise ValueError("integer nonnegative target and positive feature weight required")
    return (target.bit_count() + max_feature_weight - 1) // max_feature_weight


def exact_shortest_xor(target: int, candidate_rows, dimension: int, max_rows: int = 5):
    """Independent finite-support subset oracle; use for small tests only."""
    rows = tuple(candidate_rows)
    if (type(dimension) is not int or dimension < 0 or type(max_rows) is not int or max_rows < 0
            or len(rows) > 24 or any(type(r) is not int or r < 0 or r >> dimension for r in (target,*rows))):
        raise ValueError("invalid exact finite fragment problem")
    for n in range(min(len(rows),max_rows)+1):
        for idx in combinations(range(len(rows)),n):
            code=0
            for i in idx:code ^= rows[i]
            if code == target:
                return idx
    return None


def short_fragment_certificate(target: int, candidate_rows, dimension: int, budget: int):
    """Conservative impossibility certificate followed by exact oracle for finite instances."""
    rows=tuple(candidate_rows)
    if type(budget) is not int or budget < 0 or any(type(x) is not int or x <= 0 for x in rows):
        raise ValueError("valid positive candidate rows and nonnegative budget required")
    bound = fragment_weight_floor(target, max((x.bit_count() for x in rows),default=1))
    return {"lower_bound":bound, "weight_obstructed":budget < bound,
            "witness":exact_shortest_xor(target,rows,dimension,budget)}


def parity_disagreement_probability(row_a: int,row_b: int, dimension:int, sample_count:int) -> Q:
    """Independent uniform examples agree with two distinct parities with probability 2^-n."""
    if (type(sample_count) is not int or sample_count < 0 or type(dimension) is not int or dimension < 0
            or any(type(r) is not int or r < 0 or r >> dimension for r in (row_a,row_b))):
        raise ValueError("invalid parity collision probability")
    return Q(1) if row_a == row_b else Q(1,1 << sample_count)


def independent_parity_collision(row_a:int,row_b:int, dimension:int, n:int) -> Q:
    """Exhaustive oracle, limited to d<=5 and at most 3 independent samples."""
    if type(dimension) is not int or not 0 <= dimension <= 5 or type(n) is not int or not 0 <= n <= 3:
        raise ValueError("finite enumerator bound exceeded")
    if any(type(r) is not int or r < 0 or r >> dimension for r in (row_a,row_b)):
        raise ValueError("row outside dimension")
    alphabet=tuple(range(1<<dimension))
    good=sum(all(((x & row_a).bit_count() ^ (x & row_b).bit_count()) % 2 == 0
                 for x in seq) for seq in product(alphabet, repeat=n))
    return Q(good,len(alphabet)**n)


def spurious_fit_union_bound(n_candidates:int, n_outputs:int, train_n:int, signed:bool=True) -> Q:
    """Probability bound for ANY spurious signed parity matching a true one on all training rows.

    Applies to a fixed candidate family chosen independently of the training inputs.
    The bound is capped at 1 and can be vacuous; it is not an empirical p value.
    """
    if any(type(v) is not int or v < 0 for v in (n_candidates,n_outputs,train_n)):
        raise ValueError("nonnegative integer counts required")
    if type(signed) is not bool:
        raise ValueError("signed flag must be boolean")
    alternative_count=max(0,(2 if signed else 1)*n_candidates-1)
    return min(Q(1),Q(n_outputs*alternative_count,1<<train_n))


def exact_signed_candidates(masks, labels, training_inputs, dimension:int):
    """Uniform-prior posterior support of affine parity hypotheses from pick-time labels."""
    rows=tuple(masks)
    xs=tuple(training_inputs)
    ys=tuple(labels)
    if len(xs)!=len(ys) or len(set(rows))!=len(rows):
        raise ValueError("invalid prior candidate set or training record")
    if any(type(z) is not int or z < 0 or z >> dimension for z in (*xs,*rows)) or any(type(y) is not int or y not in (0,1) for y in ys):
        raise ValueError("binary inputs and labels required")
    return tuple((r,bias) for r in rows for bias in (0,1)
                 if all(((x&r).bit_count()&1)^bias==y for x,y in zip(xs,ys)))


def posterior_joint_predictive_accuracy(candidates, dimension:int) -> Q:
    """Bayes optimal fresh-item accuracy for a uniform posterior over signed parity candidates."""
    posterior=tuple(candidates)
    if not posterior or type(dimension) is not int or not 0 <= dimension <= 10:
        raise ValueError("nonempty posterior and small dimension required")
    if any(type(r) is not int or r < 0 or r >> dimension or b not in (0,1) for r,b in posterior):
        raise ValueError("invalid posterior parity")
    right=0
    for x in range(1 << dimension):
        counts=[0,0]
        for r,b in posterior:
            counts[((x&r).bit_count()&1)^b]+=1
        right+=max(counts)
    return Q(right,(1<<dimension)*len(posterior))


def certified_joint_goal_capacity(observations, goals,dimension:int) -> dict:
    c=tuple(observations);p=tuple(goals)
    h=deficiency(c,p,dimension)
    return {"goal_rank":rank(p,dimension),"observer_rank":rank(c,dimension),
            "remaining_entropy_bits":h,"optimal_joint_success":exact_joint_success(c,p,dimension)}
