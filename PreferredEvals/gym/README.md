# PreferredEvals rollout gym

**Status:** Executable local-model prompt runner and launch adapters for selected external native harnesses. The remaining catalog entries are research references pending integration. This is PreferredEvals **v2** (our experiment/receipt standard), distinct from Prime Intellect's `verifiers.v1` API.

The gym is intentionally split. The simple prompt runner sends real, explicitly supplied tasks to any OpenAI-compatible endpoint and saves the model's actual text and usage. Native harnesses remain responsible for interactive, coding, multimodal or tool-using tasks. The CPU test server supplies scripted output solely to check integration. It is never counted as a model result.

## Supported now

| Family | Executable path | Upstream / access | What is measured |
|---|---|---|---|
| Research-taste proposal pairs | `runner.py run` + `score` | User-supplied, permissioned TASTE or new openly labelled research pairs | Pairwise preference agreement, normal/swapped order, roots |
| Small multiple-choice and exact text | `runner.py run` + `score` | Licensed/public JSONL task sets supplied locally | Exact choice or normalized-text success, format validity |
| Coding | `external.py --profile inkling-deepswe` | Pinned Inkling Verify, rootless Podman and its images | Native patch tests, provider receipts |
| Scientific knowledge | `external.py --profile inkling-hle` | Inkling Verify, public preparation and judge selection | Native HLE score, judge caveats |
| Long context | `external.py --profile inkling-niah` | Inkling Verify and tokenizer | Native UUID retrieval by context length |
| Vision and audio | `inkling-mmmu-pro`, `inkling-mmau` | Multimodal model, media and optional container tools | Native task metrics |
| Prime agentic tool/tasksets | `external.py --profile prime-v041` | Installed Prime Verifiers v0.4.1 taskset and harness | Native episodes/traces, tool and task scores |

**Research taste requires care:** Anthropic TASTE releases the 92 proposal comparisons to researchers by request, not as a bundled public test dataset. Our `demo-research-taste` fixture consists of *two newly written synthetic examples*. Scores from that fixture are not TASTE scores, and its author-picked answer letters are not expert labels. TASTE reuses proposals across pairs, so statistical roots must account for shared proposal identity rather than treating 92 pairs as independent.

Prime v0.4.1 changed its local CLI to **`vf-run`**. Pin to that release or its SHA. `vf-eval` belongs to older Verifiers versions. The native plan checks this only at the command level; an actual external run needs installed dependencies, a serving model and the taskset. Newer versions may change the CLI again.

## 1. Use a local model with a real task file

Create *separate* task and label files:

```json
{"schema":"preferred-evals/prompt-task-v1","task_id":"research-question-001","root_id":"research-program-001","benchmark_id":"external-approved-set","kind":"pairwise","question":"Which proposal is scientifically stronger?","proposal_a":"...","proposal_b":"..."}
```

```json
{"task_id":"research-question-001","answer":"A"}
```

Only task prompts are sent to inference. Labels stay offline until the separate `score` call. Supported `kind` values are `pairwise`, `choice` (2–6 enumerated options), and `exact_text`. Native agents are needed for everything requiring tools or external state changes. Stable root IDs and source revisions are the author's responsibility.

```bash
# Check the Bonsai/Qwen endpoint first from the environment running the gym:
curl http://127.0.0.1:18127/v1/models

# Development-only synthetic integration smoke. Substitute an authorized dataset for evaluation.
python PreferredEvals/gym/runner.py run \
  --tasks PreferredEvals/gym/examples/dev_pair_tasks.jsonl \
  --benchmark demo-research-taste --out runs/taste-dev-bonsai \
  --model bonsai-27b --base-url http://127.0.0.1:18127/v1 \
  --rollouts 2 --orders both --temperature 0 --max-tokens 32

python PreferredEvals/gym/runner.py score \
  --run-dir runs/taste-dev-bonsai \
  --labels PreferredEvals/gym/examples/dev_pair_labels.jsonl \
  --out runs/taste-dev-bonsai/scores.json
```

`run.json` holds model, source dataset SHA-256, sampling, task/root selection and run settings; `rollouts.jsonl` holds every response, format parse, usage and errors. The model never receives labels. Existing output directories are protected; `--resume` only works for an identical manifest. A remote model endpoint requires `--allow-remote` so task contents are not sent away without an explicit flag. A failed call is recorded as an infrastructure error rather than a wrong answer.

## 2. Pair two model runs and export FSI-01

