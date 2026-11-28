# MIC-01: Mathematical Improvement Curriculum

**Status:** development proxy tested; model experiment draft, blocked at preflight. Source: Khanna, Putterman, Song, *A Deterministic Linear Time Algorithm for Minimum Spanning Tree*, 23 November 2026, ECCC TR26-339 (https://eccc.weizmann.ac.il/report/2026/339/). Section 1.4 reports an unsuccessful direct attempt followed by iterative improvements. The public history is one problem family, regardless of how many proof variants exist.

- [source_manifest.json](source_manifest.json): all 18 PDF paths, exact Git blob hashes, pinned commit, reported stage groups, unknown ordering explicitly preserved. No source text or PDF bytes redistributed. Filename-based groupings await proof-level audit.
- [protocol.json](protocol.json): seven model arms, familywise comparisons, strict-improvement criteria and prospective custody gates. No claim of sealed data or model efficacy.
- Code: `src/spiral_ln/mic01.py`. Public development tasks return a matrix, overhead and feasible baseline; `grade(seed, proposal)` independently checks two rational strings. Gold solutions are a structural ceiling and must not enter model prompts.

## Exact mathematical proxy

For two recursive task types, suppose a well-founded computation charges at most b_i n work to a parent of mass n and the total child mass of type j is at most M_ij n. With b positive, M nonnegative and row sums <= 4/5, p >= b + M p implies T_i(n) <= p_i n by induction, provided terminal work is included in b. The scalar baseline p=(K,K), K=max_i b_i/(1-sum_j M_ij), is feasible.

Algebraic identity under these assumptions: p*=(I-M)^(-1)b is the componentwise least feasible nonnegative certificate. The inverse is a nonnegative Neumann series (row-sum norm <1); multiply (I-M)p>=b by that inverse. A coordinate update p_i=(b_i+M_ij p_j)/(1-M_ii) keeps the updated constraint tight, decreases p_i from a feasible starting point and relaxes every other constraint. All arithmetic uses Fraction. This is a proxy for shrinking-work accounting, not the MST certificate construction or a proof of the published theorem.

## Development replay

```sh
PYTHONPATH=src pytest -q tests/test_mic01.py
PYTHONPATH=src python -m spiral_ln.mic01 > /tmp/mic01-dev.json
python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot /tmp/mic01-dev.json --strict
```

Local standalone sandbox replay: four test functions passed; 128 generated roots checked against exact solution, all six permutations of two updates to each coordinate, boundary and malformed-proposal tests. On 64 public roots, compare four greedy-ordered coordinate updates with the same update multiset randomly permuted. All arms start at identical feasible baseline. Outcome is reduction in sum(p)/sum(initial); sham compares two independently permuted update sequences.

Mean ordered advantage 0.03279313845226293, 35 positive / 29 ties / 0 negative. Maximum absolute sham 0.27988338192419826; conditional 95/95 order statistic uses rank 64. The planner returns REDESIGN_OR_PILOT_ONLY (strict exit 2): heldout unsealed, independent families unverified, target and observed mean below variation floor, confirmation underpowered. Planned 128 roots would resolve about 0.29489 under this exploratory proxy, with no defensible power estimate for the smaller target. Public roots are generated from one structural family; 64 is a count of synthetic draws, not 64 independent mathematical discoveries. Exact finite checks, no neural evidence.

Local dev JSON SHA-256: 90776ecc953b2d2233e23af525a7bd8a5b6705d6f00db84405cfd40a55a5da9e. Recompute rather than edit receipts. The existing full repository test suite and receipt checker were unavailable in the isolated sandbox; CI/reviewer should run them.

## Next gate

Design multiple distinct contraction, potential, charging and recurrence families and independent verifier implementations. Separate public development from future sealed families, estimate paired sham variation with >=59 independent development families, and freeze the model and cost budgets. The public MST result belongs exclusively to reference context, never the confirmation set. Run the existing preflight planner on real development-model outcomes before accepting a confirmation registration. No paid compute authorized by this draft.
