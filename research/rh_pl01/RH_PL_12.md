# RH-PL-12: exact numerator normalization and joint harmonic graph agreement

Status: executed proof compilation, structural replay and independent
certificate replay, 2026-11-25. The RH-PL-03 target (git blob
a55f16f293a784ca91d9d52d65cbaea1e89f80dc), its two byte encodings and
the RH-PL-02 proof grammar remain unchanged. No proof of RH itself,
new lower bound for RH, or finite upper bound on its proof length.

## 1. Exact arithmetic clauses

The frozen DMR target has 22 top-level definition clauses. Extract the
following exact ASTs from the frozen target, numbered from zero:

| Index | Definition | Unary formula bytes, excluding LF |
|---:|---|---:|
|0|Least-inductive omega|732|
|1|Designated zero belongs to omega|6|
|2|Designated zero is empty|28|
|5|Addition totality/functionality|5576|
|6|Multiplication totality/functionality|5579|
|13|Numerator totality/functionality|2612|
|14|Denominator totality/functionality|2615|
|18|Numerator initial value|724|
|19|Denominator initial value|726|
|20|Numerator successor recurrence|7704|
|21|Denominator successor recurrence|4391|

The original parameter slots are W=v0, zero=v1, designated one=v2,
addition=v3, multiplication=v4, numerator G=v7 and denominator B=v8.
The comparison numerator H=v44 and denominator C=v43 have six
definition clauses obtained by capture-free substitution from the
original six graph clauses. In the comparison numerator recurrence,
both graph parameters are substituted. The theorem assumes the
conjunction of the eleven original clauses and six comparison clauses.
It concludes agreement of all natural-valued graph outputs at each
input in W, separately for the numerator and denominator. No assertion
of equality of arbitrary extraneous elements in the graph sets.

The common designated one suffices for the uniqueness theorem;
the extra D clauses identifying it as successor of zero and a member
of W were not needed. The actual frozen D contains those clauses.
The selected-clauses antecedent is not the entire D conjunction.

## 2. Numerator base and successor normalization

RH-PL-11 established checked alpha conversion, equality transport,
empty/successor uniqueness and denominator agreement. Reuse the same
combinators. No new axiom schema or free proof rule is introduced.

Base: for any empty x in W and any natural numerator output a,
extensionality gives x=designated zero. Transport the graph application,
unpack the exact initial clause's witness, and apply functionality
to obtain a=designated zero.

Successor: suppose x,y,u,j,b in W, Succ(x,y), G(x,u), G(y,j),
and B(x,b). Assume G and B have the declared graph functionality
and G obeys the exact numerator successor clause. The clause at x
provides seven successive natural witnesses:
  k=Succ(x), a=G(k), l=Succ(x), n=G(x),
  c=Mul(l,n), d=B(x), e=Add(c,d), with a=e.
The two successor witnesses are reconciled by extensionality.
Functionality gives a=j, n=u, d=b; the last equality gives e=j.
Transport the product and sum graph relations to obtain

  exists c in W. Mul(y,u,c) and Add(c,b,j).

The proof introduces this existential before eliminating the seven
local witnesses. All generalizations, alpha bridges and equality
transports are compiled to the original Hilbert rules. The local
source clauses are extracted directly; graph occurrences with
different bound names are reconciled by the derived alpha bridge.

## 3. Joint recurrence agreement

First construct numerator agreement conditional on denominator
agreement. The induction predicate says that all natural outputs
of G and H at a given input agree. Use the exact omega interface
from RH-PL-10, which introduces a charged separation instance.

For the base, apply the normalized base theorem to G and H.
For the step, obtain predecessor values for all four graphs by
their totality clauses. The numerator induction hypothesis equates
the two numerator values, while denominator agreement equates
the denominator values. Apply the normalized successor theorem
to each numerator graph, obtaining an intermediate product witness
for each. Equality transport and multiplication functionality
equate those product witnesses. Transport the second addition
relation along the product equality and denominator equality;
addition functionality gives equality of successor outputs.
Eliminate all predecessor and product witnesses, discharge the
step premise and apply the checked induction theorem.

For the final joint theorem, rebuild RH-PL-11's denominator
agreement proof in the same exact formula arena. The previous
denominator module now exposes an additive proof-construction
interface returning its open theorem and exact premises, without
altering its default or local run. Derive denominator agreement
by applying that theorem to the corresponding eleven-plus-six
premise package's selected clauses. Apply the numerator theorem
with this derived denominator agreement, conjoin the two
conclusions, discharge the package and universally close.

