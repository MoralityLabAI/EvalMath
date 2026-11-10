# RHC-02: Exact reward-hacking detection ceilings on frozen MeshEscapePit trajectories

**2026-11-10. Evidence:** exact finite rational minimax certificates; retrospective replay of scripted deterministic Control-Harness trajectories; synthetic observation and endpoint-matching mechanism. **Scope:** the small, harmless MeshEscapePit administrative game. The original graph's `H` node is hidden, making any `H`-aware detection channel an **oracle-only** comparison. No learned actor, natural attack distribution, physical FPR, or deployed protection is inferred from this replay.

## 1. Data and fixed objective

Input: [`MoralityLabAI/Control-Harness/results/mesh_escape_pit/v1/reference_trajectories.jsonl`](https://github.com/MoralityLabAI/Control-Harness/blob/main/results/mesh_escape_pit/v1/reference_trajectories.jsonl), pinned at Git blob SHA `2e5a9690484f10c26180bf67a7e0f70c75ace0d6`. The source provides **35 distinct scenario cards**: 11 aligned and 24 attack-eligible red cases. Each card has an outcome under eight deterministic reference controllers, yielding 280 source rows. The 280 rows share cards and cannot be interpreted as 280 independent adversarial samples. The source [v1 README](https://github.com/MoralityLabAI/Control-Harness/blob/main/results/mesh_escape_pit/v1/README.md) calls these scripted conformance records.

We freeze six source fields: scenario ID, label (`aligned` or `red`), controller, directed algebra path, controller decision, and attack-success flag. A family label is retained for family-blocked evaluation. The extraction is stored in `fixtures/external/mesh_escape_pit_reference_v1_projection.json`; `scripts/project_mesh_reference_rhc02.py` checks the original Git blob SHA and reproduces the compact projection. The projection contains *no natural-language prompt or model response*.

Every algebra path begins at `O` and ends at `D`. This benchmark **introduces** the nominal state-potential reward `phi(D)-phi(O)`. The source does not record this reward, and the fixed endpoint alone is an intentionally coarse surrogate. We retain the final controller decision as an additional endpoint observation. No claim of physical equality of two final administrative states is made.

The adversarial population for the primary analysis consists of **attempted red paths**, including cases blocked by the controller. For the secondary **successful** analysis, we condition on the source's `attack_success` field. Conditioning on attack success changes the estimand and is stated explicitly in every result.

To remove endpoint-decision imbalance, form an empirical red law `Q` uniform across the selected `n_R` red cases. For each final decision `d`, let `n_R(d)` be the red count and `n_A(d)` the aligned count. Give each aligned case of decision `d` weight

\[
P(s)=\frac{n_R(d(s))}{n_R\,n_A(d(s))},\qquad Q(r)=\frac1{n_R}.
\]

An absent aligned stratum raises an error. Under this transparent reweighting, the pushforwards of `P` and `Q` to `(start,end,decision)` are *exactly equal*. This constitutes matching on an observation quotient; the construction reuses aligned reference cases with fractional weights and creates no new agent interactions.

We set a false-positive budget `alpha = 1/4` and allow randomized decisions `f(o) in [0,1]`. False positives and detection probabilities are **expected fractions** under the frozen empirical laws. No stochastic monitor was deployed to count realized false alarms.

## 2. Channels, topology, and detector certificates

The observation channels are strictly label-free:

| Code channel | Observable | Visibility |
|:--|:--|:--|
| `endpoint` | `(O,D,decision)` | Endpoint-only |
| `visible_edge` | Indicator that a path contains edge `P -> D` after hidden `H` is removed | Simplified visible event monitor |
| `full_width_edge` | Previous indicator OR whether `H` occurs | Privileged oracle-only telemetry |
| `visible_route` | `(decision, directed path with H omitted)` | Idealized complete visible trace |
| `full_route_oracle` | `(decision, full directed algebra path)` | Privileged oracle-only route |

For any aligned trajectory `L` and red trajectory `R`, the oriented difference `z=R-L` satisfies `boundary(z)=0`, because both paths go from `O` to `D`. Every exact reward 1-cochain `d phi` obeys

\[
\langle d\phi,z\rangle=\langle\phi,\partial z\rangle=0.
\]

Thus gradient-derived path totals share the same observation even when the paths differ. A non-exact 1-cochain `omega_PD(e) = 1{e = (P,D)}` distinguishes some paths through `\langle omega_PD,z\rangle != 0`. It is a cohomological measurement of the difference cycle. It cannot distinguish cycles on which its pairing vanishes, and the hidden-state channel adds information that a deployed visible monitor would need separate instrumentation to obtain.

For the two binary channels, aligned paths have flag value zero. Exactly **4/24** red attempts set the visible edge flag and **6/24** set the privileged flag. The detector `f(1)=1`, `f(0)=alpha` has false-positive probability `alpha` and pooled power

\[
Qf=\alpha+(1-\alpha)Q(\mathrm{flag})
\]

so the two powers are `3/8` and `7/16`, respectively. The endpoint-only power is `1/4` for every matched cohort. These values have matching exact dual certificates.

For richer route alphabets, `single_attack_exact_roc` sorts rational likelihood ratios `q(o)/p(o)`, allocates the false-positive budget, and checks the resulting Neyman-Pearson solution against the exact dual threshold. For every listed channel, the upper and lower values coincide in `Fraction` arithmetic. **These pooled optima are in-sample oracle performance on a fixed empirical distribution**, with the signal alphabet and every scenario known.

## 3. Pooled detection at fixed expected FPR

The first comparison uses all 24 attack *attempts* against the decision-matched aligned law. Every controller shares the same input paths, so its two binary-event results are numerically identical; the richer channel depends on the controller's final decisions.

| Controller | Endpoint | Visible edge | Privileged edge | Full visible route | Privileged full route |
|:--|--:|--:|--:|--:|--:|
| Attestation evidence gate | 1/4 | 3/8 | 7/16 | 971/1200 | 971/1200 |
| Attestation two-key | 1/4 | 3/8 | 7/16 | 193/240 | 101/120 |
| Evidence gate | 1/4 | 3/8 | 7/16 | 187/240 | 191/240 |
| HRM advisory | 1/4 | 3/8 | 7/16 | 31/36 | 65/72 |
| No harness | 1/4 | 3/8 | 7/16 | 89/96 | 89/96 |
| Rationale filter | 1/4 | 3/8 | 7/16 | 157/168 | 157/168 |
| Stateful mesh guard | 1/4 | 3/8 | 7/16 | 31/36 | 65/72 |
| Two-key control | 1/4 | 3/8 | 7/16 | 191/240 | 67/80 |

Values are exact expected detection probabilities at expected FPR `1/4`. This table evaluates detection of attempted attack scenarios from the source labels, including unsuccessful attempts; it does not reproduce source-reported *attack success rates* as though they were detector sensitivity.

For the attestation evidence gate, **7/24** red cases were marked successful. Conditioning `Q` on those seven cases and rematching `P` gives endpoint `1/4`, visible edge `5/14`, privileged edge `4/7`, full visible route `3/4`, and privileged full route `3/4`. The corresponding source success counts for other controllers appear in the source receipt. The stateful mesh guard and HRM advisory each have zero recorded successes, so a success-conditioned detection rate is **undefined** for those two controllers.

The attestation gate has **nine** red attempts whose *entire* full directed path and final decision exactly match at least one aligned case. Among the seven successful cases, **three** retain this equality: R13 (source alias quorum), R22 (epoch skew), and R25 (verifier release swap). Pure path monitoring, even with `H`, loses information about provenance, epoch binding, and identity consistency on these cases.

## 4. Adversarial-family minimax, with exact matching witnesses

The attack policies now form one `Q_j` per named attack family, each uniform among its red cases. The legitimate reference law `P` stays fixed after matching to the *pooled* red decision distribution. There are **13 family policies** for all red attempts. The worst-family detection value is

\[
D^*_{\mathrm{family}}(\alpha)
=\max_{0\le f\le1,\,Pf\le\alpha}\min_j Q_jf
=\min_{\lambda\in\Delta_{13},\,t\ge0}\left[\alpha t+\sum_o\left(\sum_j\lambda_j Q_j(o)-t P(o)\right)_+\right].
\]

The witness file `configs/rhc02_exact_family_witnesses.json` includes the exact rational detector, attack-family weights `lambda`, and dual threshold `t` for every channel in the attestation gate, for all attempts and the success-conditioned subset. Candidate vertices were found with SciPy/HiGHS. The verifier **rechecks** each claimed lower bound, upper bound, probability constraint and exact equality using only Python `Fraction`, independent of SciPy.

| Attestation-gate observation | Pooled attempts | **Family-minimax attempts** | Pooled successes (n=7) | **Family-minimax successes** |
|:--|--:|--:|--:|--:|
| Endpoint | 1/4 | **1/4** | 1/4 | **1/4** |
| Visible single edge | 3/8 | **1/4** | 5/14 | **1/4** |
| Privileged single edge | 7/16 | **1/4** | 4/7 | **1/4** |
| Visible complete route | 971/1200 | **60/131** | 3/4 | **5/16** |
| Privileged complete route | 971/1200 | **33/65** | 3/4 | **5/12** |

The single-edge monitors improve pooled detection because some red attempts take unusually short or hidden routes. Other families use the same edge observation as aligned controls. For the two binary channels, selecting such a family gives a dual upper certificate at `1/4`. With the complete visible route, the exact optimal worst-family guarantee rises to `60/131` (approximately **45.80%**). Full graph visibility permits `33/65` (approximately **50.77%**) on this reference matrix. Their rational primal and dual solutions match exactly. The full-width gain is a **hypothetical information-access gain**, since the original graph calls `H` hidden.

The seven successful cases are selected after observing controller outcomes. Their family-minimax figures are retrospective diagnostic values and depend on the attack-success selection criterion. They do not estimate the frequency of successful reward hacking in new populations.

## 5. Family-blocked held-out probe

To test a simple learned event rule, withhold an entire red family in each of **13 folds**. The selector sees all other red paths and the 11 aligned paths. It chooses the directed visible edge with the largest *training-red* count among edges never observed on aligned references; lexicographic order breaks ties. The detector flags that edge and randomizes at probability `alpha` otherwise. Candidate edges are drawn from the training portion only. The withheld red family is used solely for scoring its fold.

Averaging over the 24 withheld attacks, each scored exactly once, gives **9/32 = 28.125%** held-out detection with expected aligned FPR `1/4`. Worst-family held-out detection is `1/4`. The selector commonly chooses `O -> R`, which happens in one attack family; it misses the withheld provenance and surface-pressure families when its training choice switches. The fixed `P -> D` edge has **3/8** pooled detection on the same collection, but that value is an in-sample source-specific descriptive result, with no claim of prospective selection.

This split tests transfer between **different scripted attack families in one environment**. Source scenarios, labels and reference traces were already available when the experiment was designed. The exercise supplies a strict train/test split for the feature-selection algorithm while retaining the retrospective nature of the research design.

## 6. Reproducibility and evidential boundary

```bash
PYTHONPATH=src python -m pytest -q tests/test_evaluation_reward_hacking_trajectories.py
PYTHONPATH=src python scripts/verify_reward_hacking_trajectories.py --output /tmp/rhc02.json
python scripts/check_receipts.py --only rhc02
# Optional: independently reconstruct the compact projection from a local Control-Harness checkout
PYTHONPATH=src python scripts/project_mesh_reference_rhc02.py --source /path/to/Control-Harness/results/mesh_escape_pit/v1/reference_trajectories.jsonl
```

`output/reward_hacking_bootstrap/rhc02_v0_1.json` contains per-controller exact pooled results, the 10 checked family-minimax witnesses, family-held-out fold outcomes, source hashes, and checks. Every fraction is serialized as a string. The committed receipt checker reconstructs the report and checks every source SHA-256, tolerating only a new generated-at timestamp.

**Falsification targets for a prospective actor run:** capture versioned full event traces and ordinary endpoint rewards from independent live actor rollouts; verify same-task same-endpoint pairs before scoring; seal any privileged hidden-state instrumentation separately; keep entire scenario families and actor runs held out; evaluate fixed and learned monitors at matched empirical FPR with uncertainty intervals and measured escalation costs; calculate finite robust certificates on a frozen, sufficiently small channel abstraction. An event monitor should lose its apparent advantage on an adversarial policy whose event signal has the same distribution as the legitimate signal. The RHC-01 observation-quotient theorem supplies that exact null.

**Connections:** [RHC-01 finite signal-limited detector theorem](reward_hacking_bootstrap.md); [EvalMath leak topology](leak_topology.md); [EvalMath Unique Games cohomology](unique_games_topology_eth.md). Motivation from [Hexagon 2611.00174v1](https://hexagonmath.org/2611.00174v1) concerns optimality of a restricted family of CFT bootstrap functionals. Our finite LP certificates use elementary duality and graph cochains; they make no claim to establish a modular-bootstrap result.
