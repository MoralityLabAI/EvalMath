---
name: preferred-evals-professional-and-multimodal
description: Select and audit external practical work products and multimodal tasks evaluations under EvalMath v2; measure independent roots, pinned harness conditions and judge reliability.
---

# Practical work products and multimodal tasks

Use this skill when a proposed gym or model claim concerns diversify beyond code and mathematical worlds into deliverables, visuals, and real professional judgments.

**Preferred external benchmarks**

- **GDPval**: [source](https://openai.com/index/gdpval/). professional deliverable. Access: `open_gold_subset`.
- **MMMU-Pro**: [source](https://github.com/thinking-machines-lab/inkling-verify). multimodal reasoning. Access: `open_eval_scripts`.
- **CharXiv**: [source](https://thinkingmachines.ai/model-card/inkling/). chart interpretation. Access: `benchmark_data_review`.
- **HealthBench**: [source](https://github.com/openai/simple-evals). expert rubric. Access: `public_eval_high_stakes`.
- **MMAU**: [source](https://github.com/thinking-machines-lab/inkling-verify). audio understanding. Access: `open_scripts_audio_required`.

**Independent sampling unit:** independent professional task or media item, grouped by source/occupation.

**Primary readout:** artifact utility, expert pairwise choice, task correctness with per-domain uncertainty.

**Required comparisons and controls:** blinded expert review, vision/audio modality integrity, task artifact checks, fair resource matching. Design a negative control and record all experimental arms, including unsuccessful attempts.

**Pilot:** Start with GDPval open examples and Inkling-verify MMMU-Pro/CharXiv alternatives where licenses permit.

**Claim gate:** Clinical or other high-stakes rubric scores are research measures, not authorization to make consequential decisions.

## EvalMath procedure

Apply the [common contract](../../v2/README.md) and a pinned `preferred-evals/v2` manifest. State the target population, root IDs, data access/contamination exposure, model and harness hashes, stopping rule, resource floor/ceiling, judge protocol and planned comparison family. Use [FSI-01](../../../paper/finite_sample_inference.md) for paired binary outcomes, clustered by the independent unit, and [EvalMath preflight](../../../skills/evalmath-mechinterp-power/SKILL.md) for mechanistic or causal claims. Test external grader integrity independently; abstain from claiming resolution when tasks cannot be validated locally.

## Papers and methods

See [the annotated reading notes](../../papers/professional-and-multimodal.md) and [the research paper index](../../papers/README.md). Papers are conceptual references; they do not grant use of withheld tasks or private grader data.
