# MP-02: A set-cover lower bound on adaptive scientific experiment selection

**Status 2026-11-04:** finite deterministic mathematical theorem with proof, exact independent CPU oracles, and source-code tests. It is a specific model of **zero-error hypothesis discrimination** using known binary observation kernels. It makes no claim that scientific judgment generally reduces to set cover or that real neural agents have these exact costs.

## Model

Let \(U=\{1,\dots,n\}\) be a finite set of alternative hypotheses, and let \(h_0\) be a distinguished baseline hypothesis. The true hidden world is one of \(h_0,h_1,\dots,h_n\). Every available experiment \(e\) is identified with a known subset \(C_e\subseteq U\) and returns a **deterministic binary outcome**:

\[
Y_e(h_0)=0,\qquad
Y_e(h_i)=\mathbf 1[i\in C_e].
\tag{1}
\]

Experiments have unit cost, and a policy may adapt its next experiment to every previous result, including stopping. It must decide the binary proposition "is the world \(h_0\)?" with **zero error for every declared hypothesis**. We minimize the maximum number of tests used on any hidden world. If some alternative is never separated from \(h_0\), no zero-error policy exists.

## MP-02/T1: exact adaptive experiment complexity

Let \(c^*\) be the minimum number of experiment subsets whose union covers \(U\). Define \(d^*\) as the least worst-case test count among all deterministic binary decision trees giving the correct baseline/alternative answer under (1).

\[
\boxed{d^* = c^*.}
\tag{2}
\]

If \(U\) cannot be covered by the available experiments, both optima are infinite.

**Proof, lower bound.** Take any zero-error adaptive decision tree, and follow the path induced by \(h_0\). Every response on that path is zero. Suppose the tests on that path are \(e_1,\dots,e_q\). If there were an alternative \(h_i\) with \(i\notin \bigcup_{j=1}^{q}C_{e_j}\), it would return zero on every one of those tests and follow **exactly the same path** as \(h_0\), reaching the same terminal decision. Since the policy must return "baseline" on \(h_0\), it would then err on \(h_i\). Thus the tests along the baseline path form a set cover and \(q\ge c^*\). The worst-case tree depth is at least \(q\), giving \(d^*\ge c^*\).

**Proof, upper bound.** Given a set cover \(C_{e_1},\dots,C_{e_{c^*}}\), query those tests in any fixed order, terminate with "alternative" at the first positive result, and return "baseline" if every result is zero. Every alternative is covered and therefore triggers a positive result somewhere, while \(h_0\) returns only zeros. The worst-case count is \(c^*\), so \(d^*\le c^*\). QED.

**Corollary (positive costs).** Replace unit experiment costs by strictly positive known costs \(w_e\), and minimize worst-case total cost. The same baseline-path argument yields equality with the **minimum-weight** set cover cost, since a positive result can terminate immediately and the all-negative baseline path pays the full selected cover cost. This is a deduction under the same deterministic response contract; the supplied CPU reference tests the unit-cost case.

**MP-02/T2 (restricted NP-completeness).** Given \(U\), the explicit subsets \(C_e\), and budget \(k\), deciding whether a zero-error adaptive policy with worst-case test count at most \(k\) exists is NP-complete. Equation (2) is a polynomial reduction from **SET COVER**, a classical NP-complete problem (Karp, 1972), while a collection of at most \(k\) subset indices whose union is \(U\) is a polynomially checkable certificate.

This is a restricted zero-error binary decision-tree problem, not a complexity result for Bayesian information-gain maximization or uncertain/misspecified experiments.

## Independent finite verification

The reference module [evaluation_metaprune_cover.py](../src/spiral_ln/evaluation_metaprune_cover.py) provides:

- a memoized exact minimum-cover recurrence over bitmasks of uncovered alternatives;
- an **independent brute-force subset oracle** enumerating combinations of experiments;
- a separate **generic belief-state minimax decision-tree oracle** which considers all informative binary experiments and recursively optimizes both possible outcomes, without using the set-cover recurrence.

[test_evaluation_metaprune_cover.py](../tests/test_evaluation_metaprune_cover.py) compares these three algorithms across all \(8^3=512\) three-alternative/three-experiment mask matrices, 125 seeded larger cases, an explicit coverable case, and an example with a permanently indistinguishable alternative. It also checks invalid inputs. This is **finite software verification** of the model and theorem witness; neither independent oracle constitutes a general proof.

Reproduce:

    PYTHONPATH=src python -m unittest discover -s tests -p 'test_evaluation_metaprune_cover.py' -v

The full repository CI also runs the test module during its standard verification suite. Source hashes are captured by Git commit IDs; this note has no checked-in claim receipt and is not yet included in EvalMath's certified findings.

## What this says about meta-research agents

A sophisticated policy may appear capable of adapting research directions after observations. In this synthetic setting, the expensive branch is the one where the baseline hypothesis continually survives, forcing the controller to accumulate enough **coverage** to rule out every alternative. The adaptive policy's apparent flexibility cannot reduce that worst-case cost.

Combined with [MP-01](metaprune_decision_value.md), this makes a useful two-part benchmark:

- For Bayesian nonzero-error problems, evaluate experiment choice by the declared **terminal decision utility**, rather than assuming maximum entropy reduction is optimal.
- For zero-error baseline discrimination, verify the exact **covering obligation** and budget before declaring a scientific hypothesis resolved.

For a larger research system, the *identities of independent evidence sources* must also survive state compression. Existing [selection-risk](selection_risk_continuations.md) and [full-filtration validity](dynamic_filtration_validity.md) notes describe risks from adaptively selected or privately observed evidence. MP-02's deterministic test contract assumes the entire hypothesis/test response matrix is known and trustworthy; real observations may violate this assumption.

## References and scope

- R. M. Karp, [Reducibility Among Combinatorial Problems](https://doi.org/10.1007/978-1-4684-2001-2_9), 1972 (SET COVER among the original NP-complete covering problems).
- [QO-03](https://github.com/MoralityLabAI/Compactification-Theory/blob/main/research/ingression_dynamics_v1/MULTIACTION_COLORING.md), the separate **graph-coloring boundary** for selecting state partitions under multiple actions.

The novelty claim is deliberately narrow: a transparent crosswalk from known covering and decision-tree mathematics into a reproducible evaluator for *research-budget selection*. No empirical advantage of a learned controller, autonomous science result, or theoretical AGI scaling law follows from the finite theorem.
