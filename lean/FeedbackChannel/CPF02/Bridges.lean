import Mathlib
import FeedbackChannel.CPF02.Canonical

/-!
# CPF-02 bridges: reverse compiler, bound normalization, class transports

* `canonical_to_anthropic`: every free (OpenAI/canonical) gate table of size `s` compiles to a
  charged (Anthropic) table of size `4 * s + 2` computing the same formal polynomial, over every
  field. Together with `anthropic_exact_to_canonical` this gives `C_O ≤ C_A ≤ 4 C_O + 2`.
* `polyBounded_iff_allIndex`: the eventual bound `A * n ^ d` and Anthropic's all-index
  `n ^ a + a` define the same class of size functions.
* `vp_iff_anthropic`: canonical (equivalently OpenAI) VP and Anthropic VP coincide.
* `openai_vnp_iff_canonical`: OpenAI's VNP with arbitrary finite witness types equals the
  canonical `Fin (r n)` form.
* `vp_subset_vnp`, `canonical_vnp_to_anthropic`: VP ⊆ VNP, and canonical VNP ⊆ Anthropic VNP.

The converse `Anthropic VNP → canonical VNP` needs a total-degree bound for Boolean partial
evaluation and is not proved here. Nothing in this file concerns geometric (Zariski) border
complexity; `Approximates` is the Laurent-series notion only.
-/

namespace FeedbackChannel.CPF02

open MvPolynomial
open scoped Classical
universe u

/-! ## Padding -/

