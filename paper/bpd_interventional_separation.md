# BPD-01: Interventional separation for behavioral parameter decomposition and looped Lean gyms

**Status (2026-11-15):** mathematical proofs for a finite deterministic interface; independent exhaustive CPU checks; synthetic examples. No model weights, candidate VPD dictionaries, Lean kernel, or physical interventions were evaluated here. This note extends the *experiment design* side of [MP-02](metaprune_set_cover.md) and [QI-02](active_quotient_information_budget.md); it does not imply an existing neural decomposition works.

## 1. The question the dataset must answer

A behavioral parameter decomposition (BPD) proposes mechanisms or rival explanations \(H=\{h_0,\ldots,h_{n-1}\}\). An evaluation cell \(e\) is an **item plus a precisely specified intervention, target expert, recurrent pass and readout**. For now each cell has a deterministic known outcome \(y_e(h)\) in a finite categorical alphabet, a positive integer measurement cost \(w_e\), and a fixed routing bit \(r_e\). Only cells with \(r_e=1\) are usable. The routing bit is fixed across hypotheses; a routing failure is **missing data**, never evidence of an unchanged outcome. If expert routing depends on the hidden mechanism, it must be modeled as a separately observed stochastic channel rather than silently treated as a binary failure.

Let \(P=\{\{h_i,h_j\}:i<j\}\), and let the **separation set** of a routed cell be

\[
S_e=\{\{h_i,h_j\}\in P:y_e(h_i)\ne y_e(h_j)\},\qquad S_e=\varnothing\text{ if }r_e=0.
\tag{BPD-1}
\]

Two mechanisms are observationally equivalent precisely when they have identical outcomes on every routed cell. The observable object is the quotient of \(H\) by this equivalence relation. A model trained on this interface cannot be expected to distinguish members of the same quotient class even if a decomposition algorithm assigns them separate names.

**BPD-01/T1 (nonadaptive separation cover, algebraic identity).** The minimum total cost of a **fixed batch** which identifies every hypothesis equals

\[
C_{\rm batch}=\min_{F\subseteq E}\left\{\sum_{e\in F}w_e:\bigcup_{e\in F}S_e=P\right\},
\tag{BPD-2}
\]

with value \(+\infty\) if some pair is never separated. **Proof.** Any successful fixed batch must induce distinct output signatures for all \(h_i\), requiring a differing response for each pair. Conversely, a batch covering every pair gives distinct signatures and therefore a zero-error lookup table. Cost is the sum of its selected cells. The exact bitmask dynamic program and an independent exhaustive-subset implementation solve (BPD-2).

This is a minimum-weight set cover on **mechanism pairs**. MP-02 covers alternatives against one distinguished baseline. That special form makes its adaptive and nonadaptive worst-case costs equal; multiway identification has a different result.

**BPD-01/T2 (optimal adaptive decision tree, finite theorem).** For any surviving candidate subset \(A\subseteq H\), define \(D(\{h\})=0\) and

\[
D(A)=\min_{e\colon r_e=1,\,|\Pi_e(A)|>1}
\left[w_e+\max_{B\in\Pi_e(A)}D(B)\right],
\tag{BPD-3}
\]

where \(\Pi_e(A)\) partitions \(A\) by the observed categorical response. The value is infinite if no informative cell exists. This recurrence equals optimal worst-case identification cost for deterministic adaptive policies. **Proof.** Every valid decision tree chooses some informative first cell and must solve its realized response class. Condition on the first response for the lower bound; attach optimal subtrees for the upper bound. Strictly smaller response classes make the recursion well founded. Consequently \(D(H)\le C_{\rm batch}\), with strict inequality possible.

A four-mechanism witness has three unit-cost probes with outcome rows

| Probe | h0 | h1 | h2 | h3 |
|---|---:|---:|---:|---:|
| root | 0 | 0 | 1 | 1 |
| left | 0 | 1 | 0 | 0 |
| right | 0 | 0 | 0 | 1 |

A fixed separating batch needs all three. Querying `root`, then only `left` or `right` according to the answer, needs at most two. Turning off routing for `left` makes \(h_0,h_1\) indistinguishable; both optimizers correctly return infeasibility.

## 2. Clock and visibility as measurable finite fibres

To compare causal-importance predictors, collect **intervention labels** on records indexed by `(case, component, intervention type, state, pass, visible)`. The binary label is a declared intervention outcome, such as a thresholded change in the exact proof-checker result. It is not silently replaced by a final-answer correctness label. For any feature projection \(\phi\), let \(F_z=\{i:\phi(i)=z\}\) be the resulting finite fibres, with integer weights \(a_i>0\) and binary labels \(b_i\).

**BPD-01/T3 (finite feature-fibre error floor, algebraic identity).** Among all deterministic binary predictors allowed to inspect only \(\phi(i)\), the minimum weighted 0-1 error is exactly

\[
L^*(\phi)=\sum_z \min\!\left(\sum_{i\in F_z:b_i=0}a_i,\sum_{i\in F_z:b_i=1}a_i\right).
\tag{BPD-4}
\]

**Proof.** A deterministic predictor must issue one label per fibre. Choosing the majority label minimizes errors independently on each fibre; summing achieves the lower bound. Ties admit either choice. This result needs no statistical model and is exact even if all component labels are wrong; causal interpretation requires separately validated interventions.

