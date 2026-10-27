import Mathlib.Tactic

/-!
Finite, independent semantic witnesses for the theorem-fidelity benchmark.
These examples concern the meaning of statement fields and do not establish
Unique Games hardness or certify the pinned upstream proof.
-/

namespace FeedbackChannel.TheoremFidelity

/-- An existentially bad labeling exists even for a perfectly satisfiable edge. -/
theorem tf01_exists_bad_not_all_bad :
    (∃ x y : Bool, (x == y) = false) ∧
    ¬ (∀ x y : Bool, (x == y) = false) := by
  decide

/-- A universal relation cannot be the graph of a deterministic permutation. -/
theorem tf02_universal_not_function :
    ¬ (∃ f : Bool → Bool, ∀ x y : Bool, f x = y) := by
  rintro ⟨f, hf⟩
  have hfalse : f false = false := hf false false
  have htrue : f false = true := hf false true
  have contradiction : false = true := hfalse.symm.trans htrue
  cases contradiction

/-- Four distinct bipartite F2-translation edges, one inconsistent cycle. -/
def cycleSatisfied (a b c d : Bool) : Nat :=
  (if a = b then 1 else 0) +
  (if c = b then 1 else 0) +
  (if c = d then 1 else 0) +
  (if a ≠ d then 1 else 0)

/-- The cycle's exact optimum is 3/4 of four constraints. -/
theorem tf03_cycle_optimum_three :
    (∀ a b c d : Bool, cycleSatisfied a b c d ≤ 3) ∧
    (∃ a b c d : Bool, cycleSatisfied a b c d = 3) := by
  decide

def positiveClause (x : Bool) : Bool := x || x || x
def negativeClause (x : Bool) : Bool := (!x) || (!x) || (!x)

/-- Two legal three-slot clauses with repeated literals form unsatisfiable 3CNF. -/
theorem tf04_unsat_three_cnf :
    ¬ (∃ x : Bool, positiveClause x = true ∧ negativeClause x = true) := by
  decide

private theorem succ_le_pow_two (n : Nat) : n + 1 ≤ 2 ^ n := by
  induction n with
  | zero => norm_num
  | succ n ih =>
      have h : n + 2 ≤ 2 ^ n * 2 := by omega
      simpa [pow_succ] using h

/-- A size-dependent alphabet 2^n cannot have one finite uniform upper bound. -/
theorem tf05_exponential_alphabet_unbounded :
    ¬ (∃ bound : Nat, ∀ n : Nat, 2 ^ n ≤ bound) := by
  rintro ⟨bound, hb⟩
  have hg := succ_le_pow_two (bound + 1)
  have hl := hb (bound + 1)
  omega

/-- Finite illustrative witness; the asymptotic claim uses a separate argument. -/
theorem tf06_exponential_construction_example :
    2 * (10 : Nat) ^ 2 < 2 ^ 10 := by
  norm_num

end FeedbackChannel.TheoremFidelity
