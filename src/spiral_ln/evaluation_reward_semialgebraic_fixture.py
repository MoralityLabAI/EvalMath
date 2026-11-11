"""RHT-19: explicitly registered higher-degree q-affine proxy/gold surfaces.

For d repeated globally shared Bernoulli(p) successes, the protected
policy's proxy expectation is p**d. Gold is earned by an independent
p-success followed by a q-failure, with an optional 1/2 safe-world mass
from the registered reachable UGC pair. The competing policy's proxy is q.

The finite surface roster is explicit, so policy completeness must be
licensed outside this fixture (the two-action first-decision protocol).
"""
from fractions import Fraction as Q

from spiral_ln.evaluation_reward_two_kernel import BiPoly,PolicySurface
from spiral_ln.evaluation_reward_hacking_adaptive_feedback import one_hot_ugc_disclosure_game


def higher_degree_parabolic_surfaces(*,degree=4,ugc_worlds=False,
                                      extra_tangent=False):
    if type(degree) is not int or degree < 2 or degree > 12:
        raise ValueError("higher-degree fixture supports degree 2..12")
    p=BiPoly(((1,0,Q(1)),))
    q=BiPoly(((0,1,Q(1)),))
    pd=BiPoly(((degree,0,Q(1)),))
    gold=p-p*q
    if ugc_worlds:
        worlds=one_hot_ugc_disclosure_game(2)
        if not (worlds.unsafe(0,0) and not worlds.unsafe(1,0)):
            raise AssertionError("registered reachable UGC worlds changed")
        gold=gold.scale(Q(1,2))
    output=[PolicySurface("protected_gold",pd,BiPoly(),(gold,)),
            PolicySurface("proxy_only",q,BiPoly(),(BiPoly(),))]
    if extra_tangent:
        output.append(PolicySurface("parabolic_tie_only",
            (pd+q).scale(Q(1,2)),BiPoly(),(BiPoly(),)))
    return tuple(output)