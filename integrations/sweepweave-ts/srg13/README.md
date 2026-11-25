# SRG-13: Evidence-chain candidate (promotion FAIL)

Read [the paper](../../../paper/storyworld_evidence_chain_coordination.md) and `output/evaluation_storyworld_reasoning/srg13.json`. The candidate introduces three explicit investigation records and a final coordination register. It keeps original story text and eligibility gates. The source only supports review *requests* for some credits; manual author review remains necessary.

Replay from the EvalMath root (Node 20+):
```bash
node integrations/sweepweave-ts/srg13/verify.mjs development
node integrations/sweepweave-ts/srg13/verify.mjs validation0
node integrations/sweepweave-ts/srg13/verify.mjs validation1
```

The source-level numerical runs have executed; standalone filesystem replay has not. Neither the production editor nor the original world is changed. No model evaluation or training has been executed.
