# VAD-13C: calibrated physical timing results

Completed GitHub Actions run 45583084890 at commit 65fd67a0db2e065ec29d441625e4a45b354e38f5. All ten jobs passed. Downloaded all ten timing artifacts and checked all 240 process rows: successful exit and all requested axiom reports accepted. 4,800 target verification attempts including calibration and repetitions. One calibration/test seed block, three repetitions, horizons 8 and 32. No interactive server.

Artifact IDs: 15008500554, 15008235027, 15007960911, 15007930947, 15007910953, 15007905907, 15007167034, 15007023540, 15006773820, 15006709271.

## H=32 deployment results

Family | Lean 4.19 direct/lemma seconds | Lean 4.35 direct/lemma seconds | calibration-selected 4.19/4.35
---|---|---|---
F1 | 2.067966 / 1.623499 | 0.767936 / 0.698169 | lemma/lemma
F2 | 1.983778 / 1.257808 | 0.534266 / 0.373998 | lemma/lemma
F3 | 25.246394 / 27.346908 | 13.402008 / 17.004548 | lemma/direct
F4 | 9.258889 / 5.601743 | 3.303519 / 1.585426 | lemma/lemma
F5 | 0.644543 / 0.687347 | 0.415390 / 0.447988 | direct/direct

Pooled ratio of summed family medians, selected vs direct:
- 4.19 H=8: 0.429621; H=32: 1.074766.
- 4.35 H=8: 1.060451; H=32: 1.118248.
- H=32 always lemma: 1.073507 / 0.916111.
- H=32 charging one median calibration execution per arm: 0.321479 / 0.319851.
- H=32 estimated calibration break-even: 31.3402 / 21.1096 sessions (strictly profitable after 32 / 22 whole sessions if these savings repeat). Charging all three calibration repeats: 94.3293 / 63.5301 sessions.

F3 on 4.19 selects the slower lemma strategy at both horizons; at H=8 direct 3.878127s vs lemma 14.420734s. F1 also loses at H=8 under both versions. F2 and F4 are positive at both horizons; F1 positive at 32. F5 direct wins. These are descriptive timings, not a statistically confirmed gain or generalization guarantee; each family/version has one test block, and medians from different runner jobs are pooled descriptively. Source-generation time is included; GNU time CPU and peak RSS are retained in original receipts. Calibration charges exclude any additional research and authoring costs.

## Next gate

Run a fresh block at H=128 and 256 for F1, F2 and F4, chosen from these exploratory results. Preserve F3 and F5 as negative controls at smaller horizons; do not present the selected-family result as an all-family average. Test the fixed family-conditioned rule derived from this pilot as well as newly calibrated strategies; charge all new calibration separately. A fixed rule uses lemma for F1/F2/F4 and direct for F3/F5, but its out-of-block gain has yet to be measured. Physical costs of interactive verification and lemma invention remain outstanding. Hold neural scaling.
