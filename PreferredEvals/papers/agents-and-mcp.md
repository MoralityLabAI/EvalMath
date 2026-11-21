# Agentic tools, environment realism and multi-turn protocols

- [Prime Intellect Verifiers v1 overview](https://github.com/PrimeIntellect-ai/verifiers/blob/main/docs/v1/overview.md): Taskset, Harness, Agent, Environment, Toolset and Trace as separate objects.
- [Prime v1 evaluation guide](https://github.com/PrimeIntellect-ai/verifiers/blob/main/docs/v1/evaluation.md): `vf-eval`, config pins, trace JSONL, runtime/harness selection and resume semantics.
- [OpenAI BrowseComp (2025)](https://openai.com/index/browsecomp/): long evidence chains with short, verifiable reference answers.
- [ARC-AGI-3 (2026)](https://arcprize.org/arc-agi/3): goal discovery from interactive worlds; inspect version and harness stability.
- [EvalMath Prime atlas](../../paper/prime_intellect_eval_atlas.md): practical component-by-component decompositions of nine Hub environments.

**Design move:** compare tool contracts under matched agent and task IDs; retain all tool side effects, content redactions and final artifact submissions in a replayable trace.
