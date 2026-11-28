/- BPD-LG-01 v2 negative refutations (¬ goal); kernel-checked with #print axioms -/

theorem neg_thm_bpd2_exact_d1_r2_del0 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h1 : P0 ∧ True → P1) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P1 → D0), P1 ∧ True) := by
  intro h_all
  exact (h_all False False False False False (fun hp => False.elim hp.1) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).1

#print axioms neg_thm_bpd2_exact_d1_r2_del0

theorem neg_thm_bpd2_exact_d1_r2_del1 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h0 : P0) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P1 → D0), P1 ∧ True) := by
  intro h_all
  exact (h_all True False False False False True.intro (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).1

#print axioms neg_thm_bpd2_exact_d1_r2_del1

theorem neg_thm_bpd2_exact_d1_r3_del0 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h1 : P0 ∨ False → P1) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P1 → D0), P1 ∨ False) := by
  intro h_all
  exact ((h_all False False False False False (fun hp => False.elim (hp.elim (fun a => a) (fun b => b))) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).elim (fun a => a) (fun b => b))

#print axioms neg_thm_bpd2_exact_d1_r3_del0

theorem neg_thm_bpd2_exact_d1_r3_del1 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h0 : P0) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P1 → D0), P1 ∨ False) := by
  intro h_all
  exact ((h_all True False False False False True.intro (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).elim (fun a => a) (fun b => b))

#print axioms neg_thm_bpd2_exact_d1_r3_del1

theorem neg_thm_bpd2_exact_d1_r4_del0 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h1 : P0 ↔ P1) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P1 → D0), True ↔ P1) := by
  intro h_all
  exact ((h_all False False False False False Iff.rfl (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).mp True.intro)

#print axioms neg_thm_bpd2_exact_d1_r4_del0

theorem neg_thm_bpd2_exact_d1_r4_del1 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h0 : P0) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P1 → D0), True ↔ P1) := by
  intro h_all
  exact ((h_all True False False False False True.intro (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).mp True.intro)

#print axioms neg_thm_bpd2_exact_d1_r4_del1

theorem neg_thm_bpd2_exact_d1_r5_del0 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h1 : P0 → Unit → P1) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P1 → D0), Unit → P1) := by
  intro h_all
  exact ((h_all False False False False False (fun hf _ => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)) ())

#print axioms neg_thm_bpd2_exact_d1_r5_del0

theorem neg_thm_bpd2_exact_d1_r5_del1 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h0 : Unit → P0) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P1 → D0), Unit → P1) := by
  intro h_all
  exact ((h_all True False False False False (fun _ => True.intro) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)) ())

#print axioms neg_thm_bpd2_exact_d1_r5_del1

theorem neg_thm_bpd2_exact_d2_r0_del0 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h1 : P0 → P1) (h2 : P1 → P2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P2 → D0), P2) := by
  intro h_all
  exact (h_all False False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf))

#print axioms neg_thm_bpd2_exact_d2_r0_del0

theorem neg_thm_bpd2_exact_d2_r0_del1 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : P0) (h2 : P1 → P2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P2 → D0), P2) := by
  intro h_all
  exact (h_all True False False False False False True.intro (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf))

#print axioms neg_thm_bpd2_exact_d2_r0_del1

theorem neg_thm_bpd2_exact_d2_r0_del2 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 → P1) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P2 → D0), P2) := by
  intro h_all
  exact (h_all True True False False False False True.intro (fun _ => True.intro) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf))

#print axioms neg_thm_bpd2_exact_d2_r0_del2

theorem neg_thm_bpd2_exact_d2_r1_del0 : ¬ (∀ (P0 P1 P2 Q0 Q1 Q2 G D0 D1 D2 : Prop) (hq0 : Q0) (hs1 : P0 → P1) (hs2 : P1 → P2) (hjoin : P2 → Q2 → G) (hb1 : Q0 → Q1) (hb2 : Q1 → Q2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : G → D0), G) := by
  intro h_all
  exact h_all False False False True True True False False False False True.intro (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf _ => False.elim hf) (fun _ => True.intro) (fun _ => True.intro) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)

#print axioms neg_thm_bpd2_exact_d2_r1_del0

theorem neg_thm_bpd2_exact_d2_r1_del1 : ¬ (∀ (P0 P1 P2 Q0 Q1 Q2 G D0 D1 D2 : Prop) (hq0 : Q0) (hs1 : P0 → P1) (hs2 : P1 → P2) (hjoin : P2 → Q2 → G) (h0 : P0) (hb2 : Q1 → Q2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : G → D0), G) := by
  intro h_all
  exact h_all True True True True False False False False False False True.intro (fun _ => True.intro) (fun _ => True.intro) (fun _ hqf => False.elim hqf) True.intro (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)

#print axioms neg_thm_bpd2_exact_d2_r1_del1

theorem neg_thm_bpd2_exact_d2_r1_del2 : ¬ (∀ (P0 P1 P2 Q0 Q1 Q2 G D0 D1 D2 : Prop) (hq0 : Q0) (hs1 : P0 → P1) (hs2 : P1 → P2) (hjoin : P2 → Q2 → G) (h0 : P0) (hb1 : Q0 → Q1) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : G → D0), G) := by
  intro h_all
  exact h_all True True True True True False False False False False True.intro (fun _ => True.intro) (fun _ => True.intro) (fun _ hqf => False.elim hqf) True.intro (fun _ => True.intro) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)

#print axioms neg_thm_bpd2_exact_d2_r1_del2

theorem neg_thm_bpd2_exact_d2_r2_del0 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h1 : P0 ∧ True → P1) (h2 : P1 ∧ True → P2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P2 → D0), P2 ∧ True) := by
  intro h_all
  exact (h_all False False False False False False (fun hp => False.elim hp.1) (fun hp => False.elim hp.1) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).1

#print axioms neg_thm_bpd2_exact_d2_r2_del0

theorem neg_thm_bpd2_exact_d2_r2_del1 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : P0) (h2 : P1 ∧ True → P2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P2 → D0), P2 ∧ True) := by
  intro h_all
  exact (h_all True False False False False False True.intro (fun hp => False.elim hp.1) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).1

#print axioms neg_thm_bpd2_exact_d2_r2_del1

