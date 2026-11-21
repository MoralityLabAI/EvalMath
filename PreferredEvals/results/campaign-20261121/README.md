# PreferredEvals v2 local rollout campaign, 2026-11-21

First live rollouts of the PreferredEvals gym on local models. Ternary Bonsai 2 27B and Qwen3-4B-Instruct-2507 both ran on one RTX 5080 Laptop GPU (16 GB). Every result here is **development evidence**:
- the task samples are small;
- the readout is unsealed;
- no confirmation claim is made.

The comparison plan ([`registration.json`](registration.json)) was committed and pushed in bffa41b, before any Qwen rollout. Bonsai results were partly visible when it was written.

## Headline

| Category | Benchmark (harness) | Bonsai 27B | Qwen3-4B | Paired effect (bootstrap 95%) |
| --- | --- | --- | --- | --- |
| Math word problems | GSM8K, primeintellect/gsm8k 0.1.4 (vf-run 0.4.1, math_verify) | 12/12 (6 roots) | 12/12 | 0.00 |
| Long context | NIAH, Inkling Verify 94fd95b, 4K and 16K | 8/8 | 8/8 | 0.00 |
| Agentic tools (MCP) | mcp-sqlite 0.1.0 (vf-run 0.4.1, exact match) | 6/8 | 3/8 | +0.375 [-0.375, 1.000] |
| Science knowledge, HLE stand-in | MMLU-Pro physics, chemistry, biology (gym runner) | 7/8 | 5/8 | +0.25 [-0.375, 0.875] |
| Research taste, public proxy | ICLR 2026 oral vs rejected pairs, both orders (gym runner) | 11/24 (12 roots) | 9/24 | +0.083 [-0.292, 0.542] |
| Recursive reasoning, generated | Multi-hop variable chains, 2 to 12 hops (gym runner) | 11/12 with reasoning; 0/12 with thinking off | 0/12 | +0.917 [0.667, 1.000] |
| Software engineering | SWE-bench Lite oracle single-shot, official harness 5.0.2 | 0/6 | 0/6 | 0.00 |

What the table shows:

- **Neither model separates from the other on most sets.** Both saturate GSM8K and NIAH at these sizes. Both fail every SWE instance: the harness cannot apply their patches (malformed hunks), and the one Bonsai patch that applied left the tests failing.
- **Multi-hop is the one clear difference.** Bonsai with its default hidden reasoning solves 11 of 12 chains; with thinking off it solves none. Qwen3-4B-Instruct has no thinking mode, and under the gym's answer-only protocol it also solves none. So the registered Bonsai-versus-Qwen multi-hop effect (p = 0.00098, Holm 0.0078) measures reasoning against no reasoning, not 27B against 4B. The like-for-like exploratory comparison (Bonsai with thinking off against Qwen) is 0/12 against 0/12.
- **The research-taste proxy is near or below chance for both models** (0.46 and 0.38). Venue decisions are a weak label for taste, and these pairs are not TASTE.
- **FSI-01 verdicts are "suggestive" or "inconclusive", never "confirmed".** The readout is unsealed, and every family has fewer than the 20 independent roots the FSI-01 policy asks for.

## Attempted and scored counts

| Run | Attempts | Scored | Correct | Roots | Outcomes |
| --- | --- | --- | --- | --- | --- |
| gsm8k-bonsai / gsm8k-qwen | 12 / 12 | 12 / 12 | 12 / 12 | 6 / 6 | all correct |
| niah-bonsai / niah-qwen | 8 / 8 | 8 / 8 | 8 / 8 | 8 / 8 | all correct |
| sqlite-bonsai / sqlite-qwen | 8 / 8 | 8 / 8 | 6 / 3 | 8 / 8 | wrong 2 / wrong 5 |
| mmlupro-bonsai / mmlupro-qwen | 8 / 8 | 8 / 8 | 7 / 5 | 8 / 8 | wrong 1 / wrong 3 |
| taste-bonsai / taste-qwen | 24 / 24 | 24 / 24 | 11 / 9 | 12 / 12 | Bonsai: wrong 12, format invalid 1; Qwen: wrong 15 |
| multihop-bonsai / multihop-nocot-bonsai / multihop-qwen | 12 / 12 / 12 | 12 / 12 / 12 | 11 / 0 / 0 | 12 each | wrong 1 / 12 / 12 |
| swe-bonsai / swe-qwen | 6 / 6 | 6 / 6 | 0 / 0 | 6 / 6 | Bonsai: patch not applicable 5, unresolved 1; Qwen: patch not applicable 6 |

