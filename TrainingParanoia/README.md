# TrainingParanoia

Mathematics for evaluations that influence later training or behavior.
The [research note](evaluation_noninterference_plan.md) records the motivating
question and the proof contract for this sequence.

| Result | Question | Canonical note | Reproduction |
|---|---|---|---|
| RHT-26 | How do artifacts and updates carry effects across episodes? | [Carryover](RHT-26/carryover.md), [development bridge](RHT-26/development_bridge.md), [historical protocol](RHT-26/protocol.md) | `python scripts/check_receipts.py --only reward_carryover reward_carryover_count` |
| RHT-27 | Which transcript differences can influence the next declared state beyond permitted feedback? | [Evaluation noninterference](RHT-27/evaluation_noninterference.md) | `python scripts/check_receipts.py --only noninterference` |
| RHT-28 | How do local discrepancies propagate through a sequence, including the recorded history? | [Contamination composition](RHT-28/contamination_composition.md) | `python scripts/check_receipts.py --only contamination_composition` |

Code stays in `src/spiral_ln`, with independent tests under `tests`, deterministic
verifiers under `scripts`, and source-bound receipts under `output`. Links at the
old paper and protocol paths keep the existing repository entry points usable.
The dedicated `training-paranoia` workflow runs on ordinary GitHub CPU runners;
the repository's `verify` workflow also builds the Lean project and checks axioms.

Every numerical fixture here uses a declared finite law. The Control-Harness
pilot is archived development evidence, with its limits recorded in RHT-26.
Neural confirmation requires its own prospectively frozen protocol and preflight.

## Following work

RHT-29 is the proposed useful-feedback frontier: choose a feedback interface
that preserves a registered amount of learning while controlling downstream
risk. FSI-02 is proposed work on statistical validity when evaluation and
selection adapt across generations. Neither is implemented by this change.
