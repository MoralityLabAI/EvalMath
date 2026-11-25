# MIT-09–11: certified precision, decision certificates, depth–precision frontier

2026-11-25. Evidence: exact rational finite synthetic development roots (open; no sealed split), Lean supporting lemmas, regression tests and a central receipt (`output/evaluation_instrument_transfer/mit09_v0_1.json`, registered as `mit09` in `scripts/check_receipts.py`). Wall-clock numbers come from one shared Windows CPU and are diagnostics only. Theory: `paper/certified_instrument_transfer.md`.

## MIT-09 certified adaptive precision (`certified_precision.py`, 96 roots)

Levels 1, 2, 4, 8, 16 bits and full precision per instrument; largest-remainder rounding normalizes exactly. Cost: 8 units per acquisition plus one unit per entry-bit fetched (full precision charged as 64 bits). Controllers see only quantized columns; refinement benefit is predicted without reading unacquired columns. Three families (random, margin near-ties, slack with noisy irrelevant instruments), 32 roots each, η ∈ {1/100, 1/20, 1/5}.

* Soundness: over 15,696 root × profile cells, actual regret ≤ retrospective global bound ≤ a priori global bound, and actual regret ≤ decision certificate, in every cell. No certified controller exceeded η in any root.
* Tightness: mean actual regret 0.0035; a priori global bound 0.564; retrospective (needs ground truth) 0.218; decision certificate 0.514. The decision certificate is strictly below the global bound in 4,612 cells and zero in 1,017.
* Price of certification: the hindsight oracle (cheapest profile with actual regret ≤ η, uncertifiable) costs 15–37% of the certified oracle.
* Decision versus global certificate (Bellman oracle, mean cost): slack η=1/100 271 vs 389; random η=1/100 264 vs 323; margin family equal at η=1/20 (336 vs 336). The Bellman recursion equals exhaustive profile enumeration on every root and η.
* Controllers (η=1/20, mean cost; oracle with decision certificate = 212 random, 336 margin, 245 slack): uniform+decision 276 / 384 / 298; online certify-as-you-go 299 / 384 / 585; greedy error reduction (global) 620 / 1072 / 614; cost-normalized (decision) 584 / 1072 / 593; decision-margin order 485 / 1072 / 593. Myopic orders lose to uniform: the global certificate is a minimum over feasible query subsets, so single-instrument steps often show zero predicted gain and stepwise acquisitions add fixed charges. The online controller pays only on realized paths and matches uniform except on the slack family, where it refines the decisive instrument to full precision early.

## MIT-10 decision-sensitive certification (`decision_certificates.py`)

* Sound stepwise certificate: robust dominance with MIT-08 radii at every history, posterior drift bounded by the exact box formula (equal to the vertex maximum, tested exhaustively), combined by path and mass bounds and capped by the global 2D bound. 0 violations in 2,208 random-family and 15,060 tie-prone cells.
* Unsafe rules have exact counterexamples. Tie-prone scan: plugin (drift ignored) 1, local (immediate instrument error only) 2, rootonly 1 violation. Constructed drift witness (4 strategies, one 4-outcome instrument, radius 3/50, budget 2): plugin, local and rootonly all claim 0; true regret 1/40; sound certificate 517/7000.
* Equal scalar accuracy, different decisions: on one 6-strategy root, two approximations that move every one of 12 columns by exactly 1/16 in TV deploy policies with regrets 0, 1/96, 1/48 or 1/32 depending on the sign pattern (exhaustive over 4,096 patterns).
* Drift propagation: the sound posterior bound grows with depth along deployed policies (8 bits: mean 0.0038 at depth 1, 0.0057 at depth 2).

## MIT-11 depth–precision frontier (`depth_precision.py`, 36 roots, 96 configurations each)

Planner on dynamic signature quotient groups, depth 1/2/3/exact, uniform bits, class caps none/6/3 (approximate merging charged exactly), quotient on/off. Certified regret = search gap (information-relaxation upper bound minus achieved model value) + 2D.

* Certified frontier: low precision never appears beyond the cheapest point, because D dominates; high precision with depth 1 is the cheap frontier; depth 2 lowers certified regret modestly at about 7× time; certified regret reaches 0 only with exact search at full precision (16 bits: 0.0001 in the structured family).
* Actual-regret frontier: 2-bit depth-1 is on it (palette 0.0075 regret at 64 ms vs 0 at 800 ms for full precision depth 2). Precision buys certificates much more than it buys decisions.
* Quotient compression: mean planner states 1,021 vs 1,212 (palette), 1,481 vs 1,505 (structured), 355 vs 358 (random). Under matched state budgets the chosen (bits, depth) allocation changes only at the tightest budget in the palette family (100 states: 4-bit depth 1 becomes feasible with the quotient).
* Approximate merging (caps 6, 3) appears only at the cheapest end of the actual-regret frontier; its certificates are near 1.
* Witnesses: 46 roots × bit steps where one more bit changes the root action and lowers regret (receipt seed palette 940001: 5→6 bits, root action q0→q3, regret 671/451632→0); regret is not monotone in bits (same root: 1 bit 479/225816, 2–4 bits 1199/150544). Three roots have zero regret at every precision (no decision value), while their certificates keep improving.

## Reproduce

```
cd gyms/MathematicalInstrumentTransfer
python certified_precision.py --output results/mit09 --roots 32 --workers 6
python decision_certificates.py --output results/mit10 --roots 16
python depth_precision.py --output results/mit11 --roots 12 --workers 6
cd ../.. && python scripts/check_receipts.py --only mit09
PYTHONPATH=src python -m pytest -q tests/test_certified_precision.py
```
