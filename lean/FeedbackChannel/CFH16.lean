import FeedbackChannel.CFH07

/-! Abstract cooperative budget and independently verified batch transitions.
The ledger counts natural-number charges. Soundness of the external verifier
and authenticated observation are hypotheses, not proved properties of Python. -/

namespace FeedbackChannel.CFH16

structure Ledger where
  cap : Nat
  used : Nat
  charges : List Nat

def Valid (l : Ledger) : Prop := l.used ≤ l.cap ∧ l.charges.sum = l.used

def charge (l : Ledger) (k : Nat) : Option Ledger :=
  if l.used + k ≤ l.cap then
    some ⟨l.cap, l.used + k, k :: l.charges⟩
  else none

theorem charge_preserves (l l' : Ledger) (k : Nat) (hv : Valid l)
    (h : charge l k = some l') :
    Valid l' ∧ l'.cap = l.cap ∧ l'.used = l.used + k := by
  unfold charge at h
  split at h
  · rename_i hfit
    simp only [Option.some.injEq] at h
    subst l'
    refine ⟨⟨hfit, ?_⟩, rfl, rfl⟩
    simp [hv.2, Nat.add_comm]
  · simp at h

theorem charge_reject (l : Ledger) (k : Nat) (h : l.cap < l.used + k) :
    charge l k = none := by
  simp [charge, not_le.mpr h]

def Sound {K V : Type*} (truth : K → V) (cache : K → Option V) : Prop :=
  ∀ k v, cache k = some v → v = truth k

def merge {K V : Type*} (cache batch : K → Option V) : K → Option V :=
  fun k => match batch k with
    | none => cache k
    | some v => some v

theorem merge_sound {K V : Type*} (truth : K → V) (cache batch : K → Option V)
    (hc : Sound truth cache) (hb : Sound truth batch) :
    Sound truth (merge cache batch) := by
  intro k v h
  cases he : batch k with
  | none => exact hc k v (by simpa [merge, he] using h)
  | some w => exact hb k v (by simpa [he, merge] using h)

theorem merge_preserves {K V : Type*} (truth : K → V) (cache batch : K → Option V)
    (hc : Sound truth cache) (hb : Sound truth batch) (k : K) (v : V)
    (h : cache k = some v) : merge cache batch k = some v := by
  cases he : batch k with
  | none => simpa [merge, he] using h
  | some w =>
    have hw := hb k w he
    have hv := hc k v h
    simp [merge, he, hw, hv]

structure Snapshot (K V H : Type*) where
  ledger : Ledger
  cache : K → Option V
  hypotheses : Set H
  observations : Nat

/-- Only independently verified batches reach this abstract commit. -/
def checkpoint {K V H : Type*} (s : Snapshot K V H) (l' : Ledger)
    (batch : K → Option V) : Snapshot K V H :=
  { s with ledger := l', cache := merge s.cache batch }

theorem checkpoint_safe {K V H : Type*} (s : Snapshot K V H) (l' : Ledger)
    (batch : K → Option V) (truth : K → V) (cost : Nat)
    (hv : Valid s.ledger) (hcharge : charge s.ledger cost = some l')
    (hc : Sound truth s.cache) (hb : Sound truth batch) :
    Valid (checkpoint s l' batch).ledger ∧
    Sound truth (checkpoint s l' batch).cache ∧
    (checkpoint s l' batch).hypotheses = s.hypotheses ∧
    (checkpoint s l' batch).observations = s.observations ∧
    (checkpoint s l' batch).ledger.used = s.ledger.used + cost := by
  have hl := charge_preserves s.ledger l' cost hv hcharge
  exact ⟨hl.1, merge_sound truth s.cache batch hc hb, rfl, rfl, hl.2.2⟩

/-- Exhausted work may have charged fuel, but cannot publish an unchecked batch. -/
def interrupt {K V H : Type*} (s : Snapshot K V H) (l' : Ledger) : Snapshot K V H :=
  { s with ledger := l' }

theorem interrupt_safe {K V H : Type*} (s : Snapshot K V H) (l' : Ledger)
    (cost : Nat) (hv : Valid s.ledger) (hcharge : charge s.ledger cost = some l') :
    Valid (interrupt s l').ledger ∧
    (interrupt s l').cache = s.cache ∧
    (interrupt s l').hypotheses = s.hypotheses ∧
    (interrupt s l').observations = s.observations ∧
    (interrupt s l').ledger.used = s.ledger.used + cost := by
  have hl := charge_preserves s.ledger l' cost hv hcharge
  exact ⟨hl.1, rfl, rfl, rfl, hl.2.2⟩

/-- Observation commits only after a separate authenticated reply check. -/
def observe {K V H R : Type*} (s : Snapshot K V H) (prediction : H → Option R)
    (reply : R) : Snapshot K V H :=
  { s with hypotheses := CFH07.restrict s.hypotheses prediction reply,
           observations := s.observations + 1 }

theorem observation_safe {K V H R : Type*} (s : Snapshot K V H)
    (prediction : H → Option R) (reply : R) (hidden : H) (qcap : Nat)
    (hs : hidden ∈ s.hypotheses)
    (ha : ∀ v, prediction hidden = some v → v = reply)
    (hq : s.observations < qcap) :
    hidden ∈ (observe s prediction reply).hypotheses ∧
    (observe s prediction reply).hypotheses ⊆ s.hypotheses ∧
    (observe s prediction reply).observations ≤ qcap ∧
    (observe s prediction reply).cache = s.cache ∧
    (observe s prediction reply).ledger = s.ledger := by
  exact ⟨CFH07.restrict_retains s.hypotheses prediction reply hidden hs ha,
    CFH07.restrict_subset s.hypotheses prediction reply,
    Nat.succ_le_of_lt hq, rfl, rfl⟩

end FeedbackChannel.CFH16
