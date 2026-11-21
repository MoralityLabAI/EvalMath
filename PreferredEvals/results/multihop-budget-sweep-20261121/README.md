# Multi-hop reasoning-budget sweep, Bonsai 27B, 2026-11-21

A sealed, preregistered test of how much hidden reasoning Ternary Bonsai 2 27B needs to follow variable-binding chains.

## Design

- **Registration.** [`registration.json`](registration.json) was pushed in b646c06, before the task set existed. It recorded the hash of a secret generator seed, eight conditions, four contrasts, an effect floor of 0.10, α 0.05 and Holm.
- **Amendment 1.** [`amendment-1.json`](amendment-1.json), pushed in 10c183f before any scoring. This llama-server treats `thinking_budget_tokens: 0` as unlimited, so budget 0 is run as `enable_thinking: false` with the answer-only prompt.
- **Amendment 2.** [`amendment-2.json`](amendment-2.json): at the user's request the Qwen conditions were skipped, so H3 and H4 are untested. They stay in the Holm family with p = 1.
- **Tasks.** 80 fresh chains, 20 each at 2, 4, 8 and 12 hops, each with a distractor chain. Source: `build_public_sets.py multihop` with the sealed seed. The seed is revealed in [`set/seed.txt`](set/seed.txt): its sha256 matches the registration, and regenerating from it reproduces `set/tasks.jsonl` byte for byte (sha256 `d4f2bc61…a962`).
- **Model and runs.**
  - Bonsai 27B PTQ1_0 (sha256 `53107f53…3ee3`) on PrismML llama-server b10743, 2 × 8,192-token slots, 10 GB lease.
  - Temperature 0, seed 42, one attempt per chain, output cap 4,096 tokens.
  - Hidden thinking budget passed per request as `thinking_budget_tokens`; the server closes the thinking block at the budget and the model then answers.

## Result

| Budget (thinking tokens) | Correct / 80 | 2 hops | 4 hops | 8 hops | 12 hops | Mean completion tokens |
| --- | --- | --- | --- | --- | --- | --- |
| 0 (thinking off) | 8 | 6/20 | 1/20 | 1/20 | 0/20 | 16 |
| 64 | 1 | 1/20 | 0/20 | 0/20 | 0/20 | 191 |
| 256 | 12 | 10/20 | 1/20 | 1/20 | 0/20 | 289 |
| 1,536 | 79 | 20/20 | 20/20 | 20/20 | 19/20 | 744 |

Registered contrasts, analysed with EvalMath FSI-01: exact McNemar, Holm over four, readout declared sealed and hypotheses preregistered.

| Contrast | Correct (candidate vs baseline) | Effect | Cluster bootstrap 95% | p | p (Holm, 4) | FSI-01 verdict |
| --- | --- | --- | --- | --- | --- | --- |
| H1: budget 1,536 vs 0 | 79 vs 8 | +0.887 | [0.795, 0.963] | 8.5e-22 | < 1e-4 | **confirmed** |
| H2: budget 256 vs 0 | 12 vs 8 | +0.050 | [-0.050, 0.163] | 0.39 | 1.0 | inconclusive |
| H3: Qwen visible CoT vs answer only | not run (amendment 2) | | | | p = 1 in Holm | |
| H4: Bonsai 1,536 vs Qwen CoT 1,536 | not run (amendment 2) | | | | p = 1 in Holm | |

What it shows:

- **The threshold is steep.** With a 1,536-token budget, Bonsai tracks chains up to 12 hops almost perfectly. At 256 tokens it manages only half of the 2-hop chains, and 1 of 60 longer ones.
- **A truncated budget is worse than none.** Budget 64 (1/80) scores below thinking off (8/80): a reasoning trace cut short and then forced to an answer does worse than answering directly.
- **Each hop costs about 90 to 250 thinking tokens.** Correct answers at budget 1,536 used a median of 246, 142, 94 and 89 completion tokens per hop at 2, 4, 8 and 12 hops. So a 12-hop chain needs roughly 1,000 tokens of reasoning, far beyond 256.
- **No truncation and no format failures.** No reply hit the 4,096-token output cap, and every reply parsed.

Per-cell tables with Wilson intervals are in [`budget_tables.md`](budget_tables.md), and the per-chain ledger is in [`ledger.jsonl`](ledger.jsonl). FSI-01 manifests and results are in [`campaign_summary.json`](campaign_summary.json).

## Process notes

- **Aborted first budget-0 pass.** It was run with `thinking_budget_tokens: 0`, which the server ignored (200 to 500 thinking tokens per chain). It was stopped, archived in [`aborted-bonsai-b0/`](aborted-bonsai-b0) (18 receipts, never scored), and replaced under amendment 1.
- **Duplicate runner.** A stopped sweep shell kept running, and two runner processes wrote into the same budget-0 and budget-64 folders. Those receipts are archived in [`aborted-duplicate-runner/`](aborted-duplicate-runner), unscored. All four conditions were then rerun by a single process.
- **Tooling for this sweep.**
  - `runner.py` gained `--response-mode cot_final_line` and `--concurrency`, recorded in `run.json`.
  - `build_public_sets.py multihop` gained `--depths` and `--benchmark-id`.
  - `budget_sweep.py` builds the depth-by-budget tables.
  - The driver script is [`scripts/sweep.sh`](scripts/sweep.sh).

## Next

The confirmed effect makes per-hop reasoning cost the quantity to beat. Two runs follow from it:
- **Finer budget grid.** 384, 512, 768 and 1,024 tokens at each depth, to locate the threshold per hop count.
- **Same sealed set for compact policies.** A compact looped or recurrent policy (TRM, RLT, HRM) evaluated on the same set, reporting accuracy per reasoning token or loop step. The skipped Qwen visible-CoT arms can be run on this set at any time; it stays sealed against training.
