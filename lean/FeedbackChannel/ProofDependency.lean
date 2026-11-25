import Mathlib

namespace FeedbackChannel.ProofDependency

/-- Algebraic shared-obligation failure floor, conditional on the declared model. -/
theorem shared_floor (q r : ℚ) (k : ℕ) (hq : q ≤ 1) (hr : 0 ≤ r) :
    q ≤ q + (1-q)*r^k := by
  have h : 0 ≤ (1-q)*r^k := mul_nonneg (sub_nonneg.mpr hq) (pow_nonneg hr k)
  linarith

/-- Two independent certificates with equal marginals versus a shared gate. -/
theorem shared_two_gap (q r : ℚ) :
    q + (1-q)*r^2 - (q+(1-q)*r)^2 = q*(1-q)*(1-r)^2 := by
  ring

theorem shared_two_dominates (q r : ℚ) (hq0 : 0 ≤ q) (hq1 : q ≤ 1) :
    (q+(1-q)*r)^2 ≤ q + (1-q)*r^2 := by
  have h := shared_two_gap q r
  have hpos : 0 ≤ q*(1-q)*(1-r)^2 :=
    mul_nonneg (mul_nonneg hq0 (sub_nonneg.mpr hq1)) (sq_nonneg (1-r))
  linarith

/-- Intersection bounds from the four nonnegative joint cells of two events. -/
theorem two_event_bounds (a b c d : ℚ) (ha : 0 ≤ a) (hb : 0 ≤ b)
    (hc : 0 ≤ c) (hd : 0 ≤ d) (hs : a+b+c+d = 1) :
    max 0 ((a+b)+(a+c)-1) ≤ a ∧ a ≤ min (a+b) (a+c) := by
  constructor
  · apply max_le
    · exact ha
    · linarith
  · apply le_min <;> linarith

end FeedbackChannel.ProofDependency