theorem neg_thm_bpd2_exact_d2_r2_del2 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ∧ True → P1) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P2 → D0), P2 ∧ True) := by
  intro h_all
  exact (h_all True True False False False False True.intro (fun _ => True.intro) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).1

#print axioms neg_thm_bpd2_exact_d2_r2_del2

theorem neg_thm_bpd2_exact_d2_r4_del0 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h1 : P0 ↔ P1) (h2 : P1 ↔ P2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P2 → D0), True ↔ P2) := by
  intro h_all
  exact ((h_all False False False False False False Iff.rfl Iff.rfl (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).mp True.intro)

#print axioms neg_thm_bpd2_exact_d2_r4_del0

theorem neg_thm_bpd2_exact_d2_r4_del1 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : P0) (h2 : P1 ↔ P2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P2 → D0), True ↔ P2) := by
  intro h_all
  exact ((h_all True False False False False False True.intro Iff.rfl (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).mp True.intro)

#print axioms neg_thm_bpd2_exact_d2_r4_del1

theorem neg_thm_bpd2_exact_d2_r4_del2 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ↔ P1) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P2 → D0), True ↔ P2) := by
  intro h_all
  exact ((h_all True True False False False False True.intro Iff.rfl (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).mp True.intro)

#print axioms neg_thm_bpd2_exact_d2_r4_del2

theorem neg_thm_bpd2_exact_d2_r5_del0 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h1 : P0 → Unit → P1) (h2 : P1 → Unit → P2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P2 → D0), Unit → P2) := by
  intro h_all
  exact ((h_all False False False False False False (fun hf _ => False.elim hf) (fun hf _ => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)) ())

#print axioms neg_thm_bpd2_exact_d2_r5_del0

theorem neg_thm_bpd2_exact_d2_r5_del1 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : Unit → P0) (h2 : P1 → Unit → P2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P2 → D0), Unit → P2) := by
  intro h_all
  exact ((h_all True False False False False False (fun _ => True.intro) (fun hf _ => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)) ())

#print axioms neg_thm_bpd2_exact_d2_r5_del1

theorem neg_thm_bpd2_exact_d2_r5_del2 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : Unit → P0) (h1 : P0 → Unit → P1) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P2 → D0), Unit → P2) := by
  intro h_all
  exact ((h_all True True False False False False (fun _ => True.intro) (fun _ _ => True.intro) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)) ())

#print axioms neg_thm_bpd2_exact_d2_r5_del2

theorem neg_thm_bpd2_exact_d3_r1_del0 : ¬ (∀ (P0 P1 P2 P3 Q0 Q1 Q2 Q3 G D0 D1 D2 : Prop) (hq0 : Q0) (hs1 : P0 → P1) (hs2 : P1 → P2) (hs3 : P2 → P3) (hjoin : P3 → Q3 → G) (hb1 : Q0 → Q1) (hb2 : Q1 → Q2) (hb3 : Q2 → Q3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : G → D0), G) := by
  intro h_all
  exact h_all False False False False True True True True False False False False True.intro (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf _ => False.elim hf) (fun _ => True.intro) (fun _ => True.intro) (fun _ => True.intro) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)

#print axioms neg_thm_bpd2_exact_d3_r1_del0

theorem neg_thm_bpd2_exact_d3_r1_del1 : ¬ (∀ (P0 P1 P2 P3 Q0 Q1 Q2 Q3 G D0 D1 D2 : Prop) (hq0 : Q0) (hs1 : P0 → P1) (hs2 : P1 → P2) (hs3 : P2 → P3) (hjoin : P3 → Q3 → G) (h0 : P0) (hb2 : Q1 → Q2) (hb3 : Q2 → Q3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : G → D0), G) := by
  intro h_all
  exact h_all True True True True True False False False False False False False True.intro (fun _ => True.intro) (fun _ => True.intro) (fun _ => True.intro) (fun _ hqf => False.elim hqf) True.intro (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)

#print axioms neg_thm_bpd2_exact_d3_r1_del1

theorem neg_thm_bpd2_exact_d3_r1_del2 : ¬ (∀ (P0 P1 P2 P3 Q0 Q1 Q2 Q3 G D0 D1 D2 : Prop) (hq0 : Q0) (hs1 : P0 → P1) (hs2 : P1 → P2) (hs3 : P2 → P3) (hjoin : P3 → Q3 → G) (h0 : P0) (hb1 : Q0 → Q1) (hb3 : Q2 → Q3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : G → D0), G) := by
  intro h_all
  exact h_all True True True True True True False False False False False False True.intro (fun _ => True.intro) (fun _ => True.intro) (fun _ => True.intro) (fun _ hqf => False.elim hqf) True.intro (fun _ => True.intro) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)

#print axioms neg_thm_bpd2_exact_d3_r1_del2

theorem neg_thm_bpd2_exact_d3_r1_del3 : ¬ (∀ (P0 P1 P2 P3 Q0 Q1 Q2 Q3 G D0 D1 D2 : Prop) (hq0 : Q0) (hs1 : P0 → P1) (hs2 : P1 → P2) (hs3 : P2 → P3) (hjoin : P3 → Q3 → G) (h0 : P0) (hb1 : Q0 → Q1) (hb2 : Q1 → Q2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : G → D0), G) := by
  intro h_all
  exact h_all True True True True True True True False False False False False True.intro (fun _ => True.intro) (fun _ => True.intro) (fun _ => True.intro) (fun _ hqf => False.elim hqf) True.intro (fun _ => True.intro) (fun _ => True.intro) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)

#print axioms neg_thm_bpd2_exact_d3_r1_del3

theorem neg_thm_bpd2_exact_d3_r2_del0 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h1 : P0 ∧ True → P1) (h2 : P1 ∧ True → P2) (h3 : P2 ∧ True → P3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), P3 ∧ True) := by
  intro h_all
  exact (h_all False False False False False False False (fun hp => False.elim hp.1) (fun hp => False.elim hp.1) (fun hp => False.elim hp.1) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).1

#print axioms neg_thm_bpd2_exact_d3_r2_del0