theorem computes_mono {F V : Type*} [Field F] {p : MvPolynomial V F} {s t : ℕ}
    (h : Computes p s) (hst : s ≤ t) : Computes p t := by
  obtain ⟨l, hout, hg⟩ := h
  let l' : ℕ → MvPolynomial V F := fun k => if k < s then l k else 0
  have tr : ∀ i ≤ s, ∀ x, Available l i x → Available l' i x := by
    rintro i hi x (h | h | ⟨j, hj, hx⟩)
    · exact Or.inl h
    · exact Or.inr (Or.inl h)
    · refine Or.inr (Or.inr ⟨j, lt_of_lt_of_le hj (by omega), ?_⟩)
      have : j < s := by omega
      simp [l', this, hx]
  have tr' : ∀ x, Available l' s x → Available l' t x := by
    rintro x (h | h | ⟨j, hj, hx⟩)
    · exact Or.inl h
    · exact Or.inr (Or.inl h)
    · exact Or.inr (Or.inr ⟨j, lt_of_lt_of_le hj hst, hx⟩)
  refine ⟨l', tr' p (tr s le_rfl p hout), fun i hi => ?_⟩
  by_cases his : i < s
  · obtain ⟨a, b, ha, hb, hop⟩ := hg i his
    refine ⟨a, b, tr i his.le a ha, tr i his.le b hb, ?_⟩
    simpa [l', his] using hop
  · refine ⟨0, 0, Or.inr (Or.inl ⟨0, by simp⟩), Or.inr (Or.inl ⟨0, by simp⟩), Or.inl ?_⟩
    simp [l', his]

theorem statement_computes_mono {R : Type u} {V : Type} [CommSemiring R]
    {p : MvPolynomial V R} {s t : ℕ} (h : Statement.Computes p s) (hst : s ≤ t) :
    Statement.Computes p t := by
  obtain ⟨l, hg, k, hk, hout⟩ := h
  refine ⟨fun i => if i < s then l i else 0, ?_, k, lt_of_lt_of_le hk hst, by simp [hk, hout]⟩
  intro i hi
  by_cases his : i < s
  · rcases hg i his with ⟨v, hv⟩ | ⟨a, ha⟩ | ⟨j, hj, m, hm, he⟩ | ⟨j, hj, m, hm, he⟩
    · exact Or.inl ⟨v, by simp [his, hv]⟩
    · exact Or.inr (Or.inl ⟨a, by simp [his, ha]⟩)
    · have hj' : j < s := lt_trans hj his
      have hm' : m < s := lt_trans hm his
      exact Or.inr (Or.inr (Or.inl ⟨j, hj, m, hm, by simp [his, hj', hm', he]⟩))
    · have hj' : j < s := lt_trans hj his
      have hm' : m < s := lt_trans hm his
      exact Or.inr (Or.inr (Or.inr ⟨j, hj, m, hm, by simp [his, hj', hm', he]⟩))
  · exact Or.inr (Or.inl ⟨0, by simp [his]⟩)

/-! ## Reverse compiler: free gates to charged gates -/

/-- A value a charged table must materialize with its own leaf gate. -/
def Leaf {F V : Type*} [Field F] (x : MvPolynomial V F) : Prop :=
  (∃ j : V, X j = x) ∨ (∃ a : F, C a = x)

/-- Slot layout: index `0` holds `C (-1)`; free gate `i` owns slots `4i+1 … 4i+4` (operand
leaves, the negated second operand, and the gate value); slot `4s+1` holds a leaf output. -/
theorem canonical_to_anthropic {F : Type u} {V : Type} [Field F]
    (p : MvPolynomial V F) (s : ℕ) (h : Computes p s) : Statement.Computes p (4 * s + 2) := by
  obtain ⟨l, hout, hg⟩ := h
  choose! A B hA hB hop using hg
  have hJA : ∀ i < s, ¬ Leaf (A i) → ∃ j < i, l j = A i := by
    intro i hi hn
    rcases hA i hi with h | h | h
    · exact (hn (Or.inl h)).elim
    · exact (hn (Or.inr h)).elim
    · exact h
  have hJB : ∀ i < s, ¬ Leaf (B i) → ∃ j < i, l j = B i := by
    intro i hi hn
    rcases hB i hi with h | h | h
    · exact (hn (Or.inl h)).elim
    · exact (hn (Or.inr h)).elim
    · exact h
  choose! JA hJAlt hJAeq using hJA
  choose! JB hJBlt hJBeq using hJB
  let refA : ℕ → ℕ := fun i => if Leaf (A i) then 4 * i + 1 else 4 * JA i + 4
  let refB : ℕ → ℕ := fun i => if Leaf (B i) then 4 * i + 2 else 4 * JB i + 4
  let slot : ℕ → ℕ → MvPolynomial V F := fun i r =>
    if r = 0 then (if Leaf (A i) then A i else 0)
    else if r = 1 then (if Leaf (B i) then B i else 0)
    else if r = 2 then (if l i = A i - B i then C (-1) * B i else 0)
    else l i
  let L : ℕ → MvPolynomial V F := fun k =>
    if k = 0 then C (-1)
    else if k = 4 * s + 1 then (if Leaf p then p else 0)
    else slot ((k - 1) / 4) ((k - 1) % 4)
  have L0 : L 0 = C (-1) := by simp [L]
  have Lout : L (4 * s + 1) = if Leaf p then p else 0 := by simp [L]
  have Lslot : ∀ i < s, ∀ r < 4, L (4 * i + r + 1) = slot i r := by
    intro i hi r hr
    have h1 : 4 * i + r + 1 ≠ 0 := by omega
    have h2 : 4 * i + r + 1 ≠ 4 * s + 1 := by omega
    have h3 : (4 * i + r + 1 - 1) / 4 = i := by omega
    have h4 : (4 * i + r + 1 - 1) % 4 = r := by omega
    simp only [L, h1, h2, h3, h4, if_false]
  have Lgate : ∀ j < s, L (4 * j + 4) = l j := by
    intro j hj
    rw [show 4 * j + 4 = 4 * j + 3 + 1 by omega, Lslot j hj 3 (by norm_num)]
    simp [slot]
  have LrefA : ∀ i < s, L (refA i) = A i := by
    intro i hi
    by_cases hl : Leaf (A i)
    · rw [show refA i = 4 * i + 0 + 1 from if_pos hl, Lslot i hi 0 (by norm_num)]
      simp [slot, hl]
    · rw [show refA i = 4 * JA i + 4 from if_neg hl, Lgate (JA i) (lt_trans (hJAlt i hi hl) hi)]
      exact hJAeq i hi hl
  have LrefB : ∀ i < s, L (refB i) = B i := by
    intro i hi
    by_cases hl : Leaf (B i)
    · rw [show refB i = 4 * i + 1 + 1 from if_pos hl, Lslot i hi 1 (by norm_num)]
      simp [slot, hl]
    · rw [show refB i = 4 * JB i + 4 from if_neg hl, Lgate (JB i) (lt_trans (hJBlt i hi hl) hi)]
      exact hJBeq i hi hl
  have refA_lt : ∀ i < s, refA i < 4 * i + 3 := by
    intro i hi
    by_cases hl : Leaf (A i)
    · rw [show refA i = 4 * i + 1 from if_pos hl]; omega
    · have := hJAlt i hi hl
      rw [show refA i = 4 * JA i + 4 from if_neg hl]; omega
  have refB_lt : ∀ i < s, refB i < 4 * i + 3 := by
    intro i hi
    by_cases hl : Leaf (B i)
    · rw [show refB i = 4 * i + 2 from if_pos hl]; omega
    · have := hJBlt i hi hl
      rw [show refB i = 4 * JB i + 4 from if_neg hl]; omega
  have leafGate : ∀ x : MvPolynomial V F, ∀ k,
      L k = (if Leaf x then x else 0) →
      (∃ v : V, L k = X v) ∨ (∃ a : F, L k = C a) ∨
      (∃ i < k, ∃ j < k, L k = L i + L j) ∨ (∃ i < k, ∃ j < k, L k = L i * L j) := by
    intro x k hk
    by_cases hl : Leaf x
    · rw [if_pos hl] at hk
      rcases hl with ⟨j, hj⟩ | ⟨a, ha⟩
      · exact Or.inl ⟨j, hk.trans hj.symm⟩
      · exact Or.inr (Or.inl ⟨a, hk.trans ha.symm⟩)
    · rw [if_neg hl] at hk
      exact Or.inr (Or.inl ⟨0, by simp [hk]⟩)
  refine ⟨L, ?_, ?_⟩
  · intro k hk
    have hcases : k = 0 ∨ k = 4 * s + 1 ∨ ∃ i < s, ∃ r < 4, k = 4 * i + r + 1 := by
      rcases Nat.eq_zero_or_pos k with h0 | hpos
      · exact Or.inl h0
      · by_cases hk' : k = 4 * s + 1
        · exact Or.inr (Or.inl hk')
        · exact Or.inr (Or.inr ⟨(k - 1) / 4, by omega, (k - 1) % 4, by omega, by omega⟩)
    rcases hcases with rfl | rfl | ⟨i, hi, r, hr, rfl⟩
    · exact Or.inr (Or.inl ⟨-1, L0⟩)
    · exact leafGate p _ Lout
    · have hs := Lslot i hi r hr
      interval_cases r
      · exact leafGate (A i) _ (hs.trans (by simp [slot]))
      · exact leafGate (B i) _ (hs.trans (by simp [slot]))
      · by_cases hsub : l i = A i - B i
        · have hv : L (4 * i + 2 + 1) = L 0 * L (refB i) := by
            rw [hs, L0, LrefB i hi]; simp [slot, hsub]
          exact Or.inr (Or.inr (Or.inr ⟨0, by omega, refB i,
            by have := refB_lt i hi; omega, hv⟩))
        · exact Or.inr (Or.inl ⟨0, by rw [hs]; simp [slot, hsub]⟩)
      · have hv : L (4 * i + 3 + 1) = l i := by rw [hs]; simp [slot]
        have ha := refA_lt i hi
        have hb := refB_lt i hi
        rcases hop i hi with hadd | hsub | hmul
        · exact Or.inr (Or.inr (Or.inl ⟨refA i, by omega, refB i, by omega,
            by rw [hv, LrefA i hi, LrefB i hi, hadd]⟩))
        · have hneg : L (4 * i + 2 + 1) = C (-1) * B i := by
            rw [Lslot i hi 2 (by norm_num)]; simp [slot, hsub]
          refine Or.inr (Or.inr (Or.inl ⟨refA i, by omega, 4 * i + 2 + 1, by omega, ?_⟩))
          rw [hv, LrefA i hi, hneg, hsub, map_neg, map_one]
          ring
        · exact Or.inr (Or.inr (Or.inr ⟨refA i, by omega, refB i, by omega,
            by rw [hv, LrefA i hi, LrefB i hi, hmul]⟩))
  · rcases hout with ⟨j, hj⟩ | ⟨a, ha⟩ | ⟨j, hj, hx⟩
    · refine ⟨4 * s + 1, by omega, ?_⟩
      rw [Lout, if_pos (show Leaf p from Or.inl ⟨j, hj⟩)]
    · refine ⟨4 * s + 1, by omega, ?_⟩
      rw [Lout, if_pos (show Leaf p from Or.inr ⟨a, ha⟩)]
    · exact ⟨4 * j + 4, by omega, (Lgate j hj).trans hx⟩

/-- Exact gate counts under the two conventions agree up to `C_O ≤ C_A ≤ 4 C_O + 2`. -/
theorem charged_free_sandwich {F : Type u} {V : Type} [Field F] (p : MvPolynomial V F) (s : ℕ) :
    (Statement.Computes p s → Computes p s) ∧
      (Computes p s → Statement.Computes p (4 * s + 2)) :=
  ⟨anthropic_exact_to_canonical p s, canonical_to_anthropic p s⟩

/-- A charged lower bound `B < s` yields the free lower bound `B < 4 s + 2`. -/
theorem lower_transfer_reverse {F : Type u} {V : Type} [Field F]
    (p : MvPolynomial V F) (B : ℕ) (h : ∀ s, Statement.Computes p s → B < s) :
    ∀ s, Computes p s → B < 4 * s + 2 :=
  fun s hs => h _ (canonical_to_anthropic p s hs)

/-! ## Polynomial bounds -/

theorem polyBounded_mono {f g : ℕ → ℕ} (hfg : ∀ n, f n ≤ g n) (hg : PolyBounded g) :
    PolyBounded f := by
  obtain ⟨A, d, N, h⟩ := hg
  exact ⟨A, d, N, fun n hn => le_trans (hfg n) (h n hn)⟩

theorem allIndex_mono {a b : ℕ} (hab : a ≤ b) (n : ℕ) : n ^ a + a ≤ n ^ b + b := by
  rcases Nat.eq_zero_or_pos n with rfl | hn
  · rcases Nat.eq_zero_or_pos a with rfl | ha
    · rcases Nat.eq_zero_or_pos b with rfl | hb
      · simp
      · rw [zero_pow hb.ne']; simp; omega
    · rw [zero_pow ha.ne', zero_pow (by omega : b ≠ 0)]; omega
  · exact Nat.add_le_add (Nat.pow_le_pow_right hn hab) hab

theorem polyBounded_iff_allIndex (f : ℕ → ℕ) :
    PolyBounded f ↔ ∃ a : ℕ, ∀ n, f n ≤ n ^ a + a := by
  constructor
  · rintro ⟨A, d, N, h⟩
    refine ⟨d + A + (Finset.range N).sup f, fun n => ?_⟩
    by_cases hn : n < N
    · have hM : f n ≤ (Finset.range N).sup f := Finset.le_sup (Finset.mem_range.mpr hn)
      omega
    · have hb := h n (by omega)
      rcases Nat.lt_or_ge n 2 with h2 | h2
      · have hpow : n ^ d ≤ 1 := by
          interval_cases n
          · rcases Nat.eq_zero_or_pos d with rfl | hd
            · simp
            · simp [zero_pow hd.ne']
          · simp
        have : A * n ^ d ≤ A := by simpa using Nat.mul_le_mul_left A hpow
        omega
      · have h1 : A ≤ n ^ A :=
          le_trans (Nat.lt_two_pow_self).le (Nat.pow_le_pow_left h2 A)
        have h3 : A * n ^ d ≤ n ^ (d + A + (Finset.range N).sup f) :=
          calc A * n ^ d ≤ n ^ A * n ^ d := Nat.mul_le_mul_right _ h1
            _ = n ^ (d + A) := by rw [← pow_add, add_comm]
            _ ≤ n ^ (d + A + (Finset.range N).sup f) := Nat.pow_le_pow_right (by omega) (by omega)
        omega
  · rintro ⟨a, h⟩
    refine ⟨a + 1, a, 1, fun n hn => ?_⟩
    have h1 : 1 ≤ n ^ a := Nat.one_le_pow _ _ hn
    have h2 : a ≤ a * n ^ a := Nat.le_mul_of_pos_right a h1
    have h3 := h n
    calc f n ≤ n ^ a + a := h3
      _ ≤ n ^ a + a * n ^ a := by omega
      _ = (a + 1) * n ^ a := by ring

/-! ## VP under the three conventions -/

/-- OpenAI's `IsVP` and the canonical `VP` coincide. -/
theorem openai_vp_iff {F : Type u} [Field F] {σ : ℕ → Type} [∀ n, Fintype (σ n)]
    (f : Family F σ) : OAI.Computability.VPVNP.Valiant.Project.IsVP f ↔ VP f := by
  constructor
  · rintro ⟨hP, s, hs, hc⟩
    exact ⟨hP, s, hs, fun n => (openai_exact_iff _ _).mp (hc n)⟩
  · rintro ⟨hP, s, hs, hc⟩
    exact ⟨hP, s, hs, fun n => (openai_exact_iff _ _).mpr (hc n)⟩

/-- Canonical VP (free gates, eventual bounds) equals Anthropic VP (charged gates,
all-index `n ^ a + a` bounds). -/
theorem vp_iff_anthropic {F : Type u} [Field F] (f : Statement.Family F) :
    VP f.poly ↔ f ∈ Statement.VP F := by
  show _ ↔ ∃ a : ℕ, ∀ n, Fintype.card (f.vars n) ≤ n ^ a + a ∧
      (f.poly n).totalDegree ≤ n ^ a + a ∧ Statement.Computes (f.poly n) (n ^ a + a)
  constructor
  · rintro ⟨⟨hcard, hdeg⟩, s, hs, hc⟩
    obtain ⟨a1, h1⟩ := (polyBounded_iff_allIndex _).mp hcard
    obtain ⟨a2, h2⟩ := (polyBounded_iff_allIndex _).mp hdeg
    have hs' : PolyBounded (fun n => 4 * s n + 2) := by
      obtain ⟨A, d, N, h⟩ := hs
      refine ⟨4 * A + 2, d, max N 1, fun n hn => ?_⟩
      have hN : N ≤ n := le_trans (le_max_left _ _) hn
      have hpos : 1 ≤ n ^ d := Nat.one_le_pow _ _ (by have := le_max_right N 1; omega)
      have := h n hN
      nlinarith
    obtain ⟨a3, h3⟩ := (polyBounded_iff_allIndex _).mp hs'
    refine ⟨max a1 (max a2 a3), fun n => ⟨?_, ?_, ?_⟩⟩
    · exact le_trans (h1 n) (allIndex_mono (le_max_left _ _) n)
    · exact le_trans (h2 n) (allIndex_mono (le_trans (le_max_left _ _) (le_max_right _ _)) n)
    · refine statement_computes_mono (canonical_to_anthropic _ _ (hc n)) ?_
      exact le_trans (h3 n) (allIndex_mono (le_trans (le_max_right _ _) (le_max_right _ _)) n)
  · rintro ⟨a, h⟩
    refine ⟨⟨(polyBounded_iff_allIndex _).mpr ⟨a, fun n => (h n).1⟩,
      (polyBounded_iff_allIndex _).mpr ⟨a, fun n => (h n).2.1⟩⟩,
      fun n => n ^ a + a, (polyBounded_iff_allIndex _).mpr ⟨a, fun n => le_rfl⟩,
      fun n => anthropic_exact_to_canonical _ _ (h n).2.2⟩

/-! ## VNP witness transport -/

theorem computes_rename {F : Type*} {V W : Type*} [Field F] (σ : V → W)
    {p : MvPolynomial V F} {s : ℕ} (h : Computes p s) : Computes (rename σ p) s := by
  obtain ⟨l, hout, hg⟩ := h
  have tr : ∀ k x, Available l k x → Available (fun i => rename σ (l i)) k (rename σ x) := by
    rintro k x (⟨j, rfl⟩ | ⟨a, rfl⟩ | ⟨j, hj, rfl⟩)
    · exact Or.inl ⟨σ j, (rename_X σ j).symm⟩
    · exact Or.inr (Or.inl ⟨a, (rename_C σ a).symm⟩)
    · exact Or.inr (Or.inr ⟨j, hj, rfl⟩)
  refine ⟨fun i => rename σ (l i), tr s p hout, fun i hi => ?_⟩
  obtain ⟨a, b, ha, hb, hop⟩ := hg i hi
  refine ⟨rename σ a, rename σ b, tr i a ha, tr i b hb, ?_⟩
  rcases hop with h | h | h <;> simp [h]

/-- Boolean summation is invariant under renaming the witness type along an equivalence. -/
theorem witness_sum_reindex {F : Type*} [Field F] {V W W' : Type*} [Fintype W] [Fintype W']
    [DecidableEq W] [DecidableEq W'] (E : W ≃ W') (g : MvPolynomial (V ⊕ W) F) :
    (∑ y : W → Bool, eval₂Hom C (Sum.elim X (fun i => C (if y i then 1 else 0))) g) =
      ∑ e : W' → Bool, eval₂Hom C (Sum.elim X (fun j => C (if e j then 1 else 0)))
        (rename (Sum.map id E) g) := by
  refine Fintype.sum_equiv (E.arrowCongr (Equiv.refl Bool)) _ _ (fun y => ?_)
  simp only [coe_eval₂Hom, eval₂_rename]
  congr 1
  funext x
  rcases x with x | x <;> simp [Equiv.arrowCongr_apply]

/-- OpenAI's VNP, with an arbitrary finite witness type at each index, equals the canonical
VNP over `Fin (r n)`. -/
theorem openai_vnp_iff_canonical {F : Type u} [Field F] {σ : ℕ → Type} [∀ n, Fintype (σ n)]
    (p : Family F σ) : OAI.Computability.VPVNP.Valiant.Project.IsVNP p ↔ VNP p := by
  constructor
  · rintro ⟨hP, W, inst, g, hW, hgVP, hsum⟩
    let r : ℕ → ℕ := fun n => Fintype.card (W n)
    let E : ∀ n, W n ≃ Fin (r n) := fun n => Fintype.equivFin (W n)
    let g' : Family F (fun n => σ n ⊕ Fin (r n)) := fun n => rename (Sum.map id (E n)) (g n)
    obtain ⟨⟨hcard, hdeg⟩, s, hs, hc⟩ := (openai_vp_iff g).mp hgVP
    refine ⟨hP, r, g', hW, ⟨⟨?_, ?_⟩, s, hs, fun n => computes_rename _ (hc n)⟩, fun n => ?_⟩
    · refine polyBounded_mono (fun n => le_of_eq ?_) hcard
      simp [r, Fintype.card_sum]
    · exact polyBounded_mono (fun n => totalDegree_rename_le _ _) hdeg
    · rw [hsum n]
      exact witness_sum_reindex (E n) (g n)
  · rintro ⟨hP, r, g, hr, hgVP, hsum⟩
    refine ⟨hP, fun n => Fin (r n), fun n => inferInstance, g, ?_, (openai_vp_iff g).mpr hgVP,
      fun n => ?_⟩
    · obtain ⟨A, d, N, h⟩ := hr
      exact ⟨A, d, N, fun n hn => by simpa using h n hn⟩
    · rw [hsum n]
      convert rfl

/-- VP ⊆ VNP in the canonical (hence OpenAI) formulation: no witness bits. -/
theorem vp_subset_vnp {F : Type u} [Field F] {V : ℕ → Type} [∀ n, Fintype (V n)]
    (f : Family F V) (h : VP f) : VNP f := by
  obtain ⟨hP, s, hs, hc⟩ := h
  refine ⟨hP, fun _ => 0, fun n => rename Sum.inl (f n), ⟨0, 0, 0, fun n _ => by simp⟩,
    ⟨⟨?_, ?_⟩, s, hs, fun n => computes_rename _ (hc n)⟩, fun n => ?_⟩
  · exact polyBounded_mono (fun n => le_of_eq (by simp [Fintype.card_sum])) hP.1
  · exact polyBounded_mono (fun n => totalDegree_rename_le _ _) hP.2
  · rw [Fintype.sum_unique, coe_eval₂Hom, eval₂_rename, Sum.elim_comp_inl, eval₂_eta]

theorem aeval_bool_eq {F : Type*} [Field F] {V : Type*} {k : ℕ} (e : Fin k → Bool)
    (q : MvPolynomial (V ⊕ Fin k) F) :
    aeval (Sum.elim X fun i => if e i then 1 else 0) q =
      eval₂Hom C (Sum.elim X fun j => C (if e j then 1 else 0)) q := by
  rw [aeval_def, algebraMap_eq, coe_eval₂Hom]
  congr 1
  funext x
  rcases x with x | x
  · rfl
  · simp only [Sum.elim_inr]
    split_ifs <;> simp

/-- Canonical VNP implies Anthropic VNP. The converse needs a degree bound for the summed
family and remains open here. -/
theorem canonical_vnp_to_anthropic {F : Type u} [Field F] (f : Statement.Family F)
    (h : VNP f.poly) : f ∈ Statement.VNP F := by
  obtain ⟨_, r, g, _, hgVP, hsum⟩ := h
  refine ⟨r, g, (vp_iff_anthropic ⟨fun n => f.vars n ⊕ Fin (r n), g⟩).mp hgVP, fun n => ?_⟩
  rw [hsum n]
  exact Finset.sum_congr rfl (fun e _ => (aeval_bool_eq e (g n)).symm)

end FeedbackChannel.CPF02
