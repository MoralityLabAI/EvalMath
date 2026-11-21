# PreferredEvals execution coverage (2026-11-21)

| Category | Gym status | Next work |
|---|---|---|
| Research taste | Generic authorized pairwise prompts, order swap, exact reference scoring | TASTE access request; expert-annotated public proposal benchmark |
| Experimental design | Catalog only | Fixed-Coder TasteVal-style open project runner with compute-budget receipts |
| Software engineering | Inkling Verify DeepSWE native launcher | SWE-bench/Terminal-Bench adapter and gold-task audit before public comparisons |
| Agents and MCP | Verifiers v0.4.1 `vf-run` native launcher | Prime taskset installation and per-episode trace import for current Episode schema |
| Formal science | Native HLE launcher; generic short-answer prompts | StepFun Lean, FrontierMath, PaperBench exact/rubric adapter |
| Safety/control | Catalog only | Anthropic Bloom/Petri native audit integration |
| Recurrence and context | Inkling NIAH launcher | Freeze per-layer loop counts; benchmark matched no-CoT depth and throughput |
| Causal world models | Generic task runner; generated HGW remains separate | Interactive ARC-AGI-3 native runner and sealed root-family protocols |
| Professional and multimodal | Inkling MMMU-Pro and MMAU launchers | GDPval expert-graded artifact outputs |
| Evaluation integrity | Root accounting, provider failure ledger, FSI bridge | Gold sanity before code runs; external trace normalization and judge agreement |

Each native launcher delegates to the original evaluator, which is the authority for environment transitions and reward. The generic task runner supports only one-shot tasks with independent labels. Tools, code patches and repeated side effects require a native agent harness.
