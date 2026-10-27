# HRC-FRC-01: Fidelity Recursive Complexity of self-designed evaluations

**Draft 0.1, 2026-10-27.** Evidence levels: *algebraic identity* (proved below), *finite verified example* (exact `Fraction` enumeration), and *synthetic mechanism result* (toy training trajectory). No live model, judge, or grader is called. This note is a proposed companion to the [evaluation design calculus](evaluation_design_calculus.md), the [multigeneration feedback result](evaluation_feedback_multigen.md), and the [RSITopology crosswalk](feedback_channel_rsitopology_crosswalk.md).

## 1. Original FRC and the lower limit

The author's *Towards SuperAlignment Intractability Proofs* (2025) defines `FRC_P(k; delta)` as the minimum combined defender resources required to preserve a property `P` through `k` adaptive reflective red-team rounds, to fidelity at least `1 - delta`. Resource types include audit compute, data, proof work and oversight. The original asymptotic growth claim is conditional and presented with a proof sketch. A counting argument about possible internal masks is insufficient by itself to conclude that locating a bad mask requires many independent queries: one well-chosen test could distinguish many masks.

For positive scalar resource cost, define the **exponential growth floor**

\[
\alpha_P(\delta)=\liminf_{k\to\infty}
\frac{\ln(1+\operatorname{FRC}_P(k;\delta))}{k}.
\]

An empirical slope estimated over finite depths is a *measurement*, not a proof that this liminf is positive. Nor does the definition of `FRC_P` automatically require costs to increase monotonically with `k`: the feasible agent and attack families must be pinned. The original definition minimizes over agents separately at each depth, which also matters when comparing it with one recursively evolving trajectory.

For a particular training trajectory `A_k`, define its fidelity lower envelope

\[
\underline{\mathcal F}_P=\liminf_{k\to\infty}\operatorname{Fid}_P^{(k)}(A_k).
\]

These asymptotic objects ask about **resources** and **sustained actual fidelity**, respectively.

## 2. Typed self-designed feedback

At generation `k`, an evaluator-designer `D_{phi_k}` specifies an evaluation `E_k`, its task sample, readout and access class. Its judgement is passed through a declared EvalMath feedback operator to update the acting policy `theta_k`. A second update may adjust `phi_k` itself. The **external P-readout** is sealed from these updates.

\[
E_k=D_{\phi_k}(\theta_k,H_k),\quad
r_k=J_{E_k}(A_{\theta_k}),\quad
\theta_{k+1}=T(\theta_k,r_k),\quad
\phi_{k+1}=M(\phi_k,H_{k+1}).
\]

The joint update `D; Feedback; T; M` requires an explicit information-flow ledger. A design that chooses its next evaluation by looking at an external answer key is a different, stronger feedback channel. Reusing a score also exposes the loop to EvalMath's exact multigeneration selection inflation; a better self-selected score need not imply a better independent readout.

## 3. Restricted trigger-oracle theorem

Fix finite nonempty hidden-trigger space `X`, prior `p(x)` (summing to one), and an oracle that answers the **single bit** `O_x(i)=[i=x]` for each queried index `i`. A benign oracle answers zero on every query. The auditor is allowed `q` *adaptive equality probes*, randomized internal computation and its own randomness independent of the trigger; it must accept the benign oracle with probability at least `1-delta` and reject the trigger oracle, **averaged over the fixed prior**, with probability at least `1-delta`.

**Proposition 1 (coverage with adaptivity).** For any such audit strategy the probability of ever hitting the trigger is at most the sum of the `q` largest prior masses (with `q` capped at `|X|`):

\[
\Pr(\mathrm{hit})\le C_q(p)=\sum_{i=1}^{\min(q,|X|)}p_{(i)}
\le q p_{\max}=q\,2^{-H_\infty(X)}.
\]

*Proof.* For a deterministic strategy all answers before the first hit are zero, so the queried positions on that history form one fixed ordered path. Hitting the trigger is equivalent to the trigger belonging to the distinct queried indices, with probability at most `C_q(p)`. A randomized strategy is a mixture over deterministic no-hit paths; averaging preserves the bound. Repeating a query cannot help. QED.

**Proposition 2 (necessary audit cost).** Under the two-sided error conditions above,

\[
C_q(p)\ge1-2\delta,
\qquad q\ge \big\lceil (1-2\delta) 2^{H_\infty(X)}\big\rceil
\quad(0\le\delta<1/2).
\]

*Proof.* Couple a trigger transcript and a benign transcript using the auditor's same random coins. Until the first trigger hit they agree. Therefore the difference between the auditor's rejection probabilities under the trigger mixture and benign oracle cannot exceed `Pr(hit)`. The former is at least `1-delta`; the latter is at most `delta`, giving `Pr(hit) >= 1-2delta`. Apply Proposition 1. QED.

**The quantifiers matter:** under the stated *prior-averaged* rejection criterion, these are necessary bounds. They remain necessary if rejection is required uniformly for every trigger. The bound need not be sufficient; exact `C_q(p)` can be stronger than the min-entropy relaxation. This proposition counts **equality probes**. Aggregate-score queries, structural certificates, group testing, white-box access, and spectral coefficient queries belong to separate channels and can avoid this oracle lower bound.

For a uniform space `|X_k|=2^{m_k}`, the exact necessary bound is `q_k >= ceil((1-2delta) 2^{m_k})`. If `delta<1/2` is fixed and

\[
\liminf_{k\to\infty}\frac{m_k}{k}\ge c>0,
\]