theorem neg_thm_bpd2_exact_d3_r2_del1 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : P0) (h2 : P1 ∧ True → P2) (h3 : P2 ∧ True → P3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), P3 ∧ True) := by
  intro h_all
  exact (h_all True False False False False False False True.intro (fun hp => False.elim hp.1) (fun hp => False.elim hp.1) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).1

#print axioms neg_thm_bpd2_exact_d3_r2_del1

theorem neg_thm_bpd2_exact_d3_r2_del2 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ∧ True → P1) (h3 : P2 ∧ True → P3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), P3 ∧ True) := by
  intro h_all
  exact (h_all True True False False False False False True.intro (fun _ => True.intro) (fun hp => False.elim hp.1) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).1

#print axioms neg_thm_bpd2_exact_d3_r2_del2

theorem neg_thm_bpd2_exact_d3_r2_del3 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ∧ True → P1) (h2 : P1 ∧ True → P2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), P3 ∧ True) := by
  intro h_all
  exact (h_all True True True False False False False True.intro (fun _ => True.intro) (fun _ => True.intro) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).1

#print axioms neg_thm_bpd2_exact_d3_r2_del3

theorem neg_thm_bpd2_exact_d3_r3_del0 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h1 : P0 ∨ False → P1) (h2 : P1 ∨ False → P2) (h3 : P2 ∨ False → P3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), P3 ∨ False) := by
  intro h_all
  exact ((h_all False False False False False False False (fun hp => False.elim (hp.elim (fun a => a) (fun b => b))) (fun hp => False.elim (hp.elim (fun a => a) (fun b => b))) (fun hp => False.elim (hp.elim (fun a => a) (fun b => b))) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).elim (fun a => a) (fun b => b))

#print axioms neg_thm_bpd2_exact_d3_r3_del0

theorem neg_thm_bpd2_exact_d3_r3_del1 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : P0) (h2 : P1 ∨ False → P2) (h3 : P2 ∨ False → P3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), P3 ∨ False) := by
  intro h_all
  exact ((h_all True False False False False False False True.intro (fun hp => False.elim (hp.elim (fun a => a) (fun b => b))) (fun hp => False.elim (hp.elim (fun a => a) (fun b => b))) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).elim (fun a => a) (fun b => b))

#print axioms neg_thm_bpd2_exact_d3_r3_del1

theorem neg_thm_bpd2_exact_d3_r3_del2 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ∨ False → P1) (h3 : P2 ∨ False → P3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), P3 ∨ False) := by
  intro h_all
  exact ((h_all True True False False False False False True.intro (fun _ => True.intro) (fun hp => False.elim (hp.elim (fun a => a) (fun b => b))) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).elim (fun a => a) (fun b => b))

#print axioms neg_thm_bpd2_exact_d3_r3_del2

theorem neg_thm_bpd2_exact_d3_r3_del3 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ∨ False → P1) (h2 : P1 ∨ False → P2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), P3 ∨ False) := by
  intro h_all
  exact ((h_all True True True False False False False True.intro (fun _ => True.intro) (fun _ => True.intro) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).elim (fun a => a) (fun b => b))

#print axioms neg_thm_bpd2_exact_d3_r3_del3

theorem neg_thm_bpd2_exact_d3_r4_del0 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h1 : P0 ↔ P1) (h2 : P1 ↔ P2) (h3 : P2 ↔ P3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), True ↔ P3) := by
  intro h_all
  exact ((h_all False False False False False False False Iff.rfl Iff.rfl Iff.rfl (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).mp True.intro)

#print axioms neg_thm_bpd2_exact_d3_r4_del0

theorem neg_thm_bpd2_exact_d3_r4_del1 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : P0) (h2 : P1 ↔ P2) (h3 : P2 ↔ P3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), True ↔ P3) := by
  intro h_all
  exact ((h_all True False False False False False False True.intro Iff.rfl Iff.rfl (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).mp True.intro)

#print axioms neg_thm_bpd2_exact_d3_r4_del1

theorem neg_thm_bpd2_exact_d3_r4_del2 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ↔ P1) (h3 : P2 ↔ P3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), True ↔ P3) := by
  intro h_all
  exact ((h_all True True False False False False False True.intro Iff.rfl Iff.rfl (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).mp True.intro)

#print axioms neg_thm_bpd2_exact_d3_r4_del2

theorem neg_thm_bpd2_exact_d3_r4_del3 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : P0) (h1 : P0 ↔ P1) (h2 : P1 ↔ P2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), True ↔ P3) := by
  intro h_all
  exact ((h_all True True True False False False False True.intro Iff.rfl Iff.rfl (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)).mp True.intro)

#print axioms neg_thm_bpd2_exact_d3_r4_del3

theorem neg_thm_bpd2_exact_d3_r5_del0 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h1 : P0 → Unit → P1) (h2 : P1 → Unit → P2) (h3 : P2 → Unit → P3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), Unit → P3) := by
  intro h_all
  exact ((h_all False False False False False False False (fun hf _ => False.elim hf) (fun hf _ => False.elim hf) (fun hf _ => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)) ())

#print axioms neg_thm_bpd2_exact_d3_r5_del0

theorem neg_thm_bpd2_exact_d3_r5_del1 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : Unit → P0) (h2 : P1 → Unit → P2) (h3 : P2 → Unit → P3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), Unit → P3) := by
  intro h_all
  exact ((h_all True False False False False False False (fun _ => True.intro) (fun hf _ => False.elim hf) (fun hf _ => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)) ())

#print axioms neg_thm_bpd2_exact_d3_r5_del1

theorem neg_thm_bpd2_exact_d3_r5_del2 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : Unit → P0) (h1 : P0 → Unit → P1) (h3 : P2 → Unit → P3) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), Unit → P3) := by
  intro h_all
  exact ((h_all True True False False False False False (fun _ => True.intro) (fun _ _ => True.intro) (fun hf _ => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)) ())

#print axioms neg_thm_bpd2_exact_d3_r5_del2

theorem neg_thm_bpd2_exact_d3_r5_del3 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : Unit → P0) (h1 : P0 → Unit → P1) (h2 : P1 → Unit → P2) (hd1 : D0 → D1) (hd2 : D1 → D2) (hd3 : P3 → D0), Unit → P3) := by
  intro h_all
  exact ((h_all True True True False False False False (fun _ => True.intro) (fun _ _ => True.intro) (fun _ _ => True.intro) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf)) ())

