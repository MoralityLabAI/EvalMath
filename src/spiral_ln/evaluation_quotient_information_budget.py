"""QI-02: adaptive Bernoulli experiment information budgets, finite oracle.

Classical chain-rule / change-of-measure lower bound specialized to
addressable state-action probe cells. Every cell has a fixed iid Bernoulli
stream. The policy is deterministic and chooses each next cell from past
observations; a randomized policy is handled mathematically by conditioning
on an independent random tape, but this exact oracle tests deterministic trees.

No model training, external inference, or neural-mechanism measurement.
"""

from fractions import Fraction as Q
from math import ceil, log, sqrt


def bernoulli_kl(p, q):
    """D(Bern(p)||Bern(q)) with proper endpoint limits."""
    p, q = float(p), float(q)
    if not (0 <= p <= 1 and 0 <= q <= 1):
        raise ValueError("probabilities must be in [0,1]")
    if p == q:
        return 0.0
    if (q == 0 and p > 0) or (q == 1 and p < 1):
        return float("inf")
    return ((p * log(p / q) if p > 0 else 0.0)
            + ((1 - p) * log((1 - p) / (1 - q)) if p < 1 else 0.0))


def binary_event_kl(prob0, prob1):
    return bernoulli_kl(prob0, prob1)


def expected_diagnostic_cell_lower_bound(p0, p1, delta):
    """Lower bound on E0[N_c] for errors <= delta in both worlds.

    Worlds differ at exactly one cell with Bernoulli rates p0,p1, which
    are strictly between 0 and 1. Conditional sampling is predictable,
    and eventual decision/stopping are measurable in the transcript.
    """
    a = float(delta)
    if not 0 < a < .5:
        raise ValueError("delta must be in (0,1/2)")
    if not (0 < float(p0) < 1 and 0 < float(p1) < 1
            and float(p0) != float(p1)):
        raise ValueError("distinct interior Bernoulli rates required")
    return binary_event_kl(1 - a, a) / bernoulli_kl(p0, p1)


def expected_probe_integer_floor(p0, p1, delta):
    """Necessary integer upper bound on expected probes, when each path
    is uniformly limited to N: N >= ceil(KL target / KL per sample).
    """
    return ceil(expected_diagnostic_cell_lower_bound(p0, p1, delta) - 1e-12)


def paired_adaptive_transcript(world0, world1, policy, max_steps):
    """Exact transcript probabilities and expected draws, with float KL audit.

    The same policy maps the public history tuple ((cell,bit),...) to
    either the next cell index or None. It cannot inspect world identity.
    """
    p = tuple(Q(x) for x in world0)
    q = tuple(Q(x) for x in world1)
    if len(p) != len(q) or not p:
        raise ValueError("worlds must have matching nonempty probe cells")
    if any(not 0 < z < 1 for z in p + q):
        raise ValueError("finite KL oracle requires interior Bernoulli rates")
    if type(max_steps) is not int or max_steps < 0:
        raise ValueError("nonnegative integer max_steps required")
    counts = [Q(0) for _ in p]
    leaves = {}

    def recurse(history, mass0, mass1):
        action = None if len(history) == max_steps else policy(history)
        if action is None:
            if history in leaves:
                raise AssertionError("repeated leaf")
            leaves[history] = (mass0, mass1)
            return
        if type(action) is not int or not 0 <= action < len(p):
            raise ValueError("policy requested an invalid probe")
        counts[action] += mass0
        for outcome in (0, 1):
            prob0 = p[action] if outcome else 1 - p[action]
            prob1 = q[action] if outcome else 1 - q[action]
            recurse(history + ((action, outcome),),
                    mass0*prob0, mass1*prob1)

    recurse((), Q(1), Q(1))
    assert sum((x for x, _ in leaves.values()), Q(0)) == 1
    assert sum((x for _, x in leaves.values()), Q(0)) == 1
    transcript_kl = sum(float(a)*log(float(a/b)) for a,b in leaves.values())
    decomposed_kl = sum(float(counts[i])*bernoulli_kl(p[i], q[i])
                        for i in range(len(p)))
    return {
        "transcripts": leaves,
        "expected_cell_queries_under_world0": tuple(counts),
        "transcript_KL": transcript_kl,
        "decomposed_KL": decomposed_kl,
        "KL_chain_rule_residual": transcript_kl - decomposed_kl,
    }


def event_probability_by_world(transcript_result, event):
    """Probability of a public terminal decision under each candidate world."""
    laws = transcript_result["transcripts"]
    p = sum((a for hist,(a,b) in laws.items() if event(hist)), Q(0))
    q = sum((b for hist,(a,b) in laws.items() if event(hist)), Q(0))
    return p, q


def pinsker_transcript_upper(transcript_result):
    """Pinsker upper bound on transcript total-variation distance."""
    return min(1., sqrt(max(0., transcript_result["transcript_KL"]) / 2))


def exact_transcript_total_variation(transcript_result):
    return float(sum((abs(p - q)
                      for p,q in transcript_result["transcripts"].values()), Q(0)) / 2)
