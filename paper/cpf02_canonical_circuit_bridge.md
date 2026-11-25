# CPF-02: pinned circuit conventions and canonical claim obligations

Status: the gate-budget sandwich, the polynomial-bound normalization, VP equality across the three conventions, OpenAI-VNP witness transport, VP ⊆ VNP and VNP equality between the canonical and Anthropic conventions are kernel-checked (Lean 4.34.1, Mathlib `d13f23b`, axioms `propext`, `Classical.choice`, `Quot.sound` only). The Laurent-versus-geometric border question, the permanent/Hamiltonian family match and both upstream proofs remain open. No error rates are inferred from these papers.

## Circuit-level result

Fix a field and finite variable type. In the OpenAI comparator, an exact s-gate table uses free variables and field scalars; each gate adds, subtracts, or multiplies two available values. Anthropic's charged table has addition/multiplication gates and explicit variable/constant gates. The output can be any earlier gate. Our canonical natural-index table has free leaves and subtraction. Its family predicates bound arity, degree and circuit size eventually polynomially; the witness size is a polynomially bounded natural number and the VNP sum ranges over Boolean assignments to that many variables. The approximation predicate uses Laurent coefficients, without claiming equivalence to Zariski closure.

For charged-to-free simulation preserve the indices of the entire charged table; a charged leaf is computed by adding zero to the free leaf. Earlier operation references remain legal. Hence every charged witness of size s gives a free witness of size s. For free-to-charged, insert one constant -1; translate the two operands of every operation, inserting at most two charged leaf gates. Addition and multiplication need one further gate; subtraction uses multiplication by -1 and addition. Store the correspondence between original and translated gate indices. For a free output leaf insert one additional leaf; a gate output uses its corresponding translated index. The result has at most 4s+2 gates and exactly the same formal polynomial. Pad with constants to obtain exactly 4s+2 if needed. This proof is valid in all characteristics, including two; it never uses evaluations at field points to identify polynomials. For minimum gate counts C_O and C_A, C_O <= C_A <= 4C_O+2. Polynomial and superpolynomial exact size therefore agree under these gate models on a common sequence of polynomials.

## Verification scopes

The Lean modules import a compatibility copy of the pinned Anthropic statement (only the multivariate coefficient accessor is updated from `coeff d q` to `q.coeff d` for EvalMath's Mathlib; the archive remains byte-identical, enforced by `fixtures/external/** -text` and git-blob pins) and the definitions-only extraction of the OpenAI comparator, so every bridge is stated against the actual upstream definition bodies. The comparator's admitted challenge endpoint stays in the archive outside the build; no admitted comparator theorem enters the trusted environment.

Kernel-checked in `CPF02/Canonical.lean` and `CPF02/Bridges.lean`:

| Result | Lean theorem | Scope |
|---|---|---|
| OpenAI exact `Computes s p` iff canonical `Computes p s` | `openai_exact_iff` | every field, every variable type |
| charged size s implies free size s | `anthropic_exact_to_canonical` | every field |
| free size s implies charged size 4s+2 (reverse compiler) | `canonical_to_anthropic`, `charged_free_sandwich` | every field, any characteristic; slot layout `C(-1)` at 0, gate i in slots 4i+1..4i+4, leaf output at 4s+1 |
| lower bounds transfer both ways | `lower_transfer`, `lower_transfer_reverse` | B < s for charged gives B < 4s+2 for free |
| Laurent approximation, charged implies canonical | `anthropic_approx_to_canonical` | Laurent notion only |
| eventual `A*n^d` iff all-index `n^a + a` | `polyBounded_iff_allIndex` | finite prefix absorbed by `Finset.sup`; n = 0, 1 handled |
| OpenAI `IsVP` iff canonical `VP` iff Anthropic `VP` | `openai_vp_iff`, `vp_iff_anthropic` | same polynomial family, every field |
| OpenAI `IsVNP` (arbitrary finite witness types) iff canonical `VNP` (`Fin (r n)`) | `openai_vnp_iff_canonical` | transport along `Fintype.equivFin`; Boolean sum reindexed; renaming preserves size and does not raise degree |
| VP subset of VNP | `vp_subset_vnp` | zero witness bits |
| canonical VNP implies Anthropic VNP | `canonical_vnp_to_anthropic` | `aeval` and `eval₂Hom C` identified |
| substituting polynomials of total degree ≤ 1 does not raise total degree | `totalDegree_eval₂Hom_le` | any commutative semiring |
| Anthropic VNP implies canonical VNP, hence VNP equality | `anthropic_vnp_to_canonical`, `vnp_iff_anthropic` | arity and witness length from the verifier's card bound; degree of the summed family from `totalDegree_eval₂Hom_le` |

The finite census remains an independent executable check of the compiler on small tables: zero, one and two original arithmetic gates, all topologically valid operand choices over two variables and constants -1, 0 plus earlier gate references, every legal output, and fields of orders 2, 3, 5, comparing sparse formal coefficient maps rather than truth tables. Its two implementations share polynomial arithmetic, so it tests compiler semantics, not an independent arithmetic oracle. The Lean slot layout reserves four slots per gate where the census compiler inserts leaves on demand, so the census sizes are smaller on small tables; both are within 4s+2.

## Remaining obligations and evidence boundaries

* **Class endpoints.** OpenAI's comparator endpoint is a restricted `Fin n × Bool` statement; Anthropic's is the all-families proper subset `VP F ⊂ VNP F`. The bridges make the classes comparable but prove neither endpoint.
* **Laurent versus geometric border.** `Approximates` in the canonical and Anthropic statements is the algebraic Laurent-series notion (`q = f + ε·g`, coefficients of g in F[[ε]], gates over F((ε))). Over algebraically closed fields this agrees with Zariski-closure border complexity; over other fields it need not. Nothing here infers geometric closure from a Laurent statement, and the exact-to-constant-Laurent embedding (VP inside VPBar) is not kernel-checked. Allowing arbitrary Laurent-series constants instead of Laurent polynomials does not change the class (truncating constants beyond a valuation bound preserves the output coefficients of order at most 0), but that argument is a paper derivation here.
* **Families and rates.** Match the Hamiltonian/permanent definitions, orientation, index and characteristic, and compare quantitative bounds only after matching the underlying families, scales and quantifiers. OpenAI's comparator endpoint is exact separation; its documentation gives additional exact lower-bound scope but is not a theorem signature for a quantitative border bound. Anthropic's statement file contains quantitative exact and approximate endpoints. Neither upstream solution is imported or claimed verified in this branch.

For CPF-03 use controlled mutants: gate cost mismatch, omitted degree bound, nonuniform field threshold, characteristic-two permanent claim, exact-for-border substitution, and finite evaluation mistaken for polynomial equality. Assign labels by a proved implication or a countermodel, with unresolved cases segregated; blind the model to label and proof provenance. This is a prospective test design, not measured model accuracy.
