# RH-PL-04: implication-spine lower bounds and encoding sensitivity

Status: exact sandbox tests passed, 2026-11-25. The theorem is for the
declared RH-PL-02 axiom grammar and additive formula-line cost. It covers
all proofs in that grammar, but is a syntactic resource floor. It supplies
no proof of RH, checked upper bound, standard-ZFC metatheory proof, or
encoding-independent lower bound.

## General cost model

Let v be the minimum bytes per variable, d=1+2v the smallest formula
(an atom), q=1+v the minimum universal binder prefix. Every connective
tag costs one byte, every line ends in one LF byte, and variable
encodings are prefix-free. The original unary encoding has v=2,
d=5,q=3. The compact encoding has v=1,d=3,q=2. Define s(F)=formula
bytes excluding LF, s0(F)=minimum-variable-weight syntax size, and

  m(F)=max(s0(F), s(F)-max_t (w(t)-v)*c_t(F)),

where c_t(F) counts free occurrences of t, w(t) is the variable's
encoded length, and an empty maximum is zero. The RH-PL-03 substitution
argument establishes s(G)>=m(F) whenever capture-free variable
substitution takes G to F. This applies to corresponding subformulas
in an implication spine as well, because the right/left implication
positions introduce no binder. For closed F, m(F)=s(F) and a
capture-free substitution yielding F must have G=F.

Let C=1024. Every fixed set axiom has fewer than C bytes in both
encodings. Inventory, extracted from the pinned kernel's fixed map
without changing its recognition semantics:

| Axiom | Unary | Compact |
|---|---:|---:|
| extensionality |54|27|
| empty |16|10|
| pairing |83|37|
| union |93|45|
| power |85|37|
| infinity |136|68|
| foundation |57|34|
| choice |198|95|

The only axioms with universal root are fixed set axioms; separation
starts with negation, replacement with implication, and all logical
axioms start with equality or implication. Thus a universal formula
longer than C is not an axiom. The cap is conservative and must be
re-audited if the kernel's axiom grammar changes.

## Theorem: last-MP implication spine

Consider a nonaxiom F with universal root. Set n=s(F), t=m(F).
Truncate a proof at the first occurrence of F. If its final step is
generalization, it contains a proof of its body G before F, costing
at least s(F)+1+b4(G). Otherwise MP uses A1 and H1=(A1->F).
If H1 is not an axiom, consider the first occurrence of H1; it
cannot be generalization since its root is implication, hence it
has an MP predecessor H2=(A2->H1). Repeat until an axiom Hk.
The indices of the first occurrences decrease strictly:
Hk occurs before H(k-1), ... before H0=F.
All these spine lines are distinct since their sizes strictly
increase along the backwards spine. A1 is distinct from every
spine line (it precedes F, and it is shorter than H1 and all
longer spine lines). For j>=0, s(Hj)>=n+j(d+1).

### k=1

Only universal instantiation can produce an axiom A1->F with
universal consequent. Hence A1=forall x G, s(G)>=t and
s(A1)>=t+q. The three distinct lines cost at least
2n+2t+2q+4.

If t+q>C, A1 cannot be an axiom. Its first occurrence requires either
generalization of G or MP with an implication ending in A1. For
generalization G is distinct from the three counted lines: it is
shorter than A1 and H1, and cannot be F since F first occurs later.
This adds at least t+1 bytes. For MP the additional implication
has consequent A1, hence differs from H1 (whose consequent is F);
it has implication root and differs from A1 and F. It costs
at least t+q+d+2 bytes. In the closed-target case G=F, so
generalization of A1 is impossible before F. Thus the k=1 floor is

  2n+2t+2q+4                  if t+q<=C
  2n+3t+2q+5                  otherwise, F open
  2n+3t+3q+d+6                otherwise, F closed.

### k=2

H2=A2->(A1->F) is an axiom. K would force A2=F, contradicting
chronology. S requires F to have implication root. Atomic equality
substitution requires an atomic F, replacement has a negated
existential consequent, fixed set axioms/separation cannot have
this implication shape. Remaining cases:

* Classical: A2=(not F -> not A1), s(A2)=n+s(A1)+3.
* Universal distribution: F=forall x G,
  A2=forall x (A1->G), s(A2)=n+s(A1)+1.
* Universal instantiation: A2=forall x J, J instantiates to
  A1->F. Its corresponding right subformula costs >=t,
  its left subformula >=d, so s(A2)>=t+d+q+1.

In all three cases A2 is distinct from F by chronology, from H2
by size, and from H1 by root/consequent shape. A2 also differs
from A1: for classical/distribution this is immediate by size;
for instantiation the syntax tree of A2 strictly exceeds that
of A1 (ignore variable indices). Thus five separate lines
F,A1,H1,A2,H2 must occur. Their costs give

  classical:     5n+5d+14
  distribution:  5n+5d+10
  instantiation: 3n+2t+5d+2q+10.

