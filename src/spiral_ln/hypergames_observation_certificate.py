"""Exact sufficient GF(2) certificate from public sparse-parity observations.

Rows (a,y) assert a dot p_j = y_j over GF(2). Known weight w contributes
the all-ones row with response w mod 2. If a unit row e_i is in their span
with response 1 for output j, every compatible goal has p_j[i]=1. Exactly
w distinct such coordinates determine the complete weight-w support, so
all future parity decisions are fixed. This is sufficient, not necessary.
It certifies information in a transcript, not a model's internal mechanism.
"""
from __future__ import annotations


def certify(dimension, goal_rank, transcript, claimed_supports, width=6):
    if type(dimension) is not int or dimension < 1 or type(goal_rank) is not int or goal_rank < 1:
        raise ValueError('positive dimension and rank required')
    if type(width) is not int or not 0 <= width <= dimension:
        raise ValueError('invalid known weight')
    pivots = {}
    equations = []

    def reduce(row, code):
        while row:
            p = row.bit_length()-1
            if p not in pivots: break
            old, y = pivots[p]
            row ^= old
            code ^= y
        return row, code

    def add(mask, response):
        if type(mask) is not int or mask < 0 or mask >> dimension:
            raise ValueError('invalid intervention mask')
        if len(response) != goal_rank or any(type(b) is not int or b not in (0,1) for b in response):
            raise ValueError('invalid response vector')
        code = sum(b << j for j,b in enumerate(response))
        row, y = reduce(mask, code)
        if not row:
            if y: raise ValueError('inconsistent parity equations')
        else: pivots[row.bit_length()-1] = row, y

    for mask,response in transcript:
        add(mask,response)
        equations.append((mask,tuple(response)))
    add((1 << dimension)-1,[width % 2]*goal_rank)
    positives = [set() for _ in range(goal_rank)]
    for i in range(dimension):
        residual, code = reduce(1 << i,0)
        if residual == 0:
            for j in range(goal_rank):
                if code >> j & 1: positives[j].add(i)
    overfull = any(len(row) > width for row in positives)
    if claimed_supports is None:
        consistent = False
        valid_claim = False
    else:
        valid_claim = (len(claimed_supports) == goal_rank and all(
            type(m) is int and m >= 0 and not m >> dimension and m.bit_count() == width
            for m in claimed_supports))
        consistent = valid_claim and all(tuple((a & m).bit_count() & 1 for m in claimed_supports) == y
                                         for a,y in equations)
    complete = not overfull and all(len(row) == width for row in positives)
    match = valid_claim and all(m == sum(1 << i for i in row)
                                for m,row in zip(claimed_supports,positives))
    return {'method':'public_GF2_rowspace_plus_known_exact_sparsity',
            'equation_rank_including_known_weight_parity':len(pivots),
            'linearly_forced_positive_counts':list(map(len,positives)),
            'complete_support_forced':complete,
            'claim_matches_all_observed_deltas':bool(consistent),
            'release_certified_by_public_transcript':bool(complete and match and consistent),
            'known_sparsity_inconsistent':overfull}
