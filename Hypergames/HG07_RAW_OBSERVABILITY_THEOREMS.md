# HG-07: Raw-state parity identification, posterior nullspaces, and CPU learners

**Evidence status:** exact algebraic identities plus independent finite `F₂` enumeration. The companion PyTorch trial measures a particular synthetic 6-sparse parity generator and lightweight linear/flat/weight-tied networks, without inference on a pretrained foundation model or a playable Storyworld.

## 1. A hidden goal is an unknown parity operator

Let each observed world state be `x ∈ F₂^d`. An unknown target row `p ∈ F₂^d` generates label `y=p·x`; with k goals, `P ∈ F₂^{k×d}` and output `y=Px`. The agent receives n training pairs; the design is `X ∈ F₂^{n×d}` and observed labels `Y=XPᵀ`. It must predict new goal labels, then choose whether to release a candidate output under +10 for correct, −15 for incorrect and 0 for abstaining.

### T1: posterior parity fibre (algebraic identity)

For any consistent training design, the set of solutions for one goal row is the affine coset `p₀ + ker X`. It has exactly `2^(d−r)` members, where `r=rank_F₂(X)`. Under the independent uniform prior on k target rows, there are `2^((d−r)k)` consistent goal matrices. This holds even if the training inputs include duplicates or zeros. `fit_raw_system` obtains an exact partial predictive map using elimination; every query `x` in `rowspan X` has one determined label.

### T2: fresh-query observability (algebraic identity)

For a query `x`, its target label is identified by all consistent parity hypotheses iff `x ∈ rowspan X`. Otherwise, toggling a kernel vector `v` with `x·v=1` flips the label while retaining all training observations. With k independent uniform target-row priors, a nonidentifiable query has a uniform k-bit output, giving optimal exact-code success `2⁻ᵏ`. The fraction of all uniformly sampled query vectors that lie in `rowspan X` is `2^(r−d)`. Hence expected Bayes exact-code success for one uniform future query is

`2^(r−d) + (1−2^(r−d)) 2⁻ᵏ`.

The test is explicitly **conditional on the unrestricted uniform parity prior**. The actual HG-07 generator chooses six-sparse targets, so the posterior after data can be sharper than this unrestricted linear-algebra certificate.

### T3: sparse identification union bound (algebraic identity)

Fix one true six-sparse target `p`. Under independent uniform training vectors, for any competing `q≠p`, `Pr[Xp=Xq]=2⁻ⁿ`. There are `C(d,6)−1` other six-sparse rows. Union bounding gives

`Pr[∃ wrong six-sparse q matching all n labels] ≤ min(1, (C(d,6)−1)2⁻ⁿ)`.

This is a sufficient sample-identifiability bound with an exhaustive hypothesis class. It makes no claim about tractable optimization of a learned neural representation. At 512/2048 samples the bound is tiny even for d=512, so a neural learner stuck near 50% accuracy points to its optimization/inductive bias, rather than intrinsic absence of enough labels to identify a six-sparse parity.

### T4: affine linear readout obstruction (algebraic proof)

No affine threshold function of all d raw bits equals a parity of six selected bits at every input. Fix four of the six active bits and all nuisance bits. The remaining binary square is XOR or its complement. Both opposite corners have one class and the other two corners the other class. A separating affine functional would require incompatible inequalities after summing the two diagonals. Thus a linear classifier is a meaningful below-ceiling control, even though it may exceed chance on finite samples by fitting noise.

### T5: nuisance padding is identifiable but training-dynamics sensitive

For any fixed target mask supported on the first 140 coordinates, adding zero target coefficients on nuisance coordinates leaves the target function and its oracle accuracy invariant. A neural model trained on a 512-dimensional input projection receives extra independently initialized weights and nuisance activations. Neither finite-step training trajectories nor sample-limited generalization are forced to match those in 140 dimensions. HG-07 records this as an empirical robustness test, rather than assuming exact padding invariance for the learner.

## 2. Experimental separation

The `linear_task`, `flat_task`, and `loop_task` conditions receive raw binary input and goal labels only. `loop_true_fragment_aux` has privileged labels for the three two-sparse parities composing each six-sparse goal and reports both its direct goal head and its composed XOR of three thresholded fragment heads. `loop_shuffled_fragment_aux` has permuted fragment labels under an otherwise identical loss and architecture. Comparison with the true-aux condition therefore measures the *value of a labelled decomposition*, not spontaneous unsupervised fragment discovery.

The exact GF(2) training interpolator provides an information-recovery baseline using the disclosed linear model family; a true-goal oracle would be a privileged structural ceiling. One hundred randomly selected six-sparse rank-k parity readouts measure chance alignment. Those random controls have the same label budget and goal-output rank, while their search computation differs from backpropagation.

## 3. Verification and limits

`src/spiral_ln/evaluation_hypergames_raw.py`, `tests/test_evaluation_hypergames_raw.py` and `scripts/verify_evaluation_hypergames_raw.py` independently enumerate finite rowspace predictions and posterior counts for small dimensions. The source-hashed receipt lives at `output/evaluation_hypergames/hg07_math_v1.json`.

The experiment's PyTorch public CPU results are reported separately in `paper/hypergames_hg07_raw_recurrent_results.md`. The split-specific input generator uses SHA-256-derived Python PRNG seeds and common 512-bit source vectors for exact low-coordinate padding. Training uses CPU float32. Small differences between operating systems or BLAS/PyTorch versions can affect network optimization; the per-seed rows are empirical measurements, not a cross-platform byte-identical kernel proof. The HG-03 private held-out manifest is not accessed.
