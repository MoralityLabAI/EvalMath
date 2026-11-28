# VAD-08: sequential reliability calibration under censored feedback

2026-11-25. Finite synthetic VAD-07 stopping model, optional small CPU GRU, and independent rational verification. No new Lean theorem or kernel run.

## Likelihood under adaptive censoring

Let the latent reliability mode be R_j in {0,1}. Within a family, discovery time T has the VAD-07 base prior and unsuccessful observations are conditionally iid Bernoulli, with success probability q_{R_j,T}. A terminal search record is (n,k,h), where n is the number of paid observations, k is the number of positive cues, and h indicates discovery on observation n. There are f=n-h observed cues. For mode r define

    L_r(n,k,h) = sum_t w_t q_{r,t}^k (1-q_{r,t})^(f-k)
                          * 1[t=n if h else t>n].

This is the likelihood of one compatible cue history. For a count record, multiply by the number of compatible histories satisfying the deployed stopping policy. That factor is mode-independent conditional on past observations and the fixed within-family policy, so it cancels in posterior and likelihood ratios. The code independently checks exact normalization including path multiplicities. It never imputes unseen discoveries after stopping.

Given predictive mode probability p, the posterior is p L_1 / ((1-p)L_0+p L_1). For symmetric cross-family switching hazard a, the next predictive probability is a+(1-2a) times posterior. The filter is exact for the declared model (implemented with floating point, checked against rational enumerations), while its deployment planner rounds p to a 1/20 grid and maximizes within-family expected utility. It is myopic across families: information obtained by searching could affect later decisions, so no global optimal-control claim is made.

The mismatch monitor accumulates the log predictive likelihood ratio of a static four-model alternative mixture (weak cue and/or elevated null prior) versus the nominal two-mode Markov law, under the same predictable deployed policy. In exact arithmetic, under the fully specified nominal model and common support, this likelihood-ratio process is a nonnegative unit-mean martingale. Ville's inequality bounds the probability of ever crossing 20 by 1/20; the finite floating-point implementation is not a machine-verified martingale certificate. After crossing, the policy permanently uses cutoff two. A separate expanded six-state filter uses a persistent/redraw transition, coarse 1/5 simplex grid and includes weak/high-null modes. The expanded filter is an alternative model, not an exact filter for the shifted generator.

## Experiment

Nominal mode switching hazard 0.05. Discovery times 2,8,16,24,25 (25 is null); observation cost 2; discovery reward 88-t already nets construction. Base prior (0.15,0.10,0.15,0.10,0.50); high-null prior (0.08,0.05,0.08,0.04,0.75). Normal useful/null cue rates 0.70/0.15, reversed 0.25/0.75, weak 0.55/0.45. Eight evaluation regimes: nominal Markov, stationary normal, stationary reversed, midpoint reversal, hazard 0.25, weak cues throughout, midpoint high-null change, midpoint joint weak/high-null change. 32 independent streams of 96 families per regime, using common exogenous streams for all nine methods. Public distinct training/calibration/test seed namespaces; not independently sealed. Methods are cutoff two, frozen base policy, fixed 50:50 prior, online two-mode filter, mismatch alarm, expanded filter, privileged mode/prior/channel oracle, GRU and memoryless GRU. The privileged oracle sees true family mode and channel but not discovery time; it is a within-family benchmark, not an attainable online method.

The 369-parameter GRU receives five features of previous censored records, and predicts the next mode. Training has privileged mode labels only on 256 disjoint nominal streams (12,288 families), collected via randomized behavior policies; 48 calibration streams (3,072 families) choose epoch by BCE. Seed 83801, AdamW, 20 epochs, best epoch 20, calibration BCE 0.44235635. No mode label, unobserved cue, or latent discovery time enters evaluation decisions. NumPy inference is checked against PyTorch. Training/calibration observation expenditures 219,532 and 54,722 units respectively are recorded separately; primary evaluation does not amortize them. The filter is given the nominal generative parameters, so this is a comparison to a strong known-model symbolic comparator, not equal-information model identification. Weak/joint-shift mode-label Brier scores refer to the latent nominal label, which no longer determines the actual weak channel; they are not calibrated weak-channel forecasts.

