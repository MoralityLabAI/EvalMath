# Recurrence and long-context diagnostics

- [Thinking Machines, Inkling 2 Mini (Nov. 2026)](https://thinkingmachines.ai/news/inkling-2-mini/): matched 1–5 pass model, no-CoT horizon, N-hop retrieval, reasoning-token efficiency and LinuxArena monitoring. Observe that pass counts beyond training distribution require a claim-scope caveat.
- [Inkling Verify](https://github.com/thinking-machines-lab/inkling-verify): public DeepSWE, NIAH, HLE and multimodal verification scripts; record provider API and sampling parameters.
- [Inkling Model Card](https://thinkingmachines.ai/model-card/inkling/): multi-domain benchmark table and methodology.

**Design move:** vary passes at the same model checkpoint and across budget-matched controls, preserving roots; compare no-CoT versus CoT while logging token and wall-time budgets. For mechanism claims require latent-state interventions and matched shams.
