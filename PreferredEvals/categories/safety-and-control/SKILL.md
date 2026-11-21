---
name: preferred-evals-safety-and-control
description: Select and audit external behavioral safety and monitorability evaluations under EvalMath v2; measure independent roots, pinned harness conditions and judge reliability.
---

# Behavioral safety and monitorability

Use this skill when a proposed gym or model claim concerns distinguish measured behavior under controlled elicitation from speculative claims of model intent.

**Preferred external benchmarks**

- **TASTE**: [source](https://alignment.anthropic.com/2026/taste/). expert labeled pairwise. Access: `research_protocol`.
- **Bloom**: [source](https://alignment.anthropic.com/2025/bloom-auto-evals/). seeded behavioral suites. Access: `open_framework`.
- **Petri 2.0**: [source](https://alignment.anthropic.com/2026/petri-v2/). multi turn behavioral audit. Access: `open_framework`.
- **LinuxArena**: [source](https://thinkingmachines.ai/news/inkling-2-mini/). attack detection in agentic work. Access: `source_requires_harness_review`.

**Independent sampling unit:** independent behavioral seed/scenario, with rollouts nested inside.

**Primary readout:** behavior incidence, successful side task with detection, calibrated judge agreement.

**Required comparisons and controls:** matched benign/harmful scenarios, fixed auditor, human-validated judge, false-positive threshold. Design a negative control and record all experimental arms, including unsuccessful attempts.

**Pilot:** Use Bloom or Petri seeds to audit a narrow predeclared behavior with independent transcript review and safe synthetic tools.

**Claim gate:** Simulated tool scenarios provide behavioral evidence, not proof of hidden model intent or real-world capability.

## EvalMath procedure

Apply the [common contract](../../v2/README.md) and a pinned `preferred-evals/v2` manifest. State the target population, root IDs, data access/contamination exposure, model and harness hashes, stopping rule, resource floor/ceiling, judge protocol and planned comparison family. Use [FSI-01](../../../paper/finite_sample_inference.md) for paired binary outcomes, clustered by the independent unit, and [EvalMath preflight](../../../skills/evalmath-mechinterp-power/SKILL.md) for mechanistic or causal claims. Test external grader integrity independently; abstain from claiming resolution when tasks cannot be validated locally.

## Papers and methods

See [the annotated reading notes](../../papers/safety-and-control.md) and [the research paper index](../../papers/README.md). Papers are conceptual references; they do not grant use of withheld tasks or private grader data.
