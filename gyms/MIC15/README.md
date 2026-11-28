# MIC-15: realized multi-step lemma acquisition and an exact reuse oracle

Cloud CPU public development after [MIC-14 draft #98](https://github.com/MoralityLabAI/EvalMath/pull/98). Original finite arithmetic proof-acquisition proxy. No external manuscripts, model fits or paid GPU.

## Problem and mathematical contract

The source is eight disjoint groups of 3–5 exact nonnegative integer entries, each with public ceiling 10. Each problem has 20 lemmas: eight group sums, six reusable pair sums and six rewarded target sums. Lemma statements claim an exact sum over a subset of the eight groups. A direct rule checks all entries in a lemma's support, with declared cost 1+3 times the entry count. A composition rule checks earlier acquired premises whose pairwise disjoint supports partition the target support and whose numerical sums equal the claimed bound; declared cost 2 plus premise count. Enumerate all such decompositions using earlier nonrewarded lemmas. Every lemma has a direct rule. These costs are prescribed synthetic proof-acquisition units, not measured verifier wall time. The rewards are nonnegative integers, the sum of separate target bound improvements (baseline sum of entry ceilings minus exact sum), weighted by independently generated integer importance 1..4. Some targets overlap: their weighted rewards are distinct declared objectives, not a single global scalar bound improvement.

A policy executes a sequence of acquisitions (lemma ID, proof-rule ID). The independent path replay recomputes each claimed exact bound, rejects duplicates, missing prerequisites and over-budget acquisitions, verifies the declared costs and reconstructs the earned reward. The proof library, rules, values and costs are known; the restricted acquisition calculus charges each lemma once. It models reusable proof verification and resource allocation, not the open-ended act of discovering new theorems.

For any selected set S of lemmas, the minimum cost equals the sum over i in S of the cheapest rule for i whose premises are contained in S. Necessity: any permitted acquisition path must choose an eligible rule and pay at least that term. Sufficiency: all premise indices are earlier than their conclusions, so acquire S in ascending topological order with cheapest eligible rules. Every term is attained independently. Hence optimal realized utility is maximum sum of rewards over S with this cost within budget. Canonical subset DFS computes the optimum, using the positive cost of all future acquisitions to prune. Its state counts are feasible complete selected subsets at the largest budget, not all candidate decisions or a polynomial complexity guarantee. The direct-only alternative is a six-item exact knapsack.

The second oracle, independently implemented using vectorized integer operations, exploits the further restriction that rewarded lemmas are sinks. Enumerate every one of the 2^14 infrastructure masks, sum their minimum acquisition costs, and evaluate every one of 2^6 target subsets against the cheapest target rules enabled by each infrastructure mask. This produces optimal reward and minimum cost at all budgets. It does not invoke Planner or canonical DFS. The factorization is exponential in general. The fully observed system is Markov in (acquired lemmas, remaining budget), so chronology has no additional normative information once that state is available; ordering could still affect a bounded model's computation. This experiment does not test a learned history effect.

## Development design and headroom gate

64 roots (four generator variants partition, hub, overlap, alternatives; 16 seeds 12000..12015 each). Each root has random numeric entries, target weights and relabeled groups. After four first-seed smoke tests with initial budgets 36/52/68 exposed mostly single-target acquisition, budgets were revised to 80/116/152 before the full sweep. The four smoke roots are included; no independent heldout or prospective claim. The protocol file records the adjustment. At primary budget 116, require >=5% mean relative oracle regret against width-32 beam AND the strongest fixed declared heuristic, and >=20% of roots with >=10% relative oracle regret against beam32, before any neural training. The gate thresholds and revised budgets were written before the full sweep. Root budget variants are repeated measurements; four generator mechanisms are not independently certified mathematical families.

All controls have the same rule acquisition budget. Immediate greedy selects only ready rewarded lemmas using reward/cost. Bundle greedy considers recursively constructed alternative proof packages for each target, charging only still-missing lemmas. Two-target lookahead chooses the first package maximizing the best attainable utility of two packages then replans. Width 8 and 32 beam searches retain the highest reward states per package depth, tie-breaking by density, lower cost and mask; store the best feasible incumbent. Package search and candidate evaluations are additional computation, not charged as proof acquisitions. No time-matched comparison. Candidate counters and machine-specific elapsed time are recorded separately. Unlike MIC-14, all executed policies realize their entire sequence without an oracle-provided continuation.

## Results

Mean percent of exact optimum over 64 roots at each budget (all optima positive):

| Policy | 80 | 116 | 152 |
|---|---:|---:|---:|
| Immediate | 78.146 | 69.417 | 62.225 |
| Bundle | 78.146 | 69.417 | 62.225 |
| Two-target lookahead | 98.250 | 73.435 | 70.463 |
| Beam8 | 97.998 | 98.383 | 98.932 |
| Beam32 | 100.000 | 98.815 | 100.000 |
| Direct-only exact | 79.545 | 69.784 | 63.165 |

Reuse strictly improves on the direct-only optimum on 44/64, 63/64 and 64/64 roots respectively; mean improvement 129.031, 306.734 and 499.266 utility units. Average oracle acquisition steps 4.469, 9.406 and 12.672. Strongest fixed primary control beam32 has 53/64 exact optima, 1.185146% mean relative regret, and only 2/64 roots with at least 10% regret. Beam8 obtains 50/64 exact optima at primary budget, 1.6169% relative regret. Primary mean candidate scans for immediate, bundle, look2, beam8, beam32: 58.06,122.03,3357.34,839.16,3130.78; mean measured per-policy times 0.044,0.471,8.709,3.698,11.232 ms. These counters and timings exclude problem construction, oracle computation and independent path checking; common cache use and run order can affect timing. No universal speedup claim.

Canonical DFS visits 11,263,662 complete affordable selected sets in the 64 roots (max budget), shared across the three budgets. Full primary run 19.029 s. Independent factorized oracle and replay audit 0.234 s across all 64 roots, verifying all 192 optimal reward/minimum-cost pairs and 1152 complete policy paths. These are separate observed total runtimes; the primary includes all five heuristic searches, so the ratio is not an isolated oracle speedup. Five targeted tests passed, including independent shortest-path enumeration on smaller libraries, verification of generated proof rules, invalid path rejection, realized paths and factorized oracle comparison.

**Headroom gate: FAIL_NO_FITS.** Zero new neural fits. A repository planner diagnostic on the four grouped oracle-minus-beam32 headroom values returns REDESIGN_OR_PILOT_ONLY, strict exit 2. Mean relative regret 1.185 pp falls below 5 pp. Two hard roots fail the 20% requirement. Deterministic zero sham is a placeholder, not independent sham calibration. The headroom diagnostic is not a causal-mechanism test. Full repository CI, an independent sealed evaluation, and matched total-resource comparisons remain outstanding.

## Replay

    cd gyms/MIC15
    python -m pytest -q test_mic15.py
    python mic15.py > results.json
    python audit15.py > audit_results.json
    cd ../..
    python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC15/preflight_input.json --strict

Local Python 3.13.5, NumPy for independent oracle, no torch needed. Planner Git blob 0ff062f76f5534d9f18425f986ae3e750397f50c matched the local copy. Source SHA256 mic15.py e8469dd721106d70bb6f782b8bcd2fdec09884eac5852e6cb6dfa70f11e43d7b; audit15.py 5dec65feee68ba412526530d04513b927359cbdec630068da30bed82a4ec9bbb; test_mic15.py e803a7d1acff0f40d6065acd3ba0aa18af8aad8cb078fd53082774a414c04a96; protocol.json e7d3c4c92816d5e3343c47311a706c710a687db3b3eff8bc588b8d7c29d72811. Timing-dependent local results.json d00c18b3af25f34428e006fc11f3d76bf0b4138095d61f4a2690b1cabb75b334 and audit_results.json bd56a3e98abe280ddcdb21641f2b665c5d536341fefdc7a1e1f562e212e94352. Raw receipts are generated artifacts, not committed. No new training allocation.

## Next gate

Use the exact factorized oracle as a teacher. Before a model fit, move beyond fully disclosed fixed proof costs and terminal-only rewards: make some rule applicability or verification costs unknown until checked, include rewarded intermediates that can be premises, and count acquisition and actual planning work separately. A belief-state planning experiment could test chronological evidence rather than merely a permutation of fully observed state. The original DLMST textual-discovery question remains untested. Require verified realized utility and headroom over strong deterministic search on independent sealed families, preserving public development roots outside confirmation. No DLMST training ingestion or token allocation.