#print axioms neg_thm_bpd2_exact_d3_r5_del3

theorem neg_thm_bpd2_rw_d1_r0_del0 : ¬ (∀ (x0 x1 x2 d0 d1 d2 : Nat) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), Nat.succ x0 = Nat.succ x2) := by
  intro h_all
  have h_eq := h_all 0 1 1 0 0 0 rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d1_r0_del0

theorem neg_thm_bpd2_rw_d1_r0_del1 : ¬ (∀ (x0 x1 x2 d0 d1 d2 : Nat) (h0 : x0 = x1) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), Nat.succ x0 = Nat.succ x2) := by
  intro h_all
  have h_eq := h_all 0 0 1 0 0 0 rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d1_r0_del1

theorem neg_thm_bpd2_rw_d1_r1_del0 : ¬ (∀ (x0 x1 x2 d0 d1 d2 : Nat) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), x0 + 1 = x2 + 1) := by
  intro h_all
  have h_eq := h_all 0 1 1 0 0 0 rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d1_r1_del0

theorem neg_thm_bpd2_rw_d1_r1_del1 : ¬ (∀ (x0 x1 x2 d0 d1 d2 : Nat) (h0 : x0 = x1) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), x0 + 1 = x2 + 1) := by
  intro h_all
  have h_eq := h_all 0 0 1 0 0 0 rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d1_r1_del1

theorem neg_thm_bpd2_rw_d1_r2_del0 : ¬ (∀ (x0 x1 x2 d0 d1 d2 : Nat) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), x0 * 2 + 1 = x2 * 2 + 1) := by
  intro h_all
  have h_eq := h_all 0 1 1 0 0 0 rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d1_r2_del0

theorem neg_thm_bpd2_rw_d1_r2_del1 : ¬ (∀ (x0 x1 x2 d0 d1 d2 : Nat) (h0 : x0 = x1) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), x0 * 2 + 1 = x2 * 2 + 1) := by
  intro h_all
  have h_eq := h_all 0 0 1 0 0 0 rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d1_r2_del1

theorem neg_thm_bpd2_rw_d1_r3_del0 : ¬ (∀ (x0 x1 x2 d0 d1 d2 : Nat) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), (x0, 0) = (x2, 0)) := by
  intro h_all
  have h_eq := h_all 0 1 1 0 0 0 rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d1_r3_del0

theorem neg_thm_bpd2_rw_d1_r3_del1 : ¬ (∀ (x0 x1 x2 d0 d1 d2 : Nat) (h0 : x0 = x1) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), (x0, 0) = (x2, 0)) := by
  intro h_all
  have h_eq := h_all 0 0 1 0 0 0 rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d1_r3_del1

theorem neg_thm_bpd2_rw_d1_r4_del0 : ¬ (∀ (x0 x1 x2 d0 d1 d2 : Nat) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), [x0] = [x2]) := by
  intro h_all
  have h_eq := h_all 0 1 1 0 0 0 rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d1_r4_del0

theorem neg_thm_bpd2_rw_d1_r4_del1 : ¬ (∀ (x0 x1 x2 d0 d1 d2 : Nat) (h0 : x0 = x1) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), [x0] = [x2]) := by
  intro h_all
  have h_eq := h_all 0 0 1 0 0 0 rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d1_r4_del1

theorem neg_thm_bpd2_rw_d1_r5_del0 : ¬ (∀ (x0 x1 x2 d0 d1 d2 : Nat) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), Option.some x0 = Option.some x2) := by
  intro h_all
  have h_eq := h_all 0 1 1 0 0 0 rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d1_r5_del0

theorem neg_thm_bpd2_rw_d1_r5_del1 : ¬ (∀ (x0 x1 x2 d0 d1 d2 : Nat) (h0 : x0 = x1) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), Option.some x0 = Option.some x2) := by
  intro h_all
  have h_eq := h_all 0 0 1 0 0 0 rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d1_r5_del1

theorem neg_thm_bpd2_rw_d2_r0_del0 : ¬ (∀ (x0 x1 x2 x3 d0 d1 d2 : Nat) (h1 : x1 = x2) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), Nat.succ x0 = Nat.succ x3) := by
  intro h_all
  have h_eq := h_all 0 1 1 1 0 0 0 rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d2_r0_del0

theorem neg_thm_bpd2_rw_d2_r0_del1 : ¬ (∀ (x0 x1 x2 x3 d0 d1 d2 : Nat) (h0 : x0 = x1) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), Nat.succ x0 = Nat.succ x3) := by
  intro h_all
  have h_eq := h_all 0 0 1 1 0 0 0 rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d2_r0_del1

theorem neg_thm_bpd2_rw_d2_r0_del2 : ¬ (∀ (x0 x1 x2 x3 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), Nat.succ x0 = Nat.succ x3) := by
  intro h_all
  have h_eq := h_all 0 0 0 1 0 0 0 rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d2_r0_del2

theorem neg_thm_bpd2_rw_d2_r4_del0 : ¬ (∀ (x0 x1 x2 x3 d0 d1 d2 : Nat) (h1 : x1 = x2) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), [x0] = [x3]) := by
  intro h_all
  have h_eq := h_all 0 1 1 1 0 0 0 rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d2_r4_del0

theorem neg_thm_bpd2_rw_d2_r4_del1 : ¬ (∀ (x0 x1 x2 x3 d0 d1 d2 : Nat) (h0 : x0 = x1) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), [x0] = [x3]) := by
  intro h_all
  have h_eq := h_all 0 0 1 1 0 0 0 rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d2_r4_del1

theorem neg_thm_bpd2_rw_d2_r4_del2 : ¬ (∀ (x0 x1 x2 x3 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), [x0] = [x3]) := by
  intro h_all
  have h_eq := h_all 0 0 0 1 0 0 0 rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d2_r4_del2

theorem neg_thm_bpd2_rw_d3_r2_del0 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h1 : x1 = x2) (h2 : x2 = x3) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), x0 * 2 + 1 = x4 * 2 + 1) := by
  intro h_all
  have h_eq := h_all 0 1 1 1 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r2_del0

