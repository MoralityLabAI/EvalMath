# SRG-15: Radio repair and partial-information policy evaluation

See [paper](../../../paper/storyworld_radio_repair_and_belief_policy.md).

The radio repair fails promotion. The observation benchmark uses the unchanged SRG-13 candidate. Source and scorer functions were executed in the isolated JS runtime. Standalone Node, real model inference, independent private evaluation and production editor work remain outstanding.

```bash
node integrations/sweepweave-ts/srg15/verify.mjs radio_a
node integrations/sweepweave-ts/srg15/verify.mjs radio_b
node integrations/sweepweave-ts/srg15/verify.mjs radio_validation
node integrations/sweepweave-ts/srg15/verify.mjs belief
node integrations/sweepweave-ts/srg15/local.mjs stage /tmp/srg15-public
```

The output directory must be fresh. The fixed public diagnostic consists of 940 projected observation-history packets for goal4/H3. The scorer rebuilds the full latent trees and evaluates a complete submitted policy with no oracle continuation. Only send model_input/ to a model. Provide the same world-rule/source familiarity protocol for all models; the observed packet alone does not necessarily specify the finite empirical prior. Gold is public for replay but must not be sent to a model or used to train a model evaluated on this corpus.

Use SRG-08's local planning runner with an existing local OpenAI-compatible server. Record actual checkpoint identity, runtime and inference settings.

```bash
node integrations/sweepweave-ts/srg08/run-local.mjs \
  --suite /tmp/srg15-public --kind planning \
  --model "$MODEL" --checkpoint-sha256 "$SHA" \
  --runtime-label "$RUNTIME" --run-label bonsai-srg15 \
  --max-tokens 1024 --out /tmp/bonsai-srg15
node integrations/sweepweave-ts/srg15/local.mjs score /tmp/srg15-public /tmp/bonsai-srg15/submissions.jsonl
```

Submit {id,action} JSONL. The scorer reports informative-row correctness, weighted first-action utility/regret, and actual policy success. A high all-row accuracy can be misleading because 887 rows tie all actions. The first-legal baseline has 887/940 row accuracy, 0/53 informative accuracy, and 1/128 rollout success versus the oracle's 19/128.
