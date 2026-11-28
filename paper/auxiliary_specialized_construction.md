# ACD-01C: specialized construction under uncertain stream length

2026-11-25 | Evidence: finite synthetic algorithm selection pilot

The [protocol](../configs/acd_01c_protocol.md) was committed at f3c2e06
before the simulation. This is the follow-up to
[ACD-01B](auxiliary_selection_family_shift.md). No neural model, Lean
kernel or GPU is involved.

## Specialized certificates

Directed graphs: Kosaraju strongly connected components, condensation
DAG reach masks, and pruned BFS path extraction. Negative certificates
are the set of all vertices in reachable components, checked for
closure in the original graph.

GF(2): coefficient-carrying elimination with original-row combination
masks. A positive affine query s -> t uses a combination proving
s XOR t is in the span; a negative one uses a dual functional
annihilating every original row but not s XOR t. The basis is shared
across source states.

Affine recurrences: functional graph cycle and preperiod orbit masks.
Cycle vertices share the cycle mask and preperiod vertices inherit the
successor's mask plus themselves. Positive certificates are original
transition paths; negative certificates are closed original-state sets.

The independent oracles are Floyd-Warshall closure, exhaustive span
closure, and bounded orbit enumeration respectively. Exhaustive census:
162 worlds, 72,576 source-target pairs (42,483 negative), each checked
with both lazy and specialized certificates, giving 145,152 successful
checks. All 594 malformed controls are rejected. All simulated stream
answers also pass the original-problem verifier and oracle.

The 54 calibration and 108 test worlds use distinct generators/seeds.
A stream has a hidden length in {1,4,16,32}, with varying source
locality. Solvers see queries sequentially, without the horizon.
The abstract work metric charges selected indexed reads, writes,
bitset/transition operations and checks at unit weight. Offline oracle
and calibration work, routine control overhead and actual memory
allocation are excluded. Dispatch by known family is free; the
online policy pays one check per revealed query. Switching charges
all previously expended lazy work plus the new index build.
Budget closure is retrospective prefix censoring, not live stopping.
This experiment does not implement memory caps or measure wall time.

## Results

Held-out 108 worlds, 1,416 requested queries. Work and verified prefix
closure under 32, 128, and 512 units per requested query:

| Policy | Work | 32 | 128 | 512 |
|---|---:|---:|---:|---:|
| Fresh | 137843 | 611 | 1297 | 1416 |
| Lazy | 98626 | 908 | 1317 | 1416 |
| Eager | 118304 | 719 | 1297 | 1405 |
| Family dispatch | 65805 | 1110 | 1378 | 1416 |
| Online threshold | 67221 | 1099 | 1378 | 1416 |

Calibration chooses lazy for graphs and recurrences, eager for GF(2).
The threshold library {0,1,2,4,8,infinity} chooses infinity,0,infinity
respectively. Consequently the online arm performs exactly the static
dispatch algorithms with one extra check per query. It loses all 108
paired work comparisons by its stream length, and the registered gate
fails. This says nothing about general learned or adaptive controllers:
the tested online class is restricted to family-dependent fixed
thresholds and does not inspect structure or realized costs to decide
when to switch.

By family, dispatch costs 30,132 (graphs), 15,293 (GF(2)), 20,380
(recurrences). The corresponding primary closures are 411/449,
462/462 and 505/505. GF(2) is the specialized construction success:
eager elimination costs 15,293 versus lazy's 48,114 units; closure
462 versus 401. Graph and recurrence eager indexing costs more on
these workload mixtures.

## Headroom preflight (post hoc diagnostic)

On each held-out world choose the lowest-work arm among fresh, lazy,
and eager with hindsight. Their summed cost is 65,460 (versus 65,805
for family dispatch); the entire available improvement for a selector
of those three algorithms before charging selector work is only 345
units, about 0.524 percent of the dispatch cost. The best hindsight
fixed threshold sum with its decision charges is 66,971. Separately,
choosing the best of fresh/lazy/eager for primary closure on each world
gives 1,378, exactly dispatch's closure. These numbers were computed
from the saved receipt after observing the pilot; they are not
preregistered outcomes.

For a finite set of candidate policies P and a fixed finite test world
set, define H = sum_i (C_baseline,i - min_{p in P} C_p,i).
Any per-world selector restricted to P incurs at least the sum of
those minima, before selector overhead. Its savings are at most H.
For a nonnegative selector cost S, the net savings are at most H-S.
The same argument with maxima gives a closure headroom bound.
These identities concern a frozen finite policy library, not all
possible algorithms or an online controller inventing new policies.

The small headroom explains why this workload is a poor training
target. A more useful prospective test needs heterogeneous instances
within each known family where different valid representations win,
plus a verified oracle gap large enough to pay for policy inference.
Use memory-constrained caching, mixed locality, parameterized matrix
rank/sparsity and graph SCC structure, and recurrence families with
varying orbit lengths. First screen on independent calibration
worlds for headroom, and freeze the resulting generator before drawing
new sealed test seeds. Do not reuse this public test receipt for a
confirmatory neural claim.

## Reproduce

    node scripts/verify_acd_01c.mjs --check

The V8 core executed successfully and generated
output/evaluation_acd/acd_01c.json (162 world records, operation
categories, complete policy costs and closures). Recomputed remote
function fingerprint 71bab5c8 matched the receipt; it is FNV-1a,
not a cryptographic source hash. Git blobs:
source 37c3fc3fe2a3f1801e6e339b560ac87055d3d2dc,
receipt 2d4084e6c87e09bab75e9691baa5dd161b51e098.
No combined status checks were returned for receipt commit 8837cb4.
The Node wrapper/full CI have not been independently executed.
