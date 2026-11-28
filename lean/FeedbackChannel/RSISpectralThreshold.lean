import Mathlib

/-!
# Two-variable recursive-improvement feedback threshold

The (nonnegative) research-capability and capability-research couplings are b and c.
When both diagonal retention coefficients a and d are strictly below one,
the dominant eigenvalue of the associated 2-by-2 nonnegative matrix crosses
one exactly when b*c exceeds (1-a)*(1-d).

This certificate is a statement about the finite linearized model. An empirical
AI self-improvement process needs independently estimated coefficients and
out-of-distribution capability measurements before this threshold can be used.
-/

namespace FeedbackChannel.RSISpectralThreshold

/-- Larger eigenvalue of the two-by-two real feedback matrix [[a,b],[c,d]]
under the nonnegative-coupling hypotheses used in the theorems below. -/
noncomputable def dominant (a b c d : ℝ) : ℝ :=
  (a + d + Real.sqrt ((a - d) ^ 2 + 4 * b * c)) / 2

/-- A square-root-free certificate for the feedback threshold. -/
theorem discriminant_nonneg (a b c d : ℝ)
    (hb : 0 ≤ b) (hc : 0 ≤ c) :
    0 ≤ (a - d) ^ 2 + 4 * b * c := by
  have hbc : 0 ≤ b * c := mul_nonneg hb hc
  nlinarith [sq_nonneg (a - d)]

/-- Exact supercriticality threshold for a cooperative two-variable feedback
system with both self-retention factors below one. -/
theorem dominant_gt_one_iff (a b c d : ℝ)
    (ha : a < 1) (hd : d < 1)
    (hb : 0 ≤ b) (hc : 0 ≤ c) :
    1 < dominant a b c d ↔ (1 - a) * (1 - d) < b * c := by
  let D : ℝ := (a - d) ^ 2 + 4 * b * c
  have hD : 0 ≤ D := by
    dsimp [D]
    exact discriminant_nonneg a b c d hb hc
  have hs : 0 ≤ Real.sqrt D := Real.sqrt_nonneg _
  have hsq : (Real.sqrt D) ^ 2 = D := Real.sq_sqrt hD
  have ht : 0 < 2 - a - d := by linarith
  have hpoly :
      D - (2 - a - d) ^ 2 =
        4 * (b * c - (1 - a) * (1 - d)) := by
    dsimp [D]
    ring
  change 1 < (a + d + Real.sqrt D) / 2 ↔
    (1 - a) * (1 - d) < b * c
  constructor
  · intro h
    have hlo : 0 < Real.sqrt D - (2 - a - d) := by linarith
    have hhi : 0 < Real.sqrt D + (2 - a - d) := by linarith
    have hprod :
        0 < (Real.sqrt D - (2 - a - d)) *
          (Real.sqrt D + (2 - a - d)) := mul_pos hlo hhi
    have hdelta : 0 < D - (2 - a - d) ^ 2 := by nlinarith [hprod, hsq]
    rw [hpoly] at hdelta
    nlinarith
  · intro h
    have hdelta : 0 < D - (2 - a - d) ^ 2 := by
      rw [hpoly]
      nlinarith
    have hstrict : 2 - a - d < Real.sqrt D := by
      by_contra hn
      have hle : Real.sqrt D ≤ 2 - a - d := le_of_not_gt hn
      have hprod :
          0 ≤ (2 - a - d - Real.sqrt D) *
            (2 - a - d + Real.sqrt D) :=
        mul_nonneg (by linarith) (by linarith)
      nlinarith [hsq, hdelta]
    linarith

/-- An exact square-root balancing certificate: the minimum of
m + r²/m for m>0 is attained at m=r when r>0. -/
theorem budget_balance (m r : ℝ) (hm : 0 < m) :
    2 * r ≤ m + r ^ 2 / m := by
  have hnonneg : 0 ≤ (m - r) ^ 2 / m :=
    div_nonneg (sq_nonneg _) hm.le
  have hid : (m - r) ^ 2 / m = m + r ^ 2 / m - 2 * r := by
    field_simp [ne_of_gt hm]
    ring
  linarith

theorem budget_balance_attained (r : ℝ) (hr : 0 < r) :
    2 * r = r + r ^ 2 / r := by
  field_simp [ne_of_gt hr]
  ring

#print axioms FeedbackChannel.RSISpectralThreshold.dominant_gt_one_iff
#print axioms FeedbackChannel.RSISpectralThreshold.budget_balance

end FeedbackChannel.RSISpectralThreshold
