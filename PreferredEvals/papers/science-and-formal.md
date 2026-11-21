# Formal and scientific end-to-end checks

- [PaperBench (2025)](https://openai.com/index/paperbench/): full experimental replication, code execution and author rubrics.
- [FrontierMath (Epoch AI)](https://epoch.ai/latest/openai-and-frontiermath): purpose-built hard mathematics with access restrictions to canonical answers and verifiers.
- [EvalMath Prime atlas: StepFun Prover](../../paper/prime_intellect_eval_atlas.md): Lean proof feedback, revision opportunities and exact verifier outcomes.
- [Thinking Machines Inkling Verify: HLE](https://github.com/thinking-machines-lab/inkling-verify): independently re-runnable text reasoning grader and provider variants.

**Design move:** do compilation and theorem-kernel scoring outside the model, report parse errors separately and count task roots rather than tokens or attempts. Human audit all LLM-judged replication subrubrics before a claim.
