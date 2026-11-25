# RH-PL-06: nonstandard arithmetic and the axiom-cost frontier

Status: informal model-theoretic theorem with exact finite syntax and detector
controls, 2026-11-25. The target is the unchanged RH-PL-03 formula
(blob a55f16f293a784ca91d9d52d65cbaea1e89f80dc). All proof-length results
are for the declared RH-PL-02 calculus, not an encoding-independent RH bound.
No ZFC countermodel, Lean kernel proof, or checked upper bound is asserted.

## 1. Threshold

For a proof calculus with nonlogical axiom set Ax and positive integral
line cost c, put T_b={a in Ax:c(a)<=b}. Define b*(F) as the least b with
T_b |- F, or infinity if there is none (b=0 is permitted for logical
theorems). A model of T_b+not F gives b*(F)>b. This is distinct from
the cost of the entire proof, and distinct from a quantifier-rank threshold.
We establish b*(F_DMR)>=86 unary / >=38 compact. These are lower bounds,
not exact thresholds for provability. The exact minimum false-axiom cost
in our particular model is 86/38.

## 2. Nonstandard arithmetic seed

Take a countable nonstandard elementary extension M of the standard
natural numbers expanded by the actual functions addition, multiplication,
LCM L, product D, harmonic numerator A and denominator B of RH-PL-03.
Existence follows by compactness: add a constant exceeding every standard
numeral to the elementary diagram; each finite subset has a realization.
The original expanded structure satisfies induction for every first-order
formula with parameters in that expanded language, and so does M.
In particular every nonempty definable subset of M has a least element.

Keep addition, multiplication, L and D unchanged. Externally define new
functions A',B' equal to the original A,B on the standard numeral cut,
and zero on all nonstandard elements. The standard cut is closed under
successor and predecessor, and its complement is closed under successor.
Consequently A',B' satisfy every required successor recurrence and the
original initial conditions. This does NOT preserve induction for the
expanded language containing A',B'. Those modified functions are not
definable in the original arithmetic seed.

The original arithmetic satisfies D(n)>=n for n>=4: D(4)=12 and
D(n+1)=D(n)L(n), with L(n)>=2 for n>=2. Hence the same inequality
holds in M, and D(n) is nonstandard for every nonstandard n.
At any such n, A'(D(n))=B'(D(n))=0. The strict inequality in the
frozen formula fails since both integer sides are zero. This construction
uses only the true elementary arithmetic of the specified operations;
it assumes nothing about the truth or provability of RH.

## 3. Extensional membership universe

Create distinct core nodes u_n for n in M, with fixed extensions
Ext(u_n)={u_m:m<n in M}. Write C for the set of all core nodes.
Only u_0 has empty extension. For n>0 its extension contains u_0.
The standard core nodes are ordinary finite ordinal codes; nonstandard
ones have externally infinite extensions. This is a relational
structure, not a transitive collection of actual well-founded sets.

First form the closure H of the core under externally finite sets,
identifying any new node with an existing one with identical extension.
This can be done in successive finite stages: extensions are fixed
and never acquire new members. Extensionality is maintained. In
particular all singletons, doubletons, and Kuratowski ordered pairs
exist. A Kuratowski pair is nonempty and lacks u_0 as an element, since
both of its components are nonempty sets. Hence no pair is a core node.

Construct the six graph extensions G_i within H for the original
addition, multiplication, L, D and modified A',B'. Use exactly the
pair graph convention in rh_target.mjs, with nested pairs for binary
graphs. The graph extensions are disjoint from C. Pair coding is
injective by extensionality and the existence of finite sets.

Adjoin nodes for each subset of C definable in the ORIGINAL expanded
arithmetic M with finitely many core parameters, and for every
external subset of each G_i. Identify identical extensions, including
those already represented. All of these extensions are subsets of H,
so this simultaneous adjunction causes no membership ambiguity.
In particular the full C has a node Omega, and the full G_i have nodes.
Finally close under externally finite sets again. This defines a
set-sized extensional universe U (it need not be countable).

Two invariants of U:
(a) For every a in U, the trace Ext(a) intersect C is definable in M
with core parameters. Indeed core extensions are arithmetic initial
segments, finite traces are definable, graph traces are empty, and
all other infinite traces were introduced as definable subsets.
(b) Every externally infinite extension is contained either in C
or in one original graph extension G_i. All subsequent sets have
finite extensions.

The empty-set and pairing axioms hold by construction. Foundation in
its first-order set-theoretic sense holds even though the external
core order has infinite descending sequences: if a nonempty extension
has core elements, their definable trace has a least element u_n.
All members of u_n are smaller core elements, so u_n has no member
in common with the original extension. If there are no core elements,
choose a noncore member of minimal construction rank. Noncore-to-noncore
membership strictly descends in the stage ranks: finite H nodes,
then the simultaneous infinite adjunction, then later finite sets.
This gives a member with no common member with the extension.
Extensionality, empty set, pairing and foundation are thus all true.

