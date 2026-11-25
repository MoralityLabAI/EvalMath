# CTS-03: higher-dimensional certificate-support recovery

**Verdict: REDESIGN_OR_PILOT_ONLY.** Exact finite checks and exploratory learned-policy results, conditional on one training fit. No neural mechanism or general LP complexity claim.

## Construction and reproducibility

For dimensions 4, 8, 16, 32, generate bounded integer LPs with 6d inequalities, a feasible origin, and an invertible d-row active set S at a planted point x*. All remaining inequalities have strictly positive slack at x*. A positive linear combination of the active normals defines the objective. By weak duality x* is optimal; equality requires all S rows tight, so invertibility implies uniqueness. The bounding parallelotope is independent of S. Row permutation and positive row scaling obscure the presentation.

Three generator families (dense, sparse, correlated); 16 training and 12 development roots per family/dimension stratum, 192 and 144 roots respectively. All are development data. The learned selector is a nine-feature logistic ranker, not a transformer. The recurrent version reprojects the objective residual away from the selected-row span and repeatedly scores remaining rows. Training uses gold-prefix supervision; test-time inputs contain constraints and objective alone. Frozen uses the same weights and initial features; sham permutes the dynamic features across rows. Static fits a separate ranker at empty prefix. Greedy is a deterministic residual-pursuit baseline. HiGHS generates a numerical candidate; exact integer linear algebra independently certifies it. The oracle is the planted support, a structural ceiling.

Run from the repository root:

```sh
python -m pip install numpy==2.3.5 scipy==1.17.0 sympy==1.14.0
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python research/cts03/cts03.py
python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot research/cts03/pilot.json --out /tmp/cts03-preflight.json --strict
```

Expected preflight exit 2 (intentional stop). The runner produces complete proposals and per-arm verification outcomes in results.json, plus pilot.json. root_scores.csv records all 144 root-level outcomes, recovered support counts and HiGHS iterations. verified_mask bits in order static, greedy, recurrent, frozen, sham, HiGHS, oracle. SHA-256 of executed source: a821ef28b7ab8d591d68095253a63f6316acb491745a149e7222d7b1385fc94a. Root score receipt SHA-256: 79efba54fa94acb269b3bdfbfb24e38405e575c544f1ec53fc21cd511a32c475. The pinned upstream preflight script has git blob 0ff062f76f5534d9f18425f986ae3e750397f50c. Local CPU replay reproduced all non-timing fields and pilot bytes exactly.

## Results

| Arm | Mean root support recall | Accepted certificates | Mean rows scored |
|---|---:|---:|---:|
| Static | 0.4064670138888889 | 0/144 | 90 |
| Greedy | 0.1990017361111111 | 0/144 | 2040 |
| Recurrent | 0.4012586805555556 | 0/144 | 2040 |
| Frozen | 0.4108072916666667 | 0/144 | 2040 |
| Shuffled residual | 0.3218315972222222 | 0/144 | 2040 |
| HiGHS | 1 | 144/144 | N/A |
| Planted oracle | 1 | 144/144 | N/A |

Each arm gets one full candidate certificate and one exact validation per root; corrupted support negative controls rejected on 144/144. Each certificate is checked for primal feasibility, nonnegative dual multipliers, exact dual equality and zero duality gap. HiGHS completed 5,809 iterations in total, maximum 112 per instance. Row scores and solver iterations are different work units, not a compute-equivalent budget. Timings are environment-specific. The recurrent arm is worse than its frozen control overall (-0.009548611111111112 recall), improving on 41 roots, tied on 56, worse on 47. Sparse stratum has positive exploratory mean difference (+0.0305989583333333); no post-selection significance claim.

## Resolution gate

Unit: generated LP root within a generator/dimension stratum, conditional on one fit; 144 exposed roots, 1,008 arm outcomes, 144 additional corrupted-support controls. Primary contrast recurrent minus same-weight frozen recall. Physical dose: d sequential row selections, dynamic residual features versus frozen, one certificate attempt. Scientific floor 0.10 recall; nominal target 0.20, nominal finest measurement resolution 1/32 (coarser within smaller dimensions). Five comparisons versus frozen, family alpha .05, prospective 192 roots only as planning input. Sham variation: 0.50 observed order-statistic bound (rank 142 under the planner's 95%/95% independence assumption). Independence across fitted models/families unverified, so population tolerance coverage unestablished. Approximate resolvable effect 0.5368252461051439, observed effect negative. Required confirmation count undefined. All roots exposed for development; no sealed readout and no causal claim. The residual permutation is a feature-level intervention, not a physical neural sham. No further training or confirmation authorized by the gate.

## CTS-04 direction (proposal)

Use the learned scores to prioritize constraints in an exact constraint-generation or working-set method. Start with a bounded restricted LP; check every omitted inequality against the tentative primal optimum. Add violated constraints, or fall back to the full solver. Accept only the full primal-dual certificate, never the restricted optimum alone. Compare learned ordering to random, geometric violation ranking, and full HiGHS with all preprocessing, LP solves, exact checks and fallbacks charged. Freeze fresh independent-root design and measure total time/work to exact success. Include adversarial near-active rows, degenerate optima and larger dimensions. A useful effect would be reduced solver work at matched verified success; current data do not establish it. No upstream Hirsch construction is reproduced here.
