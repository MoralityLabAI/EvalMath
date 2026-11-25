# RH-PL-07: power-set closure and two-model semantic packing

Status: informal model-theoretic lemmas plus exhaustive bounded syntax
classification and finite combinatorial controls, 2026-11-25.
Unchanged RH-PL-03 target, blob a55f16f293a784ca91d9d52d65cbaea1e89f80dc.
Results concern the specified candidate Hilbert calculus and its two
encodings. No standard-ZFC countermodel, proof of RH, checked RH
equivalence, kernel formalization or CI result is claimed.

## 1. Purpose

RH-PL-06 model C satisfies every rank-one separation instance but
fails power set, limiting the single-model axiom-cost floor to
86 unary / 38 compact bytes. This pass constructs model P satisfying
power set and quantifier-free separation. The false-axiom sets differ.
We combine their semantic cuts using the residual capacities from
RH-PL-05. The model P construction has a precise limitation:
union fails, and some inexpensive quantified separation instances fail.

## 2. Arithmetic seed and the power-closed universe P

Reuse the nonstandard elementary extension M of the standard expanded
arithmetic structure from RH-PL-06. The core C0 consists of nodes u_n
for n in M, with Ext(u_n)={u_m:m<n}. The modified A',B' sequences
agree with the standard harmonic sequences on standard indices and
vanish on nonstandard indices. Addition, multiplication, L and D
are unchanged. All recurrence and LCM clauses of the frozen target
hold, and its inequality fails at a nonstandard index.

Call a subset S of core-and-set nodes admissible if its core trace
{n:u_n in S} is definable with finitely many parameters in the ORIGINAL
expanded arithmetic M. In particular finite traces, arithmetic
initial segments and the whole core are admissible. Do not use the
modified sequence graphs as additional predicates in M.

Define U_0=C0. At stage j+1 adjoin a node for every admissible subset
S of U_j, identifying it with any existing node with identical
extension. All extensions of old nodes remain fixed. The extension
of every newly adjoined node is precisely its specified S. The
identification is unambiguous by extensionality at the preceding
stage. Let U be the union of these stages over standard finite j.
This is a set-sized relational membership structure. All finite
subsets of U are represented (a finite collection fits in some
stage). Every represented node has an arithmetic-definable core
trace, by construction. Every noncore node has a first positive
stage, and noncore members of a noncore node have strictly smaller
first stages. Core nodes have only core members.

Extensionality, empty set and pairing hold. Foundation holds in
the internal first-order sense: for a nonempty extension with
core members, its definable core trace has a least arithmetic
element u_n, none of whose members belong to the extension.
For an extension without core members, select a member of minimum
first stage. Its members cannot be in the original extension.
The nonstandard core may be externally ill-founded; no external
well-foundedness assertion is made.

The full core is represented by Omega. Its zero and successor
satisfy inductiveness. The successor of each u_n is u_(n+1) by
extensionality. Every inductive object's core trace contains zero
and is successor-closed, so induction in M gives the full core.
Thus Omega is least inductive, and infinity holds.

Finite singletons and doubletons exist, with unique Kuratowski
pair codes. Each pair is nonempty and has no empty object as
member, so is noncore. All graph entries for the six unary/binary
graphs of RH-PL-03 occur at some common finite stage (nested pairs
have bounded construction depth). The entire graph extensions,
including the externally modified harmonic graphs, have empty
core trace, hence are admissible and represented at a later
finite stage. They implement the specified functions exactly.
The target is false at the same nonstandard index as in
RH-PL-06. In particular we do not require RH to be false in
standard arithmetic.

### Power set theorem

For any represented a, let S=Ext(a) subset U_j for some finite j.
Every represented b satisfying Ext(b) subset S has admissible
extension, hence is already represented in U_(j+1); extensionality
ensures it cannot be a new later node. Conversely every admissible
subset of S is represented by then. Let P_a be the collection of
all these subset nodes. Its core trace is

  {n in M: forall m<n, u_m in S}.

This is definable in M because the trace of S is definable.
So P_a is admissible and is represented in U_(j+2).
Its extension contains exactly the represented subsets of a,
which is the fixed power-set axiom. This proves power set for
every object, rather than just for Omega.

### Quantifier-free separation theorem

For core x=u_n and arbitrary fixed parameters p:
x=p is an empty/singleton trace; x in p is a definable core trace;
p in x is the comparison p<x if p is core and false otherwise.
Atoms not depending on x are constant; x in x is false.
Thus every quantifier-free predicate has definable core trace.
Given any source S, its selected subset remains inside a finite
stage, and its core trace is the intersection of two definable
traces. It is admissible and represented. This proves all
quantifier-free separation with arbitrary parameters.

## 3. Two exact failures in P

Union fails. The externally defined nonstandard cut M\N is
nonempty and has no least element; it cannot be definable in M.
Let a have extension consisting of singletons {u_n} for nonstandard
n. These singletons are noncore (a nonempty core extension always
contains zero); the collection occurs at a bounded stage and
has empty core trace, so a is represented. Its union would have
core trace exactly the nonstandard cut. Such a node is impossible.
The fixed union axiom is false at cost 94 unary / 46 compact.

