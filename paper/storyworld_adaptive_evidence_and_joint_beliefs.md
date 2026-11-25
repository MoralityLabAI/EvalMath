# SRG-10: Adaptive evidence acquisition and compact joint beliefs

2026-11-25. Evidence class: finite deterministic SWMD-SRG/2 execution with exact integer prior masses, independent tape-conditioned recurrence, and public scorer controls. No model inference, actual private evaluation, TypeScript application build, or Lean certification.

## 1. Family and information contract

Let T,Z be independent uniform signs (current truth and latent context). Source noise is specified with integer reliability numerators out of 8. There are five signs A,B,X,Y,Q. The reference distribution enumerates every assignment of T,Z and the five signs; weights are products of five conditional likelihood numerators. The common denominator is 4*8^5=131072. Zero-weight tapes are omitted. The worlds are deterministic conditional on a tape; probability enters only through the initial mass distribution.

Three structurally distinct procedural families (not independently human-authored):
- Specialist: A reports Z and B reports T. X and Y estimate T with swapped context-dependent reliabilities. Q estimates Z.
- Common cause: A reports Z, B reports T. X estimates TZ, Y is exactly X (same source), Q estimates T.
- Temporal: earlier truth is TZ. A and X estimate earlier truth, B and Q estimate Z, Y estimates current truth T. This is a two-epoch dependency model, not a stochastic time-evolving engine.

Each family has four observation contracts: analyst sees A only, reviewer sees B only, joint sees A and B, blind sees neither. The SWMD compiler uses explicit public/hidden declarations for the two initial observer registers, as well as three public query registers. A steward initializes the hidden tape and the corresponding A,B registers before the first action; the p/p2 source keys retain owner identity. These are matched single-decision-maker views, not autonomous interacting observers or a complete theory of subjective belief. Every query can be used once, consumes an action and costs c. Correct terminal commitment pays 16 minus cumulative query cost, incorrect commitment pays negative cost, settlement pays S minus cost. A budget-exhausted nonterminal pays negative incurred cost. Queries at the last available action are dominated in the registered payoff range and excluded from the optimal search, but explicitly scored at their unfinished value if a model submits one. Horizon H=1,2,3.

Initial public controls choose A reliability 7/8, B 6/8, strong 7/8, weak 4/8, Q 7/8, cost 1, settlement 9 in each family. Additional configurations vary reliability (including perfectly informative signals), settlement and query costs. The source uses the registered conditional distribution, rather than heuristic averaging of reports.

## 2. Exact adaptive versus fixed-order query policies

A belief cell B is a multiset of tape-conditioned runtime states with positive integer masses. For remaining action budget h, use the terminal utility above and recurse:
    W_h(B)=max_a sum_o W_(h-1)({(T(s,a),m_s) : (s,m_s) in B, O(T(s,a))=o}).
Initial observation cells are solved separately and their reward masses summed. The fixed-order control registers one predetermined sequence of distinct queries, shared across initial observations; the decision maker may stop or commit adaptively, but can query only the next member of the fixed order. Maximize expected value over all six two-query permutations (for H=1 no queries). This is a conservative comparator allowing contingent stopping, not open-loop commitment.

A separate recurrence works directly on tape signs, used query names and the conditional weights, without compiled ASTs, runtime states or transition calls. The prior tape generator is shared; the independence claim is about the decision and transition implementations. Both references match every tested initial, fixed-order, and off-policy continuation action value exactly. Every possible first query is also forced and its successor observations re-partitioned, including suboptimal queries. The resulting tasks include actual continuation actions, not only advice at the root.

| Registered configuration | Observer | H | Adaptive | Best fixed order |
|---|---|---:|---:|---:|
| Specialist | Analyst | 2 | 12.25 | 10.625 |
| Specialist | Analyst | 3 | 12.25 | 11.75 |
| Specialist | Reviewer | 2 | 12 | 12 |
| Specialist | Blind | 3 | 11.25 | 10 |
| Specialist | Joint | 2 | 12.25 | 12.125 |
| Common cause | Blind | 2 | 13 | 13 |
| Temporal | Blind | 2 | 9 | 9 |
| Temporal | Blind | 3 | 10.5 | 10.5 |

Specialist blind H=3 chooses Q first. Its two possible equally likely reports identify the more reliable query X or Y; then the agent commits using the resulting sign. The adaptive gain over fixed query order is 1.25 utility. With analyst access, the initial context report already determines the preferred specialist. The reviewer instead sees a direct truth cue. This demonstrates task-dependent information value, and why an author's observation ownership changes optimal policy even with the same underlying mechanics.

The duplicate report case also checks an exact causal effect: after reading X, query Y has zero incremental information and costs c. Reading Y and then X is symmetric. At H=2 from the post-first-query state, the duplicated query's value equals the best immediate terminal action value minus c times the cell mass. All 108 such cells satisfy equality. There are 768 tape/view copy checks, 3072 observer visibility checks, 243 initial action-value cells, 1053 fixed-policy cells, and 948 forced-continuation cells across the executed cohorts. These counts repeat configurations and related states, not independent samples. All budget/access monotonicity controls pass.

