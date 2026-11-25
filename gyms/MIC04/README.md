# MIC-04: revisitable integer recurrence certificates and atomic SCC repair

Public CPU development follow-up to [MIC-03 draft #86](https://github.com/MoralityLabAI/EvalMath/pull/86). Focus on recurrence generators; covering and the original textual discovery-history experiment remain separate. No upstream manuscript bytes used.

## Design

For integer nonnegative M with row sums <=9, positive integer b, and p>=0, use H_i(p)=b_i+ceil(sum_j M_ij p_j/10). A certificate is p>=H(p), objective sum(p). The scalar starting vector is feasible. Each visit replaces one coordinate with H_i(p); it may revisit the same coordinate. At each horizon K in {1,2,4,8,16}, the exact dynamic program minimizes the endpoint objective over at most K such visits. No-op visits can be padded, so exact and at-most budgets have the same value. Exact certificate and schedule oracles are diagnostic, with their own work excluded from policy counts.

Train six matched 1,793-parameter GRU rankers: persistent vs reset hidden state, seeds 17,29,43, 40 passes over all five horizon batches, Adam 0.01. Teacher masks contain every optimal action among productive moves (or all moves at a fixed point). Train on 48 size-four DAG and ring roots, 24 seeds per family. Develop on four generators (DAG, strongly connected rings, chorded rings, nearcritical chorded rings with row sum 9), sizes 4 and 5, seeds 1000..1011, 96 roots and 480 root-budget rows, 4,800 policy rollouts. Size pairs and horizons share root seeds; model seeds are repeated measures. The four lineages are unverified as independent and no confirmation set is sealed. The rankers receive a horizon, age, residual and dependency features; the same scan runs for the deterministic controls. Each candidate is checked for feasibility. All policies except two-step lookahead have the same count of initial and candidate certificate checks (mean 73 at K=16); lookahead averages 380.5 checks. Feature preparation, repeated baseline validation and network compute are not included in that counter, and equal counts do not imply equal wall time.

## Exact finite results

Mean gaps are percentages of starting objective, averaged over public roots and then model seeds. The first column is the optimal budgeted schedule's gap to the least feasible certificate. Remaining columns are regret to that schedule oracle.

| K | Oracle gap to least | Sweep | Residual | Dependency | 2-step lookahead | Stateless | Recurrent |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 38.35069 | 4.27908 | 0 | 0 | 0 | 0.04 | 0.04 |
| 2 | 29.56582 | 8.74297 | 0.34233 | 0.60840 | 0 | 0.35617 | 0.40071 |
| 4 | 14.59057 | 10.99791 | 1.09934 | 1.31751 | 0.30141 | 2.35057 | 2.40747 |
| 8 | 7.00512 | 5.04819 | 0.91167 | 1.13504 | 0.29192 | 2.50847 | 2.57528 |
| 16 | 3.81478 | 1.74447 | 0.41798 | 0.53767 | 0.21258 | 1.92455 | 2.01991 |

Recurrent minus stateless benefit at K=16 is -0.09537 pp. Residual greedy dominates the learned policies in the overall averages. Lookahead has a larger candidate-check budget. No trained-model advantage is established.

## A distinct obstruction: integer rounding traps

Let p^- be the limit of synchronous H iteration from zero, and p^+ the limit from the feasible upper vector p0. Monotonicity and finiteness of the integer interval imply both limits exist, with p^- the componentwise least feasible point and p^+ the greatest fixed point below p0. Every feasible coordinate tightening starting at p0 preserves p>=p^+: if p>=p^+, then H_i(p)>=H_i(p^+)=p_i^+. A fair descending schedule terminates at a fixed point, which must be p^+. Hence scheduling, even with unlimited visits, cannot cross a nonzero p^+-p^- gap.

For M=[[0,8],[8,0]], b=(1,3), the least feasible certificate is (10,11), but downward iteration from p0=(15,15) reaches (13,14). Both endpoints are fixed points. The latter sums to 27 instead of 21. A certificate-valid atomic replacement by (10,11) escapes the trap.

At K=16, decompose the normalized total gap into scheduler regret, budget gap V_K(p0)-sum(p^+), and action-class trap gap sum(p^+)-sum(p^-). The oracle mean gap of 3.81478 pp contains 2.09714 pp of finite-budget gap and 1.71764 pp of rounding trap. The trap occurs in 38/96 roots.

| Family | Trapped / 24 | Mean trap gap pp | Mean finite budget gap pp | SCC repair internal row evaluations (mean) |
|---|---:|---:|---:|---:|
| DAG | 0 | 0 | 0 | 9 |
| Ring | 4 | 0.87963 | 0 | 39.25 |
| Chords | 12 | 1.78921 | 0.06548 | 45.25 |
| Nearcritical | 22 | 4.20172 | 8.32308 | 147.5 |

## Structural repair

Solve strongly connected components in dependency-sink order. With already solved exterior dependencies fixed, iterate each component from zero to its least fixed point. Its previous feasible coordinates bound the internal iteration above. Commit the entire component atomically after verifying the global certificate. Other components' inequalities are preserved because dependency coefficients are nonnegative and changed coordinates decrease. Induction over the condensation DAG gives the global least fixed point: each component must be at least its least solution under the already-minimal dependencies. This argument applies to the stated finite monotone integer system with a feasible upper bound; it is not a theorem about general mathematical reasoning.

The SCC audit reached the exact least certificate on all 96 roots, using mean 60.25 internal row evaluations and 1.875 atomic commits. All three cyclic generators have a single SCC. A full SCC solve is a stronger action class with extra internal work; the internal row evaluations are not full candidate checks and should not be compared as equal-cost updates. The repair verifies after each block, but temporary internal iterates need not be feasible global certificates.

## Replay and evidence

```sh
cd gyms/MIC04
python -m pytest -q test_mic04.py
OMP_NUM_THREADS=1 python run.py > results.json
python block_audit.py > block_results.json
cd ../..
python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC04/preflight_input.json --strict
```

Sandbox PyTorch 2.10.0+cpu, one thread, six fits and all evaluation completed in 12.5834 s. Four isolated tests passed, with brute-force schedule verification for 12 small roots through depth 3, teacher-mask replay and SCC exactness checks. The exact preflight planner copied in MIC-03 returned exit 2: REDESIGN_OR_PILOT_ONLY. Four family summaries, unverified independence, no sealed holdout, no 95/95 sham tolerance bound, effect below scientific floor 5 pp. Observed worst development sham 4.8 pp. K=16 recurrent-vs-reset is the planner's contrast; the three-comparison allowance and thresholds were inherited from MIC-03 for retrospective planning, not an independent preregistration. No claim of statistical confirmation or training promotion. Full repository CI has not been run.

Source SHA-256 ae7e375bf204e7da243542592291636cf6cfb2e992eed3ceff13a2ff2d995519.
Raw run SHA-256 7b0da8488b12ed44a73f48079b18cb019963556c9dda5c9ecaa1f732c45c5427 (wall time is recorded and changes on replay).
Block audit SHA-256 3fa1de9ef69e5ddeea79cc502dcdf2b29b860301b21cd70776a41c1cd50bcf6a.
Four tests passed; full run files stay in sandbox and can be regenerated, no checkpoint or raw output committed.

## Next gate

Use SCC-aware proof-obligation blocks and exact rational vs integer controls, with independent verification of atomic rewrites, internal row-work receipts, and a common cost budget. For acyclic tasks, prefer reverse dependency order; for cyclic finite monotone systems, distinguish residual budget from representational obstruction. Compare deterministic decompositions with learned block proposals only on problems where exact block solves are sufficiently expensive to leave useful scope. Nearcritical, genuinely cyclic and mixed condensation-DAG structures should be distinct generator lineages. No paid compute requested.
