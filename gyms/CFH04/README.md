# CFH-04: Hidden invariant identification by adaptive mathematical probes

**Status:** exact finite algorithmic result on public development; no neural fits, causal effect claim, independent conjecture test, or paid compute. Extends CFH-02/03 from given invariant to hidden route, with the hypothesis library explicitly supplied.

## Mathematical contract

A route is one of five graph polynomial invariants (independent-set enumerator, clique enumerator, matching-size enumerator, chromatic polynomial, dominating-set enumerator) applied to the original graph, complement, or induced subgraph obtained by deleting vertex 0. Graphs are simple labeled graphs of order 4–7. The observation is an exact coefficient modulo 2 or 3 of the hidden route's polynomial on a supplied graph. All routes use padded coefficient vectors indexed by the original order. The matching-size enumerator differs from the signed matching polynomial.

There are fifteen syntactic route labels. Independent sets of the complement are exactly cliques of the original graph, and vice versa. Quotient these two global alias pairs before scoring, obtaining thirteen canonical classes. The replay exhibits distinguishing graph/coefficient witnesses for every pair of these thirteen canonical classes across the union of the public decks. A black-box observation cannot recover which syntactic member of a global alias class was intended; such provenance needs separate evidence.

For a version set S and probe a, let S_v={h in S : a(h)=v}. A query reply restricts S to its corresponding cell. A singleton licenses identification; larger sets must remain ambiguous. Let F_b(S) be the maximum number of hidden canonical classes in S identifiable with at most b further probes. F_b(S)=1 for a singleton, F_0(S)=0 for larger sets, and otherwise
```
F_b(S) = max_a sum_v F_(b-1)(S_v)
```
with nonsplitting actions removed. The recurrence is exact by induction on b: any decision tree starts with one probe, and each reply permits an independent optimal subtree. The code breaks ties by minimizing the total calls over uniformly enumerated hidden classes. The exact static control enumerates all fixed subsets of up to b distinct probe partitions; duplicate queries or distinct queries with the same partition do not improve a fixed schedule. Static schedules can stop on a singleton or when no probe splits the remaining set. Their primary objective is the same maximum count of singleton identifications; static tie-breaking does not optimize calls.

The full-interface ceiling is the singleton count of the common refinement of all available partitions. A full coefficient-vector interface supplies a stronger observation model and is measured separately. All policies receive the same exact hypothesis prediction tables; their construction is a shared setup cost of 3,952 logical canonical-route polynomial evaluations (304 graph-card occurrences times 13), excluding audit and alias checks. Memoization reduces actual work. Query counts are exact logical observations, not equal wall-clock costs. This benchmark assumes an available explicit hypothesis library and deterministic correct replies. It does not solve open-ended conjecture discovery.

## Development corpus and controls

Fixed seed 20261125. 32 mixed six-graph decks, 16 sparse-biased six-graph decks, 16 restricted single-graph decks (complete, empty, cycle, path). Each deck is exhaustively scored under all 13 canonical hidden routes, yielding 832 deck-route tasks. Repeated isomorphic graphs and shared constructors are allowed here; decks, route variants, policies and budgets are dependent, public examples, not independent conjecture roots. No train/test or sealed split.

Independent arithmetic audit: 426 distinct labeled transformed graphs, 2,130/2,130 full coefficient-vector comparisons passed. Primary bitmask/recursive enumerators compared against direct subset, edge-subset and restricted-growth partition enumeration, with independent elementary-symmetric-sum chromatic coefficient expansion. Additional small-graph controls use known identities and direct proper-color counts. All global alias assertions pass. Every trace retains the true canonical class, and every promoted singleton is correct. These are finite verification claims.

## Results

Singleton identifications (out of 832):
| Policy | 1 probe | 2 probes | 3 probes | 4 probes |
|---|---:|---:|---:|---:|
| Random fixed partition order | 12 | 78 | 217 | 378 |
| Static entropy greedy | 3 | 282 | 709 | 771 |
| Exact optimal static | 70 | 364 | 731 | 775 |
| Adaptive entropy greedy | 3 | 297 | 755 | 778 |
| Adaptive minimax greedy | 0 | 283 | 754 | 778 |
| Exact optimal adaptive | 70 | 432 | 773 | 778 |

At budget 2, exact adaptation adds 68 identifications over exact static (8.17 percentage points of all cases, 18.68% relative). At budget 3, it adds 42; at budget 4, three. Entropy and minimax optimize different quantities than singleton success, explaining why the greedy policies can be weaker at low budgets. Optimal adaptive at budget 4 uses 2,112 calls total (mean 2.538 per task) and reaches the entire residue-interface ceiling. At budget 3 it uses 2,097 calls. No claim that the adaptive implementation is faster than static search, or that the gain is neural.

All mixed and sparse cases (624/624) are identifiable at budget 3 with adaptive entropy. Restricted cases: 154/208 identifiable from all residue probes, 158/208 from all exact coefficient vectors. Across the entire corpus the ceilings are 778/832 (residue) and 782/832 (full vector). The best single graph for a full-vector query attains the latter ceiling on each deck. Fifty tasks remain ambiguous even with all full vectors on their given graphs; four more are lost by observing only residues. These numbers exclude the two globally equivalent route pairs already quotiented out. Do not label an indistinguishable alternate route as an incorrect mathematical answer without additional provenance. No false singleton promotions in 19,968 policy/budget/route traces. Random baseline samples a single fixed partition ordering per deck, not a Monte Carlo confidence estimate.

## Research disposition

PASS exact adaptive-query advantage at budgets 2–4 in this finite interface. This is a positive structural result on feedback-conditioned search, not evidence for recurrent neural architecture superiority. The optimal dynamic program knows the entire finite hypothesis library. If full-vector observations are equally cheap and available they eliminate the need for the residue strategy on these decks; actual source retrieval, coefficient derivation, verifier costs and query restrictions require separate measurement.

CFH-05 candidate: grow the route grammar to compositions of graph transformations and polynomial operations, collapse extensionally equivalent routes, and compare amortized learned query proposals to exact planning and computationally matched greedy controls when hypothesis-side prediction costs matter. Train only after fixing genuinely independent family splits and prospectively registering the scientific effect, sham and root-level power requirements. No mechanistic preflight was run on invented independent worlds; this experiment is finite arithmetic, not a neural causal study. Include explicit abstention and semantic-equivalence class supervision for DataGoblin. No admission or training quota change.

## Replay

Python 3.11+ recommended (tested environment Python 3.13 / NetworkX 3.6.1). From gyms/CFH04:
```sh
python hidden_invariant.py > receipt.json
```
Receipt contains 64 decks, 1,536 deck-policy-budget aggregates, 19,968 full query traces, exact rational mean version-set sizes, and source hash. Source SHA-256: 3af465d20b8d315f6cade3c86027604ccb568ce600b996f78597dad24c88ffe2. Local receipt SHA-256: 259c07df0084e76c104e15e1872f0f8e6a5f95d8f3bc0fd4dfeae1f854f0c1fe. Generated receipt not committed; replay regenerates it. Repository-wide CI and Lean build remain outstanding.