## Results

Mean net utility per family, after search and net construction charge but before controller computation:

| Regime | Blind | Frozen | Filter | Alarm | Expanded | GRU | Memoryless | Privileged |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Markov | 8.850 | 4.253 | 17.887 | 17.754 | 17.536 | 16.717 | 12.613 | 20.637 |
| Stationary | 8.318 | 21.613 | 21.082 | 20.227 | 20.765 | 20.976 | 14.328 | 21.613 |
| Reversed | 8.794 | -10.893 | 19.740 | 19.388 | 19.517 | 18.585 | 12.230 | 20.408 |
| Abrupt | 8.318 | 4.926 | 19.144 | 18.525 | 18.813 | 18.346 | 12.941 | 20.271 |
| Fast | 10.109 | 6.758 | 11.217 | 11.217 | 11.189 | 10.936 | 11.874 | 21.368 |
| Weak | 9.521 | 9.013 | 5.581 | 9.344 | 8.927 | 7.352 | 5.441 | 10.430 |
| Prior shift | 5.826 | -3.178 | 11.490 | 11.380 | 11.311 | 10.380 | 7.238 | 14.233 |
| Joint shift | 5.378 | -2.682 | 3.279 | 5.614 | 8.524 | 2.546 | 0.742 | 11.594 |

Nominal GRU minus filter -1.170573 per family; descriptive paired stream bootstrap interval [-1.617188,-0.748698], four wins in 32 streams. Neural gate FAIL. Recurrence helps over memoryless on the nominal law but not the fast-switch law. Weak cues trigger the monitor in 32/32 streams; joint shift in 29/32; nominal Markov in 1/32. The monitor does not dominate the blind policy under weak cues. Expanded filtering helps on joint shift in the primary metric. Controller accounting is a sensitivity, using declared proxies (nominal 4, GRU 6 plus 320 MACs per family, expanded 12, alarm approximately 8); these are heterogeneous abstract operations, not elapsed time. Primary net after these proxy controller units under nominal Markov: filter 13.887, GRU 10.717, alarm 9.778, expanded 5.536. Charging 1 unit per MAC makes GRU strongly negative. The expanded filter loses to blind under joint shift when the controller proxy is charged. Planner table generation, label acquisition, physical compute, memory, and training FLOPs are not fully charged. No model gain is established.

## Reproduction

    python scripts/verify_vad_reliability.py --out /tmp/vad08_symbolic.json
    python -m pytest -q tests/test_vad_reliability.py
    OPENBLAS_NUM_THREADS=1 python scripts/train_vad_reliability.py --out /tmp/vad08

Four local tests passed: all 21 nominal grid policies compared to VAD-07 exact rational optimal utility, 15 normalized censored-record distributions, 80 latent-path posterior comparisons, suffix causality, simplex quantization, and frozen symbolic trace digest. Optional training repeated locally under torch 2.10.0+cpu, with byte-identical checkpoint and full 2,304 stream-method record receipt (221,184 family-method evaluations, 24,576 unique test families). CI for the new commit is pending. Full receipt and checkpoint delivered in the reproduction bundle. Source and digest manifest under output/verified_abstraction/vad_08.json.

## Next gate

VAD-09 should address the value of information across families. The current filter chooses a myopic within-family policy and treats censoring as an incidental consequence. Introduce a finite meta-horizon over reliability states, an exact small belief-state control comparator and policies which may choose an expensive observation to improve later family decisions. Separate learning the mode from learning the unknown cue law, charge any calibration interventions, and compare with a safe cutoff. Do not escalate to larger TRMs on the current failed gate.
