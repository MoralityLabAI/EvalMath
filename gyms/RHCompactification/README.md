# RH compactification Lean gym

This gym provides a twenty-task Lean proof-revision curriculum and a twelve-task
candidate pack for the pinned Plastic Proof Transformer (PPT) trainer. The
curriculum follows finite recurrence prefixes through extension, overlap,
gluing, and denominator construction, then develops a joint numerator and
denominator recurrence.

The [Lean module](../../lean/FeedbackChannel/RHCompactification.lean) contains
fourteen definitions and thirty-six theorems. It imports `Init`. Each full-proof
task receives the source declarations that precede its target. A submitted
proof is compiled in that environment, followed by an axiom audit of the target.

All tasks and teacher solutions are public training and development material.
They belong to **one recurrence family**. The current preflight
verdict is **`REDESIGN_OR_PILOT_ONLY`**.

## Checked artifacts

| Artifact | Contents |
| --- | --- |
| [curriculum.json](curriculum.json) | Source hashes, task count, split, and context-cost policy |
| [tasks.jsonl](tasks.jsonl) | Twenty theorem statements with their preceding Lean source |
| [teachers.jsonl](teachers.jsonl) | Public teacher proof bodies |
| [microsteps.json](microsteps.json) | Twelve actual Lean states, candidate fragments, and verification metadata |
| [microstep_sources](microstep_sources) | Complete theorem templates with one fragment hole |
| [pack/manifest.json](pack/manifest.json) | Native candidate-pack hashes and compiler provenance |
| [pack/train.jsonl](pack/train.jsonl) | Public bounded inputs and twenty-four candidate tactics |
| [pack/train.receipts.jsonl](pack/train.receipts.jsonl) | Candidate outcomes bound to the complete compiled source |
| [native_receipt.json](native_receipt.json) | Fresh Lean checks of the module, teachers, candidate pack, and rejection controls |
| [trainer_contract.json](trainer_contract.json) | Exact upstream commits, imported-file pins, schemas, and model limits |
| [adapter_receipt.json](adapter_receipt.json) | Execution of both pinned upstream data loaders |
| [training_smoke.json](training_smoke.json) | The completed PPT optimizer smoke run and its restricted evidence scope |
| [training_steps.jsonl](training_steps.jsonl) | Thirty-two recorded optimizer updates |

The recorded local suite passed all thirty-six theorem axiom audits, all twenty
full teacher proofs, twenty-four candidate checks, and twelve local-state
replays. Its three rejection controls also passed. The local compiler was Lean
**4.35.0**. The committed receipt records that compiler.

