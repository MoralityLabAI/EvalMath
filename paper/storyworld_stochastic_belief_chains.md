# SRG-19: Stochastic reaction chains and belief geometry

[Pre-run protocol](../integrations/sweepweave-ts/srg19/PROTOCOL.md), commit 41b611221bb485d904a21f65d152717e6e2651a2. Public exploratory diagnostic, no changes to the original storyworld.

## Exact belief oracle

Hidden z in {0,1}, public t and credit e. For action a, the reaction first XORs z by the public stage/action bit, then flips independently with probability f/4. Work reward depends on the pre-reaction hidden mode; probe has the work0 phase map, zero running reward, consumes credit, and gives a noiseless post-reaction observation. Ordinary observations match the post-reaction mode with probability q/4. Terminal bonus B is paid iff the final post-reaction mode equals the target. Rewards are hidden during decisions. A packet gives exact posterior masses (x,y), not hidden state or future noise. Model-facing policy is a function of posterior-equivalence classes. History inference is intentionally separate.

Define N_d(t,e,x,y)=(x+y)16^d V_d(t,e,x/(x+y),y/(x+y)), with N_0=0. Post-transition masses (u,v) have sum 4(x+y). Each observation branch has masses (u l0,v l1), with likelihood numerators l0,l1 in {0,1,2,3,4}; the total branch mass is 16(x+y). Canonicalize each nonzero branch by gcd g_o, giving x_o,y_o. Let R be immediate reward weighted by (x,y); T be terminal reward weighted by (u,v) (zero unless last turn). Then Q_d numerator is R16^d + 4T16^(d-1) + sum_o g_o N_(d-1)(t+1,e',x_o,y_o). Max over legal actions. The continuation term is zero at terminal. All values in this registered grid are exact safe integers. Policy evaluation uses the same recurrence with the submitted action fixed, and sums exact expected utility over all possible reaction/observation branches. Missing/illegal actions stop the policy. The common denominator 4194304 makes aggregate expectations integer sums.

## Results

36 cells, 576 roots, 10592 reachable posterior-class packets (10238 informative). 240 independent conditional-probability tree checks; 576 exact oracle policy checks. All 384 matched q comparisons obey Blackwell monotonicity. All 576 sham/no-probe values agree. The sham channel is dominated by work0 since both actions have identical phase and observation distributions and work0 preserves credit and earns nonnegative reward.

| Policy | Root accuracy | Informative accuracy | Expected points/root | Fraction oracle utility | Expected probe use |
|---|---:|---:|---:|---:|---:|
| first | 34.72% | 43.38% | 6.01302 | 60.83% | 75.00% |
| d1 | 73.09% | 92.12% | 9.23180 | 93.39% | 4.12% |
| d2 | 90.28% | 97.48% | 9.73360 | 98.47% | 38.34% |
| d4 | 99.65% | 99.98% | 9.88306 | 99.98% | 46.61% |
| map | 69.62% | 89.25% | 9.09518 | 92.01% | 21.45% |
| no_probe | 76.22% | 93.60% | 9.27799 | 93.86% | 0.00% |
| oracle | 100.00% | 100.00% | 9.88512 | 100.00% | 46.61% |

Probe opportunity is positive in 262/576 roots; oracle-minus-no-probe gain totals 349.70508 points across roots. The 384 adjacent q comparisons yield 308 strict value gains and 62 strict optimal-action reversals. Sum of adjacent passive gains is 278.48438 points (overlapping matched comparisons, not independent samples). Target changes yield 30/288 strict reversals. Sham channel changes yield 97 strict reversals.

## Geometry

Embed posterior b=(p0,p1) into the positive unit sphere via psi(b)=(sqrt(p0),sqrt(p1)); chord distance is sqrt(2) times Hellinger distance. At the root, compare probe versus work0, which share the same predicted hidden-mode distribution. The average entropy gains (bits) are 0.94143 (probe) and 0.37198 (ordinary). Expected variance reductions are 0.23047 and 0.09501. Expected squared chord displacement is 0.54376 and 0.20218. These are information-only measures; probe changes reward and credit, hence information gain alone cannot determine its policy value.

For fixed dynamics compare p1=1/4,1/2,3/4. All 1728 exact action-value convexity checks pass (finite-horizon POMDP Q is a maximum over affine policy-tree values). 393/1152 adjacent prior pairs have distinct strict optimal root actions. Mean absolute sampled Q slope is 1.55129 points/unit probability. Minimum chord among sampled reversals is 0.26105. This grid spacing is not a bound on the true decision margin or minimum reasoning complexity. Geometry floats are diagnostic; utility and action comparisons use exact integers.

## Runtime and scoring

36 SWMD-SRG/2 fixtures, 688 reachable tape-conditioned witness states, 1740 checked transitions (772 terminal), 968 posterior-support checks. Hidden noise words are sampled in advance per action and stage, so runtime checks deterministic conditioned reactions, not an editor RNG. Public runtime coordinates expose only credit and signal; posterior masses for planning packets are derived by the verifier. The terminal observation is reset to sentinel. Missing/malformed and submitted-oracle checks pass (1464 one-tape packets).

The public run uses eight matched tapes and full known transition tables. The finite binary hidden state is deliberately small. Probe value may depend strongly on the selected payoff family. Model inference, standalone Node CLI and production editor integration remain outstanding. No private evaluation or paid compute.

## Reproduce

```sh
node integrations/sweepweave-ts/srg19/cli.mjs verify
node integrations/sweepweave-ts/srg19/cli.mjs stage /tmp/srg19-pilot 0x53521901 1
node integrations/sweepweave-ts/srg19/cli.mjs score /tmp/srg19-pilot /tmp/submissions.jsonl
```

Only model_input/planning.jsonl is model-facing. For a private model test use a fresh independently frozen seed, randomize packet order, and omit packet IDs from model prompts. Score JSONL id/action pairs. Hashes bind generator and corpus. SRG-08 runner compatibility and CLI remain unexecuted.