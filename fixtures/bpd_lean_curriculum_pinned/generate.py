"""BPD-LG-01: reproducible source-owned Lean witness/countermodel task family.

Generated source is a conjectured Lean syntax fixture until a pinned `lean`
compiler actually checks the positive theorem scripts. Negative cases are
independently witnessed by finite countermodels, never emitted as sorry.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "BPD-LG-01-v1"
FAMILIES = ("exact", "rw", "rcases", "induction")
DEPTHS = (1, 2, 3, 4)
ROOTS = tuple(range(6))


def split_of(root: int) -> str:
    if root in (0, 1, 2, 3):
        return "train"
    return "dev" if root == 4 else "test"


def mk_case(family: str, depth: int, root: int, critical: bool, nuisance: bool) -> dict:
    if family not in FAMILIES or depth not in DEPTHS or root not in ROOTS:
        raise ValueError("unsupported family/depth/root")
    stem = f"bpd_{family}_d{depth}_r{root}_{int(critical)}_{int(nuisance)}"
    name = "thm_" + stem
    extra = " (noise : Nat)" if nuisance else ""
    proof = None
    countermodel = None
    if family == "exact":
        props = " ".join(f"P{i}" for i in range(depth + 1))
        hyps = "" if not critical else " (h0 : P0)"
        hyps += "".join(f" (h{i} : P{i-1} → P{i})" for i in range(1, depth + 1))
        statement = f"theorem {name} ({props} : Prop){hyps}{extra} : P{depth} := by"
        if critical:
            term = "h0"
            for i in range(1, depth + 1):
                term = f"h{i} ({term})"
            proof = "  exact " + term
        else:
            countermodel = {"P_values": [False] * (depth + 1), "goal": False}
    elif family == "rw":
        a, b = "a", "b"
        for _ in range(depth):
            a, b = f"Nat.succ ({a})", f"Nat.succ ({b})"
        hyp = " (hEq : a = b)" if critical else ""
        statement = f"theorem {name} (a b : Nat){hyp}{extra} : {a} = {b} := by"
        if critical:
            proof = "  rw [hEq]"
        else:
            countermodel = {"a": 0, "b": 1, "goal": False}
    elif family == "rcases":
        props = " ".join(f"P{i}" for i in range(depth + 1))
        nested = f"P{depth}"
        for j in reversed(range(depth)):
            nested = f"(P{j} ∧ {nested})"
        hyp = f" (h : {nested})" if critical else ""
        statement = f"theorem {name} ({props} : Prop){hyp}{extra} : P{depth} := by"
        if critical:
            lines = []
            previous = "h"
            for i in range(depth):
                nxt = f"tail{i}"
                lines.append(f"  rcases {previous} with ⟨_, {nxt}⟩")
                previous = nxt
            proof = "\n".join(lines + [f"  exact {previous}"])
        else:
            countermodel = {"P_values": [False] * (depth + 1), "goal": False}
    else:
        fn = "fn_" + stem
        initial = "0" if critical else "1"
        definition = (f"private def {fn} : Nat → Nat\n"
                      f"  | 0 => {initial}\n"
                      f"  | n + 1 => Nat.succ ({fn} n)\n")
        expr = "n"
        for _ in range(depth):
            expr = f"{fn} ({expr})"
        statement = f"theorem {name}{extra} : ∀ n : Nat, {expr} = n := by"
        if critical:
            proof = (f"  intro n\n  induction n with\n"
                     f"  | zero => rfl\n"
                     f"  | succ n ih =>\n"
                     f"    simpa only [{fn}] using congrArg Nat.succ ih")
        else:
            countermodel = {"n": 0, "actual_at_zero": depth, "goal": False}
        statement = definition + "\n" + statement
    return {
        "schema": SCHEMA, "case_id": stem,
        "root_id": f"{family}-d{depth}-r{root}", "split": split_of(root),
        "family": family, "structural_depth": depth,
        "critical": critical, "nuisance": nuisance,
        "public_goal_source": statement.removesuffix(" := by"),
        "lean_theorem": statement + "\n" + (proof or "  -- Negative: no theorem is sent for Lean proof checking"),
        "gold_proof": proof, "countermodel": countermodel,
        "host_label": "positive_proof_template" if critical else "negative_countermodel",
        "kernel_verified": False,
    }


def roster() -> list[dict]:
    return [mk_case(f, d, r, critical, nuisance)
            for f in FAMILIES for d in DEPTHS for r in ROOTS
            for critical in (True, False) for nuisance in (False, True)]


def check_countermodel(row: dict) -> bool:
    if row["critical"]:
        return row["countermodel"] is None and row["gold_proof"] is not None
    w = row["countermodel"]
    d = row["structural_depth"]
    if row["family"] in ("exact", "rcases"):
        return all(v is False for v in w["P_values"]) and w["goal"] is False
    if row["family"] == "rw":
        return w == {"a": 0, "b": 1, "goal": False} and (w["a"] + d != w["b"] + d)
    return w == {"n": 0, "actual_at_zero": d, "goal": False} and d > 0


def export(out: Path) -> dict:
    cases = roster()
    out.mkdir(parents=True, exist_ok=True)
    by_split = {s: [c for c in cases if c["split"] == s] for s in ("train", "dev", "test")}
    for split, rows in by_split.items():
        (out / f"{split}.jsonl").write_text(
            "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows))
        proofs = [c["lean_theorem"] for c in rows if c["critical"]]
        (out / f"{split}_positives.lean").write_text(
            "/- BPD-LG-01 generated positive proof candidates; compile with Lean 4.19.0 -/\n\n"
            + "\n\n".join(proofs) + "\n")
    assert all(check_countermodel(row) for row in cases)
    roots = {s: {r["root_id"] for r in rows} for s, rows in by_split.items()}
    assert not roots["train"] & roots["dev"] and not roots["train"] & roots["test"]
    assert not roots["dev"] & roots["test"]
    report = {
        "schema": SCHEMA, "cases": len(cases),
        "split_counts": {k: len(v) for k, v in by_split.items()},
        "positive_templates": sum(c["critical"] for c in cases),
        "negative_finite_countermodels": sum(not c["critical"] for c in cases),
        "families": list(FAMILIES), "depths": list(DEPTHS),
        "all_countermodels_verified": True,
        "kernel_status": "not_run_by_export; require CI pinned Lean compiler",
        "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted(out.glob("*.lean")) + sorted(out.glob("*.jsonl"))},
    }
    (out / "manifest.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.out), sort_keys=True))
