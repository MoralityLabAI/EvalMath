import FeedbackChannel.RHCompactification

/-!
# RH numerator step: a relational affine update and its recurrence

This module extends the recurrence curriculum using only the existing
`RHCompactification` module and its `Init` dependencies. The operation arguments
`mul`, `add`, and `den` are arbitrary total functions on Lean's `Nat`. No
arithmetic laws or recurrence equation for `den` are assumed by the step graph
or recurrence existence theorems.

The relation follows the RH-PL-18 construction: index zero returns the old value;
at a successor index it evaluates the predecessor's denominator, multiplies the
old value by the successor index, and adds that denominator. The final theorem
specializes `den` to the previously constructed denominator and identifies the
result with the joint numerator.

These are Lean Nat/function analogues. The custom Hilbert graph encoding and its
set-theoretic proof certificates retain their separate verifier and provenance.
Every obligation belongs to the existing public recurrence training family.
-/

set_option autoImplicit false

namespace FeedbackChannel.RHNumeratorStep

open FeedbackChannel.RHCompactification

-- RHGYM-BEGIN AffineStep
/-- Relational evaluation, including the identity branch at index zero. -/
def AffineStep (mul add : Nat → Nat → Nat) (den : Nat → Nat)
    (y a b : Nat) : Prop :=
  (y = 0 ∧ b = a) ∨
    ∃ x d u : Nat, y = x + 1 ∧ d = den x ∧ u = mul y a ∧ b = add u d
-- RHGYM-END AffineStep

-- RHGYM-BEGIN affineValue
/-- The total function represented by `AffineStep`. -/
def affineValue (mul add : Nat → Nat → Nat) (den : Nat → Nat) : Nat → Nat → Nat
  | 0, a => a
  | x + 1, a => add (mul (x + 1) a) (den x)
-- RHGYM-END affineValue

-- RHGYM-BEGIN affine_step_zero_iff
theorem affine_step_zero_iff (mul add : Nat → Nat → Nat) (den : Nat → Nat)
    (a b : Nat) : AffineStep mul add den 0 a b ↔ b = a := by
  constructor
  · intro h
    rcases h with h | ⟨x, d, u, hy, hd, hu, hb⟩
    · exact h.2
    · cases hy
  · intro h
    exact Or.inl ⟨rfl, h⟩
-- RHGYM-END affine_step_zero_iff

-- RHGYM-BEGIN affine_step_succ_iff
/-- At a successor, every intermediate witness reduces to the affine update. -/
theorem affine_step_succ_iff (mul add : Nat → Nat → Nat) (den : Nat → Nat)
    (x a b : Nat) :
    AffineStep mul add den (x + 1) a b ↔ b = add (mul (x + 1) a) (den x) := by
  constructor
  · intro h
    rcases h with h | ⟨z, d, u, hy, hd, hu, hb⟩
    · cases h.1
    · have hxz : x = z := Nat.succ.inj hy
      subst z
      calc
        b = add u d := hb
        _ = add (mul (x + 1) a) (den x) := by rw [hu, hd]
  · intro h
    exact Or.inr ⟨x, den x, mul (x + 1) a, rfl, rfl, rfl, h⟩
-- RHGYM-END affine_step_succ_iff

-- RHGYM-BEGIN affine_step_iff_graph
/-- The relational and deterministic presentations have the same graph. -/
theorem affine_step_iff_graph (mul add : Nat → Nat → Nat) (den : Nat → Nat)
    (y a b : Nat) : AffineStep mul add den y a b ↔ b = affineValue mul add den y a := by
  cases y with
  | zero => exact affine_step_zero_iff mul add den a b
  | succ x => exact affine_step_succ_iff mul add den x a b
-- RHGYM-END affine_step_iff_graph

-- RHGYM-BEGIN affine_step_total
theorem affine_step_total (mul add : Nat → Nat → Nat) (den : Nat → Nat)
    (y a : Nat) : ∃ b : Nat, AffineStep mul add den y a b := by
  exact ⟨affineValue mul add den y a,
    (affine_step_iff_graph mul add den y a (affineValue mul add den y a)).mpr rfl⟩
-- RHGYM-END affine_step_total

-- RHGYM-BEGIN affine_step_functional
theorem affine_step_functional {mul add : Nat → Nat → Nat} {den : Nat → Nat}
    {y a b c : Nat} (hb : AffineStep mul add den y a b)
    (hc : AffineStep mul add den y a c) : b = c := by
  exact ((affine_step_iff_graph mul add den y a b).mp hb).trans
    ((affine_step_iff_graph mul add den y a c).mp hc).symm
-- RHGYM-END affine_step_functional

-- RHGYM-BEGIN AffineRecurrence
/-- The numerator recurrence expressed through the relational successor step. -/
def AffineRecurrence (mul add : Nat → Nat → Nat) (den : Nat → Nat)
    (seed : Nat) (f : Nat → Nat) : Prop :=
  f 0 = seed ∧ ∀ n, AffineStep mul add den (n + 1) (f n) (f (n + 1))
-- RHGYM-END AffineRecurrence

-- RHGYM-BEGIN affine_recurrence_iff
/-- Normalize the relational update to the general recursion interface. -/
theorem affine_recurrence_iff (mul add : Nat → Nat → Nat) (den : Nat → Nat)
    (seed : Nat) (f : Nat → Nat) :
    AffineRecurrence mul add den seed f ↔
      Recurrence (fun n a => add (mul (n + 1) a) (den n)) seed f := by
  constructor
  · intro hf
    refine ⟨hf.1, ?_⟩
    intro n
    exact (affine_step_succ_iff mul add den n (f n) (f (n + 1))).mp (hf.2 n)
  · intro hf
    refine ⟨hf.1, ?_⟩
    intro n
    exact (affine_step_succ_iff mul add den n (f n) (f (n + 1))).mpr (hf.2 n)
-- RHGYM-END affine_recurrence_iff

-- RHGYM-BEGIN affine_recurrence_exists_unique
/-- General recursion constructs the numerator for any supplied total denominator. -/
theorem affine_recurrence_exists_unique (mul add : Nat → Nat → Nat)
    (den : Nat → Nat) (seed : Nat) :
    ∃ f : Nat → Nat, AffineRecurrence mul add den seed f ∧
      ∀ g : Nat → Nat, AffineRecurrence mul add den seed g → g = f := by
  obtain ⟨f, hf, hunique⟩ :=
    recurrence_exists_unique (fun n a => add (mul (n + 1) a) (den n)) seed
  refine ⟨f, (affine_recurrence_iff mul add den seed f).mpr hf, ?_⟩
  intro g hg
  exact hunique g ((affine_recurrence_iff mul add den seed g).mp hg)
-- RHGYM-END affine_recurrence_exists_unique

-- RHGYM-BEGIN affine_recurrence_eq_joint_numerator
/-- Specializing the supplied denominator recovers the existing joint numerator. -/
theorem affine_recurrence_eq_joint_numerator {mul add : Nat → Nat → Nat}
    {numSeed denSeed : Nat} {f : Nat → Nat}
    (hf : AffineRecurrence mul add (denominator mul denSeed) numSeed f) :
    f = numerator mul add numSeed denSeed := by
  have hnormalized :=
    (affine_recurrence_iff mul add (denominator mul denSeed) numSeed f).mp hf
  exact recurrence_unique hnormalized ⟨rfl, numerator_succ mul add numSeed denSeed⟩
-- RHGYM-END affine_recurrence_eq_joint_numerator

end FeedbackChannel.RHNumeratorStep
