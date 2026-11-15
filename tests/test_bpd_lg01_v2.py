"""Acceptance and regression tests for BPD-LG-01 v2 vs v1 (Part 2)."""
from __future__ import annotations

from collections import deque
import json
from pathlib import Path
import re
import unittest

from spiral_ln.evaluation_bpd import Probe, coverage, minimum_test_collection, optimal_decision_tree_cost

ROOT = Path(__file__).resolve().parents[1]
V1_DIR = ROOT / "fixtures" / "bpd_lean_curriculum_pinned"
V2_DIR = ROOT / "fixtures" / "bpd_lean_curriculum_v2"

HYPOTHESIS_NAMES = (
    "truth",
    "binder_presence_detector",
    "depth_blind",
    "family_only",
    "chain_follower",
)

RESERVED_TOKENS = frozenset({
    "theorem", "private", "def", "by", "Prop", "Nat", "Bool", "Unit",
    "List", "Option", "Prod", "Exists", "True", "False", "Or", "And",
    "Iff", "some", "none", "true", "false", "succ", "fun",
})


def _user_idents(expr: str) -> list[str]:
    out = []
    for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]*", expr):
        if tok not in RESERVED_TOKENS and tok != "_":
            out.append(tok)
    return out


def _parse_public_goal(src: str) -> tuple[str, list[tuple[str, str]], str]:
    """Split `public_goal_source` into `(def_prefix, hypothesis_binders, goal_expr)`."""
    thm_idx = src.index("theorem ")
    def_prefix = src[:thm_idx].strip()
    thm_body = src[thm_idx:]

    # Skip `theorem <name>`
    m = re.match(r"^theorem\s+[A-Za-z0-9_]+\s*", thm_body)
    assert m is not None
    rest = thm_body[m.end():]

    # Split at first top-level `:` (paren depth == 0)
    depth = 0
    split_pos = -1
    for i, ch in enumerate(rest):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch == ":" and depth == 0:
            split_pos = i
            break
    assert split_pos >= 0, f"Could not find top-level ':' in {src!r}"
    binders_str = rest[:split_pos].strip()
    goal_expr = rest[split_pos + 1:].strip()

    # Extract top-level `(... : ...)` groups
    binders: list[tuple[str, str]] = []
    b_start = None
    depth = 0
    for i, ch in enumerate(binders_str):
        if ch == "(":
            if depth == 0:
                b_start = i + 1
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0 and b_start is not None:
                grp = binders_str[b_start:i].strip()
                if ":" in grp:
                    lhs, rhs = grp.split(":", 1)
                    b_name = lhs.strip()
                    b_type = rhs.strip()
                    if b_type not in ("Prop", "Nat", "Nat → Nat") and b_name != "noise":
                        binders.append((b_name, b_type))
                b_start = None
    return def_prefix, binders, goal_expr


def _is_seed_hyp(h_type: str) -> bool:
    if h_type.startswith("Unit → "):
        return True
    return ("→" not in h_type) and (not h_type.startswith("∀")) and ("+" not in h_type)


def predict_binder_presence(src: str) -> int:
    def_prefix, hyps, _ = _parse_public_goal(src)
    if def_prefix:
        return int("| 0 => 0" in def_prefix)
    return int(any(_is_seed_hyp(ht) for _, ht in hyps))


def predict_depth_blind(src: str) -> int:
    def_prefix, hyps, goal_expr = _parse_public_goal(src)
    if def_prefix:
        return int("| 0 => 0" in def_prefix)
    seeds = [ht for _, ht in hyps if _is_seed_hyp(ht)]
    if not seeds:
        return 0
    seed_syms = {sym for ht in seeds for sym in _user_idents(ht)}
    non_seeds = [ht for _, ht in hyps if not _is_seed_hyp(ht)]
    goal_syms = set(_user_idents(goal_expr))
    if not non_seeds:
        return int(bool(seed_syms & goal_syms))
    if seed_syms & goal_syms:
        return 1
    for ht in non_seeds:
        if "↔" in ht:
            lhs = ht.split("↔", 1)[0]
        elif "→" in ht:
            lhs = ht.rsplit("→", 1)[0]
        elif "=" in ht:
            lhs = ht.split("=", 1)[0]
        else:
            lhs = ht
        if set(_user_idents(lhs)) & seed_syms:
            return 1
    return 0


