# SRG-20: Multivariate evidence, conflicting histories and nested delegation

[Pre-run protocol](../integrations/sweepweave-ts/srg20/PROTOCOL.md), commit cf390496eabf82e304d5e8243edf4a389c20ac0a. Public exploratory diagnostic; original storyworld unchanged.

## Bayesian policy recursion

Let x be uniform on K-bit integers; target y is parity(x & target_mask). Agent i sees four noisy parities h_i with public masks. Conditional on x, all observations across agents are independent; each likelihood is integer l_i(x,h) / 256. Agents precommit using private histories alone. If route a in {0,1} is selected, the reward is 8 times 1[y=a]. Delegate follows the successor's precommitted action chain and subtracts fee. Successors do not observe selection, previous histories or previous fees. This is a model of fixed decision rules, not a signaling game or equilibrium.

Let U_i(x) be the expected return of the fixed suffix policy conditional on x, with fee costs included from i onward. The integer representation uses scale 256^(D-i+1). For agent i with history h, compare Q_route(a)=sum_x l_i(x,h)*8*1[y=a]*256^(D-i) and Q_delegate=sum_x l_i(x,h)*(U_(i+1)(x)-fee*256^(D-i)), where U denotes the scaled integer vector. Divide by sum_x l_i(x,h)*256^(D-i) for conditional expected points. Choose a maximizing action with fixed ties, then U_i(x)=sum_h l_i(x,h)*scaled return(x,a_i(h)). Terminal agent has two route options. The sum over x of U_i equals the sum of optimal history Q numerators. A0's submitted policy changes only its own selection; successors execute the full fixed policies. Depth d controls model the suffix truncated after d links, with the last modeled agent forced to route. All decision values and weighted aggregate utilities are integer exact (common denominator 274877906944); last/factor approximation choices use floating point and a fixed 1e-12 tie tolerance. Missing actions earn zero in scoring and coverage is reported; this is an abstention convention, not an environment action.

## Results

90 cells, 720 worlds, 11520 A0 history decisions; 10008 informative. 5760 histories contain disagreement between repeated observations, total probability mass 0.3750. 439 worlds have positive value of delegation over direct-only. 1390 strict roots change the selected action under one-link truncation. The weighted denominator uses exact A0 history probabilities, not uniform rows.

| Policy | Weighted accuracy | Weighted informative accuracy | Expected points/world | Oracle utility fraction | Delegate rate |
|---|---:|---:|---:|---:|---:|
| first | 33.56% | 23.90% | 4.0000 | 65.97% | 0.00% |
| direct | 52.49% | 45.58% | 5.2344 | 86.33% | 0.00% |
| d1 | 87.62% | 85.82% | 5.9118 | 97.50% | 35.13% |
| d2 | 98.87% | 98.71% | 6.0590 | 99.93% | 46.38% |
| d3 | 100.00% | 100.00% | 6.0633 | 100.00% | 47.51% |
| last | 83.40% | 80.99% | 5.7954 | 95.58% | 57.36% |
| factor | 85.57% | 83.47% | 5.8944 | 97.21% | 64.18% |
| oracle | 100.00% | 100.00% | 6.0633 | 100.00% | 47.51% |

| True links | d1 utility | d2 utility | d3 utility |
|---|---:|---:|---:|
| D1 | 100.00% | 100.00% | 100.00% |
| D2 | 96.58% | 100.00% | 100.00% |
| D3 | 96.14% | 99.79% | 100.00% |

The nesting comparison concerns prediction of fixed successor policies, not a lower bound on computational depth or a measure of arbitrary epistemic logic.

## History inference and action boundaries

For last-observation and independent-bit-marginal approximations, evaluate the posterior against exact A0 likelihoods.

| Control | Mean TV | Mean squared Hellinger | Mean target probability error |
|---|---:|---:|---:|
| Last observation | 0.3506 | 0.0937 | 0.0957 |
| Factorized bits | 0.2228 | 0.0580 | 0.0799 |

