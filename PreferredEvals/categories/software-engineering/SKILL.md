---
name: preferred-evals-software-engineering
description: Select and audit external repository repair and terminal engineering evaluations under EvalMath v2; measure independent roots, pinned harness conditions and judge reliability.
---

# Repository repair and terminal engineering

Use this skill when a proposed gym or model claim concerns use real issues and graded artifacts under a documented harness, including a gold-patch sanity check.

**Preferred external benchmarks**

- **SWE-bench Verified**: [source](https://evals.openai.com/). stale or contamination sensitive. Access: `public_data`.
- **SWE-bench Pro**: [source](https://openai.com/index/separating-signal-from-noise-coding-evaluations/). known task quality problems. Access: `public_subset_review_required`.
- **SWE-bench Pro Verified**: [source](https://arxiv.org/abs/2609.08149). proposed audited variant. Access: `paper_verify_suite_before_use`.
- **DeepSWE**: [source](https://github.com/thinking-machines-lab/inkling-verify). fresh container patch tests. Access: `public_scripts_images_required`.
- **Terminal-Bench 2**: [source](https://www.anthropic.com/research/infrastructure-noise). resource sensitive. Access: `public_tasks_container_required`.
- **SWE-Lancer**: [source](https://evals.openai.com/). end to end contracts. Access: `benchmark_subset_and_paper`.

**Independent sampling unit:** repository issue/task, with repeated model attempts clustered by issue.

**Primary readout:** valid-instance resolved and all-assigned resolved, patch application, infrastructure failure.

**Required comparisons and controls:** gold patch succeeds, patch applies, offline tests, resource floor/ceiling, network status. Design a negative control and record all experimental arms, including unsuccessful attempts.

**Pilot:** Re-score MCP-03's 26 tasks with the 21 valid local gold patches, then add independently audited tasks from new repositories.

**Claim gate:** SWE-bench Pro task reliability is contested; audit prompts, tests and gold before headline comparisons.

## EvalMath procedure

Apply the [common contract](../../v2/README.md) and a pinned `preferred-evals/v2` manifest. State the target population, root IDs, data access/contamination exposure, model and harness hashes, stopping rule, resource floor/ceiling, judge protocol and planned comparison family. Use [FSI-01](../../../paper/finite_sample_inference.md) for paired binary outcomes, clustered by the independent unit, and [EvalMath preflight](../../../skills/evalmath-mechinterp-power/SKILL.md) for mechanistic or causal claims. Test external grader integrity independently; abstain from claiming resolution when tasks cannot be validated locally.

## Papers and methods

See [the annotated reading notes](../../papers/software-engineering.md) and [the research paper index](../../papers/README.md). Papers are conceptual references; they do not grant use of withheld tasks or private grader data.
