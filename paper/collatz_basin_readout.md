# COL-EVAL-01: basin identity and the ceiling of a modular readout

Evidence: **finite verified example** for the census and **algebraic identity**
for the partition ceiling. The general classification of every periodic
invariant belongs to the supplied manuscript; this module constructs the
explicit `<2,3>` quotient and checks its conservation directly.

## Task and parameter contract

For positive `d = 1 (mod 4)` with `gcd(d,6)=1`, apply `3n+d` when odd `n` is
`1 (mod 4)` and `n+d` when it is `3 (mod 4)`, then divide by 2 until the value
is odd. The numerator is divisible by four. When `n <= d`, the successor is
at most `d`; when `n > d`, it is smaller than `n`. Consequently every positive
trajectory reaches the finite odd core, and every core state reaches a cycle.

The target is the minimum odd integer on that eventual cycle. Model inputs are
`(d,n)`. Gold cycle minima, depths and arithmetic labels live in separate
evaluator files. The diagnostic readouts receive, respectively, a constant,
`gcd(n,d)`, the orbit of `n mod d` under multiplication by 2 and 3, or the basin
label. The quotient may combine several basins.

## Exact score ceiling

Let `X` be the odd core, `b(x)` its basin label and `q(x)` the allowed readout.
Writing `N(z,y) = |{x : q(x)=z, b(x)=y}|`, the largest possible accuracy of a
deterministic classifier of `q(x)` under the uniform distribution on `X` is

\[
\operatorname{Acc}^*(q)=\frac{1}{|X|}\sum_z\max_y N(z,y).
\]

Proof: on each fiber the classifier emits one basin label, so it succeeds on
at most the largest label count. Choosing a maximizing label independently
on each fiber attains that count. A randomized output is a convex combination
of these counts and obeys the same bound. If a partition refines another,
the finer classifier can copy the coarser decision; its ceiling cannot fall.

These are distribution-dependent structural ceilings with access to gold
counts. They do not represent fitted predictors. An agent that receives the
integer `n` can compute extra features or iterate the map, so the quotient
ceiling applies only when the readout is restricted to that quotient.

For `d=13`, seeds 1 and 5 share a quotient orbit while belonging to different
cycles. The quotient ceiling is `4/7` over the seven core states. At `d=313`,
seven cycles occupy three quotient classes and the ceiling is `80/157`.
The reference fixture records ten independently generated MathCan cases,
including every basin size and each cycle's branch counts.

## Exact finite census

The public train/dev audit covers **531 parameter roots and 546,847 odd core
states**. Every complete orbit graph is enumerated. Of these roots, 284 contain
at least one quotient class that combines distinct eventual basins.

| Partition | Parameter roots | Core states | Roots with collisions | Quotient ceiling, macro | Quotient ceiling, micro |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train | 395 | 406,649 | 215 | 84.6585% | 84.7933% |
| Development | 136 | 140,198 | 69 | 86.2194% | 86.0861% |

The development gcd ceiling is 68.3260% averaged over roots; the constant
ceiling is 61.3348%. Exact fractions and every parameter row appear in
`output/collatz_basin/col_eval_01.json`; percentages here are display rounding.
The basin oracle reaches 100% by construction. The receipt also matches all
40 comparisons against the independent ten-parameter MathCan fixture.

## Public splits and evaluation custody

The SHA-256 rule in `parameter_split` assigns an entire `d` to train, dev or
holdout. All seeds and descendants of that parameter inherit the assignment.
The verifier scores train and dev for admissible `d <= 4093`. It records the
holdout parameter count and manifest hash without scoring that partition.

This is a public, reproducible split. Source tests, MathCan and other finite
audits can expose the same parameters. A future neural confirmation requires
fresh externally stewarded roots and an exposure ledger. Hash partitioning
alone cannot establish that the evaluator has kept labels unseen.

Training on one seed and testing on its descendant is excluded by the root
split. Distinct parameters can still share arithmetic structure. Report the
number of parameter roots separately from the number of states, and use
parameter-level paired inference for a future model comparison. This exact
census reports both macro averages over roots and micro averages over states.

## Mechanistic-resolution preflight

The repository planner was run on independent *parameter records* from the
development partition. Its contrast is the full quotient ceiling minus the
gcd ceiling. The sham permutes orbit representatives by multiplication by 2,
which leaves quotient information unchanged. A five-percentage-point minimum
is a prospective utility target for any future learned readout. Parameter
records are distinct; their stochastic independence is unverified, and no
causal model intervention has been performed.

The committed preflight therefore retains `REDESIGN_OR_PILOT_ONLY` for a neural
mechanism claim. Its numerical power calculation is planning advice. The
complete finite computations remain auditable exact-domain results.

| Required field | Current scope |
| --- | --- |
| Unit | Parameter `d`; repeated states share a root |
| Primary contrast | Quotient versus gcd readout ceiling |
| Physical dose | Replace one deterministic allowed partition |
| Scientific floor | `1/20` accuracy for a future learned comparison |
| Sham | Invariant orbit relabeling, exact zero effect |
| Comparisons | One registered contrast; four structural ceilings reported |
| Exposure | Public development fixtures; prospective confirmation pending |
| Causal controls | No neural intervention data |
| Verdict | Exact finite benchmark; mechanism claim remains pilot-only |

## Reproduce

```bash
PYTHONPATH=src python -m pytest -q tests/test_evaluation_collatz_basin.py
python skills/evalmath-mechinterp-power/scripts/preflight.py \
  --pilot configs/collatz_basin_pilot.json --strict
PYTHONPATH=src python scripts/verify_collatz_basin.py
python scripts/check_receipts.py --only collatz_basin
PYTHONPATH=src python scripts/export_collatz_basin.py --output /tmp/col-eval
```

The strict preflight exits with status 2 for its documented pilot-only decision.
The other commands must succeed. The exporter refuses the holdout partition.

The source manifest pins the independent MathCan fixture by SHA-256. The
cross-repository research lives in `patrickdugan/MathCan/research/collatz_resonance`.
The earlier large-parameter numerical findings are outside this receipt's
scope. No learned model, ordinary Collatz result, or Lean proof is claimed here.
