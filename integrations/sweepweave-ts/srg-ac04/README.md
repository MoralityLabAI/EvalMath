# SRG-AC04: Shortcut resistance

[Protocol](PROTOCOL.md) · [Report](../../../paper/storyworld_shortcut_resistance.md) · [Registered receipt](../../../output/evaluation_storyworld_reasoning/srg_ac04_shortcut_resistance.json) · [Post-hoc subset receipt](../../../output/evaluation_storyworld_reasoning/srg_ac04_ledger_subsets.json).

From EvalMath root, Node 20+:

    node integrations/sweepweave-ts/srg-ac04/cli.mjs primary
    node integrations/sweepweave-ts/srg-ac04/cli.mjs subsets
    node integrations/sweepweave-ts/srg-ac04/cli.mjs verify

Core executed against the pinned SWMD runtime in isolated ECMAScript. Standalone Node replay remains pending. All-investigate meets the registered shortcut review flag; frozen upstream narrowly misses the conjunctive script thresholds but one additional binary review-presence coordinate suffices in the post-hoc lookup diagnostic. No actual model inference, production promotion, or private validation.
