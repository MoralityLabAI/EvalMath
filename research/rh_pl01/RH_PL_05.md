# RH-PL-05: proof-wide semantic obstructions for the frozen RH target

Status: two explicit countable countermodels of the target in weak fragments,
a finite-model no-go theorem, and an additive proof-wide semantic floor.
No countermodel of ZFC or of arithmetic RH in the standard natural numbers
is claimed. No kernel-checked ZFC equivalence or proof upper bound is supplied.
The results use the exact RH-PL-02 grammar and RH-PL-03 target, pinned at
blob a55f16f293a784ca91d9d52d65cbaea1e89f80dc.

## 1. Semantic cut packing

Interpret an open formula as valid in a structure M if true under every
assignment. Identity interprets equality. Every declared logical axiom is
valid in every nonempty membership structure; modus ponens and unrestricted
generalization of theorems preserve validity. If M falsifies a closed
target F, a proof of F must contain at least one nonlogical axiom instance
false in M. This applies to an arbitrary proof, regardless of line count
or intermediate statements, and to every instance of separation/replacement.

For models M_i falsifying F, let E_i(a) indicate that a nonlogical axiom a
is not valid in M_i. Nonnegative rational weights y_i with
sum_i y_i E_i(a) <= c(a) for *every* nonlogical axiom instance a give a lower
bound sum_i y_i on the cost of nonlogical axiom lines in any proof. Sum the
cover constraints over models and interchange the sums; extra occurrences
of axioms do not harm the bound. Costs may instead be residual capacities
after an independently justified syntactic charge, provided they are
nonnegative and the load inequality remains valid.

## 2. Finite-model no-go

If a structure has an inductive object W, choose x_0 in W whose extension
is empty, and repeatedly choose x_(j+1) in W whose extension equals
Ext(x_j) union {x_j}, as required by the definition. Induction shows
Ext(x_j)={x_0,...,x_(j-1)}, the previous objects are distinct, and the
extension of the next object has cardinality j+1, so it differs from
each preceding extension. Therefore W contains infinitely many distinct
objects. This argument needs neither extensionality nor foundation.
The frozen target's definitions include inductiveness. Every finite
membership structure therefore satisfies the target vacuously, and also
falsifies the fixed infinity axiom. No finite model can supply a semantic
cut for this target.

Exhaustive enumeration on domain sizes 1..4 checked 66,066 membership
relations and 263,714 candidate inductive objects, with zero successes.
This is a finite control of the general mathematical argument.

## 3. Countermodel A: a self-successor

Domain: formal finite sets over the ordinary finite ordinals, a special
object r, and six named graph objects, closed under forming finite sets.
Canonicalize every finite set by its extension (including identification
with an ordinary finite ordinal when appropriate). The extension of r is
all finite ordinals together with r itself. Each graph object's extension
is the infinite Kuratowski-pair graph of the specified operations below.
Graph nodes are distinct (binary input pairs cannot be natural-number
objects, and each pair of same-arity functions differs at some input).
Graph nodes lack 0 as a member; their members are Kuratowski pairs, each
nonempty and not containing 0. All graph extensions are infinite and
distinct from the extension of r. This specifies a countable extensional
relational structure. All finite subsets of the domain are represented,
so pairing and empty set hold.

Interpret the target's w as r and its naturals as N union {r}. Ordinary
finite ordinals and their successors behave normally. The successor of
r is r, since its extension already contains r. Only r is inductive:
any inductive object contains all ordinary finite ordinals (successors
unique by extensionality), finite sets cannot do so, and graph nodes
lack 0. Hence r is the target's least inductive object, and infinity
holds. Foundation fails at the singleton {r}.

On N union {r}, addition agrees with ordinary addition on finite inputs
and returns r whenever either input is r. Multiplication returns 0 if
either input is 0, otherwise r if either input is r, and ordinary product
otherwise. These obey the specified zero/successor recurrences for all
inputs, including r. The membership comparison x<y is ordinary on
finite inputs, and every natural including r is a member of r.
Let L,D,A,B on finite inputs be the standard sequences in RH-PL-03.
Set L(r)=D(r)=r, A(r)=B(r)=0. L(r) is the unique positive common multiple
of every positive natural, because r divides only 0 and r. For a finite
input, ordinary L is still least; r is an additional common multiple
but every finite ordinal is a member of r. The D recurrence at r is
r=r*r; the A,B recurrences are 0=r*0+0 and 0=r*0. Thus all target
definitions hold. At n=r, D(n)=r, A(D(n))=B(D(n))=0, and the inequality
is 0<0, false.

