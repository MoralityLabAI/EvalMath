---
name: preferred-evals-agents-and-mcp
description: Select and audit external agentic tools, retrieval and cooperation evaluations under EvalMath v2; measure independent roots, pinned harness conditions and judge reliability.
---

# Agentic tools, retrieval and cooperation

Use this skill when a proposed gym or model claim concerns stress multi-step tool agents in externally maintained settings and isolate architecture versus tool api.

**Preferred external benchmarks**

- **Prime Verifiers v1**: [source](https://github.com/PrimeIntellect-ai/verifiers/blob/main/docs/v1/overview.md). taskset harness trace contract. Access: `public_tooling_some_paid_tasks`.
- **tau2-bench**: [source](https://github.com/MoralityLabAI/EvalMath/blob/main/paper/prime_intellect_eval_atlas.md). simulated user tool tasks. Access: `public_package_verify_hub`.
- **BrowseComp**: [source](https://openai.com/index/browsecomp/). hard retrieval. Access: `public_eval`.
- **ARC-AGI-3**: [source](https://arcprize.org/arc-agi/3). interactive world model. Access: `public_games_and_sdk`.

**Independent sampling unit:** independent tool task, world or user scenario.

**Primary readout:** task completion, correct tool calls, repeated reads, elapsed calls and total cost.

**Required comparisons and controls:** counterpart policy frozen, tool trace replay, token budget, alternate interface, no reward leakage. Design a negative control and record all experimental arms, including unsuccessful attempts.

**Pilot:** Import raw public Prime v1 traces with fixed task IDs, then compare no-compaction and state-preserving memory on audited tasks.

**Claim gate:** MCP behavior depends on runtime and trace schema; capture both and avoid protocol-version conflation.

## EvalMath procedure

Apply the [common contract](../../v2/README.md) and a pinned `preferred-evals/v2` manifest. State the target population, root IDs, data access/contamination exposure, model and harness hashes, stopping rule, resource floor/ceiling, judge protocol and planned comparison family. Use [FSI-01](../../../paper/finite_sample_inference.md) for paired binary outcomes, clustered by the independent unit, and [EvalMath preflight](../../../skills/evalmath-mechinterp-power/SKILL.md) for mechanistic or causal claims. Test external grader integrity independently; abstain from claiming resolution when tasks cannot be validated locally.

## Papers and methods

See [the annotated reading notes](../../papers/agents-and-mcp.md) and [the research paper index](../../papers/README.md). Papers are conceptual references; they do not grant use of withheld tasks or private grader data.
