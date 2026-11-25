# MIT-14 DataGoblin export

`datagoblin_export.py` writes JSONL rows `{"record": ..., "payload": ...}`.

* `record`: DataGoblin `DataCollectionRecord`, schema 1.0 (`DataGoblin/schemas/data_collection_record.schema.json`, `src/datagoblin/data_etiquette/records.py`). DataGoblin's etiquette pipeline reads `row["record"]`. The exporter validates every record with `DataCollectionRecord.from_jsonable` when `--validate <DataGoblin checkout>` is given (1,038 synthetic records validated, 2026-11-25, DataGoblin 5a16d9d).
* `payload`: the training content. Its canonical JSON (sorted keys, compact separators) is hashed into `record.content_sha256` and `record.verification_subject_sha256`.

## Files

| File | Origin | `model_generated` | Uses |
|---|---|---|---|
| `synthetic_oracle.jsonl` | proof fixtures with symbolic verifier receipts (MIT-06), exact teacher action values and refinement traces (MIT-09 roots), counterexample witnesses (MIT-10) | false | TRAINING, EVALUATION |
| `model_traces.jsonl` | local-model responses on MIT-13 development rows with independent verifier outcomes | true | EVALUATION only (`evaluation_material = true`) |

Reasoning text from models is not exported (`contains_hidden_reasoning = false`; only its character count). No confirmation data exists; `record()` refuses `confirmation` and `sealed` splits.

## Splits

`intended_split` is assigned per root (`dedup_group = root_id`): `train` or `dev` by SHA-256 of the root id (80/20); MIT-13 rows are `evaluation_dev`. All rows of one root share one split.

## Schema extensions (not in DataGoblin)

1. The `payload` object, schema `evalmath.mit.training_record.v1`. Fields by `kind`:
   * all: `schema`, `kind`, `root_id`, `family`, `verifier_receipt`, `provenance` (generator, seed, source SHA-256 map or checkpoint).
   * `proof_fixture`: `variant`, `arm`, `source_theorem`, `instrument`, `prerequisites`, `target_theorem`, `target_instance`, `applicability_label`, `candidate_mapping`, `counterexample`, `teacher_response`, `rejected_candidates`, `certificate`, `compute_cost.symbolic_checks`.
   * `teacher_action_values`: `environment` (exact rationals as strings), `states[]` (posterior, masks, budget, `action_values`, `teacher_action`, `rejected`, `regret`), `optimum`, `precision_refinement_trace`, `certificate` (η, global and decision bounds), `compute_cost` (refinement cost, memory bits, solver states).
   * `counterexample`: `counterexample` (full witness), `applicability_label`, `rejected_candidates` (the unsafe rules refuted).
   * `model_trace`: `variant`, `arm`, `target_prompt_sha256`, `final_response`, `attempts`, `reasoning_chars`, `closure`, `applicability_correct`, `status`, `compute_cost` (tokens in/out, wall ms).
2. `public_metadata` carries `payload_schema`, `family`, `arm`, `variant`, `origin` (`synthetic_oracle` or `model_trace`), `states`. None of DataGoblin's forbidden public keys are used.
3. `provenance_refs` carries `github.com/MoralityLabAI/EvalMath` and `payload_schema:evalmath.mit.training_record.v1` (no filesystem paths).

## Run

```
cd gyms/MathematicalInstrumentTransfer
python datagoblin_export.py --output export --validate ../../../DataGoblin [--mit13 RUN_DIR ...]
```
