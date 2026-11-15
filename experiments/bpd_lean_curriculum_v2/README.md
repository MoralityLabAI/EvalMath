# BPD-LG-02: independent structural audit and repair of the Lean curriculum

**Status, 2026-11-15:** generator, finite-model checker, split audit, and seven independent CPU tests passed. [Independent Lean 4.19.0 replay](https://github.com/MoralityLabAI/EvalMath/actions/runs/43705790859) kernel-checked **192 positive proofs and 192 negative refutations**, with **384 empty axiom inventories**. See [KERNEL_AUDIT.md](KERNEL_AUDIT.md) for source hashes and claim boundaries. No neural training, BPD decomposition, or capability result is asserted.

## Why this exists

Fable's review of BPD-01 identified a failure in the original BPD-LG-01 corpus: its six roots per template varied only in binder names, the label was a directly accessible `critical` generator toggle, depth was irrelevant to `rw` and `induction` proof scripts, and the nuisance was an unused `(noise : Nat)` binder. The original kernel audit was valid for those synthetic statements and remains archived. The earlier corpus is **a failed mechanism-separation benchmark** even though its proofs compiled.

This successor builds distinct typed *premise graphs*, preserves multiple deceptive but valid hypotheses, and exports student-visible statements in a separate file from host-only labels and witnesses. Every negative replaces **an interior dependency** of a real proof chain and is accompanied by a fully enumerated satisfying interpretation of the premises with a false target. Some positive examples also lack the straightforward path and require an active detour through a distractor node. Every split contains both kinds of positive proof structures.

## Corpus contract

Four tactic-witness families are covered, with nominal depth 3–6 and six graph shapes per family/depth. For each shape the generator emits positive/negative minimal contrasts with two nuisance-graph variants: **384 cases** (192 label-positive and 192 label-negative), divided **256/64/64** train/dev/test. The split is by a digest of the **role-labelled structural scaffold**, before constructing minimal pairs. Every one of 96 structural groups stays in exactly one partition. Each source formula's role-labelled premise-graph digest is audited against every other split, producing 384 distinct fingerprints and zero cross-split duplicates in the present deterministic set.

The graph digest ignores theorem identifiers, renamed propositional/Nat variables and shuffled hypothesis binders. It preserves the source/target and dependency relation. This is a **conservative role-labelled structural normalization**, not a complete decision procedure for logical equivalence or arbitrary graph isomorphism. Do not claim the grammar is out-of-distribution in meaning without testing alternative structural baselines.

- `exact` uses a computed chain of real implications.
- `rw` uses a `calc` proof that rewrites each required equality; the number of rewrites grows with path length.
- `rcases` deconstructs a nested conjunction of shuffled implication premises before rebuilding the dependency chain.
- `induction` proves a property of arbitrary Nat-indexed predicates. The base case requires actual Horn-chain propagation, and the successor case uses a recurrent step from the prior proof; longer chains require more proof applications.

The visible payload has just `case_id` and `lean_statement`. It exposes no generator `critical`, `variant`, nuisance, or gold label flags. Host-only JSONL includes targets, finite countermodels, proofs, original role-graphs, and structural fingerprints. Model input code must read only `*_public.jsonl`, and any selection/evaluation process must treat `*_host.jsonl` as privileged scorer data.

No claim of tactic-family uniqueness is made. The family is one witness, and another tactic or a symbolic graph algorithm can solve these tasks. A straightforward BFS/union-find oracle has 100% correctness on this deterministic Horn/equality fragment. It is an **essential strong zero-neural baseline**; the generator itself computes such a label.

## Negative certificates

A positive Lean theorem is saved to `*_positives.lean`. Each negative's original universal claim is separately refuted in `*_refutations.lean`: an explicit interpretation of every theorem parameter satisfies its hypotheses while making its goal false. Proving the negation of a universal theorem is stronger evidence than checking only a Python Boolean countermodel. All six generated Lean files need independent kernel replay and axiom inventory checks.

For induction, the finite model assigns every Nat-indexed predicate a constant truth value. This is an explicit countermodel for **all** natural numbers rather than a bounded simulation of the induction statement. The finite proof generator still has to pass the Lean kernel before it can be called certified.

## Mechanism separation and the next experiment

The mathematical BPD-01 minimax and set-cover results remain correct. Their use as a decomposition claim depends on measured interventions. The original curriculum's contrast was insufficient to distinguish proof-chain following from noticing the only critical premise. BPD-LG-02 addresses obvious corpus shortcuts but **does not yet establish T1 separation of any two trained mechanisms**.

For a genuinely discriminative neural experiment, prespecify a base/unrolled-VPD/lookup/rotation-null comparison and a **fourth-family-held-out** test. Fit components from three of `exact`, `rw`, `rcases`, `induction`, then predict single-cut and joint-cut intervention effects on the fourth. Freeze per-pass readout labels at the *next readout*, track source and state separately, and run a cue-conflict swap: perturb carried state with input fixed, then perturb input with carried state fixed. Hold matched compute and rank; compare component stability across seeds. Preregister tolerances for continuous-state matching and report held-out predictive error over a tolerance sweep. The trivial discrete fibre-error floor from T3 is only a diagnostic of a specified information interface.

For an open-set decomposition, include an explicit `none of the candidates` outcome, measure whether the intervention coordinates are comparable, and require parsimony within each observational equivalence class. If routing depends on mechanism, treat the route as an observable response or a measured missingness channel.

FC-12's separate original MathCan training-incidence data and held-out source proofs remain unchanged. The Hall deficit applies to quota feasibility for *verified positive tactic edges*, whereas BPD-01's mechanism-pair cover optimizes causal distinguishability. Its 117 suggestions are unknown compiler outcomes and carry no estimated success rate from the current graph.

## Reproduce (without Lean)

```bash
python -m unittest experiments.bpd_lean_curriculum_v2.test_generate -v
python -m experiments.bpd_lean_curriculum_v2.generate --out /tmp/bpd-lg02
```

Then, with Lean 4.19.0 installed:

```bash
for s in train dev test; do
  lean "/tmp/bpd-lg02/${s}_positives.lean"
  lean "/tmp/bpd-lg02/${s}_refutations.lean"
done
```

The CI validator should also append `#print axioms` for each declaration to a *second* file and require every statement to be axiom-free. CI must report success by split and by sign, and archive original generated source digests, stdout/stderr, and failure receipts.
