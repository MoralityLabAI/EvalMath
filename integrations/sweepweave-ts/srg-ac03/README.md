# SRG-AC03

[Registered protocol](PROTOCOL.md) · [Report](../../../paper/storyworld_upstream_evidence_acquisition.md) · [Frozen selection](../../../output/evaluation_storyworld_reasoning/srg_ac03_selection.json) · [Fresh validation](../../../output/evaluation_storyworld_reasoning/srg_ac03_validation.json).

Development PASS; frozen-policy fresh validation PASS under the registered paired-loss cap. Strict zero-loss fresh validation FAIL (two losses in cohort B). No authored-world promotion.

From EvalMath root, Node 20+:

    node integrations/sweepweave-ts/srg-ac03/cli.mjs dev_a
    node integrations/sweepweave-ts/srg-ac03/cli.mjs dev_b
    node integrations/sweepweave-ts/srg-ac03/cli.mjs select
    node integrations/sweepweave-ts/srg-ac03/cli.mjs validation

Core source executed in isolated ECMAScript. Standalone Node replay pending. The CLI pins the unchanged SWMD fixture and both runtime source blobs; it reproduces public receipts, including the frozen policy transfer. This is a policy optimizer, not a new SWMD fixture or production editor change. Keep verifier receipts and hidden states away from models under evaluation.
