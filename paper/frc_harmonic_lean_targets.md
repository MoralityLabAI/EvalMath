# Lean proof targets for HRC-FRC-02

Status 2026-10-27: **a candidate finite adaptive transcript proof was added to the GitHub research branch; CI/statement-fidelity review is pending**. The exact Python module passes its finite tests; these are proof obligations for a Lean/Mathlib implementation, not a claim of Lean verification.

## Ordered targets

1. `FRC.coverage_le_topq`: for `p : Fin n -> ℚ` nonnegative summing to one, a deterministic no-hit path of length `q` has coverage bounded by the sum of the `min(q,n)` highest masses. Prove from membership counting with repeated indices collapsed.
2. `FRC.coverage_le_q_max`: the same setting yields coverage `<= q * max p`. This step can be proved independent of sorting and is a good first theorem.
3. `FRC.randomized_coverage`: integrate the deterministic bound over a probability distribution on no-hit paths. Avoid silently assuming a deterministic evaluator.
4. `FRC.transcript_coupling`: for a benign all-zero oracle and hidden-trigger equality oracle, prove `|Pr(reject_trigger)-Pr(reject_benign)| <= Pr(hit)` under common auditor coins. Audit must have the same coins and output when observations coincide.
5. `FRC.audit_floor_sharp`: condition on benign false-rejection coins to prove the tight `(1-2δ)/(1-δ) <= C_q(p)` and the exact optimal randomized construction. A separate conservative finite uniform-seed theorem provides an initial supporting lemma.
6. `FRC.calibration_split`: prove `Pr(P=false) <= Pr(J=false) + Pr(P=false ∧ J=true)` for any joint finite distribution.
7. `FRC.capacity_lower_envelope`: for weakness-seeking two-task conserved-capacity update with `0<=η<=1`, induction gives `b_k>=min(b_0,(1-η)/2)`.
8. `FRC.exponential_liminf`: for `q_k≥(1-2δ)2^(c k)` and `δ<1/2`, prove the real-valued asymptotic inequality, with explicit positivity and `+1` in the logarithm.

## Fidelity and missing reductions

A Lean theorem about the restricted equality oracle must not be advertised as a theorem about the original existential `FRC_P(k;δ)` without an explicit reduction from every admissible agent/defense to an oracle audit. Formalization also needs a precise scalar resource functional, a fixed family of adversaries, and distinction between one evolving trajectory and an `exists A` selected anew for each depth.

Proposed finite Lean module: `lean/FeedbackChannel/FRCAdaptiveAudit.lean` (open until CI succeeds and quantifiers are checked). It counts outcome-changing triggers for an arbitrary adaptive Boolean decision tree, then sums the bound across finitely many equally weighted seeds. It does not encode arbitrary real-valued prior weights or the sharp rational two-sided constant.

Repository policy: do not add a claim to `lean/CLAIMS.md` before a clean `lake build`, `lake env lean axioms_check.lean`, and independent statement-fidelity review.
