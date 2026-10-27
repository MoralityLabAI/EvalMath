# Mythos Max independent review: ETH proof-fidelity case

Review dated 2026-10-27; concerns [EvalMath PR #10](https://github.com/MoralityLabAI/EvalMath/pull/10). This records independent review findings, with no alteration of source-hashed receipts. **Merge is blocked pending receipt regeneration by its writer.**

## Reproduced evidence

Mythos independently confirmed the seven Git blob hashes against OpenAI's source tree, the existing structural source checks, the comparator import path, and the exact Hermite valuation probe. Its expanded rational grid of 129,258 cases (`a <= 9`, `M <= u+8`) agreed with the manuscript's valuation identity and `-6Dh` lower bound. This strengthens confidence in that *finite identity check* and leaves the interpolation-recovery theorem unproved by the probe.

## Issues

**Must fix:** the committed receipt was manually patched after generation. Rerun `PYTHONPATH=src python scripts/verify_proof_fidelity_openai_eth.py --output <new unique path>` on the complete checkout, compare the output to the tracked receipt, then replace it using the generated file, not a modified JSON object. Follow with `python scripts/check_receipts.py --only openai_eth_fidelity` and the relevant pytest cases. An immutable receipt should record the writer's actual output.

**Definition fidelity:** the comparator defines its own `SAT.count`, `encodeCNF`, `runtimeScale`, `runtimeBound`, and `visitedSpace`. Identical whitespace-normalized theorem signatures do not guarantee identical elaborated meanings across namespaces/imports. Check the comparator's embedded `runtimeScale n = n * (log(log(n+16)))^2/sqrt(log(n+16))` explicitly and freeze the relevant comparator definitions. Compare elaborated types through the upstream comparator mechanism for the strongest fidelity claim.

**Count integrity:** `seven_git_blob_pins`, `evidence_labels_fail_closed`, and `three_exponents_have_strict_audit_order` duplicate stronger validation or are constant. Either drop these from the check count or mark them explicitly as derived status metadata; distinguish source-token checks from independent mathematical checks.

**Scope:** the archived files include three of four manuscript `\\input` dependencies; `quantitative-circuits.tex` is the omitted consequences appendix and is outside the main theorem's dependency path. Document the intentional omission, or archive and hash it as an eighth file.

**Cleanup:** remove duplicate `upstream_path` and `git_blob_sha` guards in `run_audit`. The general `2^{o(n)}` consequence holds for arbitrary fixed-width 3-SAT after removing duplicate clauses: `m = O(n^3)`, hence the polynomial `n+m` factor does not prevent it. Adjust the sparse-formula wording.

## Status

The reviewer found no incorrect source SHA, no counterexample to the finite valuation identity, and no justified claim of a cryptanalytic break. The remaining risks concern evidence provenance, precise formal referents, and mathematical review of the tensor proof. Preserve this note even after correcting the report so the audit trail remains legible.
