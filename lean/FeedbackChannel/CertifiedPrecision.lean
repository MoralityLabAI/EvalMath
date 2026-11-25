import Mathlib

/-!
# MIT-09/10: certified precision and decision-sensitive certificates

Supporting lemmas for `paper/certified_instrument_transfer.md`.

* `lrr_entry_error`: a largest-remainder rounded entry differs from the scaled value by
  less than one grid unit (raised entries have positive fractional part).
* `tv_box_bound`: a zero-sum perturbation bounded by `u` entrywise has positive part at most
  `card * u / 2` (the total variation envelope).
* `ratio_box_mono`: the box bound used for posterior total variation.
* `robust_dominance`: interval-certified dominance implies true near-optimality.
* `approx_argmax_regret`: policy-specific perturbation radii bound the regret of an
  approximate argmax by the sum of two radii.
* `path_bound_step`: the induction step of the path bound on certified gaps.
-/
namespace CertifiedPrecision

open Finset

/-- Largest-remainder rounding raises only entries with a positive fractional part. -/
theorem lrr_entry_error (x : ℚ) (q : ℤ)
    (hq : q = ⌊x⌋ ∨ (q = ⌊x⌋ + 1 ∧ (⌊x⌋ : ℚ) < x)) :
    |x - q| < 1 := by
  have h1 := Int.floor_le x
  have h2 := Int.lt_floor_add_one x
  rw [abs_lt]
  rcases hq with h | ⟨h, hfrac⟩
  · subst h; constructor <;> linarith
  · subst h; push_cast; constructor <;> linarith

theorem tv_box_bound {ι : Type*} (s : Finset ι) (d : ι → ℚ) (u : ℚ)
    (hsum : ∑ y ∈ s, d y = 0) (hb : ∀ y ∈ s, |d y| ≤ u) :
    2 * ∑ y ∈ s, max (d y) 0 ≤ s.card * u := by
  have hsplit : ∀ y, max (d y) 0 + max (-d y) 0 = |d y| ∧ max (d y) 0 - max (-d y) 0 = d y := by
    intro y
    rcases le_total 0 (d y) with h | h
    · rw [max_eq_left h, max_eq_right (neg_nonpos.mpr h), abs_of_nonneg h]
      constructor <;> ring
    · rw [max_eq_right h, max_eq_left (neg_nonneg.mpr h), abs_of_nonpos h]
      constructor <;> ring
  have hdiff : ∑ y ∈ s, max (d y) 0 - ∑ y ∈ s, max (-d y) 0 = 0 := by
    rw [← Finset.sum_sub_distrib]
    calc ∑ y ∈ s, (max (d y) 0 - max (-d y) 0) = ∑ y ∈ s, d y :=
          Finset.sum_congr rfl (fun y _ => (hsplit y).2)
      _ = 0 := hsum
  have habs : ∑ y ∈ s, |d y| ≤ s.card * u := by
    calc ∑ y ∈ s, |d y| ≤ ∑ _y ∈ s, u := Finset.sum_le_sum hb
      _ = s.card * u := by rw [Finset.sum_const, nsmul_eq_mul]
  have hadd : ∑ y ∈ s, max (d y) 0 + ∑ y ∈ s, max (-d y) 0 = ∑ y ∈ s, |d y| := by
    rw [← Finset.sum_add_distrib]
    exact Finset.sum_congr rfl (fun y _ => (hsplit y).1)
  linarith

theorem ratio_box_mono (a b A B : ℚ) (ha : 0 ≤ a) (haA : a ≤ A) (hB : 0 ≤ B) (hBb : B ≤ b)
    (hpos : 0 < a + b) (hPos : 0 < A + B) :
    a / (a + b) ≤ A / (A + B) := by
  rw [div_le_div_iff₀ hpos hPos]
  nlinarith

theorem robust_dominance {α : Type*} (acts : Finset α) (Q Qt rad : α → ℚ) (g : ℚ) (star : α)
    (hstar : star ∈ acts) (hg : 0 ≤ g)
    (hrad : ∀ a ∈ acts, |Q a - Qt a| ≤ rad a)
    (hcert : ∀ a ∈ acts, a ≠ star → Qt a + rad a - g ≤ Qt star - rad star) :
    ∀ a ∈ acts, Q a - g ≤ Q star := by
  intro a ha
  by_cases h : a = star
  · subst h; linarith
  · have h1 := abs_le.mp (hrad a ha)
    have h2 := abs_le.mp (hrad star hstar)
    have h3 := hcert a ha h
    linarith [h1.1, h1.2, h2.1, h2.2]

theorem approx_argmax_regret {π : Type*} (pols : Finset π) (V Vt rad : π → ℚ) (phat : π)
    (hphat : phat ∈ pols) (hrad : ∀ p ∈ pols, |V p - Vt p| ≤ rad p)
    (hmax : ∀ p ∈ pols, Vt p ≤ Vt phat) :
    ∀ p ∈ pols, V p - V phat ≤ rad p + rad phat := by
  intro p hp
  have h1 := abs_le.mp (hrad p hp)
  have h2 := abs_le.mp (hrad phat hphat)
  have h3 := hmax p hp
  linarith [h1.1, h1.2, h2.1, h2.2]

theorem path_bound_step {ι : Type*} (s : Finset ι) (W g M : ℚ) (Wc Sc Pc : ι → ℚ)
    (hW : ∑ c ∈ s, Wc c ≤ W) (hWc : ∀ c ∈ s, 0 ≤ Wc c)
    (hS : ∀ c ∈ s, Sc c ≤ Wc c * Pc c) (hP : ∀ c ∈ s, Pc c ≤ M) (hM : 0 ≤ M) :
    W * g + ∑ c ∈ s, Sc c ≤ W * (g + M) := by
  have h1 : ∑ c ∈ s, Sc c ≤ ∑ c ∈ s, Wc c * M := by
    apply Finset.sum_le_sum
    intro c hc
    calc Sc c ≤ Wc c * Pc c := hS c hc
      _ ≤ Wc c * M := mul_le_mul_of_nonneg_left (hP c hc) (hWc c hc)
  have h2 : ∑ c ∈ s, Wc c * M = (∑ c ∈ s, Wc c) * M := by rw [Finset.sum_mul]
  have h3 : (∑ c ∈ s, Wc c) * M ≤ W * M := mul_le_mul_of_nonneg_right hW hM
  nlinarith

end CertifiedPrecision
