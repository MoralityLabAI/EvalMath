# ACD-02: headroom-gated bidirectional representation selection

2026-11-25 | Finite synthetic mechanism evidence

The [frozen protocol](../configs/acd_02_protocol.md) was committed at
8656e09 before running the suite. The experiment narrows ACD-01C to
directed reachability with competing forward and reverse proof indices.
It is a study of bounded auxiliary selection, not a learned proof system.

## Census and workload

400 independent seeded graphs (160 calibration, 240 test) of 32 or 64
vertices, with four density/cache strata and five hidden query regimes:
source-hot, target-hot, uniform, source-to-target shift, target-to-source
shift. Generator shift replaces calibration blocks of size eight with
test blocks of size four plus occasional long chords. Each stream has
32 queries. The LRU cap counts two or eight cached roots across both
orientations. The reverse index is extra memory; it is built only
when first used, and construction work is charged. Real byte usage
and time are not measured.

Both directions give original graph path certificates or forward-closed
sets containing the source and excluding the target. In reverse search a
negative certificate complements the fully explored ancestor set.
Every certificate is independently checked against original edges.
All 1,024,000 world/source/target pairs match the Floyd-Warshall oracle
in both directions (2,048,000 certificate checks); all 1,200 malformed
path/cut controls are rejected. All policy-stream answers also pass.
All cost categories are fixed-unit abstract counts. Offline calibration
and reference oracle, allocation and routine control overhead are excluded.

Policies F/R use bounded forward/reverse lazy search. Fresh discards
search state each time. H and H2/H4 choose using existing cached roots
and prior endpoint counts. PF4/PR4/PF8/PR8 choose direction from the
first four/eight observed queries after initially using F/R. All
history tracking, cache operations, decision checks, construction,
certificate extraction and verification are charged under the stated
operation convention. No policy receives the hidden regime or future
queries. The selector is a calibrated table over the four known
strata, not a trained model. The offline calibration cost and table
dispatch overhead are not charged in the main arm.

## ACD-02A: headroom screen

The registered calibration criterion was at least 20% improvement
over H by per-world hindsight selection among the ten policies.

| Stratum | H cost | Hindsight cost | Headroom / H | Screen |
|---|---:|---:|---:|---|
| Sparse, cap 2 | 350302 | 284639 | 18.7447% | Fail |
| Sparse, cap 8 | 318573 | 262996 | 17.4456% | Fail |
| Dense, cap 2 | 589457 | 494284 | 16.1459% | Fail |
| Dense, cap 8 | 517375 | 435154 | 15.8920% | Fail |

Calibration selects F in every stratum, for both the full library
and the restricted static library {F,R,Fresh}. Relative to that
stronger fixed baseline, calibration oracle headroom is only 2.74%,
3.28%, 3.63%, and 6.13%. All four strata fail even against H; no
stratum is admitted to model training.

## ACD-02B: held-out diagnostic

240 worlds, 7,680 queries. Matched budget is 32 times the listed
units/query, per world. Closure is a retrospective count of fully
verified prefixes, not live stopping.

| Policy | Work | 128 | 256 (primary) | 512 |
|---|---:|---:|---:|---:|
| Fresh | 2625131 | 3537 | 5964 | 7404 |
| F | 2112153 | 4240 | 6486 | 7584 |
| R | 4267352 | 2181 | 4258 | 6370 |
| H | 2628036 | 3680 | 5885 | 7281 |
| H2 | 2626178 | 3680 | 5886 | 7284 |
| H4 | 2463254 | 3831 | 6063 | 7392 |
| PF4 | 2823665 | 3794 | 5852 | 7258 |
| PR4 | 3160252 | 2671 | 5295 | 7056 |
| PF8 | 2835925 | 3775 | 5823 | 7295 |
| PR8 | 3408956 | 2311 | 4818 | 6848 |
| Calibrated selector | 2112153 | 4240 | 6486 | 7584 |

F beats H in 195/240 worlds, loses in 45, and improves aggregate
primary closure by 601/7680 = 7.8255 percentage points. It is also
the calibration-selected fixed policy, so the gain is a baseline
correction, not evidence of useful algorithm selection. Worst paired
excess vs H is 11,054 units. Registered ACD-02B gate fails because
the admitted stratum set is empty.

## ACD-02C: robustness and observation-aware oracle

Primary closure per hidden query regime (1,536 requested per row):

| Regime | H | F/selector |
|---|---:|---:|
| Source hot | 1362 | 1400 |
| Target hot | 1132 | 1265 |
| Uniform | 1037 | 1197 |
| Source to target | 1278 | 1386 |
| Target to source | 1076 | 1238 |

Worldwise hindsight over the full library costs 1,992,669, leaving
only 119,484 units (5.657%) headroom relative to F. A hindsight
selector restricted to one policy per public stratum costs
2,112,153: the same as F. The gap is an illustration of why
hindsight oracle headroom cannot be interpreted as attainable
savings for an observation-limited policy. A controller that
observes history and changes decisions is outside that stratum-only
bound, though the full-library oracle bounds selectors that choose
one complete library policy per world.

For fixed finite library P, worlds i, observation partition g(i),
baseline cost b_i and policy cost c_ip:

    H_full = sum_i b_i - sum_i min_p c_ip
    H_obs  = sum_i b_i - sum_g min_p sum_{i:g(i)=g} c_ip

Then H_obs <= H_full, because the sum of individual minima
is bounded above by each common policy's group sum. With additional
selector cost S, maximum net saving for the observation-limited
library class is at most H_obs-S. For probabilistic inputs, replace
sums by the corresponding nonnegative weighted sums. These are
algebraic identities/inequalities for fixed costs and observations;
they do not constrain arbitrary new algorithms.

Against F, even worldwise oracle headroom after charging 1, 8 or
32 extra work units per requested query is respectively
111,804, 58,044 and -126,276. The zero-overhead closure oracle over
library policies closes 4,459/6,658/7,601 at the three caps, versus
F's 4,240/6,486/7,584. At the primary cap the maximum possible
library gain is 172/7680 = 2.24 percentage points, before selector
cost. With 8 extra units per query, F itself closes 6,418 at the
primary cap; this is a sensitivity calculation, not a neural run.

## Research disposition

ACD-01A: reusable representations can amortize construction and
audit cost.
ACD-01B: a calibrated selector fails against incremental reuse.
ACD-01C: specialized symbolic dispatch dominates fixed-threshold
online switching; its finite library has 0.524% oracle cost headroom.
ACD-02A/B/C: bounded directional caches under a new workload fail
the 20% headroom gate. The stronger fixed baseline eliminates the
observed selector effect. No GPU or model training is justified
by these particular tasks.

The next *distinct* research question is construction discovery
where the candidate objects are not already in a small fixed library.
A future gym could generate unknown proof invariants or coordinate
changes, verify original statements, and register a fresh workload
with substantial headroom against strong symbolic controls.
Screen this independently before training. Do not tune on the public
test worlds or present the current results as neural generalization.

## Reproduction

    node scripts/verify_acd_02.mjs --check

The V8 core ran to completion. The remote core-function FNV-1a
fingerprint 471bbe0f matches the receipt; Git source blob
658cde37c364125618e3d0654438a5b93648e822, receipt blob
8ed44378e04c418c55b92e4f94cf11c274ad9435.
FNV-1a is only a reproducibility checksum. The receipt retains
400 per-world records, all operation counts, policy costs, calibration
selection, closures and overhead sensitivity. The Node CLI and
full repository CI require independent execution.
