import Mathlib
import FeedbackChannel.CPF02.OpenAIComparatorDefs
import FeedbackChannel.CPF02.AnthropicStatement

namespace FeedbackChannel.CPF02

open MvPolynomial
open scoped Classical
universe u

/-- Independently specified exact circuit: natural-number indexed arithmetic gates;
    scalars and indeterminates are free, earlier results may be reused. -/
def Available {F V : Type*} [Field F] (l : ℕ → MvPolynomial V F)
    (k : ℕ) (x : MvPolynomial V F) : Prop :=
  (∃ j : V, X j = x) ∨ (∃ a : F, C a = x) ∨ ∃ j < k, l j = x

def Computes {F V : Type*} [Field F] (p : MvPolynomial V F) (s : ℕ) : Prop :=
  ∃ l : ℕ → MvPolynomial V F, Available l s p ∧ ∀ i < s,
    ∃ a b, Available l i a ∧ Available l i b ∧
      (l i = a + b ∨ l i = a - b ∨ l i = a * b)

/-- Laurent-series approximation, with no claim here about geometric closure. -/
def Approximates {F : Type u} {V : Type} [Field F] (f : MvPolynomial V F) (s : ℕ) : Prop :=
  ∃ q : MvPolynomial V (LaurentSeries F), Computes q s ∧
    ∀ (d : V →₀ ℕ) (i : ℤ), i ≤ 0 → (q.coeff d).coeff i = if i = 0 then f.coeff d else 0

def PolyBounded (s : ℕ → ℕ) : Prop := ∃ A d N : ℕ, ∀ n ≥ N, s n ≤ A * n ^ d

abbrev Family (F : Type u) [Field F] (V : ℕ → Type) := (n : ℕ) → MvPolynomial (V n) F

def PFamily {F : Type u} [Field F] {V : ℕ → Type} [∀ n, Fintype (V n)]
    (f : Family F V) : Prop :=
  PolyBounded (fun n => Fintype.card (V n)) ∧ PolyBounded (fun n => (f n).totalDegree)

def VP {F : Type u} [Field F] {V : ℕ → Type} [∀ n, Fintype (V n)]
    (f : Family F V) : Prop :=
  PFamily f ∧ ∃ s : ℕ → ℕ, PolyBounded s ∧ ∀ n, Computes (f n) (s n)

def VPBar {F : Type u} [Field F] {V : ℕ → Type} [∀ n, Fintype (V n)]
    (f : Family F V) : Prop :=
  PFamily f ∧ ∃ s : ℕ → ℕ, PolyBounded s ∧ ∀ n, Approximates (f n) (s n)

def VNP {F : Type u} [Field F] {V : ℕ → Type} [∀ n, Fintype (V n)]
    (f : Family F V) : Prop :=
  PFamily f ∧ ∃ (r : ℕ → ℕ) (g : Family F (fun n => V n ⊕ Fin (r n))),
    PolyBounded r ∧ VP g ∧ ∀ n,
      f n = ∑ e : Fin (r n) → Bool, MvPolynomial.eval₂Hom MvPolynomial.C
        (Sum.elim MvPolynomial.X (fun j => MvPolynomial.C (if e j then 1 else 0))) (g n)

private def FinAvailable {F V : Type*} [Field F] {s : ℕ}
    (v : Fin s → MvPolynomial V F) (k : ℕ) (x : MvPolynomial V F) : Prop :=
  (∃ j : V, X j = x) ∨ (∃ a : F, C a = x) ∨ ∃ j : Fin s, j.val < k ∧ v j = x

private theorem available_iff {F V : Type*} [Field F] {s : ℕ}
    (l : ℕ → MvPolynomial V F) (v : Fin s → MvPolynomial V F)
    (agree : ∀ j : Fin s, l j.val = v j) (k : ℕ) (x : MvPolynomial V F) (hk : k ≤ s) :
    FinAvailable v k x ↔ Available l k x := by
  constructor
  · rintro (h | h | ⟨j, hj, hx⟩)
    · exact Or.inl h
    · exact Or.inr (Or.inl h)
    · exact Or.inr (Or.inr ⟨j.val, hj, (agree j).trans hx⟩)
  · rintro (h | h | ⟨j, hj, hx⟩)
    · exact Or.inl h
    · exact Or.inr (Or.inl h)
    · let i : Fin s := ⟨j, lt_of_lt_of_le hj hk⟩
      exact Or.inr (Or.inr ⟨i, hj, (agree i).symm.trans hx⟩)

