# HG-07: Raw-state recurrent compositional goal learning

**Status:** registered public CPU benchmark with exact EvalMath references. HG-07 registration was committed to GPTStoryworld at `2b948b467fc9847d86cab00f65127cff6e77aa78` before local smoke tests and before the registered six-seed training sweep. EvalMath theorem targets were frozen at `b6404d26e4089ab7134451cac644b64079431a2c`.

The scientific question is whether weight-tied recurrent layers with a 64-dimensional carried state learn arbitrary six-sparse parity goals from raw binary inputs, with a k=1/2 goal-code output and no task-visible feature library. Padded 512-D worlds reuse the first 140 variables of the core task, preserving the true goal and all data; native-512 goals use the whole 512 coordinates. A 6-seed, 3-cohort, 2-rank, 2-label-budget grid is evaluated for 5 CPU-trained arms, each with 350 AdamW updates and separate 256-example calibration and 256-example scoring splits.

The true-fragment auxiliary network is provided the teacher's exact three two-bit intermediate labels during training. Its composed readout is a privileged supervision experiment. Shuffled fragment labels, task-only recurrent training, one-pass flat cells and an affine linear model test the effect of this intervention and recurrent computation. The GF(2) solver is a symbolic task-family baseline that must be interpreted with its unrestricted parity prior and full-rank criterion.

## Prospective hypotheses

H1: true-fragment-aux composed output beats the recurrent task-only direct goal head on at least four of six paired core-140/k=1/n=2048 seeds.

H2: recurrent task-only beats flat task-only under the same pairing on at least four of six seeds.

H3: each neural arm remains within 0.05 absolute joint accuracy between 140 and padded 512 dimensions on at least four of six core/k=1/n=2048 pairs.

H4: the GF(2) baseline at n=2048 has full rank and exact 256/256 raw parity predictions for all seeds, cohorts and goal ranks.

## Experimental results

**Finished public CPU census:** 360 fresh model fits across six seeded worlds × three cohorts × two goal ranks × two training budgets × five model arms. Every run used 350 updates on CPU, including 100 independently sampled rank-matched random parity controls per task/label budget (72 task-budget cells, 7,200 controls). The 360 recorded seed-arm rows live in `output/evaluation_hypergames/hg07/hg07_public_seed_rows.csv`. SHA-256: `053417219cc189208317823d5d944e5a9cc17c3eb0b50810986cdfcff933c81a`. The source-hash verifier independently reconstructs the output groups and checks 15 integrity conditions. Runtime: 251.777 seconds on Python 3.13.5, torch 2.10.0+cpu, numpy 2.3.5, two CPU threads. The training-reproducibility budget does not guarantee numerically identical floating-point operations across platforms.

### Preregistered results

| Gate | Result | Verdict |
|---|---|---|
| H1: true-fragment composed > recurrent direct, 140-D k1 n2048 | 2/6 seeds | **FAIL** |
| H2: recurrent task-only > flat task-only, 140-D k1 n2048 | 4/6 seeds | **PASS (weak)** |
| H3: core vs padded512 deviation <5pp, 140-D k1 n2048 | 4/6 to 5/6 for each of five arms | **PASS** |
| H4: GF2 full-rank exact recovery at n2048 | 6/6 seeds, all cohorts and k | **PASS** |

H2 is a directional count, not a significance result: four positive differences, one exact tie and one negative difference. The paired direct-correct differences (recurrent minus flat) on the six 256-item tests are `[4,4,4,25,0,-4]`. The H3 pass means both models behave similarly near the random-guess floor, rather than preserving useful learned goal information. It is a mechanistic control, not evidence of alignment.

### Mean joint-code held-out accuracy at 2,048 training examples

| Raw input | k | Affine linear | Flat 1-step | Tied recurrent 3-step | True fragment auxiliary (direct / composed) | Shuffled auxiliary (direct / composed) | Uniform-chance |
|---|---:|---:|---:|---:|---:|---:|---:|
| Core 140 | 1 | 49.80% | 49.48% | 51.63% | 49.93% / 52.80% | 51.37% / 50.85% | 50% |
| Padded 512 | 1 | 48.83% | 49.41% | 49.67% | 51.37% / 51.17% | 50.00% / 50.20% | 50% |
| Native 512 | 1 | 49.54% | 50.65% | 50.33% | 49.35% / 51.04% | 50.59% / 49.87% | 50% |
| Core 140 | 2 | 22.98% | 23.50% | 24.93% | 24.35% / 27.08% | 23.31% / 25.33% | 25% |
| Padded 512 | 2 | 25.91% | 24.67% | 24.15% | 26.30% / 26.56% | 24.74% / 25.78% | 25% |
| Native 512 | 2 | 26.56% | 25.91% | 26.76% | 27.60% / 25.59% | 26.17% / 25.72% | 25% |

Each mean aggregates six independently seeded 256-item test sets. Consult the executable CSV/JSON for exact fractions; percentages shown here are rounded. The auxiliary composed head is supported by privileged labels for the actual decomposition and cannot be interpreted as unsupervised feature discovery.

### Release calibration and failure

Of 360 neural fits, **one** passed the Laplace release criterion. It was the padded-512, k=1, n=2048 task-only recurrent controller on seed `2026111773`. Calibration got 155/256 exact predictions, producing `(155+1)/258 = 156/258 > 3/5`. Test accuracy was 129/256, with **127 unsafe releases** and mean true utility `−615/256` over its 256 test items. All other neural runs abstained, yielding zero utility. This is an example of calibration overconfidence near the hard release threshold, not a general rate estimate for deployed models. The test set never influenced the decision to release.

### Exact raw-state algebraic comparator

The unrestricted GF(2) interpolator recovered every 256/256 test label when the training matrix reached full column rank. At 512 labels, all six 140-D core tasks had rank 140, and the 512-D padded/native examples had rank 510 or 511 (so the conservative solver abstained). At 2,048 labels, every cohort reached full rank (140 or 512) and the solver achieved **100%** on the held-out test sets. It is given a correct parity-model-family prior, making it a structural reference rather than an architecture-matched neural baseline.

The mathematical upper bound for a wrong six-sparse parity matching all training labels is `(C(d,6)−1)2⁻ⁿ`, truncated to one. At the registered 512 or 2,048 labels this bound is already small, yet the neural models fail to exploit the available information. This identifies an optimization/inductive-bias bottleneck in the tested architectures, while exact finite family knowledge solves the task.

### Limitations

The two-dimensional parity fragments are synthetically generated; true-aux uses their labels during training. The sample counts and seeds are public development measurements, and sample-specific noise can affect directional comparisons. No state-causal neural intervention, recurrent-state linear probe, pretrained Qwen, real storyworld environment or private HG-03 test was evaluated. The model's inability to learn random parity6 with 350 AdamW updates is an empirical finding about this setup. A stronger curriculum, sparse learner or active oracle would require its own prospective protocol.

The runnable neural experiment, calibration audit and seed-level data are published in [GPTStoryworld HG-07](https://github.com/MoralityLabAI/GPTStoryworld/tree/research/hypergames-hg07-raw-recurrent-20261117/verifiers_envs/storyworld-hypergames-env). This EvalMath companion contains the exact algebraic verifier and shared result note.
