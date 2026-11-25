# CFH-06: charged hypothesis acquisition and partial symbolic certificates

**Status:** CPU public finite development, exact arithmetic and descriptive logical-resource tradeoffs. No training, neural mechanism, independent conjecture confirmation or paid compute. Continuation of CFH-05.

## Interface and accounting

Use the depth-three canonical grammar of CFH-05 (220 routes), three graph cards per deck, coefficient residues modulo 2, 3 and 5. A purchased base group is keyed by (card, left deletion, right deletion, complement, invariant). There are 68 groups per card and 204 per deck. Purchasing one group supplies the exact base polynomial and all derived route vectors in that group. Count each card/group purchase once per episode, even when two cards could share a transformed graph; charge materialized route vectors separately. Four hidden-route observations maximum, with acquisition caps 0,18,39,68,100,204. Truth is uniform over 220 canonical route labels in the exhaustive scoring enumeration; observations alone may leave aliases within a deck.

This is an offline exact emulator. Environment tables are computed for replay, including the full-interface ceiling; policies may read exact residue masks only restricted to purchased groups. Neither the true route nor the hidden-route replay subset enters the policy or its score. The ceiling is not a policy input. Cheap predictions for symbolic arms are generated solely from graph facts and coefficient identities. Setup costs: 199,980 route/probe symbolic tests across 12 decks (mean 16,665 per deck), including unknown outcomes; at most 204 distinct base-fact computations per deck. The symbolic tables are reusable for episodes on the same graph deck, but should be charged if the deck is new. The non-symbolic policies do not use those tables. The evaluator records actual logical base acquisitions, full derived-vector materializations, observation counts, probe scans and retrospective checks separately. No real lazy evaluator latency, wall-clock speedup, or equal cost per invariant is claimed; chromatic enumeration and a matching polynomial do not generally cost the same. Mask operations and symbolic table setup are not free.

## Sparse identities

For a transformed simple graph of order n, m edges, degrees d_v, triangle count t and z isolated vertices, the following coefficients are available without full polynomial enumeration:

- Independence and clique enumerators: constant 1, linear n, quadratic binom(n,2)-m or m, highest coefficient the indicator of an empty or complete graph.
- Matching-size enumerator: constant 1, linear m, quadratic binom(m,2)-sum_v binom(d_v,2); coefficients above floor(n/2) vanish.
- Chromatic polynomial: constant zero (n>0), top coefficient 1, next -m, next binom(m,2)-t.
- Dominating-set enumerator: constant zero (n>0), linear count of universal vertices, top coefficient 1 and next n-z.

For base coefficients a_j, derivative order d, shift s and residue modulus p, the coefficient at k is the sum over j>=k+d of a_j (j)_d binom(j-d,k) s^(j-d-k), reduced modulo p. If every unknown base coefficient has multiplier zero mod p, the result is exact using sparse identities alone. Otherwise return unknown. Zero derivative tails are handled by an empty sum. The code audits every reported known residue against the complete exact polynomial evaluator from CFH-05. No inferential imputation of unknowns.

For a version set of size N, a probe has known-response counts n_v and u=N-sum n_v unknown hypotheses. Unknowns survive every reply; the conservative lower bound on expected elimination (under a uniform prior on the current version set) is
G/N = N - [sum_v n_v(u+n_v) + u(u+max_v n_v)]/N.
This is a lower bound because an unknown truth can yield at most u+max n_v surviving hypotheses. The uniform-on-version-set score is a heuristic when earlier partial observations have changed the actual conditional distribution. The elimination rule itself is sound regardless of prior. At the final query, rank known singleton guarantees before gain. This is conservative: some replies with one unknown and no known hypotheses could also isolate the unknown; the score does not count them. The true class is retained at every state. Only singleton sets are promoted, and every promotion is checked against hidden truth. Unresolved sets abstain.

## Policies and experimental custody

Eager acquires groups in card order, largest route group first if truncated, until the cap; it never buys more after observations. Lazy scores available probes and buys surviving groups on one card at a time when conservative expected elimination is below 50% or no informative split exists. Select the card giving largest coverage of surviving hypotheses under remaining budget; tie-break by fewer groups then card order. Symbolic-lazy adds the sparse identities. Symbolic-only is its zero-acquisition version. After the initial public results, add four exploratory arms: recheck versions of lazy/symbolic-lazy revisit previous replies after new acquisitions; terminal versions also buy additional groups on the last observation step while there is no guarantee of identifying all surviving routes in one query. The terminal rule can spend all remaining budget if needed but often buys few additional groups because the version set has shrunk. No learned models are fitted. Baselines are specified heuristics, not globally optimal joint acquisition policies.

