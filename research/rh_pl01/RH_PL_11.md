# RH-PL-11: exact denominator recurrence normalization and uniqueness

Status: executed proof generation and structural replay, with selected
expanded original-checker replays, 2026-11-25. No proof of RH itself or
new RH proof-length floor. The frozen DMR target (git blob
a55f16f293a784ca91d9d52d65cbaea1e89f80dc), target byte encoding and
RH-PL-02 axiom grammar are unchanged.

## 1. The missing bridge

RH-PL-10 proved graph agreement from totality, a common base and an
abstract coherent-update law. To obtain a concrete arithmetic theorem,
derive those premises from the actual expanded recurrence clauses in D.

The denominator satisfies
  B(0)=1,
  B(S(n))=S(n)*B(n).
In the frozen compiler's relational language the latter equation
contains five existential natural witnesses: k=S(n), a=B(k),
l=S(n), b=B(n), c=Mul(l,b), followed by a=c. In particular the
two successor witnesses k and l are independent until uniqueness
is established. Graph application subformulas also have different
bound variable names. The proof compiler must charge the deductions
which reconcile these occurrences.

## 2. Checked equality transport and alpha conversion

transport.mjs constructs, for a formula P(v) and capture-free variable
substitutions, an explicit Hilbert derivation of

  x=y -> (P[v:=x] -> P[v:=y]).

Use the same predicate template in both directions. In particular
an unrelated free occurrence of y is not replaced by x when
transporting the antecedent of an implication.

Proof by structural recursion:
- If both instances coincide, use identity and K.
- Atoms: perform one-position substitutions with the existing
  atomic equality-substitution axiom, including two substitutions
  if the marker occurs in both positions.
- Implication: use reverse transport (derive y=x by reflexivity
  and equality substitution) on the antecedent, forward transport
  on the consequent, then discharge.
- Negation: contrapose reverse transport.
- Universal binder: instantiate at its own index, transport the
  body, generalize and discharge; enforce capture and generalization
  restrictions. If the substitution would be captured the request
  is rejected.

Each recursive step is a derived theorem using existing axioms,
not a new inference rule. Memoize exact formula IDs and variable
indices.

The alpha-conversion bridge P->Q is also derived recursively:
equal atoms use identity; implications are contravariant in the
antecedent, covariant in the consequent; negations reverse the
bridge and contrapose; universals instantiate at an index absent
from both formulas, prove the corresponding body bridge,
generalize and derive the target binder. Non-alpha-equivalent
atoms/tags are rejected. No syntactic alpha-equality rule is added
to the original checker.

Extensionality yields Empty(x) and Empty(y) -> x=y, and
Succ(n,x) and Succ(n,y) -> x=y. In the empty-set case the two
membership implications follow from the corresponding negated
memberships via the classical axiom. In the successor case,
both membership formulas are biconditional with the same
m in n or m=n expression; compose their implications.

During integration a fresh variable selected solely from the
extensionality target collided with a free variable in the larger
premise package. The compiler's generalization check rejected this.
The integration now supplies v98 explicitly as an eigenvariable
for these calls, and the generalization check still enforces
freshness relative to every undischarged hypothesis actually used.
No checker restrictions were relaxed.

Nine controls, full expanded replay in original checker:
| Control | Lines | Unary bytes | Compact bytes |
|---|---:|---:|---:|
| Atomic double occurrence |53|5425|1474|
| Unrelated occurrence preserved |33|3245|854|
| Negation |165|17052|5089|
| Implication |142|18742|4882|
| Quantifier |190|28166|7106|
| Kuratowski graph application |3807|12354558|992159|
| Nested alpha conversion |169|23385|7300|
| Empty uniqueness |230|186924|24045|
| Successor uniqueness |399|680790|78690|

Three deliberately invalid alpha/transport/capture controls rejected.
The extensionality controls used the automatic local fresh-variable
choice; the larger integration uses the explicit witness option.

## 3. Exact source clause inventory

Decode the frozen target and split its right-associated D
conjunction into the original 22 clauses. The selected clauses
are byte-identical ASTs at zero-based indices:

| Index | Meaning | Unary formula bytes (no LF) |
|---:|---|---:|
|0|Least-inductive omega|732|
|1|Designated zero belongs to omega|6|
|2|Designated zero is empty|28|
|6|Multiplication totality and functionality|5579|
|14|Denominator graph totality and functionality|2615|
|19|Denominator initial value|726|
|21|Denominator successor recurrence|4391|

The designated slots are W=v0, zero=v1, one=v2,
multiplication=v4 and denominator G=v8. An independent comparison
graph H uses v43. Its three clauses are obtained from the actual
denominator totality, initial and recurrence formulas by
capture-free substitution of the graph parameter. The remaining
arithmetic parameters are shared. The final theorem assumes the
conjunction of the seven selected clauses plus those three
comparison-graph clauses. This is a theorem about exact selected
definitions; it has not been composed with all 22 clauses of D
to produce a D-antecedent theorem.

