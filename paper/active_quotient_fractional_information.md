# QI-03: A fractional information-cover lower bound for active quotient identification

**2026-11-04.** Builds on [QI-02](active_quotient_information_budget.md), [QI-01](active_quotient_identifiability.md), and [MP-02](metaprune_set_cover.md). Mathematical components are established bandit change-of-measure inequalities and classical fractional set cover, assembled here as a finite, exact-rational **evidence-budget certificate**. The result does not prove that a query allocation attaining the lower bound exists. No neural system, hidden biological state or learned controller is evaluated.

## 1. Multi-alternative baseline-versus-capacity decision

Fix a known, addressable set of n transient state/action cells \(c=1,\ldots,n\), each returning one IID Bernoulli observation upon reset and probing. The evaluator has a baseline world W_0 and a finite list of alternative worlds W_j, indexed by j=1,...,m. All true and alternative Bernoulli rates are strictly inside (0,1), ensuring finite likelihood-ratio divergences.

The controller must decide **baseline vs alternative** with false-rejection probability at most \(\delta\) under W_0 and false-acceptance probability at most \(\delta\) under **each** W_j, for \(0<\delta<1/2\). Each probe cell c has positive cost \(w_c\). Queries may be selected adaptively from the public history and a declared independent random tape, and stopping may depend on outcomes. Let \(N_c\) be its probe count, \(\mathbb E_0\) expectation under W_0, and

\[
\beta_\delta
=\operatorname{kl}(1-\delta,\delta)
=(1-2\delta)\log\frac{1-\delta}{\delta}.
\]

The QI-02 KL chain rule and binary-event data processing give **one necessary constraint per alternative**:

\[
 \boxed{
 \sum_{c=1}^n
 \mathbb E_0[N_c]\,
 \operatorname{kl}(p_{0c},p_{jc})
 \ge\beta_\delta,\qquad j=1,\ldots,m.
 }
\tag{1}
\]

The conclusions hold for bounded-horizon policies; the stopped version assumes almost-sure termination and the standard finite-information integrability conditions. QI-02 records the exact two-world proof and precedents in bandit lower bounds.

## 2. QI-03/T1: fractional hitting set as a necessary evidence budget

Specialize to a **binary-incidence family**. There are two fixed interior probabilities p and q with \(\kappa=\operatorname{kl}(p,q)>0\). World W_0 has rate p in every cell. Alternative W_j has rate q in the cells of a specified nonempty subset \(C_j\subseteq\{1,\ldots,n\}\), and rate p in every other cell.

Then (1) becomes

\[
 \kappa\sum_{c\in C_j}\mathbb E_0[N_c]\ge\beta_\delta.
\]

With scaled expected counts \(x_c=(\kappa/\beta_\delta)\mathbb E_0[N_c]\), define the **fractional hitting-set** linear program

\[
 \begin{aligned}
 \tau_f(C,w)=
 &\min_{x\in\mathbb R^n_{\ge0}}\sum_c w_c x_c\\
 &\text{subject to }\sum_{c\in C_j}x_c\ge1
       \quad\forall j.
 \end{aligned}
\tag{2}
\]

**Theorem T1.** Every policy satisfying the stated error guarantees obeys

\[
 \boxed{
 \mathbb E_0\Big[\sum_c w_c N_c\Big]
 \ge \frac{\beta_\delta}{\kappa}\,\tau_f(C,w).
 }
\tag{3}
\]

**Proof.** The scaled vector of expected cell counts is feasible in (2), as shown by the QI-02 constraints. Its weighted sum is \((\kappa/\beta_\delta)\) times the baseline expected query cost, and must be at least the LP minimum. Rearrange. QED.

Because the masks are 0/1 and each cost positive, truncating any \(x_c>1\) to 1 preserves every covering constraint and decreases its cost. Hence an optimum can be found in \([0,1]^n\), where a bounded rational polytope has a vertex optimum. For the finite input class, the rational optimum is attained even though the scale \(\beta_\delta/\kappa\) typically involves logarithms.

If some alternative has no changed probe cells, its model is statistically indistinguishable from the baseline under the declared interface. Then (2) is infeasible and the demand for two-sided error less than 1/2 cannot be satisfied.

## 3. QI-03/T2: an exact primal/dual certificate

The LP dual of (2) is

\[
 \boxed{
 \max_{y_j\ge0}\sum_j y_j
 \quad\text{subject to }
 \sum_{j:c\in C_j}y_j\le w_c
 \quad\forall c.
 }
\tag{4}
\]

