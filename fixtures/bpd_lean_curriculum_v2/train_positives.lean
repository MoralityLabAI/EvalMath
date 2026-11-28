/- BPD-LG-01 v2 positive theorems; kernel-checked with #print axioms -/

theorem thm_bpd2_exact_d1_r2_pos (P0 P1 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ∧ True → P1) (hd1 : D0 → D1) (hd2 : D1 → D2) : P1 ∧ True := by
  exact ⟨(h1 ⟨h0, True.intro⟩), True.intro⟩

#print axioms thm_bpd2_exact_d1_r2_pos

theorem thm_bpd2_exact_d1_r3_pos (P0 P1 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ∨ False → P1) (hd1 : D0 → D1) (hd2 : D1 → D2) : P1 ∨ False := by
  exact Or.inl (h1 (Or.inl h0))

#print axioms thm_bpd2_exact_d1_r3_pos

theorem thm_bpd2_exact_d1_r4_pos (P0 P1 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ↔ P1) (hd1 : D0 → D1) (hd2 : D1 → D2) : True ↔ P1 := by
  exact ⟨fun _ => (h1.mp h0), fun _ => True.intro⟩

#print axioms thm_bpd2_exact_d1_r4_pos

theorem thm_bpd2_exact_d1_r5_pos (P0 P1 D0 D1 D2 : Prop) (h0 : Unit → P0) (h1 : P0 → Unit → P1) (hd1 : D0 → D1) (hd2 : D1 → D2) : Unit → P1 := by
  exact fun _ => (h1 (h0 ()) ())

#print axioms thm_bpd2_exact_d1_r5_pos

theorem thm_bpd2_exact_d2_r0_pos (P0 P1 P2 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 → P1) (h2 : P1 → P2) (hd1 : D0 → D1) (hd2 : D1 → D2) : P2 := by
  exact (h2 (h1 h0))

#print axioms thm_bpd2_exact_d2_r0_pos

theorem thm_bpd2_exact_d2_r1_pos (P0 P1 P2 Q0 Q1 Q2 G D0 D1 D2 : Prop) (hq0 : Q0) (hs1 : P0 → P1) (hs2 : P1 → P2) (hjoin : P2 → Q2 → G) (h0 : P0) (hb1 : Q0 → Q1) (hb2 : Q1 → Q2) (hd1 : D0 → D1) (hd2 : D1 → D2) : G := by
  exact hjoin (hs2 (hs1 h0)) (hb2 (hb1 hq0))

#print axioms thm_bpd2_exact_d2_r1_pos

theorem thm_bpd2_exact_d2_r2_pos (P0 P1 P2 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ∧ True → P1) (h2 : P1 ∧ True → P2) (hd1 : D0 → D1) (hd2 : D1 → D2) : P2 ∧ True := by
  exact ⟨(h2 ⟨(h1 ⟨h0, True.intro⟩), True.intro⟩), True.intro⟩

#print axioms thm_bpd2_exact_d2_r2_pos

theorem thm_bpd2_exact_d2_r4_pos (P0 P1 P2 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ↔ P1) (h2 : P1 ↔ P2) (hd1 : D0 → D1) (hd2 : D1 → D2) : True ↔ P2 := by
  exact ⟨fun _ => (h2.mp (h1.mp h0)), fun _ => True.intro⟩

#print axioms thm_bpd2_exact_d2_r4_pos

theorem thm_bpd2_exact_d2_r5_pos (P0 P1 P2 D0 D1 D2 : Prop) (h0 : Unit → P0) (h1 : P0 → Unit → P1) (h2 : P1 → Unit → P2) (hd1 : D0 → D1) (hd2 : D1 → D2) : Unit → P2 := by
  exact fun _ => (h2 (h1 (h0 ()) ()) ())

#print axioms thm_bpd2_exact_d2_r5_pos

