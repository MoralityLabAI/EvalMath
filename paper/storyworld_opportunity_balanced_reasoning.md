# SRG-16: Opportunity-balanced storyworld reasoning under a declared prior

2026-11-25. Synthetic public diagnostic. Continuation of [SRG-15](storyworld_radio_repair_and_belief_policy.md). The SRG-13 Reservoir Dogs candidate and rejected radio repair are unchanged. Evidence: exact finite-prior Bellman computation, independently enumerated small reference cases, actual policy-table rollouts on a matched public sample, and source-executed SWMD-SRG/2 replay. No model inference, private validation, Lean certification or production editor integration.

## 1. A controlled storyworld

A dock operator routes cargo over H slots. A public schedule marks exactly n=H*d/4 active slots for d in {1,2,4}. Every active slot has independently drawn stake w in {1,3}, equiprobable. Current stake and K observed binary signals y are shown, while future stakes/signals remain hidden. All bits are fair and independent under the declared generative prior. The true first bit x1 equals y1 with probability q=q8/8; otherwise it is flipped. The other J-1 true bits equal the corresponding observed bits. The correct dock is XOR(x1,...,xJ). K-J further bits have no causal role. For example, J=5 uses the signed product of five BNumbers (bit 0 = +1, bit 1 = -1); its sign determines the correct dock. This is a controlled interaction width, not a validated psychological difficulty scale.

Commit to dock 0 or 1, or delegate to a trusted technician (audit). A correct commitment earns w; an incorrect one earns zero. An audit is guaranteed correct by the public rules and spends the single per-shift audit credit. Every action advances one slot. All neutral-slot actions earn zero and leave the resource unchanged. No outcome feedback is released before the end. The objective is expected weighted cargo units; completing every active slot correctly is a secondary metric. A known, scarce, explicitly declared reliable fallback is an affordance, with no evaluator-only late rescue.

H in {4,8}; d in {1,2,4}; q8 in {5,7,8}; J in {1,5}; K in {8,32}. 72 full factorial conditions, 32 matched tapes per condition, 2304 campaigns. Shared tape fixes stake, schedule, common observations, menu order and error words across J/K/q8; H and density change opportunity count and/or position. H4/d2 and H8/d1 match n=2; H4/d4 and H8/d2 match n=4. Same n and q imply identical prior value for all spacings. The single audit credit is held fixed; its fraction of opportunities varies with n. Structural decision density is n/H. Enumerated policy-cell density differs because resource states are duplicated only when reachable. Neither the 23,484 rows nor the 2,304 campaigns are independent statistical replicates: there are 32 shared random tapes. Public xorshift32 is for deterministic diagnostic sampling, not secure randomness or proof of the ideal prior. Empirical mean stake differs from the ideal prior.

## 2. Exact oracle

Let V(n,b) be expected remaining utility before a new active slot, with n active slots and b in {0,1} credits. V(0,b)=0. Given the observed parity z, the posterior probability of the correct dock being z is exactly q. Define

    Q_commit(z) = q*w + V(n-1,b)
    Q_commit(1-z) = (1-q)*w + V(n-1,b)
    Q_audit = w + V(n-1,0), only if b=1
    V(n,b) = (1/2) sum_(w in {1,3}) max_legal Q.

At a neutral slot all legal action values equal V(n,b). By induction and conditional independence, the public schedule, current stake, observed parity and remaining credit suffice for the entire future policy; no hidden continuation is used. The first-bit flip holds the posterior effect size fixed across J/K. For q>1/2 every active slot has a strictly positive decision range, even when optimal actions tie. Thus structural active slots and informative decisions agree exactly on every enumerated row.

The full-state weighted ceiling is the sum of active stakes (expected 2n). The permitted-information ceiling is V(n,1). The exact greedy expected value (audit the first active slot when q<1, otherwise commit) is 2+2q(n-1) for n>=1. Across the registered grid the oracle prior expected total is 14,447.5 of 16,128, greedy 14,208 of 16,128; exact gain 239.5 units, or 1.485 percentage points of full expected utility. These are population-prior values, distinct from sample rollout totals. The policy is optimal for weighted utility, not the all-correct probability objective.

## 3. Scoring correction

