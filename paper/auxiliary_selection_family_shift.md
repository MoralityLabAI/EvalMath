# ACD-01B: auxiliary selection under family shift

2026-11-25 | Evidence level: exploratory finite synthetic mechanism

Companion to [ACD-01A](auxiliary_construction_dividend.md). This is a
negative transfer result, not an experiment on a neural model or a Lean
formalization. The motivating OpenAI manuscripts are discussed in ACD-01A.

## Question

Does a calibrated policy for building a reusable auxiliary construction
improve on a symbolic solver retaining its search frontier? The latter is
a necessary control for any future claim of learned mathematical discovery.

## Protocol

Three finite mathematical settings are represented as implicit directed
transition systems: graph reachability, GF(2) span membership via XOR
generators, and orbit membership for x -> a*x+b modulo n. A positive
certificate is a sequence of transition indices leading from the source to
the target. A negative certificate is a closed vertex set containing the
source and excluding the target. Closure is checked against original
transitions, not a cached answer. The independent reference algorithms are
Floyd-Warshall transitive closure, iterative exhaustive span closure, and
a bounded n+1-step orbit census, respectively.

There are 12 calibration and 12 test worlds per setting, at sizes 16, 32
and 64. Separate seeds and generator changes distinguish calibration and
test: clustered random graphs versus cycles with shortcuts; two versus
five additional dependent GF(2) generators; odd versus even affine
multipliers. All 2,688 world-target pairs are checked (1,591 negatives).
All 216 deliberately invalid controls are rejected. The core experiment
was executed in a V8 isolate. No model ran.

For each world, a separate target seed produces a 32-query stream with
replacement. The 1, 4, 16 and 32 query conditions are nested prefixes.
The world is the independent descriptive unit, not the query or prefix.

Five policy arms:
* Direct: fresh early-stopping breadth-first search.
* Memo: fresh search on first encounter, checked certificate cache on repeats.
* Eager: full breadth-first parent tree before answering the first query.
* Audited: eager, with a complete index provenance and closure audit.
* Lazy: preserve the partial parent tree and frontier, expanding only as needed.

All policies generate or retrieve a certificate and check it for every
query. Work counts declared reads, writes, successor evaluations and
explicit checks, each at unit weight. This includes initialization, search,
certificate construction, verification, and the audited arm's full audit.
These abstract weights are exploratory; actual time, memory, bit
complexity and routine control overhead are not measured.

The selector leaves an entire mathematical setting out of calibration.
Given the announced horizon, it chooses the lowest aggregate work policy
on the other two settings' 24 calibration worlds (fixed policy order for
ties). It is frozen before the test targets are consulted. One additional
table lookup is charged per test stream. A random policy chooses uniformly
up to the modulo bias of the seeded generator from the same five choices,
using a separate seed, and pays the same lookup charge. Offline calibration
and independent oracle work are excluded from execution budgets.

Budget is horizon times 64, 256 or 1,024 declared units; count only a prefix
of fully verified answers whose accumulated cost is inside that budget.
All work/cost traces come from complete runs; these prefix counts simulate
budget censoring rather than interrupting a live process. The selector is
optimized for total work on calibration, so equal-budget closure is a
secondary outcome. The design and results were developed in the same
exploratory pass; a prospective confirmatory run remains outstanding.

## Exact finite results

Held-out aggregate work, 36 worlds per horizon:

| Queries | Direct | Memo | Eager | Audited | Lazy | Selector | Random |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 6888 | 6960 | 11866 | 41286 | 6888 | 6924 | 16330 |
| 4 | 25526 | 25176 | 20096 | 49516 | 16228 | 20297 | 26930 |
| 16 | 107818 | 93335 | 56080 | 85500 | 54504 | 56891 | 79489 |
| 32 | 214341 | 166986 | 100984 | 130404 | 100764 | 101020 | 140592 |

At 32 queries with 64 units per requested query, the respective verified
closures are 596, 705, 851, 710, 882, 851 and 746 out of 1,152. All
arms close all 1,152 at 1,024 units/query. The selector loses aggregate
work to lazy at every horizon. At four queries, selector excess work is
4,069 / 16,228 (about 25.1%); the held-out GF(2) fold chooses eager,
incurring 9,300 versus 5,255 work.

At 32 queries the selector chooses eager in every fold and wins on 32/36
worlds, but still consumes 256 more units overall. The family breakdown
(selector minus lazy) is graph -682, GF(2) +1674, recurrence -736.
The sign of a majority-of-worlds effect therefore differs from that of
the summed-work effect in this exact receipt.

## Implication for evaluation design

For matched policy costs c_i and baseline costs b_i on held-out worlds,
define signed excess r_i=c_i-b_i. A success rate based on
sum_i 1[r_i<0] measures frequency of improvement, while sum_i r_i
measures aggregate cost. Neither determines the other. A positive
minority tail can overwhelm many small savings. The concrete ACD-01B
witness has 32 strict improvements and four strict losses, with
sum_i r_i=256. The result illustrates why we should retain paired
costs, characterize tail regret and report cost-censored certified
closure together when evaluating a learned mathematical controller.

Lazy retention exposes the weakness of a fresh-search-only baseline.
Eager and lazy use the same search order and can perform equivalent
expansions; eager can avoid repeated target checks once the full index
is useful, while lazy avoids unnecessary expansions. A majority win for
eager does not establish a better budgeted policy.

## ACD-01C: prospective specialized construction discovery

The three families above share a reachability representation. Thus
family shift here tests portability of a caching heuristic across
generator families, not general mathematical representation discovery.
To test a stronger claim:

- Offer genuinely different candidate constructions: Gaussian
  elimination with coefficient/separator certificates versus implicit
  XOR search; SCC/condensation or reusable source-specific reachability
  versus early BFS; cycle/preperiod decomposition and modular
  arithmetic versus direct recurrence iteration.
- Include multi-source and mixed one-shot/repeated streams, horizon
  uncertainty, and memory caps; charge failed construction attempts
  and policy inference. Strong domain-specific symbolic solvers and
  incremental reuse are required controls.
- Freeze generator families, calibration policy, weighting, budget
  grid, primary equal-budget closure, and acceptable upper-tail
  excess before drawing test seeds. Use independent world-level
  paired uncertainty, with no reuse of these exploratory test worlds.
- A trained TRM/LLM selector may enter only in the companion gym.
  Export its frozen policy and receipts for EvalMath's independent
  certificate/feedback-channel audit. ACD-01B supplies no evidence
  that such a model beats symbolic selection.

## Reproduce

Node.js 18+:

    node scripts/verify_acd_01b.mjs --check

The receipt is output/evaluation_acd/acd_01b.json and retains 288
world/horizon records, operation category totals, budget closure, fold
calibration and the selected policy. The stored FNV-1a fingerprint
4c0feefb is a reproducibility checksum of the core function, not a
cryptographic source hash. The GitHub source blob is
aa5025ef4142c29a04ac025eb7b68fe8704c792c and the receipt blob is
259da1667d200a473283c322d65f81aef6672697. The remote fingerprint was
recomputed and matched the receipt. Full Node CLI reproduction and
repo CI are still outstanding; no integration with the Python receipt
runner or Lean claims registry has been made.
