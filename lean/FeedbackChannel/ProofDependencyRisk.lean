import Mathlib

open scoped BigOperators

namespace FeedbackChannel.ProofDependencyRisk

/-- Product lower bound on surviving a deterministic sequence of conditional hazard caps. -/
def survivalFloor (a : ℕ → ℚ) : ℕ → ℚ
  | 0 => 1
  | n + 1 => (1 - a n) * survivalFloor a n

theorem conditional_hazard_floor (a s : ℕ → ℚ) (h0 : s 0 = 1)
    (ha : ∀ n, a n ≤ 1)
    (hs : ∀ n, (1 - a n) * s n ≤ s (n + 1)) (n : ℕ) :
    survivalFloor a n ≤ s n := by
  induction n with
  | zero => simpa [survivalFloor, h0]
  | succ n ih =>
    exact le_trans (mul_le_mul_of_nonneg_left ih (sub_nonneg.mpr (ha n))) (hs n)

theorem conditional_hazard_cap (a s : ℕ → ℚ) (h0 : s 0 = 1)
    (ha : ∀ n, a n ≤ 1)
    (hs : ∀ n, (1 - a n) * s n ≤ s (n + 1)) (n : ℕ) :
    1 - s n ≤ 1 - survivalFloor a n := by
  have h := conditional_hazard_floor a s h0 ha hs n
  linarith

/-- Algebraic telescoping bound for additive risk spending. -/
def spending (a : ℕ → ℚ) : ℕ → ℚ
  | 0 => 0
  | n + 1 => spending a n + a n

theorem spending_cap (a r : ℕ → ℚ) (h0 : r 0 = 0)
    (hs : ∀ n, r (n + 1) ≤ r n + a n) (n : ℕ) :
    r n ≤ spending a n := by
  induction n with
  | zero => simpa [spending, h0]
  | succ n ih =>
    exact le_trans (hs n) (add_le_add_right ih (a n))

/-- From a nonnegative pathwise charge bound to an exposure-weighted bound. -/
theorem exposure_cap {ι : Type*} (I : Finset ι) (D v X : ι → ℚ) (C F : ℚ)
    (hX : ∀ i ∈ I, 0 ≤ X i)
    (hD : ∀ i ∈ I, D i ≤ C * v i)
    (hF : F ≤ ∑ i ∈ I, D i * X i) :
    F ≤ C * ∑ i ∈ I, v i * X i := by
  calc
    F ≤ ∑ i ∈ I, D i * X i := hF
    _ ≤ ∑ i ∈ I, C * (v i * X i) := by
      apply Finset.sum_le_sum
      intro i hi
      rw [← mul_assoc]
      exact mul_le_mul_of_nonneg_right (hD i hi) (hX i hi)
    _ = C * ∑ i ∈ I, v i * X i := by rw [Finset.mul_sum]

/-- Each false claim has one accepted invalid obligation in its witness. -/
theorem charge_bound {ι κ : Type*} (I : Finset ι) (J : Finset κ)
    (w : κ → ℚ) (bad : ι → Prop) (inc : ι → κ → Prop)
    [DecidablePred bad] [∀ i j, Decidable (inc i j)]
    (hw : ∀ j ∈ J, 0 ≤ w j)
    (hwitness : ∀ j ∈ J, ∃ i ∈ I, bad i ∧ inc i j) :
    (∑ j ∈ J, w j) ≤ ∑ i ∈ I, (∑ j ∈ J, if bad i ∧ inc i j then w j else 0) := by
  classical
  calc
    (∑ j ∈ J, w j) ≤ ∑ j ∈ J, (∑ i ∈ I, if bad i ∧ inc i j then w j else 0) := by
      apply Finset.sum_le_sum
      intro j hj
      obtain ⟨i, hi, hbad, hinc⟩ := hwitness j hj
      have h := Finset.single_le_sum
        (f := fun k => if bad k ∧ inc k j then w j else 0)
        (fun k _ => by
          split
          · exact hw j hj
          · exact le_refl 0) hi
      simpa [hbad, hinc] using h
    _ = _ := Finset.sum_comm

/-- The robust two-verifier witness: the worst true value is at most 3/10. -/
theorem robust_two_upper (x y z : ℚ) (h : x + y ≤ 1)
    (h1 : z ≤ x / 2 + y / 10) (h2 : z ≤ x / 10 + y / 2) : z ≤ 3 / 10 := by
  linarith

theorem robust_two_attained :
    (1/2 : ℚ) * (1/10) ≤ 1/20 ∧
    (1/2 : ℚ) / 2 + (1/2 : ℚ) / 10 = 3/10 := by norm_num

end FeedbackChannel.ProofDependencyRisk
