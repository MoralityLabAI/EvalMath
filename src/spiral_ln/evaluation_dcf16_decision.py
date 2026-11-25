"""DCF16-EVAL: scoring of compute-aware reasoning and algorithm selection.

Each record of the DCF-16 curriculum is a parity query on a binary factor graph with an explicit
compute budget 2**budget_log2_ops, reward +1 correct, -penalty wrong, 0 abstain. A prediction names an
algorithm, an action (1 = parity 1, 0 = parity 0, -1 = abstain), and optionally a probability p of
parity 1 and a claimed operation count.

Exact arithmetic: stored floats enter as Fraction(float), which is exact, and every score is a
rational. Expected utility of action a under reference posterior q is linear:
EU(1) = q - pen (1 - q), EU(0) = (1 - q) - pen q, EU(-1) = 0.
Floats appear only in the "approx" display fields produced by `jsonable`.

Algorithm names are the operator names of the record, plus "abstain" and "unary_evidence_only", which
run no inference operator and cost 0 ops. Budget compliance reads the claimed operator's ops from the
record, never from the prediction; an algorithm the record does not list is non-compliant.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from collections import defaultdict
from fractions import Fraction as Q
from math import comb
from pathlib import Path

ACTIONS = (1, 0, -1)
ZERO_COST = ("abstain", "unary_evidence_only")
ECE_BINS = 10


# ---------------------------------------------------------------- records

def load_records(path) -> list[dict]:
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def file_digests(path) -> dict:
    """SHA-256 of the file bytes and, for .gz, of the decompressed bytes."""
    path = Path(path)
    raw = path.read_bytes()
    out = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    if path.suffix == ".gz":
        out["sha256_uncompressed"] = hashlib.sha256(gzip.decompress(raw)).hexdigest()
    return out


def penalty(rec) -> Q:
    return Q(-rec["decision_rule"]["reward"]["wrong"])


def budget_ops(rec) -> int:
    return 2 ** int(rec["budget_log2_ops"])


def is_hard_negative(rec) -> bool:
    return any(rec["hard_negative"].values())


def operator_ops(rec) -> dict:
    return {o["name"]: int(o["ops"]) for o in rec["operators"]}


# ---------------------------------------------------------------- utilities

def expected_utility(action: int, q: Q, pen: Q) -> Q:
    if action == -1:
        return Q(0)
    if action not in (0, 1):
        raise ValueError(f"action {action!r} not in {ACTIONS}")
    r = q if action == 1 else 1 - q
    return r - pen * (1 - r)


def oracle_utility(q: Q, pen: Q) -> Q:
    return max(Q(0), expected_utility(1, q, pen), expected_utility(0, q, pen))


def realized_utility(action: int, truth: int, pen: Q) -> Q:
    if action == -1:
        return Q(0)
    return Q(1) if action == truth else -pen


def decide_float(p, pen) -> int:
    """Bayes action with the generator's float thresholds, used by the unary shortcut."""
    pen = float(pen)
    tau, low = pen / (1 + pen), 1 / (1 + pen)
    if p is None:
        return -1
    return 1 if p >= tau else 0 if p <= low else -1


# ---------------------------------------------------------------- predictions

def validate_predictions(records, preds) -> dict:
    """Map id -> prediction; raises ValueError unless it covers the records exactly."""
    by_id = {}
    for pr in preds:
        pid = pr.get("id")
        if pid in by_id:
            raise ValueError(f"duplicate prediction id {pid}")
        act = pr.get("action")
        if isinstance(act, bool) or act not in ACTIONS:
            raise ValueError(f"prediction {pid}: action {act!r} not in {ACTIONS}")
        if not isinstance(pr.get("algorithm"), str):
            raise ValueError(f"prediction {pid}: algorithm must be a string")
        p = pr.get("p")
        if p is not None and not (isinstance(p, (int, float)) and not isinstance(p, bool) and 0 <= p <= 1):
            raise ValueError(f"prediction {pid}: p {p!r} not in [0, 1]")
        c = pr.get("claimed_ops")
        if c is not None and not (isinstance(c, int) and not isinstance(c, bool) and c >= 0):
            raise ValueError(f"prediction {pid}: claimed_ops {c!r} not a non-negative integer")
        by_id[pid] = pr
    ids = {r["id"] for r in records}
    if len(ids) != len(records):
        raise ValueError("duplicate record ids")
    missing, extra = ids - set(by_id), set(by_id) - ids
    if missing or extra:
        raise ValueError(f"predictions must cover the records exactly: {len(missing)} missing, {len(extra)} unknown ids")
    return by_id


