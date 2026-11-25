import Mathlib

/-!
# CPF-01: the adaptive certified-rejection audit

Dual-accepted null worlds carry masses in an ordered additive monoid. Each query is a
deterministic map from worlds to outcomes; some outcomes are certified rejections and remove
the world, every other outcome is diagnostic. A policy is a decision tree over outcomes that
uses at most `k` queries on every path and never repeats a query on a path. Its residual is the
false mass that survives to authorization.

* `value_le_residual`: the Bellman value `value k S U` is a lower bound for every valid policy.
* `exists_optimal`: some valid policy attains it, so the recurrence is the exact optimum.
* `residual_fixed`: a fixed schedule leaves exactly the mass that none of its queries rejects.
* `value_le_fixed`: hence the adaptive optimum is no worse than any fixed schedule.
* `witness_*`: the four-world, four-query witness of CPF-01 §2 in units of 1/100, where the
  adaptive optimum at budget two is 2 and every fixed schedule leaves at least 3.
-/

namespace FeedbackChannel.CPFAudit

open Finset

/-- Audit model: world masses, deterministic audit outcomes, and which outcomes reject. -/
structure Model (W Q O M : Type*) where
  mass : W → M
  audit : Q → W → O
  reject : O → Bool

/-- Decision trees over audit outcomes. -/
inductive Policy (Q O : Type*) where
  | stop : Policy Q O
  | query : Q → (O → Policy Q O) → Policy Q O

variable {W Q O M : Type*} [Fintype O] [DecidableEq O] [DecidableEq Q]
  [AddCommMonoid M] [LinearOrder M] [IsOrderedAddMonoid M]

namespace Model

variable (A : Model W Q O M)

def massOf (S : Finset W) : M := ∑ w ∈ S, A.mass w

/-- Surviving worlds of `S` that give outcome `o` on query `q`. -/
def cell (S : Finset W) (q : Q) (o : O) : Finset W := S.filter (fun w => A.audit q w = o)

/-- Outcomes that do not reject. -/
def pass : Finset O := univ.filter (fun o => A.reject o = false)

/-- Bellman value: least surviving mass with at most `k` further distinct queries from `U`. -/
def value : ℕ → Finset W → Finset Q → M
  | 0, S, _ => A.massOf S
  | k + 1, S, U => U.fold min (A.massOf S) (fun q => ∑ o ∈ A.pass, value k (A.cell S q o) (U.erase q))

/-- Surviving false mass when policy `p` is run from world set `S`. -/
def residual : Policy Q O → Finset W → M
  | .stop, S => A.massOf S
  | .query q next, S => ∑ o ∈ A.pass, residual (next o) (A.cell S q o)

end Model

/-- At most `k` queries on every path, each drawn from `U` and never repeated on that path. -/
def Valid : Policy Q O → ℕ → Finset Q → Prop
  | .stop, _, _ => True
  | .query q next, k, U => match k with
    | 0 => False
    | k + 1 => q ∈ U ∧ ∀ o, Valid (next o) k (U.erase q)

namespace Model

variable (A : Model W Q O M)

omit [IsOrderedAddMonoid M] in
theorem value_le_mass (k : ℕ) (S : Finset W) (U : Finset Q) : A.value k S U ≤ A.massOf S := by
  cases k with
  | zero => exact le_rfl
  | succ k => exact (Finset.fold_min_le _).mpr (Or.inl le_rfl)

/-- The Bellman value is a lower bound for every valid policy. -/
theorem value_le_residual (k : ℕ) (S : Finset W) (U : Finset Q) (p : Policy Q O)
    (hp : Valid p k U) : A.value k S U ≤ A.residual p S := by
  induction k generalizing S U p with
  | zero =>
    cases p with
    | stop => exact le_rfl
    | query q next => exact hp.elim
  | succ k ih =>
    cases p with
    | stop => exact A.value_le_mass _ _ _
    | query q next =>
      obtain ⟨hq, hn⟩ := hp
      exact ((Finset.fold_min_le _).mpr (Or.inr ⟨q, hq, le_rfl⟩)).trans
        (Finset.sum_le_sum fun o _ => ih _ _ _ (hn o))

omit [IsOrderedAddMonoid M] in
/-- Some valid policy attains the Bellman value: the recurrence is the exact optimum. -/
theorem exists_optimal (k : ℕ) (S : Finset W) (U : Finset Q) :
    ∃ p : Policy Q O, Valid p k U ∧ A.residual p S = A.value k S U := by
  induction k generalizing S U with
  | zero => exact ⟨.stop, trivial, rfl⟩
  | succ k ih =>
    choose P hP using ih
    have h := (Finset.fold_min_le (s := U) (b := A.massOf S)
      (f := fun q => ∑ o ∈ A.pass, A.value k (A.cell S q o) (U.erase q))
      (c := A.value (k + 1) S U)).mp le_rfl
    rcases h with h | ⟨q, hq, h⟩
    · exact ⟨.stop, trivial, le_antisymm h (A.value_le_mass _ _ _)⟩
    · refine ⟨.query q (fun o => P (A.cell S q o) (U.erase q)), ⟨hq, fun o => (hP _ _).1⟩, ?_⟩
      have hres : A.residual (.query q (fun o => P (A.cell S q o) (U.erase q))) S =
          ∑ o ∈ A.pass, A.value k (A.cell S q o) (U.erase q) :=
        Finset.sum_congr rfl fun o _ => (hP _ _).2
      rw [hres]
      exact le_antisymm h ((Finset.fold_min_le _).mpr (Or.inr ⟨q, hq, le_rfl⟩))