The [pinned Lean 4.34.1 CI run](https://github.com/MoralityLabAI/EvalMath/actions/runs/45652582316)
passed the complete native suite and all **54 gym tests** at implementation commit
`1ac0cad25bd2b087a5d465a0b7e407c7b0d6403d`. It also regenerated the structural
receipt identically. The full local fast-receipt command reproduced **32 of 32**
registered receipts.

## Full-proof revision service

Run these commands from the EvalMath repository root:

```bash
PYTHONPATH=src python -m spiral_ln.rh_compactification_gym build
PYTHONPATH=src python -m spiral_ln.rh_compactification_gym check
PYTHONPATH=src python -m spiral_ln.rh_compactification_gym verify \
  --lean-cmd "lake env lean"
```

`build` extracts the marked declarations from the Lean source. `check` compares
the stored task and teacher files with that extraction and checks their hashes.
`verify` starts a fresh Lean process for each teacher proof.

The service reads one JSON object per input line and returns one JSON object per
response. This example attempts an invalid proof, then supplies the public
teacher proof for the first task:

```bash
PYTHONPATH=src python -m spiral_ln.rh_compactification_gym serve \
  --lean-cmd "lake env lean" --max-attempts 4 <<'JSON'
{"op":"reset","id":"RHCG-001"}
{"op":"step","proof":"rfl"}
{"op":"step","proof":"have hne : i ≠ bound + 1 := Nat.ne_of_lt (Nat.lt_succ_of_le hi)\nsimp [extend, hne]"}
{"op":"close"}
JSON
```

`reset` selects a task and clears the episode history. Each `step` consumes an
attempt. The returned observation includes the task, remaining budget, most
recent checker feedback, and best verified proof. Surface rejection consumes an
attempt without launching Lean. A timeout or resource failure has an unknown
label and earns zero reward.

The default episode permits four attempts; `--max-attempts` accepts values from
one through thirty-two. The checker uses a twenty-second timeout by default,
768 MiB of memory, and 400,000 heartbeats. It rejects admissions, added axioms,
`native_decide`, executable elaborator tactics, command injection, and references
to the completed target or later declarations. Accepted axioms are limited to
Lean's standard `propext`, `Classical.choice`, and `Quot.sound`.

Reward follows verified progress. If the reference source has `R` UTF-8 bytes and
the best accepted complete source has `B` bytes, the episode potential is
`1 + max(0, (R - B) / R)`. It is zero before a proof passes. A step earns the
increase in potential. Repeated proofs and longer accepted proofs earn no
additional reward.

**The byte charge includes the whole supplied Lean source**, including preceding
declarations and the target axiom-audit command. A shorter proof body can reuse
an earlier theorem, and that theorem's supplied source remains charged.

Batch submissions use JSONL rows with `id` and `proof` fields:

```bash
PYTHONPATH=src python -m spiral_ln.rh_compactification_gym grade \
  --lean-cmd "lake env lean" \
  --submissions gyms/RHCompactification/teachers.jsonl \
  --output /tmp/rhcg-teacher-grade.json
```

## Bounded native microsteps

The PPT encoder accepts at most 384 UTF-8 bytes for a goal and 384 for a candidate.
Its upstream encoder keeps the suffix of an oversized input. The adapter checks
the complete input length and rejects truncation.

The twelve microsteps use complete `trace_state` output from a successful Lean
harness. Their exact model inputs have this format:

```text
<STATEMENT> Prove this goal.
<GOALS> actual Lean local context and goal
```

The combined headers and local state occupy **136–237 bytes**. Candidate tactics
occupy **3–95 bytes**. The selected steps cover prefix extension and restriction,
overlap agreement, gluing, denominator bridges, and joint recurrence uniqueness.

Each source template contains one `__RHGYM_FRAGMENT__` hole. The generator checks
the gold fragment and a mutated fragment by compiling the complete theorem.
All twelve gold fragments passed; all twelve mutations were rejected. Context
compaction, where used, consists of actual Lean projection and `clear` steps in
the surrounding teacher proof. The resulting local state is captured directly
by `trace_state`.

To regenerate these states with the `lean` executable on your path:

```bash
ELAN_TOOLCHAIN="$(cat lean/lean-toolchain)" \
  python gyms/RHCompactification/microsteps.py --lean lean
PYTHONPATH=src python -m spiral_ln.rh_compactification_pack build --lean-cmd lean
PYTHONPATH=src python -m spiral_ln.rh_compactification_pack check
PYTHONPATH=src python -m spiral_ln.rh_compactification_pack verify --lean-cmd lean
```

The pack stores full source templates separately from the bounded model input.
Its public rows contain tactic text, lemma names, and source identities. Separate
receipt rows contain acceptance labels and diagnostics. Candidate IDs derive from
the tactic and an epoch that includes the source template, public goal, and
compiler environment. Candidate order follows those IDs.

`check` validates the pack against its source-derived task specifications and
recorded candidate oracle. `verify` reruns Lean and the local-state trace for
every task. Changes to a goal, candidate, template, or checker invalidate the
corresponding source binding.

The combined native suite is available as:

```bash
PYTHONPATH=src python scripts/verify_rh_compactification_native.py --lean-cmd lean
```

For a deliberate replay with the locally recorded Lean 4.35.0 compiler, append
`--allow-toolchain-mismatch` to the pack and native-suite commands. The compiler
version remains part of each receipt. The full repository build uses:

```bash
cd lean
lake exe cache get
lake build
lake env lean axioms_check.lean
cd ..
```

## DataGoblin and PPT integration

The [trainer contract](trainer_contract.json) pins the actual imported files at
these commits:

| Repository | Commit | Loader |
| --- | --- | --- |
| `MoralityLabAI/DataGoblin` | `48c99a7d9c2d37c82fe127369dfa0124b88bc8ab` | `datagoblin.training_gym.rlt_pretrain_data.lean_rows` |
| `MoralityLabAI/LoopedTransformers` | `8931f9d9cf0b064cea5cb3ad0760fe2dcd5197fa` | `ppt_gym.data.load_checked_pack` |

The example below assumes these source checkouts sit beside EvalMath. Set
`DG_ROOT` and `LOOPED_ROOT` to the corresponding existing checkout directories.
The adapter verifies each imported file against the contract before executing
the unchanged upstream loaders.

```bash
RHCG_REPO="$(pwd)"
DG_ROOT="$(cd ../DataGoblin && pwd)"
LOOPED_ROOT="$(cd ../LoopedTransformers && pwd)"

PYTHONPATH=src python scripts/check_rh_compactification_datagoblin.py \
  --pack "$RHCG_REPO/gyms/RHCompactification/pack" \
  --datagoblin-root "$DG_ROOT" \
  --looped-transformers-root "$LOOPED_ROOT" \
  --out "$RHCG_REPO/gyms/RHCompactification/adapter_receipt.json"
```

The recorded run used source snapshots at
`/tmp/rh-pl17/contract-checkouts/DataGoblin` and
`/tmp/rh-pl17/contract-checkouts/LoopedTransformers`. Both loaders accepted all
twelve tasks and twenty-four candidate labels, with zero truncated inputs.
The adapter performs receipt and loader checks; fresh Lean execution occurs in
the gym's native verifier.

With PyTorch available in the chosen Python environment, this command reproduces
the small training configuration. `--pack` receives an absolute path, and the
output directory must be new:

```bash
RHCG_REPO="$(pwd)"
RHCG_PACK="$RHCG_REPO/gyms/RHCompactification/pack"
RHCG_OUT="$RHCG_REPO/output/rh_compactification_ppt_smoke"

cd "$LOOPED_ROOT/research/lean_cgrt_hrm400"
python -m ppt_gym train \
  --pack "$RHCG_PACK" --plan a --out "$RHCG_OUT" \
  --width 32 --heads 4 --max-bytes 384 --depths 1 2 \
  --steps 32 --threads 1 --max-seconds 60
cd "$RHCG_REPO"
```

The recorded CPU run completed **32 optimizer updates** in **0.394 seconds** on
the twelve public cases. Its model has 25,571 parameters, width 32, four attention
heads, and eight workspace slots. Training sampled recurrence depths one and
two with the upstream default seed 17. The run confirms that the checked pack
reaches the recurrent ranker and supports optimizer updates. It produced no
held-out score or comparative model-effect estimate.

The [smoke wrapper](training_smoke.json) preserves the upstream manifest and
applies the repository's pilot-only evidence scope. The upstream loader derives
its own `scientific_eligible` flag from the receipt class; this gym's wrapper
records `scientific_eligible: false` for the present single-family run.

PPT recurrence depth controls repeated model computation during candidate
ranking. The full-proof service charges a separate verifier call when a policy
submits another proof. These budgets are recorded independently. The contract
also lists the additional datasets and independent lineages required by the
upstream mixed-pretraining interface.

## Research readiness and mathematical scope

The [preflight report](preflight_report.json) retains
`REDESIGN_OR_PILOT_ONLY`. Its calibration replayed four prerequisite certificates
twice and grouped them as one construction family. Those repeatability results
measure the instrument. The subsequent optimizer smoke run checks trainer
execution.

| Planning field | Current record |
| --- | --- |
| Independent unit | Shared recurrence construction family; one unit |
| Exposed cases | Twenty full-proof tasks and twelve microsteps with twenty-four candidates |
| Proposed primary contrast | Paired Lean-certified completion under recurrent and one-pass policies with equal verifier-call budgets |
| Proposed physical dose | Loop counts one and four, with fixed source exposure and output-token limits |
| Scientific variation floor | 0.1 completion-fraction difference |
| Matched-sham calibration | Neural sham floor remains uncalibrated; repeated certificate outcomes were identical |
| Comparisons | Two planned comparisons; the completed smoke run makes no comparative claim |
| Resolution and power | Unestablished from one independent family |
| Readout exposure | Current tasks and teacher solutions are public; confirmation families remain unallocated |
| Future controls | Matched-compute feedforward policy and matched sham intervention |

Reproduce the strict preflight with:

```bash
python scripts/prepare_rh_compactification_preflight.py
```

The expected exit status is **2**, after the observations, pilot input, and report
have been written. The configured 128 future confirmation units are a planning
input; no such confirmation set has been allocated or scored.

The Lean module proves a mathematical analogue over `Nat` and total functions.
It includes finite-prefix agreement and recurrence uniqueness, along with the
kernel-reduced examples `denominator Nat.mul 1 6 = 720` and
`joint Nat.mul Nat.add 0 1 6 = (1764, 720)`. The general operation arguments carry
no multiplication or addition laws.

The custom Hilbert proofs in [research/rh_pl01](../../research/rh_pl01) retain
their own set-theoretic targets and unary/compact serialization metrics. The
Lean curriculum does not supply a translation between these calculi. The frozen
RH target remains unproved.