def predict_family_only(src: str) -> int:
    _, _, goal_expr = _parse_public_goal(src)
    return int("=" in goal_expr)


def predict_chain_follower(src: str) -> int:
    def_prefix, hyps, goal_expr = _parse_public_goal(src)
    if def_prefix:
        return int("| 0 => 0" in def_prefix)

    # Equational non-quantified goals (`rw`)
    if "=" in goal_expr and not goal_expr.startswith("∀"):
        g_lhs, g_rhs = goal_expr.split("=", 1)
        src_syms = set(_user_idents(g_lhs))
        dst_syms = set(_user_idents(g_rhs))
        adj: dict[str, set[str]] = {}
        for _, ht in hyps:
            if "=" in ht and "+" not in ht:
                el, er = ht.split("=", 1)
                ls, rs = _user_idents(el), _user_idents(er)
                for u in ls:
                    for v in rs:
                        adj.setdefault(u, set()).add(v)
                        adj.setdefault(v, set()).add(u)
        q = deque(src_syms)
        seen = set(src_syms)
        while q:
            cur = q.popleft()
            if cur in dst_syms:
                return 1
            for nxt in adj.get(cur, ()):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        return 0

    # Quantified inductive goals (`induction`)
    if goal_expr.startswith("∀"):
        seeded = {sym for _, ht in hyps if _is_seed_hyp(ht) for sym in _user_idents(ht)}
        if not seeded:
            return 0
        adj_f: dict[str, set[str]] = {}
        closes_to_base = False
        for _, ht in hyps:
            if ht.startswith("∀") and "=" in ht:
                body = ht.split(",", 1)[1]
                lhs, rhs = body.split("=", 1)
                lu = [s for s in _user_idents(lhs) if s != "k"]
                ru = [s for s in _user_idents(rhs) if s != "k"]
                for u in lu:
                    for v in ru:
                        adj_f.setdefault(u, set()).add(v)
                        if "+ 1" in rhs and v in seeded:
                            closes_to_base = True
        if not closes_to_base:
            return 0
        q = deque(seeded)
        seen = set(seeded)
        while q:
            cur = q.popleft()
            for nxt in adj_f.get(cur, ()):
                if nxt in seeded and "+ 1" in " ".join(ht for _, ht in hyps):
                    pass
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        # Check directed cycle from seeded F0 through step equations back into F0
        for start in seeded:
            q2 = deque(adj_f.get(start, ()))
            visited = set(q2)
            while q2:
                node = q2.popleft()
                if node == start:
                    return 1
                for nxt in adj_f.get(node, ()):
                    if nxt not in visited:
                        visited.add(nxt)
                        q2.append(nxt)
        return 0

    # Propositional / destructive goals (`exact`, `rcases`): naive single-edge reachability
    seeded_p = {sym for _, ht in hyps if _is_seed_hyp(ht) for sym in _user_idents(ht)}
    if not seeded_p:
        return 0
    adj_p: dict[str, set[str]] = {}
    for _, ht in hyps:
        if _is_seed_hyp(ht):
            continue
        if "↔" in ht:
            lhs, rhs = ht.split("↔", 1)
            for u in _user_idents(lhs):
                for v in _user_idents(rhs):
                    adj_p.setdefault(u, set()).add(v)
                    adj_p.setdefault(v, set()).add(u)
        elif "→" in ht:
            parts = ht.split("→")
            concl_syms = _user_idents(parts[-1])
            for prem in parts[:-1]:
                for u in _user_idents(prem):
                    for v in concl_syms:
                        adj_p.setdefault(u, set()).add(v)
    goal_p = set(_user_idents(goal_expr))
    q = deque(seeded_p)
    seen = set(seeded_p)
    while q:
        cur = q.popleft()
        if cur in goal_p:
            return 1
        for nxt in adj_p.get(cur, ()):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return 0