Omega is inductive, with successor of u_n exactly u_(n+1).
Any inductive object has u_0 in its extension and its core trace is
closed under successor. By (a) and induction in M it contains all C.
Thus Omega is a least inductive object in the sense of the frozen
formula, and the fixed infinity axiom holds. The arithmetic graph
definitions hold because their restrictions to C are precisely the
specified total functions. All LCM definitions are first-order
arithmetic statements preserved by the elementary extension. The
modified A',B' obey the recurrence by Section 2. Taking a nonstandard
n gives 0<0 in the claim. Therefore U falsifies the frozen target.

## 4. Rank-one separation theorem

Claim: For every quantifier-rank <=1 formula phi(x,p) with arbitrary
parameters p from U, its truth set on C is definable in the original M.
Quantifier rank counts the maximum number of nested quantifiers, not
the number of quantifiers in separate Boolean branches.

For quantifier-free formulas:
- x=p is empty or a singleton trace.
- x in p is the definable trace from invariant (a).
- p in x is the arithmetic comparison p<x if p is a core node,
  and false otherwise.
- Atoms not involving x are constants; x=x and x in x are constant.
Boolean operations preserve arithmetic definability.

For a subformula exists y psi(x,y,p) with quantifier-free psi, use
disjunctive normal form of atomic literals (the empty conjunction is
allowed). Fix one conjunction. Eliminate tautological/contradictory
self-comparisons. If a positive equality forces y=x or y=p_i,
substitution reduces to the quantifier-free case. Otherwise:

1. A positive literal y in x restricts y to the core. On two
   core variables, all remaining atoms reduce to arithmetic comparisons,
   equality, definable parameter traces or constants. Arithmetic
   existential quantification preserves definability.
2. If a positive literal y in p_i restricts the witness, the extension
   is either finite, a definable core subset, or a subset of one G_j,
   by the invariants. A finite extension gives a finite disjunction
   of quantifier-free traces. A core subset reduces to arithmetic
   existential quantification. In a graph subset, y is a Kuratowski
   pair, so y is not core. Consequently y=x and y in x are false.
   If x in y then x is a singleton or doubleton component of a pair,
   hence the only possible core x are u_1 or u_2 (u_0 cannot be a
   component). Outside these two exceptional x, every atom involving
   both x and y has constant truth. The remaining x-only predicates
   have definable traces, and the existence of a graph witness
   satisfying the parameter-only requirements is a constant.
   At u_1,u_2 the truth value gives at most two definable exceptions.
3. In the absence of positive equality or positive literals bounding
   y by a membership extension, the remaining y-dependent conditions
   are inequalities, negative upper-membership constraints, and
   specified inclusion/exclusion of x and parameters in y. Existence
   depends only on consistency of the specified member/nonmember
   requirements (equalities between x and the fixed parameters).
   If consistent, choose a finite set y with the required members,
   excluding forbidden ones, and with at least three members and
   a noncore filler. There are infinitely many such distinct finite
   sets: vary the additional noncore fillers, of which there are
   infinitely many even in H. Such y is neither core nor a
   Kuratowski pair. Therefore it belongs to no infinite represented
   extension by invariant (b); avoid the finitely many excluded
   finite extensions and equality exceptions by choice of fillers.
   It also cannot belong to x (which is core). This proves existence
   of a witness for every x satisfying the consistency condition,
   a quantifier-free definable trace.

All conjunctions have definable traces; take their disjunction.
Universals reduce by negation. Boolean combinations of independent
rank-one subformulas preserve definability, proving the claim.

For separation on a source a: if Ext(a) is finite, every selected
subset exists. If Ext(a) is a subset of G_i, every selected subset
exists by the construction. If Ext(a) is a definable core subset,
intersect it with the just-proved definable trace of phi and the
result exists. These cases exhaust the domain. Thus *all* separation
instances of quantifier rank <=1 hold, with unrestricted formula
length and arbitrarily many fixed parameters. This is stronger
than the bounded byte census below.

## 5. Rank two can already fail

Let the parameter g be the B' graph and z=u_0. Consider

  exists p (p in g and exists t (t in p and x in t and z in t)).

In the exact grammar use free v0 for x, v3 for g, v4 for z, bind
v5 for p and v6 for t, leaving the separation output v2 fresh.
Its quantifier rank is two. On the core, the predicate selects
exactly the nonstandard cut together with u_0 and u_1. Indeed for
nonstandard n the pair (n,0) has doubleton {n,0}; standard inputs
have B'(n)=n!>0, and only n=0 gives a pair with a component
containing 0, contributing {0,1}. Singleton components containing
0 add no other elements. No other core element is selected.

