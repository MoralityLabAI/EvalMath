# SRG-20

[Protocol](PROTOCOL.md) · [Report](../../../paper/storyworld_nested_delegation.md) · [Receipt](../../../output/evaluation_storyworld_reasoning/srg20_nested_delegation.json)

Run `node integrations/sweepweave-ts/srg20/cli.mjs verify` from the repository root. Stage separate matched history, posterior and inference pilots with `node integrations/sweepweave-ts/srg20/cli.mjs stage <new-dir> <history|posterior|inference> 0x53522001 1`. Score via `node integrations/sweepweave-ts/srg20/cli.mjs score <dir> <submissions.jsonl>`. Policy submissions use id/action, inference uses id/probabilities. Public diagnostic only; freeze an independent private seed for model evaluation. No production editor integration.
