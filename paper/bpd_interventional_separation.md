# BPD-01: Interventional separation for behavioral parameter decomposition and looped Lean gyms

**Status (2026-11-15):** mathematical proofs for a finite deterministic interface; independent exhaustive CPU checks; synthetic examples. No model weights, candidate VPD dictionaries, Lean kernel, or physical interventions were evaluated in this note itself. This note extends the *experiment design* side of [MP-02](metaprune_set_cover.md) and [QI-02](active_quotient_information_budget.md); it does not imply an existing neural decomposition works.

## 1. The question the dataset must answer

A behavioral parameter decomposition (BPD) proposes mechanisms or rival explanations \(H=\{h_0,\ldots,h_{n-1}\}\). An evaluation cell \(e\) is an **item plus a precisely specified intervention, target expert, recurrent pass and readout**. For now each cell has a deterministic known outcome \(y_e(h)\) in a finite categorical alphabet, a positive integer measurement cost \(w_e\), and a fixed routing bit \(r_e\). Only cells with \(r_e=1\) are usable. The routing bit is fixed across hypotheses; a routing failure is **missing data**, never evidence of an unchanged outcome. If expert routing depends on the hidden mechanism, it must be modeled as a separately observed stochastic channel rather than silently treated as a binary failure.

When realized observations \((o_e)_{e\in F}\) are collected on a routed subset \(F\subseteq E\), the surviving candidate set is \(\{h\in H:\forall e\in F\text{ with }r_e=1,\; y_e(h)=o_e\}\). Because the true data-generating process may lie outside the declared hypothesis set \(H\), evaluation must include an explicit **`"no hypothesis fits"`** outcome returned whenever this surviving set is empty (`identify_hypothesis`), falsifying \(H\) rather than projecting onto a nearest candidate.

Let \(P=\{\{h_i,h_j\}:i<j\}\), and let the **separation set** of a routed cell be

\[
S_e=\{\{h_i,h_j\}\in P:y_e(h_i)\ne y_e(h_j)\},\qquad S_e=\varnothing\text{ if }r_e=0.
\tag{BPD-1}
\]

Two mechanisms are observationally equivalent precisely when they have identical outcomes on every routed cell. The observable object is the quotient of \(H\) by this equivalence relation. A model trained on this interface cannot be expected to distinguish members of the same quotient class even if a decomposition algorithm assigns them separate names.

**BPD-01/T1 (minimum test collection, algebraic identity).** The minimum total cost of a **fixed batch** which identifies every hypothesis in \(H\) is the weighted **minimum test collection** (*Minimum Test Set*, Garey and Johnson 1979, `[SP6]`, p. 222; Halldórsson, Halldórsson, and Ravi 2001):

\[
C_{\rm batch}=\min_{F\subseteq E}\left\{\sum_{e\in F}w_e:\bigcup_{e\in F}S_e=P\right\},
\tag{BPD-2}
\]

with value \(+\infty\) if some pair is never separated. **Proof.** Any successful fixed batch must induce distinct output signatures for all \(h_i\), requiring a differing response for each pair. Conversely, a batch covering every pair gives distinct signatures on \(H\) (and returns `"no hypothesis fits"` on any realized signature outside \(H\)). Cost is the sum of its selected cells. The exact bitmask dynamic program (`minimum_test_collection`) and an independent exhaustive-subset implementation (`exhaustive_batch`) solve (BPD-2).

This is a minimum-weight set cover on **mechanism pairs**. MP-02 covers alternatives against one distinguished baseline. That special form makes its adaptive and nonadaptive worst-case costs equal; multiway identification has a different result.

**BPD-01/T2 (optimal decision tree, finite theorem).** The sequential counterpart is the **optimal decision tree** problem (Hyafil and Rivest 1976; Moret 1982). For any surviving candidate subset \(A\subseteq H\), define \(D(\{h\})=0\) and

\[
D(A)=\min_{e\colon r_e=1,\,|\Pi_e(A)|>1}
\left[w_e+\max_{B\in\Pi_e(A)}D(B)\right],
\tag{BPD-3}
\]

where \(\Pi_e(A)\) partitions \(A\) by the observed categorical response (with any realized response absent from \(\{y_e(h):h\in A\}\) terminating immediately with `"no hypothesis fits"`). The value is infinite if no informative cell exists. This recurrence (`optimal_decision_tree_cost`) equals optimal worst-case identification cost for deterministic adaptive policies over \(H\). **Proof.** Every valid decision tree chooses some informative first cell and must solve its realized response class. Condition on the first response for the lower bound; attach optimal subtrees for the upper bound. Strictly smaller response classes make the recursion well founded. Consequently \(D(H)\le C_{\rm batch}\), with strict inequality possible.

A four-mechanism witness has three unit-cost probes with outcome rows

