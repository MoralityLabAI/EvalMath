import Mathlib

/-! CLQ arithmetic lemmas, draft. Full quotient action and cycle separation remain open. -/
namespace FeedbackChannel.CollatzQuotient

def oddNumerator (d n : ℕ) : ℕ := if n % 4 = 1 then 3*n+d else n+d

theorem oddNumerator_four (d n : ℕ) (hd : d % 4 = 1) (hn : n % 2 = 1) :
    oddNumerator d n % 4 = 0 := by
  unfold oddNumerator
  split <;> omega

theorem odd_bound (d n r : ℕ) (hr : r ≤ oddNumerator d n / 4) :
    4*r ≤ 3*n+d := by
  unfold oddNumerator at hr
  split at hr <;> omega

theorem strict_descent (d n r : ℕ) (hn : d < n) (hr : 4*r ≤ 3*n+d) : r < n := by
  omega

theorem closed_region (d n r : ℕ) (hn : n ≤ d) (hr : 4*r ≤ 3*n+d) : r ≤ d := by
  omega

def advance (R : ℕ → ℕ) : ℕ → ℕ → ℕ
  | 0, n => n
  | k+1, n => advance R k (R n)

theorem finite_entry (d : ℕ) (R : ℕ → ℕ) (hR : ∀ n, 4*R n ≤ 3*n+d) (n : ℕ) :
    ∃ k, advance R k n ≤ d := by
  refine Nat.strong_induction_on n ?_
  intro m ih
  by_cases hm : m ≤ d
  · exact ⟨0, hm⟩
  · have hlt : R m < m := strict_descent d m (R m) (by omega) (hR m)
    obtain ⟨k, hk⟩ := ih (R m) hlt
    exact ⟨k+1, hk⟩

-- Integer, rather than truncated natural, subtraction is essential here.
theorem gate_range (d z : ℤ) (hd : 0 < d) (h0 : 0 ≤ z) (h1 : z < 2*d) :
    0 ≤ (if z < d then z else z-d) ∧ (if z < d then z else z-d) < d := by
  by_cases hlt : z < d <;> simp [hlt] <;> omega

theorem gate_unique (d z s : ℤ) (hd : 0 < d) (h0 : 0 ≤ z) (h1 : z < 2*d)
    (hs0 : 0 ≤ s) (hs1 : s < d) (hc : s = z ∨ s = z-d) :
    s = if z < d then z else z-d := by
  by_cases hlt : z < d <;> simp [hlt] <;> omega

end FeedbackChannel.CollatzQuotient
