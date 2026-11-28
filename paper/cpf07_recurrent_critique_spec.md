# CPF-07: recurrent obligation-selection critic (prospective specification)

Status: specification only. No model has been trained or evaluated under this protocol.

## Question

Given a claim, an evidence packet and a partially audited obligation set, can a compact recurrent model choose the next obligation whose verification most reduces the residual false-authorization mass, and does that policy beat fixed and myopic schedules at equal audit budget?

CPF-01 §2 gives the target exactly. For a declared finite null model with surviving world set S, unused queries Q and budget k, the optimal value V(S, Q, k) is the minimum of mass(S) and, over q in Q, the sum of V(S_o, Q \ {q}, k-1) over non-reject outcomes o. The best first query is an argmin of that recurrence. CPF-07 asks a learned policy to approximate the argmin without enumerating worlds.

## Environment

* **Roots.** Procedural instances from `spiral_ln.evaluation_cpf_suite` train-split families (gate, degree, determinant) plus a new obligation-graph family: a claim with 4 to 12 obligations, each with a deterministic checker, a prior failure mass and declared correlations (shared-source, shared-mechanism, shared-checker groups as in CPF-01 §3).
* **State.** The prompt, the obligations verified so far with their outcomes, and the remaining budget. No gold label.
* **Action.** Choose one unused obligation or stop.
* **Reward.** Negative surviving false mass at the end of the episode (exact, from the finite oracle), minus a per-query cost λ swept over a preregistered grid.
* **Oracle labels.** The exact optimal action set per state from the CPF-01 recurrence (finite enumeration is feasible at these sizes), and the exact value gap of every action.

## Model

A looped (weight-tied) transformer of at most 60M parameters with a learned halting head, so recurrence depth can track remaining budget. Inputs are the serialized state; outputs are a distribution over obligations plus stop. Baselines: the same architecture without recurrence (fixed depth equal to the loop's mean), a greedy one-step mass-reduction heuristic, a fixed schedule ordered by prior failure mass, uniform random, and the exact oracle as the ceiling.

## Curriculum and custody

Train only on procedural roots generated with a fresh private seed, excluding every CPF-05 dev and primary root ID (`export_cpf_datagoblin.py procedural --exclude-prompts`). The CPF-05 primary panel stays sealed: its Data Goblin records carry `loss.eligible=false` and are used only for analysis. Repairs (incorrect to certified) and persistent failures from the CPF-05 ledgers may be used to choose which obligation families to oversample, never as training targets.

## Primary outcome and analysis

Primary: mean residual false mass at budget k ∈ {1, 2, 3} on a held-out obligation-graph test set generated with a separate private seed whose commitment is published before training, compared with the greedy baseline at equal k. Paired by root; report the mean difference with a family-stratified bootstrap interval and an exact sign test. Secondary: regret against the oracle, optimal-action agreement, calibration of the stop decision, and transfer to obligation counts outside the training range (13 to 16). Holm adjustment over the three budgets.

## Stopping and power

Fix the test set at 1,200 roots (400 per budget) before training. With a per-root standard deviation of residual mass near 0.05, the standard error is 0.0025, giving roughly 0.9 power to detect a 0.008 mean reduction at two-sided α = 0.05 per budget (before Holm adjustment). Train for a fixed number of steps chosen on a validation split; do not stop on test results.

## Negative results that count

The recurrent policy failing to beat greedy at k = 1 is expected (greedy is optimal at one step). The informative failure is no improvement at k = 2 or 3, where CPF-01's synthetic witness shows adaptive policies can reduce residual mass by a third relative to fixed schedules.
