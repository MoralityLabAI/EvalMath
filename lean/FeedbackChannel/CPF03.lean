import Mathlib

namespace FeedbackChannel.CPF03

/-- An exact witness included in the approximate set inherits a universal bound. -/
theorem approximate_bound_transfer (W : Type) (E A G : W → Prop)
    (inc : ∀ w, E w → A w) (h : ∀ w, A w → G w) : ∀ w, E w → G w :=
  fun w he => h w (inc w he)

/-- Inclusion alone cannot give the converse. This is a logical countermodel. -/
theorem no_reverse_bound : ¬ (∀ E A G : Prop, (E → A) → (E → G) → A → G) := by
  intro h
  exact h False True False False.elim False.elim True.intro

theorem pointwise_threshold : ∀ i : ℕ, ∃ N : ℕ, ∀ n ≥ N, i ≤ n :=
  fun i => ⟨i, fun _ h => h⟩

theorem no_uniform_threshold : ¬ (∃ N : ℕ, ∀ i n : ℕ, N ≤ n → i ≤ n) := by
  rintro ⟨N, h⟩
  have bad := h (N+1) N (le_refl N)
  omega

end FeedbackChannel.CPF03
