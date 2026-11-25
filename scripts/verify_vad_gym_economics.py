"""VAD-11E: measured amortization economics and research-selection policies on the kernel-verified gym.

Replays the measured in-Lean work (work_ms of each kernel-checked file) recorded in the VAD-11 receipt.
A session is the frozen test targets of one family in seed order. Calibration instances of the same family
are the development data. Lemma build costs are the measured work_ms of the library units; a target proved
with S_lemma needs the lemma units it imports. Nothing here runs Lean; every number is a replay of kernel
runs recorded in the receipt. Process start-up (about 1.5-2.5 s per file here) is excluded from work_ms and
reported separately as verifier calls.
"""
import argparse
import itertools
import json
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
TC = "4.35.0"


def load(path):
    d = json.loads(Path(path).read_text())
    lib = {k: v["results"][TC]["work_ms"] for k, v in d["library"].items()}
    fam = {}
    for i in d["instances"]:
        s = i["strategies"]
        base = "S_decide" if "S_decide" in s else "S_direct"  # F5 has no brute-force strategy; direct omega/mul chain
        if not (s.get(base, {}).get(TC, {}).get("ok") and s.get("S_lemma", {}).get(TC, {}).get("ok")):
            continue
        fam.setdefault(i["family"], {"cal": [], "test": []})[i["split"]].append(dict(
            id=i["id"], seed=i["seed"], decide=s[base][TC]["work_ms"], lemma=s["S_lemma"][TC]["work_ms"],
            need=frozenset(s["S_lemma"][TC]["imports"])))
    for f in fam.values():
        for k in f:
            f[k].sort(key=lambda r: r["seed"])
    return d, lib, fam


def cost_with(targets, built, lib, build_on_demand=False):
    """Total work for targets given a prebuilt set; optionally build missing lemmas when first needed."""
    built = set(built)
    total = sum(lib[l] for l in built)
    for t in targets:
        if t["need"] <= built:
            total += t["lemma"]
        elif build_on_demand:
            miss = t["need"] - built
            total += sum(lib[l] for l in miss) + t["lemma"]
            built |= miss
        else:
            total += t["decide"]
    return total


def select_greedy(k, cal, lib, pool, max_size=6):
    """Add the best set of up to k lemmas at a time while calibration net saving improves."""
    built, best = frozenset(), cost_with(cal, frozenset(), lib)
    while len(built) < max_size:
        cand = None
        for r in range(1, k + 1):
            for add in itertools.combinations(sorted(pool - built), r):
                c = cost_with(cal, built | set(add), lib)
                if c < best and (cand is None or c < cand[0]):
                    cand = (c, frozenset(add))
        if cand is None:
            break
        best, built = cand[0], built | cand[1]
    return built


def select_support(cal, lib, threshold=2):
    cnt = {}
    for t in cal:
        for l in t["need"]:
            cnt[l] = cnt.get(l, 0) + 1
    return frozenset(l for l, c in cnt.items() if c >= threshold)


def bayes_online(test, cal, lib):
    """Beta posteriors over each lemma's per-target use probability, seeded by calibration counts; build a target's
    missing lemmas when expected remaining savings exceed build cost (per-use saving estimated from calibration)."""
    uses, n = {}, len(cal)
    for t in cal:
        for l in t["need"]:
            uses[l] = uses.get(l, 0) + 1
    gains = [t["decide"] - t["lemma"] for t in cal] or [0]
    per_use = max(0.0, sum(gains) / len(gains))
    built, total, seen = set(), 0.0, 0
    for idx, t in enumerate(test):
        remaining = len(test) - idx
        miss = t["need"] - built
        if miss:
            p = min((uses.get(l, 0) + 1) / (n + seen + 2) for l in miss)  # joint use prob (lower bound)
            if p * remaining * per_use > sum(lib[l] for l in miss):
                total += sum(lib[l] for l in miss)
                built |= miss
        total += t["lemma"] if t["need"] <= built else t["decide"]
        for l in t["need"]:
            uses[l] = uses.get(l, 0) + 1
        seen += 1
    return total, built


def oracle_best(test, lib, pool, max_size=6):
    best_c, best = cost_with(test, frozenset(), lib), frozenset()
    pool = sorted(pool)
    for r in range(1, min(max_size, len(pool)) + 1):
        if len(pool) > 14 and r > 3:
            break
        for add in itertools.combinations(pool, r):
            c = cost_with(test, frozenset(add), lib)
            if c < best_c:
                best_c, best = c, frozenset(add)
    return best_c, best


def run(path):
    d, lib, fam = load(path)
    out = {"protocol": "VAD-11E", "evidence": "replay of measured kernel-checked work_ms; no Lean executed",
           "receipt_sha256": sha256(Path(path).read_bytes()).hexdigest(), "toolchain": TC, "families": {}}
    pooled = {}
    for f, sp in sorted(fam.items()):
        cal, test = sp["cal"], sp["test"]
        if not cal or not test:
            continue
        pool = frozenset(l for t in cal + test for l in t["need"])
        direct = cost_with(test, frozenset(), lib)
        row = {"n_cal": len(cal), "n_test": len(test), "verifier_calls_per_session": len(test),
               "direct_ms": direct,
               "mean_saving_per_target_ms": sum(t["decide"] - t["lemma"] for t in test) / len(test),
               "lemma_units_needed": len(pool), "all_build_ms": sum(lib[l] for l in pool)}
        pols = {
            "direct": direct,
            "retrieval_on_demand": cost_with(test, frozenset(), lib, build_on_demand=True),
            "support_graph": cost_with(test, select_support(cal, lib), lib),
            "greedy0": cost_with(test, select_greedy(1, cal, lib, pool), lib),
            "lookahead2": cost_with(test, select_greedy(2, cal, lib, pool), lib),
            "lookahead3": cost_with(test, select_greedy(3, cal, lib, pool), lib),
            "bayes_online": bayes_online(test, cal, lib)[0],
            "oracle_prebuilt_set": oracle_best(test, lib, pool)[0],
        }
        row["policies_ms"] = pols
        row["gain_vs_direct"] = {k: direct / v if v else None for k, v in pols.items()}
        sav = row["mean_saving_per_target_ms"]
        row["break_even_horizon_all_lemmas"] = (row["all_build_ms"] / sav) if sav > 0 else None
        out["families"][f] = row
        for k, v in pols.items():
            pooled[k] = pooled.get(k, 0) + v
    out["pooled_ms"] = pooled
    out["pooled_gain_vs_direct"] = {k: pooled["direct"] / v for k, v in pooled.items()}
    out["source_sha256"] = {"verify_vad_gym_economics.py": sha256(Path(__file__).read_bytes()).hexdigest()}
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--receipt", type=Path, default=HERE.parent / "output/verified_abstraction/vad_11_gym.json")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    r = run(a.receipt)
    a.out.write_text(json.dumps(r, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"pooled_gain_vs_direct": r["pooled_gain_vs_direct"],
                      "break_even": {f: v["break_even_horizon_all_lemmas"] for f, v in r["families"].items()}}, indent=1))
