import Mathlib

/-! CCF-01D: formal core. Kernel audit pending until CI. -/
namespace CertificateContext
open scoped BigOperators

noncomputable section
local instance (p : Prop) : Decidable p := Classical.propDecidable p

theorem policy_le_upper {T J : Type} (s : Finset T)
    (w : T → J → ℝ) (u : T → ℝ) (policy : T → J)
    (h : ∀ t j, w t j ≤ u t) :
    (∑ t ∈ s, w t (policy t)) ≤ ∑ t ∈ s, u t := by
  exact Finset.sum_le_sum (fun t _ => h t (policy t))

theorem policy_attains_upper {T J : Type} (s : Finset T)
    (w : T → J → ℝ) (u : T → ℝ)
    (h : ∀ t, ∃ j, w t j = u t) :
    ∃ policy : T → J, (∑ t ∈ s, w t (policy t)) = ∑ t ∈ s, u t := by
  classical
  refine ⟨fun t => Classical.choose (h t), ?_⟩
  exact Finset.sum_congr rfl (fun t _ => Classical.choose_spec (h t))

theorem cell_mixture_upper {J : Type} (f g : J → ℝ) (a b m θ : ℝ)
    (hθ : 0 ≤ θ) (hθ' : θ ≤ 1)
    (hf : ∀ j, f j ≤ a) (hg : ∀ j, g j ≤ b)
    (hm : ∃ j, m = θ * f j + (1 - θ) * g j) :
    m ≤ θ * a + (1 - θ) * b := by
  obtain ⟨j, hj⟩ := hm
  rw [hj]
  exact add_le_add (mul_le_mul_of_nonneg_left (hf j) hθ)
    (mul_le_mul_of_nonneg_left (hg j) (sub_nonneg.mpr hθ'))

theorem finite_mixture_upper {T J : Type} (s : Finset T)
    (f g : T → J → ℝ) (a b m : T → ℝ) (θ : ℝ)
    (hθ : 0 ≤ θ) (hθ' : θ ≤ 1)
    (hf : ∀ t j, f t j ≤ a t) (hg : ∀ t j, g t j ≤ b t)
    (hm : ∀ t, ∃ j, m t = θ * f t j + (1 - θ) * g t j) :
    (∑ t ∈ s, m t) ≤ θ * (∑ t ∈ s, a t) + (1 - θ) * (∑ t ∈ s, b t) := by
  calc
    (∑ t ∈ s, m t) ≤ ∑ t ∈ s, (θ * a t + (1 - θ) * b t) := by
      exact Finset.sum_le_sum (fun t _ =>
        cell_mixture_upper (f t) (g t) (a t) (b t) (m t) θ hθ hθ' (hf t) (hg t) (hm t))
    _ = _ := by simp only [Finset.sum_add_distrib, Finset.mul_sum]

theorem union_indicator_le_sum {I : Type} (s : Finset I) (b : I → Bool) :
    (if ∃ i ∈ s, b i = true then (1 : ℕ) else 0) ≤
      ∑ i ∈ s, (if b i = true then (1 : ℕ) else 0) := by
  classical
  by_cases h : ∃ i ∈ s, b i = true
  · rw [if_pos h]
    obtain ⟨i, hi, hb⟩ := h
    have hs : (if b i = true then (1 : ℕ) else 0) ≤
        ∑ j ∈ s, (if b j = true then (1 : ℕ) else 0) :=
      Finset.single_le_sum (fun j _ => Nat.zero_le _) hi
    simpa [hb] using hs
  · simp [h]

theorem missingness_bounds (total verified correct missing trueCorrect : ℕ)
    (hv : verified ≤ total) (hm : missing ≤ total - verified)
    (ht : trueCorrect = correct + missing) :
    correct ≤ trueCorrect ∧ trueCorrect ≤ correct + total - verified := by
  omega

end CertificateContext
