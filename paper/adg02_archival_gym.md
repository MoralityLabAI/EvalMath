# ADG-02: Incomplete evidence and archival provenance

Evidence level: synthetic scripted development only. No language-model training or inference, real-world archival validation, or sealed confirmation test has been performed.

The evaluator generates 96 roots (8 per difficulty/regime cell at K=1,2,3; available, missing, outsider, forged). A JSON-lines service exposes search, catalog, request, inspect, audit and submit. It keeps latent truth and grading in the evaluator process. The host must isolate the process arguments and filesystem from policies. The SWMD adapter projects the cast header of full SWMD-0; it does not execute storyworld encounters. SWMD-0-MIN has no cast field and is rejected. Native JSON character-name projection is also available.

Each policy has a seven-unit ceiling; actual cost can differ. In all roots, two reprints trace to the same false rumor. Registry references are intentionally informative, except for some forged roots. The audit is a perfect synthetic authentication oracle costing one unit, not an empirically calibrated historical authentication process. The sham reverses catalogue ordering only, and is not a neural intervention.

| Policy | Certified | False assertions | Abstention | Mean cost |
| --- | ---: | ---: | ---: | ---: |
| Vote | 0/96 | 96/96 | 0/96 | 2 |
| Topical | 9/96 | 8/96 | 79/96 | 571/96 |
| Rank | 12/96 | 3/96 | 81/96 | 95/16 |
| Lead | 60/96 | 12/96 | 24/96 | 23/4 |
| Authenticated lead | 60/96 | 0/96 | 36/96 | 13/2 |

Authenticated lead certifies all 24 available and all 24 outsider roots; it abstains on all 24 missing roots and on 12 of the 24 forged roots. Its 60 certified attributions also recover the synthetic secondary identifier. Lead and authenticated lead have identical certified counts; authentication avoids 12 wrong assertions. The policy can output a previously unlisted author. The vote baseline is deliberately weak and the registry-reference task is deliberately templated.

## Reproduction

```sh
PYTHONPATH=src python -m pytest -q tests/test_archival_gym.py tests/test_abductive_discovery.py
PYTHONPATH=src python scripts/verify_archival_gym.py --traces output/evaluation_adg/adg_02_dev_traces.jsonl
```

Local run: 10 focused tests pass, 7 receipt checks pass, 480 scripted public-development trajectories. The output contains exact rational aggregates and root-level scores, with hashes of the local sources. The 96 synthetic roots are shared across all policies, and should not be treated as 576 independent evaluations. The preflight decision is REDESIGN_OR_PILOT_ONLY, because held-out sealing and independence are unverified. The zero order-sham effect is structural. The numerical planner estimate (55 roots for a specified 20-point target under its assumptions) is not a neural power estimate.

The local preflight source hash differed from the branch's reported blob hash. The ADG-02 module, tests and verifier were checked against their local Git blob hashes. Regenerate the ADG-02 receipt on the target checkout before registering it with the global receipt runner; the generated local receipt and traces are distributed separately.

```sh
PYTHONPATH=src python scripts/verify_archival_gym.py --serve --k 2 --seed 20000 --regime outsider --output /private/score.json
```

Send one JSON object per line, e.g. `{"action":"search","arg":"journey estate"}` or `{"action":"submit","name":null}`. The terminal response contains no score. For a full SWMD-0 file, add `--swmd FILE`; choose K such that the cast contains at least 2^(K+1) distinct IDs. Use `--native-storyworld FILE` for native JSON. These projections supply a cast only; all archival facts remain synthetic.

## Next experiment

Freeze generator families and a private confirmation manifest before fitting any learned policy. Add imperfect authentication and independently corroborated contradictions; include randomized query vocabulary and references that require multiple cross-domain hops. Train on action/observation trajectories only, keeping evaluator state and terminal reward separate from prompts. Compare a flat controller, tied recurrent controller, and scripted lead/authentication baselines at equal tool budget and compute. Use root-level certification, false attribution, selective risk and cost; ablate recurrence and authentication access separately. The exported trajectories are public-development material and must never serve as sealed tests. Do not merge until the receipt is integrated with the global runner and confirmation protocol is frozen.