A cheaper unary separation failure uses a parameter p whose
members y_n, for each nonstandard n, have extensions

  Ext(y_n) = {u_m:m<n} union {h},

where h is any fixed noncore node. Each extension is admissible,
all y_n are noncore at a common finite stage, and the collection
p is admissible. For x in the core the predicate

  phi(x,p) := forall y (y in p -> x in y)

selects exactly the standard cut: every standard index is below
every nonstandard index, while a nonstandard index n is not
below itself. The standard cut is not definable (its complement
is the nonstandard cut). Thus separation on Omega for phi fails.

Use v0=x, v1=y (bound inside phi), v3=p. No free v2 appears.
The bound occurrence of v1 does not refer to separation's source
parameter v1. The exact predicate is
  av10imv10v1110mv0v10
of length 20 unary. The separation instance costs 88 unary /
48 compact bytes. This is a rank-one formula, and contrasts with
model C's rank-one guarantee.

## 4. Complete short-schema coverage for P and C

The checker recognizes separation using a predicate phi with
no free v2. Its expanded line cost is 48+2*s(phi) unary, or
30+2*s(phi) compact (s excludes LF). Replacement's minimum
cost remains 125/70. Fixed costs are the pinned RH-PL-02 grammar.

### P: all unary predicates through 19 bytes

The pClass classifier in packing.mjs implements sufficient trace
rules. Each successful classification proves definable core trace
for arbitrary fixed values of all free parameters other than x.

- x not free: constant trace. Atoms: Section 2. Negation and
  implication: Boolean closure. A vacuous binder may be removed.
- For a nonvacuous universal binder y, if its body is a Boolean
  combination of atoms involving only x,y and y-independent
  subformulas already classified, then the trace is definable.
  For core y, all the x,y atoms reduce to arithmetic comparisons.
  For noncore y, equality with x and membership in x are false,
  y in y is false, and x in y has both possible truth values
  for every x (choose finite sets containing a noncore marker,
  with and without x). Thus quantifying y yields a finite Boolean
  combination of arithmetic quantified predicates and already
  definable x-traces. No information about arbitrary parameter
  extensions is needed in the noncore branch.
- If instead the body factors into a Boolean combination of
  y-independent classified pieces and x-independent pieces,
  enumerate the finite truth assignments to the former. For
  each assignment, quantification of the residual x-independent
  formula is a constant. This again yields a Boolean combination
  of definable x-traces.

Removing vacuous binders inside these tests preserves truth and
free variables. These rules are sound by structural induction.
Exhaustive grammar enumeration through 19 unary bytes, rejecting
free v2, classifies every one of 55,104 admissible predicates.
The enumeration by exact byte size is complete because each AST
constructor has positive tag cost, each variable has unary cost
j+2, and all smaller subformula sizes are generated first.
This is a finite exhaustive syntax certificate conditional on
the stated trace rules, not enumeration of models.

At size 20, 64 admissible predicates fall outside these
sufficient classifications; not all are claimed false. The
explicit false witness in Section 3 is among them. Therefore
the cheapest false separation costs exactly 88 unary bytes.
Every cheaper fixed nonlogical axiom is true in P (including
power set), and replacement is more expensive. The cheapest
false nonlogical axiom in P is exactly 88 unary bytes.

### C: all unary predicates through 22 bytes

The RH-PL-06 model C supports every rank-one separation instance.
We strengthen its bounded syntax coverage without changing C.

In any extensional nonempty structure with empty set, pairing
and foundation, a quantified single-atom formula with any
number of negations and binders reduces to a quantifier-free
formula, allowing the empty object as a fresh parameter.
For the innermost active binder, equality with another variable
has a witness and is not universally true (the domain has at
least two elements). Membership of a fixed object in a variable
has a witness by pairing and is not universally true (empty
set). Membership of a variable in a fixed object has a witness
iff that object is not empty and cannot be universally true
because self-membership fails. Self-atoms are constant.
Negations and universals/exists preserve these reductions.
Vacuous binders can be dropped. Repeatedly reduce single-atom
subtrees with a fresh empty parameter, and remove vacuous
binders. The computed reduced rank is an upper bound on the
rank of an equivalent formula.

Enumerate all 753,086 unary formulas through 22 bytes. After
the free-v2 restriction, 498,654 remain. Of these, 179,406 are
constant on the source-element variable and 319,248 reduce to
rank at most one. No predicate is unclassified. The cClass
checker also allows Boolean closure and removal of vacuous
outer binders, though these extra cases were not required
in the census. Every such separation holds in C. Consequently
all unary separation lines costing <94 hold in C.

### Compact shared threshold

A separation line costing <46 compact requires s(phi)<=7.
If phi contains two or more atoms, their minimum cost is
6 plus at least one binary connective, so there is no room
for a quantifier. If it contains one atom, the single-atom
reduction above applies. Thus all these separation instances
hold in P by quantifier-free separation. This argument covers
all variable indices, including extended base-36 encodings;
no finite variable-index cap is used. All fixed cheaper axioms
hold in P, and replacement is longer. The cheapest false
nonlogical axiom in P is exactly union's 46 compact bytes.