def build_corpus_probes(corpus_dir: Path) -> tuple[Probe, ...]:
    rows = []
    if (corpus_dir / "train.jsonl").exists():
        for split in ("train", "dev", "test"):
            for line in (corpus_dir / f"{split}.jsonl").read_text(encoding="utf-8").splitlines():
                if line.strip():
                    rows.append(json.loads(line))
    else:
        from fixtures.bpd_lean_curriculum_pinned.generate import roster

        rows = roster()
    probes = []
    for row in rows:
        truth = int(row["provable"] if "provable" in row else row["critical"])
        src = row["public_goal_source"]
        outcomes = (
            truth,
            predict_binder_presence(src),
            predict_depth_blind(src),
            predict_family_only(src),
            predict_chain_follower(src),
        )
        probes.append(Probe(name=row["case_id"], outcomes=outcomes))
    return tuple(probes)


class BpdLg01V2Tests(unittest.TestCase):
    def test_v2_separates_all_shortcut_pairs_and_v1_fails_regression(self):
        # Regression check on untouched v1: shortcuts collapse onto truth -> unresolved_pairs != []
        probes_v1 = build_corpus_probes(V1_DIR)
        cov_v1 = coverage(probes_v1)
        self.assertGreater(len(cov_v1["unresolved_pairs"]), 0)
        self.assertIsNone(minimum_test_collection(probes_v1))
        self.assertIsNone(optimal_decision_tree_cost(probes_v1))

        # Acceptance check on v2: every pair among all 5 hypotheses is separated!
        probes_v2 = build_corpus_probes(V2_DIR)
        cov_v2 = coverage(probes_v2)
        self.assertEqual(cov_v2["hypotheses"], len(HYPOTHESIS_NAMES))
        self.assertEqual(cov_v2["total_pairs"], 10)
        self.assertEqual(cov_v2["separated_pairs"], 10)
        self.assertEqual(cov_v2["unresolved_pairs"], [])
        self.assertIsNotNone(minimum_test_collection(probes_v2))
        self.assertIsNotNone(optimal_decision_tree_cost(probes_v2))

    def test_v2_content_distinct_roots_zero_split_overlap_and_depth_proofs(self):
        from fixtures.bpd_lean_curriculum_v2.generate import normalize_identifiers, normalized_sha256

        by_split: dict[str, list[dict]] = {}
        for split in ("train", "dev", "test"):
            by_split[split] = [
                json.loads(line)
                for line in (V2_DIR / f"{split}.jsonl").read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertGreater(len(by_split[split]), 0)

        norm_sets = {
            s: {normalized_sha256(r["public_goal_source"]) for r in rows}
            for s, rows in by_split.items()
        }
        self.assertEqual(norm_sets["train"] & norm_sets["dev"], set())
        self.assertEqual(norm_sets["train"] & norm_sets["test"], set())
        self.assertEqual(norm_sets["dev"] & norm_sets["test"], set())

        all_rows = [r for rows in by_split.values() for r in rows]
        positives = [r for r in all_rows if r["provable"]]
        # All 72 positive roots have distinct identifier-normalized statements
        self.assertEqual(len(positives), 72)
        self.assertEqual(
            len({normalize_identifiers(r["public_goal_source"]) for r in positives}),
            72,
        )

        # Depth strictly changes the normalized gold proof in EVERY family & root
        by_fam_root: dict[tuple[str, str], dict[int, str]] = {}
        for r in positives:
            key = (r["family"], r["root_id"].split("-")[-1])
            by_fam_root.setdefault(key, {})[r["structural_depth"]] = normalize_identifiers(
                r["gold_proof"]
            )
        self.assertEqual(len(by_fam_root), 24)
        for (fam, rt), proofs_by_d in by_fam_root.items():
            self.assertEqual(set(proofs_by_d.keys()), {1, 2, 3})
            self.assertEqual(
                len(set(proofs_by_d.values())),
                3,
                msg=f"Proof did not change across depths for {fam} {rt}",
            )


if __name__ == "__main__":
    unittest.main()
