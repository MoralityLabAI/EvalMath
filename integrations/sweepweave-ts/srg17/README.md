# SRG-17: Reasoning demand reference gyms

[Mathematical note](../../../paper/storyworld_reasoning_phase_transitions.md) · [Planning and belief receipt](../../../output/evaluation_storyworld_reasoning/srg17_reasoning_phases.json) · [Order witness receipt](../../../output/evaluation_storyworld_reasoning/srg17_order_witness.json)

Node 20+ from EvalMath root:

```sh
node integrations/sweepweave-ts/srg17/verify.mjs
node integrations/sweepweave-ts/srg17/local.mjs stage /tmp/srg17-planning planning
node integrations/sweepweave-ts/srg17/local.mjs stage /tmp/srg17-belief belief
node integrations/sweepweave-ts/srg17/local.mjs stage /tmp/srg17-order order
```

Default planning pilot: 28 factorial conditions, 1286 public packets (one matched tape). Default belief pilot: 16 base tables, one actual world per table, all four depths and both complement arms (128 packets). Default order pilot: 24 pairs (48 packets). The full public reference receipts are larger; no full-corpus model run is implied. Optional arguments after family are a nonzero uint32 seed and repeats, with family-specific caps. Use fresh directories. For held-out runs, freeze fresh seeds privately and isolate model_input from verifier files, seeds and private states.

```sh
FAMILY=planning # or belief or order
node integrations/sweepweave-ts/srg08/run-local.mjs \
  --suite /tmp/srg17-$FAMILY --kind planning \
  --model "$MODEL" --checkpoint-sha256 "$SHA" \
  --runtime-label "$RUNTIME" --run-label bonsai-srg17-$FAMILY \
  --max-tokens 1024 --out /tmp/bonsai-srg17-$FAMILY
node integrations/sweepweave-ts/srg17/local.mjs score \
  /tmp/srg17-$FAMILY /tmp/bonsai-srg17-$FAMILY/submissions.jsonl
```

The model returns one legal action ID in a JSON object; the existing runner attaches the task ID. Planning reports realized/conditional utility and informative accuracy; belief reports depth-specific correctness; order reports both-correct pairs and first-action regret. No production editor or Godot changes. Core tests executed in isolated ECMAScript, standalone Node/HTTP and actual inference pending.
