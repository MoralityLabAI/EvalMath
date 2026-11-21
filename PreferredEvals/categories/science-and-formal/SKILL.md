---
name: preferred-evals-science-and-formal
description: Select and audit external mathematical proof and scientific reasoning evaluations under EvalMath v2; measure independent roots, pinned harness conditions and judge reliability.
---

# Mathematical proof and scientific reasoning

Use this skill when a proposed gym or model claim concerns prefer exact checkers and graded experimental artifacts over verbal plausibility.

**Preferred external benchmarks**

- **PaperBench**: [source](https://openai.com/index/paperbench/). human authored rubrics. Access: `public_framework`.
- **FrontierMath**: [source](https://epoch.ai/latest/openai-and-frontiermath). independent mathematician problems. Access: `restricted_verifiers`.
- **StepFun Prover**: [source](https://github.com/MoralityLabAI/EvalMath/blob/main/paper/prime_intellect_eval_atlas.md). iterative lean proof. Access: `hub_version_dependent`.
- **GPQA Diamond**: [source](https://thinkingmachines.ai/news/inkling-2-mini/). science reasoning. Access: `benchmark_license_review`.
- **HLE**: [source](https://github.com/thinking-machines-lab/inkling-verify). challenging knowledge. Access: `public_eval_scripts`.

**Independent sampling unit:** independent theorem, problem family or paper replication project.

**Primary readout:** valid proof, independently replicated result, or rubric component with adjudicated error.

**Required comparisons and controls:** formal kernel or unit-test verifier, grader isolation, multiple proofs, source contamination. Design a negative control and record all experimental arms, including unsuccessful attempts.

**Pilot:** Run Lean/pytest repair tasks through a pinned external harness while preserving EvalMath exact finite evidence classes.

**Claim gate:** A synthetic parity oracle is a structural ceiling, and judge-based paper replication requires human audit.

## EvalMath procedure

Apply the [common contract](../../v2/README.md) and a pinned `preferred-evals/v2` manifest. State the target population, root IDs, data access/contamination exposure, model and harness hashes, stopping rule, resource floor/ceiling, judge protocol and planned comparison family. Use [FSI-01](../../../paper/finite_sample_inference.md) for paired binary outcomes, clustered by the independent unit, and [EvalMath preflight](../../../skills/evalmath-mechinterp-power/SKILL.md) for mechanistic or causal claims. Test external grader integrity independently; abstain from claiming resolution when tasks cannot be validated locally.

## Papers and methods

See [the annotated reading notes](../../papers/science-and-formal.md) and [the research paper index](../../papers/README.md). Papers are conceptual references; they do not grant use of withheld tasks or private grader data.
