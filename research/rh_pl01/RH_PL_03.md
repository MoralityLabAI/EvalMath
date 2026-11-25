# RH-PL-03: frozen DMR arithmetic target and a free-occurrence bound

Status: expanded target frozen, exact sandbox controls passed, 2026-11-25.
The numerical result is for this exact formula and the candidate RH-PL-02
calculus, not an encoding-independent complexity result. No proof of RH in
the checker or kernel-checked ZFC equivalence proof is supplied.

## Published criterion and arithmetic reduction

Davis, Matiyasevich and Robinson (1976) give an arithmetic criterion for RH,
reproduced as Statement 4 in Yedidia and Aaronson (2016), section 5:
for all positive integers n, (H_{D(n)} - n^2/2)^2 < 36 n^3.
D(n) is the product for j<n of lcm(1,...,j). Indeed the product of eta(k)
for k<=j in the published formula equals lcm(1,...,j) by prime valuations.
We use this criterion directly instead of importing the 5,372-state
machine or trusting its compiler. The bibliography is below.

Let L(i)=lcm(1,...,i), with L(0)=1. Set D(0)=1, D(i+1)=D(i)L(i).
Let A(0)=0, B(0)=1, A(i+1)=(i+1)A(i)+B(i), B(i+1)=(i+1)B(i).
Induction gives B(i)=i!>0 and A(i)/B(i)=H_i, with H_0=0.
With a=A(D(n)), b=B(D(n)), multiply the published inequality by 4b^2:
  4 a^2 + n^4 b^2 < 144 n^3 b^2 + 4 a n^2 b.
All quantities are natural numbers. This avoids dividing D(n)! by two,
which is nonintegral at n=1 and n=2 (D=1). The paper's footnote stating
integrality for n>1 has that edge case. The denominator-clearing identity
above is valid at every positive n.

## Translation into pure first-order set language

The compiler emits
  forall w,z,o,plus,times,L,D,A,B. Definitions -> Claim.
The nine variables stand for omega, zero, one, and six relation graphs.
No constant symbols, function symbols, defined predicates, external
theorem library, or inference metadata appear in the final ASCII formula.
Every macro is expanded to equality, membership, negation, implication
and universal quantification using the RH-PL-02 grammar. A binder is
assigned the smallest index outside the active scope; slots can be
reused after exiting a scope. Definitions include:

* w is inductive and a subset of every inductive set; z is empty in w;
  o is the successor of z in w.
* Pair(p,x,y) says p is exactly the set of the singleton {x} and the
  doubleton {x,y}. Sequence graph application uses membership of such
  pairs; binary graph application uses nested pairs ((x,y),v).
* Every graph is total and single-valued on w (for binary graphs, on w^2)
  with natural-number outputs. Extraneous graph elements are immaterial.
* Addition and multiplication obey their zero and successor equations.
  L(i) is a positive common multiple of every positive j<=i and is no
  greater than any other such common multiple; D,A,B satisfy the initial
  values and recurrences above.
* Claim quantifies over positive n in w and asserts the integer inequality,
  with all computed values restricted to w. On finite ordinals, x<y is
  membership and x<=y is equality or membership.

Mathematical equivalence argument in ordinary ZFC (not yet a serialized
proof): omega exists and is unique by Infinity and Separation; zero and
one are its unique specified ordinals. Standard recursion on omega and
Replacement give the total arithmetic and sequence graphs, and induction
gives uniqueness of their restrictions. L exists since every finite list
of positive integers has a common multiple (their product); well-ordering
gives a least one, uniquely. Every tuple satisfying Definitions therefore
interprets the same arithmetic functions on omega, and at least one such
tuple exists. The universal implication holds iff its Claim holds for
those functions; it is not vacuous in ZFC. The arithmetic argument above
then identifies Claim with the published RH-equivalent criterion. For a
transfer to a separately fixed analytic formula we still require explicit
checked equivalence proofs, and a rigorous audit of the candidate axiom
grammar.

## Frozen formula and measurements

File: research/rh_pl01/rh_target.txt (one formula plus LF)
Git blob SHA-1: a55f16f293a784ca91d9d52d65cbaea1e89f80dc
Commit containing the file: 82df396e1f5dc92159ae8b29a6a6c5d00aeb1495

- Formula bytes (excluding LF): 114031; line bytes: 114032.
- Minimal-variable-shape bytes: 19536; unary variable-index bytes: 94495.
- 1240 equality atoms, 1227 membership atoms, 2539 negations,
  2466 implications, 732 universal quantifiers; 8204 total nodes.
