# Adaptive disclosure: exact transcript fibres and an interval-query separation

Draft 0.1, 2026-10-26. **Evidence:** algebraic identities under a declared deterministic finite model, backed by exact finite checks. This note develops a feedback-composition question adjacent to [evaluation feedback composition](evaluation_feedback_composition.md), [the lattice](evaluation_feedback_lattice.md), and [leak topology](leak_topology.md). The finite-capacity perspective of [PR #1](https://github.com/MoralityLabAI/EvalMath/pull/1) motivates distinguishing a rational kernel from an actually feasible count-table collision. The new implementation is independent of that PR and imports none of its code. No language model, evaluator or learning algorithm is run.

Module `src/spiral_ln/evaluation_adaptive_disclosure.py`; tests `tests/test_evaluation_adaptive_disclosure.py`; verifier `scripts/verify_evaluation_adaptive_disclosure.py`; receipt `output/evaluation_adaptive_disclosure/adaptive_disclosure_v0_1.json`. All probabilities are `Fraction`s.

## 1. The experiment and its channel

Fix a count table \(x=(x_1,\ldots,x_d)\) with \(x_i\in\{0,\ldots,s_i\}\) and \(s_i\ge1\). A prior \(w_x/W\), with positive integer weights \(w_x\), is declared on a nonempty set \(\Omega\) of feasible tables; \(W=\sum_{x\in\Omega}w_x\). The *full-box, independent-fair-bit* prior uses \(\Omega=\prod_i\{0,\ldots,s_i\}\), \(w_x=\prod_i\binom{s_i}{x_i}\), and \(W=2^{\sum_i s_i}\). This is a prior on cell counts, which can represent multiple underlying raw bit records per table.

A query \(q\in\{0,1\}^d\) reports the exact subset sum \(y=q\cdot x\). A deterministic adaptive policy is a rooted, finite tree. Every internal node chooses a query from a declared bank based on the responses on its preceding path; edges correspond to responses; leaves halt. The *transcript* records **both** the chosen query indices and their answers. Policies can stop early; the maximum depth is the query budget. Every query reads the same fixed hidden table throughout the experiment. A changing learner state, noisy score, or randomized controller would need additional state and is outside the theorem.

**Theorem 1 (pathwise exactness).** Let \(t=((q_1,y_1),\ldots,(q_\ell,y_\ell))\) be a reachable leaf transcript and \(A_t\) the matrix with query rows \(q_i\). Then its observational fibre is exactly

\[
 F_t=\{x\in\Omega:A_tx=(y_1,\ldots,y_\ell)^T\}.
\]

*Proof.* The policy's first query is fixed. If a table satisfies the first answer equation, it takes the corresponding edge. Along that edge the second query is determined by the observed answer, and so on by induction. Conversely every table producing the transcript satisfies each equation. The same proof works for any finite declared support \(\Omega\). \(\square\) **Evidence: algebraic identity.**

A particular leaf contains two different feasible cell tables iff there exist \(z\in\ker_{\mathbb Z}A_t\setminus\{0\}\) and \(u\in\mathbb Z^d\) such that

\[
 0\le u_i,u_i+z_i\le s_i,\qquad A_tu=y_t,
\]

with both tables \(u,u+z\in\Omega\). If \(\Omega\) is the full box, the last support requirement is automatic. The right-hand side \(y_t\) and the path's actual rows must be retained. For example, one query \(q=(1,1)\) has a rank-one kernel, but the reachable leaf with response zero contains only \((0,0)\) for unit capacities. The response-one leaf contains \((0,1)\) and \((1,0)\).

A global matrix formed by stacking *all queries appearing anywhere in the policy tree* can misstate disclosure. With two bits, first read bit 0; if its answer is zero read bit 1, and if one repeat bit 0. Both singleton queries occur somewhere in the tree, giving a full-rank union. Yet \((1,0)\) and \((1,1)\) generate the same transcript. **Evidence: algebraic counterexample**, checked exactly in the receipt. A policy ledger therefore needs path-dependent query identities and answers.

## 2. Exact collision and reconstruction laws

**Theorem 2 (transcript collision law).** Write \(m_t=\sum_{x\in F_t}w_x\). For two independent draws from the declared prior, the probability of identical transcripts and the probability of identical joint cell tables are

\[
  \mathrm{CP}(T)=\frac{\sum_t m_t^2}{W^2},\qquad
  \mathrm{CP}(X)=\frac{\sum_x w_x^2}{W^2}.
\]

The Bayes probability of recovering the *cell-count table* from one transcript under zero-one loss is

\[
  \mathcal B(T)=\frac{1}{W}\sum_t\max_{x\in F_t}w_x.
\]

*Proof.* The fibres partition the prior support. Draws agree on the transcript precisely when they fall in the same fibre. Conditional on a fibre, guessing a maximally weighted table minimizes zero-one loss. Summing the resulting probabilities proves all formulas. \(\square\) **Evidence: algebraic identity.** A collision ratio \(\mathrm{CP}(T)/\mathrm{CP}(X)>1\) exactly detects distinct feasible count tables with identical transcripts when all declared weights are positive. The ratio isolates the disclosure loss **relative to a joint cell-count oracle**; it does not measure ambiguity between two raw records sharing the same cell counts.

**Proposition 3 (exact incremental composition).** At a reached node \(h\), let \(m_{h,a}\) be the prior masses of its response children. Define \(\mathrm{CP}_j\) as the probability that two independent draws have matching transcripts through depth \(j\), treating a halted leaf as a single continuing child. Then

\[
\mathrm{CP}_j-\mathrm{CP}_{j+1}
=\frac{2}{W^2}\sum_{h:\,|h|=j}\sum_{a<b}m_{h,a}m_{h,b}\ge0.
\]

*Proof.* Each parent mass equals the sum of its child masses; subtract the sums of squares at consecutive depths. \(\square\) **Evidence: algebraic identity.** This decomposition prices *actual conditional splits*. It does not assume that successive linear-query ranks add.

Let \(L\) be the number of reachable leaves and \(a_j\) the maximum number of reachable next responses at any history of depth \(j\), counting a halted history as one successor. Then \(L\le\prod_j a_j\). The Shannon entropy of the entire transcript obeys \(H(T)\le\log_2L\le\sum_j\log_2a_j\). This is the ordinary finite-alphabet entropy bound applied to the path tree; it is valid despite adaptively selected queries. We calculate \(L\) and the alphabet bound exactly; no floating-point Shannon values enter the verifier.

**Proposition 4 (Bayes-optimal adaptive policy recurrence).** For a nonempty posterior subset \(B\subseteq\Omega\), let \(V_0(B)=\max_{x\in B}w_x\). With \(k\ge1\) queries left and a finite bank \(\mathcal Q\), the maximum *unnormalized* probability of exact table reconstruction is

\[
 V_k(B)=\max_{q\in\mathcal Q}\ \sum_{a:q^{-1}(a)\cap B\ne\varnothing}
    V_{k-1}(B\cap\{x:q\cdot x=a\}).
\]

Stopping is allowed, and the recurrence remains valid because continuing with a constant query retains the same optimal value. *Proof.* Condition on the first chosen query and its response. Subsequent subproblems can be optimized independently because the resulting policies may differ by branch. Backward induction proves optimality. \(\square\) **Evidence: algebraic identity.** The executable dynamic programme also allows termination when further queries cannot improve success. A separate exhaustive optimizer searches fixed query schedules, including repetitions.

## 3. A sharp adaptive advantage for interval feedback

Assume **exactly one** of \(n\ge1\) cells contains a marked bit, with a uniform prior on its location. A query may select any nonempty contiguous interval of locations and report its total. Under this *one-hot* promise the reply is binary, even though the general query interface reports counts.

**Theorem 5 (interval separation).** With an allowance of at most \(k\ge1\) queries, the largest number of one-hot locations distinguishable by any fixed schedule is \(\min(n,2k)\). The corresponding maximum for an adaptive schedule is \(\min(n,2^k)\). For \(k=0\), each strategy has one transcript. Hence their optimal exact-reconstruction probabilities under the uniform one-hot prior are these counts divided by \(n\).

*Proof (fixed upper bound).* Each fixed interval defines one coordinate of a binary membership signature as the marked location moves from left to right. Insert virtual positions on either side of the line where every coordinate is zero. Each interval turns on and off at most once, so the entire signature walk contains at most \(2k\) changes. Its initial and final signatures coincide. A closed walk with \(r\) changes visits at most \(r\) distinct signatures, giving at most \(2k\), and trivially at most \(n\).

*Proof (fixed attainment).* On \(2k\) consecutive locations use the \(k\) intervals \([i,i+k)\), \(i=0,\ldots,k-1\), indexed from zero. Scanning the locations, the first \(k\) successive positions turn on a new membership bit and the final \(k\) positions turn them off. All \(2k\) location signatures are distinct. Restrict to the first \(n\) locations if \(n<2k\), trimming or omitting empty intervals. The bound is attained.

*Proof (adaptive).* Each reply is one bit, so a depth-\(k\) decision tree has at most \(2^k\) leaves. Conversely the current possible positions always form an interval. Querying approximately half that interval divides the candidates into two contiguous subsets. Recurse by response. This realizes \(\min(n,2^k)\) nonempty leaves; when \(n<2^k\), halt after identifying a singleton. \(\square\) **Evidence: algebraic identity.**

**Exact fixture, \(n=8,k=3\).** Adaptive three-round interval search identifies all eight locations, so its Bayes success is 1 and transcript collision probability is \(1/8\). A fixed three-query schedule produces at most six distinct transcripts, yielding best reconstruction probability \(6/8=3/4\). The exact fixed optimizer enumerates all 8,436 interval schedules with replacement from the bank of 36 intervals and finds the optimum 6; its witness has transcript collision probability \(7/32\). The algebraic optimum and the independent enumerator agree. The witness is *finite verified example*; the formula for all \(n,k\) is *algebraic identity*. The advantage arises under the one-hot prior and interval restriction. As an exact control, three fixed **unrestricted** subset queries that return the three binary digits of the location distinguish all eight possibilities, matching the adaptive success of 1. This isolates the interval restriction as an essential hypothesis. The result says nothing general about unrestricted scoring queries or independent fair bits.

## 4. Reproduction and boundaries

Run `python -m pytest tests/test_evaluation_adaptive_disclosure.py -q` and `python scripts/check_receipts.py --only adaptive_disclosure`. The verifier checks 32 \((n,k)\) combinations with \(1\le n\le8\), \(0\le k\le3\) against separate adaptive and fixed optimizers. For five full-box independent-fair-bit priors and four fixed policies apiece, it compares exact cell-table mass aggregation against independent enumeration of the original binary records (20 comparisons). All source file SHA-256 values and the deterministic case digest are embedded in the receipt. The entire repository's fast receipt suite runs in GitHub Actions.

Proofs are given on paper; no new Lean theorem is claimed. Exhaustive optimizers grow exponentially and target declared finite states. All policies here are deterministic, queries return perfect sums of a fixed table, and stopping is free. For genuinely changing model policies, stochastic graders, real-valued scores, or reusable examples that are rewritten during training, extend the hidden state and transition kernel before applying these formulas. A useful next direction is to derive a version of the pathwise collision recurrence for stochastic responses and a finite-horizon state transition, then determine whether an empirically observed trajectory remains inside its predicted uncertainty envelope.
