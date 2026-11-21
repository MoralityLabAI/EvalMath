---
name: preferred-evals-recursive-and-context
description: Select and audit external looped models, long context and monitorability evaluations under EvalMath v2; measure independent roots, pinned harness conditions and judge reliability.
---

# Looped models, long context and monitorability

Use this skill when a proposed gym or model claim concerns test whether internal computation improves ability while preserving inspectable causal and output evidence.

**Preferred external benchmarks**

- **Inkling Verify**: [source](https://github.com/thinking-machines-lab/inkling-verify). multi provider reproduction. Access: `public_scripts`.
- **Think Fast**: [source](https://thinkingmachines.ai/news/inkling-2-mini/). no cot time horizon. Access: `benchmark_method`.
- **N-Hop Lookup**: [source](https://thinkingmachines.ai/news/inkling-2-mini/). serial latent reasoning. Access: `benchmark_method`.
- **MRCR**: [source](https://thinkingmachines.ai/news/inkling-2-mini/). long context multihop. Access: `benchmark_method`.
- **DeepSWE**: [source](https://github.com/thinking-machines-lab/inkling-verify). fresh container patch tests. Access: `public_scripts_images_required`.

**Independent sampling unit:** independent base problem or chain template, with loop counts/variants clustered.

**Primary readout:** no-CoT time horizon, depth-response curve, token efficiency, tool-side monitor detection.

**Required comparisons and controls:** matched parameter/compute budgets, fixed training exposure, same sampled task family, no-CoT ablation. Design a negative control and record all experimental arms, including unsuccessful attempts.

**Pilot:** Replicate Inkling's fixed-versus-variable loop contrasts using its public verification scripts before proposing custom RLT metrics.

**Claim gate:** A depth gain is a capability observation until a matched causal intervention supports a mechanism claim.

## EvalMath procedure

Apply the [common contract](../../v2/README.md) and a pinned `preferred-evals/v2` manifest. State the target population, root IDs, data access/contamination exposure, model and harness hashes, stopping rule, resource floor/ceiling, judge protocol and planned comparison family. Use [FSI-01](../../../paper/finite_sample_inference.md) for paired binary outcomes, clustered by the independent unit, and [EvalMath preflight](../../../skills/evalmath-mechinterp-power/SKILL.md) for mechanistic or causal claims. Test external grader integrity independently; abstain from claiming resolution when tasks cannot be validated locally.

## Papers and methods

See [the annotated reading notes](../../papers/recursive-and-context.md) and [the research paper index](../../papers/README.md). Papers are conceptual references; they do not grant use of withheld tasks or private grader data.