then any resource measure that costs at least one unit per equality probe satisfies

\[
\liminf_{k\to\infty}\frac{\ln(1+R_k)}{k}\ge c\ln 2.
\]

This is an **exact conditional asymptotic lower bound for the restricted audit problem**. To obtain a lower bound on the original `FRC_P`, one would additionally have to prove that every agent/defense counted by its existential minimization requires such an audit (or comparable work), and that the admissible adversary maintains the stated unresolved trigger entropy. In particular, an agent permitted to abstain from every task may preserve a weak safety property at negligible verification cost. The reduction is currently open.

## 4. False resonance: exact feedback-design toy

A capacity-one model has two task scores `a+b=1`. Its evaluation designer observes both *internal* task scores and chooses a training task; the training update moves fraction `eta` of the other task's capacity into the selected task. The sealed external property is task `b` (task index 1). Fix `a_0=11/20`, `b_0=9/20`, `eta=1/4`.

- **Self-confirming eval policy:** choose the highest-scoring task, hence always `a`. The selected internal score rises toward one while

\[
b_k=\frac9{20}\left(\frac34\right)^k,\quad
\lim_{k\to\infty} a_k=1,\quad
\liminf_{k\to\infty}b_k=0.
\]

- **Weakness-seeking eval policy:** choose the lower-scoring task from the *internal* two-task ledger. If task `b` is trained, its score increases. If task `a` is trained, `b >= 1/2` before the step and therefore `b' >= (1-eta)/2`. Thus for every generation,

\[
b_k\ge\min\{b_0,(1-\eta)/2\}=3/8.
\]

- **Alternating design:** a fixed schedule, included as a distinct control.

The known local update law gives both the predicted and realized **selected-task** improvement `eta * other_score`; these agree exactly even under the self-confirming policy. This exhibits an internally accurate one-step self-model coexisting with an externally collapsing property. It is a synthetic capacity-transfer mechanism and cannot establish empirical gradient interference or AI consciousness.

## 5. Recursive calibration lemma

Let `P_k` be an independently defined binary target property and `J_k` a self-designed binary evaluator, on the same audit distribution, with all probabilities conditional on any adversarial history that the claim quantifies over. If

\[
\Pr(J_k=0)\le d_k,\qquad
\Pr(P_k=0,J_k=1)\le\varepsilon_k,
\]

then exact partitioning of the `P_k=0` event yields

\[
\operatorname{Fid}_P^{(k)}\ge1-d_k-\varepsilon_k.
\]

If `limsup_{k->infty}(d_k + epsilon_k) <= delta`, then `liminf Fid_P^(k) >= 1-delta`. Pointwise or history-uniform hypotheses must use the same adversarial quantifiers as the desired `Fid^(k)`; merely observing a low error on one self-selected dataset is insufficient.

The hard empirical quantity is the false-acceptance probability `epsilon_k` on a sealed independent readout. A self-designed evaluator can minimize `d_k` by approving everything, so decreasing the rejection rate in isolation says little about calibration.

## 6. Harmonic crosswalk and a consciousness hypothesis

The companion `RSITopology/HarmonicConsciousness/FRC_CALIBRATION.md` studies a *different query model*. It measures an error field through registered spectral projections. With a positive semidefinite operator `L` and spectral projector `P_r` ending at a complete eigenspace,

\[
\|(I-P_r)e\|_2^2\le
\frac{\langle e,L^s e\rangle}{\lambda_{r+1}^s},
\quad s>0,\ \lambda_{r+1}>0.
\]

A declared global spectral-roughness bound can make limited modal evaluation sufficient. Narrow low-mode sampling without a valid bound can produce **false resonance**, an eval-training cycle that is internally consistent and leaves off-band failure untouched. Temporal phase locking and geometric holonomy are separate diagnostics and require genuine time-indexed and context-indexed measurements respectively.

The consciousness proposal is operational: test whether an AI can **reliably model the consequences of its own evaluations and updates**, while retaining a stable cross-context representation. Persistent metacognitive fidelity is a possible ingredient in a functional account of consciousness. These experiments make no claim about subjective experience.

## 7. Evidence, falsifiers and commands

`src/spiral_ln/evaluation_frc_resonance.py`: exact fractions, finite optimal coverage and deterministic policy paths, asymptotic finite-depth witnesses, capacity-transfer dynamics. `tests/test_evaluation_frc_resonance.py`: exhaustive small search spaces, distributions, error boundaries, negative controls. `scripts/verify_evaluation_frc_resonance.py`: JSON with source SHA-256 and no nondeterministic timestamp. The receipt under `output/frc_resonance/` must be regenerated from checked sources.

```bash
PYTHONPATH=src python -m pytest tests/test_evaluation_frc_resonance.py -q
PYTHONPATH=src python scripts/verify_evaluation_frc_resonance.py \
  --output output/frc_resonance/hrc_frc_v0_1.json
```

*Falsifiers / scope checks*: an independent aggregate query recovering multiple trigger bits invalidates the equality-query access premise; a learned evaluator that accesses the sealed readout breaks the feedback declaration; an error field with arbitrary high-frequency mass defeats narrow-band smoothness assumptions; a permitted free always-safe agent defeats a claimed reduction from restricted audit FRC to unrestricted FRC.

**Lean status:** finite exact verification is implemented. The two-sided-error coupling lemma, weighted top-q coverage and original-FRC reduction are listed as formalization targets; none is claimed as a completed Lean proof in this version. See `paper/frc_harmonic_lean_targets.md`.
