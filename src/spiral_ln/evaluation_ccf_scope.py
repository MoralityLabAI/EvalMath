"""CCF-04: declared synthetic receipt obligations, not a proof verifier."""
from fractions import Fraction as F


def scope_ok(endpoint, *, n, p=2, eps=1, delta=1, radius=1,
             a=2, b=10, alpha=1, schwartz=True, memlp=True, kakeya=True):
    """Rational instances of the six pinned comparator hypotheses.

    None denotes infinity only for the extended exponents p (BR) and a.
    Membership predicates are externally attested, not computed here.
    """
    if type(n) is not int or n < 2:
        return False
    if endpoint == 'euclidean_local_smoothing':
        return p is not None and p >= 2 and (eps > 0 or p == 2 and eps == 0) and schwartz
    if endpoint == 'bochner_riesz':
        return (p is None or p >= 1) and delta > max(n * abs((F(0) if p is None else 1/F(p))-F(1,2))-F(1,2), 0) and radius > 0 and schwartz
    if endpoint == 'spherical_restriction':
        return (a is None or a > 1) and b > F(2*n,n-1) and b > F(n+1,n-1)*(1 if a is None else F(a)/(F(a)-1)) and memlp
    if endpoint == 'kakeya_maximal':
        return eps > 0 and 0 < delta <= 1 and memlp
    if endpoint == 'kakeya':
        return kakeya
    if endpoint == 'stein_square':
        return p is not None and p >= 2 and alpha > max(F(1,2), n*(F(1,2)-1/F(p))) and schwartz
    return False


GATES = ('registered_request', 'trusted_commitment', 'request_identity', 'in_scope_config',
         'exact_match', 'full_coverage', 'accepted_verification', 'artifact_identity',
         'translation_attested', 'solution_kernel_attested', 'theorem_scope', 'frozen_contract')


def authorize(gates):
    """A deliberately strict evaluation policy over independently attested facts."""
    return all(gates.get(name) is True for name in GATES)


def accuracy_interval(total, verified, correct_verified):
    """Sharp finite bounds given trustworthy labels and a registered denominator."""
    if not 0 <= correct_verified <= verified <= total or total <= 0:
        raise ValueError('invalid counts')
    return F(correct_verified, total), F(correct_verified + total - verified, total)
