import Mathlib

namespace FeedbackChannel.NFAS

/-- Three pairwise conflict constraints imply the randomized ceiling.
This is the arithmetic endpoint, not a formalization of the stopping game. -/
theorem three_conflict_ceiling (t₁ t₂ t₃ : ℚ)
    (h12 : t₁ + t₂ ≤ 1) (h13 : t₁ + t₃ ≤ 1) (h23 : t₂ + t₃ ≤ 1) :
    (t₁ + t₂ + t₃) / 3 ≤ 1 / 2 := by
  linarith

/-- Binary successes in mutually conflicting worlds permit at most one success. -/
theorem three_binary_ceiling (t₁ t₂ t₃ : ℚ)
    (b1 : t₁ = 0 ∨ t₁ = 1) (b2 : t₂ = 0 ∨ t₂ = 1)
    (b3 : t₃ = 0 ∨ t₃ = 1)
    (h12 : t₁ + t₂ ≤ 1) (h13 : t₁ + t₃ ≤ 1) (h23 : t₂ + t₃ ≤ 1) :
    (t₁ + t₂ + t₃) / 3 ≤ 1 / 3 := by
  rcases b1 with h1 | h1 <;> rcases b2 with h2 | h2 <;>
    rcases b3 with h3 | h3 <;> linarith

/-- The two-action common-threshold coupling identity for arbitrary rational
payoffs. When p,q are in [0,1] the three coefficients are probabilities. -/
theorem two_action_threshold (a b p q : ℚ) :
    min (p * a + (1 - p) * b) (q * a + (1 - q) * b) =
      min p q * a + (1 - max p q) * b + (max p q - min p q) * min a b := by
  by_cases hp : p ≤ q
  · by_cases ha : a ≤ b
    · have h : q * a + (1 - q) * b ≤ p * a + (1 - p) * b := by
        nlinarith [mul_nonneg (sub_nonneg.mpr hp) (sub_nonneg.mpr ha)]
      simp only [min_eq_left hp, max_eq_right hp, min_eq_left ha, min_eq_right h]
      ring
    · have ha' : b ≤ a := le_of_lt (lt_of_not_ge ha)
      have h : p * a + (1 - p) * b ≤ q * a + (1 - q) * b := by
        nlinarith [mul_nonneg (sub_nonneg.mpr hp) (sub_nonneg.mpr ha')]
      simp only [min_eq_left hp, max_eq_right hp, min_eq_right ha', min_eq_left h]
      ring
  · have hp' : q ≤ p := le_of_lt (lt_of_not_ge hp)
    by_cases ha : a ≤ b
    · have h : p * a + (1 - p) * b ≤ q * a + (1 - q) * b := by
        nlinarith [mul_nonneg (sub_nonneg.mpr hp') (sub_nonneg.mpr ha)]
      simp only [min_eq_right hp', max_eq_left hp', min_eq_left ha, min_eq_left h]
      ring
    · have ha' : b ≤ a := le_of_lt (lt_of_not_ge ha)
      have h : q * a + (1 - q) * b ≤ p * a + (1 - p) * b := by
        nlinarith [mul_nonneg (sub_nonneg.mpr hp') (sub_nonneg.mpr ha')]
      simp only [min_eq_right hp', max_eq_left hp', min_eq_right ha', min_eq_right h]
      ring

end FeedbackChannel.NFAS
