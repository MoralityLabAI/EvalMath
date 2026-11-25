import Mathlib

/-! CFH-07: sound sparse linear evaluation and prediction-evidence elimination.
The weighted-sum theorem applies over ZMod p after the coefficient weights and
available entries have been established. It does not prove the graph formulas
or the Python-to-Lean representation correspondence. -/

namespace FeedbackChannel.CFH07

theorem sparse_sum {I R : Type*} [CommRing R]
    (s : Finset I) (truth known weight : I → R)
    (available : I → Prop) [DecidablePred available]
    (hknown : ∀ i ∈ s, available i → known i = truth i)
    (hzero : ∀ i ∈ s, ¬ available i → weight i = 0) :
    (∑ i ∈ s, weight i * (if available i then known i else 0)) =
      ∑ i ∈ s, weight i * truth i := by
  apply Finset.sum_congr rfl
  intro i hi
  by_cases ha : available i
  · simp [ha, hknown i hi ha]
  · simp [ha, hzero i hi ha]

def restrict {H V : Type*} (S : Set H) (prediction : H → Option V)
    (reply : V) : Set H :=
  {h | h ∈ S ∧ (prediction h = none ∨ prediction h = some reply)}

theorem restrict_subset {H V : Type*} (S : Set H)
    (prediction : H → Option V) (reply : V) :
    restrict S prediction reply ⊆ S := by
  intro h hh
  exact hh.1

theorem restrict_retains {H V : Type*} (S : Set H)
    (prediction : H → Option V) (reply : V) (hidden : H)
    (hS : hidden ∈ S)
    (hsound : ∀ v, prediction hidden = some v → v = reply) :
    hidden ∈ restrict S prediction reply := by
  cases he : prediction hidden with
  | none => exact ⟨hS, Or.inl he⟩
  | some v =>
    exact ⟨hS, Or.inr (he.trans (congrArg some (hsound v he)))⟩

def replay {H V : Type*} :
    Set H → List ((H → Option V) × V) → Set H
  | S, [] => S
  | S, e :: es => replay (restrict S e.1 e.2) es

theorem replay_retains {H V : Type*} (S : Set H)
    (steps : List ((H → Option V) × V)) (hidden : H)
    (hS : hidden ∈ S)
    (hsound : ∀ e ∈ steps, ∀ v, e.1 hidden = some v → v = e.2) :
    hidden ∈ replay S steps := by
  induction steps generalizing S with
  | nil => exact hS
  | cons e es ih =>
    change hidden ∈ replay (restrict S e.1 e.2) es
    apply ih
    · exact restrict_retains S e.1 e.2 hidden hS
        (hsound e (by simp))
    · intro z hz v hv
      exact hsound z (List.mem_cons_of_mem e hz) v hv

theorem replay_subset {H V : Type*} (S : Set H)
    (steps : List ((H → Option V) × V)) :
    replay S steps ⊆ S := by
  induction steps generalizing S with
  | nil => intro h hh; exact hh
  | cons e es ih =>
    intro h hh
    change h ∈ replay (restrict S e.1 e.2) es at hh
    exact restrict_subset S e.1 e.2 (ih (restrict S e.1 e.2) hh)

theorem singleton_identification {H V : Type*} (S : Set H)
    (steps : List ((H → Option V) × V)) (hidden claimed : H)
    (hS : hidden ∈ S)
    (hsound : ∀ e ∈ steps, ∀ v, e.1 hidden = some v → v = e.2)
    (hfinal : replay S steps = {claimed}) :
    hidden = claimed := by
  have h := replay_retains S steps hidden hS hsound
  rw [hfinal] at h
  simpa using h

end FeedbackChannel.CFH07
