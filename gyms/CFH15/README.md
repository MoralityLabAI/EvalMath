# CFH-15: deterministic fuel, interruptible coefficients, and factored setup

**Disposition:** pass finite cooperative-fuel and transactional soundness checks; retain factored symbolic setup for development. Hold hard physical runtime, general discovery-policy, and learned-policy promotion. No paid compute, independent conjecture confirmation, new Lean theorem or corpus admission.

## Fuel contract

The inherited public CFH-12 depth-two grammar has 90 canonical routes, three graph cards and at most two coefficient-residue observations. Graph order is restricted to 9–10 in the replay (transformed graphs remain small). The fixed route grammar is a public library. A fresh episode constructs the graph-dependent sparse coefficient identities and query descriptors, then compiles expressions eagerly or lazily. All declared graph-dependent setup, expression compilation, query-selection, acquisition and restriction charges are counted in the ledger. No exact unpaid coefficients are read by policy choices.

The meter accepts positive integer charges only if they fit its remaining allowance. A successful charge increments both the total and its named phase by the same amount. Thus, by induction over charges, used <= cap and the ledger sums to used. A selection sublimit reserves a fraction of remaining fuel for acquisition and restriction; exhausting that sublimit keeps only fully compiled and fully scored candidates, then restores the outer cap. A coefficient Task advances a generator only after paying one unit, including the final return. A generator can suspend at any yield boundary and resume using its private local recurrence state. Its result is None until termination, and a completed task returns the exact coefficient tuple. This is an executable logical-work model: charges are defined at bounded recurrence, loop, graph/term and state transitions; there are also bounded host-language operations within or between those steps (sorting small lists, object allocation, dictionary construction, etc.). This is neither Python instruction metering nor a preemptive wall-clock, memory, or externally enforceable CPU cap. No mapping to milliseconds is claimed. Inputs and evaluator-owned reference construction, exhaustive tree replay bookkeeping, output serialization, and audit assertions are outside the policy ledger. Each shared replay branch inherits its own logical budget and prior state; branch-copy work for simulating the environment is not charged.

The five invariant families use targeted and vector generator recurrences: independent sets and cliques (complement adjacency for clique), matchings, domination, and chromatic polynomial via independent color-class partitions and signed Stirling coefficients. All recurrence memo tables are private to a call. A fixed batching rule buys the full coefficient vector when twice the requested count is at least the missing-cell count plus one, otherwise a targeted batch. Completed batches are staged in a private value map. The whole acquisition/restriction transaction commits only when every requested residue is known and the exact reply partition has been constructed. On exhaustion, discard staged values, keep the previous version set and previously committed purchases unchanged, and terminate or take a fully scored free fallback if available. Failed work stays charged. The episode policy does not resume a failed transaction after its cap expires; resumability is tested separately at the coefficient-task level, not a persistent saved-process checkpoint. Each committed value and reply partition is checked against the independently built CFH-12 reference before replay branches. Every surviving version set is sound and only a singleton is promoted.

## Primary finite replay

Six new decks, 18 parent graph cards, sparse/dense random and geometric generators, order 9–10. Exclude 255 prior graph-hash keys from CFH-07 through CFH-14 manifests. This is the same related public graph grammar; exclusion does not establish independent conjecture families or a sealed evaluation.

Compare eager scan, eager index, lazy scan, lazy index, and lazy indexed free-only selection across caps 12,000 / 30,000 / 60,000 / 120,000 fuel. Every condition has 540 hidden routes. The anytime scan uses the same degree/card/modulus ordering, conservative partition-gain heuristic for first query, and a heuristic singleton/unknown-mass score for the second; discount paid candidates by 20/(20 + missing cells). These scores are not certified expected discovery values. Search uses at most two-thirds of remaining fuel initially and three-quarters on the final observation. The index groups routes by equal coefficient dependency. Its count of logical group visits may exceed the scan count at some states; the metering model does not assign fewer units to indexing merely because previous Python timings favored it.

| Fuel cap | Eager scan | Eager index | Lazy scan | Lazy index | Lazy free |
|---:|---:|---:|---:|---:|---:|
|12,000|0|0|0|0|0|
|30,000|0|0|0|0|0|
|60,000|0|0|0|0|0|
|120,000|43|43|43|43|8|

At 120k, paid scan variants average 65,769 fuel and index variants 66,443. In particular, scan preparation averages 9,346 setup plus 48,519 expression-compilation units. Preparation dominates the charged work. Eager preparation consumes the entire 12k and 30k caps before a query on all decks, and does so at 60k on one deck. Lazy paid policies exhaust transactions at all three smaller caps. The primary pilot demonstrates enforcement, not a useful low-budget discovery policy.

180 exact coefficient cases (18 graphs of order 3,4,5,6,8,9; five invariants and two acquisition modes) match independent direct enumeration. Random quanta 1..7 reproduce all results with identical total fuel (13,518 advance calls). 3,597 cutoff tests enumerate every cap for small computations and selected boundaries for larger ones. At every tested insufficient cap, no result is published, and exactly the allotted advances are charged. The full-cap result is exact. The primary replay adds 10,800 outcomes and 197 attempted transactions (143 committed, 54 interrupted). The reference audits 702 base vectors and 51,030 residues, of which 27,171 are symbolically available. All checks pass; no logical budget overrun.

## CFH-15B: exploratory factorization on four new matched decks

