# CPF-04–06: Prospective correlated proof-fidelity experiment

Status: registered synthetic benchmark and execution harness. Model runs pending. The earlier CPF-01–03 research supplies conditional probability bounds, a canonical circuit-interface bridge, and a public 42-case critique fixture. CPF-04–06 turns that line into a reproducible finite experiment; it is not an audit of the full VP–VNP manuscripts or their upstream kernels.

## CPF-04: Procedural semantic mutations

Ten mechanisms are partitioned by entire family: train (abstract gate constraints, degree growth, determinant/permanent residue), dev (uniform thresholds), test (exact/approximate witness inclusion, formal-vs-pointwise polynomial equality, quantifier order, Horn implication, evidence scope, conditional joint risk). Each family has balanced entailed/non-entailed outcomes; evidence-scope failures are unresolved, rather than false. IDs hash the mathematical parameters, not the seed or label. A fixed public census of 512 roots per family is checked against an independent oracle. The implication oracle enumerates all Boolean assignments satisfying the premises. The polynomial oracle directly evaluates coefficient differences instead of using Horner evaluation. These are bounded checks, not universal Lean proofs.

Prompts and gold are separate; a fresh seed is chosen after the experiment protocol and model checkpoints are frozen. Publish only the high-entropy seed commitment and dataset digests until calls are complete. Exclude earlier prompt IDs if performing another prospective run; exclude the public census IDs if it was used for training. Use one prospective seed for all arms. Freeze the Python version, generator commit, configuration, model file digests, runtime/backend version, quantization, context setting, hardware and sampling settings. Never give the collector gold or tune on a held-out family. Fresh parameters do not protect against familiarity with the generator templates; this is a public procedural benchmark with a prospective instance split. It cannot measure open-ended proof-review skill on its own.

## CPF-05: Matched-call critique protocol

Each model gets four stateless requests per root: direct with cap B; low1 with cap B/2; independent low2 with cap B/2; refine2 with cap B/2, receiving low1's structured response and a verification instruction. The six per-model arms are derived without gold: direct, low1, low2, independent exact agreement (low1 and low2), refine (use refine2), serial exact agreement (low1 and refine2). Cross-model agreement uses low1 from each model. Agreement requires identical label AND certificate; otherwise abstain. Refinement sees the structured prior answer, not private chain of thought. Sharing component calls across arms makes paired comparisons economical and intentionally dependent. There is no tool access or oracle-assisted selection during collection.

Preflight: 48 roots from the development threshold family, B=512, temperature 0.3; no model selection using test results. Verify backend honors completion caps and reports usage (including reasoning tokens if applicable). The collector stops on a missing or exceeded cap, records input/output usage and latency, and resumes from a frozen prompt/config manifest. It supports one-model-at-a-time collection on constrained hardware, and fails scoring on incomplete panels or generation digest drift. Token caps are matched, actual tokens need not be; prompt lengths and model compute differ. Report costs and check whether a backend ignores requested seed or hides reasoning tokens. Cross-model comparisons do not establish equal FLOPs. Wall times are sums of request latencies, not simultaneous execution time. A transport failure or interruption can cause unrecorded billed work, so this is a completed-call ledger rather than a total hardware billing meter.

Primary prospective run: 40 fresh test roots per family (240 roots), B=512; freeze model/runtime fingerprints and config after a separate 48-root dev preflight. The preflight itself is a dry run on a disjoint mechanism; never open primary gold while configuring it. The 240-root panel has 120 entailed, 100 counterexample, and 20 unresolved labels. Two models require 1,920 requests and at most 614,400 completion tokens (4 calls per model per root, cap sum 2.5B); at 30 generated tokens/s this is about 5.7 hours of decoding at the cap, excluding prompt processing, swapping, and overhead. At 100% cap utilization the primary run consumes 307,200 generated tokens per model. Retain both the requested and reported model names; manually verify the backend maps them to the pinned weights. Optional larger run: 128 roots per test family, prespecified before primary scores are opened; use an independent seed and exclusions. Do not choose a budget or stop early on primary outcomes. All thresholds and caps are design choices, not performance forecasts.

## Pre-preflight protocol amendments (2026-11-25)

Made after three Bonsai backend probe calls on development-family prompts and before any registered dev-preflight or test call. No test prompt or gold was opened.