The nonstandard cut cannot be definable in M: it is nonempty and
has no least element, since any nonstandard n has a nonstandard
predecessor. Finite exceptions cannot make it definable. Thus the
selected subset of Omega is absent by invariant (a). The explicit
rank-two separation instance fails. It costs 218 unary / 88 compact
bytes. Rank-one separation is a sharp quantifier-rank guarantee
for this model, not a claim that rank-two separation is necessary
in every proof of the target (other set axioms could eliminate it).

## 6. Exact byte-cost frontier for this model

Power set is false. Its output for Omega would have to contain Omega
itself and every singleton of a core element, so have an externally
infinite extension containing Omega. Omega is neither core nor a
Kuratowski pair (its extension is infinite); invariant (b) rules
out such an output. The fixed power-set axiom costs 86 unary bytes
or 38 compact bytes.

All fixed nonlogical axioms cheaper than those costs hold (the
only relevant ones are among empty, extensionality, foundation,
pairing; infinity also holds). Every replacement instance costs
at least 125/70 bytes, as in RH-PL-05. For separation:

- Unary line cost is 48+2*s(phi), where s excludes LF. A line
  cheaper than 86 requires s(phi)<=18. Every such admissible
  predicate has definable trace in M. To see this, parameter-only
  subformulas are constant on x=v0; rank-one formulas are covered
  above; single-atom formulas with x free have at most one active
  bound variable and reduce to rank one by removing vacuous
  quantifiers. Negation and implication preserve definable traces.
  For an outer nonvacuous universal binder with free x and rank>=2
  and at least two atoms, its index is at least 1, so it adds at
  least one extra byte to the binder and at least one to a bound
  occurrence. Two atoms, a binary connective and two binders cost
  at least 10+1+6=17 before these extras, hence >=19, impossible.
  If the outer binder is vacuous remove it and induct on size.
  This exhausts the short grammar, without assuming that every
  higher-rank formula is rank-one equivalent.
- Compact line cost is 30+2*s(phi). Cheaper than 38 requires
  s(phi)<=3, hence an atom. Every such separation is valid by
  the rank-one theorem.

Thus the cheapest false axiom in U is exactly power set's cost,
86/38. In particular U models T_85+not F in unary and T_37+not F
in compact. No claim that adding power set alone proves F, nor
that these are the exact b*(F) values.

## 7. Proof-wide numerical bounds

Apply the residual-capacity combination in RH_PL_05.md with
delta=86/38; the proof of non-overlap depends only on the grammar,
not on which particular countermodel supplied delta. We obtain:

| Metric | Unary | Compact |
|---|---:|---:|
| RH-PL-05 bound |570239|69401|
| b*(F) lower bound |86|38|
| Spine k=1 |570261|69403|
| k=2 |570270|69409|
| k=3 |570288|69421|
| k>=4 |570306|69433|
| Generalization |684183|83220|
| RH-PL-06 total lower bound |570261|69403|

Improvement: 22 unary and 2 compact bytes. The progress in surviving
entire separation fragments is stronger than the absolute-byte
increase. We still lack a substantial lower bound on deductive
overhead beyond a few target-line equivalents. The weak fragments
do not contain full standard ZFC; the model is not a disproof of RH.

## 8. Executed controls

The dependency-free JS sandbox ran fragment.mjs logic against the
fetched frozen formula. The grammar enumeration through 18 unary
bytes contains 38232 formulas, of which 26756 are admissible
separation predicates (no free v2). Each is recognized by the
actual checker, classified by the short-grammar proof, and checked
for the exact expanded separation line cost in both encodings.
7064 have quantifier rank >1; maximum rank 4. A rank-two detector
was tested on four finite surrogate graphs, for 56 membership
controls. The finite surrogate marks a cut in a finite panel and
tests only the ordered-pair detector, not nonstandard induction.
The actual infinite-model theorem is the proof in Sections 2-5,
not an inference from a finite simulation. All controls passed.

Reproduce with:
  node research/rh_pl01/fragment.mjs

Node execution and CI have not been independently run.
No formalized metatheory theorem is claimed.

## 9. Next gate and limitations

Power set and union are now important: to raise b*(F) beyond 86
unary / 38 compact, construct a countermodel also satisfying the
fixed power-set axiom, or another model supporting a packing with
disjoint axiom costs. Merely adjoining the missing power-set
output breaks invariant (b) and requires a new rank-one proof.
In particular an actual nonstandard model of arithmetic with
the modified harmonic graph cannot support arbitrary separation
plus least-inductive Omega: the rank-two graph detector exposes
a nonstandard cut. A stronger model must address that obstruction
rather than repeating small variations on the successor trick.

The prior calculus soundness/completeness audit, equivalence of the
compiled target to an explicitly frozen analytic RH formula inside
the calculus, and checked upper bound remain outstanding. No
paid compute was used, and the PR remains a draft for review.
