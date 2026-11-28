/- BPD-LG-01 v2 positive theorems; kernel-checked with #print axioms -/

theorem thm_bpd2_exact_d1_r0_pos (P0 P1 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 → P1) (hd1 : D0 → D1) (hd2 : D1 → D2) : P1 := by
  exact (h1 h0)

#print axioms thm_bpd2_exact_d1_r0_pos

theorem thm_bpd2_exact_d2_r3_pos (P0 P1 P2 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ∨ False → P1) (h2 : P1 ∨ False → P2) (hd1 : D0 → D1) (hd2 : D1 → D2) : P2 ∨ False := by
  exact Or.inl (h2 (Or.inl (h1 (Or.inl h0))))

#print axioms thm_bpd2_exact_d2_r3_pos

theorem thm_bpd2_exact_d3_r0_pos (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 → P1) (h2 : P1 → P2) (h3 : P2 → P3) (hd1 : D0 → D1) (hd2 : D1 → D2) : P3 := by
  exact (h3 (h2 (h1 h0)))

#print axioms thm_bpd2_exact_d3_r0_pos

theorem thm_bpd2_rw_d2_r2_pos (x0 x1 x2 x3 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : x0 * 2 + 1 = x3 * 2 + 1 := by
  rw [h0, h1, h2]

#print axioms thm_bpd2_rw_d2_r2_pos

theorem thm_bpd2_rw_d2_r3_pos (x0 x1 x2 x3 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : (x0, 0) = (x3, 0) := by
  rw [h0, h1, h2]

#print axioms thm_bpd2_rw_d2_r3_pos

theorem thm_bpd2_rw_d3_r0_pos (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : Nat.succ x0 = Nat.succ x4 := by
  rw [h0, h1, h2, h3]

#print axioms thm_bpd2_rw_d3_r0_pos

theorem thm_bpd2_rw_d3_r1_pos (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : x0 + 1 = x4 + 1 := by
  rw [h0, h1, h2, h3]

#print axioms thm_bpd2_rw_d3_r1_pos

theorem thm_bpd2_rcases_d1_r2_pos (P0 P1 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Nat) => P0)) (h1 : P0 → Exists (fun (_ : Nat) => P1)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : Exists (fun (_ : Nat) => P1) := by
  rcases h0 with ⟨_, p0⟩
  rcases h1 p0 with ⟨_, p1⟩
  exact ⟨0, p1⟩

#print axioms thm_bpd2_rcases_d1_r2_pos

theorem thm_bpd2_rcases_d3_r3_pos (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Bool) => P0)) (h1 : P0 → Exists (fun (_ : Bool) => P1)) (h2 : P1 → Exists (fun (_ : Bool) => P2)) (h3 : P2 → Exists (fun (_ : Bool) => P3)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : Exists (fun (_ : Bool) => P3) := by
  rcases h0 with ⟨_, p0⟩
  rcases h1 p0 with ⟨_, p1⟩
  rcases h2 p1 with ⟨_, p2⟩
  rcases h3 p2 with ⟨_, p3⟩
  exact ⟨true, p3⟩

#print axioms thm_bpd2_rcases_d3_r3_pos

theorem thm_bpd2_induction_d1_r2_pos (F0 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, F0 n + 1 = n + 1 := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1]
    have ih0 : F0 n = n := Nat.add_right_cancel ih
    rw [ih0]

#print axioms thm_bpd2_induction_d1_r2_pos

theorem thm_bpd2_induction_d2_r3_pos (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, Nat.succ (F0 n) = Nat.succ n := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1, h2]
    injection ih with ih0
    rw [ih0]

#print axioms thm_bpd2_induction_d2_r3_pos

theorem thm_bpd2_induction_d3_r5_pos (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, Option.some (F0 n) = Option.some n := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1, h2, h3]
    injection ih with ih0
    rw [ih0]

#print axioms thm_bpd2_induction_d3_r5_pos
