# SRB-EM-01: upstream fire-sale replay with EvalMath SRB-01

**Date:** 16 November 2026. **Evidence:** verified synthetic mechanism
replay using the actual `patrickdugan/SystemicRiskBench` implementation.
There are zero model evaluations in this result. The finite-grid
probabilities are illustrative, not market estimates.

## Source lock and experiment

| Component | Exact source |
| --- | --- |
| SystemicRiskBench export PR | [patrickdugan/SystemicRiskBench #1](https://github.com/patrickdugan/SystemicRiskBench/pull/1) |
| Export branch snapshot replayed | `33e6e87a734142d01e513a2901eb1f1bdeea5bb5` |
| EvalMath scorer used | `1c3e07ece43cd617b05171d404c53cc8c906dc8c` |
| Source-bound GitHub CI | [SRB replay run 43828279531](https://github.com/patrickdugan/SystemicRiskBench/actions/runs/43828279531) |
| Exported bank SHA-256 | `eb556ce4beac4399086682a6d440731b5d41973c3d61129338b9ff1345d73737` |
| Simulator module SHA-256 | `719dd6ab7f4d8d5683cb50079c728c58acac9bd217a970dee330466ce0b1398a` |
| Exporter module SHA-256 | `5fdd92217a782f20f6e8c3cadd76913b580aca0fbf4a59a2c80304d50612892f` |
| Registered grid configuration SHA-256 | `ff8cfa2bb3e68e220cf68c9770f7984ba0468b7ecedadc1c166f4ca09abc67ca` |

The integration uses the existing `systemic_risk_bench.simulation.simulate`
cohort fire-sale engine. The registered grid contains five shock levels
(4%, 8%, 12%, 30%, 38%), three order-book depth tiers (USD 300,000,
1,000,000 and 5,000,000) and both homogeneous and heterogeneous cohort
profiles. There are **30 equally weighted scenarios** and **60 paired
simulation calls**. Fixed aggregate capital is USD 1,000,000, representing
one million agents in the cohort approximation.

One policy retains registered venue depth. The alternative triples depth
at a fixed **USD 10,000** hypothetical intervention cost. The stochastic
regime, external shock and cohort profile are paired within each world,
so this isolates the specified depth lever inside the simulator. The
observed signature reveals the shock tier; depth tier and cohort profile
are query-gated. The exporter rejects nonconvergence and reconciles
investor losses plus creditor shortfall with book-equity loss within a
cent. Every returned simulator float is rounded to cents and serialized
as an exact rational for evaluation. Native simulation dynamics remain
floating-point and synthetic.

## Verified numerical results

All USD amounts are equal-weight averages under the stipulated design
grid. Each decimal shown is rounded for display; the fractions are
the actual EvalMath output.

| Metric | Exact | USD |
| --- | ---: | ---: |
| Baseline no-support policy mean total loss | `1505037371/3000` | 501,679.12 |
| Best fixed action mean total loss | `692549663/1500` | 461,699.78 |
| Best shock-observing policy mean total loss | `689549663/1500` | 459,699.78 |
| Full-information oracle mean total loss | `343104953/750` | 457,473.27 |
| Unobservable regret / two-action collision certificate | `3339757/1500` | 2,226.50 |
| Mean total loss with depth query | `343600937/750` | 458,134.58 |
| Mean total loss with profile query | `688049663/1500` | 458,699.78 |
| Tail CVaR, baseline harm at \(\alpha=4/5\) | `304509031/300` | 1,015,030.10 |
| Tail CVaR, shock-observing policy harm at \(\alpha=4/5\) | `99287277/100` | 992,872.77 |

The best uniform intervention is tripling depth. Knowing the shock
tier allows the controller to avoid paying the backstop cost in the
4% shock regime and improves mean loss by exactly USD 2,000.
Access to depth tier lowers mean loss by another
`2347789/1500` USD (about 1,565.19) compared with the
shock-only observation. The per-world hindsight oracle still saves
`3339757/1500` USD (about 2,226.50) compared with the
shock-only controller. The exact equality with the binary collision
formula independently checks the mathematics of information-limited
policy choice on the source simulator's recorded outcomes.

Both investor losses and creditor shortfall are included in the
counterfactual harm vector. Thirteen of the sixty action-world
simulations have positive creditor shortfall. Those sixty action-world
outcomes represent thirty paired worlds; treating them as independent
financial observations would overstate the evidence.

## Misspecified checker and feedback result

The exporter implements an explicit toy checker that reports
`claimed_safe` when *exogenous* book loss falls below USD 300,000.
It overlooks subsequent endogenous deleveraging and price impact.
Under the exact counterfactual outcomes, baseline liquidity has two
false-safe worlds, while the depth-tripled intervention has one. The
latter event is included in the former event's world set.

EvalMath's maximum false authorization probability under **no
disclosure**, **one fixed query**, **two adaptive queries** and
**complete disclosure** is the same exact fraction, **1/15**.
Thus this particular joint law admits *no post-selection risk
increase* from the registered queries, even though those queries
improve intervention quality. The earlier independent two-world
fixture in [the SRB-01 mathematics](systemic_risk_evalmath.md) has
different event structure and does exhibit feedback selection gain.
Neither result is a measurement of an actual model's asserted safety.

## Independent reproduction and validity limits

The SRB GitHub Actions job ran all 58 tests in the current
SystemicRiskBench suite, generated the evaluator-only world bank,
checked it with the pinned EvalMath scorer and archived
`evalmath_bank.json` plus `evalmath_score.json`. CI passed.
The EvalMath branch separately verifies its arithmetic and synthetic
receipt in the dedicated SRB-01 workflow.

All claimed arithmetic is conditional on **one registered equal-mass
synthetic simulator grid**. There is no inference to unconditional
financial crisis rates. The upstream named-history corpus has no
measured action-counterfactual matrix and was excluded. The published
90 model calls on separate numerical tasks are not mapped to the
two-intervention action grammar. This replay supplies a working
evaluator and a new, testable question about partial observation; a
prospective model comparison requires a registered policy interface,
independent case-family holdouts, fixed budgets and per-family paired
analysis.

To regenerate from the SystemicRiskBench repo checkout:

```bash
python -m systemic_risk_bench evalmath-export \
  --config configs/evalmath-simulation-v1.json \
  --output artifacts/evalmath_bank.json
PYTHONPATH=evalmath/src python evalmath/scripts/score_systemic_risk.py \
  --input artifacts/evalmath_bank.json \
  --output artifacts/evalmath_score.json
```
