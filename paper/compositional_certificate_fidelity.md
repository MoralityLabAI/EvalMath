# CCF-01: Context-dependent certificate fidelity and zero-error receipt coding

Draft 0.1, 2026-11-25. Evidence: elementary mathematical proofs, exact finite synthetic census, uncompiled Lean draft. No real inference, proof generation, cryptographic attack, or empirical risk estimate.

## Motivation and scope

OpenAI's [October 25 local smoothing manuscript and Lean scope note](https://github.com/openai/math/blob/main/lean/docs/079.md) describe a half-wave estimate with positive Sobolev loss (and a p=2 exception), strict-range Bochner–Riesz and spherical restriction estimates, and Kakeya consequences. Anthropic's [provable inference report](https://www.anthropic.com/research/provable-inference) describes FlashProve, a commitment to model weights and a proof binding prompt and output tokens to the committed computation. The reports motivate two different certificate interfaces: mathematical scope and execution provenance. Neither paper is claimed to establish the theorem below. No upstream bug or independent proof verification is asserted. The scope note is a starting point for a future source-pinned endpoint audit.

The existing EvalMath IRC-02 predictive quotient identifies histories with identical legal future trace laws. CCF-01 changes the contract: the decoder has separately authenticated context and may exclude infeasible states. Distinct authorization signatures may share a receipt label. This is an application of classical zero-error coding with decoder side information (Witsenhausen, 1976), not a claim to have invented graph coloring or zero-error coding.

## 1. Exact receipt theorem

Let X be a finite nonempty set of upstream states, C a finite context set, D_c a declared set of feasible states, and a_c: D_c -> {0,1} the authorization predicate. An encoder e:X -> K is independent of c; a decoder d:C x K -> {0,1} sees context c and the authenticated label e(x). It must satisfy d(c,e(x)) = a_c(x) for every x in D_c. Assume D_c is sound, fixed, and authenticated independently; context and decoder description costs are not charged to the fixed-width label.

Form the undirected conflict graph G on X by adding edge xy iff some c has x,y in D_c with opposite authorization bits.

Theorem (exact coding): e permits an exact decoder iff e is a proper coloring of G. If an edge has equal labels, the same feasible decoder input demands opposite answers. Conversely, in each nonempty feasible context/label cell all bits agree under a proper coloring. Set d to that bit, choosing arbitrary outputs for infeasible cells. Hence the minimum alphabet size is chi(G), and the minimum fixed-width label length is ceil(log2 chi(G)). The Lean draft formalizes the iff only; it does not formalize graph cardinalities.

Any simple graph is realized by a context for each edge with its two endpoints assigned bits 0 and 1. Thus deciding whether an exact code with at most k labels exists is NP-complete for explicit finite contracts when k=3 (reduction from 3-colorability and a polynomial verifier). All-pairs feasible contexts recover equality of full authorization signatures. Partial feasibility instead gives a compatibility graph with potentially multiple optimal partitions.

## 2. Safety/completeness envelopes and rate-distortion

For a fixed e, define L(c,k)=min a_c(x) and U(c,k)=max a_c(x) over feasible x with e(x)=k, omitting empty cells. L is the pointwise greatest universally sound decoder; U is the pointwise least universally complete decoder. Any mixed cell forces a tradeoff. Under a specified probability law mu(c,x) supported on feasible pairs, the unconditional lost authorization mass of L is sum mu(c,x)*(a_c(x)-L(c,e(x))). The unconditional excess authorization mass of U is sum mu(c,x)*(U(c,e(x))-a_c(x)). Both are exact identities; their sum equals mixed-cell mass. Neither quantity is a conditional false-positive rate.

For uniform edge contexts with each endpoint equally likely, each uncut edge creates one mixed cell, containing exactly one false negative under L and one false positive under U. If G has m>0 edges, the minimum of either risk over k-label encoders is (m-MaxKCut(G))/(2m). This is a reduction to a classical combinatorial optimization problem; weighted asymmetric contexts instead induce distinct objectives. In particular a five-cycle has clique number two and chromatic number three. A two-label encoder leaves at least one edge uncut, attaining 1/10 lost authorization or 1/10 excess authorization, depending on which envelope is deployed. Three labels achieve exact authorization. The extra fixed-width bit buys zero ambiguity in this toy example.

## 3. Adaptive selection connection

For N independently drawn feasible pairs and a fixed complete decoder with unconditional excess-authorization probability p, a selector with full visibility of which candidates are false authorizations succeeds with probability 1-(1-p)^N. For equal marginals p and arbitrary joint dependence, the sharp bounds are p <= P(any false authorization) <= min(1,Np), attainable with identical events or maximally separated events. These are union-event bounds under full selector information, not guarantees for an actor who sees only a receipt. For the five-cycle two-label fixture p=1/10, independent N=2 gives 19/100, whereas N=2 identical events give 1/10 and disjoint events give 1/5. Under limited selector transcripts, use EvalMath selection_risk_continuations.md's cellwise maximum, with false-authorization events defined by U and the real state. A sound envelope eliminates this particular semantic authorization error by construction, subject to feasibility and authentication assumptions.

## 4. Reproducible finite census

Enumerate all 2^10=1024 labeled simple graphs on five vertices. Convert each graph to edge contexts, enumerate all 52 restricted-growth partitions, and independently enumerate labeled assignments for k=1,...,5 until a valid coloring is found. All 1024 minima agree and all 1024 decoded contracts are exact. Histogram chi=1:1, 2:375, 3:582, 4:65, 5:1. The Python suite also checks the odd-cycle budget and a nonuniform weighted fixture. Three pytest tests passed locally. No model was run.

Reproduce:
    PYTHONPATH=src python -m pytest -q tests/test_evaluation_ccf.py
    python scripts/verify_evaluation_ccf.py
    python scripts/check_receipts.py --only ccf01
The receipt hashes the module, tests and verifier. Lean draft CertificateContext.lean is not compiled and remains outside the umbrella import until the pinned toolchain build succeeds.

## 5. Next gates

CCF-01B: extend the finite solver to weighted partial-context cells, compare partition search against exhaustive labeled assignments, and compute the Pareto frontier of conservative missed mass vs optimistic false-authorization mass. Register a held-out graph family with fixed context costs. For adaptive selection, compare full-world and transcript-limited selectors under declared correlated joint laws.

CCF-01D: compile the iff theorem using the repository toolchain, audit axioms, formalize exact extremal envelopes and the fixed-width finite-cardinality claim, and integrate the Lean imports after verification. The receipt is registered in check_receipts.py; the full repository runner has not been executed locally.

CCF-02: pin OpenAI manuscript, comparator source and theorem declarations; map each actual quantifier, epsilon, dimension, Schwartz-data condition, and strict-range endpoint. Include the p=2 exception as a specific adversarial mutation control. Audit independently of any cryptographic provenance claim.

CCF-03: pin FlashProve technical report, formal model statement, verifier implementation and format. Record integer arithmetic, model commitment, prompt/output identity, decoding and implementation trust boundaries. Build positive and negative scope pairs, allowing only contexts whose feasibility can be independently checked. A commitment to a model is not a proof of correctness of its emitted mathematical statement.

Integration target: an authenticated receipt binding artifact digest, theorem declaration, environment, assumptions and dependency identity, plus a verified scope decoder. The cardinality theorem concerns mutable receipt labels for a fixed finite contract, not hash lengths, cryptographic security or total storage costs. Changes to the contract require revalidation; there is no guarantee for new contexts.
