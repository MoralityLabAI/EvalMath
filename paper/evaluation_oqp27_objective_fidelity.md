# OQP27: exact objective-fidelity probes for Bell witnesses (v0.1)

**Evidence:** exact finite enumeration, rational witnesses, algebraic extension of linear
inequalities to convex hulls. The external PSI quantum, facet-rank, noise and KL theorems are
**cited only**; no Lean kernel replay or model-agent evaluation is claimed.

## Source pin and correspondence

At PSI repository commit `da37af2ae174687403fbd97e9673c819edee71fd`:

- [`CGLMPBounds/Defs/CGLMP.lean`](https://github.com/physical-superintelligence/oqp-batch-2026/blob/da37af2ae174687403fbd97e9673c819edee71fd/oqp27-cglmp-inequalities/lean/CGLMPBounds/Defs/CGLMP.lean) (Git blob `3889781d058966e336305d8a646cfbb8aaa98bdf`): residuals and normalized CGLMP witness.
- [`CGLMPBounds/Defs/BGP.lean`](https://github.com/physical-superintelligence/oqp-batch-2026/blob/da37af2ae174687403fbd97e9673c819edee71fd/oqp27-cglmp-inequalities/lean/CGLMPBounds/Defs/BGP.lean) (Git blob `8a1bc93bd4b237112f90a2d170ebd09ac3885644`): BGP inequality coefficient vector and matrix.
- [`CGLMPBounds/BGP/Facet.lean`](https://github.com/physical-superintelligence/oqp-batch-2026/blob/da37af2ae174687403fbd97e9673c819edee71fd/oqp27-cglmp-inequalities/lean/CGLMPBounds/BGP/Facet.lean) (Git blob `096475ee8611beb3d7bdcd24fd540e23a6c062a4`): claimed 72/144/40 histogram and the rational perturbation.
- [`docs/FIDELITY.md`](https://github.com/physical-superintelligence/oqp-batch-2026/blob/da37af2ae174687403fbd97e9673c819edee71fd/oqp27-cglmp-inequalities/lean/docs/FIDELITY.md) (Git blob `10f3e7c3ce2672b25555ee851f0f9c18cb9a52b3`): scope of the Lean statements and the full distinction between witness threshold, global noise resistance and KL statistical strength.

Independent code transcribes the published coefficients and enumerates all 256 local deterministic
strategies `(a0,a1,b0,b1) ∈ {0,1,2,3}⁴`. It computes each value twice, first from the four outputs
and then by evaluating the complete conditional-probability table. All arithmetic uses
`fractions.Fraction` and integers.

## Exact findings

With `(x,y) ∈ {0,1}²`, define the four CGLMP residuals as
`r00=[a-b]4`, `r01=[b-a-1]4`, `r10=[b-a]4`, `r11=[a-b]4`, where brackets mean the
representative in `{0,1,2,3}`. Define `I₄(p) = 4 - (2/3)∑xy E(rxy)`.
Each deterministic strategy has a residual sum congruent to `-1 (mod 4)`, and the exact census is:

| Witness | Value | Number of vertices |
|---|---|---:|
| `I₄` | `2` | 80 |
| `I₄` | `-2/3` | 160 |
| `I₄` | `-10/3` | 16 |
| BGP `F` | `0` | 72 |
| BGP `F` | `-1` | 144 |
| BGP `F` | `-2` | 40 |

Because each functional is affine and the local polytope is the convex hull of the 256
vertices, the bounds `I₄ ≤ 2` and `F ≤ 0` follow for **every local behavior**.
This establishes local validity using a finite exhaustive certificate; it is not a proof of
facet rank or a statement about quantum maximization.

### Objective substitution and quantifier fidelity

The CGLMP and BGP sets of maximizing deterministic strategies have **24 vertices in common**.
Of 80 CGLMP maximizers, 56 fail to maximize BGP; of 72 BGP maximizers, 48 fail to
maximize CGLMP. The worst transferred losses are `2` BGP units and `16/3` CGLMP units.

A claim that *every* maximizer transfers is false in each direction; a claim that *some*
maximizer transfers is true. This tie-quantifier distinction is part of the benchmark.
Optimizing the named Bell functional never licenses an inference about an unrelated
statistical objective without an explicit implication proof.

### Rational, no-signalling witness

Average the 72 BGP-saturating deterministic tables to obtain `p̄`. All 64 conditional
probabilities of `p̄` are at least `1/72` and `F(p̄)=0`. At input pair `x=y=0`,
add `1/144` to cells `(a,b)=(0,1),(3,3)` and subtract `1/144` from
`(0,3),(3,1)`, producing `p⁺`. The perturbation has zero row and column sums,
so it preserves normalization and no-signalling, with nonnegative entries.

Direct rational evaluation gives `F(p⁺)=1/144 > 0`, proving `p⁺` lies outside the
local polytope, while the *fixed, supplied labeling* of the CGLMP witness evaluates
to `I₄(p⁺)=1/9 ≤ 2`. This illustrates a witness-specific blind spot; it does not
claim that every relabeling or every CGLMP inequality misses `p⁺`.

## Adversarial benchmark protocol

1. **Recovery task:** give an independent solver the Bell scenario and the published coefficient
   matrices but hide the histograms and counterexamples. Ask for a rational certificate of the
   two local bounds, including the exact number of saturating vertices. Score equality of
   the full three-bin histograms, not agreement on the bound alone.
2. **Objective-drift task:** ask whether finding a maximizer of `I₄` certifies an `F` maximizer.
   Score both the universal and existential interpretations, the shared count and explicit
   witness strategies. Present the reciprocal task to detect memorized one-way answers.
3. **Counterexample task:** ask the solver to construct a rational no-signalling table with
   `F(p)>0` and `I₄(p)≤2`. Require complete normalization, nonnegativity, marginal
   consistency and exact objective values, checked from the *returned full table*.
4. **Source-fidelity task:** ask which of PSI's projective CGLMP-rigidity, global noise, KL and
   four-outcome facet/no-fusion results follow from this finite certificate. The accepted
   answer scopes them as distinct external theorems requiring fresh upstream proof replay.

The current program supplies an exact reference oracle for the first three tasks and
mutation tests for a missing residual offset, altered BGP coefficient, omitted marginal,
invalid no-signalling table and silently weakened `∀`-to-`∃` optimizer transfer.
Running a language-model solver and independently compiling PSI's Lean 4.35.0-rc4 project
are subsequent gates; neither is represented by this offline receipt.

## Reproduction

```bash
pytest -q tests/test_evaluation_oqp27_fidelity.py
python scripts/verify_evaluation_oqp27_fidelity.py --output /tmp/oqp27.json
python scripts/check_receipts.py --only oqp27_fidelity
```

The committed receipt at `output/evaluation_oqp27_fidelity/oqp27_v0_1.json` includes
all 21 checks, the exact histograms, counterexample strategies, rational values and SHA-256
hashes of the generating sources. `check_receipts.py` regenerates it and verifies these hashes.

The upstream formalization is licensed under Apache-2.0. This file identifies the source
commit and Git blobs; code here reproduces only the small published coefficient arrays.
