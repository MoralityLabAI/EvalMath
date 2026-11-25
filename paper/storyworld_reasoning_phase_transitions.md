# SRG-17: Matched reasoning demands, nested beliefs and temporal-order witnesses

2026-11-25. Synthetic reference experiments. Continuation of [SRG-16](storyworld_opportunity_balanced_reasoning.md). No paid compute, real model inference, independently sealed test, Lean certification, production editor modification or new SWMD runtime replay. The SRG-13 authored world remains unchanged. This stage implements reference mathematics and model-facing packets; it is not a new production SWMD profile.

## 1. Resource planning with controlled K

A shift has H slots, exactly n=H*d/8 active slots, and B=max(1,floor(n/4)) audit credits. H in {8,16,32}, d in {1,4,8}, q8 in {5,7,8}, J in {1,8,32}, K in {8,32,128,1024} subject to J<=K. There are two time profiles, rising and falling. Among active slots floor(n/2) have low stake support {1,3}; the remainder have premium support {1,15}. Rising places low before premium, falling reverses that order. Neutral slots have support {0,0}. Each support comprises two equiprobable independent draws. The realized current stake and all future supports are public, future draws hidden.

The current signal has K binary observations. Its J causal positions are evenly spaced, public indices floor((j+.5)K/J). Their parity predicts the correct dock with probability q=q8/8, independently across slots. Audit guarantees correct delivery and costs one credit only on an active slot. Wrong delivery earns zero, right delivery earns the realized stake. No feedback before the shift ends. A model receives the entire public prior with its observation. Relevant bits are matched across K, and nuisance bits are drawn separately on the same tape. Thus increasing K changes the signal layout and length without altering the target distribution or attainable expected utility. The causal subset is disclosed; this tests accessing and combining given evidence, not discovering an unknown causal graph.

With T(i,b) the prior optimal value before the stake draw at slot i and b remaining credits, T(H,b)=0. At neutral slots T(i,b)=T(i+1,b). At active slots,

    Q_commit = q*w + T(i+1,b)
    Q_wrong = (1-q)*w + T(i+1,b)
    Q_audit = w + T(i+1,b-1)   (b>0)
    T(i,b) = E_w max_legal Q.

Since q>1/2, every active row has positive action range. This establishes the precise permitted-information optimum by backward induction under the stated independent prior. The full-information upper bound is the sum of active stakes. DP uses dyadic arithmetic, exact at the registered horizons for individual entries; aggregate ratios are reported to ordinary numerical precision. A matched stochastic policy-table rollout also reports realized reward, and conditional expected utility given the sampled public stake/signal tape (integrating out hidden error draws). It is important to distinguish these from the population-prior Bellman optimum. Invalid actions stop the campaign, preserving earned reward and receiving zero on remaining opportunities.

594 conditions, eight shared deterministic random tapes per condition (4752 campaigns), 334158 reachable policy rows, 238656 informative. The eight tapes, not the rows, are the independent-design replication units; the public pseudorandom diagnostic is not a cryptographic or independently frozen holdout. 4320 matched K/J prior/table comparisons passed. 36 independent brute-force decision tree checks, 11088 signal padding checks and 594 neutral-spacing value checks passed. The latter confirm that merely inserting neutral events cannot change the optimal utility when the active sequence and budget are fixed. The complete pilot oracle, missing and malformed policy scoring checks pass (28 conditions, 1286 packets at the public seed). H and density determine n and hence budget; within fixed n they can vary neutral spacing without altering the prior ceiling. This is a controlled design, not evidence of measured model phase transitions.

| Control | Raw accuracy | Informative accuracy | Realized utility |
|---|---:|---:|---:|
| Optimal policy | 100% | 100% | 93.38% |
| Premium-only audit (stake 15) | 90.64% | 86.90% | 93.24% |
| Audit immediately when q<1 | 80.43% | 72.59% | 88.01% |
| Commit to predicted dock | 79.02% | 70.62% | 82.97% |
| First legal | 60.94% | 45.30% | 60.78% |
| Commit to opposite dock | 28.58% | 0% | 17.03% |

Total expected prior utility fractions are 94.4446% optimal and 87.8093% greedy. Gain 6.6353 percentage points (SRG-16 was 1.485 points under its different design). The rising/falling prior gain for q=.625 is 20.3212/9.5377 pp; q=.875 gives 6.7737/3.1792 pp; q=1 gives zero. The stronger premium-only control nearly matches sample weighted utility: the remaining gap is just 396 of 273240 units (~.145 pp). This prevents a claim that planning is required to score highly on aggregate. Report meaningful first-action contrasts and pairwise planning witnesses as separate metrics.

## 2. Higher-order belief semantics

