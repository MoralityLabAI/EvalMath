# IRC-02: timed predictive equivalence under a partially observed action interface

**Status (2026-10-29):** handwritten finite-horizon theorem and proof, exact rational reference with 16 local tests, independent policy-tree and hidden-world enumerators. These are synthetic finite results. No Lean compilation, model training, human-performance measurements, or real BCI observations are claimed.

## Ownership and scope

EvalMath owns this canonical finite theorem, oracle and source-hashed receipt. The downstream capacity and neural experiment protocol belongs to `MoralityLabAI/Compactification-Theory/experiments/interface-relative-compactification/`. Earlier work remains authoritative for its own scope: [IC-01](../research/interventional_compactification/README.md) owns general intervention commutation; [HC-01 PR #1](https://github.com/MoralityLabAI/Compactification-Theory/pull/1) owns deterministic behavioral-state quotients in learned chunking; [RC-01](https://github.com/MoralityLabAI/Compactification-Theory/blob/main/research/recurrent_circuits_v1/THEORY.md) owns the affine finite-field minimum-state theorem. [Plan R PR #3](https://github.com/MoralityLabAI/Compactification-Theory/pull/3) contains a narrower deterministic timed distinguishing-word oracle. This note adds public interface modes, durations, rational stochastic observations and adaptive future tests.

## 1. Model and declared interface

Fix a finite hidden-state set `S`, public interface modes `Q`, and a public remaining integer budget `d >= 0`. An interface mode includes the publicly available camera/selection state when relevant. At mode `q`, the public action menu is `A(q)`, and a legal action at remaining budget `d` must have every possible hidden-state branch duration at most `d`. This conservative rule keeps legality independent of hidden state and belief. Every branch duration `ell` is a **positive integer**. Horizon strictly decreases on every nonterminal transition.

For hidden state `s`, public mode `q`, and action `a`, the rational kernel is

\[
K_{q,a}(s',q',y,r,\ell,z\mid s),\quad z\in\{\mathrm{done},\mathrm{continue}\}.
\]

Here `y` and **reward `r` are both public observations**. Their joint feedback tuple also includes `ell`, `q'`, and `z`. Each row has nonnegative rational weights summing to one. All public feedback may affect the next decision. The `d=0` readout is a common zero terminal payoff with an empty future trace. Observation-only rewards require a different posterior updater and are outside this release.

A positive-probability history `h` fixes the current `(q,d)` and a posterior `b_h` over `S`. A continuation policy `sigma` is a causal tree mapping **future public feedback** to a legal action or stop. When two histories are compared, `sigma` is the same tree in each experiment: its private control logic cannot branch on which original history was supplied. The law of its entire public action/feedback/reward/time/termination trace is denoted `L_h^sigma`.

The finite exact-cardinality claim assumes a separately **declared finite set** `H_(q,d)` of candidate positive-probability histories in each stratum. This is satisfied by a fixed finite initial-seed set, bounded decision horizon, finite observations and actions, after taking reachable histories. All encoders and decoders see `(q,d)` at zero *variable-state* cost, but delivery/storage of these values must be charged in an end-to-end implementation.

## 2. Predictive equivalence theorem

Define within the same public stratum:

\[
h\equiv_{q,d}h'\iff \forall\sigma\in\Sigma_{q,d}:\quad
  \mathcal L_h^\sigma=\mathcal L_{h'}^\sigma.
\]

**Theorem IRC-02/T (finite timed predictive quotient).** Under the preceding assumptions:

1. This is an equivalence relation and the coarsest partition preserving all declared future trace laws.
2. If `h == h'` in this equivalence and `a` is legal, immediate public-event probabilities agree. After any event `e` with positive probability, the successor posteriors are equivalent at public `(q',d-ell)`. Consequently the quotient has a graded stochastic transition kernel, conditional on the observed event.
3. With `N_(q,d)` equivalence classes in a finite declared history set, the minimum number of **fixed-length mutable state bits**, reusing the public stratum field, is

   \[
   \boxed{M_{\min}=\left\lceil\log_2\left(\max_{q,d} N_{q,d}\right)\right\rceil.}
   \]

   This is a cardinality result. It charges neither the implementation of the quotient decoder nor the program/lookup-table description, which must be reported separately.
4. Exact rational backward signatures compute this quotient on finite instances. At remaining time zero the signature is the declared common terminal law; at `d>0` it lists, for each legal public action, the probability of every next public event and the successor signature for continuing outcomes.

**Proof.** Equality of all probability measures is an equivalence. A sufficient code must distinguish histories separated by some future experiment; class identifiers attain this bound. Fix a legal first action. The trace law fixes every immediate event probability. For a shared positive-probability event `e`, any distinguishing suffix on the conditional histories could be attached after `e`; its resulting joint probability would contradict equality of the first histories' trace laws. This gives the well-defined graded update. For the bit bound, each stratum requires `N_(q,d)` distinct codewords. One fixed field reused across independently supplied public strata needs at least the displayed number of bits; a class index achieves it. Lastly, positive durations strictly reduce the horizon. Exact next-event probabilities plus induction on successor signatures give equality of all adaptive suffix laws. If signatures differ, the first differing event probability or a shorter suffix after a positive event supplies a distinguishing experiment. `□`

**Decision corollary.** The quotient preserves expected reward for every policy on its public state and successive observed feedback, including optimal unrestricted interface value. A scalar value function alone cannot generally serve as the quotient.

**Caution.** This is a quotient on **posterior histories**, not an assertion that probability-trace equivalence of physical hidden states is probabilistic bisimulation. Exact state transition factorization for an arbitrary over-refined encoder is a separate condition. The horizon-indexed quotient is graded because each transition consumes time; treating it as a same-horizon congruence generally fails.

## 3. Linear test vectors: rank and memory are distinct

For each legal public event `e` after `a`, let `K_(a,e)` be the substochastic matrix over `S`. A legal event/action cylinder `w` has probability from belief row `b`:

\[
  \Pr_b(w)=bK_w\mathbf1.
\]

All adaptive policy-tree leaf laws are determined by these cylinder probabilities. Thus two beliefs are equivalent exactly when `(b-b')K_w 1=0` for every feasible cylinder, respecting its public modes and budget. The span of the column vectors `K_w 1` has rank at most `|S|`. That rank bounds the dimension of a linear predictive signature **without** bounding the number of distinct exact-valued signatures on a growing belief domain. For a hidden bit and an action `guess1` revealing a Bernoulli reward of probability `p`, the candidate beliefs `p=k/10` for `k=0,...,10` occupy eleven exact classes and require four fixed bits on that *finite* domain. The observation-vector space still has dimension at most two. Allowing all rational `p` gives infinitely many distinguishable classes.

## 4. Counterexample suite and expected values

All values here are exact for the stated toy contracts:

| Witness | Declared environment | Exact result |
|---|---|---|
| Value-only compression | Hidden bit posterior `p=1/4` or `3/4`; one-tick `guess0/guess1` | Both optimal values `3/4`, but `guess1` event laws differ |
| Deadline grading | Fair bit, `3/4` accurate one-tick probe followed by one-tick guess | `V*(d=1)=1/2`; `V*(d=2)=3/4` |
| Camera switching | `left` permits one-tick hit; `right` requires one-tick switch | At `d=1`, values `1` and `0`; at `d=2`, right value `1` |
| Hidden delayed effect | Action `arm` is silent, then `read` exposes hidden bit | Two pure priors equivalent at `d=1`, inequivalent at `d=2` |
| Deterministic HC-01 comparison | Four two-bit states, observed first bit after `hold` or `swap` | At `d=1`, `hold` gives two classes; `hold+swap` gives four |
| Posterior cardinality | Eleven two-state beliefs with distinct reward laws | Eleven classes, four code bits for declared candidate set |
| Mixed termination | Same action may end after one tick or continue after two | Event law tracks both duration and terminal flag; robust legality rejects action at `d=1` |
| Unreachable feedback | Deterministic hidden-state-specific readout | Posterior update excludes zero-probability events |

**Interface-relative optimality memory can be nonmonotone.** In a contract requiring all action-conditioned futures, expanding a nested action interface can only refine the exact future-test partition. If instead the contract is *zero regret relative to that interface's optimal policy*, adding a new action may increase memory demand (two guesses requiring one retained bit), or lower it (an unconditional `auto` action makes the hidden bit irrelevant). Do not conflate these criteria.

**Assumption failures.** Secret action availability changes the public information channel, so the action menu must be modeled as observable feedback or a new contract derived. Zero-time cycles invalidate the strictly decreasing-horizon induction. Unbounded horizons can yield infinitely many distinct reachable rational posterior states despite finite hidden `S`. Hidden rewards must not enter Bayesian conditioning. Float-based approximate equality is outside this exact theorem.

## 5. Independent finite verification

Canonical code: `src/spiral_ln/interface_relative_compactification.py`. Tests: `tests/test_interface_relative_compactification.py`. Source-hashed receipt: `output/interface_relative_compactification/irc02_v0_1.json`. Regenerator: `scripts/verify_interface_relative_compactification.py`.

The reference computes rational Bayesian successors; exhaustive action/feedback cylinder laws; a separate **raw hidden-state-mass** cylinder oracle without Bayesian updating; recursive predictive signatures; an exact Bellman oracle with the option to stop; and a shortest distinguishing cylinder compiled to a legal conditional policy tree. Test code also enumerates every deterministic feedback-adaptive policy tree for the two-round fixture and computes its whole trace distribution by direct hidden-state propagation.

Tests include 4,800 declared pairwise equivalence comparisons on the fixed binary-probe family, 60 direct-world cross-checks on that family, 40 seeded random small two-mode kernels, timing/legality failures, and the HC-01 deterministic specialization. Reproduction is required in normal and `python -O` modes. Exact tests are finite evidence for the implementation; the preceding general statement is a handwritten proof until Lean review.

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_interface_relative_compactification.py' -v
PYTHONPATH=src python -O -m unittest discover -s tests -p 'test_interface_relative_compactification.py' -q
python scripts/verify_interface_relative_compactification.py --output /tmp/irc02.json
python scripts/check_receipts.py --only irc02
```

### Review gates

A PR must reject invalid kernels, negative or Boolean deadlines, zero duration, incomplete probability mass, changing hidden legality, and exact source-hash mismatches. Every claimed distinguishing trace must replay legally within the deadline and have positive probability under at least one compared belief. Independent raw-world and full adaptive-policy enumeration must match the signature quotient. A minimum-bit result must be explicitly limited to its finite candidate history set. Neural/human claims remain **inconclusive** until interfaces and budgets are measured and a preregistered evaluation exists.

Future tasks, separately owned: exact finite Lean statement and proof, rational TV coupling bounds, partial-feedback hidden-reward extension, finite-field affine cross-check against RC-01, and capacity-frontier experiments. Existing E10, RC-01, HC-01 and theorem-fidelity PR owners retain their paths and work.

## Sources

- Littman, Sutton and Singh (2001), [Predictive representations of state](https://papers.nips.cc/paper_files/paper/2001/hash/1e4d36177d71bbb3558e43af9577d70e-Abstract.html).
- Geiger et al. (2025), [Causal abstraction: a theoretical foundation for mechanistic interpretability](https://www.jmlr.org/papers/v26/23-0058.html).
- Bian and Abate (2017), [Bisimulation and trace equivalence in an approximate probabilistic context](https://research.google/pubs/bisimulation-and-trace-equivalence-in-an-approximate-probabilistic-context/).
- Precedents and resource cautions: existing HC-01, IC-01 and RC-01 notes linked above.
