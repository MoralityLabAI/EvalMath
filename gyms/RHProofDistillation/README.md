# RHProofDistillation: provenance-first Lean reconstruction gym

This is an experimental, CPU-first gym in EvalMath. It pins a few actual declarations in the 20 November 2026 Alpöge–Claude claimed RH/Dirichlet-GRH formalization, then asks a reasoner to reconstruct small, separately stated logical consequences in Lean. The four exercises here are **proxies** with explicit hypotheses, not extracted proofs of RH.

## Provenance and verification scope

- Original announcement: https://alpo.ge/remark.pdf . The central proposed theta-lift chain length is approximately sqrt(X).
- Community source mirror: https://github.com/leanprover-community/riemann-hypothesis . anchors.json pins a mirror commit, six Git blob hashes and declaration names. The published archive SHA-256 is also recorded.
- Independent verification: https://math.mit.edu/~drew/grh/ . As of its 2026-11-20 22:05 UTC snapshot, 175,187 modules compile, standard-axiom and module-kernel audits pass, independent kernels accept the exported proof and some end-to-end checks remained running.
- Principal-statement and dependency catalogue: https://andrewodesky.com/rh/ . Human-readable statement annotations and module-import edges have separate evidence status.
- The audited GRH statement applies to Dirichlet L-functions. Wider Artin and automorphic GRH are not the scope of this gym.
- The upstream archive does not grant a source-code license. We record links, identifiers and hashes without copying its source.

## Anchors inspected in the actual source

| Transition | Declaration | Path under src/ |
| --- | --- | --- |
| Final RH | riemannHypothesis | Main.lean |
| Target definition | DirichletLNonvanishingRightOfHalf | Statements.lean |
| All character conclusion | UpperTheory.FinalTheorems.everyCharacter | Development/AutomorphicArithmetic/CharacterBoxes/MainConclusion.lean |
| Interval Landau implication | zeroFree_of_rpow_window | Development/AutomorphicArithmetic/DedekindLFunctions/LandauTheorems/ZeroFreeOfRpowWindow.lean |
| Smoothed prime-sum estimate | UpperTheory.Comparison₂.core_gm | Development/AutomorphicArithmetic/PrimitiveCosets/CoreGm.lean |
| Theta-to-Galois wrapper | galoisLocalGlobalStrong_recParameter | Development/AutomorphicArithmetic/Foundations/GaloisRepresentations/IntegralStructures/RowSrc.lean |

A short wrapper still depends on its prerequisites. The scanner reports **module imports only**. It does not claim a minimal theorem-dependency closure. Full theorem-term dependency extraction and formal statement matching are later stages.

## CPU tests

From the EvalMath root, use the standard EvalMath Python environment:

    PYTHONPATH=src python -m spiral_ln.rh_distillation preflight
    PYTHONPATH=src pytest -q tests/test_rh_distillation.py

With a checkout of the source mirror pinned by anchors.json:

    PYTHONPATH=src python -m spiral_ln.rh_distillation audit --source-root /path/to/riemann-hypothesis --limit 5000 --output /tmp/rh-audit.json

The audit verifies all six expected Git file blobs and declarations, then walks imports from Main. Limit 0 means no traversal cap. Results explicitly label truncation, unresolved internal imports and external dependencies. A missing checkout is an error rather than synthetic evidence.

## Lean kernel scoring

Supply a JSONL file of objects with id and proof, where proof contains tactics replacing the single __PROOF__ hole in the corresponding template:

    PYTHONPATH=src python -m spiral_ln.rh_distillation grade --submissions gyms/RHProofDistillation/gold.jsonl --lean-cwd lean --require-all --output /tmp/rh-replay.json

The grader compiles each candidate via lake env lean in the existing EvalMath Mathlib project. It rejects admitted/unsafe proofs before compilation, records individual runtimes, and accepts only successful Lean processes. gold.jsonl is a **public smoke-test reference**, and should be excluded from held-out prompts. It is not a claimed proof of any upstream theorem. Gold Lean compilation is scheduled in CI; only Python preflight has been run locally.

## Next research stages

First extract declaration-level dependencies from exported Lean proof data and compare them with the import graph. Then identify and reprove explicit intermediate obligations in the Landau bound, theta scalar, Galois localization and covolume chain. Held-out tasks should split by dependency component, with exact provenance, contamination audit, compilation receipts and per-proof resource use.

Evidence levels here remain those used in EvalMath: a compiled Lean theorem, a finite test, a source-verified declaration and an open research conjecture are distinct claims.

## Second pass: source-site proof ledger and dependency probe

See [core_gm_proof_map.md](core_gm_proof_map.md) and [core_gm_sources.json](core_gm_sources.json). The two new exercises RH-D-005/006 reconstruct the +7-epsilon bookkeeping of the prime-sum bound. `spiral_ln.rh_dependency` builds a separate Lean probe using `ConstantInfo.value? (allowOpaque := true)` and `Expr.getUsedConstants`, with a toy-compilation smoke check in CI. An upstream proof-term graph is reported only after the compiled pinned mirror has been inspected; the ledger is based on source call sites.

## Character-balance and size-window benchmarks

Tasks RH-D-009 through RH-D-011 are new isolated Lean subgoals suggested by the source-verified `CharacterBalanceMoves.core` and compiled `proposition_size_bound` references. They test cancellation of finite-group averaging, aggregation of a double-indexed local correction, and real-power bound propagation. The real analytic and geometric hypotheses remain explicit. Each reference proof is compiled by the standard Lean CI grader; the gold proof file is intended only for smoke tests.
