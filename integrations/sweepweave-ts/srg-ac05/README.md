# SRG-AC05: Counterfactual difficulty hardening

[Protocol](PROTOCOL.md) · [Report](../../../paper/storyworld_counterfactual_difficulty_hardening.md) · [Frozen selection](../../../output/evaluation_storyworld_reasoning/srg_ac05_selection.json) · [Validation](../../../output/evaluation_storyworld_reasoning/srg_ac05_validation.json) · [Post-hoc matched pairs](../../../output/evaluation_storyworld_reasoning/srg_ac05_pairs.json).

Formula-hardening gate FAIL. Unchanged world, legal mixed-policy root populations contain opposite-optimum conflicts; deduplicated disjoint witness extraction establishes exact weak-channel 50% ceiling and full-ledger 100% on the conditional pair populations.

From EvalMath root with Node 20+:

    node integrations/sweepweave-ts/srg-ac05/cli.mjs dev_a
    node integrations/sweepweave-ts/srg-ac05/cli.mjs dev_b
    node integrations/sweepweave-ts/srg-ac05/cli.mjs select
    node integrations/sweepweave-ts/srg-ac05/cli.mjs validation
    node integrations/sweepweave-ts/srg-ac05/cli.mjs pairs

Core executed in isolated ECMAScript against the pinned runtime. Standalone Node replay pending. Public diagnostic only; no model inference, private evaluation or production editor change.
