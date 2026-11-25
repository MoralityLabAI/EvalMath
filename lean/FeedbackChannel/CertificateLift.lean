import Mathlib

/-! ZKL-20: bulk de Bruijn weakening and raw context lookup.
The statements concern unbounded natural syntax, not the R1CS or its parser. -/
namespace FeedbackChannel.CertificateLift

inductive Expr where
  | sort : Nat → Expr
  | var : Nat → Expr
  | pi : Expr → Expr → Expr
  | lam : Expr → Expr → Expr
  | app : Expr → Expr → Expr
  deriving DecidableEq, Repr

def lift (k d : Nat) : Expr → Expr
  | .sort u => .sort u
  | .var i => if k ≤ i then .var (i + d) else .var i
  | .pi A B => .pi (lift k d A) (lift (k + 1) d B)
  | .lam A t => .lam (lift k d A) (lift (k + 1) d t)
  | .app f x => .app (lift k d f) (lift k d x)

/-- Bulk shifts compose at a fixed cutoff, including under dependent binders. -/
theorem lift_add (t : Expr) (k a b : Nat) :
    lift k b (lift k a t) = lift k (a + b) t := by
  induction t generalizing k with
  | sort u => rfl
  | var i =>
    by_cases h : k ≤ i
    · have h' : k ≤ i + a := by omega
      simp [lift, h, h', Nat.add_assoc]
    · simp [lift, h]
  | pi A B ihA ihB =>
    simp only [lift, ihA, ihB]
  | lam A t ihA iht =>
    simp only [lift, ihA, iht]
  | app f x ihf ihx =>
    simp only [lift, ihf, ihx]

def rawLookup : List Expr → Nat → Option Expr
  | [], _ => none
  | A :: _, 0 => some A
  | _ :: Γ, i + 1 => rawLookup Γ i

def stepLookup : List Expr → Nat → Option Expr
  | [], _ => none
  | A :: _, 0 => some (lift 0 1 A)
  | _ :: Γ, i + 1 => (stepLookup Γ i).map (lift 0 1)

/-- Retrieving the stored binder and shifting once by i+1 equals recursively
    weakening at every context extension. The equality includes missing binders. -/
theorem lookup_bulk (Γ : List Expr) (i : Nat) :
    stepLookup Γ i = (rawLookup Γ i).map (lift 0 (i + 1)) := by
  induction Γ generalizing i with
  | nil => cases i <;> rfl
  | cons A Γ ih =>
    cases i with
    | zero => rfl
    | succ i =>
      simp only [stepLookup, rawLookup, ih]
      cases rawLookup Γ i with
      | none => rfl
      | some t =>
        simp [lift_add, Nat.succ_eq_add_one]

end FeedbackChannel.CertificateLift
