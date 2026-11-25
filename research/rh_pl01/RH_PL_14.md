# RH-PL-14: checked pair construction, base coverage, and graph append

Status: seven first-order theorems generated and independently replayed.
Four also passed the original fully expanded string-based checker.
The frozen RH formula, git blob a55f16f293a784ca91d9d52d65cbaea1e89f80dc,
and the RH-PL-02 grammar and two proof encodings are unchanged.
No finite proof upper bound for RH itself or new RH lower bound.

## 1. Pair and singleton lemmas

Use the exact Kuratowski graph convention of induction.mjs:
Single(s,x) iff forall t. t in s iff t=x.
Double(d,x,y) iff forall t. t in d iff (t=x or t=y).
Pair(p,x,y) iff forall t. t in p iff (Single(t,x) or Double(t,x,y)).
At(g,x,y) iff exists p. Pair(p,x,y) and p in g.
The formula constructors use the existing negation/implication expansions
of conjunction, disjunction, biconditional and existential quantification.

pairs.mjs constructs four checked closed theorems:

1. For every x,y there exists p with Pair(p,x,y). Instantiate the fixed
   pairing axiom at x,x to construct a singleton, at x,y for a doubleton,
   and at the two component witnesses. Extensionality identifies any
   other singleton or doubleton with the corresponding witness.
2. Pair(p,x,y) and Pair(p,u,v) imply x=u and y=v. Choose the singleton
   of x. Its membership in p implies it is a singleton of u or a
   doubleton of u,v, so it contains u and hence u=x. Choose the
   doubleton of x,y and use its membership in p to deduce y=u or y=v.
   Reversing the argument gives v=x or v=y. Combine these cases with
   x=u to derive y=v. This proves coordinate injectivity for a common
   pair representative, including the degenerate x=y case.
3. If x,y belong to W, P is the internal power set of W, Q is the
   internal power set of P, and Pair(p,x,y), then p belongs to Q.
   Every component of p has only x and/or y as members, so is a
   subset of W and belongs to P. Thus p is a subset of P and belongs
   to Q. This theorem assumes the two power-set biconditionals
   explicitly; the power axiom constructs those sets in RH-PL-13.
4. If Single(g,p) and Pair(p,x,y), then
   At(g,u,v) iff (u=x and v=y). Eliminate the application witness,
   identify its pair with p, and use coordinate injectivity. Conversely
   transport the two coordinate equalities into the pair relation and
   introduce the application witness.

All case splits are derived in the original Hilbert grammar. The
disjunction convention is not a primitive inference: P or Q means
not P -> Q. The implementation discharges the two case hypotheses
and derives the classical consequence using the existing logical
axioms. All quantifier changes and equality transports are charged.

## 2. Exact bounded family base coverage

The RH-PL-13 candidate family is characterized by
  g in K iff (g subset Q and Good(g))
where Q=Power(Power(W)), and Good specifies:
  an initial-segment domain through some n in W;
  functionality of natural-valued outputs;
  common base output at every empty element of W;
  the normalized multiplication successor recurrence.

prefix_base.mjs reconstructs the identical expanded Good predicate
and family characterization. The generated family characterization was
compared byte-for-byte with the one extracted from the actual closed
RH-PL-13 family-existence theorem. Good has 18,472 unary formula bytes.

Assume a designated empty z in W, a designated initial value c0 in W,
the two exact power-set conditions, and the family characterization.
Construct p=(z,c0) and its singleton graph g. The singleton-graph
equivalence establishes each Good clause:
  domain: its only natural input is z, which is the initial segment
    through z because z is empty;
  functionality: any natural-valued output is c0;
  base: every graph output equals c0;
  successor: if both graph inputs are related by Succ, both must
    equal z. The successor definition then gives z in z, contrary
    to emptiness. The recurrence implication follows by contradiction.

The checked pair bound gives p in Q; the singleton membership
definition gives g subset Q. Apply the exact family biconditional
to derive g in K. For any empty x in W, empty-set uniqueness gives
x=z; transport the graph application and introduce Cover(x).
The resulting theorem discharges base coverage for the collected
family under these six explicit premises. It is a closed universally
quantified implication, not an assertion of an unconditional
factorial graph. The construction has no dependency on arithmetic
multiplication facts.

## 3. Appending one graph entry

append.mjs constructs the appended graph U using the actual fixed
pairing and union axioms:
  p=(x,y); s={p}; f={G,s}; U=union(f).

