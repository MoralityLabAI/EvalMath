# HG-06: Sparse fragment composition, finite-data aliasing, and goal quotients

**Evidence:** algebraic identities with independent finite exact checks; paired public synthetic CPU mechanism results. No Lean kernel claim, Qwen weights, or agent mental-state inference. Protocol registered 2026-11-17 at GPTStoryworld commit `d0732821a81aa6ebaa46b85309477c3af0638c50`; data came after registration. Parent lines: HG-04 and HG-05.

## Setup

A classical world is `x in F2^d` with uniform independent coordinates. A `k`-bit goal is `y = P x`, with each target row of Hamming weight six and the k targets on disjoint coordinates. The learner receives a *restricted two-sparse candidate feature library* `B`: observations have the form `z = B x`, where each row of `B` reveals the parity of two coordinates. The action predictor may XOR at most `m` candidate features per output, optionally complementing the result; an exact six-sparse target feature never appears as a candidate. Only public supervised labels `(z,y)` from the train split may choose those XORs. Independent calibration determines a decision to release; the test labels stay sealed until scoring.

### HG-06/T1: fragment-support obstruction (algebraic identity)

For any binary row masks `b1,...,bm`, the support of their XOR is a subset of the union of their supports:

\[
\operatorname{wt}(b_1\oplus\cdots\oplus b_m)
 \le \sum_{j=1}^{m}\operatorname{wt}(b_j).
\]

Thus any target with weight `s`, represented using rows of weight at most `w`, needs at least `ceil(s/w)` fragments. In particular, no two two-sparse rows can equal a six-sparse goal. Three disjoint pairs partitioning the six support coordinates exactly reproduce that goal. Both parts were independently enumerated at `d=6` over all 15 two-sparse rows; a literal perfect-matching witness uses masks `(3,12,48)` and target `63`.

For a *single predicted output* restricted to one/two feature rows, the target is outside the observer's row span. Under the uniform state distribution the optimum test-bit accuracy is exactly `1/2`. For a three-feature correct composition it is 1. A larger multi-output observer may mix other rows to form different readouts, so the per-output two-fragment restriction must remain explicit.

### HG-06/T2: multi-goal missing-component deficiency (algebraic identity)

If the k target supports are disjoint and each target has three disjoint two-coordinate component rows, the full fragment dictionary spans the k goals. After deleting exactly one component row per target, and adding only nuisance-only features whose supports avoid all target coordinates, the k missing components cannot be synthesized from the remaining rows. In the declared construction,

\[
\mathrm{rank}\begin{bmatrix}B_{\rm full}\\P\end{bmatrix}-\mathrm{rank}(B_{\rm full})=0,
\qquad
\mathrm{rank}\begin{bmatrix}B_{\rm ablated}\\P\end{bmatrix}-\mathrm{rank}(B_{\rm ablated})=k.
\]

The HG-05 row-space theorem gives `H(PX | BX)=h` bits and Bayes best exact-code success `2^{-h}`. Hence the full dictionary has the information to solve the task, whereas the ablated dictionary's restricted observer has a `2^{-k}` exact-code ceiling. The ceiling is for the **defined candidate-feature observation interface**, not for an agent given unrestricted raw-state coordinates and permission to invent other features.

### HG-06/T3: finite-label aliasing bound (algebraic identity)

For two distinct parity masks `r != p` and independent uniform training states `X_1,...,X_n`,

\[
\Pr[\forall t\le n:\; r\cdot X_t=p\cdot X_t]=2^{-n}.
\]

The difference `r⊕p` is a nonzero linear functional on `F2^d`, making each equality a fair independent bit. The same bound applies to its signed/complemented version when evaluated on fixed inputs. If the candidate library has `M=choose(|B|,3)` triplets, a conservative union bound for `k` targets is

\[
\Pr[\exists\ \text{spurious training-perfect signed triplet}]
 \le \min\left(1,\frac{k(2M-1)}{2^n}\right).
\]

This bound concerns distinct *functions*; duplicate triplets representing the same true parity are benign. At small n it can equal 1 and provides no useful assurance. The executable reports empirical numbers of signed triples consistent with the training labels. It also records 100 **representational-rank-matched** random triple controls per seed/cohort/pool/k. Their search effort differs from the exhaustive task-conditioned optimizer.

### HG-06/T4: exact nuisance-padding invariance (algebraic identity)

Embed `F2^d` in `F2^{d+q}` with appended arbitrary nuisance coordinates. If the target matrix and feature library have zero columns in the appended coordinates, and the new samples share their original low d bits, every feature and goal signature remains identical. Any deterministic learner with stable ordering and a fixed training/calibration budget therefore makes identical predictions and release decisions. The 4,608 paired comparisons in HG-06 check this condition for the registered fixed pool.

## Decision value and evidence boundary

The release contract pays +10 on correct exact-code submission, -15 otherwise, and 0 for abstention. Expected release utility is `25q-15`; the Bayes release threshold is `q>3/5`. The registered learner estimates reliability from 32 *separate* calibration examples using `(correct+1)/34`. This is a policy under a specified calibration rule, not a proof of external calibration.

The exact finite verifier checks 1,020 parity-collision cases and 144 independent observation-fibre cases, with additional boundary cases. The prospective CPU census comprises 24 public seeds, five cohorts, four k values, two dictionary pools, four label budgets, six deterministic arms and 100 random triple bases per condition. The model class is a finite XOR-composition selector and remains separate from learned LLM internal representations.

## Reproduce

From GPTStoryworld's `verifiers_envs/storyworld-hypergames-env`:

```sh
PYTHONPATH=src python -m unittest discover -s tests -p 'test_*composition.py' -q
PYTHONPATH=src python scripts/run_hg06_cpu.py --workers 2 --out output/evaluation_hypergames/hg06
PYTHONPATH=src python scripts/run_hg06_cpu.py --workers 2 --out output/evaluation_hypergames/hg06 --check
```

Run results against the committed compact SHA-256 manifest, or download the complete public seed-level CSVs from the dedicated GitHub Actions artifact. The EvalMath module `src/spiral_ln/evaluation_hypergames_composition.py` and its independent tests and verifier contain the exact mathematics.
