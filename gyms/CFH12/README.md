# CFH-12: coefficient-level acquisition and joint residue certificates

**Disposition:** pass fine-grained logical acquisition and finite certificate soundness. Fixed-pair joint refinement fails the improvement gate; adaptive shared-coefficient refinement is exploratory. No paid compute, neural fits, production corpus admission, independent conjecture confirmation, or Lean proof of these new bounds.

## Interface

Use the CFH-05/09 depth-two grammar (90 canonical routes), three graph cards, two observations maximum. Each observation requests a coefficient modulo 2, 3 or 5. Unlike CFH-09/11, both acquisition arms pay in the same units: each previously unknown integer base-polynomial coefficient acquired costs one cell, once per episode. Whole-vector actions purchase all remaining missing cells of any required base polynomial; fine-grained actions purchase only coefficients with nonzero modular weights in the selected observation on the surviving version set. The latter can reuse those integer coefficients across other moduli and derived routes. Already symbolically known coefficients cost zero. This is a logical cost model, not a measured comparison of algorithms for computing individual coefficients. Full polynomial tables are generated offline and the online policy's known prediction interface reads only symbolic or purchased cells. No claim of physical CPU savings; setup, planning, and actual coefficient enumeration cost remain unpriced.

The exact offline planner uses the privileged complete reply partitions and dynamic programming over version set, purchase mask, remaining cell budget, horizon and price. The objective is singleton probability minus lambda times expected acquired cells, with lambda=p/400 for p in {0,2,8}, budgets 8 and 24 cells. It may stop without claiming a singleton. Granular acquisition weakly dominates whole-vector acquisition in this model: the fine-grained policy can emulate each vector policy's query choices and reply partitions while deferring unused coefficients until required, so no branch costs more. This is an interface argument conditional on the common unit cost and absence of bundle discounts. Greedy selects by conservative partition gain before the last observation, guaranteed singleton mass on the last, subtracting price times newly required cells; it falls back to exact free planning when its score is nonpositive. Free planning uses only known or symbolic residues.

## Fixed-pair joint certificate

For each affordable pair of observations on the same graph and at the same modulus p, each route's pair of predictions is an affine function of missing base coefficients over F_p. Group routes by shared base polynomial. Enumerate the attainable paired residue vectors by iteratively adding each missing variable's column, then map vectors to histograms on p^2 bins. The true histogram occurs in this set. Cross-group combinations relax possible dependencies between distinct base polynomials, preserving soundness. Singleton-count lower bounds follow from bin occupancy intervals (min=max=1 certifies a singleton) and, where tractable, minimizing the singleton count over convolved histograms with occupancies saturated at two. The independent comparator uses Cartesian products of individual reply supports with the same interval and saturated-DP scheme. Each intermediate enumeration has a 256-state cap; overflow discards the stronger bound, not any feasible completion. The coupled bound also retains the independent lower bound. This cap limits set cardinality, not total operations. The pair policy buys the union of required cells upfront and uses the fixed second query if necessary. A paid pair is selected only if its lower-bounded net utility strictly exceeds the feasible two-observation free incumbent. This is a restricted nonadaptive pair class, not the optimum robust adaptive joint policy.

## Data and primary results

Six newly generated decks (18 graphs, order 8–9), using CFH-11's random, Prufer-tree and geometric generators with 177 prior CFH-07 through CFH-11 graph-hash exclusions and intra-run deduplication. Other earlier graph manifests were not exhaustively excluded. Related public graph grammar, not independent conjecture families.

Hits out of 540, with mean charged coefficient cells in parentheses:

| Cell cap | Price | Exact vector | Exact cell | Greedy vector | Greedy cell | Free / both fixed-pair arms |
|---:|---:|---:|---:|---:|---:|---:|
|8|0|11 (0)|68 (2.2926)|11 (0)|50 (2)|11 (0)|
|8|.005|11 (0)|68 (2.2926)|11 (0)|50 (2)|11 (0)|
|8|.02|11 (0)|68 (2.2926)|11 (0)|50 (2)|11 (0)|
|24|0|65 (13.0019)|105 (12.4222)|50 (11)|60 (7.3333)|11 (0)|
|24|.005|64 (12.5463)|100 (10.4)|47 (10.6667)|50 (2)|11 (0)|
|24|.02|11 (0)|69 (2.3815)|47 (10.6667)|50 (2)|11 (0)|

At cap 8, granular exact planning identifies 68 vs 11 using vectors; greedy cell gets 50. At cap 24 and zero price, exact granular achieves 105 vs 65 while spending fewer logical cells on average. At .02 the greedy vector policy has negative utility (-.126296), while greedy cell achieves .052593 and exact cell .080148. The physical work required to calculate one cell rather than an entire polynomial can differ considerably; these observations establish an interface-level advantage only.