## 3. Joint belief compactification

For two signs, define m_T=E[T], m_Z=E[Z], m_TZ=E[TZ]. The joint posterior is recovered by the inverse Walsh transform
    P(T=t,Z=z)=(1+t*m_T+z*m_Z+t*z*m_TZ)/4.
The triple is an exact parameterization of the two-sign distribution (subject to nonnegativity). A marginal on T alone suffices for immediate commitment, but information-gathering can depend on context and correlation. Future observation kernels matter: the common-cause world also requires the identity of previously queried sources to know whether a report is a copy. Do not generalize three statistics to arbitrary social graphs.

At fixed config/view/history stage and horizon, group decision cells by legal menu and a prefix of posterior probabilities P(T=+1), P(Z=+1), P(T=Z). These are equivalent to the moments. Each group's best common first action is computed using exact weighted sums of original continuation values. The resulting ceiling restricts only first-action information; later continuation retains the full available observation. This is not a complete compressed-state planning solver, nor a learned encoder. Equal fractions are reduced exactly; dyadic quantization uses nested interval indices with endpoint clipping.

Across 324 contexts (108 roots and 216 after-query/horizon combinations), the number with any first-action ceiling loss:
- menu only: 194;
- truth marginal: 19;
- truth and context marginals: 1;
- exact joint posterior: 0.

The temporal example after forced X, analyst view, H=2 has identical truth/context marginals across its two report-agreement classes. Agreeing reports increase confidence about earlier truth, which changes T,Z correlation and raises the value of a context query; conflicting reports favor settlement. Full joint value 10.9375 vs two-marginal ceiling 10.71875. Thus even perfectly represented marginal beliefs may lose an interaction needed for action selection.

For the three-statistic coarsening, two-bit bins preserve the empirical first-action ceiling in 322/324 contexts; three-bit bins preserve it in all 324. This is finite sample partition behavior, not an optimal bit-width requirement, a global quantization guarantee or proof that a model can infer the posterior. Use separate calibration and independent world families for precision promotion.

Decision margin: at a cell with mass N, let gap=(highest summed action value - second highest)/N. If every expected action-value estimate has absolute error at most epsilon, gap>2*epsilon certifies the unique best action is unchanged. We record weighted certificate mass at epsilon=0.125,0.25,0.5,1, plus ties. In the public calibration cohort, 23,213,056 of 28,311,552 total repeated decision mass is certified at epsilon=0.25 (~82%). This is a sufficient score-space certificate; it is not a bound on arbitrary parameter or state quantization error. SRG-09 supplies a separate nonlinear contrast perturbation bound. Author utility margins should be measured against the expected consequence of actions and evidence costs, as well as mechanical reaction margins.

## 4. Dataset, scoring and custody

Public calibration: six configurations, 24 observer-world variants, 798 root/continuation tasks. Additional public smoke: three configs, 12 observer-world variants, 393 tasks. All use public procedural templates; the latter is an execution test of the private-instance generation path, not secret held-out data. The total 1191 rows are related by config, observer access, forced query and budget. Group siblings rather than randomly split rows. The public dataset is a diagnostic, not Data Goblin supervision.

Weighted scoring records optimal tie-set membership and actual selected first-action expected utility assuming optimal subsequent decisions. Missing/rejected/duplicate responses receive zero credited utility; unknown IDs are separately reported. An unfinished last-action query is legal but has negative cost. Public scorer controls:
- Gold 798/798 correct, expected utility 10.854600694444445, zero regret.
- Always settle 131/798 correct, expected utility 8.555555555555555, regret 2.299045138888889.
- First legal action 234/798 correct, expected utility 7.222222222222222, regret 3.6323784722222223.
- One invalid action, one duplicate, 796 missing and one unknown ID correctly classified.

The local materializer uses a fresh nonzero random uint32 seed for evaluation outside the checkout, excludes public seeds, and separates model_input/ and verifier/. This reserves procedural instances, not unpublished families or guaranteed-disjoint parameter settings. Reliabilities are exposed in the rules because the reasoner must calculate a decision under a declared model; the hidden tape and gold oracle are private. Freeze model and settings before generation. The seed is for reproducibility, not cryptographic secrecy. Use independently authored novel structures to test concept generalization. No actual private instances or model inference have been run. No new training examples are exported.

## 5. Reproduce and next gate

The pure JS curriculum and scorer were executed from connector-fetched source in an isolated ECMAScript runtime. The standalone Node replay hashes source blobs and compares receipts and corpus; filesystem execution and local HTTP model runs remain pending. See integrations/sweepweave-ts/srg10/README.md. Original authored worlds and production TypeScript editor remain unchanged. No Godot dependency.

SRG-11: add explicit author-side targets for balanced goal margins, inquiry cost, observer access and evidence provenance, then generate minimally edited SWMD worlds that meet those targets across counterfactual reliability interventions. Test transfer from procedural evidence families to actual authored stories with independent gold utility and a native runtime export. Run matched Bonsai/Inky/Data Goblin models locally on the frozen suites; report inference passes, memory, precision and regret separately.
