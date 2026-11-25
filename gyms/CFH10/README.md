# CFH-10: cost-priced mathematical discovery

**Disposition: pass finite cost-frontier and pruning identities; fail promotion of price-conditioned learned routing.** Public development, no independent-conjecture or causal claim, no paid compute, no production training admission.

## Exact objective

Inherit CFH-09's bundled acquisition/observation actions and two-query horizon. Route grammar depth 1 (28 routes) and depth 2 (90 routes). Base acquisition caps 4,12. For a uniform hidden route on a deck, J_lambda = P(singleton) - lambda E[distinct base acquisitions]. Observation count is bounded rather than priced; the logical base acquisitions have equal unit price in this model, not equal physical cost. Prices lambda = p/400 for integer p in (0,1,2,4,8,16). Include explicit stop/abstain. On state (S,B,c,h), price p, with action acquiring k additional groups and producing exact children S_v, use integer total value:
```
V(singleton)=400
V(non-singleton,h=0)=0
Q(a)=-p*|S|*k + sum_v V(S_v,B',c-k,h-1)
V(S,B,c,h)=max(0,max_affordable_a Q(a)).
```
Singleton termination uses no extra charge; stop at a nonsingleton gives zero future value. The DP sees exact unpaid partitions and is a privileged offline ceiling. Online arms see only sparse identities and acquired coefficients. The actual acquisition enumerator bypasses the upstream coefficient cache and cross-checks each distinct purchased vector against the independent direct enumerator. Experiment-level shared cache retains vectors across exhaustive replay branches; current episode purchase masks govern access and charge. All selected partitions are compared with independent environment truth. Costs exclude hypothesis table preparation, symbolic tests, action scans, bound computation, training and replay. No end-to-end runtime or equal total compute claim.

For fixed finite policy set, the maximum over affine functions J_lambda is convex, continuous, piecewise linear and nonincreasing on nonnegative prices. Comparing optimality at two prices lambda1<lambda2 gives (lambda2-lambda1)(C1-C2)>=0, so optimal expected acquisition cost is nonincreasing. For nonnegative prices, hit probability also cannot increase as price rises (using optimality at the smaller price and C1>=C2). For a fully partitioning decision tree, integer local regret V-Q telescopes to the difference between the optimal root utility and attained utility, including explicit stop. Audit discrete convexity using integer cross-products; no floating tolerance.

## Data and training

Eight train decks and eight evaluation decks, three cards per deck, order 7–8. Training graph generators Erdos–Renyi, Prufer trees, random bipartite; evaluation Watts–Strogatz, preferential attachment, geometric. Forty-eight distinct new (order, four-round WL hash) keys, excluding 105 distinct keys from CFH-07 candidate, CFH-08 evaluation and CFH-09 train/evaluation manifests. Earlier CFH graph sets not exhaustively excluded. All related graph grammar public development; no independent conjecture test. Seeds and graph edges in receipt.

