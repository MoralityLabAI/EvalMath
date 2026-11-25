# RH-PL-13: bounded recursive existence and compatible graph gluing

Status: four checked first-order theorems, independent certificate
replays, and exact finite standard-arithmetic controls, 2026-11-25.
The frozen arithmetic RH target, blob
a55f16f293a784ca91d9d52d65cbaea1e89f80dc, both byte encodings, and
RH-PL-02 grammar remain unchanged. No proof of RH, finite upper
bound on its proof length, or new RH lower bound is claimed.

## 1. What is proved

RH-PL-12 established conditional uniqueness for the harmonic
numerator and denominator graphs. This pass develops the existence
side in three components:
- exact union-of-graphs equivalence, including an existence theorem
  for a total functional graph from compatible partial graphs;
- existence of a normalized denominator recurrence from compatible
  partial graphs with a base and local successor extension property;
- unconditional comprehension of the set of bounded prefix candidates
  via power set and separation.

The last two theorems are separate interfaces. We have not yet
compiled the proof that the specific collected family satisfies
the base, compatibility and extension hypotheses of the existence
theorem. Thus a fully discharged recursive graph existence theorem
from the frozen arithmetic-operation definitions is still open.

All graph application predicates use the expanded Kuratowski
pair convention of RH-PL-10. Different binder names are explicit;
the checked alpha-conversion bridge is available where necessary.
The multiplication graph relation in the new recurrence and
candidate-family predicates is obtained from the actual functionality
clause 6 of the frozen D (with capture-free parameter substitutions).
It is not an uncharged primitive multiplication symbol.

## 2. Graph union and gluing

Let K be a set of partial graph representations, and write
At(g,x,a) for the existing unary graph application formula, meaning
that some Kuratowski pair representing (x,a) belongs to g. At
does not assert functionality or totality.

The fixed union axiom yields U whose members are exactly the members
of some member of K. In gluing.mjs prove both directions of

  forall x,a. At(U,x,a) <-> exists g (g in K and At(g,x,a)).

For the forward implication eliminate an ordered-pair witness in U,
apply the union membership biconditional, eliminate the graph witness,
then reintroduce the same pair as a witness in that graph. Reverse
these steps for the backward implication. Every existential introduction,
elimination, alpha renaming and generalization is checked; the theorem
is unconditional and uses one existing union axiom line.

For the gluing theorem define
  Cover(x) := exists g in K. exists a in W. At(g,x,a).
Assume:
  - the least-inductive-set condition Omega(W) from the frozen target
    with free source variable renamed to v1;
  - the exact RH-PL-10 base and successor induction premises for Cover;
  - compatibility: for any g,h in K, x,a,b in W, if At(g,x,a)
    and At(h,x,b), then a=b.

Apply the checked separation induction theorem to Cover. The union
relation then gives a natural-valued output at every x in W.
If two natural-valued outputs of U exist at x, the forward union
implication supplies two graph witnesses; compatibility equates the
outputs. Discharge all hypotheses and existentially quantify U.
The conclusion is existence of a total functional relation on W,
not absence of extraneous elements in the graph set.

The optional withRelation interface additionally retains the union
application biconditional in the existential conclusion; the next
theorem consumes this stronger interface.

## 3. Local extension and denominator recurrence existence

recursion_existence.mjs assumes these five explicit clauses:
  1. Omega(W).
  2. Base coverage for every empty x in W.
  3. Compatibility across all members of K as above.
  4. Common base: if g in K, x is empty, x,a in W and At(g,x,a),
     then a=c0.
  5. Local extension: if x,y in W, Succ(x,y), and Cover(x),
     then there exist g in K and a,b in W with
     At(g,x,a), At(g,y,b), and Mul(y,a,b).

The designated initial value c0 is a free parameter, not a
literal numeral. In the intended denominator application it is one.
The local extension hypothesis supplies a graph containing both
predecessor and successor values. It does not presuppose a total
graph on all of W.

Derive the coverage successor premise by eliminating the three
local extension witnesses and introducing Cover(y). Apply gluing
with the union relation retained. For the common base, move each
union output to a family graph and apply clause 4. For the successor
law, choose local extension witnesses using Cover(x), map both
witness values back into U and use U's derived functionality to
identify them with arbitrary natural-valued U-outputs. Transport
the Mul relation through both equalities using RH-PL-11. Eliminate
all witnesses, generalize, and discharge the premise package.

