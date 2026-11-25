# RH-PL-18: construct the joint numerator and denominator graphs

Date: 2026-11-26.

Evidence level: checked derivations in the frozen candidate Hilbert calculus, with independent certificate replay and exact proof-length accounting. All five composed existence theorems passed the independent audit recorded in [numerator_existence_audit_receipt.json](numerator_existence_audit_receipt.json).

## Exact theorem

This stage constructs a numerator graph for a supplied total denominator graph, then combines that construction with RH-PL-16's denominator construction. The final theorem uses the original variable slots and literal clauses of [rh_target.txt](rh_target.txt).

Let \(C_i\) denote clause \(i\) in the frozen target's antecedent, counting from zero. Before universal closure of its remaining free parameters, the final theorem is

\[
\left(\bigwedge_{i=0}^{6} C_i\right)
\;\longrightarrow\;
\exists v_8\,\exists v_7\;
  \left(C_{13}\land C_{14}\land C_{18}\land C_{19}\land C_{20}\land C_{21}\right).
\]

Every displayed conjunction is associated to the right in the checked formula. The existential order is denominator graph \(v_8\), followed by numerator graph \(v_7\). Universal closure binds the remaining parameters \(v_0,\ldots,v_4\).

| Clause | Meaning in the frozen target |
|---|---|
| 0 | The least-inductive natural set \(W\) |
| 1 | The designated zero belongs to \(W\) |
| 2 | The designated zero is empty |
| 3 | The designated one belongs to \(W\) |
| 4 | The designated one is the successor of zero |
| 5 | Addition is total and functional on natural arguments |
| 6 | Multiplication is total and functional on natural arguments |
| 13, 14 | Numerator and denominator totality and functionality |
| 18, 19 | Numerator initial value zero and denominator initial value one |
| 20, 21 | Numerator and denominator successor recurrences |

The proof retains clause 4 as part of the frozen zero/one block. Its derivation only uses natural membership of the selected initial denominator value, so the successor equation for one is an unused strengthening of the antecedent.

The operations remain arbitrary total functional natural relations throughout the construction. Their addition and multiplication laws are separate frozen clauses. Under the intended natural arithmetic interpretation, the resulting equations are

\[
B_0=1,\qquad B_{n+1}=(n+1)B_n,
\]

\[
A_0=0,\qquad A_{n+1}=(n+1)A_n+B_n.
\]

Identifying \(B_n\) with \(n!\), and \(A_n\) with the corresponding harmonic numerator, requires that arithmetic interpretation.

## A total affine step relation

[numerator_step.mjs](numerator_step.mjs) uses the existing exact predicates for denominator application, multiplication and addition. Write them as \(B(x,d)\), \(\operatorname{Mul}(y,a,u)\) and \(\operatorname{Add}(u,d,b)\). Define

\[
\begin{aligned}
R(y,a,b)\;\Longleftrightarrow\;&
  (\operatorname{Empty}(y)\land a=b)\\
&\lor\;\exists x,d,u\in W\;
  [\operatorname{Succ}(x,y)\land B(x,d)\\
&\hspace{39mm}\land\operatorname{Mul}(y,a,u)\land\operatorname{Add}(u,d,b)].
\end{aligned}
\]

The empty-index branch returns the previous value. It makes the auxiliary operation defined at every natural index, as required by the existing recursion constructor. The numerator's initial value is supplied separately as its seed.

The first theorem proves

\[
\forall y,a\in W\;\exists b\in W\;R(y,a,b)
\]

from Omega and exact clauses 14, 6 and 5. RH-PL-15's natural classification gives an empty set or a natural predecessor. In the empty case, choose \(b=a\). For a successor, denominator totality supplies \(d\), multiplication totality supplies \(u\), and addition totality supplies \(b\). Each existential includes the natural-membership guard required by the next application.

The functionality proof assumes natural \(y,a,b,c\) with \(R(y,a,b)\) and \(R(y,a,c)\). Two empty branches give \(b=a=c\). An empty branch and a successor branch contradict the successor's membership property. When both branches use predecessors, natural successor injectivity identifies those predecessors. Denominator functionality then identifies their values. Multiplication functionality identifies the product witnesses, and addition functionality gives \(b=c\).

This argument uses no denominator recurrence. It depends on the denominator's natural applications through its exact totality/functionality clause. The same restriction to natural inputs and outputs applies to the supplied operation graphs.

