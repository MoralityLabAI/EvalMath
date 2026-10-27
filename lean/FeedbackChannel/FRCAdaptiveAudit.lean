import Mathlib.Tactic
import FeedbackChannel.Signal

/-!
# Adaptive equality-query coupling for HRC-FRC-01

The auditor uses exactly q single-index Boolean queries. Every answer before
the first trigger hit is false; its no-hit path is therefore fixed once the
auditor's independent random seed is fixed. These results concern a restricted
equality oracle and have no unrestricted FRC implications.
-/

namespace FeedbackChannel.FRC

open Finset

abbrev Auditor (n q : ℕ) := Signal.Strategy (Fin n) Bool Bool q

def cleanOracle {n : ℕ} : Fin n → Bool := fun _ => false

def triggerOracle {n : ℕ} (trigger : Fin n) : Fin n → Bool :=
  fun index => decide (index = trigger)

def noHitPath {n : ℕ} : {q : ℕ} → Auditor n q → List (Fin n)
  | _, .done _ => []
  | _, .ask index next => index :: noHitPath (next false)

theorem noHitPath_length {n : ℕ} :
    ∀ {q : ℕ} (s : Auditor n q), (noHitPath s).length = q
  | _, .done _ => rfl
  | _, .ask _ next => by
      simp [noHitPath, noHitPath_length (next false)]

theorem run_trigger_eq_clean_of_not_mem {n : ℕ} :
    ∀ {q : ℕ} (s : Auditor n q) (trigger : Fin n),
      trigger ∉ noHitPath s →
      s.run (triggerOracle trigger) = s.run (cleanOracle (n := n))
  | _, .done _, _, _ => rfl
  | _, .ask index next, trigger, hnot => by
      have hneq : index ≠ trigger := by
        intro h
        apply hnot
        simp [noHitPath, h]
      have htail : trigger ∉ noHitPath (next false) := by
        intro h
        apply hnot
        simp [noHitPath, h]
      simpa [Signal.Strategy.run, triggerOracle, cleanOracle, hneq] using
        run_trigger_eq_clean_of_not_mem (next false) trigger htail

def changedTriggers {n q : ℕ} (s : Auditor n q) : Finset (Fin n) :=
  Finset.univ.filter (fun trigger =>
    s.run (triggerOracle trigger) ≠ s.run (cleanOracle (n := n)))

theorem changedTriggers_subset_path {n q : ℕ} (s : Auditor n q) :
    changedTriggers s ⊆ (noHitPath s).toFinset := by
  intro trigger hchanged
  by_contra hnot
  have hpath : trigger ∉ noHitPath s := by simpa using hnot
  have heq := run_trigger_eq_clean_of_not_mem s trigger hpath
  have hneq : s.run (triggerOracle trigger) ≠ s.run (cleanOracle (n := n)) := by
    simpa [changedTriggers] using hchanged
  exact hneq heq

/-- A depth-q adaptive equality-query auditor changes its final Boolean
decision on at most q single-trigger oracles compared with the clean oracle. -/
theorem changedTriggers_card_le {n q : ℕ} (s : Auditor n q) :
    (changedTriggers s).card ≤ q := by
  calc
    (changedTriggers s).card ≤ (noHitPath s).toFinset.card :=
      Finset.card_le_card (changedTriggers_subset_path s)
    _ ≤ (noHitPath s).length := List.toFinset_card_le _
    _ = q := noHitPath_length s

def rejectedTriggers {n q : ℕ} (s : Auditor n q) : Finset (Fin n) :=
  Finset.univ.filter (fun trigger => s.run (triggerOracle trigger) = true)

theorem rejectedTriggers_card_le {n q : ℕ} (s : Auditor n q) :
    (rejectedTriggers s).card ≤
      (if s.run (cleanOracle (n := n)) then n else 0) + q := by
  cases hc : s.run (cleanOracle (n := n)) with
  | false =>
      have hsubset : rejectedTriggers s ⊆ changedTriggers s := by
        intro trigger h
        have hrej : s.run (triggerOracle trigger) = true := by
          simpa [rejectedTriggers] using h
        simp [changedTriggers, hc, hrej]
      have hbound := le_trans (Finset.card_le_card hsubset) (changedTriggers_card_le s)
      simpa [hc] using hbound
  | true =>
      have hbound : (rejectedTriggers s).card ≤ n := by
        calc
          (rejectedTriggers s).card ≤ (Finset.univ : Finset (Fin n)).card :=
            Finset.card_le_card (Finset.filter_subset _ _)
          _ = n := by simp
      simp only [hc, ite_true]
      omega