## 5. Union collapse: why preserving both axioms is difficult

For the exact modified denominator graph G_B from RH-PL-06,
the rank-two detector is
  exists p in G_B, exists t in p: x in t and 0 in t.
On Omega it selects the nonstandard cut plus 0 and 1.

If even the union of G_B exists as an object U, this detector
is equivalent to the rank-one predicate
  exists t: t in U and x in t and 0 in t.
Boolean-combine it with the two finite exceptions to select
the standard cut instead. Rank-one separation on Omega
would produce a proper inductive subobject containing exactly
the standard numerals. This contradicts Omega's least-inductive
property. Hence every extensional realization of this exact
nonstandard arithmetic/graph witness with least-inductive
Omega and all rank-one separation must fail the union instance
for G_B. In particular model C fails union.

This is a no-go result for the specific modified-denominator
construction, not a theorem that no model of the target's
negation can satisfy union and rank-one separation. To extend
this approach one must change the arithmetic counterexample
or the graph exposure mechanism; just adding the missing
unions to model C cannot work.

## 6. Semantic packing and bounds

Both models validate all declared logical rules. Every proof
of F_DMR uses a nonlogical axiom false in C and a nonlogical
axiom false in P. Exact minima of false costs:

| Mask/floor | Unary | Compact |
|---|---:|---:|
| False in C (possibly also P) |86|38|
| False in P (possibly also C) |88|46|
| False in both |94|46|

The common floor is exact: union is false in both. Below 94
unary or 46 compact, power set is false only in C; all other
cheaper fixed axioms true in P or both; the separation
classification above guarantees no shared false instance.
Replacement is too expensive to affect these thresholds.

Assign semantic dual weights y_C=86,y_P=8 unary,
or y_C=38,y_P=8 compact. Each weight is below its individual
floor and the sum equals the shared floor. Every axiom's
load is <= its cost, including all instances of both schemas.
Thus total cost of axiom lines false in at least one model
is >=94 unary / 46 compact. Since union is a shared false
axiom at exactly this cost, no larger dual sum using only
these two models and this cost metric is possible. Integer
dual enumeration independently attains this optimum.

This proves b*(F)>=88 unary / >=46 compact, using P.
For unary, any proof whose nonlogical axioms all cost <94
must include DISTINCT lines falsified in C and P, costing
at least 86+88=174 bytes together. If a single line eliminates
both, it costs >=94. Do not claim b*(F)>=94 unary: the
packed lower bound concerns SUM cost, not maximum cost.

For the spine charge of RH-PL-04, reuse the residual argument
of RH-PL-05. In k=1 all charged lines are distinct from
nonlogical axiom lines. In k>=2 only A1 may be among the
false axiom lines, with d+1 already charged to it; the
aggregate semantic weight can be added minus d+1, even
if multiple false axiom lines are needed. Generalization
branch retains the previous bound.

| Last inference case | Unary | Compact |
|---|---:|---:|
| k=1 |570269|69411|
| k=2 |570278|69417|
| k=3 |570296|69429|
| k>=4 |570314|69441|
| Generalization |684183|83220|
| Combined lower bound |570269|69411|

RH-PL-06: 570261 / 69403. Gain: eight bytes in each encoding.
The added value is a genuine two-countermodel certificate
that improves over the strongest individual model in unary.
The overall normalized proof-length floor is still near
five target-line equivalents.

## 7. Executed controls

Against the fetched frozen target and pinned prior code:
- Complete unary grammar census 753,086 formulas, 498,654
  admissible separation predicates through 22 bytes.
- P classifier: all 55,104 predicates through 19 bytes
  classified; 64 unclassified at size 20.
- C classifier: all 498,654 predicates through 22 classified.
- Exact witness shape/cost and fixed union/power recognition.
- 4,503 unary and 1,092 compact feasible integer dual weight
  pairs enumerated; optimum 94/46; 81/39 attaining pairs.
- 18,434 finite power-trace identity checks and 90 finite
  intersection/union-cut surrogate checks. These test the
  combinatorics only, not nonstandard models or induction.
- All completed in JS sandbox. Reproduce:
  node research/rh_pl01/packing.mjs
- Source and receipt are in this PR. Independent Node/CI
  and formal model-theory verification remain outstanding.

## 8. Next gate

A larger improvement will require qualitatively new obstructions.
One option is a proof-length attack in a compact arithmetic
calculus where the target sentence is much shorter and the
logical axiom families differ. Another is to pursue an upper
bound and proof translation, so we have an actual interval
rather than repeatedly improving a syntactic floor. For the
present model family, union is a common cheap obstruction
and prevents larger weights. A third countermodel would
need to preserve union and have a provable false-axiom
overlap profile before it could raise the packed cost.
The full candidate ZFC grammar audit, checked equivalence
and proof upper bound remain open.