- Maximum variable index 35, maximum AST depth 235.
- Closedness, deterministic recompilation, parse/serialize round trip
  and independent length accounting passed.
- 256 ordered-pair semantic checks in V_4 on inputs in V_3.
- Exact integer tests n=1..6, D=1,1,2,12,144,8640; harmonic numerator
  checked independently by factorial-weighted summation; denominator
  clearing checked by exact integer subtraction; six inequalities true.
  These are compiler controls, not evidence for the universal theorem.
- Fetched the committed target and re-parsed its exact bytes for the
  stronger-bound run.

## Free-occurrence-aware theorem

Write s(F) for formula bytes, s0(F) for the minimum-variable-shape bytes,
and c_t(F) for the number of free occurrences of variable t. Define
  m(F) = max(s0(F), s(F) - max_t t*c_t(F)),
where the maximum over an empty set is zero.

If A -> F is a universal-instantiation axiom, then A=forall x G and
F=G[x:=t] via free-for substitution. Substitution changes only free
occurrences of x in G into free occurrences of t in F; the number
changed is at most c_t(F). Each change can increase bytes by at most t
(the length difference from variable index zero). Binders and the
formula-tree shape are unchanged. Therefore s(G)>=m(F) and
s(A)>=m(F)+3. This holds also for a vacuous substitution and x=t.

For a closed F, m(F)=s(F): instantiation cannot reduce formula length
because capture-free substitution cannot create a bound occurrence.
The only possible predecessor body is G=F.

Combining with the RH-PL-02 last-rule split, for nonaxiom F=forall x G:
  b3(F) = min(2s(F)+2m(F)+10,
              3s(F)+27,
              s(F)+1+b3(G)).
For axioms b3(F)=s(F)+1; for other nonaxioms b3(F)=2s(F)+14.
The proof is by induction on the leading universal prefix. All MP
predecessor lines counted are distinct at the target's first occurrence.
The middle term uses the strictly longer implication that derived A->F
when A->F is not an axiom; see RH_PL_02.md.

Independent finite control: enumerate formulas with <=11 bytes and
substitute every pair of variable indices 0..3, excluding capture.
All 4474 eligible substitutions (384 closed and 4090 open targets)
satisfy the predecessor floor and are recognized by the checker.

## Numerical result

Let F_DMR be the exact frozen target. Each last-rule case gives:

| Last step | Lower bound in bytes |
|---|---:|
| MP with axiom implication | 456134 |
| MP with derived implication | 342120 |
| Generalization | 456143 |

Hence L(F_DMR) >= 342120 bytes (or infinity if no proof exists).
Original RH-PL-02 baseline: 228076; previous strengthened: 267144.
Improvement over the previous bound: 74976 bytes.

The lower bound accounts mainly for the mandatory repeated formula
structure in the final inferences. Unary variable indexing is responsible
for 94495 of the 114031 target bytes. A different alpha-renaming,
representation, inference calculus or statement encoding can change
this number dramatically. Do not confuse it with a nontrivial lower
bound on the proof overhead of analytic number theory or the length
of a Lean proof. No upper bound for this target in the calculus exists
in the repository yet.

## Reproduction

  node research/rh_pl01/rh_target.mjs
  node research/rh_pl01/rh_target.mjs --formula | cmp - research/rh_pl01/rh_target.txt
  node research/rh_pl01/closed_bound.mjs

The computations were actually executed in the JS sandbox, including
the fetched target check. Node and GitHub CI reproduction remain pending.

## Next

Audit the full ZFC schema presentation and freeze the analytic RH
encoding; implement constructive equivalence translation with charged
proof bytes. Seek proof-wide, representation-sensitive lower bounds
above the last-inference floor, through admissible symbolic cuts that
cover all eligible inference instances. Use a compact alternative
encoding as a sensitivity control. Only transfer a bound to a distinct
analytic formula after subtracting the verified implication proof cost
and final-line cost (RH-PL-01).

## References

- M. Davis, Y. Matiyasevich, J. Robinson, Hilbert's tenth problem:
  Diophantine equations: positive aspects of a negative solution (1976),
  Proc. Symp. Pure Math. 28, pp. 323-378.
  https://www.ispras.ru/en/mathbib/pub/pub1186.php
- Martin Davis, 2017, author's confirmation of the Pi-0-1 formulation:
  https://fomarchive.ugent.be/2017-January/020249.html
- A. Yedidia and S. Aaronson, A Relatively Small Turing Machine Whose
  Behavior Is Independent of Set Theory (2016), p. 11, Statement 4:
  https://arxiv.org/abs/1605.04343
  https://docs.bbchallenge.org/papers/YedidiaAndAaronson2016.pdf
