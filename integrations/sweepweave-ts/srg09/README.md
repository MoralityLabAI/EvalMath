# SRG-09: Evidence provenance and interaction margins

Public, fixed diagnostic suite. See [mathematical paper](../../../paper/storyworld_noisy_belief_provenance.md) and `output/evaluation_storyworld_reasoning/srg09.json`, `srg09_scorer.json` from repo root.

## Local replay

```bash
node integrations/sweepweave-ts/srg09/verify.mjs
node integrations/sweepweave-ts/srg09/local.mjs stage /tmp/srg09-public
```

The stage path must be fresh. The manifest hashes source and data. Only `model_input/` goes to a model. This is a public diagnostic; it does not produce a secret holdout.

For Bonsai or Inky with an existing local OpenAI-compatible server, use the SRG-08 planning runner and specify the actual checkpoint SHA256 and served model ID.

```bash
node integrations/sweepweave-ts/srg08/run-local.mjs \
  --suite /tmp/srg09-public --kind planning \
  --model "$MODEL" --checkpoint-sha256 "$SHA" \
  --runtime-label "$RUNTIME" --run-label bonsai-srg09 \
  --endpoint http://127.0.0.1:8080/v1/chat/completions \
  --max-tokens 1024 --out /tmp/bonsai-srg09
node integrations/sweepweave-ts/srg09/local.mjs score evidence /tmp/srg09-public /tmp/bonsai-srg09/submissions.jsonl
```

Evidence submissions use `{id,action}`. Author provenance repair submissions use `{id,line,before,after}`; the SRG-08 Boolean-author mode does not accept these patches. Supply the public author packet to your own local author prompt, validate JSON and submit the patch rows:

```bash
node integrations/sweepweave-ts/srg09/local.mjs score author /tmp/srg09-public /tmp/author-patches.jsonl
```

The author verifier requires both numerical counterfactual coverage and the intended full-keyring read set. The evidence scorer reports weighted expected utility and regret, assuming optimal continuation. Standalone CLI and HTTP model execution have not yet run; source-level reference and scorer functions were executed in the isolated JS environment.

Do not import the public diagnostic gold as training examples for models evaluated on the same data. No private reliability family, real model inference or editor integration has been completed.
