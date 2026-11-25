# SRG-16: Opportunity-balanced storyworld policy benchmark

See [mathematical note](../../../paper/storyworld_opportunity_balanced_reasoning.md) and [public receipt](../../../output/evaluation_storyworld_reasoning/srg16_opportunity_balance.json).

Node 20+ from EvalMath root:

```sh
node integrations/sweepweave-ts/srg16/verify.mjs
# A low-cost pilot: one matched replicate per factorial condition.
node integrations/sweepweave-ts/srg16/local.mjs stage /tmp/srg16-pilot 0x53521601 1
# Default public diagnostic: 32 replicates per factorial condition.
node integrations/sweepweave-ts/srg16/local.mjs stage /tmp/srg16-public
```

Use a fresh output directory. Send only model_input/planning.jsonl to the existing SRG-08 local runner. No verifier labels, seed, private SWMD source or future states may enter model prompts. The full public diagnostic has 23484 packets; use the balanced one-replicate pilot first, rather than truncating a condition-ordered corpus. A fresh private seed must be frozen separately for any held-out evaluation.

```sh
node integrations/sweepweave-ts/srg08/run-local.mjs \
  --suite /tmp/srg16-pilot --kind planning \
  --model "$MODEL" --checkpoint-sha256 "$SHA" \
  --runtime-label "$RUNTIME" --run-label bonsai-srg16 \
  --max-tokens 1024 --out /tmp/bonsai-srg16
node integrations/sweepweave-ts/srg16/local.mjs score \
  /tmp/srg16-pilot /tmp/bonsai-srg16/submissions.jsonl
```

The runner expects one JSON object containing the selected legal action ID. Scoring checks source and corpus hashes, regenerates the verifier corpus, and composes the submitted policy on the sampled roots. Report informative accuracy and weighted utility alongside raw accuracy. Report all-correct campaigns as a separate objective. The verifier-only SWMD generator checks actual SRG/2 reaction effects and observation visibility. No Godot dependency or production editor change.

The committed core and upstream SWMD runtime were executed in isolated ECMAScript; standalone Node CLI and local model inference remain pending.
