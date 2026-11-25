# Referee-style review of "The Economics of Mathematical Discovery" and responses

Review of 2026-11-25 by a fresh delegated reviewer (sonnet worker, not shown the lead's conclusions, instructed to be adversarial but fair, to recompute at least twelve claims and to try to break Propositions 2 and 3). The reviewer is a model run by the same team on the same machine; it is independent of the author's context, not of the author's tooling or institution. The full report is kept unedited in [`economics_referee_review_raw.md`](economics_referee_review_raw.md) (including its addendum on the 09D attribution, which we reproduced exactly in `output/verified_abstraction/vad_09d_attribution.json` and `vad_09d_heuristic.json`).

Recommendation of the reviewer: **revise (major)**. The exact-oracle and amortization-law material was judged sound; Proposition 2 survived a 3,000-instance attack; several statements in the economics and neural sections were judged overstated or wrong.

## Responses

| # | Finding (verdict) | Response in this revision |
|---|---|---|
| M1 | VAD-11E gains rest on in-Lean `work_ms`, flip with toolchain, and vanish on wall time (overstatement) | Accepted. Section 3.2 now reports both toolchains and per-file wall time (all policies 0.72x to 1.05x), says the ratios are not an economic gain, and lists that no horizon sweep was run. The receipt `vad_11e_economics.json` now carries the sensitivity block. |
| M2 | n = 5 single-session replay; calibration lemmas do not overlap test lemmas; "oracle" is not an upper bound; library authored (overstatement) | Accepted. Overlap counts added to the receipt and text; the policy renamed in the text "best searched prebuilt set"; retrieval's per-family standing and the authored library stated. |
| M3 | False sentence: "the only family where a neural arm beats a symbolic baseline is chains" (confirmed error) | Corrected with the exact comparisons from `vad_12_gate.json`. |
| M4 | "Exact belief supplied; Markov" is not what the features contain (overstatement) | Corrected: the feature list is stated, the explanation of the memory result is withdrawn, the failure is described as confounded with feature insufficiency. The limitation sentence on distribution family was corrected. |
| M5 | Undisclosed design details; ablation off by one; "pre-declared" and "cheaper" unsupported | Disclosed: 1,000 instances, tie-to-stop labels, accuracy-based checkpoints, oracle-feature definition, off-by-one ablation (cannot be re-run, models not saved), seed spread. "Pre-declared" replaced by an accurate statement of when the rule was fixed; the "cheaper per call" claim withdrawn (per-instance cost is comparable). |
| M6 | "Each hypothesis is necessary" not demonstrated; the p = 1 strategic sentence conflated the baseline with the optimum (overstatement) | Restated; no counterexample for two hypotheses is reported as such; p = 1 sentence corrected in both the paper and the VAD-10 note. |
| M7 | Proposition 3 needs tie-break, lambda = 0, N = 1 (gap) | Conditions added to the statement, proof, and note; the lambda = 1/10 value 6.019 is stated. |
| M8 | 09D: 12.9 and 8.93 misattributed to planning and to law knowledge | Accepted. New exact decomposition `vad_09d_attribution.json`: planning depth 3.96, probe 8.93, law knowledge adds a negligible amount to the planner; overhead allowances stated separately. |
| M9 | "Wins at long horizons" contradicted by the paper's own shift results | Section 4(1) rewritten: amortization requires matched distribution and a measured horizon. |
| M10 | "Independent" verification wording | Changed to "separately written (same team)"; audit retitled; limitation stated. |
| M11 | Source section: contradictory "secondary reporting not used" sentence, unverified third-hand details, PAPER-1 mis-levelled, event language | Removed the third-hand details and the process meta; claim level changed to C (cited, not archived); wording changed from "events" to "reports". |
| m1-m12 | Denominator mix in the 1.2537x sentence; uncommitted 24 s scaling remark; self-undermining invention sentence; missing files; naming; per-seed spread; 09B digest; "four controllers"; kernel status; stale runtime; process meta | All addressed in the text (the 24 s remark deleted, invention sentence rewritten, kernel status stated as CI lean job success with receipts NOT_RUN, runtime updated, probe receipt committed). Per-seed values are in `results.json` and `vad_12_gate.json`. |

## Not changed

* We did not add a horizon sweep, a repeat-run timing study, or a re-run of the neural arms with richer features; these are listed as the content of the next experiment (paper section 6). The shuffled-memory ablation could not be re-run because model weights were not saved.
* The reviewer could not re-fetch the two vendor web pages and made no claim about their content; neither did it verify any Lean kernel result.
