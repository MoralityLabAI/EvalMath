# CLQ-02/03 exploratory CPU results and CLQ-01 replay

Status: exact finite audit passed locally. Twelve CPU neural runs completed. Raw-input learning gate failed. Lean arithmetic draft wired into build/axiom audit, kernel status pending. No claim of a literature-priority result or neural solver.

## Evidence

CLQ-01 reran byte-for-byte (340,747 finite roots, 336 long roots, 36 modular witnesses; five tests pass). CLQ-02 generates shared-anchor balanced same-basin pairs on factor-disjoint prime splits: 24 train, 8 validation, 12 test moduli, excluding public CLQ-01 factors. Train 16/24/32-bit inputs; test 16/24/32/64/256/1024. Hard pairs match modulo 4d; all pairs match bit length and low two bits. 129 attempted groups were skipped by bounded generation; results apply to the selected population. Independent full-step audit verified all 7,749 distinct roots and group/split conditions.

| Population | Pairs | Distinct roots |
|---|---:|---:|
| Train | 2830 | 4245 |
| Validation | 524 | 786 |
| Test | 1812 | 2718 |

Quotient equality predicts 1530/1812 test pairs (282/564 collisions). Exact quotient gate decides 1248/1812 with zero errors and abstains on 564 collisions. Exact odd-step fallback resolves all 564. Direct iteration 440920 odd steps vs 146580 with typed routing. This is an iteration count with precomputed tables, not a total-cost or latency comparison.

Five-epoch raw byte-input transformer pilot, seeds 19/43/71:
| Arm | Parameters | Correct by seed out of 1812 | Mean accuracy |
|---|---:|---|---:|
| Tied one block | 29545 | 906, 910, 932 | 50.55% |
| Tied three loops | 29545 | 905, 909, 911 | 50.13% |
| Untied three blocks | 39289 | 902, 912, 902 | 49.96% |

Collision performance is approximately chance, including the 1024-bit length. Train performance remains weak. Linear quotient-equality probe balanced accuracy 48.28–53.52%; final-representation norm-matched perturbation is a head sensitivity check, not proof of internal mechanism. No positive recurrence or mechanistic result. Same-parameter contrast changes compute; same-depth contrast changes parameter count.

## Typed modular recurrence: CLQ-03

For 0<=r<d and b in {0,1}, let z=2r+b. Exactly one of z and z-d is in [0,d). A learned binary gate proposes one, and exact range verification accepts precisely the correct residue. Rejected proposals use the analytic integer comparator. This is a mathematical property of the typed transition, independent of neural reliability. The comparator alone solves the task cheaply.

Two-parameter float32 affine gate on z/d, supervised on 50,304 states:
| Seed | Transition correct /26880 | Clean roots /2718 | Repairs /755424 | Clean 1024-bit roots /540 |
|---|---:|---:|---:|---:|
|19|26731|1524|4070|0|
|43|26838|2057|1053|116|
|71|26803|1803|2102|30|

Verified recurrence: 2718/2718 roots for each seed. Precision witness: d=2^32+1, z=d-1 vs z=d, both normalize to float32 1.0; their correct decisions differ. Any deterministic gate given only this rounded feature has at most 1/2 accuracy on the balanced pair.

The neural gate starts with exact typed arithmetic supplied. It does not learn the raw quotient invariant. No performance benefit over the exact integer comparator is demonstrated.

## Receipt hashes

The complete local replay package includes experiment.py, typed_recurrence.py, independent audit.py, oracle.py, raw dataset and JSON receipts, README and SHA256SUMS. This repository note records the result digests; the separate CPU package is distributed as a conversation attachment, not committed here.

- Canonical dataset digest (sorted compact JSON): 9ff598cd8474a5846537c9ee60b47ffb960c284422f125f0ee49ae54ffc0fb7a
- results.json: f38354723c69a3e7c47f44647ec900e7c17614747c48e4ff5b6efd9d65625c1c
- typed_results.json: 2cf71f20655a0713c0e3cf23f9367f6b30b88abb8229c23ad377600addc4602d
- audit.json: da8f7071b0af3a8ca67e3e215a8e71886f9e7c288d88ba9c4560e3c3d25593fb

## Formal gates

lean/FeedbackChannel/CollatzQuotient.lean drafts odd numerator divisibility, odd-step bound, strict descent, closed region, abstract finite entry, exact gate range and uniqueness. No local Lean installation. Main quotient group action, linkage of actual next-odd map to the abstract bound, arbitrary modulus witness construction, and finite atlas correspondence remain unformalized. CI must check the draft before promoting its evidence level.

## Next sealed experiment

This pilot is public development evidence. Freeze fresh modulus-level splits and data hashes before further training; increase raw training budget, compare explicit digit-state supervision, exact quotient routing, exact comparator, learned gate with range projection, and a symbolic cost-matched control. No post-hoc reuse of present test roots as sealed evidence. Gate causal probes on above-baseline held-out representation and task accuracy; use matched counterfactual patches and charge all arithmetic and preprocessing.