1. **Thinking channel.** With thinking disabled Bonsai answered every probe in 19 tokens with prose certificates, so completion caps would not bind. Both models are therefore requested with `chat_template_kwargs.enable_thinking=true` and a per-request `reasoning_budget_tokens = cap - 128`, so the server closes the think block and the JSON answer fits in the same completion cap. Thinking tokens are counted in `completion_tokens` and against the cap. A model whose chat template has no thinking channel (Inky) ignores both fields and answers inside the cap.
2. **Parse rule.** The registered parse accepts the whole reply optionally wrapped in one Markdown code fence; the reply must still be exactly one JSON object with keys `label` and `certificate`. The strict no-fence parse is reported as an exploratory sensitivity analysis.
3. **Ledger fields.** Each call additionally records the reasoning text (`reasoning_content`), server timings and request options. Refinement still receives only the prior answer's content, never its reasoning text.
4. **Analysis and export.** `scripts/analyze_cpf_suite.py` computes the registered contrasts (paired family-stratified bootstrap, exact McNemar, Holm) and labelled exploratory tables; `scripts/export_cpf_datagoblin.py` writes `rlt_gym.aleph_corpus.v1` streams with evaluation roots quarantined (`loss.eligible=false`).

The frozen run configuration is `configs/cpf_suite_models.json`; model fingerprints are recorded in the run receipts.

## CPF-06: Risk, accuracy, and adjudication

Primary outcome: exact certificate AND label correctness over every root, including abstentions as misses. Primary comparisons within each model are direct vs refine, independent agreement vs serial agreement, and cross-model agreement vs within-model agreement. Secondary outcomes: label-only accuracy, coverage, false authorization among counterexample roots, and authorization among unresolved roots (reported separately). Wrong or missing certificates never count as certified correct. Authorization is based on the proposed label before access to gold, so even an accepted label with an incorrect certificate is included in the risk numerator. Exact agreement is not a proof check.

For each pair report marginal false-authorization counts a,b and intersection j on N counterexample roots, j/N minus (a/N)(b/N), and the paired certified-correct discordant counts. Report results within each mechanism as well as pooled. The difference from a product of pooled marginals can arise from heterogeneous problem difficulty; it is not a causal dependence estimate. The scorer also emits descriptive exact two-sided McNemar p-values for paired certified correctness; they assume independent roots within the stated sampling scheme, are unadjusted and do not justify extrapolation to new mechanisms. Treat 78 pairwise contrasts (13 arms) as exploratory except the preregistered primary contrasts; use Holm adjustment for any family of significance claims. No new mechanism-general accuracy estimate is warranted from six test families. Report absolute paired effects and failure cases even if significance is not reached. A synthetic control of 100 null roots gives both marginal risks 10/100, and intersections 10/100 for shared errors, 1/100 for a balanced independent table, 0/100 for disjoint errors. The corresponding excess risks are 9/100, 0, -1/100. This validates the scorer only.

Operational gates: (1) five local tests including a 5,120-root independent census and 96-call localhost mock, (2) freeze fingerprints, run preflight and check receipt schema, (3) run the full panel without opening gold, (4) score once, retain raw receipts, stratify and inspect all false authorizations, (5) follow with an independent larger panel if preregistered. The finite corpus uses deliberately explicit certificate schemas and relatively small tasks; these may be too easy for larger models. If a ceiling effect appears, register a harder successor (longer chains, composed contracts, genuine Lean statement mutations) on a new seed instead of replacing the current test. The mock oracle is deliberately constructed and is not a measured model result.

## Commands

From EvalMath root, with Python 3.13 or a separately pinned version and pytest installed:

```sh
PYTHONPATH=src pytest -q tests/test_evaluation_cpf_suite.py tests/test_cpf_suite_runner.py
PYTHONPATH=src python scripts/verify_evaluation_cpf_suite.py --output output/evaluation_cpf/cpf_suite.json
# set CPF_SEED to a development seed, generate and collect/score the dev preflight with the same command pattern
PYTHONPATH=src python scripts/run_cpf_suite.py generate --per-family 48 --split dev --out /private/cpf-preflight
# then set CPF_SEED to a private high-entropy primary seed, using your local secret store or terminal
PYTHONPATH=src python scripts/run_cpf_suite.py generate --per-family 40 --split test --out /private/cpf-main
# copy and edit configs/cpf_suite_models.example.json with served model IDs and fingerprints
PYTHONPATH=src python scripts/run_cpf_suite.py collect --prompts /private/cpf-main/prompts.jsonl --config /private/models.json --calls /private/cpf-main/calls.jsonl --only-model bonsai
# unload Bonsai, load Inky (separate servers can also be used together)
PYTHONPATH=src python scripts/run_cpf_suite.py collect --prompts /private/cpf-main/prompts.jsonl --config /private/models.json --calls /private/cpf-main/calls.jsonl --only-model inky
PYTHONPATH=src python scripts/run_cpf_suite.py score --prompts /private/cpf-main/prompts.jsonl --gold /private/cpf-main/gold.jsonl --generation-manifest /private/cpf-main/manifest.json --calls /private/cpf-main/calls.jsonl --out /private/cpf-main/report.json
```

Set distinct model-server URLs in the config or use the same endpoint URL with a different configured served ID if switching servers. Keep config unchanged between stages. No GPU, cloud budget, model endpoint, or upstream proof build was used by this local fixture. Only the mock server simulates usage and responses.