/-- Uniform random seed mixture. The right side charges all n triggers when
a seed rejects the benign oracle, and at most q otherwise. -/
theorem randomized_rejection_bound {n q : ℕ} {Seed : Type*} [Fintype Seed]
    (auditor : Seed → Auditor n q) :
    (∑ seed : Seed, (rejectedTriggers (auditor seed)).card) ≤
      (∑ seed : Seed,
        (if (auditor seed).run (cleanOracle (n := n)) then n else 0)) +
        q * Fintype.card Seed := by
  calc
    (∑ seed : Seed, (rejectedTriggers (auditor seed)).card) ≤
        ∑ seed : Seed,
          ((if (auditor seed).run (cleanOracle (n := n)) then n else 0) + q) := by
        apply Finset.sum_le_sum
        intro seed _
        exact rejectedTriggers_card_le (auditor seed)
    _ = _ := by simp [Finset.sum_add_distrib, mul_comm]

/-- A finite two-sided auditing floor with integer budgets for clean rejection
pairs and trigger rejection pairs. The comparison includes adaptive and
randomized strategies; seeds are independent and uniform. -/
theorem randomized_audit_floor {n q : ℕ} {Seed : Type*} [Fintype Seed]
    (auditor : Seed → Auditor n q) (cleanCap triggerFloor : ℕ)
    (hclean :
      (∑ seed : Seed,
        (if (auditor seed).run (cleanOracle (n := n)) then n else 0)) ≤ cleanCap)
    (htrigger :
      triggerFloor ≤ ∑ seed : Seed, (rejectedTriggers (auditor seed)).card) :
    triggerFloor ≤ cleanCap + q * Fintype.card Seed := by
  exact le_trans htrigger
    (le_trans (randomized_rejection_bound auditor)
      (Nat.add_le_add_right hclean (q * Fintype.card Seed)))


/-- Sharp deterministic counting lemma: a benign-rejecting seed contributes
at most n triggered rejections, while a benign-accepting seed contributes at
most q. The earlier n+q bound is a deliberately conservative relaxation. -/
theorem rejectedTriggers_card_le_sharp {n q : ℕ} (s : Auditor n q) :
    (rejectedTriggers s).card ≤
      (if s.run (cleanOracle (n := n)) then n else q) := by
  cases hc : s.run (cleanOracle (n := n)) with
  | false =>
      have hbound : (rejectedTriggers s).card ≤ q := by
        simpa [hc] using rejectedTriggers_card_le s
      simpa [hc] using hbound
  | true =>
      have hbound : (rejectedTriggers s).card ≤ n := by
        calc
          (rejectedTriggers s).card ≤ (Finset.univ : Finset (Fin n)).card :=
            Finset.card_le_card (Finset.filter_subset _ _)
          _ = n := by simp
      simpa [hc] using hbound

/-- Exact finite uniform-seed sharp coupling: a randomized auditor is
a mixture of deterministic adaptive trees with an independent random seed.
The sum on the right counts clean-rejecting seeds with weight n and all
other seeds with weight q. Probability-weighted priors remain a separate
formalization target. -/
theorem randomized_rejection_bound_sharp {n q : ℕ} {Seed : Type*} [Fintype Seed]
    (auditor : Seed → Auditor n q) :
    (∑ seed : Seed, (rejectedTriggers (auditor seed)).card) ≤
      ∑ seed : Seed,
        (if (auditor seed).run (cleanOracle (n := n)) then n else q) := by
  apply Finset.sum_le_sum
  intro seed _
  exact rejectedTriggers_card_le_sharp (auditor seed)

end FeedbackChannel.FRC
