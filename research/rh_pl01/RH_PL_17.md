# RH-PL-17: numerator bridge and proof curriculum

Date: 2026-11-25.

Evidence level for the mathematics below: checked derivations in the frozen candidate Hilbert calculus, with independent certificate replay and exact proof-length accounting.

## Conditional numerator bridge

The normalized numerator properties imply the exact numerator clauses in the frozen target. The proof requires the least-inductive Omega predicate, a designated empty natural set, and a denominator graph satisfying the target's totality/functionality clause. Existence of a numerator graph satisfying the normalized properties remains an assumption throughout this stage.

The new formulas and proofs are in [numerator_predicates.mjs](numerator_predicates.mjs) and [numerator_bridge.mjs](numerator_bridge.mjs). The selected free parameters are:

| Meaning | Frozen slot | Parameter in the first bridge |
|---|---:|---:|
| Natural set | 0 | `W37` |
| Designated zero | 1 | `Z60` |
| Addition graph | 3 | `ADD7` |
| Multiplication graph | 4 | `MUL8` |
| Numerator graph | 7 | `NUM62` |
| Denominator graph | 8 | `DEN61` |

The predicate helper also carries the unused mapping from the original one parameter, slot 2, to slot 6. Neither one parameter occurs freely in the numerator bridge statements.

Renaming proceeds through fresh temporary variables. This preserves the distinction between original numerator slot 7 and new addition slot 7, as well as original denominator slot 8 and new multiplication slot 8. The final supporting theorem instantiates the parameters back into the original frozen slots.

### Normalized premise

Write `G(x,a)` for the existing Kuratowski-pair application formula for the numerator graph, and `B(x,d)` for application of the denominator graph. `Mul` and `Add` use the exact binary-operation graph formulas extracted from frozen clauses 6 and 5. The normalized numerator predicate is the conjunction of:

\[
\begin{aligned}
&\forall x\in W\;\exists a\in W\;G(x,a),\\
&\forall x,a,b\in W\;[G(x,a)\land G(x,b)\to a=b],\\
&\forall x,a\in W\;[\operatorname{Empty}(x)\land G(x,a)\to a=Z],\\
&\forall x,y,a,b,d\in W\;[\operatorname{Succ}(x,y)\land G(x,a)\land G(y,b)\land B(x,d)\\
&\hspace{35mm}\to\exists p\in W\;(\operatorname{Mul}(y,a,p)\land\operatorname{Add}(p,d,b))].
\end{aligned}
\]

The update premise has the same existential product-and-sum form proved by the earlier [numerator normalization](numerator.mjs). It supplies the natural operation witness needed by the forward bridge. No separate totality assumption for addition or multiplication is required for this conditional implication.

### Exact conclusion

Before universal closure, the combined theorem has exactly five premises:

| Premise | Source or definition |
|---|---|
| `Omega(W37)` | Frozen clause 0 after parameter renaming |
| `Z60 ∈ W37` | Membership of the designated zero |
| `Empty(Z60)` | Existing empty-set formula with bound variable 23 |
| `Total1(DEN61)` | Frozen denominator clause 14 after parameter renaming |
| `NormalizedNumerator(NUM62,DEN61)` | The four properties displayed above |

Its consequent is the conjunction of the literal renamed clauses 13, 18 and 20. Clause 13 packages numerator totality and functionality in the target's grouped implication form. The base bridge obtains a natural output at `Z`, then uses the normalized base equation to produce clause 18's existential witness.

For clause 20, successor closure supplies a natural successor. Numerator totality provides the outputs at the predecessor and successor, while denominator totality supplies its predecessor output. The normalized update then provides a natural product witness with the required sum relation. The exact clause has seven nested natural witnesses. The proof reuses the same successor for both successor terms and the same new numerator value for the outer value and sum value, so its final equality follows from reflexivity.

The denominator graph's base and recurrence equations are unused in this implication. Its totality/functionality clause is sufficient. Each graph statement concerns natural inputs and natural outputs; unrelated set members in a graph remain permitted by the frozen definitions.

## Proof sizes and replay

All costs below count the complete serialization of each emitted proof line plus its LF terminator. DAG sharing reduces certificate storage without changing these proof-length totals.

