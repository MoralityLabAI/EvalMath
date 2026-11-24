# ACD-01A: auxiliary construction costs and feedback provenance

Date: 2026-11-25. Status: exploratory finite synthetic mechanism; no neural or Lean result.

## Motivation

The motivating comparison is between OpenAI's October 2026 manuscripts on local
smoothing for the Euclidean wave equation and the Quasi-Riemann Hypothesis.
The hypothesis is that constructing a richer intermediate mathematical object
can reduce subsequent proof work. The upstream mathematical claims are cited
as motivation only; this pilot does not audit or generalize their proofs.

EvalMath studies exact evaluation channels. Accordingly this pilot runs no
model, and separates the deterministic cost accounting of an auxiliary object
from the future empirical question of learning how to discover one.

## Finite experiment

For dimensions 6 and 8, construct four seeded row sets at each rank
d/2, d-1, and d. Each world has d+3 rows, with dependent rows added to a
rank-preserving random generator. All 2^d targets are independently checked
against the exhaustive span closure, giving 24 worlds and 3,840 world-target
pairs (1,824 nonmembers). The target order is a deterministic shuffle using a
separate seed. The construction uses only the row set.

A member certificate is a bit mask of original rows whose XOR equals the
target. A nonmember certificate is a separating functional y such that every
original row has dot product zero with y and the target has dot product one.
Both are checked against original rows. An auxiliary basis also has a
provenance mask per pivot; its audit checks echelon shape, membership of each
basis row in the original span, and membership of every original row in the
basis span. These conditions imply equal spans. The exhaustive oracle uses
iterative set closure rather than elimination and is outside the policy budget.
All 72 deliberately malformed certificate/basis controls are rejected.

One work unit is one declared bit probe, bitset XOR, dot-product parity,
indexed read/write, or explicit check. Loop control, memory allocation, and
offline oracle work are excluded. These are abstract operation counts; neither
wall-clock speed nor real model inference costs have been measured.

Compare fresh elimination for each query, cached elimination, cached
elimination with a one-time full basis audit, and a deliberately uncharged
oracle basis (diagnostic only). Every arm includes per-query certificate
generation and checking. A budget-limited arm processes a prefix of the
same target order; a query counts only when its entire certificate has been
checked. Each cap is the requested stream length times 64, 128, or 256 units.
The uncapped comparison is paired within each world.

## Exact accounting identity

For build cost B>0, basis audit cost A>=0, and nonnegative certified query
costs q_i, the frozen policies give

    W_fresh(n) = n B + sum_i q_i
    W_cached(n) = B + sum_i q_i
    W_audited(n) = B + A + sum_i q_i

Consequently an audited cache strictly wins iff (n-1)B>A.
The first integer n with a strict win is 2+floor(A/B).
This identity holds for the stated policies, regardless of target order. It is
not a lower bound on general proof search or a theorem about learned reasoning.
A direct solver with caching is an equivalent strong baseline. A solver which
stops elimination early, or uses another representation, may be cheaper.

## Frozen finite receipt

| Stream length | Fresh | Cached | Audited cache | Free oracle |
|---:|---:|---:|---:|---:|
| 1 | 3989 | 3989 | 10233 | 1028 |
| 2 | 8028 | 5067 | 11311 | 2106 |
| 4 | 16138 | 7255 | 13499 | 4294 |
| 8 | 32159 | 11432 | 17676 | 8471 |
| 16 | 64511 | 20096 | 26340 | 17135 |
| 32 | 129232 | 37441 | 43685 | 34480 |
| 64 | 258564 | 72021 | 78265 | 69060 |

The strict break-even point ranges from 3 to 4 queries across worlds. At
32 requested queries per world and 64 units per query, fresh closes 294/768,
cached 768/768 and audited cache 746/768. These are finite descriptive results.
Queries within a world are correlated, and cannot be treated as independent
experimental replicates. The supplied basis diagnostic omits the build and
audit costs, which would overstate the one-query dividend.

## EvalMath-specific issue: an auxiliary construction is a feedback channel

Validity of an auxiliary object does not imply independence from the hidden
answer. For example, take the span of e1 and e2 in F_2^3. On a uniformly
sampled target, membership is a fair bit. An evaluator can send the ordered
basis (e1,e2) for a member and (e2,e1) for a nonmember. Both are valid bases
and both span precisely the same space. Their order reveals the membership
bit exactly, so the mutual information between the order and membership is
one bit. This is an exact two-symbol example; it does not assert that any
upstream paper or model uses such leakage.

For a prospective holdout, freeze the auxiliary generation policy and log
its input and output before sampling hidden targets. A construction computed
from public rows and independent randomness has zero conditional mutual
information with the hidden target given those rows, under the declared
sampling model. If the auxiliary object is intended to depend on the target,
charge its discovery budget and separately audit any external feedback, rather
than claiming it has target-independent preprocessing.

## ACD-01B registration proposal (original design)

The exploratory follow-up is now available in [Auxiliary selection under family shift](auxiliary_selection_family_shift.md). It tests a common reachability representation across three settings, with a calibrated symbolic selector rather than a trained model; the stronger specialized-construction and neural tests remain prospective.

Move from supplied elimination to a library of candidate constructions and
freeze the selector before evaluation. Use graph reachability (path/cut),
GF(2) span membership (coefficient/separator), and finite recurrence invariants.
Hold out whole generator families. Compare a strong symbolic adaptive cache,
matched-budget direct search, a random valid construction, supplied construction
with its full costs charged, and a learned selector. Include one-shot and
repeated-query streams, construction failures, and certificate cost in every
arm. Require a positive equal-budget paired effect across independent worlds
against the strong symbolic cache before claiming learned discovery. Record
work in each operation category as well as actual time and memory, with
preregistered weights and uncertainty at the world level. Keep any model
training in the companion gym; EvalMath retains the exact audit and receipts.

The initial 480-task Lean design remains prospective. The present GF(2) result
establishes accounting and verification behavior in a deliberately simple
family; it does not establish discovery or cross-family generalization.

## Reproduce

From repository root with Node.js 18+:

    node scripts/verify_acd_01a.mjs --check

The verifier regenerates all worlds, exhausts their targets, tests malformed
certificates, and compares the source-hashed receipt at
output/evaluation_acd/acd_01a.json. The core function was executed in a V8
isolate when the initial receipt was produced; the repository Node CLI and
existing full CI suite have not yet been run locally. No new Python package
or Lean dependency is required. This standalone pilot is not yet wired into
scripts/check_receipts.py.
