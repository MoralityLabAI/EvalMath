# VAD-09: the value of information across theorem families

2026-11-25. Exact finite Bayesian menu-control model (09A), numerical long-horizon planner and sampled stress test (09B), finite-memory policy expectation (09C). No new Lean theorem, kernel replay, or model training.

## Meta-level Bellman law

Carry the VAD-08 latent reliability mode forward across families. Let p be the predictive probability of reversed cues, and a be a fixed within-family search policy. From the exact terminal-record distribution, write l_r(o)=P(o|r,a), r_r(a)=E[net utility|r,a]. The record consists of paid observations, positive cues before discovery or censoring, and the hit indicator. Histories compatible with the selected policy are counted, including censored histories. Immediate utility charges every observation and nets cache construction in the discovery reward. Equal likelihood ratios can be merged for the continuation calculation while retaining immediate expected rewards separately.

For symmetric switching hazard eta, let z=(1-p)l_0+p l_1. The next predictive belief is q=eta+(1-2 eta)p l_1/z, for z>0. The exact finite-horizon menu optimum satisfies

    V_0(p)=0
    V_h(p)=max_a [(1-p)r_0(a)+p r_1(a)+sum_o z V_{h-1}(q)].

The policy can sacrifice immediate utility to learn the current mode, improving later choices. It does not see unobserved discoveries or the true mode. The within-family strategy is frozen when chosen; this is not a fully unrestricted within-family POMDP optimum.

V_h is convex piecewise affine: every complete contingent policy has expected utility affine in the initial mode probability, and the finite maximum is convex. For a supporting continuation line A+Bq, its perspective z(A+Bq) is affine in p. Sum transformed convex functions by sweeping their rational breakpoints; take the upper envelope across available actions. Zero-probability records contribute zero. This gives an exact Fraction implementation without a discretized belief state. Independent direct history recursion on small randomly generated models (including zero likelihoods and hazards 0,1/4,1/2) verifies the backup.

A separate two-mode static toy illustrates a strictly negative immediate probe: safe pays 1 and reveals nothing; probe pays -1 and reveals the mode; each mode-specific bet pays +6 if right and -12 otherwise, revealing the mode. At p=1/2 the one-family optimum is safe (1); two-family optimum probes (5 versus myopic 2); three-family optimum 11 versus myopic 3. The example deliberately stipulates an information action; it does not imply that actual theorem discovery has these payoffs.

## 09A exact VAD-08 menu

Use the original discovery-time prior, cue channels and costs of VAD-07/08, hazard 1/20, and a fixed menu: cutoffs 0,1,2,4,8,16,24 plus five exact within-family adaptive policies planned at reversed-cue priors 0,1/4,1/2,3/4,1. At p=1/2 and horizons 1,2,3, the exact total values are 9.3777027312, 20.8631051452 and 37.8794532685. Initial policies are p50, p50 and cut24. The third-horizon optimum chooses immediate utility 2.3 in place of the myopic 9.3777027312. Thus the immediate opportunity cost is about 7.078, and the increase in expected future utility is about 8.976, giving net improvement 1.8980957284 over forcing the myopic first action and then continuing optimally. These are rational model results; the decimal values are displays. The exact upper hull grows from 1 to 5 to 187 to 3785 pieces (including the zero horizon). 123 direct Bellman equality checks across 41 rational beliefs and three horizons pass. Terminal probabilities, expected utility, observation counts and hit rates for all 24 action-mode combinations agree with VAD-07's independent evaluator.

## 09B longer-horizon stress test

Use 401 belief grid points, linear interpolation and horizon caps 1,3,8,32; compare with 801-point values, a fixed cutoff of two, frozen normal policy, full VAD-08 myopic grid filter, expanded mismatch filter, and privileged mode/channel/prior oracle. The full myopic filter has a larger within-family action menu than the meta-controller, so the matched primary comparison is menu_32 versus menu_1. The privileged oracle cannot observe discovery time. At 41 rational test beliefs the maximum absolute grid discrepancy from the exact oracle for horizons 1/2/3 is about 3.6e-15/0.002886/0.000392. The 401-vs-801 discrepancy at horizon 32 is at most 0.001466 at the tested coarse grid points; this is a numerical check, not a uniform error certificate.

Fresh public seed namespace 9100000; 32 streams of 96 families in each of eight VAD-08 scenarios. All methods receive matched exogenous streams but see only their own censored observations. 24,576 distinct families, 2,304 stream-method records, 221,184 family-method evaluations. Planning horizon, menu and grid chosen before evaluation, but no independently sealed test. Net means per family before controller overhead:

