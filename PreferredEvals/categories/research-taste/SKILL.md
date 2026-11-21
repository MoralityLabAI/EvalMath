---
name: preferred-evals-research-taste
description: Select and audit external research taste and proposal judgment evaluations under EvalMath v2; measure independent roots, pinned harness conditions and judge reliability.
---

# Research taste and proposal judgment

Use this skill when a proposed gym or model claim concerns assess which hypotheses or proposals are worth pursuing, with blinded human consensus and uncertainty.

**Preferred external benchmarks**

- **TASTE**: [source](https://alignment.anthropic.com/2026/taste/). expert labeled pairwise. Access: `research_protocol`.
- **TasteVal**: [source](https://arxiv.org/abs/2610.06824). research experiment budget. Access: `tasks_withheld`.
- **IdeaTaste**: [source](https://arxiv.org/abs/2611.03424). future publication match. Access: `public_paper_and_leaderboard`.
- **SciTaste**: [source](https://arxiv.org/abs/2610.28653). paper value assessment. Access: `public_paper`.

**Independent sampling unit:** expert-judged proposal pair or research problem; repeats stay clustered.

**Primary readout:** pairwise agreement and calibration; compute-to-quality frontier kept separate.

**Required comparisons and controls:** human adjudication, blinded identity, matched topic/length, label stability. Design a negative control and record all experimental arms, including unsuccessful attempts.

**Pilot:** Start with TASTE-style public illustrative pairs and disagreement adjudication; request authorized held-out human labels before claims.

**Claim gate:** Never present private TasteVal tasks as reproduced, and never call a single model judge an expert consensus.

## EvalMath procedure

Apply the [common contract](../../v2/README.md) and a pinned `preferred-evals/v2` manifest. State the target population, root IDs, data access/contamination exposure, model and harness hashes, stopping rule, resource floor/ceiling, judge protocol and planned comparison family. Use [FSI-01](../../../paper/finite_sample_inference.md) for paired binary outcomes, clustered by the independent unit, and [EvalMath preflight](../../../skills/evalmath-mechinterp-power/SKILL.md) for mechanistic or causal claims. Test external grader integrity independently; abstain from claiming resolution when tasks cannot be validated locally.

## Papers and methods

See [the annotated reading notes](../../papers/research-taste.md) and [the research paper index](../../papers/README.md). Papers are conceptual references; they do not grant use of withheld tasks or private grader data.