Primal feasibility, dual feasibility, and equality of their rational objectives certify a global optimum via weak duality, independently of how the candidate assignments were found.

The [reference module](../src/spiral_ln/evaluation_quotient_fractional_cover.py) enumerates all small rational active-constraint vertices for both LPs using a handwritten Gauss–Jordan solver. It then checks primal and dual inequalities and their exact objective equality. **This is a finite verification oracle** with at most six cells and ten alternatives, whose exponential work is intentional; it is not a scalable LP solver. A general LP algorithm is available for larger instances.

The exact objective of an *integer* hitting set, where each \(x_c\in\{0,1\}\), is an upper bound on \(\tau_f\). Since the KL lower bound only constrains **expected counts**, replacing \(\tau_f\) by the integer optimum would generally produce an invalid stronger lower bound.

## 4. Exact integrality-gap witness and a direct-sum result

Take **three alternatives and three probe cells**, with changed-cell sets

\[
 C_1=\{1,2\},\quad C_2=\{2,3\},\quad C_3=\{1,3\},
\]

and unit cell costs. Every integral covering set needs at least two cells, so its cost is 2. The feasible rational primal assignment \(x=(1/2,1/2,1/2)\) has cost 3/2. The same assignment \(y=(1/2,1/2,1/2)\) is dual-feasible with value 3/2. Weak duality proves

\[
 \boxed{\tau_f=3/2,\qquad \tau_{\rm integer}=2.}
\]

For p=1/2, q=5/8 and \(\delta=1/20\), QI-02's scalar lower bound \(\beta_\delta/\kappa\approx82.121345\) gives an expected **total** probe lower bound of \(\approx123.182018\), with every uniformly capped procedure requiring a cap of **at least 124** queries. The integer cover value 2 would suggest 164.24 queries, which is stronger than the information argument licenses.

For the **distinct-cell family** \(C_j=\{j\}\) for j=1,...,n, each alternative must be distinguished using its own addressable cell. Every LP constraint independently forces \(x_j\ge1\), giving \(\tau_f=n\) for unit costs and

\[
 \boxed{
 \mathbb E_0[N_{\rm total}]
 \ge n\frac{\beta_\delta}{\kappa}.
 }
\tag{5}
\]

For n=3 under the same rates and risk, the necessary total expected observations are at least 246.364..., so any hard total-query cap must be **at least 247**. This direct-sum theorem is a deduction from the well-known bandit change-of-measure method. It does not assert an attainable adaptive testing design at that budget.

## 5. Finite audit and relation to experiment allocation

- [evaluation_quotient_fractional_cover.py](../src/spiral_ln/evaluation_quotient_fractional_cover.py) computes primal and dual rational optima and verifiable witnesses, a separate integer subset-cover oracle, a separate half-grid reference for three-cell instances, and numerical Bernoulli information scaling.
- [test_evaluation_quotient_fractional_cover.py](../tests/test_evaluation_quotient_fractional_cover.py) exhaustively checks all **127** nonempty subsets of the seven possible nonzero three-cell masks, including strict integrality gaps and exact primal/dual objective agreement. Additional seeded four/five-cell tests use heterogeneous rational query costs. It checks the triangle, single-cell direct sum, inaccessible-alternative case and bad inputs.
- The dedicated least-privilege GitHub workflow runs the rational test suite on every branch/PR update. The existing EvalMath verify workflow separately runs the full repository's Python, Lean and source-receipt checks.

The evaluation budget in QO-08 is deliberately small compared with some of these information floors. That comparison is motivational: QO-08's actual alternative models and tolerance decisions differ from the QI-03 binary-incidence hypothesis family, so one should **not** transfer the numerical floors to QO-08 without a validated reduction of its decision contract.

**Next experiment:** choose a finite candidate family and a genuine prior, then use the fractional-cover weights to propose cost-aware query allocations, comparing their held-out performance against simple round-robin and confidence-width allocation under the same risk criterion. The LP solution is a *lower-bound witness*, not a certified optimal adaptive policy.

**References:** Kaufmann, Cappé & Garivier, [On the Complexity of Best-Arm Identification in Multi-Armed Bandit Models](https://jmlr.org/papers/v17/14-066.html), JMLR 2016; Lattimore & Szepesvári, [Bandit Algorithms](https://tor-lattimore.com/downloads/book/book.pdf), Chapter 15; and classical LP duality/SET COVER.
