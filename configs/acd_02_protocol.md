# ACD-02: headroom-gated bidirectional auxiliary discovery

Frozen before the ACD-02 execution. ACD-01A/B/C established certificate
accounting and negligible headroom in a family-aware static dispatch.
This is a deliberately narrower follow-up on directed reachability, where
forward and reverse proof indices are distinct valid constructions and
the better direction changes with the query stream. It is not a general
mathematical reasoning benchmark.

## Workload and splits

Four public cache/topology strata: sparse and dense directed graphs,
with at most 2 or 8 cached search roots. Graph sizes 32 and 64. Each
stratum contains five hidden query regimes: source-hot, target-hot,
uniform, source-to-target shift, target-to-source shift. Streams have
32 queries. Source and target hotspots are independently sampled.
Calibration uses 8 seeds per stratum/regime; test uses 12 disjoint
seeds per stratum/regime with a shifted graph generator, for 160 and
240 worlds. Stream seeds differ from graph seeds. The public inputs
are graph, cache cap, current source/target, and past observed queries.
No regime tag, future queries, reference answers, or test labels
are passed to a policy. The graph size, stratum and cap are public;
a stratum-specific calibration rule may use sparse/dense topology tag.

Forward search retains a BFS frontier rooted at the source. Reverse
search retains a BFS frontier rooted at the target in the transposed
graph; the transpose build is charged once when first used. Either
returns an original-graph path or a forward-closed set containing the
source and excluding the target. Both check certificates against the
original adjacency. For a reverse negative answer, complement the
exhausted ancestor set before checking original closure. A shared
LRU cap covers both orientations. No uncharged cache reuse across arms.

## Fixed policy library

F, R: always forward/reverse with bounded reuse.
Fresh: forward, discard frontier after each query.
H: use cached current source/target root if one exists; otherwise use
the direction with the greater observed endpoint frequency, ties F.
H2, H4: same rule, with reverse requiring at least 2 or 4 occurrences
of the current target when no cache exists; if both roots exist,
use the root with greater observed endpoint frequency.
PF4, PR4, PF8, PR8: start F or R for 4 or 8 queries, then choose
orientation by the number of distinct sources vs targets in that
prefix; ties F. Retain cache entries across the choice. Reuse H's
frequency tracking is charged; prefix policies charge their history
tracking even when it does not change a decision. All adaptive rules
charge lookup/update/decision work.

Calibrated selector: choose one complete policy per public stratum
from the fixed library by lowest total calibration work. Strong fixed
symbolic baseline H; also choose the best single F/R/Fresh policy
per stratum from calibration. H2/H4 and prefix rules are alternative
symbolic controls, not learned networks. Use no test tuning.

## Screen, gate, and outputs

For each stratum, compute calibration per-world hindsight cost minimum
over the full fixed library, relative to H. Require >=20% relative
headroom to pass ACD-02A. Report all strata, even failures. The
same prospective suite evaluates all four strata on test as a
diagnostic even if the calibration screen fails; only screened
strata could be considered for a later confirmatory model experiment.
Compute a hindsight bound using the best single library policy per
public stratum, which is strictly constrained compared with worldwise
hindsight. It is a descriptive bound for stratum-only decisions and
does not bound dynamic policies that observe more history.

Primary closure: per-world budget 32 * 256 declared work units;
secondary 32 * 128 and 32 * 512. Compute verified prefix closure
retrospectively, without live cancellation. Also report total work,
paired wins/losses, worst excess, and exact oracle regret. ACD-02B gate:
on the screened strata combined, calibrated selection strictly beats
H at primary closure, with <= H work. ACD-02C checks robustness at
secondary budgets, per hidden regime and across independent world
seeds, and computes cost headroom after an explicit per-query
selector overhead of 1, 8, 32 work units. No GPU/model run unless
both prior gates pass and a future sealed workload is registered.
No model training is part of this repository.

Work unit is one declared read, write, edge/bitset operation, or
check, each weight 1; all arms include original-proof verification.
Offline oracle/calibration work, routine control overhead and actual
memory size/wall time are excluded. The LRU cap is on root entries,
not bytes; transpose is extra memory. Each world is an independent
descriptive unit, not individual queries. The independent oracle is
all-pairs transitive closure using a separate algorithm. Check all
world-target pairs against both directions in a separate census;
reject malformed path/cut controls. No claim about arbitrary
algorithms or learned reasoning follows from this finite experiment.