First derive the membership equivalence
  z in U iff (z in G or z in s)
from the fixed union formula and the doubleton definition. Use the
singleton graph theorem and explicit existential pair witnesses to
derive
  At(U,i,j) iff (At(G,i,j) or (i=x and j=y)).
The universal closure of existence of U with this equivalence is
unconditional. The pair, singleton, family and union witnesses have
all been introduced and eliminated in their legal scopes.

Next assume x,y in W, P=Power(W), Q=Power(P), G subset Q,
functionality of G for inputs/outputs in W, and absence of any
natural-valued G-output at x. The checked pair bound and membership
equivalence give U subset Q. For two natural-valued U-outputs at a
common input, there are four disjunction cases: both old (old
functionality), both new (both equal y), or one old and one new
(the new relation equates the input to x, contradicting absence).
This yields a closed theorem of existence of an appended graph
with the exact relation, boundedness and functionality.

This proves the basic fresh-input append preservation needed for
prefix extension. It has not yet proved that the enlarged graph
satisfies the entire Good predicate. That additionally requires
the initial-segment successor/order facts and proof of the base
and recurrence clauses for the new graph.

## 4. Verification results

Every byte total counts the fully expanded serialization of each
proof line including its LF. DAG sharing changes only internal
representation and certificate size, not the cost metric.

| Closed theorem | Lines | Unary bytes | Compact bytes | Certificate JSON bytes | Original expanded replay |
|---|---:|---:|---:|---:|---|
| Ordered pair exists |4854|17698557|1435387|117945|Pass|
| Ordered pair injectivity |3853|13115516|1231520|96940|Pass|
| Double-power bound |1247|6759148|542921|31513|Pass|
| Singleton graph application |10833|41620884|3680418|269428|Pass|
| Exact bounded family base coverage |28005|349458394|31303394|793316|Not run|
| Graph append application equivalence |21672|152635108|11960185|573967|Not run|
| Bounded fresh append preserves functionality |37855|401597797|30585822|1033477|Not run|

All seven passed assumption-free structural replay and the independent
ordered-DAG certificate verifier from RH-PL-12. It rediscovered earlier
line justifications, checked exact roots, and recomputed unary and
compact costs using arbitrary-precision integers without trusting
producer parent pointers. It shares the original nonpropositional
axiom recognizer. The four smaller theorems also passed full
original-checker replay. The larger three were not materialized as
fully expanded proof strings.

The base theorem has 35,178 reachable formula nodes, and the bounded
append theorem has 46,006. The base theorem uses pairing and
extensionality; the append theorem additionally uses union.
The power-set hypotheses are explicit. No separation instance is
needed for these local theorems because the exact family membership
biconditional is supplied as a premise in the base theorem.
The family construction itself remains charged in RH-PL-13.

## 5. Reproduction

  node research/rh_pl01/pairs.mjs
  node research/rh_pl01/prefix_base.mjs
  node research/rh_pl01/append.mjs
  node research/rh_pl01/pair_audit.mjs pairs
  node research/rh_pl01/pair_audit.mjs base
  node research/rh_pl01/pair_audit.mjs append
  node research/rh_pl01/pair_audit.mjs append --emit 1 > append.json
  node research/rh_pl01/joint_audit.mjs --verify append.json

Generation, independent checks and the four expanded replays were
actually executed in the JS sandbox against fetched committed source
and the frozen target. The standalone Node entry points were not
independently run here; GitHub CI remains pending. No paid compute.

## 6. Remaining existence obligations and next gate

Base coverage is now derived for the exact collected family when the
designated zero and common initial value belong to W and zero is
empty. Local extension has a checked fresh-input append primitive.
The next gate is the ordinary ordinal arithmetic of the least-inductive
set, including transitivity and the successor/initial-segment order
facts. Then establish preservation of the full prefix domain and
recurrence predicates, and the overlap agreement of two prefixes.
Only then can the exact family theorem and its base/compatibility/
extension proofs be composed with the RH-PL-13 gluing theorem.
A bridge to the original existential recurrence clause is still
required. Factorial existence, numerator existence, positivity and
the universal harmonic identity are not yet checked here.

The RH-PL-07 candidate-calculus lower floors remain 570269 unary /
69411 compact bytes. The finite RH proof upper bound is unknown.
The full calculus audit and analytic-to-arithmetic equivalence
remain outstanding. No inference about the shortest RH proof
can be made from the sizes of these interface proofs alone.
