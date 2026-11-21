| category | benchmark | model | condition | attempts | scored | correct | accuracy (Wilson 95%) | roots scored | root-mean accuracy (bootstrap 95%) | outcomes | prompt tok. | completion tok. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| agentic tools (MCP) | mcp-sqlite 0.1.0 | bonsai-27b | default | 8 | 8 | 6 | 0.75 (0.41-0.93) | 8/8 | 0.75 (0.38-1.00) | correct 6, wrong 2 | 1130.8 | 650.4 |
| agentic tools (MCP) | mcp-sqlite 0.1.0 | qwen3-4b | default | 8 | 8 | 3 | 0.375 (0.14-0.69) | 8/8 | 0.375 (0.12-0.75) | correct 3, wrong 5 | 625.9 | 169.5 |
| long context | niah (Inkling Verify, 4K and 16K) | bonsai-27b | default | 8 | 8 | 8 | 1.0 (0.68-1.00) | 8/8 | 1.0 (1.00-1.00) | correct 8 | 9849.5 | 32.2 |
| long context | niah (Inkling Verify, 4K and 16K) | qwen3-4b | default | 8 | 8 | 8 | 1.0 (0.68-1.00) | 8/8 | 1.0 (1.00-1.00) | correct 8 | 9842.9 | 82.0 |
| math word problems | gsm8k (primeintellect/gsm8k 0.1.4) | bonsai-27b | default | 12 | 12 | 12 | 1.0 (0.76-1.00) | 6/6 | 1.0 (1.00-1.00) | correct 12 | 153.2 | 332.2 |
| math word problems | gsm8k (primeintellect/gsm8k 0.1.4) | qwen3-4b | default | 12 | 12 | 12 | 1.0 (0.76-1.00) | 6/6 | 1.0 (1.00-1.00) | correct 12 | 109.3 | 247.7 |
| recursive reasoning (generated) | dev-multihop-binding | bonsai-27b | default reasoning | 12 | 12 | 11 | 0.9167 (0.65-0.99) | 12/12 | 0.9167 (0.75-1.00) | correct 11, wrong 1 | 228.2 | 632.3 |
| recursive reasoning (generated) | dev-multihop-binding | bonsai-27b | enable_thinking=false | 12 | 12 | 0 | 0.0 (0.00-0.24) | 12/12 | 0.0 (0.00-0.00) | wrong 12 | 192.2 | 2.9 |
| recursive reasoning (generated) | dev-multihop-binding | qwen3-4b | default (non-thinking model) | 12 | 12 | 0 | 0.0 (0.00-0.24) | 12/12 | 0.0 (0.00-0.00) | wrong 12 | 187.5 | 3.0 |
| research-taste (public proxy) | public-proxy-iclr2026-oral-vs-reject | bonsai-27b | default | 24 | 24 | 11 | 0.4583 (0.28-0.65) | 12/12 | 0.4583 (0.21-0.71) | correct 11, format_invalid 1, wrong 12 | 662.1 | 692.9 |
| research-taste (public proxy) | public-proxy-iclr2026-oral-vs-reject | qwen3-4b | default | 24 | 24 | 9 | 0.375 (0.21-0.57) | 12/12 | 0.375 (0.17-0.62) | correct 9, wrong 15 | 617.5 | 2.0 |
| science knowledge (HLE stand-in) | public-mmlu-pro-science | bonsai-27b | default | 8 | 8 | 7 | 0.875 (0.53-0.98) | 8/8 | 0.875 (0.62-1.00) | correct 7, wrong 1 | 255.2 | 591.4 |
| science knowledge (HLE stand-in) | public-mmlu-pro-science | qwen3-4b | default | 8 | 8 | 5 | 0.625 (0.31-0.86) | 8/8 | 0.625 (0.25-0.88) | correct 5, wrong 3 | 210.0 | 2.0 |
| software engineering | swe-bench-lite oracle single-shot | bonsai-27b | default | 6 | 6 | 0 | 0.0 (0.00-0.39) | 6/6 | 0.0 (0.00-0.00) | format_invalid 5, wrong 1 | 5425.3 | 2807.5 |
| software engineering | swe-bench-lite oracle single-shot | qwen3-4b | default | 6 | 6 | 0 | 0.0 (0.00-0.39) | 6/6 | 0.0 (0.00-0.00) | format_invalid 6 | 5167.3 | 1119.7 |

| comparison | paired attempts (roots) | candidate correct | baseline correct | root-macro effect | cluster bootstrap interval | test | p | p (Holm) | FSI-01 verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| taste-bonsai-vs-qwen | 24 (12) | 11 | 9 | 0.083 | [-0.292, 0.542] | exact_cluster_sign_flip | 0.796875 | 1.0 | inconclusive |
| mmlupro-bonsai-vs-qwen | 8 (8) | 7 | 5 | 0.25 | [-0.375, 0.875] | exact_McNemar_independent_pairs | 0.625 | 1.0 | suggestive |
| multihop-bonsai-vs-qwen | 12 (12) | 11 | 0 | 0.917 | [0.667, 1.000] | exact_McNemar_independent_pairs | 0.0009765625 | 0.0078 | suggestive |
| gsm8k-bonsai-vs-qwen | 12 (6) | 12 | 12 | 0.0 | [0.000, 0.000] | exact_cluster_sign_flip | 1.0 | 1.0 | inconclusive |
| niah-bonsai-vs-qwen | 8 (8) | 8 | 8 | 0.0 | [0.000, 0.000] | exact_McNemar_independent_pairs | 1.0 | 1.0 | inconclusive |
| sqlite-bonsai-vs-qwen | 8 (8) | 6 | 3 | 0.375 | [-0.375, 1.000] | exact_McNemar_independent_pairs | 0.375 | 1.0 | suggestive |
| swe-bonsai-vs-qwen | 6 (6) | 0 | 0 | 0.0 | [0.000, 0.000] | exact_McNemar_independent_pairs | 1.0 | 1.0 | inconclusive |
| multihop-bonsai-reasoning-vs-nocot | 12 (12) | 11 | 0 | 0.917 | [0.667, 1.000] | exact_McNemar_independent_pairs | 0.0009765625 | 0.0078 | suggestive |
| multihop-bonsai-nocot-vs-qwen (exploratory) | 12 (12) | 0 | 0 | 0.0 | [0.000, 0.000] | exact_McNemar_independent_pairs | 1.0 | None | inconclusive |

Blocked: HLE text (Inkling Verify hle): cais/hle is gated on Hugging Face and this account has no access (DatasetNotFoundError at prepare)

Blocked: DeepSWE (Inkling Verify deepswe): needs rootless Podman on native x86-64 Linux and four-hour agent budgets; Podman is not installed in this WSL

Blocked: PaperBench: needs multi-hour agent runs and rubric judging; no executable proxy staged

Blocked: Prime sandbox tasksets: paid Prime sandboxes are out of scope for this campaign