Totals:
- Bonsai: 90 attempts, 90 scored, 55 correct (multi-hop counted in both conditions).
- Qwen: 78 attempts, 78 scored, 37 correct.
- No attempt of the final runs ended in an infrastructure or grader error.

Full per-attempt records are in [`ledger.jsonl`](ledger.jsonl), the scorecard in [`scorecard.md`](scorecard.md), and the FSI-01 manifests and results in [`campaign_summary.json`](campaign_summary.json).

## Failure ledger

| Class | Count | Where |
| --- | --- | --- |
| Model failure: wrong answer | Bonsai 29 (12 of them in the thinking-off multi-hop run), Qwen 35 | see the table above |
| Model failure: output outside the format | Bonsai 6 (1 taste reply, 5 inapplicable SWE patches), Qwen 6 (SWE) | SWE patches failed with `malformed patch` or `Patch Apply Failed` |
| Grader failure | 0 | all six gold patches round-trip through SWE-bench's `extract_diff`, so patch extraction was not the cause |
| Infrastructure failure (final runs) | 0 | |
| Infrastructure failure (discarded first Bonsai attempt) | 56 prompt-runner calls; 1 of 12 GSM8K episodes; 2 of 2 mcp-sqlite episodes; NIAH stopped after 2 samples | The llama-server lease was stopped from outside the job at 16:51. Every run of that attempt was rerun from scratch; its receipts are summarised in `receipts/relay_calls_failed_attempt1.jsonl` |
| Missing dependency | HLE text, DeepSWE, PaperBench | see Blocked |

## Blocked

- **HLE (Inkling Verify `hle`).** `cais/hle` is gated on Hugging Face, and this account has no access; `prepare` fails with `DatasetNotFoundError`. To unblock it, request access at https://huggingface.co/datasets/cais/hle, then run the `inkling-hle` profile. A separate judge model is needed: HLE self-judges by default. MMLU-Pro science is reported as a public stand-in, labelled as such.
- **DeepSWE (Inkling Verify `deepswe`).** It needs rootless Podman on native x86-64 Linux, plus four-hour agent budgets. Podman is not installed in this WSL. SWE here is SWE-bench's own single-shot oracle-retrieval setting instead, graded by the official harness.
- **PaperBench.** It needs multi-hour agent runs and rubric judging. No executable experimental-design proxy was staged.
- **Prime sandbox tasksets.** Excluded: paid sandboxes.

## Setup

| Item | Bonsai 27B | Qwen3-4B |
| --- | --- | --- |
| Weights | `prism-ml/Ternary-Bonsai-2-27B-gguf` rev 94dd51cd, PTQ1_0 GGUF, sha256 `53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3` | `Qwen/Qwen3-4B-Instruct-2507` snapshot cdbee75f (bf16), converted to Q8_0 GGUF with the PrismML `convert_hf_to_gguf.py`; sha256 `c892d3128b07169d55d67eb8aa11e071f8e47d3b341eac2c463c9cb5e10d65bc` |
| Server | PrismML llama-server b10743 (adfffbe41), CUDA, all layers on the GPU, `--reasoning-format deepseek --reasoning-budget 1536` | same server; no reasoning flags (the model has no thinking mode) |
| Slots | 2 × 32,768 tokens | 2 × 24,576 tokens, f16 KV. Its full-attention KV cache does not fit 2 × 32K beside the weights; the largest campaign prompt plus output is about 20K tokens |
| GPU memory held | 10,313 MiB (vramorama lease 11G) | 11,315 MiB (lease 13G) |
| Decode speed, median per slot | 13.2 tokens/s | 76.1 tokens/s |
| Output budget | 4,096 tokens per call for every benchmark | same |

Sampling:
- temperature 0 for the gym runner sets, NIAH and SWE;
- temperature 0.6 for GSM8K (two attempts per problem) and mcp-sqlite;
- seed 42.

How the harnesses reached the models:
- The WSL harnesses (vf-run, Inkling Verify, the SWE runner) reached the Windows server through the HybridTRMLDT `MCP/hubrun/proxy.py` relay, raw arm, via Windows `curl.exe`.
- The relay strips `reasoning_content` from replies, so `reasoning_chars` is 0 in those receipts, but Bonsai's thinking tokens are included in its completion token counts.
- The gym runner called the server directly.