| Scenario | Menu myopic | Menu 32 | Full myopic | Expanded | Blind |
|---|---:|---:|---:|---:|---:|
| Markov | 18.534 | 18.547 | 18.583 | 18.327 | 9.857 |
| Stationary | 21.167 | 21.179 | 20.976 | 21.002 | 9.298 |
| Reversed | 19.305 | 19.609 | 19.281 | 18.479 | 8.402 |
| Abrupt reversal | 20.133 | 20.273 | 20.134 | 19.551 | 8.514 |
| Fast switching | 10.026 | 9.981 | 10.195 | 9.811 | 7.870 |
| Weak cues | 3.592 | 3.587 | 3.796 | 8.039 | 8.514 |
| Prior shift | 10.479 | 10.545 | 10.389 | 10.304 | 4.846 |
| Joint shift | 3.482 | 3.560 | 3.645 | 9.674 | 6.162 |

Nominal menu_32 minus menu_1 mean 0.0130208, descriptive paired stream bootstrap interval [-0.17448,0.21094], 14/32 wins. Against full myopic mean -0.0364583, interval [-0.27083,0.18880], 15/32 wins. The longer-horizon practical advancement gate fails: no reliable nominal advantage even before controller/planner overhead. The rare full-exploration action appears in 1.4974% of nominal menu_32 families. This experiment does not show robustness to weak cues or joint shift.

## 09C numerical value bounds and exact-law policy evaluation

In exact arithmetic, interpolation of upper estimates on grid points dominates a convex true value between points. The Bellman operator is monotone, so induction gives a grid upper bound on the nominal menu optimum. Separately, fix the finite-memory controller that rounds each predictive posterior to the nearest grid point and chooses the stored maximizing action. Its true expected reward is calculated by conditioning on the true mode and memory index, summing record probabilities, then transitioning the true mode with the actual hazard. This is a lower bound in exact arithmetic. The implementation uses float64; these reported upper/lower values are numerical estimates, not rigorous interval-certified bounds. The memory-rounded policy in C differs from B's continuous-belief policy with interpolated action scores.

Same-grid (401 points) nominal values:

| Families | Myopic | Full-horizon policy | Delta |
|---:|---:|---:|---:|
| 1 | 9.377703 | 9.377703 | 0 |
| 2 | 20.863098 | 20.863098 | 0 |
| 3 | 35.978587 | 37.879453 | 1.900866 |
| 8 | 122.405029 | 127.230257 | 4.825228 |
| 16 | 265.049758 | 270.298327 | 5.248569 |
| 32 | 550.564596 | 556.432739 | 5.868143 |
| 96 | 1692.626322 | 1700.970386 | 8.344065 |

At 801 grid points, horizon-96 policy expectation is 1700.970522 and grid upper estimate 1700.970914, numerical gap 0.000392. The C receipt's advantage field uses the fine policy and coarse myopic; the table above uses identical grid size for both. At horizon 96 the incremental utility is 0.086917 per family, a break-even allowance for all additional planning computation and memory. No physical overhead was measured or charged. With horizon cap 8 the 401-point policy has the same expected value as horizon 96 in the evaluated model; this numerical equality is not an all-horizon theorem.

Fix assumed hazard 0.05; true hazard 0/0.01/0.05/0.25/0.5. At 96 families the myopic/long-horizon values respectively are 1958.465/1975.392, 1901.187/1916.334, 1692.626/1700.970, 982.123/965.789, 495.153/465.065. Exploration loses value when mode changes invalidate its information more quickly. Correctly specifying the hazard is part of the model, not a free real-world assumption.

## Reproduction and gate

    python scripts/verify_vad_meta.py --out /tmp/vad09a.json
    OPENBLAS_NUM_THREADS=1 python scripts/verify_vad_meta_grid.py --out /tmp/vad09b.json
    OPENBLAS_NUM_THREADS=1 python scripts/verify_vad_meta_cert.py --out /tmp/vad09c.json
    OPENBLAS_NUM_THREADS=1 python -m pytest -q tests/test_vad_meta.py

The numerical scripts require NumPy; the exact oracle is standard library. Four targeted local tests pass with NumPy installed, including 324 small-model history-tree comparisons, exact 09A replay, terminal record checks and independent rational short-horizon evaluation of the selected grid policy. The numerical test skips when NumPy is absent. All three receipts reproduced byte for byte in the same local environment before a comment-only correction; regenerated receipts record the corrected source digest. See compact manifest and downloadable reproduction bundle. Remote CI pending. No new Lean work.

Recommendation: stop escalation to larger recurrent meta-planners on this gate. VAD-10 can study whether an adaptive observation action pays when there are longer-lived regimes or uncertainty over the cue law itself, with independent hazard calibration, a safe fallback, and full measured policy-selection costs. For a future Lean gym, distinguish transferable proof knowledge from transient evidence about which inference policy works. A learned controller must beat myopic and robust symbolic comparators at matched information access and measured cost.
