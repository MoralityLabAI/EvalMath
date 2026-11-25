# SRG-19

[Protocol](PROTOCOL.md) · [Mathematical report](../../../paper/storyworld_stochastic_belief_chains.md) · [Public receipt](../../../output/evaluation_storyworld_reasoning/srg19_belief_chains.json)

From repo root run `node integrations/sweepweave-ts/srg19/cli.mjs verify`. Stage a balanced pilot with `node integrations/sweepweave-ts/srg19/cli.mjs stage /tmp/srg19-pilot 0x53521901 1` and score JSONL id/action pairs with `node integrations/sweepweave-ts/srg19/cli.mjs score /tmp/srg19-pilot /tmp/submissions.jsonl`. Public posterior-class planning only; separate history inference and private seed evaluation remain pending.
