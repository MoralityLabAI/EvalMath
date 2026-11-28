# VAD-07: optimal stopping and cue reliability in abstraction discovery

Status 2026-11-25. VAD-07A/B are exact finite Bayesian models. VAD-07C is a finite synthetic Horn proof-reference cost experiment. No neural training or new Lean replay.

## 07A: stopping law

Let the latent type i have prior w_i, deterministic discovery time t_i (a sentinel H+1 represents null), and Bernoulli cue probability p_i conditional on an unsuccessful observation. Conditional on type, these cues are iid. Observation costs c=2; discovery at time t <= H pays r(t)=88-t net of cache construction, with H=24. Discovery terminates exploration. Stopping before discovery gives zero future payoff. No external information or intermediate construction is available.

At state (n,k), n failed observations and k positive cues, unnormalized type mass is

    W_i(n,k) = w_i p_i^k (1-p_i)^(n-k) 1[t_i>n].
    Z(n,k) = sum_i W_i(n,k).

By Bayes and conditional independence, (n,k) is sufficient. Write V(H,k)=0 and use 0 for zero-mass states. Then

    V(n,k) = max(0, -c + [
      sum_{i:t_i=n+1} W_i(n,k) r(t_i)
      + sum_{b=0,1} Z(n+1,k+b) V(n+1,k+b)
    ] / Z(n,k)).

Backward induction proves optimality over history-dependent and randomized policies in this model. The code evaluates exact rational values and independently propagates forward probability mass through latent type and observed state.

Without informative cues, any deterministic policy using only time and the absence of discovery chooses a cutoff K. If optional noise and policy randomness are independent of type until discovery, pre-sample a complete hypothetical unsuccessful trajectory; this induces a random cutoff independent of type. Expected net utility is then a mixture of fixed cutoff values

    U(K) = sum_i w_i [1[t_i<=K] r(t_i) - c min(t_i,K)].

The maximum is attained by a deterministic cutoff. Adaptation requires information beyond the bare fact of unsuccessful observation (or another observed variable that affects costs or reward).

Use times (2,8,16,24,25); base weights (15,10,15,10,50)/100; p=(0.7,0.7,0.7,0.7,0.15). Estimate type prior and cue rates from 512 labeled complete training trajectories with Laplace pseudocounts and seed 713207. Freeze estimated parameters, and evaluate exactly on seven declared scenario distributions. This is model-based evaluation, not a finite sampled test confidence interval. The exact oracle is allowed the evaluation distribution, whereas calibrated/base policies are frozen. The scenario choices are synthetic sensitivity controls.

Base optimal blind cutoff 2, net 8.9; exact adaptive 21.1820; estimated policy 21.1817. Null-heavy: blind 2.88, estimated 7.6604, oracle 7.9900. Late-heavy: blind 2.1, estimated 16.2939, oracle 16.5387. With weaker cues the estimated policy drops to 8.2158 vs blind 8.9; with reversed cues it drops to -10.4431; the scenario-aware oracle reaches 20.6057. The original calibrated policy can lose money when cue likelihoods change.

## 07B: reliability robustness

Introduce a latent family-level reliability mode (base or reversed). Form eleven prior mixtures with weights 0 through 1 in steps of 0.1. Evaluate resulting exact Bayesian policies and five cutoffs. Search all pairs of the 16 policies with mixing probabilities on a 1/20 grid. Protected scenarios use the original time prior and four cue channels (base, reversed, weak, blind). Other time-prior shifts are reported but outside the protected set.

The two-observation cutoff has worst-case value 8.9, and the pair-mixture search achieves the same value. Moreover, this is an exact minimax value for the four protected scenarios over all permitted policies: the blind scenario supplies an upper bound of 8.9 by the cutoff theorem; the two-observation cutoff attains 8.9 in all four scenarios, since its payoff does not depend on the cue channel. This argument does not establish robustness against arbitrary priors, costs, horizons, or additional observations. The equal base/reverse Bayesian mixture achieves base/reverse values 9.1166/9.6388 but weak/blind values 5.2694/6.1040, showing why prior mixing alone does not ensure a worst-case improvement.

## 07C: matched Horn prefix experiment

Use the bounded ancestor index of VAD-06D2 (depth three, two distinct supporting goals, commit at the first candidate) with a choice of observation caps 0,1,2,4,8,16,24,32,48,64. A cheap cue is whether the first already-charged ancestor traversal returns zero nonfact ancestors. No additional traversal is charged for testing emptiness. Fit a global cap and a separate cap per cue class on 256 calibration families. Score frozen policies on 512 fresh test families, 64 per regime, using predetermined regime weights. These are weighted sums, not independent test draws from each mixture; shifts reweight the same test traces. The cue policy must pay at least its first observation. The full graph solve is an ex post cost oracle and supplies no future information to decisions.

Eight regimes include shared, concealed unlock after 16/48 goals with easy or hard early private proofs, permanent easy/hard nulls and permanently dominated alternate routes. Matched easy or hard null and concealed worlds at the same seed have identical observed roots and ancestor-cone rules before unlock; tested on 48 matched pairs. This means the cue is not a certificate of a particular future. The regime weights impose a correlation in the base mixture and change that correlation in the cue-shift mixture. This is intentional and not a claim that real Lean proof shapes predict future reuse. All proofs in the observation prefix are charged uncached, index work is charged even on abstention, and construction is charged once on discovery. The cost grammar and parent oracle remain those of VAD-06A. Memory, index construction, physical Lean inference and training costs remain outside the reference model; common DP scans are a separate sensitivity.

Calibration picks fixed cap 24, and cue-conditioned cap 64 for empty, 2 for nonempty. Weighted base direct cost 19,289,750; fixed 17,760,955; cue 15,385,990; cap64 17,958,940. Cue gain 1.253722x versus direct, 13.3718% reduction versus fixed; including common DP scans 1.086253x. Under null-heavy weights fixed/cue gains 0.980460/1.093951; under late-heavy 1.011641/1.250420; under cue shift 1.119470/1.091842 (fixed wins); under uniform 1.260911/1.335009 (cap64 wins at 1.41095). The cue policy discards all hard-concealed hubs in the tested setup, and pays 64 observations on easy nulls. It improves the declared base mixture without dominating all mixtures. These limitations matter for the future learned controller.

## Reproduce

    python scripts/verify_vad_stopping.py --out /tmp/vad_07a.json
    python scripts/verify_vad_robust_stop.py --out /tmp/vad_07b.json
    python scripts/verify_vad_horn_stop.py --out /tmp/vad_07c.json
    python -m pytest -q tests/test_vad_stopping.py

Three local tests pass (15.61s on the local replay). 07A checks 117 exact equalities/inequalities and 07B checks eleven forward/Bellman equalities; a separate explicit binary history-tree test checks ten priors. 07C checks 2,036,550 cost entries against independent fixed-point relaxation across calibration/test, including repeated cost checks. The replay test checks SHA256 of all three complete receipts. The receipt records the source digests. All four new code blob hashes were checked against the local tested files after committing.

## Next: VAD-08

Introduce online cue-reliability calibration across a sequence of families: predictive checks on discoveries and censored non-discoveries, independent calibration receipts, explicit observation budgets, and a safe default when posterior model fit deteriorates. Compare an exact finite Bayesian filter, a frozen cue policy, and a small recurrent predictor trained only on disjoint trajectories. Charge the cost of calibration and false continuation. Test changing priors and cue reliability separately. Require a learned model to beat the strongest deployable symbolic policy at matched information and costs before advancing to harder Lean proof discovery. No neural gain is claimed here.
