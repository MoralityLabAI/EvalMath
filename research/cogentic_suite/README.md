# Cogentic-inspired experiments: COG-02, 03, 04, 07 and 08

The suite connects a verified synthetic proof curriculum to trained search policies, an experiment on communication cost, a finite compression certificate and an independent evaluator. The shared task contract makes results across repositories comparable at the level of individual rule applications.

The motivating source is the [Google Research Cogentic papers directory at commit 4a7bc8ab0bc7](https://github.com/google-research/google-research/tree/4a7bc8ab0bc7/cogentic_research_papers). Its themes of persistent lemmas, independently checked progress and orchestrated proof search inform the experiment design. The data used here is generated propositional Horn mathematics. Counts in this suite concern that curriculum.

## Delivered experiments

| ID | Repository and review | Executed work | Main evidence |
|---|---|---|---|
| COG-02 | [DataGoblin PR 77](https://github.com/MoralityLabAI/DataGoblin/pull/77) | Generate a public proof ledger and derive training views | 256 roots, 2,965 teacher attempts, 66,893 checked candidate labels, 256 native Lean teacher proofs |
| COG-03 | [LoopedTransformers PR 394](https://github.com/MoralityLabAI/LoopedTransformers/pull/394) | Train recurrent and one-pass routers, then run controls | Four 5,811-parameter checkpoints, 40,968 evaluation attempts including calibration |
| COG-04 | [BPD PR 152](https://github.com/MoralityLabAI/BPD/pull/152) | Train a scorer and execute quantized factor-message protocols | 23 arms, 46,923 decisions, measured serialized byte counts |
| COG-07 | [Compactification-Theory PR 302](https://github.com/MoralityLabAI/Compactification-Theory/pull/302) | Compress constraints while preserving a fixed finite policy class | Five examples preserve the full version space of 11,836 training rows; independent source audit and Lean supporting theorem |
| COG-08 | This repository | Independently replay attempts and account for useful progress | 29,788 test decisions, full expected-run denominators, 253 successful model trajectories compiled in Lean |

Published producer commits and file hashes are recorded in `sources.json`. Raw COG-02 runs are regenerated outside its repository according to its artifact policy. LoopedTransformers preserves the input snapshot, trained checkpoints and full attempted-action stream. BPD records its trained weights and wire encodings.

## Read the results

The [COG-08 note](../../paper/cogentic_ledger_evaluation.md) describes the verifier and all sixteen arm-by-split results. Its independently replayed summary agrees with the producer. Each test partition has 64 roots and two model seeds. At a 24-call limit, the recurrent router completed 125/128 deeper-world runs and the one-pass comparator completed 122/128. The interval around that difference crosses zero. The reset and shuffled controls show sensitivity to the model's internal computation in this curriculum.

COG-04's rank-four, four-bit transport uses 991.22 mean online bytes per deeper-world root, versus 19,802.39 for the dense float32 identity reference. Completion counts are 57/64 and 55/64, with 1,150 and 1,137 verifier calls. Setup bytes are 722 and 1,682 respectively. The protocol assigns feature production and action scoring to separate endpoints; it measures the resulting wire traffic. A colocated scorer can choose an action locally, so the transport contract is part of the result.

COG-07 measures an exact finite certificate. The full training set has 46 distinct constraints, which use 59 bytes in the same codec. Five constraints fit in a 13-byte packet. Shared symbolic features include goal ancestry, and the known target is a conjunction within the declared class. The report measures the cost of that shared context and includes a 13-bit hypothesis-index baseline.

## Run the independent evaluator

Use Python 3.11 or later. The replay uses the standard library; pytest is required for the test suite. Place the pinned LoopedTransformers checkout beside this repository or adjust the paths below.

```bash
python -c "import gzip,pathlib; pathlib.Path('/tmp/cog02-tasks.jsonl').write_bytes(gzip.decompress(pathlib.Path('../LoopedTransformers/research/cog03_ledger_router/data/tasks.jsonl.gz').read_bytes()))"
python scripts/score_cogentic_ledger.py \
  --tasks /tmp/cog02-tasks.jsonl \
  --attempts ../LoopedTransformers/research/cog03_ledger_router/results/attempts.jsonl.gz \
  --protocol research/cogentic_suite/protocol.json \
  --output /tmp/cog03-independent-replay.json \
  --compare looped:one_pass \
  --compare looped:reset_history \
  --compare looped:reset_inner \
  --compare looped:shuffled_history \
  --compare looped:random \
  --compare looped:ready_first \
  --compare looped:goal_ancestry
python -m pytest -q tests/test_cogentic_ledger.py
python scripts/check_receipts.py --only cogentic_ledger
```

The frozen protocol verifies the decompressed task-file hash, complete registry and expected root counts. The attempts archive includes calibration; the scoring protocol selects the two test partitions and retains the entire registered arm/seed/root product. `output/cogentic_ledger/cog03_independent_replay.json` includes the root-level outcomes, prefix curves, exact ratios and descriptive cluster comparisons.

The native exporter runs after replay and writes its own receipt under `output/cogentic_ledger/model_lean/`. Its CLI lists the source files, selected arm and seeds, budget and Lean executable explicitly. The emitted theorem parameters state the initial facts and allowed rules, so a successful compilation checks the trajectory's concrete proof obligation.

Use an output directory that does not exist yet:

```bash
python scripts/export_cogentic_lean.py \
  --tasks /tmp/cog02-tasks.jsonl \
  --attempts ../LoopedTransformers/research/cog03_ledger_router/results/attempts.jsonl.gz \
  --arm looped --splits ordinary_test ood_test --seeds 17 29 --budget 24 \
  --lean /path/to/lean-4.35.0/bin/lean \
  --out /tmp/cog08-native-replay
```

## How to interpret the costs

One finite verifier call checks one attempted implication. Failed calls and repeated conclusions consume the same unit. COG-02 records 66,893 candidate checks across all four splits, including 11,836 training-split labels. COG-03 separately records 159,724 checks used to build training labels and transitions. The experiment reports these processes independently so their reuse can be accounted for when comparing amortized costs.

Model computation has its own counter. Four shared transformer passes consume more neural work per decision than a one-pass router. Communication bytes in COG-04 count the actual encoded messages, header bytes and two-byte action replies; one-time setup is separate. Batch Lean compiler processes provide a further verification layer after search.

## Evidence limits and follow-up criteria

The generator creates new graph roots within four shared templates. Ordinary depths range from two to five; the deeper partition uses six to nine. This tests transfer across those generated depths. Public seeds and inspected readouts make all reported comparisons development evidence.

The power records retain the `REDESIGN_OR_PILOT_ONLY` gate. A future causal claim needs a new sealed root population, a fixed meaningful effect threshold and matched interventions that separate the proposed mechanism from alternative explanations. The exact finite compression certificate and native proof checks retain their stated scope regardless of the statistical gate.

## Local validation status

The combined ledger and finite-sample tests passed all 28 cases. The 13-check Cogentic receipt regenerated identically, and the complete model-proof cohort passed native replay. The repository's full fast receipt command verified 33 of 34 entries. Its existing DCF-16 verifier requires an external corpus manifest unavailable in this checkout; that verifier's source is unchanged from the base commit. [validation.json](validation.json) records the commands, counts and dependency failure.
