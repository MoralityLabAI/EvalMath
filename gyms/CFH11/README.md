# CFH-11: certified lower bounds on mathematical information purchases

**Disposition:** pass finite soundness and low-price improvement over free planning; hold policy promotion. No neural fits, independent conjecture test, corpus admission, or paid compute. The shared-coefficient refinement was explored after the first run, on the same public decks.

## Interface and certificates

Inherit CFH-09/10 depth-two grammar (90 routes), two observations maximum, acquisition caps 4 and 12, price lambda=p/400 with p in (0,1,2,4,8,16). All hypotheses in the surviving set have equal conditional weight. Values are integer ticks: a resolved hypothesis contributes 400 and each paid base group contributes -p per hidden hypothesis that incurs the purchase. For first query a with known disjoint reply cells K_v and unknown set U, let k_v=|K_v|, u=|U|. Adversarially allocate the unknowns among residues. The immediate guaranteed singleton count is min over z_v>=0, sum z_v=u, of sum_v 1[k_v+z_v=1]. Min-plus dynamic programming over the residue bins computes this exactly. No assumptions on independence of actual unknown replies are necessary for the lower bound.

For a two-query bound, let B'=B union need(S,a) be the acquisition set after query a. For each possible first reply v, consider a second query q that is fully predictable on K_v union U with B'. This is free for any actual child of that reply after the purchase. Before purchase, within K_v count the known q-reply bins of size one, and subtract the number of K_v hypotheses with unknown q predictions. Maximize this lower bound over such q and zero; call it G_v. Adding z_v unknown-first-reply hypotheses can spoil at most z_v more singleton bins. Hence a guaranteed child count is max(1[k_v+z_v=1], G_v-z_v, 0), using immediate termination or an appropriate free continuation. Minimize the sum over all allocations and take the maximum with the immediate bound. Subtract immediate purchase cost p*|S|*k from 400 times the guaranteed count, where k is the number of newly bought groups. All these bounds use only purchased or symbolically known residues and known acquisition requirements.

At each decision the certified planner starts from an exact feasible free-only plan. It buys a query only if the certified lower value strictly exceeds that incumbent. The adaptive variant also considers every fully known first split followed by certified child decisions. By induction on the remaining horizon, the executed policy achieves at least its certified value: a paid first action can always follow the guaranteed free continuation, and recursively applying the same safe choice never reduces that continuation value. Guarantees are for aggregate conditional utility under the uniform route distribution in the exact bundled-action model, not individual route success, physical CPU time, or general conjecture discovery. Zero-price ties retain the incumbent.

## Shared-coefficient refinement (exploratory)

For a fixed query on graph card c, each unknown derived coefficient residue in a common base group is an affine linear expression in the group's missing base coefficient residues mod q, q in {2,3,5}. Compute all response vectors by iteratively adding the images of each missing coordinate; take their residue histograms and convolve the histograms across groups. The actual unknown reply histogram belongs to the resulting set because the true missing coefficients constitute a valid assignment. Treating groups independently and ignoring constraints between unknown base coefficients may enlarge this set, which preserves lower-bound soundness. Minimizing the original child-profile objective over this smaller feasible histogram set is at least as strong as minimizing over arbitrary allocations. If an intermediate vector or histogram set exceeds 8192 entries, discard the refinement and use the independent bound. This is a set-size limit, not an end-to-end work or memory cap. No learned predictions.

The refinement preserves shared linear constraints for the first observation; it does not jointly solve all second-query coefficient constraints. Its post hoc same-deck scores are development evidence. All visited coupled candidate bounds, including unchosen candidates, are checked after replay against actual first splits and their exact feasible free continuations, using the privileged independently constructed oracle. For every retained histogram set verify containment of the actual histogram. The policy itself never reads this oracle information in its choice.

## Data and results