| Checked theorem | Lines | Unary bytes | Compact bytes | Certificate JSON bytes | Full original replay |
|---|---:|---:|---:|---:|---|
| Normalized totality/functionality to clause 13 | 3,107 | 19,861,013 | 2,045,187 | 90,281 | Passed |
| Normalized base to clause 18 | 1,620 | 13,558,404 | 1,282,228 | 45,401 | Passed |
| Normalized update to clause 20 | 12,603 | 332,506,235 | 34,003,549 | 371,587 | Above cap |
| Combined bridge with selected parameter names | 18,693 | 470,512,931 | 48,289,999 | 555,532 | Above cap |
| Combined bridge in original frozen slots | 18,711 | 471,370,349 | 48,389,788 | 566,120 | Above cap |

The original checker replay cap is 48,000,000 unary bytes. Every row passed structural replay and independent certificate replay. The first two also passed replay of their fully expanded proof text through the original checker. The larger three retain that remaining verification step.

## Statement fidelity and mutation checks

[numerator_audit.mjs](numerator_audit.mjs) checks the actual theorem antecedents and consequents against reference formulas derived independently of the new predicate helper. It extracts the exact numerator clauses directly from the frozen target and applies simultaneous substitution through an AST traversal. The producer uses fresh temporary variables instead.

For the normalized side, the auditor obtains totality, functionality, and the base formula from the earlier RH-PL-13 recurrence theorem, setting its initial value to `Z`. It obtains the product-and-sum witness formula from the actual target of RH-PL-12's local numerator normalization theorem. A delegating observer records that compiler's closed target while its original proof checks still execute. Neither the prior module nor the checker is modified.

Each of the five certificates rejects six mutations: an incorrect byte count, a different target, cyclic formula syntax, a duplicate syntax node, a duplicate proof line, and removal of an essential proof premise. The last mutation has its byte counts recomputed before replay, so rejection occurs at derivability. Each statement check also rejects a changed conclusion and deletion of its first premise. This gives 30 rejected certificate mutations and 10 rejected statement mutations.

Five substitution controls check the overlapping addition/numerator slots, overlapping multiplication/denominator slots, simultaneous swapping, bound-variable scope, and capture avoidance. All passed. The receipt records transitive source SHA-256 hashes and verifies these frozen Git blobs:

| File | Git blob |
|---|---|
| `kernel.mjs` | `35da89e237ecbd1a807ade3fffb39ffd57890ace` |
| `rh_target.txt` | `a55f16f293a784ca91d9d52d65cbaea1e89f80dc` |
| `rh_target_compact.txt` | `98fb1ce81784556af2f6dff8d0d6b31d9c69d7e5` |

The independent replayer shares the original recognizer for nonpropositional axioms. Its checks provide separate certificate traversal, inference replay, and byte accounting; they do not complete the outstanding audit of the candidate calculus against standard ZFC.

## Reproduction

```bash
node research/rh_pl01/numerator_bridge.mjs
node research/rh_pl01/numerator_audit.mjs \
  --output /tmp/numerator_bridge_audit_receipt.json
cmp /tmp/numerator_bridge_audit_receipt.json \
  research/rh_pl01/numerator_bridge_audit_receipt.json
```

The audit regenerated [numerator_bridge_audit_receipt.json](numerator_bridge_audit_receipt.json) identically in a separate run. Individual certificates can be emitted with `numerator_audit.mjs --emit INDEX` for indices 0 through 4 and checked with `joint_audit.mjs --verify FILE`.

