/- BPD-LG-01 v2 negative refutations (¬ goal); kernel-checked with #print axioms -/

theorem neg_thm_bpd2_exact_d1_r1_del0 : ¬ (∀ (P0 P1 Q0 Q1 G D0 D1 D2 : Prop) (hq0 : Q0) (hs1 : P0 → P1) (hjoin : P1 → Q1 → G) (hb1 : Q0 → Q1) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : G → D0), G) := by
  intro h_all
  exact h_all False False True True False False False False True.intro (fun hf => False.elim hf) (fun hf _ => False.elim hf) (fun _ => True.intro) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)

#print axioms neg_thm_bpd2_exact_d1_r1_del0

theorem neg_thm_bpd2_exact_d1_r1_del1 : ¬ (∀ (P0 P1 Q0 Q1 G D0 D1 D2 : Prop) (hq0 : Q0) (hs1 : P0 → P1) (hjoin : P1 → Q1 → G) (h0 : P0) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : G → D0), G) := by
  intro h_all
  exact h_all True True True False False False False False True.intro (fun _ => True.intro) (fun _ hqf => False.elim hqf) True.intro (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)

#print axioms neg_thm_bpd2_exact_d1_r1_del1

theorem neg_thm_bpd2_rw_d2_r1_del0 : ¬ (∀ (x0 x1 x2 x3 d0 d1 d2 : Nat) (h1 : x1 = x2) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), x0 + 1 = x3 + 1) := by
  intro h_all
  have h_eq := h_all 0 1 1 1 0 0 0 rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d2_r1_del0

theorem neg_thm_bpd2_rw_d2_r1_del1 : ¬ (∀ (x0 x1 x2 x3 d0 d1 d2 : Nat) (h0 : x0 = x1) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), x0 + 1 = x3 + 1) := by
  intro h_all
  have h_eq := h_all 0 0 1 1 0 0 0 rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d2_r1_del1

theorem neg_thm_bpd2_rw_d2_r1_del2 : ¬ (∀ (x0 x1 x2 x3 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), x0 + 1 = x3 + 1) := by
  intro h_all
  have h_eq := h_all 0 0 0 1 0 0 0 rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d2_r1_del2

theorem neg_thm_bpd2_rw_d2_r5_del0 : ¬ (∀ (x0 x1 x2 x3 d0 d1 d2 : Nat) (h1 : x1 = x2) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), Option.some x0 = Option.some x3) := by
  intro h_all
  have h_eq := h_all 0 1 1 1 0 0 0 rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d2_r5_del0

theorem neg_thm_bpd2_rw_d2_r5_del1 : ¬ (∀ (x0 x1 x2 x3 d0 d1 d2 : Nat) (h0 : x0 = x1) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), Option.some x0 = Option.some x3) := by
  intro h_all
  have h_eq := h_all 0 0 1 1 0 0 0 rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d2_r5_del1

theorem neg_thm_bpd2_rw_d2_r5_del2 : ¬ (∀ (x0 x1 x2 x3 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), Option.some x0 = Option.some x3) := by
  intro h_all
  have h_eq := h_all 0 0 0 1 0 0 0 rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d2_r5_del2

theorem neg_thm_bpd2_rcases_d1_r0_del0 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h1 : P0 → (P1 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P1 → (D0 ∧ D2)), (P1 ∧ True)) := by
  intro h_all
  rcases h_all False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d1_r0_del0

theorem neg_thm_bpd2_rcases_d1_r0_del1 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h0 : (P0 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P1 → (D0 ∧ D2)), (P1 ∧ True)) := by
  intro h_all
  rcases h_all True False False False False ⟨True.intro, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d1_r0_del1

theorem neg_thm_bpd2_rcases_d2_r1_del0 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h1 : P0 → (True ∧ P1)) (h2 : P1 → (True ∧ P2)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), (True ∧ P2)) := by
  intro h_all
  rcases h_all False False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r1_del0

theorem neg_thm_bpd2_rcases_d2_r1_del1 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : (True ∧ P0)) (h2 : P1 → (True ∧ P2)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), (True ∧ P2)) := by
  intro h_all
  rcases h_all True False False False False False ⟨True.intro, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r1_del1

theorem neg_thm_bpd2_rcases_d2_r1_del2 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : (True ∧ P0)) (h1 : P0 → (True ∧ P1)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), (True ∧ P2)) := by
  intro h_all
  rcases h_all True True False False False False ⟨True.intro, True.intro⟩ (fun _ => ⟨True.intro, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r1_del2

theorem neg_thm_bpd2_rcases_d2_r3_del0 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h1 : P0 → Exists (fun (_ : Bool) => P1)) (h2 : P1 → Exists (fun (_ : Bool) => P2)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), Exists (fun (_ : Bool) => P2)) := by
  intro h_all
  rcases h_all False False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r3_del0

theorem neg_thm_bpd2_rcases_d2_r3_del1 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Bool) => P0)) (h2 : P1 → Exists (fun (_ : Bool) => P2)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), Exists (fun (_ : Bool) => P2)) := by
  intro h_all
  rcases h_all True False False False False False ⟨true, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r3_del1

theorem neg_thm_bpd2_rcases_d2_r3_del2 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Bool) => P0)) (h1 : P0 → Exists (fun (_ : Bool) => P1)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), Exists (fun (_ : Bool) => P2)) := by
  intro h_all
  rcases h_all True True False False False False ⟨true, True.intro⟩ (fun _ => ⟨true, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r3_del2

theorem neg_thm_bpd2_rcases_d3_r1_del0 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h1 : P0 → (True ∧ P1)) (h2 : P1 → (True ∧ P2)) (h3 : P2 → (True ∧ P3)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), (True ∧ P3)) := by
  intro h_all
  rcases h_all False False False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r1_del0

theorem neg_thm_bpd2_rcases_d3_r1_del1 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : (True ∧ P0)) (h2 : P1 → (True ∧ P2)) (h3 : P2 → (True ∧ P3)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), (True ∧ P3)) := by
  intro h_all
  rcases h_all True False False False False False False ⟨True.intro, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r1_del1

theorem neg_thm_bpd2_rcases_d3_r1_del2 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : (True ∧ P0)) (h1 : P0 → (True ∧ P1)) (h3 : P2 → (True ∧ P3)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), (True ∧ P3)) := by
  intro h_all
  rcases h_all True True False False False False False ⟨True.intro, True.intro⟩ (fun _ => ⟨True.intro, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r1_del2

theorem neg_thm_bpd2_rcases_d3_r1_del3 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : (True ∧ P0)) (h1 : P0 → (True ∧ P1)) (h2 : P1 → (True ∧ P2)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), (True ∧ P3)) := by
  intro h_all
  rcases h_all True True True False False False False ⟨True.intro, True.intro⟩ (fun _ => ⟨True.intro, True.intro⟩) (fun _ => ⟨True.intro, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r1_del3

theorem neg_thm_bpd2_induction_d3_r1_del0 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, [F0 n] = [n]) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun k => k + 2) (fun k => k + 2) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r1_del0

theorem neg_thm_bpd2_induction_d3_r1_del1 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, [F0 n] = [n]) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 1) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r1_del1

theorem neg_thm_bpd2_induction_d3_r1_del2 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, [F0 n] = [n]) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r1_del2

theorem neg_thm_bpd2_induction_d3_r1_del3 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, [F0 n] = [n]) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r1_del3
