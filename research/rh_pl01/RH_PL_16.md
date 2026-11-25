# RH-PL-16: existence of the exact frozen denominator clauses

Date: 2026-11-25.

Evidence level: checked derivations in the frozen candidate Hilbert calculus, with exact proof-length accounting. The standard-ZFC audit and the analytic equivalence of the arithmetic RH target remain open.

## Result

The normalized recurrence constructed in RH-PL-15 now yields a graph satisfying the literal denominator clauses of the frozen target. The final theorem uses the original parameter slots and binds the denominator in its original slot 8.

Write `C_i` for the zero-based clause index in the frozen definition block. The new closed theorem is the universal closure over slots 0, 1, 2, and 4 of

\[
(C_0\land C_1\land C_2\land C_3\land C_4\land C_6)
\;\longrightarrow\;
\exists v_8\;(C_{14}\land C_{19}\land C_{21}).
\]

The auditor compares this entire antecedent and consequent against formulas extracted directly from `rh_target.txt`.

| Clause | Role in the final theorem |
|---|---|
| 0 | The least-inductive Omega predicate |
| 1 | The designated zero belongs to Omega |
| 2 | The designated zero is empty |
| 3 | The designated one belongs to Omega |
| 4 | The designated one is the successor of zero |
| 6 | The supplied binary operation is total and functional on natural inputs and outputs |
| 14 | The constructed denominator graph is total and functional on natural applications |
| 19 | Its value at the designated zero equals the designated one |
| 21 | Its successor values satisfy the exact frozen multiplication recurrence |

The first six rows are premises. The final rows occur under the existential denominator quantifier. Clause 4 records the designated-one interpretation; the general construction also proves existence for any natural initial value.

The final proof has 155,014 lines, charging 5,007,619,039 unary bytes or 463,124,911 compact bytes. These costs belong to the displayed denominator-existence theorem. The arithmetic RH target's finite upper bound remains unknown.

Its replay certificate occupies 4,591,215 JSON bytes. The canonical-parameter existence certificate occupies 4,556,621 bytes. Both passed independent certificate replay and exact comparison of their complete antecedents and consequents with the frozen source formulas.

## Reconstructing the frozen syntax

`denominator_predicates.mjs` extracts clauses directly from the frozen definition block. It also names the normalized recurrence from RH-PL-13 and RH-PL-15. The source parameter mapping requires care: original slot 4 denotes multiplication, while original slot 8 denotes the denominator. The normalized modules use slot 8 for multiplication. Renaming through fresh temporary variables preserves both parameters.

The independent auditor implements a different simultaneous substitution procedure over the decoded syntax tree. It checks swaps and overlapping source/destination slots, preserves bound source occurrences, and renames binders to prevent capture. An identity-mapping control confirms that the original literal clauses remain byte-identical.

### Forward bridge

`denominator_bridge.mjs` proves individual bridges for clauses 14, 19, and 21, then combines them.

Clause 14 reorganizes the normalized totality and functionality statements into the original quantified conjunction. The graph-application formulas undergo checked alpha conversion.

For clause 19, totality supplies a natural value at the designated zero. The normalized base equation identifies that value with the initial value, providing the exact existential witness required by the frozen clause.

Clause 21 expands nested term evaluation into several natural existential witnesses. Omega supplies a natural successor. Graph totality supplies the value at the predecessor and the value at that successor. The normalized update equation gives the multiplication relation. The proof reuses the same successor for both syntactic successor terms and the same output for the outer graph value and product value. Equality reflexivity supplies the final equality.

The clause-14 and clause-19 bridges passed the original checker on fully expanded unary proof strings. The remaining forward proofs passed certificate replay.

### Reverse bridge and equivalence

`denominator_normalize.mjs` recovers the complete normalized contract from the exact frozen clauses, assuming naturalness and emptiness of the designated zero. Empty-set uniqueness handles any empty natural input in the normalized base statement. For the update, successor uniqueness aligns the two successor witnesses in clause 21, and graph functionality identifies the remaining values.

`denominator_equivalence.mjs` combines both directions. Its statement has only Omega, naturalness of the designated zero, and emptiness of that zero as premises:

\[
\Omega(W)\land Z\in W\land\operatorname{Empty}(Z)
\;\longrightarrow\;
\bigl(\operatorname{Normalized}(G)\leftrightarrow
(C_{14}(G)\land C_{19}(G)\land C_{21}(G))\bigr).
\]

The existence proof uses naturalness of the initial value and totality of multiplication to construct a new recurrence graph. The equivalence theorem concerns a graph already satisfying one of the two contracts, so its antecedent is smaller.

## Composing existence

`denominator_existence.mjs` applies the forward bridge to the graph witness produced by RH-PL-15. The normalized graph witness is eliminated after introducing the exact denominator witness. A second theorem restores the original source slots and includes the designated-one successor clause in its premise block.

The output uses the exact frozen denominator totality, initial-value, and recurrence formulas. Its natural restrictions permit unrelated set members in the graph, consistently with the original `Total1` definition.