All dependencies are actual proof nodes. The final theorem has
two charged separation instances, one for each induction.
It does not assume denominator agreement as an additional axiom
or omit the cost of the denominator derivation.

## 4. Measured proof sizes

All values include LF per emitted proof line. Fully expanded
formula bytes are charged even when the internal representation
shares a subformula.

| Closed theorem | Lines | Unary bytes | Compact bytes | Original expanded replay |
|---|---:|---:|---:|---|
| Numerator base normalization |6018|20348786|2910541|Pass|
| Numerator successor normalization |28389|598319739|69076884|Not run|
| Numerator agreement given denominator agreement |69221|1430045416|168153964|Not run|
| Joint graph agreement from exact selected clauses |94425|2405544949|294631981|Not run|

All four passed assumption-free structural replay. The original
string checker separately accepted the fully expanded 20.35 MB
base proof. The other three expanded string replays were not
run. The main generation used 129,549 exact formula nodes.
The closed joint conclusion is 57,831 unary formula bytes.
These are upper bounds for the specified interface theorems,
not for RH.

## 5. Independent portable certificate replay

joint_audit.mjs exports a version-1 JSON certificate containing
only the reachable formula DAG in topological order, the ordered
proof-line formula IDs, the root, its exact unary formula, and
the claimed expanded costs. It contains no producer inference
parent pointers or trusted rule labels. The generated certificate
is 2,697,601 ASCII JSON bytes before the optional final LF,
with 117,353 reachable formula nodes and 94,425 proof lines.

The independent verifier:
- Checks constructor arities, safe nonnegative variable indices,
  strict topological child ordering, canonical syntactic node
  uniqueness and closed root.
- Recomputes exact free-variable sets and BigInt unary/compact
  serialized costs from the grammar. Sharing does not reduce
  the charged cost of a repeated formula occurrence.
- Reconstructs each line's justification from earlier lines.
  A declarative independent matcher checks K/S/classical
  schemas; MP and generalization search the earlier formulas.
  Nonpropositional axiom recognition calls the existing
  RH-PL-02 kernel's axiom recognizer.
- Checks root AST against the exact target formula in the
  certificate and checks both expanded cost claims.

Results:
| Independently found justification | Lines |
|---|---:|
| K |21984|
| S |19977|
| Classical |3748|
| MP |47343|
| Generalization |375|
| Forall elimination axiom |399|
| Forall distribution axiom |526|
| Extensionality |1|
| Equality reflexivity |20|
| Equality substitution |50|
| Separation |2|

The independent verifier accepted the entire joint theorem and
recomputed exactly 2,405,544,949 unary / 294,631,981 compact
bytes. This verifies the ordered expanded-proof representation
structurally without allocating the full proof string. The
verification is independent of the generator's parent pointers
but still shares the original kernel's nonpropositional axiom
recognition and its declared proof grammar. It is not a second
formalization of ZFC metatheory, nor a full original string replay.

Mutation audit: incorrect cost, incorrect root, cyclic formula
reference and removal of the first separation line all rejected.
The last mutation failed on an unjustified line (zero-based
index 44,012 in the shortened proof). Mutation commands are
included in the auditor. The certificate is regenerated on
demand rather than committed as a multi-megabyte blob.

## 6. Reproduction

  node research/rh_pl01/numerator.mjs --local
  node research/rh_pl01/numerator.mjs
  node research/rh_pl01/joint_audit.mjs --mutations
  node research/rh_pl01/joint_audit.mjs --emit > joint.json
  node research/rh_pl01/joint_audit.mjs --verify joint.json
  node research/rh_pl01/joint_audit.mjs --target

The actual computations ran in the JS sandbox with the fetched
repository code. The standalone Node entry points and independent
CI have not been run here. No paid compute.

## 7. Next gate

The uniqueness step establishes at most one natural-valued
solution to these recurrences, given the shared arithmetic
operations and least-inductive set. It does not construct the
factorial and harmonic graphs or prove that the provided graphs
exist in the selected axiomatic fragment. Next develop a checked
finite-sequence recursion construction (existence, extension,
and uniqueness), then prove that B agrees with factorial and
that A(n)/B(n)=H_n with a positivity theorem for B. A separate
route would use exact integer identity induction before defining
rational division. These are prerequisites to a fully charged
arithmetic equivalence proof, not the analytic RH proof itself.

RH-PL-07's candidate-calculus lower floors are unchanged:
570269 unary / 69411 compact bytes. No finite RH proof upper
bound is known in this project. The complete calculus audit,
ordinary-ZFC reconstruction, analytic-DMR equivalence proof
and independent CI remain open.