Twelve new deterministic public decks (8 shift generator decks, 4 structured decks) use seeds 96000..96007 and 96100..96103, distinct from CFH-05. Each is exhaustively replayed for 220 hidden routes, yielding 2640 tasks. Graph cards and route variants are related; no isomorphism deduplication or independent family split is claimed. These are public development cases, not independent conjecture roots.

## Results

Hits out of 2640, with four observations maximum. Initial arms:

| Base acquisition cap | Eager | Lazy | Symbolic lazy |
|---:|---:|---:|---:|
| 0 | 0 | 0 | 68 |
| 18 | 0 | 0 | 508 |
| 39 | 0 | 0 | 1574 |
| 68 | 1660 | 1660 | 1849 |
| 100 | 1816 | 1999 | 2000 |
| 204 | 2363 | 1999 | 2000 |

At cap 39, all three arms buy exactly 39 groups and materialize 191 route vectors per episode. The non-symbolic heuristics retain too many uncomputed routes to reach a singleton; this zero score is not an impossibility theorem for the resource cap. Symbolic lazy identifies 1574/2640 (59.62%) with mean remaining version size 2.277, against 30.459 for the non-symbolic controls. Symbolic setup supplies 133,698/199,980 residues (66.86%); all known residues match exact evaluation. At zero base purchases it identifies 68 cases. At cap 68, symbolic adds 189 hits to the shared 1660 baseline. At large caps, the 50% acquisition trigger stops early and loses hits relative to fully eager.

Exploratory variants at cap 100 (same public decks):

| Policy | Hits | Mean base acquisitions | Mean route vectors | Mean probe scans |
|---|---:|---:|---:|---:|
| Eager | 1816 | 100.000 | 390.000 | 282.515 |
| Lazy | 1999 | 69.144 | 224.960 | 380.856 |
| Symbolic lazy | 2000 | 68.731 | 223.504 | 372.755 |
| Lazy recheck | 1999 | 69.144 | 224.960 | 380.856 |
| Symbolic recheck | 2000 | 68.730 | 223.497 | 372.755 |
| Lazy terminal | 2167 | 72.470 | 241.625 | 422.264 |
| Symbolic terminal | 2167 | 72.219 | 240.691 | 416.775 |

Retrospective checks alone barely change outcomes. Terminal lazy adds 351 hits to eager at cap 100 while reducing mean base acquisitions by 27.53%; it performs more probe scans. At cap 204, terminal lazy retains 2167/2363 (91.71%) of full eager hits while using 72.47/204 (35.52%) of base acquisitions. This is a quality/cost tradeoff, not equal-optimum speedup. The full observation-interface ceiling is 2541/2640; 99 cases cannot be identified with this deck interface even at unlimited queries. The 4-query eager score is a heuristic and does not equal the optimal planning ceiling. The terminal variants are exploratory and need prospective testing before promotion. At low caps, use symbolic screening; at higher caps, acquisition timing helps even without sparse identities. No aggregate compute claim without cost weights for base enumeration, derived materialization, probes and scans.

## Verification and replay

113,520 full hidden-route traces across 516 deck-policy-cap aggregates. Every true route stays in the version set, every singleton is correct, and each episode obeys both budgets. No independent-root significance testing or causal claims. The upstream CFH-05 arithmetic was independently audited there; CFH-06 known-coefficient comparisons use its exact evaluator as the reference, not a new independent proof of all formulas. For future work, implement actual on-demand coefficient computation and per-operation costs, then freeze novel construction families and compare cost-aware planning against exact lazy acquisition on small cases. A state-transition training export would include sparse identities, unknown masks, acquired groups, query, observation, sound restriction and abstention, but none is admitted to DataGoblin in this pilot.

From gyms/CFH06:
```sh
OPENBLAS_NUM_THREADS=1 python lazy_acquisition.py > receipt.json
```
Python 3.13, NumPy 2.3.5, NetworkX 3.6.1, SymPy 1.14.0; imports CFH-05 and CFH-04. Source SHA-256 61a567dc9f92c60ebe08c4b43c2c38e90635f4a6d211a890c349a14321510325. Final receipt SHA-256 f5a1ba6511eaa6d45017a76a030edd84b2835d06ce39c87c79852b89b316b59c. Initial receipt SHA-256 7f76b3b11cbd8645be045f9730dc844e55ec6a8a3839e7cbca920e2ba25cf4ab. Initial source SHA-256 7f4b641e666bfcc6230174f1c6aedea6e915f65333db178af2c1a37b2be29357. Generated receipts not committed. Source blob verified against the tested local file. Full repository CI and Lean rebuild not performed.
