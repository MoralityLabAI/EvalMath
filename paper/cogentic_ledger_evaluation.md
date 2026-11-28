# COG-08: verified progress per verifier call

**Evidence level:** finite verified example and observations from trained models on synthetic proof tasks.
**Receipt:** `output/cogentic_ledger/cog08_v1.json`, schema `EvalMath/cog08-audit/v1`, 13 checks.
**Implementation:** `src/spiral_ln/cogentic_ledger.py`.
**Run date:** 2026-11-26.

## Question and result

This evaluator measures whether a proof-search policy completes a registered root within a fixed call budget, and how many useful new facts it obtains along the way. It independently reconstructs the proof state after every action. Every attempted rule application costs one finite verifier call.

The integration run covers 2,048 episodes from eight arms, two training seeds, and 128 source roots across ordinary and deeper test partitions. All 29,788 test-split decisions replayed successfully. The registry contains every expected run, so completed-run and efficiency denominators include all failures. The recurrent router completed 128 of 128 ordinary runs and 125 of 128 deeper runs. Its separately trained one-pass comparator completed 128 and 122 respectively.

Each partition has 64 independent generator roots under the declared sampling assumption. The two seeds repeat those roots. The deeper-partition completion difference is exactly `3/128`, or 2.34375 percentage points. The integration report's root-cluster bootstrap interval is approximately [-3.90625, 9.375] percentage points at its stated settings. The public readout and unverified paired-label exchangeability leave the inferential verdict `inconclusive`. The producer has a separate descriptive interval under its own registration.

## Verifier contract

A world has a finite atom set, initial facts, Horn implications and a goal atom. The public observation contains that world, the accumulated known facts and the attempt history. A rule succeeds when all its premises are known. A successful rule can add one fresh fact; a repeated conclusion receives zero progress credit. Rejected rules remain in the ledger and consume budget.

The verifier validates the world before replay. It compares each submitted observation with the state it reconstructs, checks ordered zero-based attempt indices, and binds task identity, split, budget and receipt values. JSON-level comparisons distinguish Boolean values from integer atom IDs. A producer verdict grants no credit by itself.

The whole supplied task registry is checked before selecting report splits. Duplicate roots, task aliases and exact world aliases are rejected. The protocol pins the registry digest and complete task-file SHA-256, which prevents a caller from shrinking the root denominator while retaining internally consistent logs. These syntactic checks authenticate this registry; independence between generated roots remains a sampling assumption.

The expected run set is the Cartesian product of registered roots, policy arms and training seeds. Missing runs stay in completion denominators. An unsolved run ending before its budget is also detected. When either condition prevents complete cost accounting, the scorer withholds efficiencies using actual spend and retains the explicitly allocated-budget denominator. This closes the incentive to discard failed trajectories before reporting cost.

## Metrics

| Quantity | Definition and interpretation |
|---|---|
| Completion at budget `b` | Registered runs whose independently replayed goal is known by call `b`, divided by every expected run |
| New verified facts | Conclusions first added during an episode; initial facts and repeated conclusions receive zero new-fact credit |
| Goal-ancestor facts | New conclusions in the backward syntactic closure of the goal |
| Goal-ancestor facts per call | Sum of those episode-level additions divided by every charged attempt, when cost accounting is complete |
| Completed runs per call | Solved run count divided by charged attempts; training-seed repeats remain repeated runs |
| Completed runs per allocated call | Solved count divided by expected runs times the registered maximum budget |
| Coverage | Missing runs, early unsolved runs and independent root count reported alongside scores |

Structural ancestry includes alternative proof paths. It supplies an exact graph-based proxy for relevance in the declared worlds. Some ancestral facts can be unnecessary for a particular shortest proof. This metric therefore measures syntactic progress. The primary outcome remains completion of the registered goal.

Fact deduplication operates within each episode. Repeated model seeds have separate ledgers and separate costs. Root-cluster analysis groups their outcomes for uncertainty estimates.

## Independently replayed results

All arms receive a maximum of 24 finite verifier calls per run. Each cell below includes 64 roots evaluated with both training seeds.

