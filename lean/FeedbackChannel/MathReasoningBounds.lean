import Mathlib

/-! Candidate supporting lemmas for EM-MPT-01--07.
The full generating-function and stochastic-order theorem is not formalized here. -/

namespace FeedbackChannel.MathReasoningBounds

theorem oneSlackExchange (a b c e : ℚ) (h : a * b = c * e) :
    c * e * (3 - c - e) - a * b * (3 - a - b) =
      a * b * (a + b - c - e) := by
  rw [← h]
  ring

theorem oneSlackMonotone (a b c e : ℚ) (h : a * b = c * e)
    (hp : 0 ≤ a * b) (hs : c + e ≤ a + b) :
    a * b * (3 - a - b) ≤ c * e * (3 - c - e) := by
  have hgap : 0 ≤ a + b - c - e := by linarith
  have hh : 0 ≤ c * e * (3 - c - e) - a * b * (3 - a - b) := by
    rw [oneSlackExchange a b c e h]
    exact mul_nonneg hp hgap
  exact sub_nonneg.mp hh

def pairDenom (a b t : ℚ) : ℚ :=
  (1 - (1 - a) * t) * (1 - (1 - b) * t)

theorem pairDenomDelta (a b c e t : ℚ) (h : a * b = c * e) :
    pairDenom c e t - pairDenom a b t =
      (c + e - a - b) * t * (1 - t) := by
  unfold pairDenom
  calc
    _ = (c + e - a - b) * t * (1 - t) + (c * e - a * b) * t ^ 2 := by ring
    _ = _ := by rw [← h]; ring

theorem equalLossWitness :
    (1 / 2 : ℚ) * (1 / 2) = 1 * (1 / 4) ∧
    (1 / 2 : ℚ) * (1 / 2) * (3 - 1 / 2 - 1 / 2) = 1 / 2 ∧
    (1 : ℚ) * (1 / 4) * (3 - 1 - 1 / 4) = 7 / 16 := by
  norm_num

theorem affineEndpoints (l p u x y : ℚ) (hl : l ≤ p) (hu : p ≤ u) :
    min (l*x+(1-l)*y) (u*x+(1-u)*y) ≤ p*x+(1-p)*y ∧
    p*x+(1-p)*y ≤ max (l*x+(1-l)*y) (u*x+(1-u)*y) := by
  by_cases h : y ≤ x
  · have h1 := mul_nonneg (sub_nonneg.mpr hl) (sub_nonneg.mpr h)
    have h2 := mul_nonneg (sub_nonneg.mpr hu) (sub_nonneg.mpr h)
    have ha : l*x+(1-l)*y ≤ p*x+(1-p)*y := by nlinarith only [h1]
    have hb : p*x+(1-p)*y ≤ u*x+(1-u)*y := by nlinarith only [h2]
    exact ⟨le_trans (min_le_left _ _) ha, le_trans hb (le_max_right _ _)⟩
  · have hx : x ≤ y := le_of_not_ge h
    have h1 := mul_nonneg (sub_nonneg.mpr hl) (sub_nonneg.mpr hx)
    have h2 := mul_nonneg (sub_nonneg.mpr hu) (sub_nonneg.mpr hx)
    have ha : u*x+(1-u)*y ≤ p*x+(1-p)*y := by nlinarith only [h2]
    have hb : p*x+(1-p)*y ≤ l*x+(1-l)*y := by nlinarith only [h1]
    exact ⟨le_trans (min_le_right _ _) ha, le_trans hb (le_max_left _ _)⟩

inductive AnnotatedPolicy where
  | leaf (v reward : ℚ)
  | branch (p v : ℚ) (yes no : AnnotatedPolicy)

def potential : AnnotatedPolicy → ℚ
  | .leaf v _ => v
  | .branch _ v _ _ => v

def closure : AnnotatedPolicy → ℚ
  | .leaf _ r => r
  | .branch p _ y n => p * closure y + (1-p) * closure n

def totalGap : AnnotatedPolicy → ℚ
  | .leaf v r => v - r
  | .branch p v y n =>
    v - (p * potential y + (1-p) * potential n) +
      p * totalGap y + (1-p) * totalGap n

theorem gapTelescopes (tree : AnnotatedPolicy) :
    totalGap tree = potential tree - closure tree := by
  induction tree with
  | leaf v r => rfl
  | branch p v y n ihy ihn =>
    simp only [totalGap, potential, closure]
    rw [ihy, ihn]
    ring

end FeedbackChannel.MathReasoningBounds
