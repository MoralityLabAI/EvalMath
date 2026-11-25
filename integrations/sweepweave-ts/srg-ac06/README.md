# SRG-AC06: Minimum sufficient observations and controlled K ladder

[Protocol](PROTOCOL.md) · [Report](../../../paper/storyworld_minimum_sufficient_reasoning.md) · [Calibration](../../../output/evaluation_storyworld_reasoning/srg_ac06_calibration.json) · [Fresh evaluation](../../../output/evaluation_storyworld_reasoning/srg_ac06_validation.json) · [Controlled K ladder](../../../output/evaluation_storyworld_reasoning/srg_ac06_ladder.json).

Natural exact minimum cardinality 2/3/2; all six reach the full empirical ceiling. The frozen two-coordinate transfer falls below 95% of attainable utility. Controlled full-cube certificate passes at every registered J/K cell. Public synthetic model packets only; no model inference or authored-world promotion.

From EvalMath root with Node 20+:

    node integrations/sweepweave-ts/srg-ac06/cli.mjs calibration
    node integrations/sweepweave-ts/srg-ac06/cli.mjs validation
    node integrations/sweepweave-ts/srg-ac06/cli.mjs ladder
    node integrations/sweepweave-ts/srg-ac06/cli.mjs stage /tmp/ac06-pilot pilot
    node integrations/sweepweave-ts/srg-ac06/cli.mjs stage /tmp/ac06-full full

Use a fresh directory. The 48-packet pilot has four packets per J/K cell, two per answer label; the full 516-packet corpus enumerates the legal cubes. Only send model_input/planning.jsonl to the model. Use the SRG-08 local planning runner with the checkpoint SHA and runtime label. Then:

    node integrations/sweepweave-ts/srg-ac06/cli.mjs score /tmp/ac06-pilot /tmp/run/submissions.jsonl

Submission format: one JSON object {id,action} per line. Score reports cell accuracy, macro accuracy and micro counts; unknown, malformed, duplicate or invalid rows receive no credit. Core source and runtime executed in isolated ECMAScript; standalone Node CLI and actual HTTP inference remain pending. Natural histories are verifier-only; no claim of independent private evaluation.