| Arm | Ordinary completed / 128 | Ordinary calls | Deeper completed / 128 | Deeper calls |
|---|---:|---:|---:|---:|
| Looped transformer | 128 | 954 | 125 | 1,927 |
| One-pass transformer | 128 | 1,072 | 122 | 2,072 |
| Reset carried history | 123 | 1,016 | 87 | 2,189 |
| Reset inner loop | 128 | 1,316 | 101 | 2,266 |
| Shuffled history | 123 | 1,158 | 70 | 2,423 |
| Random | 16 | 2,997 | 0 | 3,072 |
| Ready-first rule | 126 | 1,738 | 50 | 2,690 |
| Symbolic goal ancestry | 128 | 974 | 128 | 1,924 |

The symbolic arm uses the known graph structure and supplies a reference policy. The learned policy uses four shared transformer passes and a carried state; the one-pass policy uses one pass at the same parameter count. Their neural computation differs. Call savings describe the cost of the verifier and need a separate compute budget when assessing deployment cost.

The recurrent arm uses 2,881 calls over both test partitions. Independent replay finds 2,819 fresh facts, 62 rejected calls, zero repeated facts and zero post-solution calls. The final Lean export retains the full 256-run cohort, including the three unsuccessful deeper-world runs. Successful trajectories yield 253 proof terms checked by Lean 4.35.0 with empty axiom lists. A deliberately wrong proof term is rejected.

## Native Lean boundary

`scripts/export_cogentic_lean.py` first runs the independent finite verifier, then constructs a theorem for each successful trajectory. Atom propositions, initial proofs and rule implications are explicit theorem parameters. Each newly accepted conclusion is obtained by applying the corresponding rule to already available proofs. This checks that the recorded sequence proves its Horn goal under the task's premises.

The exporter binds input files and both source modules by SHA-256 and checks that they remain stable during execution. Its index includes all expected episodes, so the native success count can be reconciled with the unsolved runs. Lean compilation and the rejected sentinel have separate process counts from finite rule checks. The 24-call search budget concerns finite verifier invocations; the batch compilation happens afterward.

## Evidence and exposure

The corpus comes from COG-02's deterministic synthetic proof-world generator. It contains four families with train, calibration, ordinary and deeper partitions. Structural family templates are shared. Atoms and rule order are randomized within roots, and all presentations of a root stay in one split. Public seeds allow exact reproduction.

The COG-03 architecture and training registration preceded its full rollout, while this independent integration audit followed the producer's results. The COG-08 protocol records that timing. The source registry and task hash were bound during integration hardening. Its paired analysis reports fourteen comparisons and uses the existing finite-sample engine with exchangeability unattested and the readout marked public. The producer's ten-point meaningful effect threshold remains the research planning target; the integration engine's five-point default supplies an additional descriptive gate, which also stays closed.

The retrospective planning record is under `research/cogentic_suite/preflight/`. Calibration roots supply the inputs. A shuffled-history intervention measures sensitivity to disrupting state; a future causal study needs a physically matched sham and fresh sealed roots. Training-seed repeats and thousands of within-world actions do not increase the number of independent task roots.

## Verification and source provenance

Fourteen focused tests cover exact costs, duplicate and irrelevant facts, invalid or forged receipts, missing and truncated runs, root aliases, denominator attacks and task-registry binding. The registered 13-check receipt records source hashes and regenerates identically. The integration report records hashes for the task file, attempts archive, protocol, independent verifier, scorer and finite-sample engine.

The source tasks are pinned to DataGoblin commit `ae0dbecffc1d246778ee47d8f3d8ec59b5948f2b`, with task-file SHA-256 `aef151e3f7de099e9b5d7b51c92ad94aa3bab20a85b4f73b8f4fb5ac8ce7905a`. Attempts come from LoopedTransformers commit `c1c903b3f0664ee19838fcba45bd67e24f779aab`, with archive SHA-256 `9b3a0412bdc683b95bc6bcf6a843801f947c288f23e9f32dfa354accd8c0f461`.

See [the suite guide](../research/cogentic_suite/README.md) for commands, linked experiments and the complete evidence map.
