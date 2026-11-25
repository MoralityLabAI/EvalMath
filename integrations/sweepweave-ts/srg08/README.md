# SRG-08: Authoring formula synthesis, bounded memory and contingent planning

SWMD-SRG/2 reference curriculum. All reported results are deterministic reference and mock-protocol controls, not trained model performance. The production TypeScript editor remains unchanged.

## Evidence

Three public control seeds cover training, calibration and a deliberately public evaluation-family smoke. The formula families are split by linear threshold, metric ball membership and paired interactions. Each has K=4, 8, 16. The memory and planning families repeat across splits with different procedural instances; do not claim that they are held-out families.

- 9 synthesis worlds: 626/626 multilevel reference checks, 626/626 executed classification transitions, 197424/197424 exhaustive binary assignments at magnitude 0.5. Empty gates pass 321/626 multilevel inputs; inverted gold passes 0/626. Each coordinate has a binary influence witness, 84 witnesses in total. The gate must be synthesized from the textual mathematical specification, examples, and a FALSE hole. The negative fallback does not contain the complementary formula. This is a finite test domain and does not certify every continuous input.
- 18 memory worlds: 288 complete cue traces, 576 correct/wrong report transition checks, 288 final observations checked for absence of hidden coordinate values. A forced clear step erases the last cue before the query is revealed. The parity register requires one bit for exact recall. The indexed recall task requires K bits for deterministic perfect recovery over all K-bit inputs and all final indices: if two input strings collide in the register, an index on which they differ forces an error on one. K bits suffice by storing the input. For b retained prefix bits and an independent uniform index, guessing on unretained bits gives (K+b)/(2K); this is a constructive policy, not an optimal partial-memory bound. The zero-memory/current-only accuracy is 1/2 under the independent uniform prior, and full history gives 1. Finite sampled labels need not have perfectly balanced frequencies.
- 27 planning worlds, 54 exact initial-budget oracle checks, 27 post-survey checks. Hidden regime and independent uniform prior, direct correct payoff 8, settlement 5, survey correct payoff 6, incorrect or unfinished payoff 0. Hidden initial regime gives expected utility 5 at budget 1 and 6 at full survey horizon 2, 3 or 5. An initially visible regime permits direct payoff 8. A missing survey cue lowers the post-survey value to 3 and makes settlement optimal at either budget. The oracle maximizes over common legal actions, partitions successor states by observation, and sums exact integer reward mass across cells. These are small deterministic finite-horizon POMDP fixtures.
- Actual runner/scorer functions exercised with deterministic reference callbacks, no HTTP or LLM calls: 9/9 formula submissions, 576/576 player gold decisions, 72/72 planning gold decisions, 288/288 streamed-memory reference decisions with parity one-bit and index K-bit registers. The runner rejects invalid memory, extra formula output fields, and illegal actions; the scorer counts duplicate, unknown, missing and rejected rows. Gold scoring verifies the scoring contract, not model ability.

Receipts: `output/evaluation_storyworld_reasoning/srg08.json` and `srg08_runner.json`.

## Run locally

Use a pinned EvalMath checkout, Node >=20, and a local OpenAI-compatible server. Generate a fresh private evaluation directory **outside** the repository. The private seed is generated locally and is distinct from public smoke seeds. The model runner reads only `model_input/`; do not upload the private verifier directory or put it in a model context.

```bash
node integrations/sweepweave-ts/srg08/local.mjs generate calibration_public /tmp/srg08-cal 1
node integrations/sweepweave-ts/srg08/local.mjs generate evaluation_private /tmp/srg08-private 1
```

Each split/replicate yields 3 synthesis tasks, 192 memory questions (96 history, 96 current-only), and 24 planning questions. The stream arm uses the 96 history items but gives the model only one cue per update and a fixed-width integer register. The gold manifest is bound to the generator and both runtime source hashes, as well as task and label files.

Set MODEL and SHA to the actual served model ID and checkpoint SHA256; record the actual server build, hardware/runtime and context/cache settings separately. Example calibration command:

```bash
node integrations/sweepweave-ts/srg08/run-local.mjs \
  --suite /tmp/srg08-cal --kind author \
  --model "$MODEL" --checkpoint-sha256 "$SHA" \
  --runtime-label "$RUNTIME" --run-label bonsai-author-cal \
  --endpoint http://127.0.0.1:8080/v1/chat/completions \
  --max-tokens 1024 --out /tmp/bonsai-author-cal
node integrations/sweepweave-ts/srg08/local.mjs score author /tmp/srg08-cal /tmp/bonsai-author-cal/submissions.jsonl
```

Use `--kind player` or `--kind planning` and a fresh output path to evaluate the respective tasks. For streaming:

```bash
node integrations/sweepweave-ts/srg08/run-local.mjs \
  --suite /tmp/srg08-cal --kind stream --memory-bits 1 \
  --model "$MODEL" --checkpoint-sha256 "$SHA" \
  --runtime-label "$RUNTIME" --run-label bonsai-stream-m1 \
  --out /tmp/bonsai-stream-m1
node integrations/sweepweave-ts/srg08/local.mjs score stream /tmp/srg08-cal /tmp/bonsai-stream-m1/submissions.jsonl
```

Repeat with register widths 0,1,2,4,8,16 and fresh output directories, then repeat with Inky on the same frozen input files. Record an actual architectural pass count if applicable with `--pass-count`; that flag is metadata only and does not configure the server. Use separate server processes or explicitly verify stateless request isolation and cache policy. The update prompt never includes the transcript or future query; the final prompt sees only the register and public observation. Text-model streaming changes the number of API requests; compare latency/tokens separately from accuracy. Do not infer a native neural-memory lower bound from this external register contract.

Stage `--max-tasks` only for smoke; scorer retains the full denominator and counts omissions. Run full matched calibration before fixing model settings and generating a genuinely private test. No model endpoint or GPU execution was available in this turn. Standalone Node filesystem/HTTP CLI execution and full CI remain pending; the exact core and callback functions were executed in the isolated JS environment.

## Data Goblin

`public/srg08_train.jsonl` contains 123 reference SFT examples: 3 synthesis, 96 full-history decisions and 24 belief-planning decisions. The committed ingestion manifest pins the source and Git blob. The train-only exporter rejects calibration input and excludes current-only memory, smoke and all reserved evaluation material. Keep siblings grouped by source world; this is pedagogical supervision, not an independent benchmark.

```bash
node integrations/sweepweave-ts/srg08/export-dg.mjs /tmp/srg08-dg-train 1
```

The local exporter creates a SHA256-bound manifest. The committed manifest uses a separate SRG ingestion schema; the existing Data Goblin game-adapter schema names four different games and is not falsely claimed to validate this dataset. No model training or architecture promotion is authorized by the reference receipt.

## Research next

SRG-09 should cross memory capacity with causal structure and observed belief depth: vary noise and cue timing, include histories with genuinely competing evidence, and add randomized effect-cost budgets, branch-dependent actions, and independently authored nonlinear formula specifications. Run matched local Bonsai/Inky calibration before claiming learned reasoning. Distinguish state dimension K, minimal sufficient observation, external-memory register width, adaptive planning horizon, and inference pass count.
