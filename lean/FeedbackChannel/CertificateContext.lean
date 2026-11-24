import Mathlib

/- CCF-01 draft; kernel build and axiom audit pending. -/
namespace CertificateContext

variable {X C K : Type}

def Conflict (feasible : C → X → Prop) (auth : C → X → Bool)
    (x y : X) : Prop :=
  ∃ c, feasible c x ∧ feasible c y ∧ auth c x ≠ auth c y

def Separates (feasible : C → X → Prop) (auth : C → X → Bool)
    (encode : X → K) : Prop :=
  ∀ x y, Conflict feasible auth x y → encode x ≠ encode y

def ExactCode (feasible : C → X → Prop) (auth : C → X → Bool)
    (encode : X → K) : Prop :=
  ∃ decode : C → K → Bool,
    ∀ c x, feasible c x → decode c (encode x) = auth c x

theorem exact_iff_separates (feasible : C → X → Prop)
    (auth : C → X → Bool) (encode : X → K) :
    ExactCode feasible auth encode ↔ Separates feasible auth encode := by
  constructor
  · rintro ⟨d, hd⟩ x y ⟨c, hx, hy, hne⟩ he
    apply hne
    rw [← hd c x hx, ← hd c y hy, he]
  · intro h
    classical
    let d : C → K → Bool := fun c k =>
      if ∃ x, feasible c x ∧ encode x = k ∧ auth c x = true
      then true else false
    refine ⟨d, ?_⟩
    intro c x hx
    cases hax : auth c x with
    | false =>
      have hn : ¬ ∃ y, feasible c y ∧ encode y = encode x ∧ auth c y = true := by
        rintro ⟨y, hy, he, hay⟩
        have hne : auth c x ≠ auth c y := by simp [hax, hay]
        exact h x y ⟨c, hx, hy, hne⟩ he.symm
      simp [d, hn, hax]
    | true =>
      have hy : ∃ y, feasible c y ∧ encode y = encode x ∧ auth c y = true :=
        ⟨x, hx, rfl, hax⟩
      simp [d, hy, hax]

end CertificateContext

#print axioms CertificateContext.exact_iff_separates
