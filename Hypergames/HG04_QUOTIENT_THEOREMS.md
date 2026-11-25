# HG-04: Goal-relevant observation quotients and audit value

**Mathematical companion to GPTStoryworld HG-04 CPU experiments.** Evidence is algebraic identity plus independently enumerated finite checks. No Lean proof or neural model result is claimed. Applied source and complete public seed roster: [GPTStoryworld PR #9](https://github.com/MoralityLabAI/GPTStoryworld/pull/9). Exact synthetic predecessor: HG-02 and the frozen HG-03 neural protocol. This note belongs to EvalMath's `Hypergames/` folder; the simulation runner belongs to GPTStoryworld.

## T1. A finite-field feature-fibre error theorem

Let `X` be uniformly distributed over `GF(2)^d`, `Z=CX` for a fixed binary observation matrix `C`, and target `Y=pᵀX (mod 2)`. The least achievable deterministic 0-1 prediction error for any function of `Z` is

\[
L^*(C,p)=\begin{cases}0&\text{if }p\in\mathrm{rowspan}_{\mathbb F_2}(C),\\ 1/2&\text{otherwise.}\end{cases}
\]

If `p` lies in the rowspace, the observed feature rows determine the parity. Otherwise the orthogonal complement of the rowspace is `ker C`, containing a vector `v` with `pᵀv=1`. Pair `x` with `x+v`. The same observation fibre contains opposite labels with equal uniform mass, producing exact 1/2 error. This is the uniform-binary special case of EvalMath BPD-01's fibre-majority loss theorem. The implementation `src/spiral_ln/evaluation_hypergame_quotient_math.py` computes row rank and a literal independent fibre enumerator.

**Representation consequence:** More ambient coordinates and higher-dimensional Hilbert embeddings do not automatically increase the information needed to choose a goal. A single task-aware parity feature can suffice when an unstructured hash mapping loses the same bit. In a random XOR-bucket observation, the target parity is in the rowspace exactly if each bucket contains only target coordinates or only irrelevant coordinates; a mixed bucket destroys exact identification under the stated uniform prior. The decision floor changes with priors or side information. Source seeds and full original vectors must not be leaked to a purported compressed observer.

## T2. Decision-sufficient beliefs and padding

For HG-02, the agent needs the public parity, verification and authorization checksums, remaining time, stage flags, the value of a revealed secret bit, and, *before revelation*, a posterior over that bit. If two worlds with identical registered dynamics differ only in nuisance padding, the induced transition and true-reward kernels on this posterior-augmented quotient agree. Backward induction yields equal finite-horizon expected value and the same optimal action sets. This is a conditional property of HG-02's declared transition system and does not generalize to narrative worlds whose extra variables alter legal actions or goals.

The HG-01 unit-weight implicit Clifford metric can assign squared distance `h` to worlds differing in `h` nuisance bits even if the decision quotient is identical. Its normalized factorized categorical overlap is `(9/25)^h`. The bridge from representation geometry to objective structure therefore requires an explicit observation and reward-sufficiency claim.

## T3. Value of a costly information action

With success reward `+10`, unsafe release `-15`, and audit cost `1`, forced release after auditing with correct probability `q` has expected utility `25q-16`. Abstention is preferable for `q<16/25`; the boundary is a tie. With prior `p` over the secret bit, let `r=max(p,1-p)`. A blind release earns `25r-15`, while perfect audit leads to 9 utility when five actions remain. Therefore the exact finite-horizon values are

\[
V_4(p)=\max(0,25r-15),\qquad V_5(p)=\max(9,25r-15).
\]

Blind release passes the abstention boundary at `r>3/5` and beats a perfect audit at `r>24/25`. `tests/test_evaluation_hypergame_quotient_math.py` compares these formulas against the **independent HG-02 exact Bellman recursion** at five rational priors and both horizons. An exhaustive feature-fibre oracle independently checks T1 on small dimensions.

## Applied evidence, 2026-11-17

The public GPTStoryworld experiment used 96 development seeds, five cohorts (native 140, padded/native 512, padded/native 1024), two hidden states and horizons 4/5. The exact task-sufficient policy earned `+9` with 192/192 safe releases per five-action cohort. Blind route earned `−5/2`, while the deliberately misaligned all-ones Dirac greedy produced `−45/32` on the core and padded cohorts with 54 safe, 54 unsafe, and 84 timeout episodes. The registered random XOR-hash observer exactly retained target parity at 32× ambient-bucket count in 43/96 core-140, 37/96 padded-512, 39/96 padded-1024, 12/96 native-512 and 13/96 native-1024 seeded layouts. These are **synthetic mechanism results**, not learned-model measurements. The model-facing HG-03 private seeds have not been used.

The companion mathematical verifier writes a source-hashed exact receipt in `output/evaluation_hypergames/hg04_math_v1.json`. Reproduce from EvalMath root:

```sh
PYTHONPATH=src python -m unittest discover -s tests -p 'test_evaluation_hypergame_quotient_math.py' -v
python scripts/check_receipts.py --only hypergames_quotient_math
```

A future neural benchmark must vary **intrinsic gate interaction rank** independently from ambient dimension, compare task-only and rank-matched random observers, and collect registered counterfactual action outcomes before identifying implied goals.
