# Cryptomania assumption audit (CA-01, 2026-10-27)

**Evidence level:** cited propositions, exact logical deductions within a declared
proposition vocabulary, exact rational Bayesian example, and finite toy-#SAT
tests. This note makes no cryptanalytic claim about real-world keys or
independently reproduced Lean-verification claim.

## Boundary: five worlds versus quantitative hardness

The canonical classical implication chain (read left to right) is

\[
\mathrm{PKE}\Longrightarrow\mathrm{OWF}\Longrightarrow
\mathrm{DistNP}\not\subseteq\mathrm{AvgP}\Longrightarrow\mathrm P\ne\mathrm{NP}.
\]

The converses remain open under the conventional classical formalizations.
The five projections of these four predicates, with impossible combinations
excluded by the implications, form Algorithmica, Heuristica, Pessiland,
Minicrypt, Cryptomania. This is a logical taxonomy. Showing ETH false removes
none of the five worlds. Showing ETH true would exclude Algorithmica.

The schema also encodes SETH => ETH and Gap-ETH => ETH. It deliberately
distinguishes decision ETH from exact-counting #ETH:

\[
\mathrm{ETH}\Longrightarrow\#\mathrm{ETH}.
\]

An exact subexponential #3SAT counter refutes #ETH directly, and because
counting decides satisfiability it refutes ETH. An ETH counterexample that
only decides 3SAT says nothing about #ETH. Neither truth direction provides a
bridge to the classical existence of OWFs or PKE.

The logical engine propagates only the forward truth and backward falsity of
each registered implication. It detects contradictions, does not turn unknown
propositions into false, and validates that every world projection satisfies
the core implications.

## Provenance and what "reported" means

The machine-readable ledger at
configs/cryptomania_assumptions_v1.json includes explicit proposition IDs,
assumptions for the counterfactual scenarios, source links, quantified
problem scopes, review-stage labels, and conditional argument routes.

* unadjudicated trusts no result automatically.
* eth_only asks what follows if ETH is false, without a counting assumption.
* accept_october_2026_reports takes the announced exact #SAT and
  3SUM/APSP/zero-weight-clique algorithms at face value. It is a what-if
  analysis, not a certificate that independent reviewers have accepted them.

OpenAI's October 26 announcement reports a Lean-formalized ETH result and
names Impagliazzo, Paturi and Williams as independent shepherds. EvalMath
[PR #10](https://github.com/MoralityLabAI/EvalMath/pull/10) audits the
manuscript-to-Lean statement and quantitative constants;
[PR #11](https://github.com/MoralityLabAI/EvalMath/pull/11) undertakes an
independent pinned upstream replay. Their review gates are separate from this
assumption graph. The October 2026 3SUM/APSP paper reports polynomial
improvements, and via reductions rules out the established worst-case
zero-weight k-clique hypothesis in its stated parameter regime.

* ETH source: https://openai.com/index/building-scientific-understanding-with-academic-communities/
* Alman and Vassilevska Williams: https://arxiv.org/abs/2610.06783
* Canonical five-world chain: https://researchmap.jp/shuichi.hirahara/published_papers/40816859/attachment_file.pdf
* Fine-grained PKE dependence: https://eprint.iacr.org/2019/625.pdf

## Conditional argument routes

The route checker records premises for named fine-grained PKE, PoW,
SETH-CVP and Gap-ETH-SVP claims and independent LWE/ECDLP hardness questions.
An all_listed_routes_invalidated result means that every listed path
has a false premise in this scenario. It has a narrower scope than "security
broken" or "no alternative theorem exists." An open route has one or more
unknown premises. premises_asserted simply describes the assigned premises;
it is never a security certificate. Unmodeled proof routes are outside scope.

A universal worst-case zero-weight-clique algorithm also runs on instances
sampled from supported average-case distributions. The transfer requires
checking the particular fine-grained PKE construction's distributions,
weight bounds and polynomial exponents. It does not break arbitrary
public-key encryption. Loss of SETH/Gap-ETH lattice lower-bound arguments
likewise does not imply an attack against LWE or a deployed parameter set.

## Credence is a joint distribution

For each world \(w\) and event \(E\), a posterior needs \(P(E\mid w)\):

\[
P(w\mid E)=
\frac{P(E\mid w)P(w)}{\sum_v P(E\mid v)P(v)}.
\]

The exact-rational demonstration chooses a toy prior
\(P(\mathrm{Algorithmica})=1/1000\), all other prior mass summing to
\(999/1000\), and \(P(\mathrm{ETH})=9/10\). With
\(P(\neg\mathrm{ETH}\mid\mathrm{Algorithmica})=1\) and
\(P(\neg\mathrm{ETH}\mid w)=11/111\) for every other world,
Algorithmica rises tenfold to \(1/100\). Under this particular joint model,
Cryptomania moves from \(4/5\) to \(88/111\). Alternative world-conditional
likelihoods yield different updates. The five-world marginal alone cannot
determine the direction or magnitude.

## Tiny exact-count control

cryptomania_toy_count.py constructs seeded 3CNFs with blocks of three
variables and an otherwise identical control joined by bridging clauses.
Two exact counters independently enumerate assignments: the baseline
enumerates all \(2^n\), while the factorized counter multiplies counts on
connected clause-hypergraph components. Eight cases at 6, 9, 12 and 15
variables record exact solution counts, component sizes and an assignment
enumeration proxy. The proxy excludes component discovery and overhead;
it is not timing data. Joined controls remove the factorization advantage.
No general subexponential #SAT result follows from this structured family.

This fixture is useful as a protocol check before using substantially
larger experimental systems: any purported algebraic shortcut must keep
exact count fidelity, define its operation model, survive connected or
adversarial controls, and demonstrate scaling on held-out distributions.

For LWE, decoding, and isogeny-path experiments, preregister reductions,
bit complexity, instance distributions, memory and success probability.
Keep low-dimensional algebraic identities and solver wall-clock traces in
distinct evidence columns. The Semaev work in
patrickdugan/semaev-index-calculus already maintains a separate
count-preservation and gate-census program. No ECDLP speedup is claimed here.

## Reproduce

From the EvalMath root:

~~~bash
PYTHONPATH=src python -m pytest -q tests/test_cryptomania_audit.py
PYTHONPATH=src python scripts/verify_cryptomania_audit.py
PYTHONPATH=src python scripts/verify_cryptomania_audit.py --scenario eth_only
~~~

The verifier emits canonical JSON with source hashes and machine-checkable
Boolean assertions. Every seeded benchmark instance is deterministic; all
arithmetic in the Bayesian example is rational. To add a new assumption,
enter its implication only after checking the exact computational model and
direction of the reduction, then add a counterexample-oriented unit test.