theorem neg_thm_bpd2_rw_d3_r2_del1 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h2 : x2 = x3) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), x0 * 2 + 1 = x4 * 2 + 1) := by
  intro h_all
  have h_eq := h_all 0 0 1 1 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r2_del1

theorem neg_thm_bpd2_rw_d3_r2_del2 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), x0 * 2 + 1 = x4 * 2 + 1) := by
  intro h_all
  have h_eq := h_all 0 0 0 1 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r2_del2

theorem neg_thm_bpd2_rw_d3_r2_del3 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), x0 * 2 + 1 = x4 * 2 + 1) := by
  intro h_all
  have h_eq := h_all 0 0 0 0 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r2_del3

theorem neg_thm_bpd2_rw_d3_r3_del0 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h1 : x1 = x2) (h2 : x2 = x3) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), (x0, 0) = (x4, 0)) := by
  intro h_all
  have h_eq := h_all 0 1 1 1 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r3_del0

theorem neg_thm_bpd2_rw_d3_r3_del1 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h2 : x2 = x3) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), (x0, 0) = (x4, 0)) := by
  intro h_all
  have h_eq := h_all 0 0 1 1 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r3_del1

theorem neg_thm_bpd2_rw_d3_r3_del2 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), (x0, 0) = (x4, 0)) := by
  intro h_all
  have h_eq := h_all 0 0 0 1 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r3_del2

theorem neg_thm_bpd2_rw_d3_r3_del3 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), (x0, 0) = (x4, 0)) := by
  intro h_all
  have h_eq := h_all 0 0 0 0 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r3_del3

theorem neg_thm_bpd2_rw_d3_r4_del0 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h1 : x1 = x2) (h2 : x2 = x3) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), [x0] = [x4]) := by
  intro h_all
  have h_eq := h_all 0 1 1 1 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r4_del0

theorem neg_thm_bpd2_rw_d3_r4_del1 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h2 : x2 = x3) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), [x0] = [x4]) := by
  intro h_all
  have h_eq := h_all 0 0 1 1 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r4_del1

theorem neg_thm_bpd2_rw_d3_r4_del2 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), [x0] = [x4]) := by
  intro h_all
  have h_eq := h_all 0 0 0 1 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r4_del2

theorem neg_thm_bpd2_rw_d3_r4_del3 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), [x0] = [x4]) := by
  intro h_all
  have h_eq := h_all 0 0 0 0 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r4_del3

theorem neg_thm_bpd2_rw_d3_r5_del0 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h1 : x1 = x2) (h2 : x2 = x3) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), Option.some x0 = Option.some x4) := by
  intro h_all
  have h_eq := h_all 0 1 1 1 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r5_del0

theorem neg_thm_bpd2_rw_d3_r5_del1 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h2 : x2 = x3) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), Option.some x0 = Option.some x4) := by
  intro h_all
  have h_eq := h_all 0 0 1 1 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r5_del1

theorem neg_thm_bpd2_rw_d3_r5_del2 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h3 : x3 = x4) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), Option.some x0 = Option.some x4) := by
  intro h_all
  have h_eq := h_all 0 0 0 1 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r5_del2

theorem neg_thm_bpd2_rw_d3_r5_del3 : ¬ (∀ (x0 x1 x2 x3 x4 d0 d1 d2 : Nat) (h0 : x0 = x1) (h1 : x1 = x2) (h2 : x2 = x3) (hd1 : d0 + 1 = d1 + 1) (hd2 : d1 + 2 = d2 + 2) (hd3 : d0 + 3 = d2 + 3), Option.some x0 = Option.some x4) := by
  intro h_all
  have h_eq := h_all 0 0 0 0 1 0 0 0 rfl rfl rfl rfl rfl rfl
  exact absurd h_eq (by decide)

#print axioms neg_thm_bpd2_rw_d3_r5_del3

theorem neg_thm_bpd2_rcases_d1_r1_del0 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h1 : P0 → (True ∧ P1)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P1 → (D0 ∧ D2)), (True ∧ P1)) := by
  intro h_all
  rcases h_all False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d1_r1_del0

theorem neg_thm_bpd2_rcases_d1_r1_del1 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h0 : (True ∧ P0)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P1 → (D0 ∧ D2)), (True ∧ P1)) := by
  intro h_all
  rcases h_all True False False False False ⟨True.intro, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d1_r1_del1

theorem neg_thm_bpd2_rcases_d1_r3_del0 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h1 : P0 → Exists (fun (_ : Bool) => P1)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P1 → (D0 ∧ D2)), Exists (fun (_ : Bool) => P1)) := by
  intro h_all
  rcases h_all False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d1_r3_del0

theorem neg_thm_bpd2_rcases_d1_r3_del1 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Bool) => P0)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P1 → (D0 ∧ D2)), Exists (fun (_ : Bool) => P1)) := by
  intro h_all
  rcases h_all True False False False False ⟨true, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d1_r3_del1

theorem neg_thm_bpd2_rcases_d1_r4_del0 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h1 : P0 → Exists (fun (_ : Unit) => P1 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P1 → (D0 ∧ D2)), Exists (fun (_ : Unit) => P1 ∧ True)) := by
  intro h_all
  rcases h_all False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d1_r4_del0

theorem neg_thm_bpd2_rcases_d1_r4_del1 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Unit) => P0 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P1 → (D0 ∧ D2)), Exists (fun (_ : Unit) => P1 ∧ True)) := by
  intro h_all
  rcases h_all True False False False False ⟨(), True.intro, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d1_r4_del1

theorem neg_thm_bpd2_rcases_d1_r5_del0 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h1 : P0 → ((P1 ∧ P1) ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P1 → (D0 ∧ D2)), ((P1 ∧ P1) ∧ True)) := by
  intro h_all
  rcases h_all False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨⟨hf_goal, _⟩, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d1_r5_del0

theorem neg_thm_bpd2_rcases_d1_r5_del1 : ¬ (∀ (P0 P1 D0 D1 D2 : Prop) (h0 : ((P0 ∧ P0) ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P1 → (D0 ∧ D2)), ((P1 ∧ P1) ∧ True)) := by
  intro h_all
  rcases h_all True False False False False ⟨⟨True.intro, True.intro⟩, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨⟨hf_goal, _⟩, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d1_r5_del1

theorem neg_thm_bpd2_rcases_d2_r0_del0 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h1 : P0 → (P1 ∧ True)) (h2 : P1 → (P2 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), (P2 ∧ True)) := by
  intro h_all
  rcases h_all False False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r0_del0

