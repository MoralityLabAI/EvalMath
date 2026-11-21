---
name: preferred-evals-experimental-design
description: Select and audit external experiment selection and scientific execution evaluations under EvalMath v2; measure independent roots, pinned harness conditions and judge reliability.
---

# Experiment selection and scientific execution

Use this skill when a proposed gym or model claim concerns measure choices of informative experiments and iterative scientific work under fixed budgets.

**Preferred external benchmarks**

- **TasteVal**: [source](https://arxiv.org/abs/2610.06824). research experiment budget. Access: `tasks_withheld`.
- **PaperBench**: [source](https://openai.com/index/paperbench/). human authored rubrics. Access: `public_framework`.
- **MLE-bench**: [source](https://github.com/openai/mle-bench). kaggle ml engineering. Access: `public_code_data_external_dependencies`.
- **METR time horizon**: [source](https://metr.org/blog/2026-11-20-q4-2026-capability-update/). horizon estimates. Access: `research_and_method`.

**Independent sampling unit:** independent research project or problem, not its many experiment steps.

**Primary readout:** quality-vs-cumulative-compute, achieved replication rubrics, uncertainty on project roots.

**Required comparisons and controls:** fixed Coder or fixed tool capability, equal compute, opportunity-cost ledger, hidden grader. Design a negative control and record all experimental arms, including unsuccessful attempts.

**Pilot:** Run a fixed-Coder researcher planning pilot on one openly specified project with reproducible CPU experiments.

**Claim gate:** Separate experimental taste from coding skill and distinguish serial compute from elapsed time.

## EvalMath procedure

Apply the [common contract](../../v2/README.md) and a pinned `preferred-evals/v2` manifest. State the target population, root IDs, data access/contamination exposure, model and harness hashes, stopping rule, resource floor/ceiling, judge protocol and planned comparison family. Use [FSI-01](../../../paper/finite_sample_inference.md) for paired binary outcomes, clustered by the independent unit, and [EvalMath preflight](../../../skills/evalmath-mechinterp-power/SKILL.md) for mechanistic or causal claims. Test external grader integrity independently; abstain from claiming resolution when tasks cannot be validated locally.

## Papers and methods

See [the annotated reading notes](../../papers/experimental-design.md) and [the research paper index](../../papers/README.md). Papers are conceptual references; they do not grant use of withheld tasks or private grader data.