All 182 eligible root pairs satisfy 0 <= independent <= coupled <= actual singleton count. Each histogram convolution DP fits its cap in 164/182 cases; no group affine-vector fallback occurs, and 7,098 group histogram containment checks pass. There are zero strictly improved coupled pair bounds, and zero paid pair selections under either certificate. 52 pairs have zero lower bound despite positive actual pair singleton count. Summed lower-bound counts 24/24 versus actual 204 across pairs are diagnostic only, not episode-level hits.

## Exploratory same-deck adaptive continuation

Adapt CFH-11's certified free-first and paid-first continuation to coefficient cells. For a paid first query with known reply cells K_v and unknown count u, compute a guaranteed free-second-query yield G_v on K_v, subtracting unknown second predictions. Any second query must be free on K_v union U after the initial purchase. If z_v initially unknown hypotheses enter reply v, at most z_v additional singleton guarantees can be destroyed. Minimize the sum of max(1[|K_v|+z_v=1], G_v-z_v, 0) over all allocations with sum z_v=u. In the coupled variant restrict the allocations to affine first-response histograms, substituting purchased coefficient values and convolving independent base groups, with a 256-state cap and sound independent fallback. This continuation refinement couples the first-response histogram; it does not jointly solve all second-query affine constraints. Fully known free first splits can recurse into certified paid child decisions. Every purchased action strictly exceeds its current free incumbent, and each realized subtree clears its certificate.

Both cell caps have the same exploratory aggregate results:

| Price | Free | Adaptive independent | Adaptive coupled |
|---:|---:|---:|---:|
|0|11 (0)|25 (.6667)|29 (1)|
|.005|11 (0)|25 (.6667)|29 (1)|
|.02|11 (0)|11 (0)|11 (0)|

At price .005, net utility .048704 coupled vs .042963 independent and .020370 free. Both trail greedy and privileged exact planning. The two arms inspect different reachable states; the 27 improvements are paired lower-bound comparisons within the coupled arm, not independent-root gains. The initial independent arm has 1,121 bound checks; coupled has 1,479, of which 1,241 retain histograms and 238 fall back. All checks pass against actual free continuation. The coupled arm improves 27 bounds; 679 zero guarantees still miss a positive actual continuation. All 20 paid tree decisions (8 independent, 12 coupled, repeated across cap/price conditions) satisfy strict free-incumbent improvement and realized lower-bound checks. This follow-up reuses the primary decks and is exploratory.

## Verification

Primary: 22,680 exhaustive hidden-route outcomes, 702 base-vector comparisons using direct enumeration, 47,250 derived residue comparisons (26,453 available symbolically), 120 small affine-histogram exhaustive enumeration tests, 182 fixed-pair soundness checks. Follow-up: 6,480 outcomes and 2,600 candidate bounds. Every episode respects the cell and observation caps, and singleton promotion is checked against the fully partitioning replay. Exact planners' replay equals their DP root utility. Aggregate exact cell utility exceeds or equals all primary policies at each cap and price. No statistically independent family inference. The offline auditing code can populate memoized hypothetical states, but the policy selects only on the matching state, purchase mask, symbolic expressions and certified quantities, never on unpaid exact replies.

Next: measure genuinely targeted coefficient computation rather than logical cell counts, include bundle discounts and planning work, and test a separately registered family with explicit robust adaptive joint bounds. Do not promote another neural policy before measuring that interface.

## Reproduction

From gyms/CFH12 (requires earlier CFH04–11 source dependencies, Python 3.13, NetworkX, NumPy/SymPy/Torch inherited imports):
```sh
OPENBLAS_NUM_THREADS=1 python coefficients_joint.py --prior /path/to/cfh07_candidates.json.gz /path/to/cfh08_receipt.json.gz /path/to/cfh09_receipt.json.gz /path/to/cfh10_receipt.json.gz /path/to/cfh11_receipt.json.gz --out receipt.json
OPENBLAS_NUM_THREADS=1 python safe_cell.py receipt.json --out safe.json
```
Both local CPU runs exited 0. No raw receipt bytes or weights committed. SHA-256:
- coefficients_joint.py: c5193da39f265228281ce42f2253a4c00d2c5bc9853a48ce55a89a9284e5f47c
- safe_cell.py: 02f52f2a6ca1504fcc56a871e448c920e88fe81fd3eb5f8fb08f488dcc540bc2
- receipt.json: 468d5db39cdf8bd7fd3cc3a2864903e3f79be0bad0e4629a3d482e7851cea7fe
- safe.json: 3eae420668178d7b2b3965a667a689ff92e0dcd0a9a93df504f31c2ae7ec735a
- gzip receipts: 7a1e7cab562181282495775879b5d50aa522cc15d25f768e5a47fc74bad0341f and 252c84ca8c8b28008459026ad10b47fb1c5d90fbbddfc92217e1f5403cadf194.

Repository-wide CI pending. No new Lean claim, independent conjecture confirmation, or production corpus admission.