The focused proof-replay workflow adds a numerator job that regenerates its receipt under `/tmp` and compares it with the committed receipt. [Run 45652582194](https://github.com/MoralityLabAI/EvalMath/actions/runs/45652582194) passed the numerator job and all four denominator groups at implementation commit `1ac0cad25bd2b087a5d465a0b7e407c7b0d6403d`.

## Proof curriculum

The new module `lean/FeedbackChannel/RHCompactification.lean` develops the sequence over Lean's `Nat`, using functions and graph predicates. It contains 14 definitions and 36 theorems, each delimited for source-derived task extraction. Its operation arguments are arbitrary total natural functions. The numerical witnesses specialize them to natural multiplication and addition and check denominator(6) = 720 and joint(6) = (1764, 720) by kernel reduction.

| Curriculum stage | Native mathematical obligation | Related Hilbert stage |
|---|---|---|
| Finite prefixes | Preserve earlier values, restrict a prefix, extend its endpoint, construct every finite prefix | RH-PL-14 and RH-PL-15 |
| Overlap | Agree on a common domain and recover graph functionality | RH-PL-15 |
| Gluing | Identify the union graph with a diagonal function and recover its recurrence | RH-PL-15 |
| Global recursion | Prove existence, uniqueness, and equality with the glued function | RH-PL-15 |
| Denominator | Translate between recurrence equations and existential evaluation witnesses | RH-PL-16 |
| Joint recurrence | Construct numerator/denominator states and prove component uniqueness | RH-PL-17's next construction, in the native Nat setting |

Lean's primitive natural-number recursor supplies existence in this native setting. The separate Hilbert construction must still derive its corresponding set-coded graph. The native module's existential denominator predicate captures evaluation order; the frozen set-theoretic clauses retain their own checks and byte accounting.

### Gym and trainer interface

The gym lives in [`gyms/RHCompactification`](../../gyms/RHCompactification/README.md). Twenty exercises expose every declaration before the target and omit the target's completed proof and later declarations. A submitted proof is compiled in that exact prefix, and its theorem receives an axiom audit. The revision API accepts bounded sequences of candidate proofs, retains the shortest verified result, and returns the Lean diagnostic after each attempt. Its length measure charges the entire supplied Lean source, including the earlier declarations. The Hilbert byte measures above retain their original meaning.

A separate pack contains 12 local repair tasks and 24 candidate tactics. Each local goal comes from an actual `trace_state` run in the complete theorem harness. Public inputs occupy 136–237 UTF-8 bytes and tactics occupy 3–95 bytes, fitting the pinned PPT reader's 384-byte cap. Candidate labels are stored separately. Each positive label requires native closure, an allowed axiom list, and the hash of the complete source that was checked. Epochs bind the task to its context, template and compiler environment. Resource limits and missing audits produce unknown outcomes.

Both original loaders accepted the pack: DataGoblin's `rlt_pretrain_data.lean_rows` at commit `48c99a7d9c2d37c82fe127369dfa0124b88bc8ab` and LoopedTransformers' `ppt_gym.data.load_checked_pack` at `8931f9d9cf0b064cea5cb3ad0760fe2dcd5197fa`. The adapter authenticates 40 upstream source files. Its receipt records 12 positive and 12 negative candidates with zero truncated inputs.

The pinned PPT trainer completed 32 CPU optimizer updates on this pack using 25,571 parameters, width 32, four heads, eight slots, and recurrent depths 1 and 2. The recorded run took 0.394 seconds. `training_smoke.json` retains the raw upstream result and the explicit local engineering scope; `training_steps.jsonl` records every update. This checks the data-to-optimizer path. No held-out result or comparative neural effect was measured. The broader DataGoblin mixed-pretraining interface still requires independently allocated held structures, text data, and its revision lane.

### Verification and evidence scope

Local execution used Lean 4.35.0. Fresh replay passed all 36 module theorem axiom audits, all 20 teacher exercises, all 24 candidate checks, and all 12 local-context checks. The candidate labels matched their native results. The module's axiom union is `propext` and `Quot.sound`. Three negative controls rejected an invalid equality, an admission, and a self-reference. The module is registered in the repository's normal Lean build and axiom list. [The focused Lean 4.34.1 CI run](https://github.com/MoralityLabAI/EvalMath/actions/runs/45652582316) passed the complete native suite and all 54 gym tests at implementation commit `1ac0cad25bd2b087a5d465a0b7e407c7b0d6403d`. The full local fast-receipt command reproduced all 32 registered receipts.

The current curriculum is one public training family. Earlier solutions are available in later exercises, and all teacher material is public. The preflight therefore records `REDESIGN_OR_PILOT_ONLY`. Its four repeated pair certificates are instrument checks within the shared construction family. They supply no estimate of a neural loop effect. Fresh independent families, a causal sham calibration and a sealed readout remain prerequisites for a transfer study.

The fast structural receipt checks 11 integrity conditions, binds the recorded native and training results to their source files, and recomputes the preflight. Fresh Lean compilation is provided separately by `scripts/verify_rh_compactification_native.py`.

```bash
python scripts/verify_rh_compactification_native.py --lean-cmd lean
python scripts/check_receipts.py --only rh_compactification
PYTHONPATH=src python -m spiral_ln.rh_compactification_gym serve --lean-cmd lean
```

## Remaining mathematical obligations

This stage assumes the normalized numerator graph. Constructing that graph in the frozen Hilbert calculus, then composing it with the denominator construction, remains open. The proof also leaves the arithmetic interpretation of the supplied operation graphs to the corresponding frozen definitions.

These bridge sizes measure conditional supporting theorems. They supply no finite upper bound for a proof of the frozen RH target. The established RH lower floors remain 570,269 unary bytes and 69,411 compact bytes. The standard-ZFC calculus audit, analytic equivalence, and reconstruction of the full target retain their earlier open status.
