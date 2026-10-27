/-!
Tiny independently checkable Lean examples for theorem-statement fidelity.
These are semantic countermodels; they do not import or validate OpenAI's proof.
Run in EvalMath/lean with: lake env lean ../research/theorem_fidelity/ContractMutations.lean
-/
example : (∃ x : Fin 2, x = 0) := by decide
example : ¬ (∀ x : Fin 2, x = 0) := by decide
example : (2 ^ 2 : Nat) ≠ 2 ^ 3 := by decide
example : (∀ x : Bool, x = true ∨ x = false) := by decide
example : ¬ (∀ x : Bool, x = true) := by decide

-- A weakened theorem can compile despite omitting the intended contract.
theorem tfaf_weak_existential : ∃ x : Fin 2, x = 0 := by decide
theorem tfaf_non_equivalence :
    (∃ x : Fin 2, x = 0) ∧ ¬ (∀ x : Fin 2, x = 0) := by decide
