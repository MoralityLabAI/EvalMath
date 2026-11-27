"""Independent offline audit of BPD-COL-02 public-development receipts."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from collections import defaultdict
from statistics import fmean

SOURCE = "f1d489a000406e2d8732f4ea7a39e5473392efe2"
MODEL = "451ed48c3273ecef7ea8faaa43c31ce529763bb1"
ROLES = ("recipient", "effect_donor", "sham_donor")
ARMS = ("identity", "effect", "sham", "random", "full_donor_prefix")
PINS = {
  "__init__.py": "1f364d1bd62eae0f6538110fbfd77294c7a2692fc09a0ff07daa6959e5fb31a6",
  "cases.py": "353cc6a227669e04ec59095cbe59a0cd79ed5c34c591750244b1a2ef788f6a60",
  "interventions.py": "4eb6faacdf922c5e4458799b9cfbaa5f0a0339fd083cc15a23c61161c77f612f",
  "run_gym.py": "d7cc5d617a25c17c06c4e16e9b2faca7a579f77a566147255b47472e416fee0f",
  "scoring.py": "2b235065d5bc01c69df176e5578e3c4b9837a82dc89f462d11fbda7527c21be1",
  "streaming.py": "273d6193288be6a2e3f1b895875cca2379e6acc18631abede1831c3e8f3b639d"
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical_hash(value):
    return hashlib.sha256((json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()).hexdigest()


def integer(x, lo, hi):
    require(type(x) is int and lo <= x <= hi, "integer outside contract")
    return x


def branch(n):
    return 3 if n % 4 == 1 else 1


def step(d, n):
    n = branch(n) * n + d
    while n % 2 == 0:
        n //= 2
    return n


def basin(d, n):
    seen = {}
    while n not in seen:
        seen[n] = len(seen)
        n = step(d, n)
    return min(x for x, i in seen.items() if i >= seen[n])


def quotient(d, n):
    pending = [n % d]
    seen = set()
    while pending:
        a = pending.pop()
        if a not in seen:
            seen.add(a)
            pending.extend((2*a % d, 3*a % d))
    return min(seen)


def validate_manifest(m):
    require(m["schema"] == "BPD-COL-02/public-development-cases/v1", "manifest schema")
    require(m["manifest_sha256"] == canonical_hash({k: v for k, v in m.items() if k != "manifest_sha256"}), "manifest hash")
    require(m["specification"]["split"] == "development_only" and m["specification"]["confirmation_authorized"] is False, "exposure")
    require(m["source"]["commit"] == "b3eb33ed10485264fe7a593e3b0ace418d9f9a6d" and m["source"]["oracle_sha256"] == "24ff52171aedf890c33439896ab5e71de65d9b05d557ba61d162f3623aa5dbca", "oracle provenance")
    cases = {}
    for i, c in enumerate(m["cases"]):
        d = integer(c["d"], 1, 1025)
        h = integer(c["horizon"], 1, 2)
        tier = c["tier"]
        require(d % 4 == 1 and math.gcd(d, 6) == 1 and type(c["root_id"]) is int and c["root_id"] == d, "root")
        require(tier in ("trace", "arithmetic") and tier == m["specification"]["tier"], "tier")
        cid = f"COL3050-d{d:06d}-h{h}-{tier}"
        require(cid == c["case_id"] and cid not in cases, "case id")
        labels = c["label_map"]
        require(set(labels) == {"1", "3"} and set(labels.values()) == {"A", "B"}, "label bijection")
        ns, bs, answers = [], [], []
        for role in ROLES:
            x = c[role]
            n = integer(x["n"], 1, d)
            require(n % 2 == 1, "odd seed")
            trace = [n]
            for _ in range(h):
                trace.append(step(d, trace[-1]))
            require(x["trace"] == trace and x["future_branch"] == branch(trace[-1]), "arithmetic replay")
            answer = labels[str(branch(trace[-1]))]
            require(x["label"] == answer and x["basin"] == basin(d, n), "oracle label")
            require(c["current_observer"] == {"quotient": quotient(d, n), "branch_multiplier": branch(n)}, "observer")
            if tier == "arithmetic":
                prefix = ("For odd x, set t=3*x+d when x mod 4=1, otherwise t=x+d. "
                          "Divide t by 2 until odd; this is one step. "
                          f"Use d={d:06d}, start={n:06d}, steps={h}. ")
            else:
                prefix = ("Read the recorded odd-state trace. "
                          f"d={d:06d}; steps={h}; trace=" + " -> ".join(f"{s:06d}" for s in trace) + ". ")
            expected = prefix + f"For the final x, answer {labels['3']} if x mod 4=1, or {labels['1']} if x mod 4=3. Reply with one letter. Answer:"
            require(x["prompt"] == expected, "prompt differs from replay")
            ns.append(n)
            bs.append(x["basin"])
            answers.append(answer)
        require(len(set(ns)) == 3 and answers[0] == answers[2] and answers[0] != answers[1], "donor relation")
        require(c["all_same_basin"] is (len(set(bs)) == 1), "basin stratum")
        require(answers[0] == ("A" if i % 2 == 0 else "B"), "label assignment")
        cases[cid] = c
    roots = list(dict.fromkeys(c["d"] for c in cases.values()))
    require(1 <= len(roots) <= 32 and len(cases) == m["n_cases"] and roots == m["root_ids"] and len(roots) == m["n_roots"], "denominators")
    return cases


def number(x):
    require(type(x) in (int, float) and math.isfinite(x), "nonfinite or nonnumeric")
    return float(x)


def probs(a):
    z = a["answer_logits"]
    p = a["probabilities"]
    require(set(z) == set(p) == {"A", "B"}, "answer ids")
    z = {k: number(v) for k, v in z.items()}
    high = max(z.values())
    e = {k: math.exp(v-high) for k, v in z.items()}
    expected = {k: v/sum(e.values()) for k, v in e.items()}
    require(all(0 <= number(p[k]) <= 1 and abs(p[k]-expected[k]) <= 1e-6 for k in p), "probabilities disagree with logits")
    return expected


def audit(m, contract, records):
    cases = validate_manifest(m)
    require(contract["schema"] == "BPD-COL-02/native-streamed-run/v1" and contract["revision"] == MODEL and contract["model_id"] == "Nanbeige/Nanbeige4.2-3B", "checkpoint")
    require(contract["cases_manifest_sha256"] == m["manifest_sha256"] and contract["source_sha256"] == PINS, "frozen source")
    require(contract["loop_count"] == 2 and contract["batch_size"] == 1 and contract["max_tokens"] == 128 and contract["dtype"] == "bfloat16" and contract["use_cache"] is False, "native profile")
    require(contract["arms"] == list(ARMS) and contract["delivered_dose_relative_tolerance"] == .02 and contract["delivered_dose_absolute_tolerance"] == 1e-6 and contract["scientific_floor_answer_probability"] == .05, "scoring profile")
    indexed = {}
    for rec in records:
        cid = rec["case_id"]
        require(cid in cases and cid not in indexed and type(rec["root_id"]) is int and rec["root_id"] == cases[cid]["d"], "duplicate/foreign record")
        indexed[cid] = rec
    per = []
    for cid, c in cases.items():
        rec = indexed.get(cid)
        row = {"case_id": cid, "root_id": c["d"], "eligible": False}
        if rec is None:
            row["status"] = "not_attempted"
        elif rec["status"] in ("error", "skipped"):
            require(isinstance(rec.get("reason"), str) and bool(rec["reason"].strip()), "missing failure reason")
            row["status"] = rec["status"]
        else:
            require(rec["status"] == "completed", "unknown status")
            require(set(rec["clean"]) == set(ROLES) and set(rec["arms"]) == set(ARMS), "incomplete arms")
            clean = {k: probs(v) for k, v in rec["clean"].items()}
            arms = {k: probs(v) for k, v in rec["arms"].items()}
            for role in ROLES:
                probs(rec["clean"][role]["first_pass"])
            competence = all(clean[k][c[k]["label"]] > .5 for k in ROLES)
            doses = {}
            admitted = True
            for k, arm in rec["arms"].items():
                d = number(arm["physical_dose"])
                measured = number(arm["measured_dose"])
                require(d >= 0 and abs(d-measured) <= max(1e-6, 1e-6*d), "dose mismatch")
                require(type(arm["admission"]) is bool and arm["patch_calls"] == 1, "patch contract")
                doses[k] = d
                admitted &= arm["admission"] and number(arm["protected_readout_max_abs"]) == 0
            matched = [doses[k] for k in ("effect", "sham", "random")]
            admitted &= (doses["identity"] == 0 and min(matched) > 0
                         and max(matched)-min(matched) <= .02*max(matched)+1e-6
                         and max(abs(arms["identity"][k]-clean["recipient"][k]) for k in ("A","B")) <= 1e-6)
            label = c["effect_donor"]["label"]
            shifts = {k: arms[k][label]-clean["recipient"][label] for k in ARMS}
            row.update(status="completed", competent=competence, instrument_admitted=admitted,
                       eligible=competence and admitted, contrast=shifts["effect"]-max(abs(shifts["sham"]), abs(shifts["random"])), shifts=shifts)
        per.append(row)
    roots = defaultdict(list)
    for row in per:
        roots[row["root_id"]].append(row)
    means = {str(d): fmean(x["contrast"] for x in rs) for d, rs in roots.items() if all(x["eligible"] for x in rs)}
    return {"verdict": "PILOT_ONLY", "source": SOURCE, "n_units": len(roots),
            "n_eligible_units": len(means), "n_cases": len(per), "n_attempted_cases": len(indexed),
            "n_completed_cases": sum(x["status"] == "completed" for x in per),
            "n_eligible_cases": sum(x["eligible"] for x in per),
            "primary_root_mean": fmean(means.values()) if means else None,
            "root_means": means, "per_case": per, "matched_sham_floor": None,
            "scope": "offline arithmetic and numerical receipt consistency; runtime assertions are not independently authenticated"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    p = args.run
    m = json.loads((p/"cases_manifest.json").read_text(encoding="utf-8"))
    c = json.loads((p/"run_contract.json").read_text(encoding="utf-8"))
    f = p/"records.jsonl"
    records = [json.loads(line) for line in f.read_text(encoding="utf-8").splitlines()] if f.exists() else []
    result = audit(m, c, records)
    summary = json.loads((p/"summary.json").read_text(encoding="utf-8"))
    for key in ("n_units", "n_eligible_units", "n_cases", "n_attempted_cases", "n_completed_cases", "n_eligible_cases"):
        require(result[key] == summary[key], "summary mismatch: "+key)
    x, y = result["primary_root_mean"], summary["primary_root_mean"]
    require((x is None and y is None) or (x is not None and y is not None and abs(x-y) <= 1e-6), "summary contrast mismatch")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