/-- Actual pinned comparator definition, with only the admitted endpoint removed. -/
theorem openai_exact_iff {F V : Type*} [Field F] (p : MvPolynomial V F) (s : ℕ) :
    OAI.Computability.VPVNP.Valiant.Project.Computes s p ↔ Computes p s := by
  change (∃ v : Fin s → MvPolynomial V F, FinAvailable v s p ∧ ∀ i : Fin s,
    ∃ a b, FinAvailable v i.val a ∧ FinAvailable v i.val b ∧
      (v i = a + b ∨ v i = a - b ∨ v i = a * b)) ↔ Computes p s
  constructor
  · rintro ⟨v, hout, hg⟩
    let l : ℕ → MvPolynomial V F := fun k => if h : k < s then v ⟨k,h⟩ else 0
    have agree (j : Fin s) : l j.val = v j := by simp [l, j.isLt]
    refine ⟨l, (available_iff l v agree s p le_rfl).mp hout, ?_⟩
    intro i hi
    let j : Fin s := ⟨i, hi⟩
    obtain ⟨a,b,ha,hb,hop⟩ := hg j
    refine ⟨a,b,(available_iff l v agree i a hi.le).mp ha,
      (available_iff l v agree i b hi.le).mp hb, ?_⟩
    change l j.val = a + b ∨ l j.val = a - b ∨ l j.val = a * b
    rw [agree j]
    exact hop
  · rintro ⟨l, hout, hg⟩
    let v : Fin s → MvPolynomial V F := fun j => l j.val
    have agree (j : Fin s) : l j.val = v j := rfl
    refine ⟨v, (available_iff l v agree s p le_rfl).mpr hout, ?_⟩
    intro j
    obtain ⟨a,b,ha,hb,hop⟩ := hg j.val j.isLt
    exact ⟨a,b,(available_iff l v agree j.val a j.isLt.le).mpr ha,
      (available_iff l v agree j.val b j.isLt.le).mpr hb, hop⟩

/-- Charging leaves can only increase cost. A charged leaf becomes a copy via +0. -/
theorem anthropic_exact_to_canonical {F : Type u} {V : Type} [Field F]
    (p : MvPolynomial V F) (s : ℕ) (h : Statement.Computes p s) : Computes p s := by
  obtain ⟨l, hg, k, hk, hout⟩ := h
  refine ⟨l, Or.inr (Or.inr ⟨k,hk,hout⟩), ?_⟩
  intro i hi
  have zeroAvail : Available l i 0 := Or.inr (Or.inl ⟨0, by simp⟩)
  rcases hg i hi with ⟨j,hj⟩ | ⟨c,hc⟩ | ⟨j,hj,k,hk,hadd⟩ | ⟨j,hj,k,hk,hmul⟩
  · exact ⟨l i,0,Or.inl ⟨j,hj.symm⟩,zeroAvail,Or.inl (by simp)⟩
  · exact ⟨l i,0,Or.inr (Or.inl ⟨c,hc.symm⟩),zeroAvail,Or.inl (by simp)⟩
  · exact ⟨l j,l k,Or.inr (Or.inr ⟨j,hj,rfl⟩),Or.inr (Or.inr ⟨k,hk,rfl⟩),Or.inl hadd⟩
  · exact ⟨l j,l k,Or.inr (Or.inr ⟨j,hj,rfl⟩),Or.inr (Or.inr ⟨k,hk,rfl⟩),Or.inr (Or.inr hmul)⟩

theorem anthropic_approx_to_canonical {F : Type u} {V : Type} [Field F]
    (p : MvPolynomial V F) (s : ℕ) (h : Statement.Approximates p s) : Approximates p s := by
  obtain ⟨q,hq,hcoeff⟩ := h
  exact ⟨q,anthropic_exact_to_canonical q s hq,hcoeff⟩

theorem lower_transfer {F : Type u} {V : Type} [Field F]
    (p : MvPolynomial V F) (B : ℕ) (h : ∀ s, Computes p s → B < s) :
    ∀ s, Statement.Computes p s → B < s := by
  intro s hs
  exact h s (anthropic_exact_to_canonical p s hs)

end FeedbackChannel.CPF02