For each train deck/depth/cap, use the initial state and up to 16 sampled non-singleton child states of affordable first actions. 544 sampled state records, expanded across six prices to 3,264 examples (170,316 exact planner state-action scans for label generation). Per-action 28 features (CFH-09's 26, price and stop flag). Nine CPU width-32 two-layer tanh models, 2,017 parameters, three matched initialization seeds 11,29,47; 160 AdamW steps, batch 48 sampled with replacement, lr .003, decay .001. Blind rank trains on the zero-price slice only and receives price zero even at nonzero evaluation price. Priced ties uses uniform optimal-action targets for all six prices. Priced rank uses softmax of relative utility (Q-max Q)/max(1,max Q-min Q), temperature .2. Blind rank uses the same relative objective at price zero. Identical model sizes/updates; training example pools and sampled prefixes differ between blind and price-conditioned arms, so no clean causal price-feature claim. The priced objectives share training examples. No checkpoint selection. Four deterministic policies: privileged exact; exact free-query lookahead using only purchased or symbolically known predictions; CFH-09 greedy; priced greedy subtracting lambda times immediate cost from its primary heuristic, with exact free fallback when its heuristic score is nonpositive. The latter is a heuristic and does not guarantee nonnegative net utility.

## Results (720 routes per cap/price; neural means across seeds)

Cap 12 exact frontier:

| lambda | hits | mean base calls | J |
|---:|---:|---:|---:|
|0|117|8.53889|.162500|
|.0025|116|7.64444|.141999|
|.005|116|7.64444|.122889|
|.01|94|3.78333|.092722|
|.02|81|2.33472|.065806|
|.04|38|.68333|.025444|

Cap 12 mean utility:

| lambda | exact | free | greedy | priced greedy | blind rank | priced ties | priced rank |
|---:|---:|---:|---:|---:|---:|---:|---:|
|0|.16250|.01806|.08889|.08889|.10185|.07639|.01250|
|.0025|.14200|.01806|.06993|.06861|.07715|.06919|.00694|
|.005|.12289|.01806|.05097|.06361|.05245|.06245|.00139|
|.01|.09272|.01806|.01306|.05361|.00305|.04897|-.00954|
|.02|.06581|.01806|-.06278|.03361|-.09576|.02201|-.03157|
|.04|.02544|.01806|-.21444|-.00639|-.29337|-.02998|-.04491|

At cap 4, exact hits are 78,78,78,76,72,30 across the six prices and mean calls fall from 3.10556 to .41667. Full per-seed, both-cap results in receipt. At cap 12, priced ties typically buys 2.70 calls vs blind rank 9.88; still trails priced greedy at .005,.01,.02 and has negative utility at .04. At .04 the free planner gets 13 hits with no purchases and beats every learned and tested heuristic policy. Priced rank produces only 9–10.33 mean hits at cap 12. The price-conditioned learning objective fails promotion. Do not infer the mechanism of failure from descriptive performance. Price blind does well at the lowest two prices and suffers as the price increases. No total-cost-efficient learned superiority established.

## Exploratory admissible pruning

After the main run, compare two nonlearned controls on the same decks. Let k_v be the known counts of a query's possible residue cells, u the unknown count, and r=h-1. A child of size m can yield at most L_r(m)=m if m<=5^r and 5^r-1 otherwise: the decision tree has at most 5^r leaves and an unresolved leaf is required when more hypotheses remain than there are leaves. For empty child this is zero. For r=0, this gives exactly the singleton indicator. Define
```
U(a) = 400 * max_{z_v>=0, sum z_v=u} sum_v L_r(k_v+z_v) - p*|S|*k
```
where k is the additional acquisition count. This relaxes the unknown replies independently across cells and ignores all future nonnegative costs, so upper-bounds the optimal continuation Q. Compute by cached integer allocation DP. If U is no larger than the feasible exact free-plan incumbent, exclude that paid action without sacrificing a strictly better option. The online policies do not read the true unknown counts; the offline audit independently checks Q<=U for every visited paid candidate. Guarded greedy ranks surviving paid probes by price-adjusted heuristic; bound optimistic ranks by U first. Free plan is fallback; neither policy guarantees its selected paid actions improve on the incumbent because a surviving upper bound is not a lower bound. This is a safe pruning rule, not a guarantee of heuristic profitability.

23,496 paid action bounds checked; 15,724 (66.92%) pruned, all checked sound. At cap 12, bound optimistic hits/cost/utility are 73/7.6333/.10139 at zero price and 58/4.7542/.06867 at .0025. At .01 it gets .03301 vs guarded greedy .05361; at .04 both are negative and lose to the free plan. Bound computation overhead not priced. Retain pruning lemma and exact free incumbent, reject heuristic promotion. An admissible upper bound does not certify positive value of a purchase. A future test should compare explicit robust lower-bound acquisition rules and exact free lookahead, or a learned predictor with calibrated abstention, on fresh families before more neural spend.

## Verification and reproduction

Main run 112,320 outcomes, 5,855 tree decisions; extra run 17,280 outcomes, 968 tree decisions. Across both, 1,440 policy/deck/cap/price/seed groups passed integer utility-regret equality and both budget checks; 16 exact deck/cap frontiers passed monotonicity and convexity. Main evaluation 54,810 symbolic route/residue checks and 295 distinct purchased base vector enumerations, cross-checked. Counts are correlated repeated cases, not independent roots. No sealed confirmation or mechanistic preflight with invented shams.

From gyms/CFH10:
```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python cost_frontier.py --prior /path/to/cfh07_candidates.json.gz /path/to/cfh08_receipt.json.gz /path/to/cfh09_receipt.json.gz --out receipt.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python bound_control.py receipt.json --out bounds.json
python check_frontier.py receipt.json bounds.json
```
Python 3.13, Torch CPU, NumPy, NetworkX, inherited CFH-04..09 dependencies. No weights or raw receipts committed. Exact hashes of local artifacts:
- cost_frontier.py SHA-256 7b5bc63da633247271846096092f400891ec915ec093fe10c46dca6caa897450
- bound_control.py SHA-256 774b96ae10a14de8aa636022d6a7c4c930031336eff54fe364b9fc1c7f7c2ed8
- check_frontier.py SHA-256 311e19e592e57a1ad6fbcc58f7b486749c1c0692645eba585025b803fd3c74a2
- receipt.json SHA-256 71fb61550f21039eed22ca71f2d2e900272920bacabe59e9cde83a639d606345
- bounds.json SHA-256 a92865f95eef431955b4f5c4dd3a3f8d5491ab0f0dc5b33cd97900d0dd5697
- gzip receipts SHA-256 3bffd6f833ef5bbedd33ea1c12728f21d6c0966bca0a41b450e437db6d89511a and 137eb65ec33ac57b8aee777ea5f9d4197c42ff5715f032329bf6943ef6abd3bd.
No Lean verification of new pruning bound or priced regret identity; previous CFH-07 abstract soundness lemmas remain separately verified. Full repository CI pending. No corpus admission or quota changes.
