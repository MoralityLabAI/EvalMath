# SRG-14: Full-history causal intervention audit

The original SRG-05 world and frozen SRG-13 candidate are unchanged. See [paper](../../../paper/storyworld_full_history_causal_interventions.md) and `output/evaluation_storyworld_reasoning/srg14.json`.

Run from EvalMath root:
```bash
node integrations/sweepweave-ts/srg14/verify.mjs original_a
node integrations/sweepweave-ts/srg14/verify.mjs original_b
node integrations/sweepweave-ts/srg14/verify.mjs candidate_a
node integrations/sweepweave-ts/srg14/verify.mjs candidate_b
node integrations/sweepweave-ts/srg14/verify.mjs factorial
```

These are public finite diagnostic replays, with binary experimental goal utility and a full-state bounded reachability oracle. The underlying functions ran in the isolated JS environment. Standalone Node, model inference and production editor testing remain outstanding. The candidate's earlier promotion failure is unchanged.
