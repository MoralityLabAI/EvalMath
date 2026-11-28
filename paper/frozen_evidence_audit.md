# FRE-01: preserve the first measured result across schemas and reruns

**Evidence level:** finite verified code examples. The verifier records eight
deterministic checks, using synthetic timing values and synthetic trusted-anchor
fixtures. A separate adversarial test suite exercises malformed records. This
module produces no statistical, neural, or deployment result.

## Research source and scope

The NOR series in
[`MoralityLabAI/Compactification-Theory`](https://github.com/MoralityLabAI/Compactification-Theory)
preserves first CPU receipts and compares exact output parity across optimized
verification paths. NOR-59's signed whole-verifier experiment is archived at
[`2b7b5aef461b9fda3c5dd9aa92793606d3dd58da`](https://github.com/MoralityLabAI/Compactification-Theory/tree/2b7b5aef461b9fda3c5dd9aa92793606d3dd58da/research/nor59_authorized_merkle).
Its narrow component gains and smaller whole-call gains motivate explicit
measurement boundaries. Historical source digests include experiment wrappers;
equal operative inputs can therefore receive different source identities.

FRE-01 adds `spiral_ln.evaluation_frozen_evidence` as an opt-in audit before a
performance result is interpreted. Existing finite-sample tests and receipt
verifiers keep their own contracts. A caller supplies the trusted anchor from an
independently retained register. Trust in that register is an external premise.

## Exact input projections

An adapter places the operative query in `query` and every operative program
parameter in `program`. Outer fields such as experiment schema, domain label,
case name, profile and seed remain outside both projections. A query digest
identifies the query alone. A task digest identifies the ordered pair of query
and program. A change to the operative program produces a new task identity
while retaining the shared query identity.

Canonical exact JSON sorts object keys and preserves list order. Boolean values
retain their JSON type. Floats, non-string keys and custom Python objects are
rejected. The two digest domains are fixed by FRE-01, independently of the
experiment's wrapper schema. Each adapter remains responsible for its semantic
projection. Hash equality does not decide algebraic equivalence, graph
isomorphism, or shared generative ancestry. Domain-specific canonicalization can
be added as a separately reviewed layer.

Each source case carries a `root_id`. Reports count declared roots separately
from cases and timing repetitions. Distinct strings provide no evidence of
statistical independence. Repeated tasks and externally excluded task digests
are rejected. A registered `unique_queries` policy decides whether shared
queries with different programs are allowed.

## Anchor and attempt chain

The independent anchor binds the registration artifact digest, exact source
artifact digest, expected first attempt ID, and first attempt artifact digest.
Its first-attempt digest is captured after that first artifact exists, then
retained through a separate authenticated register or reviewed repository
commit. Registration chronology requires its own prior commitment. Copying an
anchor field into an untrusted receipt supplies no independent trust.

The anchor also fixes the arm names and setup policies, baseline, repeat count,
query-uniqueness rule, prior task exclusions, and session-context policy. The
auditor requires every case/repeat/arm combination exactly once. Paired arms
must carry the same invocation-context digest and exact task digest. Nanosecond
durations are positive integers. Optional nonoverlapping phase durations are
nonnegative integers whose sum cannot exceed the whole-call duration.

Later artifacts must link to the immediately preceding attempt's ID and raw
SHA-256. They carry a reason and the role `diagnostic`. The report retains the
original declared outcome and computes its ratios from the original complete
paired sample. The benchmark-specific gate formula remains with its own
independent grader; FRE-01 does not recompute that declared outcome. A failed original gate remains `fail` when a diagnostic run succeeds.
Deleting the original, changing its bytes, or promoting a later result fails
the anchored audit.

Incomplete runs should be archived with their original errors. They cannot
supply complete paired timing evidence through this API; omitted repeats or
arms fail the performance audit. A corrected protocol or changed source cohort
needs a new external anchor and explicit lineage to the earlier work.

## Cost and inference

Per-source medians use exact integer/rational arithmetic. The summary ratio is
the sum of candidate source medians divided by the sum of baseline source
medians. These are descriptive ratios for the original call boundary. Explicit
`in_call` and `outside_call` setup policies prevent silent warm/cold relabelling.
An adapter must measure the declared boundary honestly and account for setup
separately when deployment pays it.

A component speedup supports a component claim. Whole-call timing includes
authentication, execution and root work when those are part of the declared
call. No confidence interval or significance claim is produced here. Prospective
empirical studies still require the repository's independent-root preflight,
matched controls, and sealed readout rules. FRE-01's deterministic schema tests
do not consume a development or confirmation split.

## Reproduce

```bash
PYTHONPATH=src python -m pytest -q tests/test_evaluation_frozen_evidence.py
PYTHONPATH=src python scripts/verify_evaluation_frozen_evidence.py
python scripts/check_receipts.py --only frozen_evidence
```

The verifier's receipt records every check and the SHA-256 of its module, tests,
verifier and this note. Its source-hash audit proves replay of these fixtures.
Authentication of real anchors and clock measurements remains with the caller.
