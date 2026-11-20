import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Ring

/-!
# TrainingParanoia: exact feedback factorization and sequential bounds

RHT-27 uses a fixed, externally declared feedback map. Its interventional
kernel is constant on each feedback fibre precisely when it factors through
the attained feedback image. The codomain below is arbitrary, so it may be
a probability kernel without changing the statement.

RHT-28 uses a chronological list of pairs `(contraction, fresh discrepancy)`.
The algebra below includes the initial discrepancy and every subsequent
injection. It supports the note's Markov-kernel proof; it does not formalize
total variation, Dobrushin contraction, or the licensing of a physical state.
-/

namespace FeedbackChannel.TrainingParanoia

universe u v w x y

/-- Equal permitted feedback yields equal outcomes at every declared state. -/
def FibreConstant {Transcript : Type u} {Feedback : Type v}
    {State : Type w} {Outcome : Type x}
    (phi : Transcript → Feedback) (kernel : Transcript → State → Outcome) : Prop :=
  ∀ left right, phi left = phi right → ∀ state, kernel left state = kernel right state

/-- Only feedback values attained by a transcript belong to this interface. -/
def FeedbackImage {Transcript : Type u} {Feedback : Type v}
    (phi : Transcript → Feedback) := {value : Feedback // ∃ input, phi input = value}

/-- Exact noninterference iff the intervened kernel factors through the
permitted feedback image. Empty transcript and state types are allowed. -/
theorem fibreConstant_iff_factors {Transcript : Type u} {Feedback : Type v}
    {State : Type w} {Outcome : Type x}
    (phi : Transcript → Feedback) (kernel : Transcript → State → Outcome) :
    FibreConstant phi kernel ↔
      ∃ permitted : FeedbackImage phi → State → Outcome,
        ∀ input state,
          kernel input state = permitted ⟨phi input, ⟨input, rfl⟩⟩ state := by
  classical
  constructor
  · intro h
    refine ⟨fun value => kernel (Classical.choose value.property), ?_⟩
    intro input state
    exact h input (Classical.choose (show ∃ other, phi other = phi input from ⟨input, rfl⟩))
      (Classical.choose_spec (show ∃ other, phi other = phi input from ⟨input, rfl⟩)).symm
      state
  · rintro ⟨permitted, h⟩ left right heq state
    have hvalue : (⟨phi left, ⟨left, rfl⟩⟩ : FeedbackImage phi) =
        ⟨phi right, ⟨right, rfl⟩⟩ := Subtype.ext heq
    rw [h left state, h right state, hvalue]

/-- A common downstream map preserves exact noninterference. -/
theorem fibreConstant_postprocess {Transcript : Type u} {Feedback : Type v}
    {State : Type w} {Outcome : Type x} {Downstream : Type y}
    {phi : Transcript → Feedback} {kernel : Transcript → State → Outcome}
    (h : FibreConstant phi kernel) (postprocess : Outcome → Downstream) :
    FibreConstant phi (fun input state => postprocess (kernel input state)) := by
  intro left right heq state
  exact congrArg postprocess (h left right heq state)

/-- Disclosing the whole transcript makes fibre noninterference vacuous. -/
theorem identity_feedback_vacuous {Transcript : Type u} {State : Type w}
    {Outcome : Type x} (kernel : Transcript → State → Outcome) :
    FibreConstant (fun input : Transcript => input) kernel := by
  intro left right heq state
  exact congrArg (fun input => kernel input state) heq

/-- Two-element fibres can also admit a full behavioral change through the
permitted channel. Noninterference alone supplies no safety property. -/
theorem unsafe_permitted_feedback :
    FibreConstant (fun input : Bool × Bool => input.1)
        (fun input (_ : Unit) => input.1) ∧
      (fun input : Bool × Bool => input.1) (false, false) = false ∧
      (fun input : Bool × Bool => input.1) (true, false) = true := by
  refine ⟨?_, rfl, rfl⟩
  intro left right heq state
  exact heq

/-- Chronological recursion: the head step acts before the remaining steps. -/
def budget : List (ℝ × ℝ) → ℝ → ℝ
  | [], initial => initial
  | (delta, epsilon) :: later, initial => budget later (delta * initial + epsilon)

/-- Product of all contraction factors. -/
def gain : List (ℝ × ℝ) → ℝ
  | [] => 1
  | (delta, _) :: later => delta * gain later

/-- Each new discrepancy is multiplied by all later contraction factors. -/
def injected : List (ℝ × ℝ) → ℝ
  | [] => 0
  | (_, epsilon) :: later => epsilon * gain later + injected later

/-- Unrolled sequential bound, including the initial discrepancy. -/
theorem budget_eq_weighted (steps : List (ℝ × ℝ)) (initial : ℝ) :
    budget steps initial = initial * gain steps + injected steps := by
  induction steps generalizing initial with
  | nil => simp [budget, gain, injected]
  | cons step later ih =>
      rcases step with ⟨delta, epsilon⟩
      rw [budget, ih]
      simp only [gain, injected]
      ring

/-- A nonnegative contraction schedule preserves order in its starting bound. -/
theorem budget_mono (steps : List (ℝ × ℝ)) :
    (∀ step ∈ steps, 0 ≤ step.1) → ∀ {left right : ℝ}, left ≤ right →
      budget steps left ≤ budget steps right := by
  induction steps with
  | nil => intro _ left right h; exact h
  | cons step later ih =>
      intro hdelta left right h
      rcases step with ⟨delta, epsilon⟩
      have hhead : 0 ≤ delta := hdelta (delta, epsilon) (by simp)
      have htail : ∀ step ∈ later, 0 ≤ step.1 := by
        intro step hmem
        exact hdelta step (by simp [hmem])
      apply ih htail
      exact add_le_add (mul_le_mul_of_nonneg_left h hhead) le_rfl

/-- Every observed step is bounded by its licensed affine recurrence. -/
inductive BoundedChain : ℝ → List (ℝ × ℝ) → ℝ → Prop
  | nil (initial : ℝ) : BoundedChain initial [] initial
  | cons {initial middle final delta epsilon : ℝ} {later : List (ℝ × ℝ)}
      (step : middle ≤ delta * initial + epsilon)
      (tail : BoundedChain middle later final) :
      BoundedChain initial ((delta, epsilon) :: later) final

/-- Induction composes local discrepancy bounds for every finite horizon. -/
theorem chain_le_budget {initial final : ℝ} {steps : List (ℝ × ℝ)}
    (chain : BoundedChain initial steps final) :
    (∀ step ∈ steps, 0 ≤ step.1) → final ≤ budget steps initial := by
  induction chain with
  | nil initial => intro _; exact le_rfl
  | @cons initial middle final delta epsilon later hstep hchain ih =>
      intro hdelta
      have htail : ∀ step ∈ later, 0 ≤ step.1 := by
        intro step hmem
        exact hdelta step (by simp [hmem])
      exact le_trans (ih htail) (budget_mono later htail hstep)

/-- The initial term and all later-weighted injections bound the final state. -/
theorem chain_le_weighted {initial final : ℝ} {steps : List (ℝ × ℝ)}
    (chain : BoundedChain initial steps final)
    (hdelta : ∀ step ∈ steps, 0 ≤ step.1) :
    final ≤ initial * gain steps + injected steps := by
  rw [← budget_eq_weighted]
  exact chain_le_budget chain hdelta

/-- If a discrepancy is at most one, its composed bound may be clipped at one. -/
theorem chain_le_clipped {initial final : ℝ} {steps : List (ℝ × ℝ)}
    (chain : BoundedChain initial steps final)
    (hdelta : ∀ step ∈ steps, 0 ≤ step.1) (hcap : final ≤ 1) :
    final ≤ min 1 (initial * gain steps + injected steps) := by
  exact le_min hcap (chain_le_weighted chain hdelta)

end FeedbackChannel.TrainingParanoia