A distinct epistemic family has a uniform common prior on 27 worlds (a,b,c) in {0,1,2}^3. Agent i observes the two coordinates other than i. Its belief operator B_i maps a Boolean proposition to the majority over its three indistinguishable worlds. The formula B_i B_j P is evaluated compositionally, innermost first. The evaluator receives the full proposition table and actual world; the task is to compute other agents' beliefs, not to infer inaccessible facts. This is finite probabilistic belief at a strict majority threshold, not factive knowledge or arbitrary agent psychology.

For each of 16 base random proposition tables, use a randomly ordered chain of the three distinct agents, depth 0..3, every actual world, and a complement table. Every depth has 864 queries with 432 true labels. Complement symmetry follows because every information cell has odd size. The two algorithms independently agree on 1728 recursive checks (and 1728 complement checks). The oracle is exact and attainable at every depth. Count shared base tables as 16 design units.

| Depth | Use ground proposition only | Use one outer operator | Use two outer operators | Full |
|---|---:|---:|---:|---:|
| 0 | 100% | n/a | n/a | 100% |
| 1 | 73.84% | 100% | n/a | 100% |
| 2 | 61.34% | 72.22% | 100% | 100% |
| 3 | 57.87% | 64.58% | 68.75% | 100% |

The truncation control removes innermost operators, retaining the first k outer agents. Each depth has equal class balance; chance 50%. A depth-three formula can therefore remain consequential even after two operators have been computed. These are mathematical controls on the question family, not empirical LLM accuracy. There is no model-facing hidden answer. A separately frozen seed and model isolation are still required for a held-out test.

## 3. Matched temporal-order witness

The premium shortcut motivates a separate exact first-action diagnostic. Fix one audit credit, current stake w, current predicted dock, reliability q<1, horizon H, and two future active slots. Let their stake supports be A={l,h} (equiprobable), C={m,m}, with l<m<h and l+h=2m. Both orders A,C and C,A have identical expected future total 2m and identical unordered supports. Future audit option value, relative to commitment without credit, is

    Delta_AC = (1-q) E[max(A,m)] = (1-q)(h+m)/2,
    Delta_CA = (1-q)m.

At current stake w, audit now has marginal value (1-q)w. Choose m<w<(h+m)/2. In AC, uniquely optimal to commit to the predicted dock and retain the credit; in CA, uniquely optimal to spend the audit now. This is a direct mathematical counterexample to any deterministic order-blind policy, including policies using the full unordered distribution, mean future stakes, current stake, available resource and remaining horizon. Such a policy must give the same action on both rows, yielding at most 50% individual accuracy and zero both-correct pairs. For randomized actions independently sampled on the pair, the same individual expected bound holds but a nonzero both-correct probability is possible; zero paired bound is deterministic only.

H in {4,8,16,32}, q8 in {5,7}, m in {8,16,32}, l=1, h=2m-1, w=m+floor((h-m)/4). Two future slots randomly located, other slots neutral. Both rows of each pair share locations, current prediction, menu order and prior expected full utility. 192 pairs (384 packets) from eight public repeats. Exact DP and closed-form thresholds agree, all pairs have unique opposite optima. Always-audit and always-commit-to-prediction each get 192/384 with 0/192 pairs both correct. Oracle 384/384 and 192/192. Even a best deterministic order-blind action per pair loses at least 176 expected weighted utility units, 0.7682% of summed full-information expected utility. The regret denominator is deliberately broad; use paired exact-action accuracy as the main diagnostic. This family tests only the first action with optimal continuation; do not combine its regret with complete policy rollout totals.

## 4. Geometry and deployment

For parity over signed BNumbers z_j in {-1,+1}, the product of J causal signs is the correct predicted dock sign. A perturbation in any causal sign flips the parity, while changes confined to K-J nuisance signals do not. Thus one-coordinate causal support tests distinguish causal width from ambient observation dimension, even though the optimal action may be tied because of audit. The Dirac/Clifford norm of changes in raw observed coordinates is not a certificate of decision relevance. In the epistemic family, nesting is the number of composed information-set majority operators; it is a distinct axis from interaction width and K.

Reference source executed in an isolated ECMAScript runtime. The local Node 20+ stage and verifier scripts are committed but were not executed in a standalone Node environment. The SRG-16 SWMD-SRG/2 bridge was previously tested; SRG-17 adds independent mathematical reference packets and does not claim new engine conformance. Production TS editor integration, authored narrative realism, real compact-model inference, measured scaling curves and statistically credible held-out performance remain outstanding. Public IDs, seed and gold are unsuitable for secret validation.

Next: run the balanced planning pilot, epistemic queries and order-swap pilot on actual checkpoints with fixed inference budgets; evaluate paired per-tape policy utility, depth-specific correctness and order-swap both-correct rate. Freeze fresh seeds, hide verifier artifacts, and use separately registered families that defeat the premium shortcut. Then test authoring in genuine SWMD narratives with validated causal support, provenance and observation-channel fidelity.
