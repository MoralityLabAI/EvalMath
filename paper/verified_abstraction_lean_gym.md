# VAD-05A — isolated Lean proof abstraction gym

Status: 2026-11-25. Local source-term audit and reference-cost experiment complete; Lean kernel replay pending. The VAD-01–04 parent commit c0e4836 passed CI before this addition.

## Design

Use core Lean conjunction trees with distinct propositional leaves, explicit hypotheses, and constructor-only proof terms. Every family contains four development targets and eight disjoint deployment targets. There are 16 separate global calibration families and 32 test families (eight each of shared concrete motifs, renamed motifs, shifted tree structure, and null random trees). Seeds are public and fixed. These are toy proof templates, not novel mathematical theorem discovery.

Four matched arms: direct constructor proof; concrete subtree matching; structural anti-unification by ordered binary tree shape; one global shape learned from the separate calibration families. The family-local arms see only their four development trees. A candidate of k leaves has direct reference cost 2k-1 and cache application cost k+1, so each matching subtree saves k-2 references. Matches of equal size cannot nest. Select the candidate maximizing projected development savings less construction cost, allowing abstention; ties are deterministic. Charge one unit for each visited subtree and distinct candidate scored, plus construction references. Charge global discovery/construction once over the full deployment set. These are abstract units, not measured physical work. Hashing, key formation, declaration/type costs, and shared development acquisition are not charged; source bytes are recorded separately.

Each generated file imports only Init, sets autoImplicit false, declares at most one generic cache and exactly one target, then prints axioms for both. Each target gets a fresh file and (with --lean) a fresh Lean process. No earlier targets are imported. A separate restricted-grammar parser checks the binders, reconstructs the statement from the explicit proof term and verifies exact agreement with the expected target tree. It rejects self-reference, unrecognized identifiers, admitted terms and changed arguments. This is a source-level grammar restriction, not a general Lean dependency auditor or sandbox. Generated files are trusted inputs to the compiler. No claim of kernel closure is made without replay.

## Results

256 roots, 1,024 generated files; all passed local grammar audit. Three local tests pass. Pooled reference counts direct/concrete/shape/global = 4626/4442/4160/4443. Including abstract discovery and construction charges gives 4626/6227/5898/5096. Thus direct proof wins the eight-target horizon. Shape generalization reduces raw proof references by 10.07% before its costs. Global cache uses 183 instances; shape uses 190; concrete uses 64. Concrete savings occur only in the shared regime. Source bytes include cache redeclarations in isolated files and should not be conflated with amortized construction.

An exploratory deployment sweep freezes all choices at their original eight-target horizon and extends each public family to 256 targets. Shape gain at H=8,16,32,64,128,256 is 0.7843, 0.9190, 1.0071, 1.0555, 1.0821, 1.0959. Global-shape gain is 0.9078, 0.9719, 1.0059, 1.0243, 1.0342, 1.0386. Concrete gain is 0.7429, 0.8677, 0.9464, 0.9916, 1.0159, 1.0285. Prefixes are nested, so this is descriptive and not a fresh sealed evaluation. No kernel execution in this sweep.

## Reproduce

    python scripts/verify_vad_lean.py --out /tmp/vad05
    python -m pytest -q tests/test_vad_lean.py
    python scripts/sweep_vad_lean.py --out /tmp/vad05_sweep.json
    cd lean
    lake env python3 ../scripts/verify_vad_lean.py --out /tmp/vad05_kernel --lean lean

The last command requires the pinned Lean toolchain. It fails on a nonzero compiler exit or any target/cache axiom report other than no axioms; per-file timing and output are written to kernel.json. The source-grammar audit is not a replacement for that step. A future gym must include inference-time accounting, genuinely difficult unseen claims, a transitive premise auditor for unrestricted Lean, and nontrivial abstraction invention controls. Train only after this kernel gate closes; the simple symbolic baseline is the comparator.
