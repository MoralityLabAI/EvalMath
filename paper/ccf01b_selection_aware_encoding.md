# CCF-01B: Weighted selection-aware receipt encoding

Status: exact finite synthetic witness, source-hashed receipt, independent exhaustive oracles. No empirical model claim. Extends CCF-01 in compositional_certificate_fidelity.md.

## Weighted envelopes

For a context c and code label r, let M(c,r) be the feasible state cell. Let W0 and W1 be the nonnegative total masses of authorization bits 0 and 1 within that cell. The conservative envelope L and complete envelope U have unconditional false-negative and false-positive mass respectively equal to the sum of W1 and W0 over mixed cells, divided by total mass. Proof: homogeneous cells are decoded exactly; in a mixed cell L=0 and U=1. If universal safety and universal completeness are both relaxed, an unrestricted deterministic Bayes decoder with equal error costs makes error mass min(W0,W1) in each cell. These are different objectives. A zero-weight feasible state still counts for universal fidelity.

For a fixed budget k the envelope tradeoff is the nondominated set of (FN(L), FP(U)) over encodings with at most k labels. This is an encoding-level pair of envelope risks, not a pair of errors of one decoder. For the 128 seeded partial-context contracts on five states, four contexts and positive integer weights, budgets 1,2,3 yield 384 cases; 109 have multiple nondominated points. Independent exhaustive labeled-assignment and restricted-growth partition implementations agree in every case.

## Transcript-limited selection theorem

Let Z1,Z2 be an ordered pair of candidate (context,state) records with a declared joint law. Fix encoding e. For complete decoder U define F_j=1 when candidate j is falsely authorized, and zero otherwise. The selector must publish exactly one candidate. Its transcript T may depend on both candidates and their receipt labels. The maximal false-authorization probability equals

    R(e,T) = sum_t max_j P(T=t, F_j=1).

Proof: any deterministic selector chooses one index per transcript cell. The displayed expression is achieved by choosing the larger error mass in each cell; randomization cannot improve it. This is the existing EvalMath cellwise maximum principle applied to certificate encoders; the novelty sought is the optimization over encoders, which also changes the transcript. Full-world visibility yields P(F1 or F2); no visibility yields max(P(F1),P(F2)). Refining T cannot reduce R for a fixed e. All probabilities below are unconditional per pair; no claim about acceptance-conditioned error or empirical rates.

## Exact optimizer reversal

Three states 0,1,2. Contexts c0={0:0,1:1}, c1={1:0,2:1}, c2={0:0,2:1}. The marginal weights on (c0,0),(c1,1),(c2,0),(c0,1),(c1,2),(c2,2) are 2,3,4,3,4,4 (total 20). Start with diagonal joint masses equal to these weights. Exchange two units from each diagonal of a=(c0,0) and b=(c2,2) into ordered off-diagonals (a,b),(b,a). Marginals remain exactly the same.

| Encoding | No visibility | Context + receipt | Full world |
|---|---:|---:|---:|
| 000 | 9/20 | 11/20 | 11/20 |
| 001 | 1/10 | 1/5 | 1/5 |
| 010 | 1/5 | 1/5 | 1/5 |
| 011 | 3/20 | 3/20 | 3/20 |

The passive optimum is 001. The selection-aware optimum is 011, even with receipt-only visibility (context indices and code labels for both ordered candidates). Relative reduction from deploying the passive optimum to the selection-aware optimum: (1/5-3/20)/(1/5)=1/4. These are all four partitions of three states using at most two labels, so the optimum is exact. Code 001 aliases states 0 and 1, producing one ambiguous context c0; 011 aliases states 1 and 2 instead.

Change b to (c0,1) while holding the same marginals. For code 001 the off-diagonal worlds now share the same observed ordered transcript, but their false-authorization index differs. No visibility and receipt-only visibility yield 1/10; full-world visibility still yields 1/5. Thus a marginal-only audit cannot distinguish the two couplings; even full-world union risk does not determine risk at a compressed interface. The proof is finite: the two off-diagonal worlds each have mass 2/20 and opposite erroneous indices. In the visible coupling distinct contexts separate the worlds; in the hidden coupling both worlds have identical context/label pairs. An independent exhaustive transcript-policy enumerator checks every code under both couplings and all three visibility conditions (24 cases).

## Evidence and limits

Reproduce with PYTHONPATH=src python -m pytest -q tests/test_evaluation_ccf.py tests/test_evaluation_ccf_weighted.py and python scripts/verify_evaluation_ccf_weighted.py. Exact rational arithmetic. Seed 20261125 is a deterministic diagnostic, not a held-out confirmatory experiment. The upstream CCF-01 fixture and new tests passed locally (6 tests). This work uses the optimistic envelope deliberately to expose the selection effect; the conservative envelope has zero false authorizations under the declared feasibility contract, at the cost of missed authorizations. No Lean kernel check for this extension and no upstream theorem or inference proof audit are claimed.

## Next registered direction

CCF-01C: finite minimax encoders under a family of feasible joint laws, with public disclosure as a decision variable; charge disclosure and encoding separately. Generalize the two-candidate cellwise maximum to N candidates, verify sharp bounds against an independent policy oracle, and construct a case where optimizing for the worst declared coupling differs from optimizing for one known coupling. Only after freezing the finite objective should Control-Harness adopt an authorization receipt policy. The upstream OpenAI and Anthropic audits remain separate evidence obligations.