The cheapest false nonlogical axiom costs 58 unary / 35 compact bytes:
foundation is false, and every shorter fixed axiom is true (extensionality,
empty). All separation instances have at least 58/36 bytes, replacement
at least 125/70, and other fixed axioms are longer. This gives the
preliminary semantic floors 570233/69400.

## 4. Countermodel B: a well-founded extra successor chain

The stronger model is an actual transitive collection of well-founded
sets in the ambient set theory. Write t_1={1}, t_(j+1)=t_j union {t_j}
for j>=1. Thus t_j={1,t_1,...,t_(j-1)}. Every t_j is hereditarily
finite, distinct from every ordinary ordinal (nonempty and lacks 0),
and the t_j are mutually distinct by size. Define W=N union {t_j:j>=1}.
Let the domain be HF, W, and the six infinite operation graphs over W
defined below, closed under finite-set formation. All elements of these
objects are in the domain: W and graph entries are hereditarily finite,
and HF is transitive. Every element of the domain is a well-founded
actual set, so foundation and extensionality hold in the induced
membership structure. Empty and pairing hold, and W is inductive:
ordinary n has successor n+1 and t_j has successor t_(j+1). W is the
only inductive object, because all other objects are finite or are
graphs lacking zero. Therefore the definitions of omega and infinity
hold. In particular the model preserves foundation, unlike A.

Use the weights |n|=n and |t_j|=j. For x,y in W:
- Addition is ordinary for two ordinary inputs; otherwise it is
  t_(|x|+|y|). At least one tag ensures the weight is positive.
- Multiplication is zero if either input is 0. For positive inputs:
  ordinary*ordinary is ordinary product;
  t_j*y=t_(j*|y|) for either kind of positive y;
  1*t_j=t_j;
  n*t_j=n*(j-1) (ordinary), for ordinary n>=2.
  This intentionally asymmetric operation is allowed by the target's
  recurrence-only definitions. It obeys multiplication by zero and
  x*succ(y)=x*y+x for every kind of input. Addition similarly obeys
  x+0=x and x+succ(y)=succ(x+y). For tagged y the weight advances by
  one, and the exceptional ordinary n>=2 product advances by n.
- The natural membership order is ordinary within N and
  t_i in t_j iff i<j. The only ordinary natural in t_j is 1.
  There is no tagged element in an ordinary ordinal.
- For a positive tagged target, an ordinary divisor exists iff that
  divisor is 1. Tagged divisors of t_j are exactly t_i with i|j.
  Ordinary positive targets have exactly their ordinary positive
  divisors: the special n*t_j ordinary products are still multiples
  of n. These statements follow directly from the multiplication cases.
- For ordinary n, take ordinary L(n); for t_j take t_(L(j)).
  If n=0 or 1, L(n)=1 is <= every positive natural, including tagged
  ones. If n>=2, tagged common multiples are impossible since 2
  cannot divide a tagged number. Thus ordinary L is least. For t_j,
  the positive predecessors including itself are 1 and t_1..t_j.
  A common multiple must be tagged and its weight divisible by
  1..j; the chosen tagged L is precisely the least such weight.
- For ordinary n, use the usual D,A,B recurrences. Set
  D(t_j)=t_(D(j)), A(t_j)=B(t_j)=0.
  Then D(t_(j+1))=t_(D(j)*L(j))=D(t_j)*L(t_j).
  Since multiplication by zero yields zero, the A,B recurrences
  hold along the entire tagged chain; the ordinary initial conditions
  constrain only the ordinary successor chain.

Represent all six graphs by their actual Kuratowski-pair sets
(binary graphs use nested pairs), with exactly the prescribed
domain and outputs. Every graph is total and single-valued on W;
the nested-pair and ordinary-pair graph conventions agree with
the compiled formula. The graph nodes are actual sets and can coincide only if their
extensions really coincide; any coincident graph symbols would still
interpret their specified graphs correctly. No graph equals W,
since its members lack 0 and its extension does not contain 0.
All definitions therefore hold, but at n=t_1 the D value is t_1,
the A,B values are both zero, and the strict inequality is 0<0.

This model does not satisfy full separation. With source W and
parameter v3 interpreted as ordinary 0, use phi=M(v3,v0).
It selects precisely the positive ordinary finite ordinals. This
infinite set is absent from the domain: it is not W, no finite
object equals it, and no graph node equals it because it contains
1, whereas every graph member is a Kuratowski pair and 1={0}
cannot be such a pair. This explicit false separation instance
is recognized by the checker. Its cost is 64 unary / 36 compact.

## 5. Exact cheapest false axiom in B

