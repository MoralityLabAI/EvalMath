# Benchmark quality, grader validity and environment noise

- [OpenAI SWE-bench Pro audit (July 2026)](https://openai.com/index/separating-signal-from-noise-coding-evaluations/): task-quality failures identified by systematic methods and external human audit.
- [Anthropic Infrastructure Noise (Feb. 2026)](https://www.anthropic.com/research/infrastructure-noise): CPU and RAM limits are part of the evaluation treatment.
- [Anthropic Bloom judge trust](https://alignment.anthropic.com/2025/bloom-auto-evals/): human agreement, seeded judge changes and performance under scoring thresholds.
- [EvalMath judge shared-error measurement](../../paper/judge_shared_error_measurement.md), [FSI-01](../../paper/finite_sample_inference.md): correlated grader failures, root-level inference and claim fences.

**Design move:** preregister invalid-task audit criteria before model scores, publish full/valid denominators, compare resource envelopes and quantify judge disagreement. Model failures and platform failures have distinct receipt codes.
