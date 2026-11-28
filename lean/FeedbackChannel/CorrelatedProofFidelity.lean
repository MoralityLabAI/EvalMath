import Mathlib

namespace FeedbackChannel.CPF

/-- Four nonnegative atom weights imply the sharp intersection interval. -/
theorem frechet (a b r : ℚ) (h0 : 0 ≤ r) (ha : 0 ≤ a-r)
    (hb : 0 ≤ b-r) (hn : 0 ≤ 1-a-b+r) :
    max 0 (a+b-1) ≤ r ∧ r ≤ min a b := by
  constructor
  · apply max_le
    · exact h0
    · linarith
  · apply le_min
    · linarith
    · linarith

/-- Every point of the interval has a nonnegative four-atom witness. -/
theorem witness (a b r : ℚ) (hl : max 0 (a+b-1) ≤ r)
    (hu : r ≤ min a b) :
    0 ≤ r ∧ 0 ≤ a-r ∧ 0 ≤ b-r ∧ 0 ≤ 1-a-b+r := by
  have h0 : 0 ≤ r := le_trans (le_max_left _ _) hl
  have hs : a+b-1 ≤ r := le_trans (le_max_right _ _) hl
  have ha : r ≤ a := le_trans hu (min_le_left _ _)
  have hb : r ≤ b := le_trans hu (min_le_right _ _)
  exact ⟨h0, by linarith, by linarith, by linarith⟩

theorem atom_total (a b r : ℚ) : r + (a-r) + (b-r) + (1-a-b+r) = 1 := by ring

theorem conditional_audit (r c : ℚ) (hr : 0 ≤ r) (hc : 0 ≤ c) (hc1 : c ≤ 1) :
    0 ≤ r*c ∧ r*c ≤ r := by
  constructor
  · exact mul_nonneg hr hc
  · calc
      r*c ≤ r*1 := mul_le_mul_of_nonneg_left hc1 hr
      _ = r := by ring

end FeedbackChannel.CPF
