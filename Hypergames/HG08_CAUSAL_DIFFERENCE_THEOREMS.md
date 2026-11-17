# HG-08: Exact causal difference and support-certificate mathematics

The experiment's public synthetic generator is in GPTStoryworld's `verifiers_envs/storyworld-hypergames-env/`. This EvalMath component states the transferable theorems and verifies finite cases independently. The preregistration was committed at `677735b6dbc336df6935f6fc78921fc37dcc97f2` before CPU outcomes; the applied data were registered in GPTStoryworld at `a54c806b0c9b16219d9e823aabd399361078fc7e`.

Let `F_2` be the two-element field, `P in F_2^{kxd}`, and `f_P(x) = Px`.

**Exact intervention difference:** for arbitrary baseline x and coordinate flip vector s,

`f_P(x+s) - f_P(x) = Ps`.

**Verified support recovery:** a subset whose residual group-parity response is one contains an odd number of unlocated support coordinates, even after subtracting the contribution of known positives. Recursive binary partitioning therefore identifies at least one true support coordinate. Verifying each candidate with the singleton intervention records an exact witness. Under a separately declared exact row weight of six, six unique positive singleton certificates determine the complete support row. The certificate relies on the row-weight prior; if this assumption fails, an apparent complete row could omit causes.

**Sparse information lower bound:** a uniformly sampled one-output six-sparse support has `binom(d,6)` possible values. Any exact adaptive binary-response intervention identification strategy requires at least `ceil(log2 binom(d,6))` queries in the worst case. Numerically this is 34 at d=140, 45 at d=512, and 51 at d=1024. An arbitrary group intervention counts as one query in the registered model, so this cost model differs from independent physical single-coordinate interventions.

**Residual rank and release:** for a uniform fresh x, a parity row `p` outside the rowspace of known observations `C` retains one bit of conditional uncertainty. More generally `h=rank([C;P])-rank(C)` gives ideal joint-code success `2^{-h}` when the goal parity is fixed and x is uniform. One unidentified bit yields expected forced-release utility `25/2 - 15 = -5/2` at the HG-02 reward contract; abstention gives zero. The full hard support certificate implements fail-closed release with exact predictions in the noiseless model.

The mathematical module `src/spiral_ln/evaluation_hypergames_causal.py`, test `tests/test_evaluation_hypergames_causal.py`, and verifier `scripts/verify_evaluation_hypergames_causal.py` check these statements using integer bitmasks, Fractions, and enumerated small state spaces. **No Lean proof is claimed**. The applied HG-08 neural sub-study failed its H5 direction gate (causal-masked test accuracy beat raw on 1 of 6 paired seeds), despite successful causal support recovery. These are separate statements about identifiability and gradient optimization.
