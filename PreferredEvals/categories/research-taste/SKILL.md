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

### Dataset rights and pair dependencies

Anthropic TASTE distributes its 92 scored proposal pairs by request to AI safety researchers. Use an authorized local copy only. Pair labels are not a generic public benchmark, and repeated proposal identities induce dependence between comparison pairs. Use the [gym pairwise runner](../../gym/README.md) for candidate-model rollouts once rights are established, and group inferential units by independent proposal/source graph rather than automatically by pair. The included demo pairs are authored examples with synthetic answer letters, not TASTE data.

## Ideation Arena researcher-labeled development pairs

Use the [Ideation Arena conversion contract](../../results/campaign-20261121/README.md) for external human-labeled research idea comparisons. Record NC license acceptance, upstream source revision and human-label dimension. Analyze repeated contexts as one root, and test swapped order sensitivity. Preserve the label file outside inference prompts.