The final closed theorem is the universal closure of the implication
from those five clauses to existence of U satisfying:
  - totality on W;
  - functionality for natural-valued outputs;
  - all natural-valued outputs at empty core elements equal c0;
  - for x,y,a,b in W, Succ(x,y), At(U,x,a), At(U,y,b)
    imply Mul(y,a,b).

This is a normalized recurrence. A separate first-order bridge
to the precise existential clause 21 is still required; the
theorem does not silently identify logically equivalent ASTs.

## 4. Unconditional candidate-family collection

prefix_family.mjs gives a closed theorem constructing the set of
all bounded candidates. Here W=v37 (distinct from the fixed
separation slots), initial value=v6, multiplication graph=v8.
Let P=Power(W), Q=Power(P) and R=Power(Q) internally, with the
exact fixed power-set axiom. Every Kuratowski pair of two elements
of W is in Q: its singleton and doubleton components are subsets
of W. This pair-bound observation is a mathematical fact used
in the proposed subsequent prefix-extension proof; the current
serialized collection theorem itself does not depend on a proof
of pair existence or pair injectivity.

For each candidate set s, define Good(s) by four literal clauses:
  - some n in W is a last index, and for every x in W,
    Dom(s,x) iff x=n or x in n, where Dom(s,x) means
    existence of a natural-valued output at x;
  - functionality for natural-valued outputs on W;
  - common base condition at empty core elements;
  - normalized denominator successor law for all natural
    inputs/outputs of s at a successor pair.

This definition allows irrelevant graph elements. It describes
bounded prefix candidates relative to the declared core and
arithmetic parameters; it is not an external finiteness assertion
about arbitrary membership models.

Use separation on R with element variable v0 and output v2.
The exact predicate Good has no free v1 or v2; generalize and
instantiate the separation source to R's witness variable.
Compose the power-set biconditional for R with the separation
biconditional. The closed theorem gives existential witnesses
P,Q,K such that:
  Power(W,P) and Power(P,Q) and
  forall s. s in K <-> (s subset Q and Good(s)).

The third power-set witness R is eliminated, since the conclusion
does not need it. The same fixed power-set axiom line is reused
three times through universal instantiation. The emitted proof
contains one power axiom line and one separation instance.
This establishes candidate-family existence for arbitrary
parameters; it does not assert the family is nonempty or compatible.

## 5. Exact proof costs and independent verification

All costs count the full serialized formula bytes plus LF for
every emitted line. Formula DAG sharing changes storage only.

| Theorem | Lines | Unary bytes | Compact bytes | Certificate JSON bytes |
|---|---:|---:|---:|---:|
| Graph-union equivalence |2292|25598945|2267409|59395|
| Compatible graph gluing |9854|167267210|15088339|268965|
| Normalized denominator existence from local extensions |25019|707251710|67350649|705933|
| Bounded prefix-candidate family exists |2372|353892869|33873144|96175|

All four passed the producer's assumption-free structural replay
and the separate ordered-DAG verifier of RH-PL-12. The latter
rediscovered every line justification without producer parent
pointers, checked closed roots and recomputed both expanded
costs using BigInt. It shares the original nonpropositional axiom
recognizer. The union equivalence additionally passed full
25,598,945-byte original string-checker replay. The other three
full expanded string replays were not run.

The existence theorem's independently reconstructed justification
counts are K=5826, S=5389, classical=930, MP=12541,
generalization=75; forall elimination=88, forall distribution=156,
union=1, separation=1, equality reflexivity=4, equality
substitution=8. Its reachable portable certificate has 31,413
formula nodes. Its closed conclusion is 34,969 unary formula bytes.
The candidate-family theorem has 3,183 reachable nodes and
37,981 unary formula bytes in its closed conclusion; Good has
18,472 unary formula bytes before expansion into separation.

Two integration failures were corrected: a formula constructor
was incorrectly applied to a proof node in final quantifier
closure, and a variable used for a successor was captured by an
inner binder in the graph-union interface. The corrected code
uses proof generalization and a distinct successor variable.
The checker restrictions were not weakened.

## 6. Mathematical construction of the needed prefix properties

