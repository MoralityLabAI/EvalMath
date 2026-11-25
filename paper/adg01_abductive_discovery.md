# ADG-01: Abductive discovery with gated evidence

**Evidence: finite synthetic mechanism result / development only.** Inspired by the reported attribution of the anonymous 1808 sketchbook to the vicomte de Chabot (Mark Humphries, https://generativehistory.substack.com/p/gpt-62-astra-solves-a-historical). The historical claim is motivation, not independently audited evidence here.

## Model

A root has a uniform hidden author among N = 2^(K+1) candidates, a public deterministic likelihood table, K route-bit clues (occasionally corrupted in the table), a random distractor, and N/2 archival documents. An archive identifies either of two authors in its group, or returns a negative match. Each archive costs two units and is accessible only after its unit-cost catalogue prerequisite. The catalogue is constant across hypotheses. The agent sees action metadata and the full likelihood table but no realized hidden-author index or unretrieved outcome. This is a closed-world structural planning oracle, not open-ended hypothesis generation. Costs are synthetic units.

Given a candidate set S, used actions A and budget b, stopping has expected utility 1/(4|S|). A positive archive match stops with utility one. Every other outcome y restricts S to S_y. The exact Bellman recursion maximizes stopping and the sum over outcomes of |S_y|/|S| times successor value, with action cost debited and prerequisite enforced. This follows from conditioning and finite backward induction for positive costs. The objective is (P(correct)+3P(certified))/4, with fixed tie order: stop, then action index. A certificate requires a positive archive receipt. The horizon-limited controls solve the same recursion with at most one or two future actions, then replan. They share the same budget and objective.

## Development census

16 fixed generator seeds per K in {1,2,3}; budgets K+2; 48 generator roots, 448 possible author assignments, fully integrated exactly rather than 448 independent samples. No training or model inference.

| K | One-step correct / certified | Two-step | Full horizon | Full horizon ungated |
|---|---|---|---|---|
| 1 | 3/4, 0 | 3/4, 1/2 | 3/4, 1/2 | 1, 59/64 |
| 2 | 3/4, 0 | 95/128, 1/4 | 3/4, 1/2 | 1, 119/128 |
| 3 | 47/64, 0 | 147/256, 1/4 | 3/4, 1/2 | 1, 247/256 |

The two-author witness has budget three: one-step finds the author with certainty but obtains no archive receipt; two-step and full horizon obtain both. Across the development census, relabeling identical catalogue prerequisites leaves full-horizon utility and both reported rates unchanged. This sham is an exact symmetry, not a calibration of neural intervention noise. The one-step policy's inability to select a constant-outcome catalogue is built into its stopping rule; its zero certified rate is therefore a deliberately weak baseline, not evidence about real greedy research agents.

Reproduce:
```sh
PYTHONPATH=src python -m pytest -q tests/test_abductive_discovery.py
PYTHONPATH=src python scripts/verify_abductive_discovery.py
```
The two local test functions passed, including boundary witnesses and eight finite comparisons. The receipt contains per-root exact rates and SHA-256 of the module, tests and verifier. Local and remote Git blob hashes were checked identical for those files and the receipt. The global receipt runner has not yet been wired or executed.

## Preflight

The repository's preflight planner was run locally on the 48 root-level certified-rate differences (full horizon minus horizon two) and relabel shams. Provisional scientific floor 1/20, measurement resolution 1/16, target 1/5, three planned comparisons, alpha 1/20, 240 future confirmation roots; independence and sealing marked false. Mean pilot effect 1/6; root standard deviation 0.11910; structural sham maximum zero; 95/95 sham upper tolerance bound unavailable (48 roots). Decision REDESIGN_OR_PILOT_ONLY, strict exit 2: heldout_unsealed, independence_unverified, sham_quantile_uncalibrated. Approximate eight-root power from the structural data is not a neural sample-size estimate. Physical intervention dose N/A, no causal model test. Actual structural comparisons include horizon one, horizon two, ungated and relabel controls. All roots exposed to development; no protected confirmation roots generated.

## ADG-02: open-world extension proposal

Use SWMD storyworlds as the ground-truth generator with a private event/identity graph and a separately exported public corpus. Public observations and documents may be incomplete, noisy, temporally inconsistent or dependent on shared sources. Names, repositories and archive IDs must not encode gold identity. Introduce unknown-author hypotheses and unavailable or contradictory documents. The tool API should expose search(query), catalog(id), request(id), inspect(receipt_id) and submit(hypothesis, probabilities, evidence_ids). Gate documents at the service boundary; never supply the full likelihood table to learned policies. Exact planning remains a structural ceiling on the finite core.

Measure certified true attribution, unsupported assertion, calibrated abstention, cost and secondary independently verified findings. Score evidence provenance and source dependency before accepting a certificate. A null or unavailable document must not count as positive evidence. Make the evaluator blind to self-reported certainty when scoring support.

Before training, freeze source-family disjoint train/dev/confirmation splits and a manifest hash. Use at least 59 genuinely independent dev sham roots for the 95/95 calibration, then rerun preflight on actual neural paired effects. Compare equal token/query/budget flat agent, recurrent agent, catalogue-aware heuristic, beam search and the exact ceiling on applicable finite tasks. Include shuffled catalogue descriptions, no-gate, unavailable archives, false document and source-copy controls. Test learned query depth and retrieval cost under the same API. Reserve proposed 240 confirmation roots untouched, with root-level paired inference and multiplicity corrections; replan count after dev calibration.

Data Goblin export should contain only train/dev policy-visible transcripts, canonical action, tool receipts, before/after probability distribution, actual cost and verified reward. Keep private world state, gold answer and confirmation data evaluator-side; tag generated versus real archival sources and all model/checkpoint provenance. Secondary discovery, open-world inference, noisy-source modeling and SWMD integration are planned, not implemented here.
