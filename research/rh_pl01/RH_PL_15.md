# RH-PL-15: ordinal facts and construction of the normalized recurrence

Date: 2026-11-25.

Evidence level: checked derivations in the frozen candidate Hilbert calculus, with exact proof-length accounting. The standard-ZFC audit and the analytic equivalence of the arithmetic RH target remain open.

## Result

The construction conditions left explicit in RH-PL-13 have been discharged. A set-coded recurrence now follows from the least-inductive Omega predicate, a natural initial value, and the exact totality/functionality clause for the supplied multiplication graph. Power and Separation construct the bounded family of finite prefixes inside the proof. The proof establishes the family's coverage and compatibility, supplies the local recurrence witnesses, and applies the checked union-gluing theorem.

The resulting closed theorem universally quantifies its remaining free parameters. Before that closure, its antecedent has exactly these formulas:

| Parameter condition | Exact source |
|---|---|
| `Omega(W37)` | Frozen definition clause 0, with its natural-set parameter renamed |
| `C06 ∈ W37` | The designated initial value belongs to the natural set |
| `Total2(MUL8,W37)` | Full frozen clause 6, with the graph and natural-set parameters renamed |

Here `U(x,a)` abbreviates the existing Kuratowski-pair graph-application formula. The conclusion supplies a set `U` satisfying:

\[
\begin{aligned}
&\forall x\in W\;\exists a\in W\;U(x,a),\\
&\forall x,a,b\in W\;[U(x,a)\land U(x,b)\to a=b],\\
&\forall z,a\in W\;[\operatorname{Empty}(z)\land U(z,a)\to a=C_0],\\
&\forall x,y,a,b\in W\;[\operatorname{Succ}(x,y)\land U(x,a)\land U(y,b)
\to\operatorname{Mul}(y,a,b)].
\end{aligned}
\]

The actual target uses the original membership/equality syntax and the existing encodings of conjunction and quantification. Its conclusion matches the normalized RH-PL-13 recurrence goal exactly after the natural-set parameter is renamed. The audit reconstructs that goal from the older compiler and compares it with the new theorem's actual consequent.

`Total2` supplies a total functional binary operation on the natural domain. The construction uses no arithmetic identity specific to multiplication. Specializing the initial value to the designated one and relating the operation to the arithmetic definitions will give the intended denominator interpretation.

The graph properties quantify natural inputs and natural-valued applications. They allow unrelated set members in the graph, as the frozen `Total1` definition also does.

## Ordinal facts derived from Omega

`ordinals.mjs` compiles seven supporting theorems. Their only set-theoretic input beyond logical equality is the existing least-inductive Omega predicate and the Separation instances used by the induction compiler.

Every member of a natural belongs to Omega. Induction also establishes that each natural is transitive. From that result, another induction gives `n ∉ n`: if a successor belonged to itself, its successor equation would place it inside its predecessor or identify it with that predecessor. Transitivity then contradicts the induction hypothesis. Foundation is absent from these emitted proofs.

The resulting helpers prove that natural successors are injective, that the successor of `n` lies outside the initial segment through `n`, and that a predecessor lies in any natural endpoint containing its successor. The final fact has the form

\[
\Omega(W)\land n\in W\land\operatorname{Succ}(x,y)
\land(y=n\lor y\in n)\;\to\;x\in n.
\]

An additional induction classifies a natural as empty or as the successor of another natural. The prefix construction needs no general trichotomy theorem.

All seven ordinal theorems passed both certificate replay and the original checker on their fully expanded unary proof strings.

## Exact Good prefixes

`prefix_predicates.mjs` names the formulas already used by RH-PL-13. It preserves the literal `Good` predicate, which requires a natural initial-segment domain, functionality on natural applications, the common base equation, and the multiplication recurrence.

The audit extracts `Good` from the independently generated RH-PL-13 family theorem. It checks byte-for-byte equality with the shared predicate and verifies that the appropriate instantiations occur in the actual theorem targets. The source family equation receives the same comparison.

