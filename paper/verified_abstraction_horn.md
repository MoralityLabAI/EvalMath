# VAD-06A — Horn proof DAGs and support-count abstraction discovery

Status: 2026-11-25. Fresh-family exact finite oracle and restricted source audit complete. Lean kernel replay for VAD-06A remains pending. The preceding VAD-05A kernel gate passed at a14ff7c, Actions run 45518870988.

## Model

Let F be a set of assumed propositional facts, and let each Horn rule (a1,...,ak) -> h be an assumed implication. All antecedent identifiers precede the consequent in a topological order. Every positive target is a leaf of the rule DAG and cannot be used as a premise. For a cache A of independently proved intermediate propositions, the exact minimum unfolded proof-reference cost is

    C_A(h) = min(1 if h is in F union A,
                 min_{rules r concluding h} [1 + sum_{a in antecedents(r)} C_A(a)]).

An empty minimum is infinity. Proof: induct over the topological order. Any proof term starts with a fact/cache reference or a rule reference applied to proofs of its antecedents. Conversely, take the minimizing rule and concatenate minimizing antecedent proofs. Costs count repeated references with multiplicity; this is not minimum DAG size when arbitrary let-bindings are allowed. With one chosen cache, a batch proof pays C_empty(a) once for its local let-binding, then pays each cached reference as one. The batch's conjunction has H-1 constructor references. Count discovery cost separately; compare a second metric with deployment DP rule/antecedent scans included. Neither metric is physical inference or kernel time.

## Selection

Each family has eight development roots, 256 distinct deployment roots and an unreachable atom. There are two independent hub chains and each root has a private competing path; the shared/mixed/shifted/null regimes vary which hub appears on deployment routes. All candidate intermediate atoms come from the backward development cone, excluding facts and target atoms. Rule/antecedent visits, proof-reference traversals, candidate scans and a declared sorting proxy contribute to selection cost; common graph index construction and generator work are excluded. A direct arm chooses no cache. Frequency ranks occurrences on direct shortest proof trees. Top4 reranks the four highest by exact development savings. Exhaustive scores all development-cone candidates. The privileged oracle sees deployment targets only to select from that same development menu and pays for its scoring work; its raw references are useful diagnostics, its charged gain is not an attainable policy.

Support discovery initializes one bit per development goal at that goal and propagates the masks backward along every rule. Induction in reverse topological order shows that the mask on an intermediate atom is the union of development goals for which it lies in the backward rule cone. Rank candidates with at least two support bits by H * support_count * (C_empty(a)-1) minus m * C_empty(a), where m=8 and H=256. Support_exact reranks the surviving menu using exact development savings. This rank is a heuristic: alternative paths may never be chosen and a proof tree may use a proposition repeatedly. Reachability is not proof usefulness. Selection sees no deployment outcomes except in the separately labeled privileged arm. Nested horizons use the choice frozen for H=256.

## Fresh-family receipt

The initial exploratory 32-family run used seeds 66000–66031 before adding support discovery. The full benchmark then used 48 fresh families (seeds 67000–67047, 12 per regime), with seven arms and four nested horizons: 1,344 records. No independent third-party sealing. Independent reverse-order relaxation matches topological DP for all compared cost/reachability entries: 563,624 checks. At H=256, total reference-plus-selection gain and gain including deployment DP:

| Regime | Frequency | Support | Support with DP | Exhaustive |
| --- | ---: | ---: | ---: | ---: |
| Shared | 1.5914 | 1.7250 | 1.1892 | 0.3026 |
| Mixed | 1.0380 | 1.1232 | 1.0432 | 0.3072 |
| Shifted | 0.7834 | 0.8139 | 0.9221 | 0.2556 |
| Null | 0.8297 | 0.9001 | 0.9540 | 0.3700 |
| Pooled | 0.9813 | 1.0499 | 1.0189 | 0.3049 |

Support selection produces savings in all 24 shared/mixed families, no shifted/null family; it abstains in all 12 null families but still pays discovery. Pooled direct references 139,811; support references 106,122, selection 26,640, construction 402, total 133,164. Support matches the raw proof references of exhaustive and privileged selection in this planted generator while charging far less. At horizon 128 pooled gain is 0.8708 and only 12 families profit. Shifted families remain a transfer failure; the current method is not a deployment validity guarantee.

## Lean fixture and reproducibility

At H=8, each of six non-privileged arms generates a fresh Lean file per family: 288 isolated batch proofs. Every arm in a family/horizon has identical legal premises, namely the target cone plus the non-privileged candidate-construction cones. All implications and facts are explicit theorem hypotheses; no prior target or theorem imports. A local let represents a proved reusable deduction. The source parser independently type-checks restricted proof terms against the declared hypotheses, confirms the exact conjunction of targets, verifies cache construction before use, and counts references. It rejects admission, self-citation and changed cache-type mutations. Four targeted local tests pass, including deterministic receipt replay. This is a restricted grammar audit, not Lean kernel validation. The long horizon costs are exact DP results, not Lean proofs replayed for all 256 roots.

    python scripts/verify_vad_horn.py --out /tmp/vad06
    python -m pytest -q tests/test_vad_horn.py
    cd lean
    lake env python3 ../scripts/verify_vad_horn.py --out /tmp/vad06_kernel --lean lean

The last command checks zero Lean exit status and no axioms for every batch. Each file runs in a fresh process. The manifest authenticates the emitted files, and the committed summary pins canonical record/summary digests. Local Lean is unavailable. No trained model has run in VAD-06A.

## Advancement

Test prospective transfer validation and repeated-cache selection against support count before learned routing. Require deployment-representative validation roots with explicit cost, independent seeds, rejection accounting and a stronger graph generator with interacting subproofs, repeated antecedents and distractor paths. Then introduce learned policies only against the strongest charged symbolic controller. A learner should optimize amortized utility under valid proof scope; raw proof length or repeated reachability alone is insufficient.