Clause 6 supplies a total functional binary operation. Ordinary multiplication semantics require the arithmetic equations in clauses 9 and 10 together with the addition structure. The usual factorial interpretation and positivity of denominator values remain arithmetic consequences to establish.

## Proof costs

Each byte column charges the full serialization of every emitted formula plus LF. The compiler and certificate may share syntax while maintaining these expanded costs.

| Theorem | Lines | Unary bytes | Compact bytes | Original expanded replay |
|---|---:|---:|---:|---|
| Normalized totality to clause 14 | 3,107 | 19,776,834 | 2,045,187 | Passed |
| Normalized base to clause 19 | 1,621 | 13,364,584 | 1,273,167 | Passed |
| Normalized update to clause 21 | 7,562 | 140,045,426 | 13,952,085 | Pending |
| Combined forward bridge | 13,511 | 237,391,041 | 23,708,460 | Pending |
| Exact clauses to normalized recurrence | 39,170 | 981,896,300 | 98,992,720 | Pending |
| Equivalence of the two contracts | 51,004 | 1,243,462,943 | 126,220,716 | Pending |
| Exact existence with normalized parameter slots | 154,140 | 4,981,306,872 | 459,246,371 | Pending |
| Exact existence with original frozen slots | 155,014 | 5,007,619,039 | 463,124,911 | Pending |

## Audit

`denominator_audit.mjs` checks every theorem's complete antecedent and consequent. The exact side comes from independently extracting the selected frozen clauses; the normalized side comes from the older RH-PL-13 compiler. The comparison therefore reaches the formulas in the actual theorem target.

The certificate replay validates the syntax DAG and proof order, recognizes propositional axiom schemas, checks modus ponens and generalization, and recomputes expanded costs with `BigInt`. Nonpropositional axiom recognition still uses the frozen kernel's recognizer.

Each theorem receives six certificate mutation checks and two statement mutation checks. The statement mutations replace the conclusion or remove the first premise. Deleting an essential proof premise recalculates costs before replay, so the expected rejection occurs at proof derivability. Five separate substitution controls cover the source-slot collision and binder behavior.

All eight theorems passed independent certificate replay. The audit rejected all 48 certificate mutants and all 16 statement mutants; every substitution control passed in each group. Four deterministic audit receipts record the target hashes, source SHA-256 values, and replay results, and every recorded source hash matches. The kernel and both target files retain their previous Git blobs:

| File | Git blob |
|---|---|
| `kernel.mjs` | `35da89e237ecbd1a807ade3fffb39ffd57890ace` |
| `rh_target.txt` | `a55f16f293a784ca91d9d52d65cbaea1e89f80dc` |
| `rh_target_compact.txt` | `98fb1ce81784556af2f6dff8d0d6b31d9c69d7e5` |

The full `python scripts/check_receipts.py` command passed all 31 fast receipts in this research checkout. No existing proof compiler was modified during RH-PL-16.

## Reproduce

The local run used Node v24.22.3.

```bash
node research/rh_pl01/denominator_audit.mjs bridge
node research/rh_pl01/denominator_audit.mjs normalize
node research/rh_pl01/denominator_audit.mjs equivalence
node research/rh_pl01/denominator_audit.mjs existence
python scripts/check_receipts.py
```

Each audit supports `--output PATH` for deterministic regeneration. A final standalone certificate can be produced and replayed with:

```bash
node research/rh_pl01/denominator_audit.mjs existence --emit 1 > /tmp/rh-pl16-denominator.json
node research/rh_pl01/joint_audit.mjs --verify /tmp/rh-pl16-denominator.json
```

The new `RH proof-length replay` GitHub Actions workflow runs the four audit groups on this research branch with Node 24. It writes regenerated receipts to `/tmp` and compares them with the committed copies. The matrix allows two concurrent jobs and sets a 20-minute limit per job.

[GitHub Actions run 45633076598](https://github.com/MoralityLabAI/EvalMath/actions/runs/45633076598) passed all four jobs at proof commit `b4ed6e589f1a73feb13e58d457b801b65e775842`. Each job independently regenerated its receipt and matched the committed JSON byte-for-byte.

The preceding general `verify` run at commit `280f430` passed 1,909 Python tests plus 13 subtests, and its Lean job passed. Its merge-ref receipt step stopped at a DCF16 check added on `main`, which expected a held-out data file in a sibling Compactification-Theory checkout. That external-data dependency remains outside these proof changes.

## Next construction

The displayed primitive setup now proves existence of the entire exact denominator block. The next recurrence construction can address the joint numerator/denominator update, including clauses 13, 18, and 20. The lcm and delta definitions, the frozen inequality, and the DMR-to-RH equivalence still require their own proofs.

Full expanded replay of the six larger RH-PL-16 proofs remains open. Standard-ZFC certification of the candidate calculus and ordinary-ZFC reconstruction also remain open. The frozen arithmetic target retains the RH-PL-07 lower floors of 570,269 unary bytes and 69,411 compact bytes.