Eight newly generated public decks, three graphs each, orders 8–9, random graphs, Prufer trees, geometric graphs. Deduplicate (order, four-round WL hash) against 153 keys from CFH-07/08/09/10 manifests and newly generated cards; other prior sets not exhaustively excluded. The initial 7–8 order generator exhausted its bounded retries on the prior exclusions before evaluation; order was raised to 8–9. These are related graph-grammar roots, not independent conjectures. Six arms in the primary run: privileged exact, exact free-only, priced greedy, immediate certified, two-query certified, and adaptive free-first certified. Eight decks * 90 routes * two caps * six prices * six arms = 51,840 outcome rows. Coupled same-deck extension adds 8,640 rows. All 672 deck/cap/price/arm groups obey the budgets and exact utility/regret identity. All 1,395 small allocation comparisons against direct enumeration passed.

Cap 12 results. Hits out of 720, mean logical base purchases in parentheses:

| lambda | Exact | Free | Priced greedy | Pair/adaptive certified | Coupled certified |
|---:|---:|---:|---:|---:|---:|
|0|125 (9.1333)|15 (0)|75 (6.5)|30 (.5111)|60 (1.5208)|
|.0025|124 (8.5)|15 (0)|67 (2.75)|30 (.5111)|60 (1.5208)|
|.005|118 (6.7458)|15 (0)|66 (2)|30 (.5111)|60 (1.5208)|
|.01|94 (2.3403)|15 (0)|66 (2)|15 (0)|36 (.7611)|
|.02|94 (2.3403)|15 (0)|66 (2)|15 (0)|15 (0)|
|.04|91 (2.2014)|15 (0)|66 (2)|15 (0)|15 (0)|

Certified arms have identical aggregate results at caps 4 and 12. Immediate bound never purchases and matches the free planner. At zero price the coupled arm has utility .083333, four times the free baseline .020833 and about 48% of the exact planner's .173611. At .01 coupled utility .042389 exceeds free .020833 but remains below exact .107153 and priced greedy .071667. At .04 both certified variants return to free utility .020833, exceeding priced greedy .011667. This does not establish overall utility superiority over heuristic policies.

The primary pair and adaptive arms each make 18 paid decisions across repeated conditions. Coupled makes 56. Every selected paid decision passes strict improvement over its current free-only incumbent, and each realized policy subtree clears its certified lower bound. Coupled audits: 2323 candidate bounds sound; 2299 retained histogram sets contain the actual histogram; 24 safe fallbacks; 42 bounds strictly improve on their uncoupled values; 1097 bounds are tight; 1171 have zero bound despite a positive actual continuation. The latter is evidence of substantial pessimism. Coupled scans 23,963 actions and 41,499 second-query candidates, in addition to histogram computation and evaluation work. Logical purchase charges exclude all this planning overhead. No claim of end-to-end compute savings, general performance, or Lean formalization. No protected confirmation set, neural training, or promotion.

## Reproduction

From gyms/CFH11 with CFH04..10 dependencies and prior gzip receipts:
```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python certified.py --prior /path/to/cfh07_candidates.json.gz /path/to/cfh08_receipt.json.gz /path/to/cfh09_receipt.json.gz /path/to/cfh10_receipt.json.gz --out receipt.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python coupled.py receipt.json --out coupled.json
```
Python 3.13.5, NetworkX 3.6.1, NumPy 2.3.5, SymPy 1.14.0, Torch CPU inherited imports. Local SHA-256:
- certified.py: dfca31c6095c8ed4706f249e1b72df4aff89f591fa759dc67e6a430e817d0089
- coupled.py: b32f7cc883f6d694a9c9909fc916715acb4dbf07b89012fa47845ee27edb229f
- receipt.json: 659b90776eca4562a1d954ca4bda8d3dbe5bf5ec9428b2da9a4285ba2c4b0f6d
- coupled.json: 5b762b762c23cbc2345892e9aa090d348d96480afd771cb33d9540aaf62a126e
- gzip receipts: fe64f1bdcbaa31030cb26be7bb7577e251fd78715b6e7c80d7474f18d7d1d2e8 and 347824d3f5e6feac45eee646dd743b1c850c1f01f121333d1374d2fbd48c5b60.

Next: reduce pessimism using verified joint first/second response constraints (or separately priced acquisition of coefficients), compare against simpler free-planning and greedy controls under charged planning work, and freeze a new independent-family protocol before fitting any confidence policy. Repository-wide CI pending.
