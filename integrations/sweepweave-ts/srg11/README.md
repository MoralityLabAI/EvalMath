# SRG-11: constrained authoring optimizer

See [paper](../../../paper/storyworld_authoring_optimizer.md) and `output/evaluation_storyworld_reasoning/srg11.json`, `srg11_envelope.json`.

Replay from the EvalMath checkout:

```bash
node integrations/sweepweave-ts/srg11/verify.mjs
```

Both calibration-selected candidates fail frozen public validation. Keep the original worlds unchanged. The economics fixture requires its explicit external probability/payoff contract; loading only its SWMD prose does not implement the scoring model. The Reservoir Dogs candidate modifies one Q constant only; the original source is the authority for all other mechanics.

No live model or standalone Node run has occurred. The source functions and matched replay ran in the isolated ECMAScript environment. The envelope is a post-selection diagnostic, never a new test set.