### Extending a prefix

`prefix_extension.mjs` starts with a bounded Good graph whose domain ends exactly at `n`, a natural successor `s`, and natural values `a,b` satisfying `G(n,a)` and `Mul(s,a,b)`. It appends the ordered pair `(s,b)` using the existing Pairing and Union construction.

The new graph has the exact domain through `s`. Its Good proof handles every combination of old and appended applications in the recurrence:

| Predecessor application | Successor application | Justification |
|---|---|---|
| Old | Old | The previous Good recurrence applies |
| Old | Appended | Successor injectivity identifies the old index with `n`; functionality identifies its value with `a` |
| Appended | Old | Predecessor closure would put `s` in the old initial segment, contradicting freshness |
| Appended | Appended | Successor membership would force the same forbidden initial-segment membership |

The base equation survives because a successor contains its predecessor and therefore cannot be empty. The theorem returns boundedness, the complete Good predicate, the exact enlarged domain, and the append relation.

### Agreement on overlaps

`prefix_overlap.mjs` applies Omega induction to agreement between two Good graphs at a natural index. At an empty index, their base equations give the same value. At a successor index, each domain equation supplies a predecessor value. The induction hypothesis identifies those values, after which the exact functionality half of the multiplication clause identifies the new values.

The family version obtains Good from each graph's membership in the literal bounded family. Its conclusion has the compatibility form required by the union-gluing proof.

### Coverage through each endpoint

The weaker statement that some prefix covers `x` leaves its endpoint unspecified. A prefix selected by that statement can already extend beyond `x`, so appending at the successor of `x` requires an additional argument.

`prefix_total.mjs` proves the stronger statement directly:

\[
\forall n\in W\;\exists G\in\mathcal F\;
\bigl(\operatorname{DomainThrough}(G,n)
\land\exists a\in W\;G(n,a)\bigr).
\]

The new strong singleton theorem supplies the exact empty endpoint. At each successor, multiplication totality produces the next natural value and the full Good-extension theorem constructs the next prefix. The family equation then admits that graph as a member.

For the final local-extension interface, `prefix_recursion.mjs` chooses a prefix ending at the successor `y`. The successor equation yields `x ∈ y`, so its exact domain supplies the predecessor value at `x`. Both values now occur in one Good graph, whose recurrence provides the required multiplication witness. This also handles the older interface's arbitrary coverage witness.

## Proof lengths

Unary and compact columns charge every emitted formula in full, followed by LF. Formula sharing in the compiler leaves these costs unchanged. Certificate JSON sizes measure the stored replay format and have a different role.

| Theorem | Lines | Unary bytes | Compact bytes | Original expanded replay |
|---|---:|---:|---:|---|
| Omega transitive | 4,351 | 12,431,552 | 1,299,425 | Passed |
| Natural members transitive | 4,549 | 19,037,766 | 1,639,799 | Passed |
| Natural members irreflexive | 7,812 | 24,978,008 | 2,502,100 | Passed |
| Natural zero or successor | 4,176 | 23,640,812 | 2,263,040 | Passed |
| Natural successor injectivity | 8,712 | 28,532,823 | 2,881,024 | Passed |
| Successor outside prior initial segment | 8,344 | 26,515,089 | 2,685,359 | Passed |
| Predecessor in initial segment | 5,023 | 20,687,519 | 1,825,188 | Passed |
| Exact empty endpoint | 24,022 | 350,494,097 | 31,474,512 | Pending |
| Full Good-prefix extension | 74,615 | 1,222,709,972 | 102,714,722 | Pending |
| Good-prefix overlap agreement | 16,357 | 403,079,869 | 35,494,820 | Pending |
| Bounded-family compatibility | 18,001 | 581,619,726 | 52,281,301 | Pending |
| Exact endpoint coverage | 92,049 | 2,330,717,645 | 206,023,266 | Pending |
| Normalized recurrence construction | 139,386 | 4,660,265,835 | 426,456,191 | Pending |

