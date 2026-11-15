/- BPD-LG-01 v2 positive theorems; kernel-checked with #print axioms -/

theorem thm_bpd2_exact_d1_r1_pos (P0 P1 Q0 Q1 G D0 D1 D2 : Prop) (hq0 : Q0) (hs1 : P0 → P1) (hjoin : P1 → Q1 → G) (h0 : P0) (hb1 : Q0 → Q1) (hd1 : D0 → D1) (hd2 : D1 → D2) : G := by
  exact hjoin (hs1 h0) (hb1 hq0)

#print axioms thm_bpd2_exact_d1_r1_pos

theorem thm_bpd2_rw_d2_r1_pos (x0 x1 x2 x3 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : x0 + 1 = x3 + 1 := by
  rw [h0, h1, h2]

#print axioms thm_bpd2_rw_d2_r1_pos

theorem thm_bpd2_rw_d2_r5_pos (x0 x1 x2 x3 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : Option.some x0 = Option.some x3 := by
  rw [h0, h1, h2]

#print axioms thm_bpd2_rw_d2_r5_pos

theorem thm_bpd2_rcases_d1_r0_pos (P0 P1 D0 D1 D2 : Prop) (h0 : (P0 ∧ True)) (h1 : P0 → (P1 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : (P1 ∧ True) := by
  rcases h0 with ⟨p0, _⟩
  rcases h1 p0 with ⟨p1, _⟩
  exact ⟨p1, True.intro⟩

#print axioms thm_bpd2_rcases_d1_r0_pos

theorem thm_bpd2_rcases_d2_r1_pos (P0 P1 P2 D0 D1 D2 : Prop) (h0 : (True ∧ P0)) (h1 : P0 → (True ∧ P1)) (h2 : P1 → (True ∧ P2)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : (True ∧ P2) := by
  rcases h0 with ⟨_, p0⟩
  rcases h1 p0 with ⟨_, p1⟩
  rcases h2 p1 with ⟨_, p2⟩
  exact ⟨True.intro, p2⟩

#print axioms thm_bpd2_rcases_d2_r1_pos

theorem thm_bpd2_rcases_d2_r3_pos (P0 P1 P2 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Bool) => P0)) (h1 : P0 → Exists (fun (_ : Bool) => P1)) (h2 : P1 → Exists (fun (_ : Bool) => P2)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : Exists (fun (_ : Bool) => P2) := by
  rcases h0 with ⟨_, p0⟩
  rcases h1 p0 with ⟨_, p1⟩
  rcases h2 p1 with ⟨_, p2⟩
  exact ⟨true, p2⟩

#print axioms thm_bpd2_rcases_d2_r3_pos

theorem thm_bpd2_rcases_d3_r1_pos (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : (True ∧ P0)) (h1 : P0 → (True ∧ P1)) (h2 : P1 → (True ∧ P2)) (h3 : P2 → (True ∧ P3)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : (True ∧ P3) := by
  rcases h0 with ⟨_, p0⟩
  rcases h1 p0 with ⟨_, p1⟩
  rcases h2 p1 with ⟨_, p2⟩
  rcases h3 p2 with ⟨_, p3⟩
  exact ⟨True.intro, p3⟩

#print axioms thm_bpd2_rcases_d3_r1_pos

theorem thm_bpd2_induction_d3_r1_pos (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, [F0 n] = [n] := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1, h2, h3]
    injection ih with ih0
    rw [ih0]

#print axioms thm_bpd2_induction_d3_r1_pos
