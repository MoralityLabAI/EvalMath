# VAD-01: Verified abstraction discovery and evaluation feedback

Status: 2026-11-25. VAD-01A is a completed exact synthetic control. VAD-01B is a proposed prospective Lean/model experiment, to be frozen before model execution. No model was run. No Lean theorem is claimed here.

## Motivation

OpenAI's October 26 report describes a model-produced local smoothing proof using an auxiliary PDE and a subsequent Lean formalization ([source](https://openai.com/index/building-scientific-understanding-with-academic-communities/)). Anthropic's September 4 report describes the autoformalization of Fermat's Last Theorem using an explicit dependency graph and a large library of intermediate theorems ([source](https://www.anthropic.com/research/formalizing-fermats-last-theorem)). These are cited upstream claims, not independently reverified here. They motivate measuring the reusable computational value of an abstraction, with attention to the evaluation feedback channel through which it is chosen.

## Exact cache model (VAD-01A)

Represent theorem targets by vectors t in F_2^d. Primitive generators are the standard basis. An admissible cache is the XOR of a subset of primitives, represented by a nonzero vector a. Its statement and construction agree by definition; there is no general-purpose proof checker here. Charge one unit per generator reference to the producer and one to an abstract checker, including each cache reference. Repeated generators cancel in pairs, so a shortest derivation uses every available generator at most once.

Without a cache the exact minimum is C_0(t)=2|t|, where |.| is Hamming weight. With one cache it is C_a(t)=2 min(|t|,1+|t XOR a|). Either no cache reference occurs, or exactly one does and the remaining primitives must have support t XOR a. Thus the nonnegative per-target saving is

    Delta(t,a)=2 max(0, 2|supp(t) intersect supp(a)| - |a| - 1).

Let D(a) denote the charged discovery work and K(a)=2|a| its construction/checking charge. For any nonempty deployment set H with positive total cost, the exact aggregate gain is

    G = sum_H C_0(t) / [D(a)+K(a)+sum_H C_a(t)].

Strict gain occurs iff sum_H Delta(t,a)>D(a)+K(a). If all n targets contain the support of a and |a|>1, this becomes n>(D(a)+2|a|)/(2(|a|-1)). Proof: substitute the per-target saving and subtract the two positive costs. This is a mathematical identity under the stated reference-cost model, not a claim about elapsed time or Lean kernel work.

## Finite control and receipt

For each of 32 seeds in each regime, use d=20, four development roots, and 64 distinct held-out roots disjoint from development. Every target has weight 10. Shared: a six-bit motif persists. Shifted: the deployment motif is disjoint from the development motif. Null: roots are uniform weight-10 draws conditioned on uniqueness. Select a single candidate from pairwise development-root intersections by maximizing development savings minus cache construction cost; abstain when that score is nonpositive. Tie-break by numerical mask. Discovery charges six pair intersections and one unit per distinct nonzero candidate/development-target score probe. All arms use the same roots and exact shortest single-cache cost; optional use of the cache is allowed. The privileged oracle is given the deployment motif for free but pays its construction/checking cost; it is a planted-motif comparator, not a proven optimum over all caches.

At the nested deployment horizons 4, 8, 16, 32, 64, compare total baseline and charged cache work across seeds. At horizon 64 the shared arm costs 23,996 vs 40,960; shifted costs 42,062; null costs 40,634. At horizon 4 even the shared arm costs 2,720 vs 2,560. In dimension 6 independently enumerate every generator subset for all 64 cache values and 64 target values: 4,096 formula checks. See the source-hashed summary receipt and regenerate all 480 per-family/horizon rows with:

    python src/spiral_ln/evaluation_vad.py > /tmp/vad_01a_full.json

    PYTHONPATH=src python -m pytest -q tests/test_evaluation_vad.py

The planted motif is a synthetic construction. The shifted and null results show why transfer and discovery overhead must be charged; the null regime itself has real opportunistic reuse. Fixed public seeds make this a reproducible development control, not an untouched holdout for future model selection. Nested horizons are correlated, not independent replications. Generator-reference counts and abstract probe units deliberately omit physical inference/Lean costs.

## Evaluation feedback risk

If k proposed abstractions have independent fair Bernoulli development success and equally fair independent deployment success, selecting any development winner (or a fixed fallback when there is none) gives apparent success probability 1-2^(-k), while the selected candidate's deployment success probability remains 1/2. For k=8 this gives 255/256 vs 1/2. The independence assumption is essential: this is an exact toy selection witness, not a distribution-free bound. EvalMath's existing feedback-channel and adaptive selection-risk framework should be used when the abstraction proposer observes repeated verifier feedback. A valid lemma can still be selected for an overoptimistic estimate of reuse. Log all candidate queries, rejected abstractions, verifier errors and the selection transcript; freeze the library before sealed deployment.

## VAD-01B: prospective downstream gym (proposed)

Use 256 target statements in 32 independently generated families, with a separate training corpus. Freeze generator, seeds, target hashes, family splits, toolchain, allowed imports and budget before running. Start with finite algebra, graph invariants and Boolean polynomial identities. Use 16 families for development and 16 fresh families for sealed transfer; for each fresh family separately assess a no-adaptation transfer slice and a declared within-family adaptation slice, disjoint from final scoring. Commit sealed hash manifest before revealing roots. Use a prefix-only environment or transitive dependency filter so a target or its descendants cannot serve as a premise. Match intended theorem statements with independent comparators, reject sorryAx and unexpected axioms, record kernel replay and dependency DAG.

Arms: independent proof search, standard premise retrieval, symbolic candidate extraction, TRM lemma proposer, recurrent TRM with persistent verified lemma memory, privileged oracle-supplied abstraction. Match model parameter counts, calibration roots, retrieval access, verifier limits, maximum work and wall time across comparable arms; account separately for oracle information. Add size-matched random cache and shuffled family labels. Include shifted families, syntactically renamed tasks, and null families without a planted invariant. Preserve all failed attempts and candidate evaluations. Use family-level paired estimates, report closure and resource use separately; compare cost on all assigned targets under a common failure penalty or at fixed success/compute frontiers, not only completed proofs. Report physical wall time, model tokens/FLOPs, kernel calls, search work, memory/index cost, library construction and verification. Predeclare weights if aggregating heterogeneous resources and include sensitivity analysis. Freeze policy and library before sealed evaluation. Require independently verified statement fidelity, zero prohibited dependencies and zero admitted proof steps.

Suggested advancement gate, to freeze prospectively: no decrease in held-out closure versus the strongest matched non-neural baseline; positive net savings at matched closure on sealed families after full charging, with a paired family-level interval above zero; ablation of persistent memory; no unexplained advantage from leaked targets. A failed gate is informative. An independent reviewer must approve the split, cost accounting and leakage checks before running. Model training/execution belongs in a downstream gym such as LoopedTransformers or DataGoblin, leaving EvalMath as the exact oracle and protocol registry.

Open problems: multiple caches with dependency-aware discovery, optimum cache selection, generalization bounds after adaptive verifier feedback, and Lean formalization of the one-cache cost identity. No claim that a finite XOR cache captures the full content of an auxiliary PDE.