### k=3

H3=A3->(A2->(A1->F)) is an axiom. K forces A3=H1 and is
chronologically impossible: H1 first occurs after H2, yet
A3 must occur before H2. Distribution and equality substitution
require H1 to have universal and atomic roots respectively,
while H1 has implication root. Replacement and fixed axioms
are excluded by the shape as above.

S requires A3=P->(Q->F) for some P,Q, and
s(A3)>=n+2d+2. Classical requires
A3=(not H1 -> not A2), s(A3)>=n+2d+4.
Universal instantiation requires A3 to have a quantified body
instantiating to H2, hence s(A3)>=t+2d+2+q.
All cases imply s(A3)>=t+2d+2, so s(H3)>=n+t+4d+5.
Counting F,H1,H2,H3,A1, without assuming A2 or A3 are distinct
from all those lines, gives 4n+t+8d+13.

### k>=4

Count only F,H1,H2,H3,H4,A1. Their distinctness gives
5n+11d+16. This applies even when the axiom lies very far back
in the proof.

### Recurrence

Define b4(F)=s(F)+1 if F is an axiom, 2s(F)+2d+4 for
nonaxioms of non-universal root, and otherwise the minimum of
the k=1, k=2, k=3, k>=4 and generalization floors. The latter
recurses on a shorter body. The proof above and induction on
leading universal binders establish b4(F)<=L(F). The k split
is exhaustive for the fixed grammar. Reuse of formulas does
not invalidate the count because every charged line has been
shown distinct, and all exclusions use first-occurrence order.
The result extends RH-PL-03 and remains valid for open intermediate
theorems in assumption-free derivations.

## Compact encoding

For variable indices 0..35 use one ASCII character 0..9,A..Z.
For larger indices use ~, the canonical uppercase base-36
numeral with no leading zero, and semicolon. Formula tags stay
e,m,n,i,a; LF separates formula lines. This is prefix-free at
variable positions and is a bijection at the formula AST level.
The mathematical proof rules, target syntax tree and axiom
recognition are identical. Compact verification decodes and
translates into the original checker, so it does not add proof
rules or change the deductive system. JS safe-integer and
resource limits are implementation limits; the mathematical
encoding extends to arbitrary natural-number indices.

Both targets have exactly the same AST (8,204 nodes; 732
universal binders; maximum variable index 35). All variables in
the frozen target fit in one compact byte.

| Metric | Unary | Compact |
|---|---:|---:|
| Formula bytes n |114031|13870|
| Formula line bytes |114032|13871|
| RH-PL-03 b3 |342120|41629|
| Axiom depth 1 |570175|69365|
| Axiom depth 2 |570190|69375|
| Axiom depth 3 |570208|69387|
| Depth >=4 |570226|69399|
| Generalization |684183|83220|
| RH-PL-04 b4 |570175|69365|

The compact target is 87.84% shorter and its certified absolute
bound is about 87.83% lower. Both floors are essentially five
target-line equivalents, which makes clear how much this
improvement still owes to syntax. No evidence of a substantial
lower bound on proof overhead beyond constant target-size
multiples has been obtained.

## Executed controls

Fetched frozen unary target blob a55f16f293a784ca91d9d52d65cbaea1e89f80dc,
decoded, reserialized, and tested identical compact AST.
The fixed-axiom inventory above was independently extracted from the
pinned kernel. Executed in JS sandbox:
- 286 small formula round trips.
- 24,696 generated proof-prefix/encoding bound checks, with explicit
  derivability checks; these counts include shared/repeated prefixes.
- 20,400 capture-safe substitution/encoding floor checks.
- 36,096 terminal axiom/encoding structural floor checks, with
  distinct mandatory-line checks. These are synthetic schema controls,
  not an exhaustive proof search.
- Eight malformed compact strings rejected; extended variable
  round trips at 0,35,36,1295,1296 and JS maximum safe integer.

Commands:
  node research/rh_pl01/spine.mjs
  node research/rh_pl01/spine.mjs --compact | cmp - research/rh_pl01/rh_target_compact.txt

JS sandbox execution passed; Node and CI reproduction remain outstanding.
See spine_receipt.json for exact counts and target measurements.

## Next gate

The major remaining difficulty is a proof-wide lower bound that is large
relative to target syntax. A promising next step is a symbolic cut
certificate using families of formulas classified by a syntactic or
semantic invariant, with a verified load inequality for every permitted
inference instance. The cut universe must include alternative proofs,
and the construction must avoid merely charging repeated target syntax.
For a finite calibration, compare integer cut certificates against exact
proof search with shared subderivations and measure improvements over b4.
For the actual RH target, the upper-bound side and ZFC equivalence proof
also remain open. The compact encoding is a sensitivity control, not a
new official replacement of the original frozen target.
