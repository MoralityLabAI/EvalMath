# PreferredEvals v2: portable experiment contract

**Decision:** implement a small independent `PreferredEvals` manifest/receipt contract, with adapters to existing harnesses, instead of forking the Prime Intellect Verifiers library. As of November 2026 the upstream documented API is `verifiers.v1` (Taskset + Harness + Agent + Trace), and `vf-eval` with `config.toml` is the natural execution path.

## Boundaries

- **Experiment definition:** EvalMath's \(\langle G,\Pi,D,Z,J,\mathcal A,C\rangle\) maps game, controller, assignment, evidence, judge, aggregation and claim into explicit versioned fields.
- **Runner:** Prime v1, Inkling Verify, SWE-bench or custom task runner supplies actual trajectories. This package does not reimplement those simulators.
- **Judgment:** prefer exact tests, reference outputs, Lean kernels, sandbox checks or adjudicated professional work. Treat LLM-judge measurements as a separate instrument subject to calibration.
- **Statistics:** FSI-01 uses independent root clusters, protected held-out sampling, registered multiplicity and meaningful effect floors. Repetitions and loop counts remain nested.
- **Resource validity:** record process-floor versus hard ceiling, CPU/RAM, GPU, timeouts, network permissions, model version, scaffold and generation budget. Infrastructure failures and invalid gold tests are separate cells.
- **Data governance:** do not copy restricted evaluation items into the repo; store only public metadata and owned synthetic fixtures.

## V2 validation

```sh
python PreferredEvals/v2/manifest.py --catalog PreferredEvals/v2/catalog.json
python PreferredEvals/v2/manifest.py --manifest PreferredEvals/v2/examples/development.json
python -m unittest discover -s PreferredEvals/v2/tests -p 'test_*.py' -v
```

The CLI lints a *plan*. A valid manifest means its structure is coherent, never that a benchmark passed or a causal claim was confirmed. Any "confirmation ready" label means only that preregistration and sealing assertions are present; these author assertions need external review.

## Adapter policy

Prime v1 tasksets and traces remain native upstream. As of Verifiers 0.4.1, the local runner is `vf-run`, while the full evaluator is in `prime-rl`; archived `vf-eval` recipes require their original version. Store `TaskData.id/key/hash`, installed taskset version, harness ID/version, runtime type, environment and agent configurations, model sampling, error codes and `ModelCall` usage. With the pinned 0.4.1 CLI, use `vf-run --dry-run` before model evaluation; older `vf-eval @ config.toml --dry-run` belongs to prior releases. Preserve `traces.jsonl`; never replay an errored rollout as an independent new task. Maintain a strict v1 converter for archived summaries, rather than silently guessing trace schema.

For other frameworks, create ingestion adapters behind the same evidence contract. If a task requires a paid sandbox, missing API judge, or private TasteVal item, record that limitation and choose a public alternative for development.

## Priority gates

A proposed "new Verifiers v2 set" is warranted for **missing scientific controls**, not replacement infrastructure: research taste with human paired judgments, progressive experimental design with equal fixed Coder, causal intervention transfer, model self-monitorability and graded artifact repair. Each custom set needs benchmark-independent task roots, available gold verifier, human adjudication for subjective labels, contamination audit and reusable external comparator.

See [catalog](catalog.json), [skills](../README.md) and [papers](../papers/README.md).

## Connected rollout execution

Use [the runnable gym](../gym/README.md) for local model endpoints and [execution coverage](../gym/STATUS.md) for current adapter boundaries. Native profiles do not install dependencies, obtain private data, or score with an alternative judge. Prompt tasks keep label files separate; pairwise position swaps and samples inherit the task's independent root. The `compare.py` bridge exports unsealed development cases for EvalMath FSI-01, with multiple attempts nested under roots.