### Recover the normalized update

A fourth theorem handles the interface needed by the numerator constructor. Given natural \(x,y,a,b,d\), a successor equation \(\operatorname{Succ}(x,y)\), \(R(y,a,b)\), and a requested denominator value \(B(x,d)\), it proves

\[
\exists u\in W\;
  [\operatorname{Mul}(y,a,u)\land\operatorname{Add}(u,d,b)].
\]

The empty branch contradicts \(x\in y\). In the successor branch, injectivity aligns the relation's predecessor with \(x\); denominator functionality aligns its value with \(d\). Equality transport then gives the requested sum relation. Omega and exact denominator functionality suffice for this conditional conversion.

The exported `successorUpdateAt` helper chooses private witnesses above every variable currently in the formula arena. Its output existential also avoids the supplied arguments. A separate control invokes it with argument 70 and checks that 70 remains free in the result. That control passes independent certificate replay.

## Build a set containing the binary graph

[binary_graph.mjs](binary_graph.mjs) realizes a natural ternary relation as a binary operation graph. Its application formula is the frozen encoding

\[
\operatorname{App}_2(T,y,a,b)
\;\Longleftrightarrow\;
\langle\langle y,a\rangle,b\rangle\in T,
\]

with the ordered pairs expanded into their existing Kuratowski definitions.

For \(y,a\in W\), the inner pair \(p=\langle y,a\rangle\) belongs to \(\mathcal P^2(W)\). The outer pair has coordinates \(p\) and \(b\), so the constructor forms the carrier

\[
S=W\cup\mathcal P^2(W).
\]

Both outer coordinates belong to \(S\), which places \(\langle p,b\rangle\) inside \(\mathcal P^2(S)\). Power Set supplies the powersets. Pairing and Union produce \(S\) by forming \(\{W,\mathcal P^2(W)\}\) and taking its union.

Separation selects the elements of \(\mathcal P^2(S)\) that have natural witnesses \(y,a,b\), the required inner and outer pair witnesses, and \(R(y,a,b)\). The ordered-pair injectivity lemmas then prove

\[
\forall y,a,b\in W\;
\left[\operatorname{App}_2(T,y,a,b)\longleftrightarrow R(y,a,b)\right].
\]

The realization theorem works for the supplied relation without assuming Omega. A second theorem transports natural totality and functionality through this equivalence to obtain the literal `Total2(T)` shape extracted from frozen clause 6. All bounding-set witnesses are eliminated before the constructor returns its existential graph.

Instantiating this constructor with the affine relation gives a total binary graph from Omega, denominator clause 14, multiplication clause 6 and addition clause 5. Its graph variable is fresh slot 64. The auxiliary graph will be eliminated after recursion has produced the numerator.

## Apply finite-prefix recursion

[numerator_existence.mjs](numerator_existence.mjs) specializes the RH-PL-15 recurrence theorem to seed \(Z\) and the new affine graph \(T\). The theorem's operation parameter accepts the exact `Total2` contract, so the construction can reuse the completed family of finite prefixes, their overlap agreement, and the graph obtained from their union.

The recurrence yields natural totality and functionality for the numerator, its empty-input equation, and an application of \(T\) at each successor. The graph equivalence turns that application into \(R(y,a,b)\). The successor conversion above supplies the natural product-and-sum witness used by RH-PL-17's normalized numerator predicate. At this point the target contains no free reference to \(T\), allowing its existential witness to be discharged.

The normalized existence theorem has exact premises \(C_0,C_1,C_5,C_6,C_{14}\). Adding \(C_2\), the designated zero's empty-set formula, enables the earlier numerator bridge and gives

\[
(C_0\land C_1\land C_2\land C_5\land C_6\land C_{14})
\longrightarrow
\exists v_7\;(C_{13}\land C_{18}\land C_{20}).
\]

[joint_recurrence_existence.mjs](joint_recurrence_existence.mjs) first constructs the denominator using natural seed one and the supplied multiplication graph. Its exact clause 14 discharges the remaining denominator premise of the numerator existence theorem. The exact base and recurrence clauses from both graphs are then placed in their original order and both graph witnesses are existentially closed.

Parameter changes are proved by universal generalization and instantiation. The literal-source numerator theorem consumes the selected addition parameter 7 before renaming the bound numerator to original slot 7. It consumes multiplication parameter 8 before introducing denominator parameter 8. The final joint theorem has no free graph parameters, and its consequent binds the original denominator and numerator slots directly.

