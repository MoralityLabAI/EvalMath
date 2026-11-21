# PreferredEvals execution coverage (2026-11-21)

"Executed" means at least one live local-model run with native or reference grading, recorded in [`results/campaign-20261121`](../results/campaign-20261121/README.md) (Bonsai 27B and Qwen3-4B on one RTX 5080).

| Category | Gym status | Executed | Next work |
|---|---|---|---|
| Research taste | Generic authorized pairwise prompts, order swap, exact reference scoring; public ICLR 2026 oral-vs-reject proxy builder | Yes: proxy pairs, both orders | TASTE access request; expert-annotated public proposal benchmark |
| Experimental design | Catalog only | No | Fixed-Coder TasteVal-style open project runner with compute-budget receipts |
| Software engineering | SWE-bench Lite oracle single-shot (`swebench_oracle.py`, official harness); Inkling DeepSWE launcher | Yes: 6 gold-valid Lite instances. DeepSWE blocked: no rootless Podman | Agentic SWE harness; DeepSWE on a Podman host |
| Agents and MCP | Verifiers v0.4.1 `vf-run` launcher with explicit harness; Episode importer | Yes: mcp-sqlite (taskset harness, judge removed) | More non-paid v1 tasksets; judge-model selection for judged tasksets |
| Formal science | Inkling HLE launcher; MMLU-Pro science builder; generic short-answer prompts | MMLU-Pro stand-in only. HLE blocked: `cais/hle` gated | HLE after access, with a separate judge; StepFun Lean, FrontierMath, PaperBench adapters |
| Math | Verifiers v0.4.1 `primeintellect/gsm8k` with the chat-only harness | Yes: 6 problems × 2 attempts | Harder sets (MATH-500, AIME) to escape the ceiling |
| Safety/control | Catalog only | No | Anthropic Bloom/Petri native audit integration |
| Recurrence and context | Inkling NIAH launcher; generated multi-hop chains with a no-CoT condition | Yes: NIAH 4K/16K; multi-hop 2 to 12 hops | Reasoning-budget sweep and visible-CoT condition; freeze per-layer loop counts for compact recurrent policies |
| Causal world models | Generic task runner; generated HGW remains separate | No | Interactive ARC-AGI-3 native runner and sealed root-family protocols |
| Professional and multimodal | Inkling MMMU-Pro and MMAU launchers | No (needs a multimodal endpoint) | GDPval expert-graded artifact outputs |
| Evaluation integrity | Root accounting, failure-class ledger (`campaign.py`), FSI-01 pairing with Holm, provider failure ledger | Yes | Sealed confirmation readouts; judge agreement |

Each native launcher delegates to the original evaluator, which is the authority for environment transitions and reward. The generic task runner supports only one-shot tasks with independent labels. Tools, code patches and repeated side effects require a native agent harness.
