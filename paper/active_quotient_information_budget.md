# QI-02: An information-budget lower bound for active quotient identification

**2026-11-04.** A finite Bernoulli-bandit change-of-measure theorem applied to the addressable hit/hold quotient identification interface of [QI-01](active_quotient_identifiability.md) and the anytime confidence-sequence optimizer in [QO-07](https://github.com/MoralityLabAI/Compactification-Theory/blob/main/research/ingression_dynamics_v1/ANYTIME_ACTIVE_QUOTIENT.md). The information-theoretic identity is established prior art, especially Kaufmann, Cappé & Garivier (2016) and Lattimore & Szepesvári (2020). This work provides a specifically scoped lower-bound contract and independent small exact-transcript oracles. No general scientific intuition, neural transfer or AGI claim follows.

## 1. Addressable conditional observations

Let C be a finite set of public state/action probe cells. Under world W_0, cell c emits IID Bernoulli(p_c) observations; under W_1 it emits IID Bernoulli(q_c) observations. Assume both rate vectors are in the **strict interior** (0,1)^C, which guarantees finite KL divergences and common finite-transcript support.

A policy chooses each new cell using only previous public cells/outcomes and optional private randomization independent of the world. It eventually decides whether W_0 or W_1 is true, possibly stopping adaptively. Let N_c be the total number of queries to cell c. For the stopped transcript distribution P_0 and P_1, write

\[
\mathrm{kl}(p,q)=p\log(p/q)+(1-p)\log((1-p)/(1-q)).
\]

**QI-02/T1 (adaptive transcript KL decomposition):** For any bounded-horizon policy,

\[
\boxed{\mathrm{KL}(P_0\Vert P_1)
=\sum_{c\in C}\mathbb E_0[N_c]\,
\mathrm{kl}(p_c,q_c).}
\tag{1}
\]

The same identity extends to almost-surely terminating policies when the expected information and appropriate interchange/integrability conditions are satisfied.

**Proof.** Factor the probability of an observed action/reward sequence into the predictable policy's action probabilities and the conditional Bernoulli response factors. The policy factors are identical under W_0 and W_1 and cancel in the likelihood ratio. The log-likelihood ratio is therefore the sum, over each queried cell, of log(dBern(p_c)/dBern(q_c)) for that observation. Condition on the past action selection to obtain expected increment kl(p_c,q_c) and sum by the tower property. For bounded stopping the sum is finite, so expectation and summation can be interchanged directly. QED.

The result specializes the standard **bandit divergence decomposition** (Lemma 1 in Kaufmann, Cappé, Garivier, 2016; Lemma 15.1 in Lattimore & Szepesvári, 2020).

## 2. Lower bound for a reliable quotient decision

Let E be the terminal event "decide W_0". Suppose a procedure has false rejection and false acceptance probabilities **each at most** \(\delta\), for a fixed \(\delta\in(0,1/2)\):

\[
P_0(E)\ge1-\delta,\qquad P_1(E)\le\delta.
\]

Data processing for the binary event implies

\[
\mathrm{KL}(P_0\Vert P_1)\ge
\mathrm{kl}(P_0(E),P_1(E))
\ge\mathrm{kl}(1-\delta,\delta).
\]

Hence the experiment budget obeys

\[
\boxed{
\sum_{c\in C}\mathbb E_0[N_c]\,
\mathrm{kl}(p_c,q_c)
\ge
(1-2\delta)\log\frac{1-\delta}{\delta}.
}
\tag{2}
\]

The second inequality follows because binary KL increases with its first argument and decreases with its second when the former exceeds the latter. This is the elementary change-of-distributions lower bound.

If W_0 and W_1 differ **only at one cell c***, all other terms in (2) are zero. It follows that

\[
\boxed{
\mathbb E_0[N_{c^*}]
\ge
\frac{\mathrm{kl}(1-\delta,\delta)}
{\mathrm{kl}(p_{c^*},q_{c^*})}.
}
\tag{3}
\]

A policy subject to a hard uniform total-query cap B must therefore have B at least the ceiling of the right-hand side. This remains true if it expends most queries on the unchanged cells, since those probes contribute zero discrimination information.

**Numerical example.** Let p=1/2, q=5/8, and \(\delta=1/20\). Then

\[
\mathrm{kl}(1/2,5/8)
=-\tfrac12\log(15/16)
\approx0.03226926,
\]

while \(\mathrm{kl}(19/20,1/20)\approx2.64999508\). Consequently a procedure meeting both 5% error limits needs **at least 82.121... expected probes** of the changed cell under W_0. Any uniform hard cap must allow at least 83 probes. This is a lower bound; an optimal finite-sample test may require more.

For p=1/2 and q=1/2+\(\Delta\), the per-cell divergence is \(-\tfrac12\log(1-4\Delta^2)\), approximately \(2\Delta^2\) for small \(\Delta\). Hence the necessary samples are of order \(\Delta^{-2}\log(1/\delta)\). These are classical information-theoretic scaling estimates under two fixed candidate worlds.

## 3. Relevance to exact quotient capacity and QO-08

For one action on two named transient states, compare W_0 rates (1/2,1/2) and W_1 rates (1/2,5/8). Under W_0 an exact goal-preserving quotient has **one transient** macrostate plus the absorbing goal. Under W_1 it requires **two transient** macrostates. The models differ in one addressable cell and satisfy the conditions of (3), so evidence-based capacity detection inherits the sample lower bound.

This complements QI-01's finite-budget *zero-error impossibility* with a quantitative lower bound on two-world error levels. QO-07 supplies *time-uniform upper confidence bounds* for a state/action estimation protocol. Neither result guarantees a particular heuristic policy is optimal. The paired QO-08 study measures selected heuristics under equal simulated query budgets, with the complete results committed to [Compactification-Theory](https://github.com/MoralityLabAI/Compactification-Theory/blob/main/results/paired_probe_pilot/receipt.json).

For an experiment planner, the information accounting suggests estimating the expected discriminatory KL gained **per unit of probe and inference cost**, while keeping uncertainty on unknown alternative rates explicit. This is a proposed future optimization objective and has not been trained or evaluated by QI-02.

## 4. Exact finite computational audits

The reference implementation [evaluation_quotient_information_budget.py](../src/spiral_ln/evaluation_quotient_information_budget.py) enumerates every terminal transcript of a bounded deterministic adaptive policy under two interior Bernoulli worlds. Leaf probabilities and expected per-cell query counts use Python Fraction arithmetic. It independently calculates the full transcript KL from leaf likelihood ratios and the right-hand sum in (1), with floating-point logarithms used only for the information score.

The [tests](../tests/test_evaluation_quotient_information_budget.py) compare the two expressions across fixed-action and outcome-adaptive policies, including early stopping; verify binary-event KL contraction for multiple transcript events; check Pinsker's TV upper bound; and reproduce the 83-probe necessary cap. It also checks that sampling an unchanged cell yields zero discrimination information.

**Evidence level:** QI-02/T1 and equation (2) are established textbook mathematical results with written proofs. CPU checks corroborate finite examples. A general stopped-policy measure-theory theorem, the statistics of real neural probes and a learned experiment policy are not formalized or measured in this PR.

To reproduce:

    PYTHONPATH=src python -m unittest discover -s tests -p 'test_evaluation_quotient_information_budget.py' -v

## References

- Kaufmann, Cappé & Garivier (2016), *On the Complexity of Best-Arm Identification in Multi-Armed Bandit Models*, [JMLR 17(1)](https://www.jmlr.org/beta/papers/v17/kaufman16a.html); see the change-of-distributions lemma.
- Lattimore & Szepesvári (2020), *Bandit Algorithms*, Chapter 15.1, [book page](https://tor-lattimore.com/downloads/book/book.pdf), for divergence decomposition and information-theoretic lower bounds.
