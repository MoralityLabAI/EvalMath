# CPF-01: correlated proof fidelity and certified-rejection audits

Status: research draft, algebraic identities and synthetic finite evidence. The Lean lemmas are candidates pending kernel checks. No empirical error rates, upstream rebuilds, or referee verdicts are claimed.

## 1. Conditional null law

Fix a sampling protocol for intended mathematical claims and condition on the intended claim being false (a positive-probability event). A and B mean that respective verification pipelines authorize the intended claim. A kernel accepting a correctly encoded proof is distinct from a pipeline authorizing a natural-language claim. Error rates here concern the latter, including semantic mismatch; no kernel failure is assumed.

Write a=P(A|null), b=P(B|null), r=P(A and B|null). The four atoms have masses (r,a-r,b-r,1-a-b+r). Nonnegativity is equivalent to max(0,a+b-1) <= r <= min(a,b). Conversely these four masses sum to one and give the prescribed marginals, so every feasible r is attained. With a=b=1/20, r can range from 0 to 1/20; independence gives 1/400. These are conditional false-acceptance rates, not posterior error probabilities. Posterior error also requires a prior and the joint true-claim acceptance rate.

If an additional audit passes with probability c conditional on null and both accept, the remaining false-authorization rate is rc. When r=0 the residual is zero and c need not be defined. A marginal audit calibration alone cannot justify this product. Conditional calibration on the selected fibre is required.

## 2. Adaptive audit oracle

In a declared finite null model the initially dual-accepted worlds carry nonnegative rational masses summing to r. An audit is a deterministic map from world to outcome. Only a certified reject blocks authorization; other outcomes may supply diagnostic information. Assume rejection is sound on true claims; the model does not test true-claim coverage or audit cost heterogeneity. Each query costs one, cannot be repeated on a path, and a policy may stop early. Terminal loss is the surviving false mass. There is no free discretionary rejection.

For surviving world set S, unused queries Q, and remaining budget k, V(S,Q,0)=mass(S). For k>0, V is the minimum of mass(S) and, for each q in Q, the sum of V(S_o,Q\\{q},k-1) over non-reject outcomes o. By induction on k, the first action is either stop or some q; each observed outcome has an independent optimal continuation. This yields the exact minimum. A fixed schedule of k distinct queries has residual equal to the mass never rejected by those queries; extra queries cannot increase residual. Therefore adaptive optimum is no worse than fixed optimum. Independent policy enumeration collects possible survivor sets instead of evaluating this recurrence.

Four dual-accepted null worlds have masses 1/100, 1/100, 1/100, 1/50. One diagnostic identifies one of three detectable classes or the invisible class; three separate tests each reject precisely one detectable class. At budget two a fixed schedule leaves at least 3/100; the diagnostic followed by the indicated targeted test leaves 1/50. The invisible class is a lower bound for every policy. The reduction is exactly 1/100 of the null distribution, a third of fixed residual. It is a synthetic witness only. The receipt enumerates all four-atom distributions on denominator 8 and all 2-world, 3-query outcome matrices over three outcomes at budgets 0,1,2.

## 3. VP-VNP crosswalk (published source inventory, not a completed fidelity proof)

- OpenAI, *VP and VNP are different*, 2026-11-23. [Scope note](https://github.com/openai/math/blob/main/lean/docs/379.md). Exact circuit separation and exact permanent/Hamiltonian lower bounds are described as formalized; the stronger quantitative border claim in the paper is outside the stated Lean scope. Gate model: binary addition, subtraction, multiplication.
- Anthropic, *VP != VNP over every field*, 2026-11-23. [Paper](https://hexagonmath.org/2611.00954v1), [README](https://github.com/anthropics/formal-math/blob/main/vp-vnp/README.md), [Statement.lean](https://github.com/anthropics/formal-math/blob/main/vp-vnp/Statement.lean). The release describes exact and approximate claims, with VPBar and SeparationClosure in the statement file. The README explicitly leaves natural-language statement fidelity to review. The manuscript claims a bound of m^(c(log m)^(1/3)); OpenAI claims exp(Omega((log n)^(5/4))) for border circuits. Comparing rates requires a proved size-parameter crosswalk and matching definitions.

Before assigning any joint confidence, freeze both upstream commits and manuscript hashes; map exact circuits, gate accounting, field quantifiers, permanent in characteristic two, Hamiltonian witnesses, closure definitions and the explicit size exponent. Classify each implication as text match, elaborated type match, proved bridge, unresolved, or outside scope. Then map dependencies for shared compression/diagonalization mechanisms. A shared defect is a hypothesis, not a finding. Independent kernels can reduce implementation risk while leaving the common semantic bridge unaudited. Do not treat two selected releases as a random calibration sample.

CPF-02 gate: separately authored canonical definitions and machine-checked bridges, with adversarial mutants and prospective, blinded calibration over independently labeled claims. Record dependence at the intended-claim level and distinguish shared source/definition, proof mechanism, and checker failure. No upstream artifacts are pinned or rebuilt by CPF-01; the links above identify the consulted public interfaces and can drift.

## 4. Reproduction

Run `PYTHONPATH=src pytest -q tests/test_evaluation_cpf.py` and `PYTHONPATH=src python scripts/verify_evaluation_cpf.py --output output/evaluation_cpf/cpf_01.json`. Receipt hashes cover the module, tests, verifier, note and candidate Lean file. Candidate lemmas cover the four-atom interval and product contraction only; the adaptive theorem has the paper induction and finite oracle, not a Lean proof. From `lean/` run `lake env lean FeedbackChannel/CorrelatedProofFidelity.lean`.