Wall time:
- Bonsai: GSM8K 5 min 14 s; NIAH 1 min 41 s; mcp-sqlite 7 min 1 s; taste pairs 22 min; MMLU-Pro 6 min 20 s; multi-hop 8 min 40 s; multi-hop with thinking off 10 s; SWE generation 22 min 13 s.
- Qwen: GSM8K 42 s; NIAH 27 s; mcp-sqlite 48 s; taste pairs 6 s; MMLU-Pro 2 s; multi-hop 3 s; SWE generation 1 min 27 s.
- The SWE harness took about 1 minute per model, with cached Docker images.

## Task provenance

| Set | Source | Licence / status | Selection |
| --- | --- | --- | --- |
| GSM8K | `primeintellect/gsm8k` 0.1.4 (Prime hub), test split | public | first 6 problems, 2 attempts each |
| NIAH | Inkling Verify synthetic UUID retrieval | generated by the harness | 4,000 and 16,000 tokens × depths 25 and 75 × 2 cases; prompts are built per tokenizer (Qwen3.5 tokenizer for Bonsai, Qwen3 for Qwen), so pairs share a cell and seed, not identical text |
| mcp-sqlite | `mikqu/mcp-sqlite` 0.1.0 | public | first 8 of 57 tasks; the `openai/gpt-5.4-nano` judge removed; scored by the taskset's `exact_match` |
| MMLU-Pro science | `TIGER-Lab/MMLU-Pro` @ b189ec76 | MIT | 8 physics, chemistry and biology questions in seeded hash order |
| Research-taste proxy | `JerMa88/ICLR_Peer_Reviews_2026` @ 4054df6b (OpenReview ICLR 2026) | ICLR submissions are CC BY 4.0 | 12 pairs, one oral and one rejected paper from the same primary area; the label is the venue decision, not expert taste; not Anthropic TASTE. One paper labelled "Conditional Accept (Oral)" counts as an oral |
| Multi-hop | generated by `build_public_sets.py multihop`, seed 2026 | development control | 3 chains at each of 2, 4, 8 and 12 hops, with a distractor chain |
| SWE-bench | `princeton-nlp/SWE-bench_Lite_oracle` @ 6fc5a853 | public | the 6 shortest oracle prompts among the 21 Lite instances whose gold patch resolves on this host |

GSM8K, MMLU-Pro and SWE-bench Lite are old enough to be in both models' training data. ICLR 2026 decisions postdate Qwen3-4B-Instruct-2507 but may not postdate Bonsai 2. Source-task reuse: the SWE instances are the gold-valid subset of the 26 used in the HybridTRMLDT end-to-end run.

## Statistics

Every paired comparison was exported as an EvalMath FSI-01 manifest and evaluated with `spiral_ln.evaluation_finite_sample`:
- **Units.** Roots are independent problems; attempts and presentation orders stay inside their root.
- **Declarations.** The manifests declare the hypotheses preregistered, roots independent and pair labels exchangeable. `independence_note` in `campaign.json` gives the justification; independence is declared, not proven.
- **Tests.** Exact McNemar where one case per root; an exact cluster sign-flip test where roots repeat (GSM8K, taste).
- **Interval.** Equal-cluster bootstrap.
- **Multiplicity.** Holm over the 8 registered comparisons.
- **Readout.** Unsealed, so no verdict can reach "confirmed".

## Gym fixes made for these runs