The following is an ordinary-ZFC reconstruction plan with a
short mathematical proof. It has not yet been serialized in the
candidate Hilbert calculus.

Assume W is the usual omega, c0=1, and Mul is the ordinary
total functional natural multiplication graph. Let K be the
bounded candidate family of Section 4.

Base: form the singleton graph containing (0,1). Pairing constructs
the Kuratowski pair and singleton. It is bounded by Q=P(P(W)).
It has domain the initial segment through zero, is functional,
has the required base, and its successor clause is vacuous.
It belongs to K.

Extension: if a candidate covers x, its last index n satisfies
x<=n. For y=x+1<=n, the same graph covers y and its local
recurrence holds. If y>n, then n=x. Let a be its value at x;
total multiplication provides b=y*a. Form the union of the
old graph with the singleton containing (y,b), using pairing
and union. It stays bounded by Q, has domain through y,
and is functional by ordered-pair injectivity and the old
domain condition (the old graph had no natural-valued output at y).
The only new successor case is x->y; it obeys the chosen
multiplication law. The resulting candidate belongs to K.
This supplies the local extension witnesses.

Compatibility: for any two candidates with last indices n,m,
compare their outputs along the initial segment through min(n,m).
At zero the base agrees. At a successor within the common domain,
predecessor values agree by induction; functionality of multiplication
equates the successor values. Hence every natural-valued overlap
agrees. Extraneous graph elements cannot alter this conclusion.

Apply the checked local-extension/gluing theorem to the family
after bridging its exact parameter and binder layout. This would
give a total functional denominator graph with normalized
recurrence. Existence of the numerator then follows by the same
finite-prefix construction with the denominator graph already
given: for each next index choose the product, then the sum with
the predecessor denominator. Totality and functionality of addition
and multiplication replace the corresponding multiplication-only
obligations.

In ordinary arithmetic, induction proves B_n=n!>0. Starting
with A_0=0, assume A_n=sum_{k=1}^n n!/k. Then

  A_(n+1) = (n+1) A_n + n!
           = sum_{k=1}^(n+1) (n+1)!/k.

Consequently A_n/B_n=H_n. The algebra is exact, but these
identities and the positive-denominator theorem have not been
compiled to the first-order Hilbert checker.

## 7. Finite arithmetic controls

prefix_controls.mjs ran n=0..128 in exact BigInt arithmetic:
129 factorial checks (independent direct multiplication);
129 numerator checks (direct factorial-weighted summation);
129 positivity checks; 129 comparisons with an independently
maintained reduced harmonic rational; 128 prefix extension
checks; 366,145 overlap-value comparisons over all pairs of
prefixes; 129 union coverage/value checks; and 258 rejected
terminal numerator/denominator mutations. Total 367,176 checks.
These finite standard-natural controls do not prove induction,
prefix compatibility in arbitrary models, or the universal RH
inequality.

## 8. Reproduction and open gates

  node research/rh_pl01/gluing.mjs
  node research/rh_pl01/recursion_existence.mjs
  node research/rh_pl01/prefix_family.mjs
  node research/rh_pl01/prefix_controls.mjs
  node research/rh_pl01/recursion_audit.mjs union
  node research/rh_pl01/recursion_audit.mjs glue
  node research/rh_pl01/recursion_audit.mjs existence
  node research/rh_pl01/recursion_audit.mjs family
  node research/rh_pl01/recursion_audit.mjs existence --emit > existence.json
  node research/rh_pl01/joint_audit.mjs --verify existence.json

The underlying runs were executed in the JS sandbox against
fetched committed code and target. The standalone Node entry
points and GitHub CI have not been independently executed here.
No paid compute used.

Next formal gate: pair existence and injectivity, pair bound
in the double power set, singleton base and append preservation,
initial-segment overlap induction, exact family-to-gluing
parameter bridge, and equivalence of normalized and original
recurrence clauses. The ordinary mathematical proof in Section 6
identifies these obligations rather than supplying a serialized
proof of them.

RH-PL-07's candidate-calculus lower floors remain 570269 unary /
69411 compact bytes. Its upper bound is unknown. The full
standard-ZFC calculus audit, analytic-DMR equivalence, ordinary-ZFC
RH reconstruction and independent CI remain outstanding.
