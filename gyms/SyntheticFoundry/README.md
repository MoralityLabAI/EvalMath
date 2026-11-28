# ESF-01: EvalMath Synthetic Foundry

**Objective:** Get a source-grounded Fable referee review of the whole EvalMath mathematical program and use its research decisions to identify repairs, missing assumptions, adversarial cases, and independently executable synthetic curricula for DataGoblin and recurrent models.

## Scientific loop

1. Freeze the EvalMath git revision and inventory its papers, research/experiment notes, gyms, skills, Lean claim index, mathematical sources, tests and receipt verifiers. A local DataGoblin checkout contributes its 100-root research catalog and GoblinWorld atlas.
2. Build six parallel review packets with source paths, exact hashes and distributed excerpts: feedback and selection; filtration and leakage; proof fidelity and reliability; mechanisms and recurrent representations; recursive evaluation and games; remaining frontier mathematics.
3. Each Fable reviewer supplies mathematical critique, ranked repairs, candidate data generators, a pre-action rationale, predicted results, and a bounded action chosen from the registered generator/profile menu.
4. Freeze the response and execute the selected independent CPU generator, checking its exact gold with native, analytic or exhaustive reference calculations as applicable. Return the actual observation for a second research round.
5. Synthesize the reviews into a single program-level referee report and ranked implementation plan. New generator proposals require independent implementation, validation and permissions review. No model-authored executable code is run.

The initial executable corpus comprises 16 distinct families:

| Family | Exact task |
| --- | --- |
| judge | Conditional judge error and observed-score ceiling |
| cpf | Joint false-authorization bounds and conditional audit contraction |
| adaptive_cpf | Adaptive versus fixed certified-rejection auditing |
| audit | Binary authorization-audit value |
| disclosure | One-hot interval identification and adaptive/fixed separation |
| selection | Post-selection risk from a public transcript |
| adaptive_risk | Adaptive two-round query trees and exhaustive policy check |
| covert | Bounded hidden-message event coverage |
| capacity | Integer capacity-sensitive margin collisions |
| patch | Minimum expected patches to the next hit |
| reuse | Independent null running-maximum inflation |
| bpd | Routed intervention separation and minimum identifying probe cost |
| paired | Indistinguishable paired worlds and Brier loss |
| revocation | Optimal capacity-constrained provenance memory |
| filtration | Private signal arrival-order effect |
| private_stopping | Pre-peek inflation of a public martingale |

Each has baseline, boundary and structural-shift profiles; structural shifts are family-specific and are not uniformly new mathematical mechanisms. This is a starting executable subset, not a claim to implement every theorem in the repository.

## Offline commands

Run from the EvalMath checkout with its normal Python environment. The new module is under src/spiral_ln.

```bash
python -m pytest tests/test_evaluation_synthetic_foundry.py -q
python scripts/run_evalmath_synthetic_foundry.py generate --count 32 --profile baseline --split discovery --out runs/esf01/baseline
python scripts/run_evalmath_synthetic_foundry.py generate --count 16 --profile structural_shift --split development --out runs/esf01/dev_shift
python scripts/run_evalmath_synthetic_foundry.py prepare --datagoblin /path/to/DataGoblin --out runs/esf01/review
```

Use an installed EvalMath package or set PYTHONPATH=src. Count is a target per family; small finite families may exhaust their unique inputs. Inspect actual family counts. Task IDs hash the family and canonical problem specification. The discovery/development assignment is based on this identity, not on the random seed. It prevents exact input overlap; it does not establish family-disjoint or private confirmation.

The task pack contains tasks.jsonl, evaluator_gold.jsonl, and a hash manifest. Keep gold outside actor-facing paths and score predictions with:

```bash
python scripts/run_evalmath_synthetic_foundry.py score --pack runs/esf01/dev_shift --predictions predictions.jsonl --out runs/esf01/score.json
```

Each prediction contains task_id and an answer object. Missing rows remain in the denominator. The baseline tasks come from source-grounded independently authored generators, with no teacher-generated content. Training admission remains pending corpus review.

## Fable campaign

Use the existing DataGoblin environment and shared campaign ledger. Add its src directory to PYTHONPATH alongside EvalMath's src. The existing budget and batch modules supply authentication, reservations and receipts. Do not initialize a new ledger, and do not run this campaign concurrently with other ledger writers.

The offline preparation writes requests.json, the full source inventory and the per-panel packets. Source excerpts are bounded, so the review is a program-wide triage and mathematical assessment of selected sections rather than exhaustive verification of every proof. Inspect coverage, missing excerpts, and permissions before submission. If a claim requires complete context, obtain the full source in a separate approved packet.

```bash
python scripts/run_evalmath_synthetic_foundry.py preflight --requests runs/esf01/review/requests.json --ledger /path/to/existing/ledger.json
python scripts/run_evalmath_synthetic_foundry.py submit --requests runs/esf01/review/requests.json --ledger /path/to/existing/ledger.json --approved-sha <reviewed_request_sha256> --max-new-usd <approved_wave_cap> --confirm-paid --out runs/esf01/wave1
python scripts/run_evalmath_synthetic_foundry.py collect --ledger /path/to/existing/ledger.json --batch-id <batch_id> --out runs/esf01/wave1
python scripts/run_evalmath_synthetic_foundry.py continue --requests runs/esf01/review/requests.json --results <collected_results_json> --out runs/esf01/round2
```

Review and preflight round2/followup_requests.json, then submit it using the same command. Use synthesize with the collected result files from both waves for a final, separately preflighted review. Reconcile all actual charges before each wave. Preserve the campaign safety reserve; estimated maximum reservations are not guaranteed provider-side spending limits. Failed or truncated responses are preserved, without invented scientific content.

All Fable requests and responses are research-only, not eligible for training. Keep paid results in local research custody. Independently generated task packs are separately reviewed; no Fable response or proxy is exported as training data. Do not send private confirmation roots, secrets or raw private data to the provider. No GPU allocations or live Aleph training changes.

## Status

Implementation and regression tests are committed on a draft branch. The local pytest run, full packet preparation, exact corpus production, and paid review are execution steps for the operator's environment. This branch does not assert that these have already completed.