Compare three projections with `case`, `component` and `intervention` always fixed:

- **state-only:** add the carried-state identifier;
- **state + clock:** add the same state identifier and pass index;
- **visible-only:** add the projected head-readable identifier.

The state + clock projection refines state-only, so \(L^*_{\mathrm{state+clock}}\le L^*_{\mathrm{state}}\). A strict gap **certifies that the observed labelled records cannot be fit by a deterministic state-only importance rule**. A visible-only gap certifies loss of information relative to the tested richer interface only when comparing on the same cases and labels. It does not establish that the hidden representation is intrinsically uninterpretable or that clocks cause differences without controlled trajectory matching.

A finite test contains two records at the same carried state and component, at passes 0 and 1, with labels 0 and 1. Adding the clock reduces the irreducible error from one to zero. A third record changes full state while preserving visible readout, exhibiting the visible collision. Identical state IDs must be produced by a calibrated matching protocol; rounded embedding hashes do not certify exact state equality.

## 3. Refill makes final-only importance underestimate path importance

**BPD-01/T4 (synthetic counterexample).** Let a loop refresh a one-bit carried component from an input bit \(x=1\) at each of \(T\ge2\) boundaries. Erasing the component at any boundary \(t<T\), immediately after its refresh, changes that boundary's state but the later refresh reconstructs it. The final output is unchanged. Erasing it at every boundary changes the final output from 1 to 0. A final-output-only oracle marks the early single cuts irrelevant, whereas a per-boundary trajectory oracle detects them. The implementation enumerates the single-cut trajectories and persistent-cut final state; it has no claim to simulate TRM or measure a learned fixed point.

Therefore report **single-pass** interventions, **all-pass** interventions, intermediate readouts, and separate final verdicts. For weight-tied operators the proposed decomposition shares component matrices across passes; an optional clock may alter the *mask policy*, rather than the shared weight identity. Report raw effects and rotation-null-calibrated effects separately, with ablation replacement semantics recorded.

## 4. Driving the next Lean gym

A useful BPD item is a `(source theorem, original Lean goal state, concrete action, component edit, recurrent pass, independent outcome)` record. FC-12 already compiles parameterized `exact`, `rw`, `rcases`, and `induction` candidates against source Lean theorems. Its training-only positive incidence graph may propose new queries, but an *unprobed* tactic is **unknown**, not negative. Candidate success, goal-count progress, exact source SHA, and compiler diagnostics belong in the outcome. All final proofs require kernel replay; a syntactic or learned label alone supplies no proof.

The next corpus should combine matched one-factor changes in distractor rules, required Horn closure depth, candidate action family, and pass budget. Split by original theorem root **before** any variants, ablations, or traces are generated. Record collision groups, impossible goals with independently checked countermodels, and full intermediate distributions or traces. A public theorem whose tactic outcome is memorized is a separate contamination stratum.

Use the following acceptance gates before calling BPD components identifiable:

1. **Routed coverage:** every declared mechanism pair has an actually observed separating cell. Report the number unresolved and the exact batch/adaptive budgets.
2. **Causal relevance:** paired edit changes an independent Lean proof/search outcome or intermediate state; maintain the same source and budget across arms. Track model error separately from compiler reject/timeout.
3. **Unsaturation:** log per-case intact and edited probabilities, including rare cases where a flip occurs. Allocate repetitions from [QI-02](active_quotient_information_budget.md) only when Bernoulli interior and conditional IID assumptions hold.
4. **Negative controls:** keep no-op, source-matched rotation, route failure, early single cut and persistent cut as distinct arms. Calibration-only choice of rotation-null tolerance avoids selecting on evaluation labels.
5. **Clock ablation:** compare state-only, state + pass, and visible-only selectors under matched decomposition rank, compute and search budgets. Use (BPD-4) to test whether the *data interface* can reveal a gap before training a predictor.

The linked LoopedTransformers adapter specifies an additional generated Lean candidate bank with its own theorem-root-disjoint split and a host-owned compiler gate. That generator is **synthetic training material**, kept separate from FC-12's original MathCan data and its test set. No learned advantage follows from the mathematical examples here.

## 5. Verification and scope

`evaluation_bpd.py` implements (BPD-2) with a pivot-based bitmask recurrence and an independent exhaustive enumeration; (BPD-3) uses explicit response partitions over subsets of surviving worlds. Unit tests cover all \(8^3=512\) three-hypothesis binary three-probe matrices, 96 seeded categorical and weighted/routed cases, routing collisions, invalid records, weighted feature fibres, and refresh counterexamples. The source-hashed verifier regenerates `output/evaluation_bpd/bpd_01.json`.

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_evaluation_bpd.py' -v
PYTHONPATH=src python scripts/verify_evaluation_bpd.py
python scripts/check_receipts.py --only bpd
```

These checks certify finite computations and source integrity. General identities T1–T3 have the mathematical proofs stated above; no Lean formalization has yet been performed. The adaptive recurrence and set cover are classical ideas in finite decision theory. BPD-01 contributes their explicit causal-observation contract, pass-visibility budget and deployment gates for this research programme.