theorem neg_thm_bpd2_rcases_d2_r0_del1 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : (P0 ∧ True)) (h2 : P1 → (P2 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), (P2 ∧ True)) := by
  intro h_all
  rcases h_all True False False False False False ⟨True.intro, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r0_del1

theorem neg_thm_bpd2_rcases_d2_r0_del2 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : (P0 ∧ True)) (h1 : P0 → (P1 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), (P2 ∧ True)) := by
  intro h_all
  rcases h_all True True False False False False ⟨True.intro, True.intro⟩ (fun _ => ⟨True.intro, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r0_del2

theorem neg_thm_bpd2_rcases_d2_r2_del0 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h1 : P0 → Exists (fun (_ : Nat) => P1)) (h2 : P1 → Exists (fun (_ : Nat) => P2)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), Exists (fun (_ : Nat) => P2)) := by
  intro h_all
  rcases h_all False False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r2_del0

theorem neg_thm_bpd2_rcases_d2_r2_del1 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Nat) => P0)) (h2 : P1 → Exists (fun (_ : Nat) => P2)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), Exists (fun (_ : Nat) => P2)) := by
  intro h_all
  rcases h_all True False False False False False ⟨0, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r2_del1

theorem neg_thm_bpd2_rcases_d2_r2_del2 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Nat) => P0)) (h1 : P0 → Exists (fun (_ : Nat) => P1)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), Exists (fun (_ : Nat) => P2)) := by
  intro h_all
  rcases h_all True True False False False False ⟨0, True.intro⟩ (fun _ => ⟨0, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r2_del2

theorem neg_thm_bpd2_rcases_d2_r4_del0 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h1 : P0 → Exists (fun (_ : Unit) => P1 ∧ True)) (h2 : P1 → Exists (fun (_ : Unit) => P2 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), Exists (fun (_ : Unit) => P2 ∧ True)) := by
  intro h_all
  rcases h_all False False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r4_del0

theorem neg_thm_bpd2_rcases_d2_r4_del1 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Unit) => P0 ∧ True)) (h2 : P1 → Exists (fun (_ : Unit) => P2 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), Exists (fun (_ : Unit) => P2 ∧ True)) := by
  intro h_all
  rcases h_all True False False False False False ⟨(), True.intro, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r4_del1

theorem neg_thm_bpd2_rcases_d2_r4_del2 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Unit) => P0 ∧ True)) (h1 : P0 → Exists (fun (_ : Unit) => P1 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), Exists (fun (_ : Unit) => P2 ∧ True)) := by
  intro h_all
  rcases h_all True True False False False False ⟨(), True.intro, True.intro⟩ (fun _ => ⟨(), True.intro, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r4_del2

theorem neg_thm_bpd2_rcases_d2_r5_del0 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h1 : P0 → ((P1 ∧ P1) ∧ True)) (h2 : P1 → ((P2 ∧ P2) ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), ((P2 ∧ P2) ∧ True)) := by
  intro h_all
  rcases h_all False False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨⟨hf_goal, _⟩, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r5_del0

theorem neg_thm_bpd2_rcases_d2_r5_del1 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : ((P0 ∧ P0) ∧ True)) (h2 : P1 → ((P2 ∧ P2) ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), ((P2 ∧ P2) ∧ True)) := by
  intro h_all
  rcases h_all True False False False False False ⟨⟨True.intro, True.intro⟩, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨⟨hf_goal, _⟩, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r5_del1

theorem neg_thm_bpd2_rcases_d2_r5_del2 : ¬ (∀ (P0 P1 P2 D0 D1 D2 : Prop) (h0 : ((P0 ∧ P0) ∧ True)) (h1 : P0 → ((P1 ∧ P1) ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P2 → (D0 ∧ D2)), ((P2 ∧ P2) ∧ True)) := by
  intro h_all
  rcases h_all True True False False False False ⟨⟨True.intro, True.intro⟩, True.intro⟩ (fun _ => ⟨⟨True.intro, True.intro⟩, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨⟨hf_goal, _⟩, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d2_r5_del2

theorem neg_thm_bpd2_rcases_d3_r0_del0 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h1 : P0 → (P1 ∧ True)) (h2 : P1 → (P2 ∧ True)) (h3 : P2 → (P3 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), (P3 ∧ True)) := by
  intro h_all
  rcases h_all False False False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r0_del0

theorem neg_thm_bpd2_rcases_d3_r0_del1 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : (P0 ∧ True)) (h2 : P1 → (P2 ∧ True)) (h3 : P2 → (P3 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), (P3 ∧ True)) := by
  intro h_all
  rcases h_all True False False False False False False ⟨True.intro, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r0_del1

theorem neg_thm_bpd2_rcases_d3_r0_del2 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : (P0 ∧ True)) (h1 : P0 → (P1 ∧ True)) (h3 : P2 → (P3 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), (P3 ∧ True)) := by
  intro h_all
  rcases h_all True True False False False False False ⟨True.intro, True.intro⟩ (fun _ => ⟨True.intro, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r0_del2

theorem neg_thm_bpd2_rcases_d3_r0_del3 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : (P0 ∧ True)) (h1 : P0 → (P1 ∧ True)) (h2 : P1 → (P2 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), (P3 ∧ True)) := by
  intro h_all
  rcases h_all True True True False False False False ⟨True.intro, True.intro⟩ (fun _ => ⟨True.intro, True.intro⟩) (fun _ => ⟨True.intro, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r0_del3

theorem neg_thm_bpd2_rcases_d3_r2_del0 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h1 : P0 → Exists (fun (_ : Nat) => P1)) (h2 : P1 → Exists (fun (_ : Nat) => P2)) (h3 : P2 → Exists (fun (_ : Nat) => P3)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), Exists (fun (_ : Nat) => P3)) := by
  intro h_all
  rcases h_all False False False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r2_del0

