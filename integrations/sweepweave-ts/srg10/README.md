# SRG-10: Adaptive evidence planning and posterior compression

Public calibration and public smoke controls; no live model inference. See [paper](../../../paper/storyworld_adaptive_evidence_and_joint_beliefs.md).

## Reproduce and stage

```bash
node integrations/sweepweave-ts/srg10/verify.mjs
node integrations/sweepweave-ts/srg10/local.mjs generate calibration_public /tmp/srg10-cal 2
node integrations/sweepweave-ts/srg10/local.mjs generate evaluation_private /tmp/srg10-private 1
```

The output must be fresh and private output outside the repository. Private generation reserves new seeds, not secret family definitions or guaranteed-disjoint reliability configurations. Only send model_input/ to a model; keep verifier/ with the evaluator. Do not train on the public diagnostic and then report the same data as test performance.

## Run on a local model

Use SRG-08's loopback-only planning runner with the actual server model ID, checkpoint SHA256 and runtime label. The supplied example assumes an already-running llama.cpp-compatible server. It does not configure the model or architectural passes.

```bash
node integrations/sweepweave-ts/srg08/run-local.mjs \
  --suite /tmp/srg10-cal --kind planning \
  --model "$MODEL" --checkpoint-sha256 "$SHA" \
  --runtime-label "$RUNTIME" --run-label bonsai-srg10 \
  --max-tokens 1024 --out /tmp/bonsai-srg10
node integrations/sweepweave-ts/srg10/local.mjs score /tmp/srg10-cal /tmp/bonsai-srg10/submissions.jsonl
```

Repeat with Inky and frozen input, then select model settings before materializing the final private suite. Submit {id,action} JSONL. The scorer reports utility, regret and optimal actions by family, observer, stage and horizon. Runtime continuation is oracle-optimal after the first submitted action; this is not a full model rollout. Gold and public controls are deterministic exact-mass fixtures.

Standalone Node filesystem/HTTP execution, private evaluation and actual local model runs have not yet been performed. The production editor remains unchanged.
