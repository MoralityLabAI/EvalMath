# HG-06: Compositional latent goal recovery in high-dimensional storyworld abstractions

**Status (2026-11-17):** synthetic CPU experiment; prospective protocol registered in GPTStoryworld at `d073282`. The registered 24 public development seeds and all six deterministic-arm outputs were computed after registration. HG-03 private seeds remain sealed, and no Qwen / other neural model is evaluated.

## Question

HG-05 supplied the exact six-bit goal masks as unidentified candidate dictionary atoms. HG-06 removes those goal atoms. Instead, the learner must identify their decomposition into three two-bit parity fragments. We hold the *intrinsic target interaction* width and rank fixed while varying ambient dimension and distractor dictionary size. A two-fragment decoder has a provable representation limit; a three-fragment decoder has sufficient capacity.

See `Hypergames/HG06_COMPOSITION_THEOREMS.md` for the GF(2) support obstruction, structural missing-fragment information deficit, the `2^-n` training-collision law and an upper bound on false training-perfect compositions.

## Protocol

24 public seeds `202611170600..202611170623`; five 140/512/1024 native or padded cohorts; k=1/2/4/8 disjoint six-bit goals; fixed/ambient candidate pools; 8/16/32/64 labels; 32 calibration and 128 held-out synthetic test examples per cell; 100 rank-k random triple bases. The candidate dictionary contains 3k correct two-sparse fragments in shuffled order plus independent nuisance-only two-sparse decoys. An ablation replaces one necessary fragment per target with another nuisance row of identical width, preserving dictionary size and withholding exact goals.

All controls observe the same training labels, with the following search classes: direct privileged goal ceiling, best 1-fragment signed parity, best 2-fragment signed parity, best 3-fragment signed parity, 3-fragment search on the ablated dictionary, and label-shuffled 3-fragment search. Random triple bases are matched for output rank and label access. Their search work is smaller than that of the task-only fitter, so this comparison is a rank-matched null distribution rather than a compute-matched causal attribution.

## Results: exact joint-code accuracy

At **64 training examples**, the task-conditioned 3-fragment solver scored 128/128 test examples on **24/24 public seeds** for each k in the core-140 fixed-pool cohort. In those same paired cells, it beat the two-fragment controller on **24/24** seeds at k=1,2,4,8. The registered 20/24 direction criteria therefore passed for all four ranks.

### Eight-label scarcity with ambient-expanded feature pools

| k goal outputs | core 140 accuracy | padded 1,024 accuracy | native 1,024 accuracy |
|---|---:|---:|---:|
| 1 | 0.9196 | 0.5143 | 0.5495 |
| 2 | 0.4310 | 0.2510 | 0.2523 |
| 4 | 0.0749 | 0.0628 | 0.0745 |
| 8 | 0.0046 | 0.0039 | 0.0039 |

The more populated ambient dictionaries admit additional accidental training-perfect three-fragment explanations. In the fixed-pool padding control, every scored field remained identical across 4,608 paired core-versus-padded comparisons. Ambient dimension alone made no difference when the task's observable feature dictionary and low-coordinate examples were held constant.

### The sample-size transition

Native-1,024 / ambient, 16 labels: k=1 reached 0.9788 mean joint-code accuracy, k=2 0.9600, k=4 0.8444 and k=8 0.2311. At 32 labels, all k reached 1.0. On the fixed core-140 library, 16 labels sufficed for k=1, while k=8 reached 0.2529, then 1.0 at 32 labels.

At k=8 and 64 labels in core-140 fixed, three-fragment composition achieved 1.0 exact-code accuracy and mean release utility +10. The two-fragment policy scored 5/768 exact-code accuracy; the missing-component and shuffled-label controls each scored 1/256. All three controls abstained throughout that group (mean utility 0). Under the registered 3/5 calibration gate, the trained composite policy released safely for 24/24 seeds with zero false accepts.

The 100 random-basis comparisons (24 independent seeded blocks per k) gave median within-seed empirical rank p-values of 2/101 for k=1 and 1/101 for k=2,4,8 at n=64. This is a finite matched-null ranking, not an externally blinded model-comparison p-value.

## Evidence and limitations

- Algebraic identity: three two-sparse fragments are necessary and sufficient to represent the constructed six-sparse goal using XOR; the rowspace deficiency determines the uniform-prior best success with the defined observation interface.
- Independent finite verification: 1,020 brute-force parity collisions and 144 exact observation fibres, plus width/edge and posterior-boundary tests.
- Synthetic mechanism result: 23,040 recorded seed-arm rows, 96,000 matched random triple draws, 4,608 exact padded-pair comparisons. All registered directional gates passed.
- Important boundary: a decoder allowed to inspect raw coordinates and invent new features could bypass the restricted dictionary. HG-06 tests **feature-library compositional learning**, with its underlying target structure deliberately generated, and provides no evidence that an LLM spontaneously discovers the same representations.

The next prospectively registered study should include a learned model whose architecture must discover the two-coordinate fragments from raw coordinates and a separate frozen evaluation of actual storyworld gate sequences. Avoid scoring a one-step parity objective as a complete test of alignment.
