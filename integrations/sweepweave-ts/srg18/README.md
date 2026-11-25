# SRG-18

[Protocol](PROTOCOL.md) · [Report](../../../paper/storyworld_causal_reaction_chains.md) · [Receipt](../../../output/evaluation_storyworld_reasoning/srg18_causal_chains.json)

Run `node integrations/sweepweave-ts/srg18/cli.mjs verify` from the repository root. Stage a one-tape balanced pilot with `node integrations/sweepweave-ts/srg18/cli.mjs stage /tmp/srg18-pilot 0x53521801 1`. Score JSONL id/action pairs with `node integrations/sweepweave-ts/srg18/cli.mjs score /tmp/srg18-pilot /tmp/submissions.jsonl`. Public diagnostic only. Use a fresh independently frozen seed for actual held-out model evaluation. Standalone CLI and SRG-08 runner compatibility remain unverified.
