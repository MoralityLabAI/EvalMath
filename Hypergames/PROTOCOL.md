# HG-02 design: actual storyworld hypergames and implied goals

**Status:** proposed measurement protocol, unrun. HG-01 is a mechanics-only pilot. Register before consuming any held-out model traces.

## Interfaces and data discipline

1. Source-lock one version of GPTStoryworld, the local simulation scripts, all chosen worlds, their JSON hashes, and their variable dictionary. Treat `p`, `p2`, ground truth, and belief after-effects as different namespaces. List which fields were visible *to each actor* at pick time. `shared_full_state` is an explicit baseline information condition rather than a guarantee of plausible privacy.
2. For every `(episode,turn,acting_agent)`, record pre-choice visible state, exact legal actions, chosen action, and a simulator-produced candidate successor for **every** legal action under each declared *subjective* game view. An authoritative replay gives the corresponding objective successor table. The two views may disagree. If those tables cannot be produced, mark the example `insufficient_counterfactual_data` and exclude it from inverse planning.
3. Register dimensional treatment: BNumbers (including character and keyring index), value ranges, missing values, explicit world-variable allowlist, weights, categorical encoding, and treatment of time. Never silently map missing features to zero. Freeze thresholds and discretization boundaries on development worlds.
4. Fit goal candidates from train-only reachable endings, declared gate constraints, or a rational low-rank parameterization. A candidate goal means a terminal state or goal set with provenance. If no goal fits chosen actions under the declared behavioral rule, output `no_hypothesis_fits`.
5. Use exact inverse-Voronoi inequalities for one-step preference identification. For longer horizons, estimate or certify action Q-values with a finite-horizon Bellman oracle. Do not reuse one-step distance as a substitute for dynamic reachability.

## Comparators and uncertainty

- Baselines: random legal, fixed first legal, path-prefix oracle, the existing capability-state composite, and unweighted Euclidean or Hamming distance. Include a no-belief view, p-only, p+p2, and a hash-bucket manifold adapter with collision audit.
- Hold out world generators, ending gates, agent names, and transition templates. Use ≥100 rank-matched randomized projections and matched-size goal dictionaries for causal mechanism claims. Report per-world/seed counts, never only pooled gains.
- Compare registered true ending with rank/coverage under **objective** replay; assess behavioral consistency under **subjective** predictions. Evaluate counterfactual prediction on fresh interventions rather than interpreting text labels as mental facts.
- Register ablation axes: projection rank; coordinate weights; p2 access; dynamic horizon; perturbation of actual vs perceived values; and unseen decoy actions. Count zero-regret candidates, dimension of blind nullspace, margin certificate frequency, ties, impossible hypotheses, and predictive accuracy.
- Report operational compute costs `O(d)` metric, `O(n_goals*n_actions*d)` inverse-goal ranking, and exponential `2^n_probes` exact cover reference (cap 16). Evaluate learned approximations separately against this oracle.

## Proposed falsification gates

**HG-02/A:** With clean counterfactuals and shared visible state, an outcome-blinded goal model must beat the fixed-first-legal policy on unseen goal-endpoint predictions at matched budget. Register numerical thresholds and seeds before training; HG-01 does not set performance targets.

**HG-02/B:** Adding observer-owned p/p2 features must improve **held-out** opponent-choice forecasting over equal-capacity shuffled and hash-bucket controls. Report any p2 improvement separately from access to post-turn truth.

**HG-02/C:** For claimed latent-goal identification, interventions must reduce the set of compatible goals under the *actor's real information* and improve future action predictions. A single best-matching ending without intervention evidence is a descriptive prototype.

## Related EvalMath modules

- `paper/bpd_interventional_separation.md` and `src/spiral_ln/evaluation_bpd.py`: pair separation, fixed/adaptive probe cost and `no hypothesis fits`.
- `src/spiral_ln/interface_relative_compactification.py`: predictive signatures and observation-dependent dynamic quotients.
- `paper/agency_unknown_reliability.md`: latent channel identification and sealed future labels.
- `paper/evaluation_game_testbed.md`: opponent policies, information channels and regret baselines.
- `tests/test_interface_relative_compactification.py`: independent cylinder-law oracle design.

The eventual integration in GPTStoryworld can be a read-only exporter into this module. HG-01 does not modify either source engine or the narrative files.