| Probe | h0 | h1 | h2 | h3 |
|---|---:|---:|---:|---:|
| root | 0 | 0 | 1 | 1 |
| left | 0 | 1 | 0 | 0 |
| right | 0 | 0 | 0 | 1 |

A fixed separating test collection needs all three. Querying `root`, then only `left` or `right` according to the answer, needs at most two. Observing `(root=1, left=1, right=1)` matches none of `h0..h3` and returns `"no hypothesis fits"`. Turning off routing for `left` makes \(h_0,h_1\) indistinguishable; both optimizers correctly return infeasibility.

## 2. Clock and visibility as measurable finite fibres

To compare causal-importance predictors, collect **intervention labels** on records indexed by `(case, component, intervention type, state, pass, visible)`. The binary label is a declared intervention outcome, such as a thresholded change in the exact proof-checker result. It is not silently replaced by a final-answer correctness label. For any feature projection \(\phi\), let \(F_z=\{i:\phi(i)=z\}\) be the resulting finite fibres, with integer weights \(a_i>0\) and binary labels \(b_i\).

**BPD-01/T3 (finite feature-fibre error floor, algebraic identity).** Among all deterministic binary predictors allowed to inspect only \(\phi(i)\), the minimum weighted 0-1 error is exactly

\[
L^*(\phi)=\sum_z \min\!\left(\sum_{i\in F_z:b_i=0}a_i,\sum_{i\in F_z:b_i=1}a_i\right).
\tag{BPD-4}
\]

**Proof.** A deterministic predictor must issue one label per fibre. Choosing the majority label minimizes errors independently on each fibre; summing achieves the lower bound. Ties admit either choice. This result needs no statistical model and is exact even if all component labels are wrong; causal interpretation requires separately validated interventions.

Two structural caveats govern how (BPD-4) applies to neural loops:

1. **Continuous states have floor zero; matching tolerance decides the result.** With continuous hidden states in \(\mathbb{R}^d\), distinct passes almost never revisit bit-identical vectors, so every unbinned state forms a singleton fibre and \(L^*(\phi_{\mathrm{state}})=0\) trivially. Any non-zero empirical floor is induced by the chosen state-matching tolerance \(\varepsilon\) (or clustering radius) used to group nearby states into discrete fibres, so \(\varepsilon\) decides the result and must be pre-registered and swept.
2. **Exact clock gap at a repeated state measures remaining budget.** Suppose a time-homogeneous weight-tied operator runs for a fixed horizon \(T\) and visits the *exact* same carried state \(s_{\tau_1}=s_{\tau_2}\) at two passes \(\tau_1<\tau_2\). Because downstream trajectory readouts run for \(T-\tau_1\) versus \(T-\tau_2\) remaining iterations (e.g., whether enough passes remain to rebuild an ablated feature before termination), intervention labels at \(\tau_1\) and \(\tau_2\) can legitimately differ. An exact clock gap \(L^*_{\mathrm{state+clock}}<L^*_{\mathrm{state}}\) at a repeated state therefore measures **remaining pass budget** \(T-\tau\), rather than proving that the shared transition matrix itself varies with time.

Compare three projections with `case`, `component` and `intervention` always fixed:

- **state-only:** add the carried-state identifier;
- **state + clock:** add the same state identifier and pass index;
- **visible-only:** add the projected head-readable identifier.

The state + clock projection refines state-only, so \(L^*_{\mathrm{state+clock}}\le L^*_{\mathrm{state}}\). A visible-only gap certifies loss of information relative to the tested richer interface only when comparing on the same cases and labels.

## 3. Refill makes final-only importance underestimate path importance

**BPD-01/T4 (explicit refill state-update counterexample).** Let a loop evolve a one-bit carried state \(s_t\in\{0,1\}\) from \(s_0=0\) over \(t=0,\ldots,T-1\) (\(T\ge 2\)) with input bit \(x\in\{0,1\}\) and per-pass cut indicator \(c_t\in\{0,1\}\) under the explicit update rule (`refill_step`):

\[
s_{t+1}=\begin{cases}
0,& c_t=1,\\
\mathrm{refresh}(s_t,x)=s_t\lor x,& c_t=0.
\end{cases}
\tag{BPD-5}
\]

For \(x=1\):
- Under no cuts (\(c_t=0\) for all \(t\)), \((s_1,\ldots,s_T)=(1,\ldots,1)\).
- Under a single early cut at pass \(k<T-1\) (\(c_t=\mathbf{1}[t=k]\)), pass \(k\) sets \(s_{k+1}=0\), and pass \(k+1\) executes \(s_{k+2}=0\lor 1=1\), rebuilding the erased state so \(s_T=1\) matches the clean final output.
- Under a persistent cut (\(c_t=1\) for all \(t\)), \((s_1,\ldots,s_T)=(0,\ldots,0)\), flipping the final output from \(1\) to \(0\).

