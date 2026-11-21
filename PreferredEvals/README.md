# PreferredEvals

This is EvalMath's external-benchmark-first research catalog. It exists to reduce repeated evaluation against project-specific Storyworlds and mechanism toys. The catalog is a *selection and quality-control layer*, with a native manifest and trace contract called **PreferredEvals v2**. It is not Prime Intellect Verifiers v2; upstream Prime's documented implementation uses `verifiers.v1` tasksets/harnesses/traces.

## Categories

- [Research taste and proposal judgment](categories/research-taste/SKILL.md): Assess which hypotheses or proposals are worth pursuing, with blinded human consensus and uncertainty.
- [Experiment selection and scientific execution](categories/experimental-design/SKILL.md): Measure choices of informative experiments and iterative scientific work under fixed budgets.
- [Repository repair and terminal engineering](categories/software-engineering/SKILL.md): Use real issues and graded artifacts under a documented harness, including a gold-patch sanity check.
- [Agentic tools, retrieval and cooperation](categories/agents-and-mcp/SKILL.md): Stress multi-step tool agents in externally maintained settings and isolate architecture versus tool API.
- [Mathematical proof and scientific reasoning](categories/science-and-formal/SKILL.md): Prefer exact checkers and graded experimental artifacts over verbal plausibility.
- [Behavioral safety and monitorability](categories/safety-and-control/SKILL.md): Distinguish measured behavior under controlled elicitation from speculative claims of model intent.
- [Looped models, long context and monitorability](categories/recursive-and-context/SKILL.md): Test whether internal computation improves ability while preserving inspectable causal and output evidence.
- [Causal inference and interactive world models](categories/causal-world-models/SKILL.md): Test model formation under interventions across externally designed interactive worlds.
- [Practical work products and multimodal tasks](categories/professional-and-multimodal/SKILL.md): Diversify beyond code and mathematical worlds into deliverables, visuals, and real professional judgments.
- [Judge reliability, harness effects and benchmark forensics](categories/evaluation-integrity/SKILL.md): Audit the measuring instrument itself before interpreting leaderboard deltas.

## Order of preference

1. **Outside, independently designed tasks** with public source code and audited graders.
2. **External professional, agentic or human-judged tasks** where task or grader access is licensed/pinned.
3. **Our own transparent synthetic worlds** as causal controls or development pilots, labelled as such.
4. New custom tasks only to fill an explicit missing capability, with an external comparator and a fresh untouched confirmation split.

The [machine-readable catalog](v2/catalog.json) stores provider, original URL, access constraints, proposed priority and category. A benchmark appearing in this catalog is **not** certified as reliable. OpenAI's 2026 review identified significant task defects in SWE-bench Pro; older SWE-bench Verified is contamination-sensitive, and an independent review questions ARC-AGI-3 version/harness comparability. Audit tasks and evaluator design before headline comparisons.

See [v2 design and executable preflight](v2/README.md), [annotated papers](papers/README.md), and EvalMath's existing [evaluation-design calculus](../paper/evaluation_design_calculus.md), [Prime examples atlas](../paper/prime_intellect_eval_atlas.md) and [finite-sample inference](../paper/finite_sample_inference.md).

## Immediate starter set

- **Research judgment:** TASTE-style proposal ranking, plus a labelled TasteVal-style *open* experimental-design proxy. Original TasteVal tasks are withheld.
- **Coding:** audited SWE instances plus DeepSWE or Terminal-Bench under pinned resource rules; never reuse the 26-task MCP-03 pilot as independent confirmation.
- **Agents:** Prime v1 tasksets and real tool traces; distinguish compaction's token savings from actual task completion.
- **Recursive models:** Inkling Verify and matched no-CoT/multi-hop or loop-depth controls.
- **Generalization:** public ARC-AGI-3 games, GDPval deliverables and multimodal tasks, with task quality and licensing checks.

The first v2 change is a standard-library validation/receipt adapter and catalog. There are no new model scores in this repository unless accompanied by raw trace hashes, a registered experimental protocol and a separately identified grader.