def algorithm_ops(rec, algorithm):
    """Counted ops of the named algorithm from the record, or None if the record lists no such operator."""
    if algorithm in ZERO_COST:
        return 0
    return operator_ops(rec).get(algorithm)


# ---------------------------------------------------------------- per-record scoring

def score_record(rec, pr) -> dict:
    pen = penalty(rec)
    q = Q(rec["verification"]["reference_p"])
    truth = int(rec["verification"]["truth_parity"])
    a = pr["action"]
    ops = algorithm_ops(rec, pr["algorithm"])
    compliant = ops is not None and ops <= budget_ops(rec)
    eu = expected_utility(a, q, pen)
    p = pr.get("p")
    claimed = pr.get("claimed_ops")
    oracle = oracle_utility(q, pen)
    return dict(
        id=rec["id"], family=rec["family"], hard_negative=is_hard_negative(rec),
        eu=eu, oracle=oracle, regret=oracle - eu,
        eu_enforced=eu if compliant else Q(0),
        realized=realized_utility(a, truth, pen),
        acted=a != -1, wrong=a != -1 and a != truth,
        alg_match=pr["algorithm"] == rec["selected"]["operator"],
        compliant=compliant, known_algorithm=ops is not None,
        claimed_ops_given=claimed is not None,
        claimed_ops_match=claimed is not None and ops is not None and claimed == ops,
        p=None if p is None else Q(p), truth=truth,
    )


def calibration(rows) -> dict:
    """Brier score and 10-bin ECE of p against truth_parity over rows that carry p."""
    pr = [r for r in rows if r["p"] is not None]
    n = len(pr)
    if n == 0:
        return dict(n_p=0, brier=None, ece=None)
    brier = sum((r["p"] - r["truth"]) ** 2 for r in pr) / n
    bins = defaultdict(list)
    for r in pr:
        bins[min(int(r["p"] * ECE_BINS), ECE_BINS - 1)].append(r)
    ece = sum(Q(len(b), n) * abs(sum(Q(x["truth"]) for x in b) / len(b) - sum(x["p"] for x in b) / len(b))
              for b in bins.values())
    return dict(n_p=n, brier=brier, ece=ece)


def aggregate(rows) -> dict:
    n = len(rows)
    if n == 0:
        return dict(n=0)
    acted = [r for r in rows if r["acted"]]

    def mean(key):
        return sum(r[key] for r in rows) / n

    out = dict(
        n=n,
        eu=mean("eu"), eu_budget_enforced=mean("eu_enforced"), realized=mean("realized"),
        oracle_eu=mean("oracle"), regret=mean("regret"),
        coverage=Q(len(acted), n),
        selective_risk=Q(sum(r["wrong"] for r in acted), len(acted)) if acted else None,
        algorithm_accuracy=Q(sum(r["alg_match"] for r in rows), n),
        budget_compliance=Q(sum(r["compliant"] for r in rows), n),
        unknown_algorithm=sum(not r["known_algorithm"] for r in rows),
        claimed_ops_given=sum(r["claimed_ops_given"] for r in rows),
        claimed_ops_match=sum(r["claimed_ops_match"] for r in rows),
    )
    out.update(calibration(rows))
    return out