Graph relations in intermediate lemmas are taken directly from
the corresponding functional clauses. When another occurrence
differs only in binder names, apply the derived alpha bridge.
Ordinary graph terms and pairs retain the compiler's expanded
Kuratowski convention.

## 4. Derive the actual base and successor law

### Base normalization

For arbitrary empty x in W and arbitrary natural graph value
a=G(x), extensionality gives x=zero. Equality transport turns
G(x,a) into G(zero,a). The exact initial clause supplies a
natural witness b with G(zero,b) and b=one. Functionality
gives a=b, hence a=one. Eliminate the witness and discharge
the package of hypotheses. Generalize the graph and the two
local variables. This gives the base lemma used for both G
and H.

### Successor normalization

Assume the exact denominator totality/functionality and
successor clauses, natural x,y,u,j, Succ(x,y), G(x,u) and G(y,j).
Instantiate the successor clause at x and unpack all five
existential natural witnesses described in Section 1.

By extensionality k=y=l. Transport the graph relation G(k,a)
to G(y,a), then use functionality with G(y,j) to get a=j.
Likewise functionality gives b=u. The recurrence's last
equality a=c implies c=j. Transport Mul(l,b,c) along l=y,
b=u and c=j, deriving the relation Mul(y,u,j). Eliminate all
five existential witnesses with the checked eigenvariable
rule, discharge the package and generalize.

The normalized recurrence is derived, not an additional assumption:
  x,y,u,j in W and Succ(x,y) and G(x,u) and G(y,j)
    -> Mul(y,u,j),
conditional on the exact denominator graph and recurrence clauses.

### Apply induction

The exact least-inductive omega interface gives the RH-PL-10
separation induction theorem with
  P(x) = forall a,b in W. G(x,a) and H(x,b) -> a=b.

Base: both graphs' arbitrary values at an empty core element
equal the common designated one, by the proved base lemma.

Step: use graph totality to choose predecessor values u,v.
The induction hypothesis yields u=v. For arbitrary natural
successor outputs j,l, the normalized recurrence lemmas yield
Mul(y,u,j) and Mul(y,v,l). Transport v=u, then apply the exact
multiplication functionality clause to get j=l. Eliminate
the two predecessor witnesses. Generalize and discharge to
obtain the exact step premise.

Apply the previously proved separation induction theorem
(using one charged separation axiom). Discharge the ten
source clauses and universally close the root. Therefore
every pair of natural-valued G,H outputs agrees at every
core index. With totality this establishes uniqueness of the
denominator graph's natural-valued function given the declared
definitions. No claim that the entire set representing a graph
is unique: extraneous graph elements remain immaterial.

## 5. Exact proof costs and replay

| Closed theorem | Lines | Unary bytes | Compact bytes | Original expanded replay |
|---|---:|---:|---:|---|
| Denominator base normalization |6019|20370986|2911333|Pass|
| Denominator successor normalization |20400|210690387|24944631|Not run|
| Denominator agreement from selected exact clauses |45991|554307018|65176351|Not run|

All three passed assumption-free structural replay: every
reachable MP and generalization uses an earlier exact parent
formula and all nonpropositional axioms are checked by the
original recognizer. Formula lengths charge every occurrence
of a shared subformula and every LF. The full unary strings of
the last two were not materialized for the original checker.
The 20 MB base proof was expanded and replayed separately
after increasing its cap to 24 MB; the other costs agree
between the repeated local run and the full run.

The agreement proof has one extensionality axiom, one
separation instance, 13 equality reflexivity and 29 equality
substitution lines, 233 universal-elimination and 277
universal-distribution lines, and 22,300 propositional
axiom lines (as reported by the structural replay). Counts
are distinct proof-line counts for this generated derivation,
not lower bounds on all derivations. The full run used 65,670
formula nodes in the shared representation.

Reproduction:
  node research/rh_pl01/transport.mjs
  node research/rh_pl01/denominator.mjs --local
  node research/rh_pl01/denominator.mjs

The JS sandbox executed the controls and proof generation
against the fetched source and frozen target. Independent
Node/CI runs and the full original expanded replay of the
two largest theorems are outstanding.

## 6. Next mathematical gate

For the numerator,
  A(S(n)) = S(n)*A(n) + B(n),
normalize the exact clause 20 against denominator agreement,
multiplication and addition functionality. It has seven
natural witnesses, including the intermediate product and
denominator value. Prove uniqueness using induction (or a
joint invariant), then establish that the denominator agrees
with an independently defined factorial graph. Such graph
existence and the factorial/harmonic arithmetic identities
are further obligations; uniqueness alone does not prove
B(n)=n! or A(n)/B(n)=H_n.

The numerical RH floors from RH-PL-07 remain 570269 unary /
69411 compact bytes in the candidate calculus. There is still
no finite verified upper bound for RH itself. The numerator
normalization, explicit analytic equivalence, ordinary-ZFC
reconstruction, calculus metatheory audit and independent
CI remain open. No paid compute used.
