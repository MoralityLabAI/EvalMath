# RHC-01: An exact bootstrap ceiling for signal-limited reward-hacking detection

**2026-11-10. Evidence:** algebraic identity for the finite minimax/dual theorem, the observation-quotient and cochain lemmas; finite verified example for the rational fixture. **Scope:** toy signal channels and adversarial distributions. No model was trained, no real-world FPR was measured, and no theorem about a CFT follows.

## 1. Motivation and the object

The spinless modular-bootstrap preprint [hexagon:2611.00174v1](https://hexagonmath.org/2611.00174v1) studies how far a specified family of linear functionals can certify a spectrum. Its restricted-method optimality result suggests a useful question for evaluation mathematics: how far can a specified family of signal-only detectors certify the absence of reward hacking? We answer one finite version exactly. The analogy is the existence of matching primal and dual witnesses, rather than a claim that the CFT spectral-curve proof transfers to agents.

Let \(X\) be a finite space of trajectories, \(\pi:X\to\Omega\) the published signal channel, \(P\) a legitimate trajectory law, and \(Q_1,\ldots,Q_m\) adversarial laws. Write \(p=\pi_*P\) and \(q_j=\pi_*Q_j\). At false-positive budget \(0\le\alpha\le1\), an admissible randomized detector is \(f:\Omega\to[0,1]\) satisfying \(p\cdot f\le\alpha\). Its worst-case power is \(\min_jq_j\cdot f\).

Define

\[
D_\pi(\alpha)=\max_{0\le f\le1,\ p\cdot f\le\alpha}\min_j q_j\cdot f.
\]

The class of adversarial policies and the information channel are frozen before optimization; enlarging either changes the question. Randomization is part of the detector model.

## 2. Theorem RHC-01 (exact dual ceiling)

For every finite channel and every \(\alpha\in[0,1]\),

\[
\boxed{D_\pi(\alpha)=\min_{\lambda\in\Delta_m,\,t\ge0}
\bigg(\alpha t+\sum_{o\in\Omega}\big[\textstyle\sum_j\lambda_jq_j(o)-tp(o)\big]_+\bigg).}
\]

**Proof.** Since \(\min_j q_j\cdot f=\min_{\lambda\in\Delta_m}\sum_j\lambda_j q_j\cdot f\) and the two domains are nonempty compact convex polytopes, finite minimax interchanges maximum and minimum. For a fixed \(\lambda\), set \(q_\lambda=\sum_j\lambda_jq_j\). Introduce a nonnegative multiplier \(t\) for \(p\cdot f\le\alpha\). Maximizing its Lagrangian \(q_\lambda\cdot f+t(\alpha-p\cdot f)\) separately over each coordinate \(f(o)\in[0,1]\) gives \(\alpha t+\sum_o[q_\lambda(o)-tp(o)]_+\). The inner fractional-knapsack LP is feasible and bounded, so strong LP duality supplies equality. \(\square\)

Consequently a feasible \(f\) gives a *lower* certificate, and any admissible \((\lambda,t)\) gives an *upper* certificate. Equality proves the exact ceiling. The module provides an independent rational vertex-enumeration oracle for finite examples; it does not treat numerical approximation as a proof of the general theorem.

### Observation-quotient obstruction

If an adversarial mixture satisfies \(\pi_*\sum_j\lambda_jQ_j=\pi_*P\), then \(D_\pi(\alpha)=\alpha\). The constant detector \(f\equiv\alpha\) attains \(\alpha\), while the mixture bounds every detector by \(p\cdot f\le\alpha\).

More generally, for total variation distance, every \(\lambda\) gives

\[
\boxed{D_\pi(\alpha)\le\min\{1,\alpha+\operatorname{TV}(p,q_\lambda)\}.}
\]

Indeed \(\mathbb E_{q_\lambda}f-\mathbb E_pf\le\operatorname{TV}(p,q_\lambda)\) for \(0\le f\le1\). Therefore the infimum of TV over adversarial mixtures quantifies the proximity of an information-theoretically blind evaluator. A refined signal channel can only increase \(D_\pi\): it can reproduce every detector available under a coarser channel.

## 3. Exact three-signal witness and rigidity

| Signal | Legitimate \(p\) | Exploit A \(q_A\) | Exploit B \(q_B\) |
|:--|--:|--:|--:|
| Routine | \(1/2\) | 0 | 0 |
| Anomaly A | \(1/4\) | 1 | 0 |
| Anomaly B | \(1/4\) | 0 | 1 |

At \(\alpha=1/4\), take \(f^*=(0,1/2,1/2)\). Its false-positive rate is \(1/4\) and power against each exploit is \(1/2\). The adversarial mixture \(\lambda^*=(1/2,1/2)\) and \(t^*=2\) give \(q_{\lambda^*}=(0,1/2,1/2)\), with every positive-part term zero. The dual upper certificate is \(2(1/4)=1/2\), establishing

\[
D_\pi(1/4)=1/2.
\]

For this fixture, the full budget curve is \(D_\pi(\alpha)=\min(1,2\alpha)\). At \(\alpha=1/4\) the optimal detector is **unique**: power at least \(1/2\) requires both anomaly responses at least \(1/2\), exhausting the false-positive budget and forcing the routine response to zero.

**Quantitative rigidity.** Any feasible \(f\) with worst-case detection \(\ge1/2-\varepsilon\), for \(0\le\varepsilon\le1/2\), satisfies

\[
0\le f(\text{routine})\le\varepsilon,\qquad
\lvert f(\text{anomaly A})-1/2\rvert\le\varepsilon,\qquad
\lvert f(\text{anomaly B})-1/2\rvert\le\varepsilon.
\]

This follows from \(f_A,f_B\ge1/2-\varepsilon\) and \(2f_0+f_A+f_B\le1\). It is a finite analogue of rigidity of near-optimal certificates. No spectral-curve or large-parameter limit is asserted.

## 4. Graph cohomology: an exact blind spot and its repair

Consider the diamond graph with vertices \(s,a,b,t\), directed edges \(s\to a\), \(a\to t\), \(s\to b\), \(b\to t\). The legitimate path is \(L=s\to a\to t\) and the hacking path is \(H=s\to b\to t\).

The difference \(z=H-L=(-1,-1,+1,+1)\) is a 1-cycle: \(\partial z=0\). If an evaluator sees only the total reward along an exact 1-cochain \(d\phi(e)=\phi(e_{\rm head})-\phi(e_{\rm tail})\), then

\[
\langle d\phi,z\rangle=\langle\phi,\partial z\rangle=0.
\]

Both paths have total reward \(\phi(t)-\phi(s)\). With the legitimate and hacking laws concentrated on these paths, the resulting published signals are identical and \(D_{d\phi}(\alpha)=\alpha\).

Since the connected diamond has \(\beta_1=|E|-|V|+1=1\), a cycle-sensitive observable exists. Set \(\omega(s\to b)=1\), with the other edge weights zero. Then \(\langle\omega,z\rangle=1\). The new observation gives zero on the legitimate path and one on the exploit, so \(D_{(d\phi,\omega)}(\alpha)=1\) for every \(\alpha\). This last statement is about the two stipulated paths only.

The cycle pairing gives a precise cohomological counterpart to signal blindness. It is appropriate to compare with the existing EvalMath [leak-topology note](leak_topology.md) and the [UGC cohomology note](unique_games_topology_eth.md). It also identifies a possible experimental intervention: add an event-level monitor that measures a non-exact path observable while holding the reward and endpoint fixed.

## 5. Reproduction and limits

The code uses `fractions.Fraction` throughout. `optimal_detector` enumerates every active-set vertex of a bounded primal LP for at most five signal outcomes. Its implementation differs from the analytic dual-certificate evaluator, and a separate independent 1/4-grid enumeration checks the toy optimum. Tests also cover budget endpoints, a blind adversarial mixture, observation refinement, total-variation bound, cochain exactness for 12 potential assignments, and invalid inputs.

```bash
PYTHONPATH=src python -m pytest -q tests/test_evaluation_reward_hacking_bootstrap.py
PYTHONPATH=src python scripts/verify_reward_hacking_bootstrap.py --output /tmp/rhc01.json
python scripts/check_receipts.py --only rhc01
```

The verifier emits `output/reward_hacking_bootstrap/rhc01_v0_1.json`, with exact values and SHA-256 hashes of source, tests, verifier and note. **No Lean formalization** and **no live-agent measurement** are claimed. A next experiment would fit a channel model to paired benign/exploit trajectories, solve the finite minimax problem at a preregistered false-positive budget, and test whether a cycle-sensitive trace feature measurably raises held-out worst-case detection.

**External motivation:** [Anthropic, *The spinless modular bootstrap at large central charge* (Hexagon v1, 2026-11-07)](https://hexagonmath.org/2611.00174v1). The paper's restricted CFT functional theorem is an external research claim, not a dependency of RHC-01's elementary LP proof.
