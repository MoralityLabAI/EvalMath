"""Exact certificate-cost score intervals for externally checked proofs."""
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class CostBounds:
    root: str
    profile: str
    lower: int
    upper: int | None = None

    def __post_init__(self):
        if not self.root or not self.profile:
            raise ValueError('missing identity')
        if type(self.lower) is not int or self.lower < 1:
            raise ValueError('invalid lower bound')
        if self.upper is not None and (type(self.upper) is not int or self.upper < self.lower):
            raise ValueError('invalid reference upper bound')


@dataclass(frozen=True)
class CheckedCost:
    root: str
    profile: str
    cost: int


def interval(bounds: CostBounds, checked: CheckedCost | None):
    """Inputs must originate in independent checker custody, not model JSON.

    None is a failed/invalid/absent certificate, scored zero. Positive integer
    cost is assumed. Bounds refer to the same root and cost function.
    """
    if checked is None:
        return Fraction(0), Fraction(0)
    if (checked.root, checked.profile) != (bounds.root, bounds.profile):
        raise ValueError('root or cost-profile mismatch')
    c = checked.cost
    if type(c) is not int or c < bounds.lower:
        raise ValueError('cost contradicts admissible bound')
    upper = min(c, bounds.upper) if bounds.upper is not None else c
    return Fraction(bounds.lower, c), Fraction(upper, c)


def aggregate(rows):
    """Equal weight per distinct evaluation root, including failures."""
    ids = set()
    lo = hi = Fraction(0)
    solved = count = 0
    profile = None
    for bounds, checked in rows:
        if profile is None:
            profile = bounds.profile
        if bounds.profile != profile or bounds.root in ids:
            raise ValueError('mixed cost profiles or duplicate roots')
        ids.add(bounds.root)
        a, b = interval(bounds, checked)
        lo += a
        hi += b
        solved += int(checked is not None)
        count += 1
    if count == 0:
        raise ValueError('empty evaluation')
    return {'roots': count, 'solved': solved, 'coverage': Fraction(solved, count),
            'efficiency_lower': lo / count, 'efficiency_upper': hi / count}