theorem neg_thm_bpd2_rcases_d3_r2_del1 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Nat) => P0)) (h2 : P1 → Exists (fun (_ : Nat) => P2)) (h3 : P2 → Exists (fun (_ : Nat) => P3)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), Exists (fun (_ : Nat) => P3)) := by
  intro h_all
  rcases h_all True False False False False False False ⟨0, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r2_del1

theorem neg_thm_bpd2_rcases_d3_r2_del2 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Nat) => P0)) (h1 : P0 → Exists (fun (_ : Nat) => P1)) (h3 : P2 → Exists (fun (_ : Nat) => P3)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), Exists (fun (_ : Nat) => P3)) := by
  intro h_all
  rcases h_all True True False False False False False ⟨0, True.intro⟩ (fun _ => ⟨0, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r2_del2

theorem neg_thm_bpd2_rcases_d3_r2_del3 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Nat) => P0)) (h1 : P0 → Exists (fun (_ : Nat) => P1)) (h2 : P1 → Exists (fun (_ : Nat) => P2)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), Exists (fun (_ : Nat) => P3)) := by
  intro h_all
  rcases h_all True True True False False False False ⟨0, True.intro⟩ (fun _ => ⟨0, True.intro⟩) (fun _ => ⟨0, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r2_del3

theorem neg_thm_bpd2_rcases_d3_r4_del0 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h1 : P0 → Exists (fun (_ : Unit) => P1 ∧ True)) (h2 : P1 → Exists (fun (_ : Unit) => P2 ∧ True)) (h3 : P2 → Exists (fun (_ : Unit) => P3 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), Exists (fun (_ : Unit) => P3 ∧ True)) := by
  intro h_all
  rcases h_all False False False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r4_del0

theorem neg_thm_bpd2_rcases_d3_r4_del1 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Unit) => P0 ∧ True)) (h2 : P1 → Exists (fun (_ : Unit) => P2 ∧ True)) (h3 : P2 → Exists (fun (_ : Unit) => P3 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), Exists (fun (_ : Unit) => P3 ∧ True)) := by
  intro h_all
  rcases h_all True False False False False False False ⟨(), True.intro, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r4_del1

theorem neg_thm_bpd2_rcases_d3_r4_del2 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Unit) => P0 ∧ True)) (h1 : P0 → Exists (fun (_ : Unit) => P1 ∧ True)) (h3 : P2 → Exists (fun (_ : Unit) => P3 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), Exists (fun (_ : Unit) => P3 ∧ True)) := by
  intro h_all
  rcases h_all True True False False False False False ⟨(), True.intro, True.intro⟩ (fun _ => ⟨(), True.intro, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r4_del2

theorem neg_thm_bpd2_rcases_d3_r4_del3 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : Exists (fun (_ : Unit) => P0 ∧ True)) (h1 : P0 → Exists (fun (_ : Unit) => P1 ∧ True)) (h2 : P1 → Exists (fun (_ : Unit) => P2 ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), Exists (fun (_ : Unit) => P3 ∧ True)) := by
  intro h_all
  rcases h_all True True True False False False False ⟨(), True.intro, True.intro⟩ (fun _ => ⟨(), True.intro, True.intro⟩) (fun _ => ⟨(), True.intro, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨_, hf_goal, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r4_del3

theorem neg_thm_bpd2_rcases_d3_r5_del0 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h1 : P0 → ((P1 ∧ P1) ∧ True)) (h2 : P1 → ((P2 ∧ P2) ∧ True)) (h3 : P2 → ((P3 ∧ P3) ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), ((P3 ∧ P3) ∧ True)) := by
  intro h_all
  rcases h_all False False False False False False False (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨⟨hf_goal, _⟩, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r5_del0

theorem neg_thm_bpd2_rcases_d3_r5_del1 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : ((P0 ∧ P0) ∧ True)) (h2 : P1 → ((P2 ∧ P2) ∧ True)) (h3 : P2 → ((P3 ∧ P3) ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), ((P3 ∧ P3) ∧ True)) := by
  intro h_all
  rcases h_all True False False False False False False ⟨⟨True.intro, True.intro⟩, True.intro⟩ (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨⟨hf_goal, _⟩, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r5_del1

theorem neg_thm_bpd2_rcases_d3_r5_del2 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : ((P0 ∧ P0) ∧ True)) (h1 : P0 → ((P1 ∧ P1) ∧ True)) (h3 : P2 → ((P3 ∧ P3) ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), ((P3 ∧ P3) ∧ True)) := by
  intro h_all
  rcases h_all True True False False False False False ⟨⟨True.intro, True.intro⟩, True.intro⟩ (fun _ => ⟨⟨True.intro, True.intro⟩, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨⟨hf_goal, _⟩, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r5_del2

theorem neg_thm_bpd2_rcases_d3_r5_del3 : ¬ (∀ (P0 P1 P2 P3 D0 D1 D2 : Prop) (h0 : ((P0 ∧ P0) ∧ True)) (h1 : P0 → ((P1 ∧ P1) ∧ True)) (h2 : P1 → ((P2 ∧ P2) ∧ True)) (hd1 : D0 → (D1 ∧ D0)) (hd2 : D1 → (D2 ∧ D1)) (hd3 : P3 → (D0 ∧ D2)), ((P3 ∧ P3) ∧ True)) := by
  intro h_all
  rcases h_all True True True False False False False ⟨⟨True.intro, True.intro⟩, True.intro⟩ (fun _ => ⟨⟨True.intro, True.intro⟩, True.intro⟩) (fun _ => ⟨⟨True.intro, True.intro⟩, True.intro⟩) (fun hf => False.elim hf) (fun hf => False.elim hf) (fun hf => False.elim hf) with ⟨⟨hf_goal, _⟩, _⟩
  exact hf_goal

#print axioms neg_thm_bpd2_rcases_d3_r5_del3

theorem neg_thm_bpd2_induction_d1_r0_del0 : ¬ (∀ (F0 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n = n) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d1_r0_del0

theorem neg_thm_bpd2_induction_d1_r0_del1 : ¬ (∀ (F0 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n = n) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d1_r0_del1

theorem neg_thm_bpd2_induction_d1_r1_del0 : ¬ (∀ (F0 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, [F0 n] = [n]) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d1_r1_del0

theorem neg_thm_bpd2_induction_d1_r1_del1 : ¬ (∀ (F0 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, [F0 n] = [n]) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d1_r1_del1

theorem neg_thm_bpd2_induction_d1_r3_del0 : ¬ (∀ (F0 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, Nat.succ (F0 n) = Nat.succ n) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d1_r3_del0

theorem neg_thm_bpd2_induction_d1_r3_del1 : ¬ (∀ (F0 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, Nat.succ (F0 n) = Nat.succ n) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d1_r3_del1

theorem neg_thm_bpd2_induction_d1_r4_del0 : ¬ (∀ (F0 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, (F0 n, true) = (n, true)) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d1_r4_del0

theorem neg_thm_bpd2_induction_d1_r4_del1 : ¬ (∀ (F0 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, (F0 n, true) = (n, true)) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d1_r4_del1

theorem neg_thm_bpd2_induction_d1_r5_del0 : ¬ (∀ (F0 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, Option.some (F0 n) = Option.some n) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d1_r5_del0

theorem neg_thm_bpd2_induction_d1_r5_del1 : ¬ (∀ (F0 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, Option.some (F0 n) = Option.some n) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d1_r5_del1

theorem neg_thm_bpd2_induction_d2_r0_del0 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n = n) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun k => k + 2) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r0_del0

theorem neg_thm_bpd2_induction_d2_r0_del1 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n = n) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r0_del1

theorem neg_thm_bpd2_induction_d2_r0_del2 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n = n) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r0_del2

theorem neg_thm_bpd2_induction_d2_r1_del0 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, [F0 n] = [n]) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun k => k + 2) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r1_del0

theorem neg_thm_bpd2_induction_d2_r1_del1 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, [F0 n] = [n]) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r1_del1

theorem neg_thm_bpd2_induction_d2_r1_del2 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, [F0 n] = [n]) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r1_del2

theorem neg_thm_bpd2_induction_d2_r2_del0 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n + 1 = n + 1) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun k => k + 2) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r2_del0

theorem neg_thm_bpd2_induction_d2_r2_del1 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n + 1 = n + 1) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r2_del1

