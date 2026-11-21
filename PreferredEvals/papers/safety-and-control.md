# Behavioral safety and auditing

- [Anthropic Bloom (Dec. 2025)](https://alignment.anthropic.com/2025/bloom-auto-evals/): pre-specified behavior, seeded scenarios, repeated suites and judge-validity checks.
- [Anthropic Petri 2.0 (Jan. 2026)](https://alignment.anthropic.com/2026/petri-v2/): multi-turn auditing and improved realism/evaluation-awareness mitigation.
- [Thinking Machines Inkling 2 Mini (Nov. 2026)](https://thinkingmachines.ai/news/inkling-2-mini/): CoT controllability and LinuxArena monitorability under matched false-positive rates.
- [Anthropic Demystifying Agent Evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents): specify grader and environment semantics, allow realistic tool-side artifacts.

**Design move:** treat auditor and judge as separate fallible agents; measure FPR/TPR, scenario-diversity and subject-review reliability on independent families. Keep simulated attacks confined to harmless test infrastructure.