theorem thm_bpd2_exact_d3_r1_pos (P0 P1 P2 P3 Q0 Q1 Q2 Q3 G D0 D1 D2 : Prop) (hq0 : Q0) (hs1 : P0 → P1) (hs2 : P1 → P2) (hs3 : P2 → P3) (hjoin : P3 → Q3 → G) (h0 : P0) (hb1 : Q0 → Q1) (hb2 : Q1 → Q2) (hb3 : Q2 → Q3) (hd1 : D0 → D1) (hd2 : D1 → D2) : G := by
  exact hjoin (hs3 (hs2 (hs1 h0))) (hb3 (hb2 (hb1 hq0)))

#print axioms thm_bpd2_exact_d3_r1_pos

theorem thm_bpd2_exact_d3_r2_pos (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ∧ True → P1) (h2 : P1 ∧ True → P2) (h3 : P2 ∧ True → P3) (hd1 : D0 → D1) (hd2 : D1 → D2) : P3 ∧ True := by
  exact ⟨(h3 ⟨(h2 ⟨(h1 ⟨h0, True.intro⟩), True.intro⟩), True.intro⟩), True.intro⟩

#print axioms thm_bpd2_exact_d3_r2_pos

theorem thm_bpd2_exact_d3_r3_pos (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ∨ False → P1) (h2 : P1 ∨ False → P2) (h3 : P2 ∨ False → P3) (hd1 : D0 → D1) (hd2 : D1 → D2) : P3 ∨ False := by
  exact Or.inl (h3 (Or.inl (h2 (Or.inl (h1 (Or.inl h0))))))

#print axioms thm_bpd2_exact_d3_r3_pos

theorem thm_bpd2_exact_d3_r4_pos (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ↔ P1) (h2 : P1 ↔ P2) (h3 : P2 ↔ P3) (hd1 : D0 → D1) (hd2 : D1 → D2) : True ↔ P3 := by
  exact ⟨fun _ => (h3.mp (h2.mp (h1.mp h0))), fun _ => True.intro⟩

#print axioms thm_bpd2_exact_d3_r4_pos

theorem thm_bpd2_exact_d3_r5_pos (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : Unit → P0) (h1 : P0 → Unit → P1) (h2 : P1 → Unit → P2) (h3 : P2 → Unit → P3) (hd1 : D0 → D1) (hd2 : D1 → D2) : Unit → P3 := by
  exact fun _ => (h3 (h2 (h1 (h0 ()) ()) ()) ())

#print axioms thm_bpd2_exact_d3_r5_pos

