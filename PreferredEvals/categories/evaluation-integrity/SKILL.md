---
name: preferred-evals-evaluation-integrity
description: Select and audit external judge reliability, harness effects and benchmark forensics evaluations under EvalMath v2; measure independent roots, pinned harness conditions and judge reliability.
---

# Judge reliability, harness effects and benchmark forensics

Use this skill when a proposed gym or model claim concerns audit the measuring instrument itself before interpreting leaderboard deltas.

**Preferred external benchmarks**

- **OpenAI SWE-bench audit**: [source](https://openai.com/index/separating-signal-from-noise-coding-evaluations/). grading error. Access: `public_audit`.
- **Anthropic infrastructure noise**: [source](https://www.anthropic.com/research/infrastructure-noise). runtime configuration effect. Access: `public_study`.
- **Bloom judge trust**: [source](https://alignment.anthropic.com/2025/bloom-auto-evals/). grader sensitivity. Access: `published_method`.
- **EvalMath FSI-01**: [source](https://github.com/MoralityLabAI/EvalMath/blob/main/paper/finite_sample_inference.md). root level inference. Access: `public_code`.

**Independent sampling unit:** audited task/root with each judge or resource configuration paired.

**Primary readout:** false positive/negative grader rates, infra-failure fraction, root-level CI and mechanism floor.

**Required comparisons and controls:** gold sanity, independent human reviewer, grader-version lock, infra fail triage, resource envelope. Design a negative control and record all experimental arms, including unsuccessful attempts.

**Pilot:** Build a benchmark QA receipt for the 5 gold-patch failures in MCP-03 and evaluate task repairability across hosts.

**Claim gate:** Never silently remove invalid tasks after looking at model outcomes; report both full and independently pre-audited sets.

## EvalMath procedure

Apply the [common contract](../../v2/README.md) and a pinned `preferred-evals/v2` manifest. State the target population, root IDs, data access/contamination exposure, model and harness hashes, stopping rule, resource floor/ceiling, judge protocol and planned comparison family. Use [FSI-01](../../../paper/finite_sample_inference.md) for paired binary outcomes, clustered by the independent unit, and [EvalMath preflight](../../../skills/evalmath-mechinterp-power/SKILL.md) for mechanistic or causal claims. Test external grader integrity independently; abstain from claiming resolution when tasks cannot be validated locally.

## Papers and methods

See [the annotated reading notes](../../papers/evaluation-integrity.md) and [the research paper index](../../papers/README.md). Papers are conceptual references; they do not grant use of withheld tasks or private grader data.
