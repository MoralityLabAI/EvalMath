---
name: preferred-evals-causal-world-models
description: Select and audit external causal inference and interactive world models evaluations under EvalMath v2; measure independent roots, pinned harness conditions and judge reliability.
---

# Causal inference and interactive world models

Use this skill when a proposed gym or model claim concerns test model formation under interventions across externally designed interactive worlds.

**Preferred external benchmarks**

- **ARC-AGI-3**: [source](https://arcprize.org/arc-agi/3). interactive world model. Access: `public_games_and_sdk`.
- **HGW-05 causal families**: [source](https://github.com/MoralityLabAI/GPTStoryworld/pull/20). structural control not confirmation. Access: `public_synthetic_development`.
- **counterfactual task pairs**: [source](https://github.com/MoralityLabAI/EvalMath/blob/main/paper/evaluation_design_calculus.md). generator needed. Access: `design_pattern`.

**Independent sampling unit:** independent world generator/root; levels and counterfactuals remain within it.

**Primary readout:** goal discovery/action efficiency, causal transfer and posterior calibration.

**Required comparisons and controls:** do/sham pairs, confounder contrast, random action, p2-correlation-only signals. Design a negative control and record all experimental arms, including unsuccessful attempts.

**Pilot:** Anchor to ARC-AGI-3 public games, then treat HGW-05 as a transparent development-only mechanistic control.

**Claim gate:** Synthetic generator degrees of freedom do not equal independent sampled worlds; inspect benchmark-version fairness.

## EvalMath procedure

Apply the [common contract](../../v2/README.md) and a pinned `preferred-evals/v2` manifest. State the target population, root IDs, data access/contamination exposure, model and harness hashes, stopping rule, resource floor/ceiling, judge protocol and planned comparison family. Use [FSI-01](../../../paper/finite_sample_inference.md) for paired binary outcomes, clustered by the independent unit, and [EvalMath preflight](../../../skills/evalmath-mechinterp-power/SKILL.md) for mechanistic or causal claims. Test external grader integrity independently; abstain from claiming resolution when tasks cannot be validated locally.

## Papers and methods

See [the annotated reading notes](../../papers/causal-world-models.md) and [the research paper index](../../papers/README.md). Papers are conceptual references; they do not grant use of withheld tasks or private grader data.