## Proof costs

Each cost charges every emitted formula in full, followed by LF. Certificate DAGs share syntax for storage and replay; the unary and compact totals still charge the expanded formula for each proof line.

| Supporting theorem | Lines | Unary bytes | Compact bytes |
|---|---:|---:|---:|
| Affine step totality | 12,298 | 221,413,090 | 20,811,320 |
| Affine step functionality | 27,732 | 728,844,473 | 65,033,720 |
| Affine totality and functionality together | 38,979 | 981,525,399 | 89,332,662 |
| Affine successor to normalized update | 18,135 | 252,745,977 | 22,022,016 |
| Bounded graph realizing the affine relation | 45,212 | 1,798,502,470 | 139,093,135 |
| Total binary graph from the relation's two laws | 50,081 | 2,007,959,894 | 158,721,756 |
| Affine binary graph from the arithmetic premises | 88,193 | 2,987,635,713 | 247,875,722 |

[affine_audit_receipt.json](affine_audit_receipt.json) records independent replay of these seven certificates and the additional argument-70 capture control. All 48 certificate mutations and 25 statement mutations were rejected. The audit checks the complete closed targets and reconstructs the relation from the frozen source through an independent AST traversal. A second regeneration reproduced the receipt byte for byte.

| Existence theorem | Lines | Unary bytes | Compact bytes | Target bytes |
|---|---:|---:|---:|---:|
| Normalized numerator | 226,985 | 8,331,911,039 | 740,536,054 | 37,281 |
| Exact numerator with selected parameter names | 246,828 | 8,934,664,565 | 804,661,729 | 28,482 |
| Exact numerator in original frozen slots | 246,976 | 8,944,171,582 | 806,029,512 | 25,641 |
| Joint block with selected parameter names | 261,632 | 9,447,309,489 | 862,632,384 | 34,925 |
| Joint block in original frozen slots | 261,905 | 9,472,148,411 | 866,264,361 | 30,897 |

Every row passed structural replay and independent certificate replay, which recomputed these counts. The final original-slot certificate occupies 7,961,630 JSON bytes. Its charged unary proof length remains 9,472,148,411 bytes, and its compact proof length remains 866,264,361 bytes. Fully expanded original-checker replay has not been run for these proofs.

[numerator_existence_audit.mjs](numerator_existence_audit.mjs) checks the complete closed targets, including their universal closure. It reconstructs literal source clauses through an independent AST traversal and reads the normalized contracts from the earlier RH-PL-12 and RH-PL-13 theorem targets. The receipt authenticates 36 transitive source files and the unchanged frozen checker and target blobs.

Each of the five existence certificates rejects six mutations, giving 30 certificate controls. For each statement, the audit also rejects a changed conclusion, a dropped premise, and replacement of an existential witness by a universally closed parameter, giving 15 statement controls. All passed.

The independent replayer checks inference and costs without the producer's parent pointers. It shares the frozen recognizer for nonpropositional axioms. The larger audit of this candidate calculus against standard ZFC remains open.

## Native Lean obligations

[RHNumeratorStep.lean](../../lean/FeedbackChannel/RHNumeratorStep.lean) adds a native analogue over Lean's `Nat`. Its `mul`, `add` and `den` arguments are arbitrary total functions. The relation's intermediate graph applications become equality witnesses for function values, and the earlier native recurrence theorem supplies the final function.

| Theorem | Obligation |
|---|---|
| `affine_step_zero_iff` | Identify the empty-index branch with the previous value |
| `affine_step_succ_iff` | Normalize a successor's predecessor and operation witnesses |
| `affine_step_iff_graph` | Identify the relation with its deterministic function |
| `affine_step_total` | Produce an output for every index and previous value |
| `affine_step_functional` | Prove that two relational outputs agree |
| `affine_recurrence_iff` | Translate the relational recurrence to the earlier recurrence interface |
| `affine_recurrence_exists_unique` | Construct the function and prove uniqueness for any seed and denominator |
| `affine_recurrence_eq_joint_numerator` | Identify the function with the earlier joint numerator when its denominator is selected |

All eight declarations carry source-boundary markers and are exported as full-proof exercises in [gyms/RHNumeratorStep](../../gyms/RHNumeratorStep). A learner's source inlines the earlier recurrence module and includes the declarations before its target. The source charge includes that dependency and the visible prefix. The teacher proofs remain public training material in the existing recurrence family.

