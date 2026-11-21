# PreferredEvals Bonsai vs Qwen: registered eight-comparison development ledger

This report is development evidence; the plan was written after partial Bonsai exposure.

| Contrast | Status | Assigned | Paired | Missing/error | Roots | Macro effect | Raw p | Holm p (8) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| public-proxy-iclr2026-oral-vs-reject | observed | 24 | 24 | 0 | 12 | 0.083333 | 0.79688 | 1 |
| public-mmlu-pro-science | observed | 8 | 8 | 0 | 8 | 0.25 | 0.625 | 1 |
| dev-multihop-binding (default reasoning) | observed | 12 | 12 | 0 | 12 | 0.91667 | 0.00097656 | 0.0078125 |
| gsm8k (primeintellect/gsm8k 0.1.4, vf-run 0.4.1) | observed | 12 | 12 | 0 | 6 | 0 | 1 | 1 |
| niah (Inkling Verify 94fd95b, 4K/16K x depth 25/75 x 2) | observed | 8 | 8 | 0 | 8 | 0 | 1 | 1 |
| mcp-sqlite 0.1.0 (vf-run 0.4.1, exact_match) | observed | 8 | 8 | 0 | 8 | 0.375 | 0.375 | 1 |
| swe-bench-lite oracle single-shot (6 gold-valid instances) | observed | 6 | 6 | 0 | 6 | 0 | 1 | 1 |
| dev-multihop-binding (Bonsai reasoning vs no-CoT) | observed | 12 | 12 | 0 | 12 | 0.91667 | 0.00097656 | 0.0078125 |

Effect floor: 10%. Registered tests: 8. Holm includes every registered arm; missing p-values contribute p=1 to the family.

Scored and missing denominators remain unreported wherever the corresponding receipt files were not published.