def score(records, preds) -> dict:
    """Overall, hard-negative slice, its complement, per family, and the per-record rows."""
    by_id = validate_predictions(records, preds)
    rows = [score_record(r, by_id[r["id"]]) for r in records]
    fam = defaultdict(list)
    for r in rows:
        fam[r["family"]].append(r)
    return dict(
        overall=aggregate(rows),
        hard_negative=aggregate([r for r in rows if r["hard_negative"]]),
        easy=aggregate([r for r in rows if not r["hard_negative"]]),
        per_family={f: aggregate(v) for f, v in sorted(fam.items())},
        rows=rows,
    )


# ---------------------------------------------------------------- paired comparison

def sign_test_p(wins: int, losses: int) -> Q:
    """Exact two-sided sign test on the discordant records under a fair-coin null."""
    n = wins + losses
    if n == 0:
        return Q(1)
    k = min(wins, losses)
    return min(Q(1), Q(2 * sum(comb(n, j) for j in range(k + 1)), 2 ** n))


def paired(records, preds_a, preds_b) -> dict:
    """Per-record comparison of A against B; a win means A is strictly better. The sign test treats
    records as exchangeable; records of one family share structure, so read p as descriptive."""
    ra = {r["id"]: r for r in score(records, preds_a)["rows"]}
    rb = {r["id"]: r for r in score(records, preds_b)["rows"]}
    out = {}
    for key in ("eu", "realized", "alg_match"):
        diffs = {i: Q(ra[i][key]) - Q(rb[i][key]) for i in ra}
        w = sum(d > 0 for d in diffs.values())
        l = sum(d < 0 for d in diffs.values())
        fam = defaultdict(list)
        for i, d in diffs.items():
            fam[ra[i]["family"]].append(d)
        out[key] = dict(
            n=len(diffs), wins=w, losses=l, ties=len(diffs) - w - l,
            mean_diff=sum(diffs.values()) / len(diffs), sign_test_p=sign_test_p(w, l),
            per_family_mean_diff={f: sum(v) / len(v) for f, v in sorted(fam.items())},
        )
    return out


# ---------------------------------------------------------------- reference predictors (record fields only)

def predict_abstain(rec) -> dict:
    return dict(id=rec["id"], algorithm="abstain", action=-1, claimed_ops=0)


def predict_symbolic(rec) -> dict:
    """Cheapest exact operator within budget (ties: record order), else mini-bucket (mbe) within
    budget, else abstain. Acts on that operator's stored action and p."""
    cap = budget_ops(rec)
    exact = [o for o in rec["operators"] if o["exact"] and o["ops"] <= cap and o["p"] is not None]
    mbe = [o for o in rec["operators"] if o["name"] == "mbe" and o["ops"] <= cap and o["p"] is not None]
    pick = min(exact, key=lambda o: o["ops"]) if exact else (mbe[0] if mbe else None)
    if pick is None:
        return predict_abstain(rec)
    return dict(id=rec["id"], algorithm=pick["name"], action=int(pick["action"]), p=pick["p"], claimed_ops=int(pick["ops"]))


def predict_unary(rec) -> dict:
    """Decide from the unary-evidence-only posterior alone."""
    u = next(c for c in rec["candidate_representations"] if c["name"] == "unary_evidence_only")
    return dict(id=rec["id"], algorithm="unary_evidence_only", action=decide_float(u["p"], penalty(rec)),
                p=u["p"], claimed_ops=0)


REFERENCE_PREDICTORS = {"symbolic": predict_symbolic, "always_abstain": predict_abstain, "unary_shortcut": predict_unary}


# ---------------------------------------------------------------- serialisation

def jsonable(x):
    if isinstance(x, Q):
        return {"exact": str(x), "approx": round(float(x), 12)}
    if isinstance(x, dict):
        return {k: jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    return x


def report(records, preds) -> dict:
    r = score(records, preds)
    r.pop("rows")
    return r
