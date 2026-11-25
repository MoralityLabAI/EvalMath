# RH-PL-02: candidate first-order ZFC verifier and full-calculus syntax bounds

Status: exact finite controls passed in JS runtime, 2026-11-25. No numerical
bound for RH itself, no checked ZFC proof of RH, and no Lean kernel claim.

## Contract

`kernel.mjs` implements a candidate concrete, assumption-free Hilbert calculus.
The object language has variable terms only and atomic equality/membership.
Formula tags are e, m, n, i, a for equality, membership, negation, implication,
and universal quantification. A variable index j is v followed by j ones and
a terminal zero. Existential quantification, conjunction, disjunction, and
biconditional are macros expanded before charging bytes. Every line is an
ASCII formula followed by LF; inference references are implicit. Final
target must be closed; intermediate lines can be open universal theorems.
No imports, uncharged definitions, theorem libraries, or external oracles.

Logical axioms: K, S, classical contraposition, free-for universal
instantiation, quantifier distribution with its free-variable restriction,
equality reflexivity, and single-position atomic equality substitution.
Rules: modus ponens and unrestricted universal generalization of a previously
derived line (there are no hypotheses). The eight fixed set axioms are
extensionality, empty set, pairing, union, power set, infinity, foundation,
and disjoint-family choice. Separation and functional replacement are
recognized by exact AST patterns with designated fresh-variable restrictions;
the remaining free parameters can be generalized. Instances use fixed binder
slots and can use alpha-renamed predicates. This is a candidate presentation
of ZFC; independent soundness/completeness and schema-equivalence review is
still required. In particular the tests are not a formal metatheory proof.
Implementation resource limits (JS recursion, memory, integer indexing)
are distinct from the mathematical unbounded calculus.

## Syntax lower bound

Let s(F) be the encoded formula bytes excluding LF, c(F)=s(F)+1. Every formula
has at least 5 bytes. Let L(F) be the least proof cost including open
intermediate theorems, and infinity if unreachable. Take a proof truncated
at its first occurrence of F. If F is an axiom, L(F)=c(F). Otherwise its
last step is either MP using A and (A -> F), or generalization of G where
F=forall x G. In the MP case the predecessor lines and F are distinct:
A=F would violate first occurrence, and (A -> F) is strictly longer than
both. Their total length is at least 2s(F)+14.

Thus for nonaxioms,
  b(F) = min(2s(F)+14, c(F)+b(G) if F=forall x G).
For axioms b(F)=c(F). Induction on the leading universal prefix proves
b(F)<=L(F) across the entire specified calculus, including alternative
proofs and ZFC axioms.

## Stronger universal-target bound

Let s0(F) be the byte length of the same syntax tree when every variable
occurrence (including binder indices) has the minimum two-byte encoding.
For a nonaxiom F beginning with forall, consider the last MP. In this
presentation the only axiom schema that can have the shape A -> F is
universal instantiation: all other implication-shaped axioms have
an implication or existential macro (negation) as consequent.
Consequently:

- If A -> F is an axiom, A=forall x G and capture-free substitution of a
  variable for x in G yields F. Substitution preserves the formula-tree
  shape, so s(A)>=s0(F)+3. The three mandatory lines cost
  at least 2s(F)+2s0(F)+10.
- Otherwise A -> F must itself have been derived by MP, since its root
  is implication. Its preceding implication C -> (A -> F) is strictly
  longer than each of A, F, and A -> F; it adds at least
  s(A)+s(F)+8 bytes (including LF). The total is at least
  3s(F)+3s(A)+12 >= 3s(F)+27.

Together with generalization, the improved recurrence for nonaxiom
universal F=forall x G is
  b2(F) = min(2s(F)+2s0(F)+10, 3s(F)+27, c(F)+b2(G)).
Use b2(F)=2s(F)+14 for other nonaxioms, c(F) for axioms.
This proof is specific to the fixed axiom grammar; adding a macro rule or
extra axiom schema requires re-auditing it. It is an unconditional syntax
bound for that calculus and is not an intrinsic, encoding-invariant RH bound.

## Exact controls

For P = v0 in v0, R = (v0=v0), and F = forall v0 (P -> P),
the following is a 51-byte proof:
  R
  R -> (P -> P)
  P -> P
  F
The first two lines are reflexivity and atomic equality substitution
respectively; the remaining lines are MP and generalization.

F has 14 bytes. Baseline b(F)=42; improved b2(F)=51. The 51-byte witness
makes this an exact minimum. An independent bounded last-MP enumeration
at total budget 50 checks all 82 possible antecedents and all legal
additional-line candidates (52), testing 464 orderings, with no proof found.
Any MP-ending proof in this budget has at most one additional line beyond
its three required formulas. The other last-step case, generalization,
requires a proof of P -> P of at least 36 bytes (attained), plus 15 bytes
for F. Hence the finite check also closes the gap.

Nested universal reflexivity controls (v0 innermost, distinct successive
outer binder indices) also attain the improved bound by repeated
generalization:

| leading binders | target bytes | baseline | strengthened | explicit upper |
|---:|---:|---:|---:|---:|
| 1 | 8 | 15 | 15 | 15 |
| 2 | 12 | 28 | 28 | 28 |
| 3 | 17 | 46 | 46 | 46 |
| 4 | 23 | 60 | 70 | 70 |
| 5 | 30 | 74 | 101 | 101 |

## Executed checks

- 880 distinct generated logical instances, 112,640 evaluations over all
  16 two-element membership relations and 8 assignments to 3 variables.
- 8 and 32 countermodel-assignment witnesses for variable-capture and
  illegal quantifier-distribution examples respectively.
- 6 negative axiom-schema cases, 7 malformed formula cases, 5 invalid
  proof cases; 8 fixed set axiom recognition/closedness/one-line checks.
- The kernel fixture also checked proof lengths 15, 28, 51 with original
  lower bounds 15, 28, 42 respectively.
- Stronger exact 51-byte target certificate and the bounded MP enumeration.
- Sources were evaluated in the JS sandbox; the bounds run used the
  fetched kernel at commit 85dc9f07d1b0095096457d42bfd26f5aaf055630.
  No GitHub CI or Node execution claim. Reproduce independently with:
  `node research/rh_pl01/kernel.mjs` and `node research/rh_pl01/bounds.mjs`.

## Next gate (RH-PL-03)

Produce and freeze actual closed arithmetic RH formula bytes in this
calculus. A formal proof of equivalence to the analytic RH must accompany
the target. Avoid claiming a lower bound on RH based on a machine name or
an unexpanded macro. Apply both recurrences to the frozen target as a
baseline, then look for stronger obstruction families that are complete
over the permitted full inference universe. Audit proof-system equivalence,
including alpha renaming and the replacement schema, before calling a
numeric result a standard ZFC proof-length result. No assumption about
the correctness or ZFC conservativity of a recent claimed RH proof is
needed for these lower-bound lemmas.