In the unary grammar a separation line has cost
58+2(s(phi)-5), where s excludes LF. The shortest atomic formula
is 5 bytes; the two copies of phi arise from expanded biconditional.
Replacement has cost at least 125 unary / 70 compact, by substituting
minimum-length atoms into both predicate slots. The fixed possibly
false axioms union, power, choice have costs 94/86/199 unary and
46/38/96 compact. The remaining fixed axioms, including foundation,
are true in B.

A separation line below 64 unary bytes requires s(phi)<=7.
Every such admissible phi is an iterated negation of an atom
using only v0 (element x) and v1 (source a): v2 cannot occur free,
and there is no room for a quantifier or implication. For x in a,
well-foundedness makes x!=a, x notin x, a notin a, and a notin x;
the remaining equality/membership atoms are constant as well.
Thus phi is uniform over every source, and the required subset
is either the source itself or empty. Both are present. The
exhaustive grammar census found 16 such admissible predicates.
All have true separation in B. Since the explicit false instance
above costs 64, the minimum false nonlogical axiom cost is exactly
64 unary. In compact encoding every separation line costs >=36
and the same false instance attains 36; every other possibly
false family has larger cost. Hence the compact minimum is
exactly 36.

## 6. Combining with RH-PL-04 without double charging

Let delta be this minimum false-axiom line cost. For the large
closed universally quantified frozen target, the k=1 spine case
charges F,A1,H1 and the additional implication ending in A1.
None is a nonlogical axiom: F and A1 exceed the fixed-axiom cap,
and the charged implications have universal consequents. The
false axiom mandated by model B is a distinct line, adding delta.

For k=2, among F,H1,H2,A1,A2 only A1 could be a false nonlogical
axiom. The large universally rooted A2 of instantiation or
distribution is not a fixed axiom; in the classical case its
antecedent is negated, excluding replacement. H_i end in a
universal formula or implication, excluding nonlogical schema
axioms. For k>=3 the counted lines are F, the spine lines and
A1; again only A1 could be a false axiom. If that line is false
in B it costs at least delta instead of the generic atom-line
floor d+1 already charged. If it is not, an extra distinct line
costs delta. Thus add delta-(d+1) in the k>=2 cases, leaving the
generalization branch unchanged. This is a residual-capacity
argument, not naive addition of independently derived bounds.

| Case | Unary | Compact |
|---|---:|---:|
| RH-PL-04 overall floor |570175|69365|
| k=1 |570239|69401|
| k=2 |570248|69407|
| k=3 |570266|69419|
| k>=4 |570284|69431|
| Generalization |684183|83220|
| RH-PL-05 overall floor |570239|69401|

Every proof of the frozen formula in the declared calculus has
at least these costs, or no proof exists. No verified upper
bound is known here. The semantic increment is 64/36 bytes, not
a substantial increase in normalized proof complexity. The
novelty is that the additional obligation depends on axiom use
throughout the entire proof.

## 7. Executed controls and reproducibility

- Complete finite census (66,066 structures, 263,714 candidates).
- Model A: 143 arithmetic, 68 LCM, 225 pair, 252 graph-membership,
  15 graph-distinction controls; explicit false inequality.
- Model B: 400 arithmetic, 351 HF-membership, 105 LCM and 169
  divisibility controls; explicit false inequality.
- Exact enumeration of 16 short admissible separation predicates.
- Fetched target round trips and both encodings' residual bounds.
- All executable controls passed in the JS sandbox. The proof of
  the infinite models is the mathematical argument above, not an
  extrapolation from the finite sample. No Lean formalization or
  Node/GitHub CI run is claimed.

Run:
  node research/rh_pl01/semantic.mjs
  node research/rh_pl01/well_founded.mjs
  node research/rh_pl01/semantic_refined.mjs

Receipts preserve the first model, second model, and refined
minimum separately. The latest semantic_refined_receipt.json
supersedes the earlier weaker floors for this target.

## 8. Next gate

The next worthwhile improvement requires countermodels satisfying
substantially stronger separation/induction fragments, or multiple
obstructions whose eliminating axioms have provably limited overlap.
Our malformed successor-chain models are removed by a cheap bounded
separation instance. A meaningful proof-overhead floor needs a different
family. The two models are not independent additive certificates:
a single separation instance may eliminate both, so we charge only
the stronger model. Do not infer any lower bound on the usual arithmetic
theorem in PA, or an intrinsic RH proof-length bound, from these models.
The candidate ZFC schema-equivalence audit, actual analytic-to-arithmetic
proof translation, and checked upper bound remain open.