Among 40320 same-last-observation pairs, 7296 have distinct unique optimal actions; 4464 also differ in repeated-evidence disagreement status. A deterministic last-observation-only policy cannot solve both members of these selected witnesses. Exact both-correct 7296; last-observation both-correct 0. These conditioned pairs overlap, so counts are not independent samples.

## Hilbert geometry and K

Map posterior p to sqrt(p), a unit vector. Use weighted centered feature covariance C over all A0 histories in each world. Participation ratio tr(C)^2/tr(C^2) measures effective feature dimension (zero when covariance vanishes). Compute rank over GF(2) of observed masks and union of all agents' masks. Rank bounds distinguishable noiseless parity classes by 2^rank. Entropy perplexity is 2^(expected posterior entropy); it measures remaining uncertainty, not feature dimension. Posterior equivalence uses gcd-reduced exact masses.

| Nominal K / support R | Mean A0 rank | Mean union rank | Mean posterior classes | Mean posterior entropy (bits) | Mean feature participation ratio |
|---|---:|---:|---:|---:|---:|
| K2_R2 | 2.0000 | 2.0000 | 9.7500 | 1.3367 | 2.3491 |
| K4_R2 | 2.0000 | 2.0000 | 9.7500 | 3.3367 | 2.3491 |
| K4_R4 | 3.0000 | 4.0000 | 12.0000 | 3.2907 | 3.2216 |
| K6_R2 | 2.0000 | 2.0000 | 9.7500 | 5.3367 | 2.3491 |
| K6_R6 | 3.0000 | 5.6667 | 12.0000 | 5.2907 | 3.2216 |

288 comparisons confirm exact Q invariance (after state-count normalization), policy invariance and control choices for fixed R=2 with larger nominal K. Padding changes remaining entropy but not the decision problem. Nominal K, algebraic rank, empirical feature dimension and delegation depth must be reported separately.

## Verification and integration

125952 statewise likelihood normalization checks, 48 independent explicit history recursion checks and 288 explicit root action-value checks, 11520 repeated-mask swap checks and 720 direct lower bound checks. All 720 oracle worlds replay exactly. 90 compiled SWMD-SRG/2 fixtures, 270 active-agent states, 720 checked transitions, 540 terminal checks and 90 fixed policy paths. Runtime projects only active history and actor; it does not enforce separate authenticated agent views or prevent a central player from remembering earlier observations. Hidden tapes are predetermined. The model-facing benchmark explicitly supplies only A0's view and fixed partner rules. No actual agent communication protocol or production editor modifications.

Separate matched staging modes: history-only planning, posterior-supplied planning, history-to-posterior inference. Inference scorer accepts finite nonnegative probabilities summing to one within 1e-8 and reports coverage alongside probability errors. Invalid/missing inference submissions are excluded from error means and counted in coverage. Policy scorer accepts id/action JSONL, inference scorer id/probabilities JSONL. All scorer gates passed. Public run used eight matched tapes; no private evaluation, standalone Node CLI, actual model calls or paid compute. Q4 late agents have some impossible private histories excluded. Root q3 histories all have nonzero mass.

## Reproduction

```sh
node integrations/sweepweave-ts/srg20/cli.mjs verify
node integrations/sweepweave-ts/srg20/cli.mjs stage /tmp/srg20-history history 0x53522001 1
node integrations/sweepweave-ts/srg20/cli.mjs stage /tmp/srg20-posterior posterior 0x53522001 1
node integrations/sweepweave-ts/srg20/cli.mjs stage /tmp/srg20-inference inference 0x53522001 1
node integrations/sweepweave-ts/srg20/cli.mjs score /tmp/srg20-history /tmp/submissions.jsonl
```

Send only the chosen model_input files, with packet IDs withheld from prompts; use a fresh independently frozen seed for private validation. Keep paired arms separate and randomized. Standalone CLI and SRG-08 runner compatibility remain unexecuted.