A final-output-only oracle marks all \(T-1\) early single cuts irrelevant, whereas a per-boundary trajectory oracle detects every cut at \(s_{k+1}\). `refill_witness` executes (BPD-5) step by step; it has no claim to simulate TRM or measure a learned fixed point.

Therefore report **single-pass** interventions, **all-pass** interventions, intermediate readouts, and separate final verdicts. For weight-tied operators the proposed decomposition shares component matrices across passes; an optional clock may alter the *mask policy*, rather than the shared weight identity. Report raw effects and rotation-null-calibrated effects separately, with ablation replacement semantics recorded.

## 4. Driving the next Lean gym and FC-12 negative-cell accounting

A useful BPD item is a `(source theorem, original Lean goal state, concrete action, component edit, recurrent pass, independent outcome)` record. FC-12 compiles parameterized `exact`, `rw`, `rcases`, and `induction` candidates against `51` source Lean goal states (`51 × 4 = 204` total `(goal, family)` cells). In the unprobed training incidence table, **`39` verified positives plus `165` untested cells already account for all `204` cells (`39 + 165 = 204`)**, leaving **`0` recorded negative cells**. Because an *untested* cell is missing data rather than a negative outcome, every probed tactic candidate that fails Lean compilation or countermodel check must be explicitly recorded as a **negative cell** (`fc12_cell_ledger`: `positive_cells + negative_cells + untested_cells == 204`), moving audited cells out of the `165` untested pool into `negative_cells`. Candidate success, explicit compiler rejection, goal-count progress, exact source SHA, and compiler diagnostics belong in the outcome. All final proofs and negations require kernel replay; a syntactic or learned label alone supplies no proof.

The next corpus (`BPD-LG-01 v2`) combines content-distinct theorem roots split by post-identifier-normalisation SHA-256 hash, interior-link and entry-hypothesis deletions paired with type-checking decoy premises, depth-sensitive proofs across all included families, and Lean-kernel-checked proofs of both positive theorems and negative refutations (`¬ goal`).

Use the following acceptance gates before calling BPD components identifiable:

1. **Routed coverage & shortcut separation:** every declared mechanism or shortcut pair has an actually observed separating cell, and realized vectors outside \(H\) report `"no hypothesis fits"`.
2. **Causal relevance:** paired edit changes an independent Lean proof/search outcome or intermediate state; maintain the same source and budget across arms. Track model error separately from compiler reject/timeout.
3. **Unsaturation:** log per-case intact and edited probabilities, including rare cases where a flip occurs. Allocate repetitions from [QI-02](active_quotient_information_budget.md) only when Bernoulli interior and conditional IID assumptions hold.
4. **Negative controls:** keep no-op, source-matched rotation, route failure, early single cut and persistent cut as distinct arms, and record explicit negative cells in FC-12 (`positive + negative + untested = 204`).
5. **Clock ablation:** compare state-only, state + pass, and visible-only selectors under matched decomposition rank, compute and search budgets, reporting state-matching tolerance \(\varepsilon\) and remaining-budget \(T-\tau\) effects explicitly.

## 5. Verification and scope

`evaluation_bpd.py` implements `minimum_test_collection` (BPD-2) with a pivot-based bitmask recurrence and an independent exhaustive enumeration (`exhaustive_batch`); `optimal_decision_tree_cost` (BPD-3) uses explicit response partitions over subsets of surviving worlds; `identify_hypothesis` enforces the `"no hypothesis fits"` outcome outside \(H\); `refill_witness` executes the explicit recurrence (BPD-5); and `fc12_cell_ledger` audits `positive + negative + untested == 204`. The source-hashed verifier regenerates `output/evaluation_bpd/bpd_01.json`.

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_evaluation_bpd.py' -v
PYTHONPATH=src python scripts/verify_evaluation_bpd.py
python scripts/check_receipts.py --only bpd
```

## References

- M. R. Garey and D. S. Johnson, *Computers and Intractability: A Guide to the Theory of NP-Completeness*, W. H. Freeman, San Francisco, 1979, `[SP6]` (*Minimum Test Set*), p. 222.
- B. V. Halldórsson, M. M. Halldórsson, and R. Ravi, "On the Approximability of the Minimum Test Collection Problem," in *Algorithms — ESA 2001*, Lecture Notes in Computer Science, vol. 2161, Springer, 2001, pp. 158–169.
- L. Hyafil and R. L. Rivest, "Constructing optimal binary decision trees is NP-complete," *Information Processing Letters*, vol. 5, no. 1, pp. 15–17, May 1976 (`doi:10.1016/0020-0190(76)90095-8`).
- B. M. E. Moret, "Decision Trees and Diagrams," *ACM Computing Surveys*, vol. 14, no. 4, pp. 593–623, Dec. 1982 (`doi:10.1145/356893.356898`).
