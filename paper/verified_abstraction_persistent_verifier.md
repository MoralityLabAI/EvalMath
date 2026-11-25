# VAD-13: joint demand and batch verification

Status: VAD-13A retrospective replay executed against the committed VAD-11 receipt. VAD-13B physical benchmark implemented and submitted to CI; no new physical timings or kernel results claimed yet.

## Joint-demand correction

For events A_i indicating that a future target uses lemma i, the minimum marginal probability is an upper bound on their intersection. The Frechet lower bound is max(0, sum_i P(A_i) - k + 1). The product of marginals is valid under independence only. A smoothed empirical joint event count estimates co-use without assuming independence. Bounds applied to estimated marginal probabilities are not confidence bounds on unknown population probabilities.

The VAD-13A replay uses the same 200 VAD-11 instances, five families, two toolchains, two metrics, and nested test horizons 4, 8, 16, 20. Charge transitive library closure for direct proofs as well as alternative proofs; charge each newly acquired unit once. Compare direct, minimum marginal, smoothed joint, independence, Frechet, and unconditional on-demand construction. When the required alternative units are already built, select the alternative strategy, whether or not it is faster. The online estimators use prior calibration and past targets only, with Laplace smoothing. Per-use saving is the mean signed direct-minus-alternative time over that history, truncated below at zero. The method sees the required units of the current target and both historical strategy timings, which are supplied by the retrospective receipt. Real acquisition of these signals may require extra proof work. Direct-required units are acquired even when the alternative route is used; this is a stipulated conservative charge. Policy computation, discovery of the authored library, and additional measurement overhead are not charged. No new theorem proving or causal deployment is established by this replay.

At H=20, work gains over the revised direct baseline under Lean 4.19 / 4.35 are min and joint 1.534 / 1.543; independence 1.512 / 1.542; Frechet 1.510 / 1.540; on-demand 0.882 / 0.868. Using recorded isolated-process seconds, min and joint attain 1.091 / 1.045. These ratios differ from VAD-11E because the direct comparator also pays required transitive library costs; this is a new accounting convention, not an improvement in the measured timing of the earlier policies. The equal min/joint performance in this dataset does not make the probability expressions equivalent. The replay contains 480 family-policy-horizon-metric-toolchain records.

Reproduce with Node:

    node scripts/verify_vad_joint_demand.mjs output/verified_abstraction/vad_11_gym.json

## VAD-13B: matched one-process batches

The generator uses VAD-11 theorem specifications and proof strategies. It includes transitive library dependencies as source within the same process, with a single definition per unit per batch. Direct and alternative arms each pay their required library construction. Target helper definitions and theorems are placed in target-specific namespaces. Audit the library against held-out names, check source references, verify statement fidelity using the existing semantic checker, and require successful Lean exit plus an allowed axiom report for every requested theorem. This is restricted generated-source hygiene rather than a general kernel dependency audit. The physical primary estimand is batch_direct versus batch_lemma on identical targets; the optional fully cold arms rebuild each target's required library and must be interpreted accordingly. Report total Lean process time, source-generation time, number of calls, and axiom outcomes. The two arms use different proof strategies; author-supplied lemma availability is not evidence of abstraction invention.

CI pilot: two toolchains (4.19.0, 4.35.0), F1/F5, horizons 8/32, two repeats, randomized arm order. Full command defaults to 8/32/128/256 horizons with three repeats; the generator also accepts F2/F3/F4, which are outside the pilot. These are public nested prefixes, not independently sealed families. Timing from shared CI hardware is descriptive; use more repetitions and controlled hardware before an advancement decision. No peak memory/CPU measurement yet. The batch is preassembled, not an interactive persistent server. Policy overhead and online construction decisions need a separate implementation with an isolated target environment and retained library state.

    python scripts/verify_vad_batch.py --out /tmp/vad13 --lean lean --families F1 F5 --horizons 8 32 --repeats 2

Do not advance neural training from this replay. Require positive wall-clock gain at matched closure with construction and policy computation charged, then test on fresh theorem streams with actual joint demand observations and no privileged historical counterfactual timings.
