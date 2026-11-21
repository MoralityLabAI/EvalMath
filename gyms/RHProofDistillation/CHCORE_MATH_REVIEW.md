# RH-CHCORE-02: what the analytic size-bound lemma needs

Evidence: published Lean source at pinned `leanprover-community/riemann-hypothesis` commit
`f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3` and the
[ChCore compiled-expression run](https://github.com/MoralityLabAI/EvalMath/actions/runs/44899211767).
This is a conditional mathematical analysis and gym development note.

## The precise role of `proposition_size_bound`

The source declaration
[`proposition_size_bound`](https://github.com/leanprover-community/riemann-hypothesis/blob/f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3/src/Formalism/SizeWindowBrackets/ChainSlopeWindows/LipschitzWeightAndMinimum.lean#L507)
has type `Formalism.LFunctionChainParameters.ThickSetMeanBounds.GrowthSizeBound`,
defined [here](https://github.com/leanprover-community/riemann-hypothesis/blob/f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3/src/Formalism/SizeWindowBrackets/GrowthBoundGivesRiemannHypothesis.lean#L119).
Its statement takes the `SizeWindows C ε x n nT nT2 m b k aE Err` proposition
and a character-balance inequality as premises, and concludes

`Gx ≤ x ^ (1/2 + (C + 3) * ε)`.

The size-window premises include `x ≥ 3`, `ε > 0`, `C ≥ 0`, `n > 0`,
`b > 0`, and the following scale constraints:

```text
x^(-ε/8) * n / 2 ≤ nT
x^(-ε) ≤ nT2 / n,           nT2 ≤ n
x^(1/2-ε) ≤ m ≤ x^(1/2+ε/2)
x*m ≤ k ≤ n²*x^(1/2-ε)
26 ≤ x^(3ε/8)
```

Here `n`, `nT`, `nT2` and `m` are natural numbers, usually instantiated
with a group cardinality, two finite-set cardinalities and a sampling count.
The source also imposes constraints on `aE` and an explicit upper bound
on the error `Err`; the displayed subset alone does not imply the
growth estimate.

## Exact exponent bookkeeping

Let `X = x^(1/2+ε)`, `P = x^(Cε)`, `Y = x^(1/2+13ε/8)`,
`Q = nT*m*b` and `δ = nT2/n`. The original proof obtains

```text
Err ≤ 10 * P * Y * Q
Q * (δ/2) * (Gx - 4X) ≤ Err + 2Q/x
```

Strict positivity of `Q` permits cancellation. With `x ≥ 3`,
`P*Y ≥ 1` and `x^ε * δ ≥ 1`, the proof derives

```text
δ * (Gx - 4X) ≤ 22 * P * Y
Gx - 4X ≤ 22 * P * Y * x^ε
Gx ≤ 26 * x^(1/2 + (C+21/8)ε)
```

The final `26 ≤ x^(3ε/8)` premise absorbs the coefficient:

```text
26*x^(1/2 + (C+21/8)ε) ≤ x^(1/2 + (C+3)ε).
```

The compiled proof value directly contains `SZ.T1` through `SZ.T4`
and `SZ.rp`; these are the registered next-level obligations for proof
reconstruction. Source-verified locations for the defining declarations
were obtained in [the source locator CI](https://github.com/MoralityLabAI/EvalMath/actions/runs/44899731801).

## Necessary feasibility constraints

Since `x > 0`, its real power `x^(1/2-ε)` is strictly positive.
The three inequalities

```text
x^(1/2-ε) ≤ m
x*m ≤ k
k ≤ n²*x^(1/2-ε)
```

imply `x ≤ n²`. The group order must therefore satisfy
`n ≥ sqrt(x)` whenever the full size-window assumptions hold.
This is a mathematical consequence of the displayed assumptions,
rather than a claim about whether the upstream construction
successfully supplies the required group.

The lower bounds on `nT`, `nT2/n`, and `m`, together with `x>0`
and `n>0`, also enforce `nT>0`, `nT2>0`, and `m>0`.
Tasks `RH-D-012` and `RH-D-013` formalize these necessities
as standalone Lean propositions.

## Four explicit error-term inequalities

The four named `SZ` lemmas in
[`LipschitzWeightAndMinimum.lean`](https://github.com/leanprover-community/riemann-hypothesis/blob/f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3/src/Formalism/SizeWindowBrackets/ChainSlopeWindows/LipschitzWeightAndMinimum.lean#L25-L130)
bound each contribution in the `SizeWindows` error expression.
With `Y=x^(1/2+13ε/8)` and `Q=nT*m*b`, their estimates are:

| Source lemma | Contribution | Upper bound |
| --- | --- | ---: |
| `SZ.T1` | `nT*aE` | `2YQ` |
| `SZ.T2` | `nT*aE*m²/k` | `2YQ` |
| `SZ.T3` | `m*(2n*m*b*x^ε)` | `4YQ` |
| `SZ.T4` | `m*(nT2*k*b*x^ε / (n²*x^(-ε)))` | `2YQ` |

The sum is `10YQ`, which becomes `10*x^(Cε)*YQ` after
multiplication by the error-window factor. This is the exact source
of the coefficient 10 in `hErr'`. The subsequent bound 22 arises
after dividing by the positive `Q` and absorbing `2Q/x`.

These lemmas isolate a valuable reconstruction curriculum.
`T1` and `T2` are scalar inequalities. `T3` uses the lower bound
on `nT` and upper bound on `m`; `T4` uses the upper bounds
on `nT2` and `k`. Their separate hypotheses make them natural
targets for compact reasoner tests and counterexample checks.
## Where the research difficulty remains

`proposition_size_bound` is a conditional analytic estimate with explicit
window constraints. The nontrivial global argument must construct
compatible algebraic, geometric and character data that satisfy those
constraints at the scales required by the final theorem.
That is the important feasibility and proof-navigation target for
Data Goblin and future compact Lean reasoners.

The source has no redistribution license; this note records only concise
mathematical formulae, source identifiers and interpretation.