- **Bash harness by default.** vf-run 0.4.1 falls back to its bash harness when neither the run nor the taskset names one, which would have given the model a shell on the host for GSM8K. The Prime plan now requires `--harness` (`null` for chat-only tasksets, `taskset` to keep a taskset's own).
- **External harness settings.** `external.py` now passes the output budget, temperature, concurrency, Inkling `--data-dir` and verbatim native arguments.
- **Runner changes.** Choice tasks accept up to 10 options. Exact-text grading strips one layer of quotes and one trailing period. Receipts record reasoning length. `--request-extra` (recorded in `run.json`) carries options such as `enable_thinking=false`.
- **New modules:**
  - `build_public_sets.py` builds the three prompt sets, writing byte-exact LF files;
  - `swebench_oracle.py` handles SWE generation and harness-report scoring;
  - `campaign.py` produces the ledger, scorecard and FSI-01 pairing.

## Reproduce

The scripts that drove these runs are in [`scripts/`](scripts). They use this host's paths: WSL `/root/pe2`, Windows `C:\Users\patri\Documents\Codex\pe2-work`.

```bash
python PreferredEvals/gym/build_public_sets.py multihop --out PreferredEvals/gym/sets/multihop --per-depth 3 --seed 2026
python PreferredEvals/gym/runner.py run --tasks PreferredEvals/gym/sets/mmlu-pro-science/tasks.jsonl \
  --benchmark public-mmlu-pro-science --out runs/mmlupro-M --model M --base-url http://127.0.0.1:18127/v1 \
  --temperature 0 --seed 42 --max-tokens 4096
python PreferredEvals/gym/runner.py score --run-dir runs/mmlupro-M \
  --labels PreferredEvals/gym/sets/mmlu-pro-science/labels.jsonl --out runs/mmlupro-M/scores.json
python PreferredEvals/gym/external.py --profile prime-v041 --taskset gsm8k --harness null --model M \
  --base-url URL --out runs/gsm8k-M --limit 6 --rollouts 2 --max-tokens 4096 --temperature 0.6 --execute
python PreferredEvals/gym/external.py --profile inkling-niah --model M --base-url URL --out runs/niah-M \
  --limit 8 --data-dir DATA --max-tokens 4096 --temperature 0 --workdir inkling-verify --execute
python PreferredEvals/gym/campaign.py --root PreferredEvals/results/campaign-20261121
```

## Registered eight-comparison ledger

`gym/campaign_report.py` reports the frozen family of eight from [`receipt_index.json`](receipt_index.json). It reads one pair of files per comparison, written by `gym/campaign.py`:
- `fsi/<comparison>/fsi-result.json`, the FSI-01 result with effect floor 0.10 and a family of 8;
- `fsi/<comparison>/paired.json`, the paired receipt.

All eight are observed. See [`registered_eight_status.md`](registered_eight_status.md) and [`registered_eight.json`](registered_eight.json). The report matches the scorecard: only the two multi-hop contrasts pass Holm (0.0078). Bonsai's reasoning drives both of them, and both stay development evidence.

```sh
python PreferredEvals/gym/campaign.py --root PreferredEvals/results/campaign-20261121
python PreferredEvals/gym/campaign_report.py \
  --registration PreferredEvals/results/campaign-20261121/registration.json \
  --index PreferredEvals/results/campaign-20261121/receipt_index.json \
  --out-json PreferredEvals/results/campaign-20261121/registered_eight.json \
  --out-md PreferredEvals/results/campaign-20261121/registered_eight_status.md
```

For a paired prompt comparison through `gym/compare.py`, the campaign values are `--minimum-effect 0.10 --planned-comparisons 8`. The script's defaults (0.05, one comparison) do not apply here.

## Next experiment

The cleanest open question is the multi-hop gap: how much reasoning does each model need at each depth? The proposed run has three parts:
- **Visible CoT for Qwen.** Give Qwen3-4B-Instruct a visible chain-of-thought condition, scored on a final `Answer:` line.
- **A budget sweep for Bonsai.** Sweep its thinking budget (0, 64, 256, 1,536 tokens).
- **Larger samples.** Raise the generator to 20 chains per depth, so that each family clears FSI-01's 20-root floor.

Then register the effect floor and seal a fresh generator seed before the readout. That gives a confirmatory test of reasoning tokens per hop, the quantity that compact looped or recurrent policies (TRM, RLT, HRM) would need to beat.

## New outside research-taste source

[Ideation Arena, EMNLP 2026](https://aclanthology.org/2026.emnlp-main.688/) uses blind researcher preference comparisons. The [Hugging Face data](https://huggingface.co/datasets/yolo1213811/research-ideation-arena-dataset) is `CC BY-NC 4.0`. Its dataset viewer currently fails because `queries.json` and `final_ideation_results_with_response.json` have distinct schemas; download the latter directly, keep both under their pinned upstream revision, and use `gym/ideation_arena.py` to extract development task and label files separately. `D4` is a configurable selection placeholder: verify dimension semantics against the paper and original labeling rules before results are published.

```sh
pip install ijson
python PreferredEvals/gym/ideation_arena.py \
  --comparisons /path/to/final_ideation_results_with_response.json \
  --out-tasks runs/ideation-arena/tasks.jsonl \
  --out-labels runs/ideation-arena/labels.jsonl \
  --dimension D4 --limit 24 --ack-noncommercial
```

Treat task roots as research-context groups; further linked ideas and researchers may induce additional dependence. This tests judge agreement with recorded human preferences, not the ability of Bonsai or Qwen to generate original high-quality proposals.