theorem neg_thm_bpd2_induction_d2_r2_del2 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n + 1 = n + 1) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r2_del2

theorem neg_thm_bpd2_induction_d2_r4_del0 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, (F0 n, true) = (n, true)) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun k => k + 2) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r4_del0

theorem neg_thm_bpd2_induction_d2_r4_del1 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, (F0 n, true) = (n, true)) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r4_del1

theorem neg_thm_bpd2_induction_d2_r4_del2 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, (F0 n, true) = (n, true)) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r4_del2

theorem neg_thm_bpd2_induction_d2_r5_del0 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, Option.some (F0 n) = Option.some n) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun k => k + 2) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r5_del0

theorem neg_thm_bpd2_induction_d2_r5_del1 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h2 : ∀ k : Nat, F1 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, Option.some (F0 n) = Option.some n) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r5_del1

theorem neg_thm_bpd2_induction_d2_r5_del2 : ¬ (∀ (F0 F1 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, Option.some (F0 n) = Option.some n) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d2_r5_del2

theorem neg_thm_bpd2_induction_d3_r0_del0 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n = n) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun k => k + 2) (fun k => k + 2) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r0_del0

theorem neg_thm_bpd2_induction_d3_r0_del1 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n = n) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 1) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r0_del1

theorem neg_thm_bpd2_induction_d3_r0_del2 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n = n) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r0_del2

theorem neg_thm_bpd2_induction_d3_r0_del3 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n = n) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r0_del3

theorem neg_thm_bpd2_induction_d3_r2_del0 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n + 1 = n + 1) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun k => k + 2) (fun k => k + 2) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r2_del0

theorem neg_thm_bpd2_induction_d3_r2_del1 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n + 1 = n + 1) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 1) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r2_del1

theorem neg_thm_bpd2_induction_d3_r2_del2 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n + 1 = n + 1) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r2_del2

theorem neg_thm_bpd2_induction_d3_r2_del3 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, F0 n + 1 = n + 1) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r2_del3

theorem neg_thm_bpd2_induction_d3_r3_del0 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, Nat.succ (F0 n) = Nat.succ n) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun k => k + 2) (fun k => k + 2) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r3_del0

theorem neg_thm_bpd2_induction_d3_r3_del1 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, Nat.succ (F0 n) = Nat.succ n) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 1) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r3_del1

theorem neg_thm_bpd2_induction_d3_r3_del2 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, Nat.succ (F0 n) = Nat.succ n) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r3_del2

theorem neg_thm_bpd2_induction_d3_r3_del3 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, Nat.succ (F0 n) = Nat.succ n) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r3_del3

theorem neg_thm_bpd2_induction_d3_r4_del0 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, (F0 n, true) = (n, true)) := by
  intro h_all
  have h_at := h_all (fun k => k + 1) (fun k => k + 2) (fun k => k + 2) (fun _ => 0) (fun _ => 0) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 0
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r4_del0

theorem neg_thm_bpd2_induction_d3_r4_del1 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h2 : ∀ k : Nat, F1 k = F2 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, (F0 n, true) = (n, true)) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 1) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r4_del1

theorem neg_thm_bpd2_induction_d3_r4_del2 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h3 : ∀ k : Nat, F2 k = F0 k + 1) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, (F0 n, true) = (n, true)) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 1) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r4_del2

theorem neg_thm_bpd2_induction_d3_r4_del3 : ¬ (∀ (F0 F1 F2 D0 D1 : Nat → Nat) (h0 : F0 0 = 0) (h1 : ∀ k : Nat, F0 (k + 1) = F1 k) (h2 : ∀ k : Nat, F1 k = F2 k) (hd1 : ∀ k : Nat, D0 (k + 1) = D1 k) (hd2 : ∀ k : Nat, D1 k = D0 k) (hd3 : ∀ k : Nat, D0 (k + 2) = D1 k), ∀ n : Nat, (F0 n, true) = (n, true)) := by
  intro h_all
  have h_at := h_all (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) (fun _ => 0) rfl (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) (fun _ => rfl) 1
  exact absurd h_at (by decide)

#print axioms neg_thm_bpd2_induction_d3_r4_del3