theorem thm_bpd2_rw_d1_r0_pos (x0 x1 x2 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : Nat.succ x0 = Nat.succ x2 := by
  rw [h0, h1]

#print axioms thm_bpd2_rw_d1_r0_pos

theorem thm_bpd2_rw_d1_r1_pos (x0 x1 x2 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : x0 + 1 = x2 + 1 := by
  rw [h0, h1]

#print axioms thm_bpd2_rw_d1_r1_pos

theorem thm_bpd2_rw_d1_r2_pos (x0 x1 x2 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : x0 * 2 + 1 = x2 * 2 + 1 := by
  rw [h0, h1]

#print axioms thm_bpd2_rw_d1_r2_pos

theorem thm_bpd2_rw_d1_r3_pos (x0 x1 x2 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : (x0, 0) = (x2, 0) := by
  rw [h0, h1]

#print axioms thm_bpd2_rw_d1_r3_pos

theorem thm_bpd2_rw_d1_r4_pos (x0 x1 x2 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : [x0] = [x2] := by
  rw [h0, h1]

#print axioms thm_bpd2_rw_d1_r4_pos

theorem thm_bpd2_rw_d1_r5_pos (x0 x1 x2 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : Option.some x0 = Option.some x2 := by
  rw [h0, h1]

#print axioms thm_bpd2_rw_d1_r5_pos

theorem thm_bpd2_rw_d2_r0_pos (x0 x1 x2 x3 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : Nat.succ x0 = Nat.succ x3 := by
  rw [h0, h1, h2]

#print axioms thm_bpd2_rw_d2_r0_pos

theorem thm_bpd2_rw_d2_r4_pos (x0 x1 x2 x3 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : [x0] = [x3] := by
  rw [h0, h1, h2]

#print axioms thm_bpd2_rw_d2_r4_pos

theorem thm_bpd2_rw_d3_r2_pos (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : x0 * 2 + 1 = x4 * 2 + 1 := by
  rw [h0, h1, h2, h3]

#print axioms thm_bpd2_rw_d3_r2_pos

theorem thm_bpd2_rw_d3_r3_pos (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : (x0, 0) = (x4, 0) := by
  rw [h0, h1, h2, h3]

#print axioms thm_bpd2_rw_d3_r3_pos

theorem thm_bpd2_rw_d3_r4_pos (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : [x0] = [x4] := by
  rw [h0, h1, h2, h3]

#print axioms thm_bpd2_rw_d3_r4_pos

theorem thm_bpd2_rw_d3_r5_pos (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) : Option.some x0 = Option.some x4 := by
  rw [h0, h1, h2, h3]

#print axioms thm_bpd2_rw_d3_r5_pos

theorem thm_bpd2_rcases_d1_r1_pos (P0 P1 D0 D1 D2 : Prop) (h0 : (True ∧ P0)) (h1 : P0 → (True ∧ P1)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : (True ∧ P1) := by
  rcases h0 with ⟨_, p0⟩
  rcases h1 p0 with ⟨_, p1⟩
  exact ⟨True.intro, p1⟩

#print axioms thm_bpd2_rcases_d1_r1_pos

theorem thm_bpd2_rcases_d1_r3_pos (P0 P1 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Bool) => P0)) (h1 : P0 → Exists (fun (_ : Bool) => P1)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : Exists (fun (_ : Bool) => P1) := by
  rcases h0 with ⟨_, p0⟩
  rcases h1 p0 with ⟨_, p1⟩
  exact ⟨true, p1⟩

#print axioms thm_bpd2_rcases_d1_r3_pos

theorem thm_bpd2_rcases_d1_r4_pos (P0 P1 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Unit) => P0 ∧ True)) (h1 : P0 → Exists (fun (_ : Unit) => P1 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : Exists (fun (_ : Unit) => P1 ∧ True) := by
  rcases h0 with ⟨_, p0, _⟩
  rcases h1 p0 with ⟨_, p1, _⟩
  exact ⟨(), p1, True.intro⟩

#print axioms thm_bpd2_rcases_d1_r4_pos

theorem thm_bpd2_rcases_d1_r5_pos (P0 P1 D0 D1 D2 : Prop) (h0 : ((P0 ∧ P0) ∧ True)) (h1 : P0 → ((P1 ∧ P1) ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : ((P1 ∧ P1) ∧ True) := by
  rcases h0 with ⟨⟨p0, _⟩, _⟩
  rcases h1 p0 with ⟨⟨p1, _⟩, _⟩
  exact ⟨⟨p1, p1⟩, True.intro⟩

#print axioms thm_bpd2_rcases_d1_r5_pos

theorem thm_bpd2_rcases_d2_r0_pos (P0 P1 P2 D0 D1 D2 : Prop) (h0 : (P0 ∧ True)) (h1 : P0 → (P1 ∧ True)) (h2 : P1 → (P2 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : (P2 ∧ True) := by
  rcases h0 with ⟨p0, _⟩
  rcases h1 p0 with ⟨p1, _⟩
  rcases h2 p1 with ⟨p2, _⟩
  exact ⟨p2, True.intro⟩

#print axioms thm_bpd2_rcases_d2_r0_pos

theorem thm_bpd2_rcases_d2_r2_pos (P0 P1 P2 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Nat) => P0)) (h1 : P0 → Exists (fun (_ : Nat) => P1)) (h2 : P1 → Exists (fun (_ : Nat) => P2)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : Exists (fun (_ : Nat) => P2) := by
  rcases h0 with ⟨_, p0⟩
  rcases h1 p0 with ⟨_, p1⟩
  rcases h2 p1 with ⟨_, p2⟩
  exact ⟨0, p2⟩

#print axioms thm_bpd2_rcases_d2_r2_pos

theorem thm_bpd2_rcases_d2_r4_pos (P0 P1 P2 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Unit) => P0 ∧ True)) (h1 : P0 → Exists (fun (_ : Unit) => P1 ∧ True)) (h2 : P1 → Exists (fun (_ : Unit) => P2 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : Exists (fun (_ : Unit) => P2 ∧ True) := by
  rcases h0 with ⟨_, p0, _⟩
  rcases h1 p0 with ⟨_, p1, _⟩
  rcases h2 p1 with ⟨_, p2, _⟩
  exact ⟨(), p2, True.intro⟩

#print axioms thm_bpd2_rcases_d2_r4_pos

theorem thm_bpd2_rcases_d2_r5_pos (P0 P1 P2 D0 D1 D2 : Prop) (h0 : ((P0 ∧ P0) ∧ True)) (h1 : P0 → ((P1 ∧ P1) ∧ True)) (h2 : P1 → ((P2 ∧ P2) ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : ((P2 ∧ P2) ∧ True) := by
  rcases h0 with ⟨⟨p0, _⟩, _⟩
  rcases h1 p0 with ⟨⟨p1, _⟩, _⟩
  rcases h2 p1 with ⟨⟨p2, _⟩, _⟩
  exact ⟨⟨p2, p2⟩, True.intro⟩

#print axioms thm_bpd2_rcases_d2_r5_pos

theorem thm_bpd2_rcases_d3_r0_pos (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : (P0 ∧ True)) (h1 : P0 → (P1 ∧ True)) (h2 : P1 → (P2 ∧ True)) (h3 : P2 → (P3 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : (P3 ∧ True) := by
  rcases h0 with ⟨p0, _⟩
  rcases h1 p0 with ⟨p1, _⟩
  rcases h2 p1 with ⟨p2, _⟩
  rcases h3 p2 with ⟨p3, _⟩
  exact ⟨p3, True.intro⟩

#print axioms thm_bpd2_rcases_d3_r0_pos

theorem thm_bpd2_rcases_d3_r2_pos (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Nat) => P0)) (h1 : P0 → Exists (fun (_ : Nat) => P1)) (h2 : P1 → Exists (fun (_ : Nat) => P2)) (h3 : P2 → Exists (fun (_ : Nat) => P3)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : Exists (fun (_ : Nat) => P3) := by
  rcases h0 with ⟨_, p0⟩
  rcases h1 p0 with ⟨_, p1⟩
  rcases h2 p1 with ⟨_, p2⟩
  rcases h3 p2 with ⟨_, p3⟩
  exact ⟨0, p3⟩

#print axioms thm_bpd2_rcases_d3_r2_pos

theorem thm_bpd2_rcases_d3_r4_pos (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Unit) => P0 ∧ True)) (h1 : P0 → Exists (fun (_ : Unit) => P1 ∧ True)) (h2 : P1 → Exists (fun (_ : Unit) => P2 ∧ True)) (h3 : P2 → Exists (fun (_ : Unit) => P3 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : Exists (fun (_ : Unit) => P3 ∧ True) := by
  rcases h0 with ⟨_, p0, _⟩
  rcases h1 p0 with ⟨_, p1, _⟩
  rcases h2 p1 with ⟨_, p2, _⟩
  rcases h3 p2 with ⟨_, p3, _⟩
  exact ⟨(), p3, True.intro⟩

#print axioms thm_bpd2_rcases_d3_r4_pos

theorem thm_bpd2_rcases_d3_r5_pos (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : ((P0 ∧ P0) ∧ True)) (h1 : P0 → ((P1 ∧ P1) ∧ True)) (h2 : P1 → ((P2 ∧ P2) ∧ True)) (h3 : P2 → ((P3 ∧ P3) ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) : ((P3 ∧ P3) ∧ True) := by
  rcases h0 with ⟨⟨p0, _⟩, _⟩
  rcases h1 p0 with ⟨⟨p1, _⟩, _⟩
  rcases h2 p1 with ⟨⟨p2, _⟩, _⟩
  rcases h3 p2 with ⟨⟨p3, _⟩, _⟩
  exact ⟨⟨p3, p3⟩, True.intro⟩

#print axioms thm_bpd2_rcases_d3_r5_pos

theorem thm_bpd2_induction_d1_r0_pos (F0 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, F0 n = n := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1]
    rw [ih]

#print axioms thm_bpd2_induction_d1_r0_pos

theorem thm_bpd2_induction_d1_r1_pos (F0 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, [F0 n] = [n] := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1]
    injection ih with ih0
    rw [ih0]

#print axioms thm_bpd2_induction_d1_r1_pos

theorem thm_bpd2_induction_d1_r3_pos (F0 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, Nat.succ (F0 n) = Nat.succ n := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1]
    injection ih with ih0
    rw [ih0]

#print axioms thm_bpd2_induction_d1_r3_pos

theorem thm_bpd2_induction_d1_r4_pos (F0 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, (F0 n, true) = (n, true) := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1]
    injection ih with ih0 _
    rw [ih0]

#print axioms thm_bpd2_induction_d1_r4_pos

theorem thm_bpd2_induction_d1_r5_pos (F0 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, Option.some (F0 n) = Option.some n := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1]
    injection ih with ih0
    rw [ih0]

#print axioms thm_bpd2_induction_d1_r5_pos

theorem thm_bpd2_induction_d2_r0_pos (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, F0 n = n := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1, h2]
    rw [ih]

#print axioms thm_bpd2_induction_d2_r0_pos

theorem thm_bpd2_induction_d2_r1_pos (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, [F0 n] = [n] := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1, h2]
    injection ih with ih0
    rw [ih0]

#print axioms thm_bpd2_induction_d2_r1_pos

theorem thm_bpd2_induction_d2_r2_pos (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, F0 n + 1 = n + 1 := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1, h2]
    have ih0 : F0 n = n := Nat.add_right_cancel ih
    rw [ih0]

#print axioms thm_bpd2_induction_d2_r2_pos

theorem thm_bpd2_induction_d2_r4_pos (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, (F0 n, true) = (n, true) := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1, h2]
    injection ih with ih0 _
    rw [ih0]

#print axioms thm_bpd2_induction_d2_r4_pos

theorem thm_bpd2_induction_d2_r5_pos (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, Option.some (F0 n) = Option.some n := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1, h2]
    injection ih with ih0
    rw [ih0]

#print axioms thm_bpd2_induction_d2_r5_pos

theorem thm_bpd2_induction_d3_r0_pos (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, F0 n = n := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1, h2, h3]
    rw [ih]

#print axioms thm_bpd2_induction_d3_r0_pos

theorem thm_bpd2_induction_d3_r2_pos (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, F0 n + 1 = n + 1 := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1, h2, h3]
    have ih0 : F0 n = n := Nat.add_right_cancel ih
    rw [ih0]

#print axioms thm_bpd2_induction_d3_r2_pos

theorem thm_bpd2_induction_d3_r3_pos (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, Nat.succ (F0 n) = Nat.succ n := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1, h2, h3]
    injection ih with ih0
    rw [ih0]

#print axioms thm_bpd2_induction_d3_r3_pos

theorem thm_bpd2_induction_d3_r4_pos (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) : ∀ n : Nat, (F0 n, true) = (n, true) := by
  intro n
  induction n with
  | zero => rw [h0]
  | succ n ih =>
    rw [h1, h2, h3]
    injection ih with ih0 _
    rw [ih0]

#print axioms thm_bpd2_induction_d3_r4_pos