/-- A fixed schedule: the same query sequence whatever is observed. -/
def fixedPolicy : List Q → Policy Q O
  | [] => .stop
  | q :: qs => .query q (fun _ => fixedPolicy qs)

/-- World `w` is rejected by none of the queries `qs`. -/
abbrev survives (qs : List Q) (w : W) : Prop := ∀ q ∈ qs, A.reject (A.audit q w) = false

omit [DecidableEq Q] [LinearOrder M] [IsOrderedAddMonoid M] in
/-- A fixed schedule leaves exactly the mass that none of its queries rejects. -/
theorem residual_fixed (qs : List Q) (S : Finset W) :
    A.residual (fixedPolicy qs) S = A.massOf (S.filter (A.survives qs)) := by
  induction qs generalizing S with
  | nil =>
    show A.massOf S = _
    rw [Finset.filter_true_of_mem (fun w _ q hq => by simp at hq)]
  | cons q qs ih =>
    show ∑ o ∈ A.pass, A.residual (fixedPolicy qs) (A.cell S q o) = _
    simp only [ih]
    have hfib : ∀ o ∈ A.pass, (A.cell S q o).filter (A.survives qs) =
        (S.filter (A.survives (q :: qs))).filter (fun w => A.audit q w = o) := by
      intro o ho
      have ho' : A.reject o = false := by simpa [pass] using ho
      ext w
      simp only [cell, mem_filter, survives, List.mem_cons, forall_eq_or_imp]
      constructor
      · rintro ⟨⟨hw, rfl⟩, hs⟩
        exact ⟨⟨hw, ho', hs⟩, rfl⟩
      · rintro ⟨⟨hw, -, hs⟩, rfl⟩
        exact ⟨⟨hw, rfl⟩, hs⟩
    rw [Finset.sum_congr rfl fun o ho => congrArg A.massOf (hfib o ho)]
    unfold massOf
    exact Finset.sum_fiberwise_of_maps_to (fun w hw => by
      simp only [mem_filter, survives, List.mem_cons, forall_eq_or_imp] at hw
      simpa [pass] using hw.2.1) _

omit [Fintype O] [DecidableEq O] in
theorem valid_fixed (qs : List Q) (hnd : qs.Nodup) (k : ℕ) (U : Finset Q)
    (hU : ∀ q ∈ qs, q ∈ U) (hk : qs.length ≤ k) : Valid (fixedPolicy (O := O) qs) k U := by
  induction qs generalizing k U with
  | nil => trivial
  | cons q qs ih =>
    obtain ⟨k, rfl⟩ : ∃ k', k = k' + 1 := ⟨k - 1, by simp at hk; omega⟩
    refine ⟨hU q (by simp), fun _ => ih (List.nodup_cons.mp hnd).2 k _ (fun q' hq' => ?_)
      (by simpa using hk)⟩
    have hne : q' ≠ q := fun h => (List.nodup_cons.mp hnd).1 (h ▸ hq')
    exact Finset.mem_erase.mpr ⟨hne, hU q' (by simp [hq'])⟩

/-- The adaptive optimum is no worse than any fixed schedule of at most `k` distinct queries. -/
theorem value_le_fixed (k : ℕ) (S : Finset W) (U : Finset Q) (qs : List Q) (hnd : qs.Nodup)
    (hU : ∀ q ∈ qs, q ∈ U) (hk : qs.length ≤ k) :
    A.value k S U ≤ A.massOf (S.filter (A.survives qs)) := by
  rw [← A.residual_fixed qs S]
  exact A.value_le_residual k S U _ (valid_fixed qs hnd k U hU hk)

end Model

/-! ## The CPF-01 witness, masses in units of 1/100 -/

/-- Worlds 0, 1, 2 are detectable classes of mass 1, world 3 is invisible with mass 2.
Query 0 is a diagnostic that reports the class and never rejects; query `j + 1` rejects exactly
world `j`. Outcome 4 is the certified rejection. -/
def witness : Model (Fin 4) (Fin 4) (Fin 5) ℕ where
  mass w := if w = 3 then 2 else 1
  audit q w := if q = 0 then w.castSucc else if w.val + 1 = q.val then Fin.last 4 else 0
  reject o := o == Fin.last 4

/-- Budget two, adaptive: the diagnostic then the indicated test leaves only the invisible class. -/
theorem witness_adaptive : witness.value 2 univ univ = 2 := by decide

/-- Every fixed schedule of at most two distinct queries leaves at least 3, and 3 is attained. -/
theorem witness_fixed :
    3 ≤ witness.massOf (univ.filter (witness.survives [])) ∧
    (∀ q, 3 ≤ witness.massOf (univ.filter (witness.survives [q]))) ∧
    (∀ q₁ q₂, q₁ ≠ q₂ → 3 ≤ witness.massOf (univ.filter (witness.survives [q₁, q₂]))) ∧
    witness.massOf (univ.filter (witness.survives [1, 2])) = 3 := by decide

/-- The invisible class is a lower bound for every valid policy at budget two. -/
theorem witness_lower (p : Policy (Fin 4) (Fin 5)) (hp : Valid p 2 univ) :
    2 ≤ witness.residual p univ :=
  witness_adaptive ▸ witness.value_le_residual 2 univ univ p hp

end FeedbackChannel.CPFAudit