```bash
python PreferredEvals/gym/compare.py \
  --candidate-run runs/taste-dev-bonsai \
  --baseline-run runs/taste-dev-qwen \
  --candidate-scores runs/taste-dev-bonsai/scores.json \
  --baseline-scores runs/taste-dev-qwen/scores.json \
  --out runs/pair.json --fsi-out runs/fsi01.json
PYTHONPATH=src python -m spiral_ln.evaluation_finite_sample \
  --manifest runs/fsi01.json --output runs/fsi01-result.json
```

Pairing requires identical datasets, task selection, order variants and labels. Samples and swapped presentations stay inside a task's `root_id`. The exported FSI manifest is **development/unsealed** by construction; for prospective confirmation, register the independent population, matched controls, effect floor and sealed readout separately through EvalMath.

## 3. Launch genuine external harnesses

```bash
# Show adapters and their resource requirements
python PreferredEvals/gym/external.py --list

# Prime Verifiers 0.4.1, local taskset and subprocess runtime; --prepare executes vf-run --dry-run.
python PreferredEvals/gym/external.py --profile prime-v041 --taskset gsm8k \
  --model bonsai-27b --base-url http://127.0.0.1:18127/v1 \
  --out runs/prime-gsm8k --limit 6 --rollouts 2 --workdir /path/to/verifiers \
  --prepare --execute

# Thinking Machines Inkling Verify on two coding tasks. Preparation can download data.
python PreferredEvals/gym/external.py --profile inkling-deepswe \
  --model qwen3-4b-instruct-2507 --base-url http://127.0.0.1:8095/v1 \
  --out runs/deepswe --limit 2 --rollouts 1 --workdir /path/to/inkling-verify \
  --prepare --allow-downloads --execute

# A fast long-context profile, after preparing a pinned tokenizer for the model.
python PreferredEvals/gym/external.py --profile inkling-niah \
  --model qwen3-4b-instruct-2507 --base-url http://127.0.0.1:8095/v1 \
  --out runs/niah --limit 5 --rollouts 1 --tokenizer /path/to/tokenizer \
  --workdir /path/to/inkling-verify --prepare --allow-downloads --execute
```

Without `--execute`, `external.py` only prints a command plan. Remote inference requires `--allow-remote`; Prime paid runtimes require `--allow-paid`; downloading benchmark data through `prepare` requires `--allow-downloads`. A `vf-run` process return code indicates process success or failure and cannot substitute for task-level grading. Native `traces.jsonl` and `summary.json` must be kept and inspected, including dropped/error episodes.

The DeepSWE example requires Linux x86-64 with rootless Podman. WSL on Windows needs a reachable host endpoint; verify its URL with `curl` from *inside WSL*. Prime packages and environment versions must be installed explicitly at the pinned release. HLE may use a self-judge by default, so record a separate judge when making score claims.

## 4. Import native Prime v0.4.1 episodes

The 0.4.1 `vf-run` runner saves **Episode** records in `traces.jsonl`, with one episode holding an attributed task, zero or more agent traces, a `dropped` status and weighted reward fields. Our `ingest_prime.py` consumes this current schema (and the matching serialized subset of earlier v1 files). Supply an **explicit** mapping from task key / ID to independent world root, then retain the original upstream trace file as the evidence artifact:

```bash
cat > runs/prime-root-map.json <<'JSON'
{"task-001": "world-01", "task-002": "world-02"}
JSON
python PreferredEvals/gym/ingest_prime.py \
  --traces /path/to/vf-run-output/traces.jsonl \
  --root-map runs/prime-root-map.json \
  --out runs/prime-summary.json
```

It records scored/dropped/unscored/error episodes separately and computes an equal-root descriptive reward only on scored traces. It doesn't substitute for native Prime judgment, nor does it certify that task roots are independent. Older `PreferredEvals/v2/prime_v1.py` remains the narrow historical importer for the serialized task/traces subset used in earlier development runs.

## 5. CPU smoke / CI

```bash
python -m unittest discover -s PreferredEvals/gym/tests -p 'test_*.py' -v
```

The integration tests start a scripted local HTTP Chat Completions server, run two prompt pairs in both orders, score against separate labels, test resume/remote safeguards, and check an unsealed root-clustered FSI-01 export. They validate the native command plans and the current Prime Episode importer, including dropped/error traces, without contacting external services. This verifies the gym pipeline. **It is not a Bonsai, Qwen, TASTE, HLE or SWE-bench result.**

## Next benchmark gaps

Full Verifiers/Petri/Bloom agentic suites need upstream-native adapters with version-pinned evaluators. PaperBench and TasteVal require available task data and human/reference rubric decisions. Our own generated tasks remain development controls. The catalog's 39 entries are not 39 executable benchmarks.
