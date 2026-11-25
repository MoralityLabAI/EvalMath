# VAD-13B outcome and VAD-13C prospective gate

2026-11-25. VAD-13B physical batch pilot completed on GitHub Actions run 45575593358, commit f22e2fe5f50497bc45ba93acbf1dd30719550924. Both Lean toolchains and the joint-demand deterministic replay passed; full verify run 45575593397 also passed.

Artifacts: 15003588474 (Lean 4.19.0, archive SHA256 35eb560452777f32a982f77c563e4db825ef7f460d4a2b3938fb7e7163ee6ca1); 15003742317 (Lean 4.35.0, archive SHA256 c779854d2a2714b74b29f57aaa324a3a85eae9cbe2589ddfded2af513e393691). Downloaded and inspected receipt.json in both archives. Across 32 process invocations, 640 target checks and 92 library theorem checks passed (repetitions count separately). Each session contains a batch of generated source; it is not an interactive Lean server.

Median total seconds including generation and Lean execution, two repetitions per cell:

| Version | Family | Horizon | Direct | Lemma | Gain |
|---|---|---:|---:|---:|---:|
|4.19|F1|8|0.515572|0.332449|1.550831|
|4.19|F1|32|1.584091|0.825977|1.917839|
|4.19|F5|8|0.169891|0.188793|0.899876|
|4.19|F5|32|0.381607|0.406464|0.938846|
|4.35|F1|8|0.290664|0.269735|1.077591|
|4.35|F1|32|0.643330|0.496561|1.295572|
|4.35|F5|8|0.214484|0.233372|0.919067|
|4.35|F5|32|0.320190|0.345333|0.927193|

The ratio of summed family medians at H=32 is 1.594963 (4.19) and 1.144468 (4.35). F1 is a positive physical pilot; F5 is a negative control. Two repeats on shared CI runners are insufficient for a confirmatory timing claim. No memory, child CPU, interactive policy, or abstraction invention measurements were made. Generation time includes repeated source audits; both arms pay their own required library definitions. The supplied lemma library is authored, not discovered.

## VAD-13C (prospective)

Extend matched batch timing to F1–F5, horizons 8/32/128/256, five repetitions, randomized arm order, and additional disjoint public seed blocks. Keep each target's statements and namespace isolation identical between arms. Measure wall time and process CPU/peak RSS; use distinct calibration blocks to choose proof strategy per family and horizon before test execution. Include a direct-only control and an always-lemma control. Charge both arms for any separate calibration runs and selection overhead; report break-even numbers with and without this sunk calibration expense. Report per-family and pooled ratios, paired repeat differences and hardware metadata. Treat a failed compiler/axiom check as a failed arm, not a timing observation to discard. The first CI expansion is exploratory and may use fewer repeats/horizons due to resource limits. A subsequent interactive session must enforce legal prefix access and demonstrate that retaining the environment actually reduces time compared with the stronger batch baseline. Hold neural training until that gate passes.