The final recurrence certificate occupies 4,093,403 JSON bytes. Its closed target has 22,880 unary bytes, of which 16,035 describe the normalized existential conclusion. That conclusion's SHA-256 is `dd40178c27f63eb4ca9be7b46ff5c1f64831667d7d131ea34218a844dfe09320`.

These proof costs describe the displayed auxiliary theorems. The arithmetic RH target retains its recorded lower floors of 570,269 unary bytes and 69,411 compact bytes. Its finite upper bound remains unknown.

## Verification and trust

The six audit receipt files record source SHA-256 values, frozen-file Git blobs, exact target hashes, proof lengths, replay results, and mutation outcomes. All thirteen theorems passed independent certificate replay. All recorded source hashes match the completed source files.

The certificate verifier checks the syntax DAG, closed target, proof order, logical axiom schemas, modus ponens, generalization, and exact costs. It computes lengths with `BigInt`. Nonpropositional axiom recognition still calls the frozen original kernel's recognizer; the independent replay therefore shares that component of the trust base.

Each theorem received six mutation checks, and all 78 mutants were rejected. They corrupt the byte count or target, introduce a cycle or duplicate syntax, duplicate a proof line, and remove an essential premise. The last check recalculates the claimed costs before replay and requires rejection at an unjustified proof line. The helper regression also rejected five invalid Omega, membership, initial-segment, and successor arguments.

The existing append, base, gluing, family-existence, and conditional-recursion compiler receipts reproduce exactly across seven old theorem rows. The earlier four ordered-pair/interface theorems were also replayed with the original checker under Node. All execution described here used the actual Node CLI.

The repository's Python receipt check regenerated 29 of its 31 fast receipts on its first run. The two remaining checks required the missing `pytest` dependency. After installing that dependency, `python scripts/check_receipts.py --only cpf_suite cpf` regenerated both identically. The combined runs cover all 31 fast receipts. The slow receipt set and the full Python/Lean suites were outside this stage's verification.

The frozen files retain these Git blobs:

| File | Git blob |
|---|---|
| `kernel.mjs` | `35da89e237ecbd1a807ade3fffb39ffd57890ace` |
| `rh_target.txt` | `a55f16f293a784ca91d9d52d65cbaea1e89f80dc` |
| `rh_target_compact.txt` | `98fb1ce81784556af2f6dff8d0d6b31d9c69d7e5` |

## Reproduce

Use Node 24 or another runtime supporting the existing `.mjs` modules. The verification run used Node v24.22.3.

```bash
node research/rh_pl01/ordinal_audit.mjs ordinals
node research/rh_pl01/ordinal_audit.mjs base
node research/rh_pl01/ordinal_audit.mjs extension
node research/rh_pl01/ordinal_audit.mjs overlap
node research/rh_pl01/ordinal_audit.mjs total
node research/rh_pl01/ordinal_audit.mjs recursion
node research/rh_pl01/pl15_regression.mjs all
```

Each audit receipt can be regenerated with `--output PATH`. To export and check a standalone final certificate:

```bash
node research/rh_pl01/ordinal_audit.mjs recursion --emit 0 > /tmp/rh-pl15-recursion.json
node research/rh_pl01/joint_audit.mjs --verify /tmp/rh-pl15-recursion.json
```

## Remaining bridge

RH-PL-16 can specialize the initial value to the designated one and reconstruct the exact frozen denominator clauses. Clause 14 requires the existing totality/functionality formulas in their original quantified layout. Clause 19 needs a value at the designated empty natural and its base equality. For clause 21, Omega successor closure and graph totality supply the existential witnesses that wrap the normalized update equation.

Full expanded replay of the six larger new proofs remains open. The standard-ZFC calculus audit, analytic-DMR equivalence, and ordinary-ZFC reconstruction also remain open. The new Node audit has yet to receive an independent CI execution.