Every realized root exports one packet for each reachable (slot,credit) combination, including off-policy resource states. Every packet states the prior and rules, current evidence, public schedule, legal action IDs and remaining horizon. The model sees no latent bits, future draws or gold scores. The scorer rebuilds verifier-only targets and scores complete submitted policies by composed rollout. Missing, duplicate, illegal or malformed submissions fail the row; an affected campaign stops, retains earned utility and receives zero utility for remaining opportunities. Unknown IDs are reported. The perfect-campaign count requires a complete rollout. Score raw all-cell accuracy, informative accuracy, normalized local regret (sum of Q gaps / sum of action ranges, invalid charged worst range), weighted realized utility / weighted full attainable utility, structural and enumerated opportunity density, perfect campaigns, and exact prior oracle fraction. Off-policy local regret is diagnostic, not actual trajectory regret.

| Control | Raw accuracy | Informative accuracy | Weighted utility | Perfect campaigns |
|---|---:|---:|---:|---:|
| Exact oracle | 100% | 100% | 13380/14832 (90.21%) | 1696/2304 |
| Greedy audit | 90.67% | 84.14% | 13280/14832 (89.54%) | 1744/2304 |
| Evidence commit | 86.44% | 76.97% | 12500/14832 (84.28%) | 1520/2304 |
| First legal | 68.61% | 46.67% | 9130/14832 (61.56%) | 644/2304 |
| Deliberately wrong commitment | 41.13% | 0% | 2332/14832 (15.72%) | 120/2304 |

First legal is order-controlled by a randomized menu on each matched tape. At 25% structural density it scores 87.39% raw, 41.41% informative. Wrong commitment scores 78.49% raw and 0% informative in that stratum; at 100% density its raw accuracy is zero. Neutral cells must not dominate an assessment of reasoning. The wrong control occasionally succeeds because evidence is noisy. The oracle's realized advantage over greedy is 100/14832 (~0.67 pp), smaller than the population-prior advantage; this finite sample does not support a confidence interval treating matched rows as independent.

## 4. SWMD and geometry

The verifier-only generator emits a private per-root SWMD-SRG/2 world. The true destination is computed by the frozen signed-product reaction guard, then cumulative earned stake increases by w/(4H) on a successful reaction; this is bounded and dyadic. Public signal coordinates refresh only on slot advancement. Audit credit is updated by an explicitly gated reaction. All outcome reaction prose is identical, and the earned-utility coordinate is hidden. Full private source contains future and latent states; provide only the declared public rules and observation projection to the model. The public schedule is supplied by the task packet; the private fixture encodes its realized schedule as well.

Replay the five controls and each legal one-step counterfactual at each reached state for one representative per factorial cell: 72 fixtures, 6036 transitions, exact reward/credit agreement, menu and signal agreement, hidden coordinates excluded from observations, valid terminal routing. This is sampled runtime conformance, not exhaustive verification of every possible latent tape. The maximum raw squared coordinate-step energy is 73.5625 because refreshing many public signal-cache coordinates can dominate geometric movement. This is an observation-cache effect, not a large cargo outcome. An authoring geometry certificate should report separate energy for persistent semantic state, epistemic/observation refresh and utility ledger; changing K must not itself trigger a deus-ex-machina penalty. The larger fixture contains more engine bookkeeping coordinates than K, so K here denotes current observed dimensions, not total SWMD coordinate count.

## 5. Validation and limitations

30 independent small Bellman checks enumerate observed parity, stake, all eight error words, action and future branches through n<=4; exact agreement. 2112 matched tape comparisons, all informative-label checks, malformed/missing controls and exact oracle/wrong-policy scoring passed. The source-level SWMD tests used the pinned SRG-04/SRG-05 runtime in an isolated ECMAScript executor. Node filesystem staging/scoring and HTTP inference are provided but not run in that executor. The fixed public dataset and sequential packet IDs are unsuitable as sealed tests. A private evaluation must use a separately frozen unpredictable seed, disallow seed/source access, freeze model and runner, and preserve only the public observation protocol. Do not train on the public gold and then report the same corpus as held-out. Real model capability and storyworld authoring quality remain unmeasured. The parity family is deliberately artificial; a future benchmark should introduce multiple evidence structures and author-reviewed narrative families while preserving effect size and opportunity count.

Next gate: measure Bonsai/Inky/Data Goblin on a balanced small pilot, then freeze a new seed and compare paired per-tape informative accuracy and realized utility across J/K/q/H, including exact expected value and greedy controls. Add a harder long-horizon resource-coupling family if the ~1.5 pp prior planning advantage is too small for reliable model discrimination. No paid compute used.