The [native receipt](../../gyms/RHNumeratorStep/native_receipt.json) records a complete local pass on the pinned Lean 4.34.1 toolchain. Thirty native compilations checked the module, all eight teacher exercises, six actual `trace_state` goals, twelve candidate closures, and the controls that require compilation. The candidate pack contains six accepted tactics and six rejected mutations. Six additional controls cover invalid equality, admission, self-reference, a future theorem reference, a changed zero branch, and an incorrect predecessor index. The module's theorem axiom union is `Quot.sound`.

The six local repair inputs occupy 134–214 UTF-8 bytes in the exact PPT statement/goal format; their tactics occupy 94–303 bytes. Each fits the existing 384-byte input or candidate cap. Their complete theorem sources accompany the compact public views, and the native checker verifies closure of the whole submitted theorem. This package remains one public training family. Its native Nat/function proofs and the Hilbert constructions retain separate formulas, verifiers and proof-length measures.

Both pinned upstream loaders accepted the new pack with six usable cases, twelve candidate labels and zero truncated inputs, as recorded in the [adapter receipt](../../gyms/RHNumeratorStep/adapter_receipt.json). The shared trainer contract fixes DataGoblin at `48c99a7d9c2d37c82fe127369dfa0124b88bc8ab` and LoopedTransformers at `8931f9d9cf0b064cea5cb3ad0760fe2dcd5197fa`.

The pinned PPT trainer completed 32 CPU candidate-ranking updates on the new pack using 25,571 parameters, width 32, four heads and eight workspace slots. The step log visits all six cases and uses recurrent depths 1 and 2. With seed 17 and Torch `2.5.1+cpu`, the trainer reported 0.200 seconds for its training loop. [training_smoke.json](../../gyms/RHNumeratorStep/training_smoke.json) preserves the upstream manifest and runtime details; [training_steps.jsonl](../../gyms/RHNumeratorStep/training_steps.jsonl) records every update. This run checks the path from verified Lean candidates to optimizer updates. Its preflight verdict remains `REDESIGN_OR_PILOT_ONLY` within the existing public family. Transfer or comparative loop-effect claims require independent families and a separate evaluation design.

## Reproduction

The producers can be compiled separately:

```bash
node research/rh_pl01/numerator_step.mjs
node research/rh_pl01/binary_graph.mjs
node research/rh_pl01/numerator_existence.mjs
node research/rh_pl01/joint_recurrence_existence.mjs
```

The native module and its exported proof tasks can be replayed with the pinned toolchain:

```bash
python scripts/verify_rh_numerator_native.py --lean-cmd lean
PYTHONPATH=src python -m spiral_ln.rh_numerator_gym serve --lean-cmd lean
```

The binary-graph CLI uses the default multiplication relation. The affine audit instantiates it with `numeratorStep.relation` and records the costs displayed here. The audit commands write fresh receipts:

```bash
node research/rh_pl01/affine_audit.mjs \
  --output /tmp/affine_audit_receipt.json
node research/rh_pl01/numerator_existence_audit.mjs \
  --output /tmp/numerator_existence_audit_receipt.json
cmp /tmp/affine_audit_receipt.json \
  research/rh_pl01/affine_audit_receipt.json
cmp /tmp/numerator_existence_audit_receipt.json \
  research/rh_pl01/numerator_existence_audit_receipt.json
```

The existence audit checks the three numerator theorems and the two joint theorems. It reconstructs their complete antecedents and consequents from the frozen source. Individual existence certificates are available with `numerator_existence_audit.mjs --emit INDEX`, for indices 0 through 4, and can be replayed using `joint_audit.mjs --verify FILE`.

## Remaining obligations

The final theorem still assumes the least-inductive natural set, the zero/one block, and total functional addition and multiplication graphs. Their arithmetic interpretation and the corresponding defining equations remain separate proof obligations. Constructing the least-common-multiple and increment graphs would address the other auxiliary objects in the frozen antecedent.

The exact numerator and denominator block is now obtained from those displayed arithmetic premises. This advances the earlier numerator bridge's assumed existence contract. The full frozen RH conclusion, its analytic equivalence, and standard-ZFC certification remain open. The RH lower floors remain 570,269 unary bytes and 69,411 compact bytes; a finite upper bound for the frozen RH target remains unknown.