After observing the preparation bottleneck, reuse transformed-graph statistics (edge count, degree summaries, triangle count) across invariants, and reuse nonzero modular derivative/translation weights across expressions with identical (transformed order, target degree, modulus, derivative order, shift). The shared expression is
    sum_j a_j (j)_d binom(j-d,k) s^(j-d-k) mod p.
The weights do not depend on graph edges or the invariant. Caches contain only symbolic descriptors and known facts, not hidden replies. Charge building a template and applying each nonzero term. Sharing the same graph transform and weight template avoids repeated charged work; memory and physical time are not proved proportional to these charges.

Four further new decks (12 graph cards, excluding 273 prior keys including primary). Compare original lazy scan/index against factored scan/index, factored free, and exploratory guarded index. The guard reserves one quarter of the post-selection budget for an already-scored free fallback when a paid query is chosen and such a fallback exists. No guard fallback actually activated in this sample; its benefit remains untested. Compare original and factored graph descriptors/ID maps exactly, and all 372 compiled probe expressions, dependency partitions and sparse reply masks byte-for-structure. All equivalent. Full graph preparation plus expression compilation costs (original vs factored):
- deck 0: 60,658 vs 30,018
- deck 1: 52,219 vs 26,490
- deck 2: 52,069 vs 26,462
- deck 3: 59,398 vs 29,768
Aggregate 224,344 vs 112,738 charged units (49.75% reduction). These are deterministic units in the stated implementation model.

| Fuel cap | Lazy scan | Lazy index | Factored scan | Factored index | Factored guard | Factored free |
|---:|---:|---:|---:|---:|---:|---:|
|12,000|0|0|0|0|0|0|
|30,000|0|0|0|0|0|0|
|60,000|0|0|33|33|33|6|
|120,000|33|33|33|33|33|6|

Each condition has 360 hidden routes. At 120k, factored scan has the same 33 identifications as original scan with mean fuel 34,998 vs 62,899 (44.4% reduction); the factored index has mean 35,692 vs original index 63,593. At 60k, original scan and index yield no discoveries and exhaust all 360 episode transactions; factored paid arms achieve 33 and exhaust none. At <=30k even factoring does not resolve a singleton: the heuristic still commits to expensive queries or lacks a useful free candidate. The factored scan uses fewer metered steps than factored index at ample budget. This is an exploratory redesign on four fresh but related public decks; no causal claim about recurrence or independence.

Follow-up 8,640 outcomes, 258 attempted transactions (204 committed, 54 interrupted), 468 reference vectors and 33,480 residue comparisons. Combined: 19,440 outcome rows, 347 committed transactions, 108 interrupted transactions (tree nodes, not independent episodes), 1,170 base-vector checks, 84,510 derived-residue checks, 45,191 symbolic residues. Separate receipt verifier checks complete hidden-route coverage, query caps, nonnegative integer ledgers, used <= cap, and singleton scoring in all 216 policy/deck/budget groups. No false promotion or overrun. The acquired-coefficient and full reference checks are finite evidence, not a Lean proof of the implementation. Both programs exited successfully and tested source Git blob hashes match their committed copies.

## Replay

From gyms/CFH15, with the previous CFH-04..14 modules available and Python 3.13, NetworkX, and inherited dependencies:
```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python pilot.py --prior /path/to/cfh07_candidates.json.gz /path/to/cfh08_receipt.json.gz /path/to/cfh09_receipt.json.gz /path/to/cfh10_receipt.json.gz /path/to/cfh11_receipt.json.gz /path/to/cfh12_receipt.json.gz /path/to/cfh13_receipt.json.gz /path/to/cfh13_conservative.json.gz /path/to/cfh14_receipt.json.gz /path/to/cfh14_indexed.json.gz --out receipt.json
# repeat the same --prior list and append receipt.json:
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python factored.py --prior <same prior paths> receipt.json --out factored.json
python check_receipt.py receipt.json factored.json
```
Local SHA-256:
- fuel.py 89847df951d7aa0a9ab3e06890ec599d27d4f85853180c3255f77cc0f35768b2
- pilot.py 83318fbfcf3c2f6f406b8f6dd9dc80cd78fba00e30ac426ba12bb51816f9e549
- factored.py 3673e670c52999eed93f1ccc4bf91789ff32fb5da79c1b270a3b9fb0a4e05c5d
- check_receipt.py 46bd015fbade04b9803686e1b9ca7b39668548aacc0b80eda8f5e2823f11c43c
- receipt.json 2e8122cd75e3e800501f8c7b7802f8797a2a5258d6777faf41ca67f57b93b64c
- factored.json 7605febacef4cde06910908828bd1e435559e6acbbefae7bd9f5f883c592ed01
- gzip receipts b38a8ff46109dba897efa6b459dcc7f897e4db72173c7c211d102a91037ba193 and fe9cc264b9d27661fc2573bba46950fb783157c6562e7a50c5175f8e17eb5aca.

Generated receipts not committed. Repository-wide CI for these commits pending.

Next: improve budget-aware selection with incremental acquisition work limits and actual value-of-information estimates, preserving completed batches only with independently checked provenance. Prove the abstract meter and transactional state invariant in Lean, then test the factored interface on new mathematical families with a prospectively frozen operation-accounting protocol. Avoid more neural fits until a cheap, robust mathematical discovery interface works under tight budgets.
