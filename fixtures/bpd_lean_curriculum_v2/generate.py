"""BPD-LG-01 v2: content-distinct roots, normalized-hash split, interior-link + decoy negatives,
depth-sensitive proofs across all families, and Lean-kernel-checked positives AND negatives.

Addresses all Part 2 audit requirements while leaving `fixtures/bpd_lean_curriculum_pinned/` (v1)
completely untouched as a regression fixture:
  1. Six content-distinct roots per family (differing in logical/algebraic/type constructors,
     never merely alpha-renamed identifiers). Split is assigned from the SHA-256 hash of the
     identifier-normalized root statement, with zero normalized-hash overlap across train/dev/test.
  2. Negatives delete each interior link `1..depth` as well as entry link `0`, and include
     type-checking decoy premises on both positives (2 decoys) and negatives (3 decoys, matching
     total hypothesis binder count so binder-count / `critical`-flag shortcuts fail).
  3. Structural depth `d in {1, 2, 3}` strictly changes the required proof term / rewrite chain /
     destructive unpacking / inductive step chain in every family (`exact`, `rw`, `rcases`, `induction`).
  4. Exports both `{split}_positives.lean` and `{split}_negatives.lean` (proving `¬ (...)` for
     every negative) with `#print axioms` lines for `scripts/check_lean_axioms.py`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

SCHEMA = "BPD-LG-01-v2"
FAMILIES = ("exact", "rw", "rcases", "induction")
DEPTHS = (1, 2, 3)
ROOTS = tuple(range(6))

LEAN_RESERVED = frozenset({
    "theorem", "private", "def", "by", "intro", "exact", "rw", "rcases", "with",
    "induction", "zero", "succ", "rfl", "simpa", "only", "using", "congrArg",
    "Prop", "Nat", "Bool", "Unit", "List", "Option", "Prod", "Exists",
    "True", "False", "Or", "And", "Iff", "some", "none", "true", "false",
    "inl", "inr", "mp", "mpr", "elim", "absurd", "decide", "have", "fun",
    "injection", "add_right_cancel",
})


def normalize_identifiers(lean_source: str) -> str:
    """Alpha-normalize all non-reserved identifiers to `_id0`, `_id1`, ... in first-seen order."""
    mapping: dict[str, str] = {}

    def _repl(match: re.Match[str]) -> str:
        tok = match.group(0)
        if tok in LEAN_RESERVED or tok.isdigit():
            return tok
        if tok not in mapping:
            mapping[tok] = f"_id{len(mapping)}"
        return mapping[tok]

    # Collapse whitespace after alpha-renaming all identifier tokens (handling dotted projections like h1.mp)
    def _dotted_repl(match: re.Match[str]) -> str:
        parts = match.group(0).split(".")
        out_parts = []
        for idx, p in enumerate(parts):
            if p in LEAN_RESERVED or p.isdigit():
                out_parts.append(p)
            elif idx > 0 and p in ("mp", "mpr", "inl", "inr", "succ", "some", "elim", "rfl"):
                out_parts.append(p)
            else:
                if p not in mapping:
                    mapping[p] = f"_id{len(mapping)}"
                out_parts.append(mapping[p])
        return ".".join(out_parts)

    renamed = re.sub(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*", _dotted_repl, lean_source)
    return " ".join(renamed.split())


def normalized_sha256(lean_source: str) -> str:
    return hashlib.sha256(normalize_identifiers(lean_source).encode("utf-8")).hexdigest()


def split_from_normalized_hash(norm_hash: str) -> str:
    """Deterministic split from post-normalization SHA-256 hash (~60% train / 20% dev / 20% test)."""
    bucket = int(norm_hash[:16], 16) % 10
    if bucket < 6:
        return "train"
    if bucket < 8:
        return "dev"
    return "test"


def _build_exact_case(
    stem: str, depth: int, root: int, deleted_link: int | None
) -> tuple[str, str, str | None, str | None, dict | None]:
    """Build `(binders, goal, pos_proof, neg_proof, countermodel)` for `exact`."""
    is_pos = deleted_link is None
    if root == 1:
        # Diamond multi-premise join: P-spine + Q-branch joined by `hjoin : Pd → Qd → G`
        prop_names = (
            [f"P{i}" for i in range(depth + 1)]
            + [f"Q{i}" for i in range(depth + 1)]
            + ["G", "D0", "D1", "D2"]
        )
        binders_list = [f"({' '.join(prop_names)} : Prop)"]
        binders_list.append("(hq0 : Q0)")
        for s in range(1, depth + 1):
            binders_list.append(f"(hs{s} : P{s-1} → P{s})")
        binders_list.append(f"(hjoin : P{depth} → Q{depth} → G)")
        if deleted_link != 0:
            binders_list.append("(h0 : P0)")
        for k in range(1, depth + 1):
            if deleted_link != k:
                binders_list.append(f"(hb{k} : Q{k-1} → Q{k})")
        binders_list.append("(hd1 : D0 → D1)")
        binders_list.append("(hd2 : D1 → D2)")
        if not is_pos:
            binders_list.append("(hd3 : G → D0)")
        goal = "G"

        if is_pos:
            p_term = "h0"
            for s in range(1, depth + 1):
                p_term = f"(hs{s} {p_term})"
            q_term = "hq0"
            for k in range(1, depth + 1):
                q_term = f"(hb{k} {q_term})"
            pos_proof = f"  exact hjoin {p_term} {q_term}"
            return " ".join(binders_list), goal, pos_proof, None, None

        assert deleted_link is not None
        if deleted_link == 0:
            p_vals = ["False"] * (depth + 1)
            q_vals = ["True"] * (depth + 1)
            args = p_vals + q_vals + ["False", "False", "False", "False"]
            args.append("True.intro")  # hq0
            args.extend(["(fun hf => False.elim hf)"] * depth)  # hs1..hsd
            args.append("(fun hf _ => False.elim hf)")  # hjoin
            args.extend(["(fun _ => True.intro)"] * depth)  # hb1..hbd
            args.extend(["(fun hf => False.elim hf)"] * 3)  # hd1..hd3
            cm = {"P_values": [False] * (depth + 1), "Q_values": [True] * (depth + 1), "G": False}
        else:
            m = deleted_link
            p_vals = ["True"] * (depth + 1)
            q_vals = ["True" if i < m else "False" for i in range(depth + 1)]
            args = p_vals + q_vals + ["False", "False", "False", "False"]
            args.append("True.intro")  # hq0
            args.extend(["(fun _ => True.intro)"] * depth)  # hs1..hsd
            args.append("(fun _ hqf => False.elim hqf)")  # hjoin
            args.append("True.intro")  # h0
            for k in range(1, depth + 1):
                if k == m:
                    continue
                args.append("(fun _ => True.intro)" if k < m else "(fun hf => False.elim hf)")
            args.extend(["(fun hf => False.elim hf)"] * 3)  # hd1..hd3
            cm = {
                "P_values": [True] * (depth + 1),
                "Q_values": [i < m for i in range(depth + 1)],
                "G": False,
            }
        neg_proof = "  intro h_all\n  exact h_all " + " ".join(args)
        return " ".join(binders_list), goal, None, neg_proof, cm

    # Roots 0, 2, 3, 4, 5
    prop_names = [f"P{i}" for i in range(depth + 1)] + ["D0", "D1", "D2"]
    binders_list = [f"({' '.join(prop_names)} : Prop)"]
    if deleted_link != 0:
        if root == 5:
            binders_list.append("(h0 : Unit → P0)")
        else:
            binders_list.append("(h0 : P0)")

    for k in range(1, depth + 1):
        if deleted_link == k:
            continue
        if root == 0:
            binders_list.append(f"(h{k} : P{k-1} → P{k})")
        elif root == 2:
            binders_list.append(f"(h{k} : P{k-1} ∧ True → P{k})")
        elif root == 3:
            binders_list.append(f"(h{k} : P{k-1} ∨ False → P{k})")
        elif root == 4:
            binders_list.append(f"(h{k} : P{k-1} ↔ P{k})")
        elif root == 5:
            binders_list.append(f"(h{k} : P{k-1} → Unit → P{k})")

    binders_list.append("(hd1 : D0 → D1)")
    binders_list.append("(hd2 : D1 → D2)")
    if not is_pos:
        binders_list.append(f"(hd3 : P{depth} → D0)")
    if root == 0:
        goal = f"P{depth}"
    elif root == 2:
        goal = f"P{depth} ∧ True"
    elif root == 3:
        goal = f"P{depth} ∨ False"
    elif root == 4:
        goal = f"True ↔ P{depth}"
    else:
        goal = f"Unit → P{depth}"

    if is_pos:
        term = "(h0 ())" if root == 5 else "h0"
        for k in range(1, depth + 1):
            if root == 0:
                term = f"(h{k} {term})"
            elif root == 2:
                term = f"(h{k} ⟨{term}, True.intro⟩)"
            elif root == 3:
                term = f"(h{k} (Or.inl {term}))"
            elif root == 4:
                term = f"(h{k}.mp {term})"
            elif root == 5:
                term = f"(h{k} {term} ())"
        if root == 0:
            final_term = term
        elif root == 2:
            final_term = f"⟨{term}, True.intro⟩"
        elif root == 3:
            final_term = f"Or.inl {term}"
        elif root == 4:
            final_term = f"⟨fun _ => {term}, fun _ => True.intro⟩"
        else:
            final_term = f"fun _ => {term}"
        return " ".join(binders_list), goal, f"  exact {final_term}", None, None

    assert deleted_link is not None
    m = deleted_link
    p_vals = ["True" if i < m else "False" for i in range(depth + 1)]
    args = p_vals + ["False", "False", "False"]
    if m != 0:
        args.append("(fun _ => True.intro)" if root == 5 else "True.intro")
    for k in range(1, depth + 1):
        if k == m:
            continue
        if k < m:
            if root == 4:
                args.append("Iff.rfl")
            elif root == 5:
                args.append("(fun _ _ => True.intro)")
            else:
                args.append("(fun _ => True.intro)")
        else:
            if root == 0:
                args.append("(fun hf => False.elim hf)")
            elif root == 2:
                args.append("(fun hp => False.elim hp.1)")
            elif root == 3:
                args.append("(fun hp => False.elim (hp.elim (fun a => a) (fun b => b)))")
            elif root == 4:
                args.append("Iff.rfl")
            elif root == 5:
                args.append("(fun hf _ => False.elim hf)")
    args.extend(["(fun hf => False.elim hf)"] * 3)
    cm = {"P_values": [i < m for i in range(depth + 1)], "goal": False}
    app = f"(h_all {' '.join(args)})"
    if root == 0:
        extract_false = app
    elif root == 2:
        extract_false = f"{app}.1"
    elif root == 3:
        extract_false = f"({app}.elim (fun a => a) (fun b => b))"
    elif root == 4:
        extract_false = f"({app}.mp True.intro)"
    else:
        extract_false = f"({app} ())"
    neg_proof = f"  intro h_all\n  exact {extract_false}"
    return " ".join(binders_list), goal, None, neg_proof, cm


def _build_rw_case(
    stem: str, depth: int, root: int, deleted_link: int | None
) -> tuple[str, str, str | None, str | None, dict | None]:
    is_pos = deleted_link is None
    xs = [f"x{i}" for i in range(depth + 2)]
    binders_list = [f"({' '.join(xs)} d0 d1 d2 : Nat)"]
    for k in range(depth + 1):
        if deleted_link != k:
            binders_list.append(f"(h{k} : x{k} = x{k+1})")
    binders_list.append("(hd1 : d0 + 1 = d1 + 1)")
    binders_list.append("(hd2 : d1 + 2 = d2 + 2)")
    if not is_pos:
        binders_list.append("(hd3 : d0 + 3 = d2 + 3)")

    x_end = f"x{depth + 1}"
    if root == 0:
        goal = f"Nat.succ x0 = Nat.succ {x_end}"
    elif root == 1:
        goal = f"x0 + 1 = {x_end} + 1"
    elif root == 2:
        goal = f"x0 * 2 + 1 = {x_end} * 2 + 1"
    elif root == 3:
        goal = f"(x0, 0) = ({x_end}, 0)"
    elif root == 4:
        goal = f"[x0] = [{x_end}]"
    else:
        goal = f"Option.some x0 = Option.some {x_end}"

    if is_pos:
        rw_steps = ", ".join(f"h{k}" for k in range(depth + 1))
        return " ".join(binders_list), goal, f"  rw [{rw_steps}]", None, None

    assert deleted_link is not None
    m = deleted_link
    x_vals = ["0" if i <= m else "1" for i in range(depth + 2)]
    args = x_vals + ["0", "0", "0"]
    args.extend(["rfl"] * depth)  # (depth + 1) - 1 kept links
    args.extend(["rfl"] * 3)  # hd1, hd2, hd3
    neg_proof = (
        "  intro h_all\n"
        f"  have h_eq := h_all {' '.join(args)}\n"
        "  exact absurd h_eq (by decide)"
    )
    cm = {"x_values": [0 if i <= m else 1 for i in range(depth + 2)], "goal": False}
    return " ".join(binders_list), goal, None, neg_proof, cm


def _build_rcases_case(
    stem: str, depth: int, root: int, deleted_link: int | None
) -> tuple[str, str, str | None, str | None, dict | None]:
    is_pos = deleted_link is None
    prop_names = [f"P{i}" for i in range(depth + 1)] + ["D0", "D1", "D2"]
    binders_list = [f"({' '.join(prop_names)} : Prop)"]

    def _pack_type(p_sym: str) -> str:
        if root == 0:
            return f"({p_sym} ∧ True)"
        if root == 1:
            return f"(True ∧ {p_sym})"
        if root == 2:
            return f"Exists (fun (_ : Nat) => {p_sym})"
        if root == 3:
            return f"Exists (fun (_ : Bool) => {p_sym})"
        if root == 4:
            return f"Exists (fun (_ : Unit) => {p_sym} ∧ True)"
        return f"(({p_sym} ∧ {p_sym}) ∧ True)"

    if deleted_link != 0:
        binders_list.append(f"(h0 : {_pack_type('P0')})")

    for k in range(1, depth + 1):
        if deleted_link == k:
            continue
        binders_list.append(f"(h{k} : P{k-1} → {_pack_type(f'P{k}')})")

    binders_list.append("(hd1 : D0 → (D1 ∧ D0))")
    binders_list.append("(hd2 : D1 → (D2 ∧ D1))")
    if not is_pos:
        binders_list.append(f"(hd3 : P{depth} → (D0 ∧ D2))")
    goal = _pack_type(f"P{depth}")

    def _unpack_line(src_expr: str, out_var: str) -> str:
        if root == 0:
            return f"  rcases {src_expr} with ⟨{out_var}, _⟩"
        if root in (1, 2, 3):
            return f"  rcases {src_expr} with ⟨_, {out_var}⟩"
        if root == 4:
            return f"  rcases {src_expr} with ⟨_, {out_var}, _⟩"
        return f"  rcases {src_expr} with ⟨⟨{out_var}, _⟩, _⟩"

    if is_pos:
        lines = [_unpack_line("h0", "p0")]
        for k in range(1, depth + 1):
            lines.append(_unpack_line(f"h{k} p{k-1}", f"p{k}"))
        pd = f"p{depth}"
        if root == 0:
            close_line = f"  exact ⟨{pd}, True.intro⟩"
        elif root == 1:
            close_line = f"  exact ⟨True.intro, {pd}⟩"
        elif root == 2:
            close_line = f"  exact ⟨0, {pd}⟩"
        elif root == 3:
            close_line = f"  exact ⟨true, {pd}⟩"
        elif root == 4:
            close_line = f"  exact ⟨(), {pd}, True.intro⟩"
        else:
            close_line = f"  exact ⟨⟨{pd}, {pd}⟩, True.intro⟩"
        lines.append(close_line)
        return " ".join(binders_list), goal, "\n".join(lines), None, None

    assert deleted_link is not None
    m = deleted_link
    p_vals = ["True" if i < m else "False" for i in range(depth + 1)]
    args = p_vals + ["False", "False", "False"]
    raw_true_pack = {
        0: "⟨True.intro, True.intro⟩",
        1: "⟨True.intro, True.intro⟩",
        2: "⟨0, True.intro⟩",
        3: "⟨true, True.intro⟩",
        4: "⟨(), True.intro, True.intro⟩",
        5: "⟨⟨True.intro, True.intro⟩, True.intro⟩",
    }[root]
    if m != 0:
        args.append(raw_true_pack)
    true_witness = f"(fun _ => {raw_true_pack})"
    for k in range(1, depth + 1):
        if k == m:
            continue
        args.append(true_witness if k < m else "(fun hf => False.elim hf)")
    args.extend(["(fun hf => False.elim hf)"] * 3)
    cm = {"P_values": [i < m for i in range(depth + 1)], "goal": False}
    app = f"h_all {' '.join(args)}"
    neg_proof = (
        "  intro h_all\n"
        f"{_unpack_line(app, 'hf_goal')}\n"
        "  exact hf_goal"
    )
    return " ".join(binders_list), goal, None, neg_proof, cm


def _build_induction_case(
    stem: str, depth: int, root: int, deleted_link: int | None
) -> tuple[str, str, str | None, str | None, dict | None]:
    is_pos = deleted_link is None
    fn_names = [f"F{i}" for i in range(depth)] + ["D0", "D1"]
    binders_list = [f"({' '.join(fn_names)} : Nat → Nat)"]
    if deleted_link != 0:
        binders_list.append("(h0 : F0 0 = 0)")

    if depth == 1:
        if deleted_link != 1:
            binders_list.append("(h1 : ∀ k : Nat, F0 (k + 1) = F0 k + 1)")
    else:
        if deleted_link != 1:
            binders_list.append("(h1 : ∀ k : Nat, F0 (k + 1) = F1 k)")
        for k in range(2, depth):
            if deleted_link != k:
                binders_list.append(f"(h{k} : ∀ k : Nat, F{k-1} k = F{k} k)")
        if deleted_link != depth:
            binders_list.append(f"(h{depth} : ∀ k : Nat, F{depth-1} k = F0 k + 1)")

    binders_list.append("(hd1 : ∀ k : Nat, D0 (k + 1) = D1 k)")
    binders_list.append("(hd2 : ∀ k : Nat, D1 k = D0 k)")
    if not is_pos:
        binders_list.append("(hd3 : ∀ k : Nat, D0 (k + 2) = D1 k)")

    if root == 0:
        goal = "∀ n : Nat, F0 n = n"
        ih_extract = "    rw [ih]"
    elif root == 1:
        goal = "∀ n : Nat, [F0 n] = [n]"
        ih_extract = "    injection ih with ih0\n    rw [ih0]"
    elif root == 2:
        goal = "∀ n : Nat, F0 n + 1 = n + 1"
        ih_extract = "    have ih0 : F0 n = n := Nat.add_right_cancel ih\n    rw [ih0]"
    elif root == 3:
        goal = "∀ n : Nat, Nat.succ (F0 n) = Nat.succ n"
        ih_extract = "    injection ih with ih0\n    rw [ih0]"
    elif root == 4:
        goal = "∀ n : Nat, (F0 n, true) = (n, true)"
        ih_extract = "    injection ih with ih0 _\n    rw [ih0]"
    else:
        goal = "∀ n : Nat, Option.some (F0 n) = Option.some n"
        ih_extract = "    injection ih with ih0\n    rw [ih0]"

    if is_pos:
        step_rws = ", ".join(f"h{k}" for k in range(1, depth + 1))
        pos_proof = (
            "  intro n\n"
            "  induction n with\n"
            "  | zero => rw [h0]\n"
            "  | succ n ih =>\n"
            f"    rw [{step_rws}]\n"
            f"{ih_extract}"
        )
        return " ".join(binders_list), goal, pos_proof, None, None

    assert deleted_link is not None
    m = deleted_link
    if m == 0:
        fn_args = ["(fun k => k + 1)"] + ["(fun k => k + 2)"] * (depth - 1) + ["(fun _ => 0)", "(fun _ => 0)"]
        hyp_args = ["(fun _ => rfl)"] * depth + ["(fun _ => rfl)"] * 3
        eval_n = "0"
        cm = {"n": 0, "F0_at_n": 1, "expected": 0, "goal": False}
    else:
        fn_args = ["(fun _ => 0)"]
        for j in range(1, depth):
            fn_args.append("(fun _ => 0)" if j < m else "(fun _ => 1)")
        fn_args.extend(["(fun _ => 0)", "(fun _ => 0)"])
        hyp_args = ["rfl"] + ["(fun _ => rfl)"] * (depth - 1) + ["(fun _ => rfl)"] * 3
        eval_n = "1"
        cm = {"n": 1, "F0_at_n": 0, "expected": 1, "goal": False}

    neg_proof = (
        "  intro h_all\n"
        f"  have h_at := h_all {' '.join(fn_args)} {' '.join(hyp_args)} {eval_n}\n"
        "  exact absurd h_at (by decide)"
    )
    return " ".join(binders_list), goal, None, neg_proof, cm


def _dispatch_builder(
    family: str, stem: str, depth: int, root: int, deleted_link: int | None
) -> tuple[str, str, str | None, str | None, dict | None]:
    if family == "exact":
        return _build_exact_case(stem, depth, root, deleted_link)
    if family == "rw":
        return _build_rw_case(stem, depth, root, deleted_link)
    if family == "rcases":
        return _build_rcases_case(stem, depth, root, deleted_link)
    if family == "induction":
        return _build_induction_case(stem, depth, root, deleted_link)
    raise ValueError(f"Unsupported family: {family!r}")


def mk_case(family: str, depth: int, root: int, deleted_link: int | None) -> dict:
    if family not in FAMILIES or depth not in DEPTHS or root not in ROOTS:
        raise ValueError("unsupported family/depth/root")
    if deleted_link is not None and not (0 <= deleted_link <= depth):
        raise ValueError(f"deleted_link {deleted_link} outside 0..{depth}")

    pos_stem = f"bpd2_{family}_d{depth}_r{root}_pos"
    pos_binders, pos_goal, _, _, _ = _dispatch_builder(family, pos_stem, depth, root, None)
    pos_public_source = f"theorem thm_{pos_stem} {pos_binders} : {pos_goal}"
    root_norm_hash = normalized_sha256(pos_public_source)
    split = split_from_normalized_hash(root_norm_hash)

    variant_tag = "pos" if deleted_link is None else f"del{deleted_link}"
    stem = f"bpd2_{family}_d{depth}_r{root}_{variant_tag}"
    thm_name = f"thm_{stem}"
    neg_thm_name = f"neg_{thm_name}"

    binders, goal, pos_proof, neg_proof, countermodel = _dispatch_builder(
        family, stem, depth, root, deleted_link
    )
    public_goal_source = f"theorem {thm_name} {binders} : {goal}"
    stmt_norm_hash = normalized_sha256(public_goal_source)
    is_positive = deleted_link is None

    if is_positive:
        assert pos_proof is not None
        lean_pos = f"{public_goal_source} := by\n{pos_proof}\n\n#print axioms {thm_name}"
        lean_neg = None
    else:
        assert neg_proof is not None
        lean_pos = None
        lean_neg = (
            f"theorem {neg_thm_name} : ¬ (∀ {binders}, {goal}) := by\n"
            f"{neg_proof}\n\n#print axioms {neg_thm_name}"
        )

    return {
        "schema": SCHEMA,
        "case_id": stem,
        "root_id": f"{family}-d{depth}-r{root}",
        "root_normalized_sha256": root_norm_hash,
        "statement_normalized_sha256": stmt_norm_hash,
        "split": split,
        "family": family,
        "structural_depth": depth,
        "provable": is_positive,
        "deleted_link": deleted_link,
        "decoy_count": 2 if is_positive else 3,
        "public_goal_source": public_goal_source,
        "lean_positive_theorem": lean_pos,
        "lean_negative_theorem": lean_neg,
        "gold_proof": pos_proof,
        "negation_proof": neg_proof,
        "countermodel": countermodel,
        "host_label": "positive_kernel_checked" if is_positive else "negative_kernel_refuted",
    }


def roster() -> list[dict]:
    out: list[dict] = []
    for f in FAMILIES:
        for d in DEPTHS:
            for r in ROOTS:
                out.append(mk_case(f, d, r, None))
                for del_k in range(d + 1):
                    out.append(mk_case(f, d, r, del_k))
    return out


def export(out: Path) -> dict:
    cases = roster()
    out.mkdir(parents=True, exist_ok=True)

    # Assert all 72 positive roots have pairwise-distinct normalized hashes (content-distinct roots!)
    pos_cases = [c for c in cases if c["provable"]]
    pos_norm_hashes = {c["statement_normalized_sha256"] for c in pos_cases}
    assert len(pos_norm_hashes) == len(pos_cases), (
        f"Expected {len(pos_cases)} distinct normalized positive statements, got {len(pos_norm_hashes)}"
    )

    by_split = {s: [c for c in cases if c["split"] == s] for s in ("train", "dev", "test")}
    assert all(len(rows) > 0 for rows in by_split.values()), "Every split must be non-empty"

    # Assert zero normalized-hash overlap across train / dev / test
    norm_by_split = {
        s: {c["statement_normalized_sha256"] for c in rows} for s, rows in by_split.items()
    }
    assert not (norm_by_split["train"] & norm_by_split["dev"])
    assert not (norm_by_split["train"] & norm_by_split["test"])
    assert not (norm_by_split["dev"] & norm_by_split["test"])

    for split, rows in by_split.items():
        (out / f"{split}.jsonl").write_text(
            "".join(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )
        pos_scripts = [c["lean_positive_theorem"] for c in rows if c["provable"]]
        neg_scripts = [c["lean_negative_theorem"] for c in rows if not c["provable"]]
        (out / f"{split}_positives.lean").write_text(
            "/- BPD-LG-01 v2 positive theorems; kernel-checked with #print axioms -/\n\n"
            + "\n\n".join(pos_scripts)
            + "\n",
            encoding="utf-8",
        )
        (out / f"{split}_negatives.lean").write_text(
            "/- BPD-LG-01 v2 negative refutations (¬ goal); kernel-checked with #print axioms -/\n\n"
            + "\n\n".join(neg_scripts)
            + "\n",
            encoding="utf-8",
        )

    report = {
        "schema": SCHEMA,
        "cases": len(cases),
        "distinct_positive_normalized_hashes": len(pos_norm_hashes),
        "distinct_total_normalized_hashes": len({c["statement_normalized_sha256"] for c in cases}),
        "split_counts": {k: len(v) for k, v in by_split.items()},
        "positive_theorems": sum(1 for c in cases if c["provable"]),
        "negative_refutations": sum(1 for c in cases if not c["provable"]),
        "families": list(FAMILIES),
        "depths": list(DEPTHS),
        "zero_normalized_split_overlap": True,
        "sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(out.glob("*.lean")) + sorted(out.glob("*.jsonl"))
        },
    }
    (out / "manifest.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.out), sort_keys=True))
