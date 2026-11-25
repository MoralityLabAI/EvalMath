# RH-PL-10: checked induction and graph recurrence agreement

Status: executed proof compilation and replay, 2026-11-25.
The frozen target (blob a55f16f293a784ca91d9d52d65cbaea1e89f80dc)
and RH-PL-02 axiom grammar are unchanged. No proof of RH or new
numerical RH proof-length bound is claimed.

## 1. Exact induction interface

Extract the least-inductive-set clause Omega(w) from the actual
frozen arithmetic definition conjunction D. Its original unary
formula length is 732 bytes. The source variable is v0.
Capture-free substitution changes its free source variable to v1
for the fixed separation schema. All bound variable names in
the extracted clause are preserved.

Given a predicate phi with free element variable v0, separation
is the exact existing axiom
  exists v2 forall v0.
    (v0 in v2 <-> (v0 in v1 and phi)).
It is recognized by the original checker. The predicate must
have no free v2 and the fresh variables used by the compiler
must be available. All actual substitutions are checked for
capture; the implementation rejects collisions.

The base premise B is
  forall z. (Empty(z) and z in w) -> P(z).
The step premise T is
  forall x y. (x in w and (y in w and
    (Succ(x,y) and P(x)))) -> P(y).
Empty and Succ use the expanded first-order membership definitions.
The derived open theorem is
  Omega(w) -> (B -> (T -> forall n. n in w -> P(n))).
No assumption of arithmetic induction is added to the kernel.

Proof construction:
1. Use the exact separation instance to obtain the subset S.
2. From the zero witness in Omega(w)'s inductive clause, use B
   to show zero is in S. From the successor witness in the same
   clause and T, show S is closed under successor.
3. Combine the two clauses to obtain Inductive(S), with the
   exact binder names expected by the extracted leastness formula.
4. Instantiate leastness at S to obtain w subset S.
5. Use the forward separation biconditional to derive P for
   every member of w. Eliminate the existential separation witness.
6. Discharge all three local hypotheses. Generalize the free
   source variable v1 and instantiate it at v0, recovering the
   exact original Omega(v0) antecedent byte-for-byte. Universally
   close the resulting theorem.

The output is a theorem conditional on B and T. The base and
step premises for the harmonic denominator and graph agreement
are not asserted as theorems of the frozen D at this stage.

## 2. Natural deduction proof DAG

induction.mjs introduces no new trusted logical rules. Its
internal proof nodes have an exact formula ID, rule, actual
parent proof nodes and a set of undischarged hypothesis IDs.

- Axioms: K/S/classical checked by the RH-PL-09 exact structural
  recognizer; nonpropositional axioms checked by the original
  RH-PL-02 axiom recognizer.
- MP: compare exact antecedent and implication IDs.
- Generalization: reject when the variable occurs free in any
  undischarged hypothesis on which the proof depends.
- Discharge: structural deduction theorem transformation.
  If the proof does not depend on the discharged hypothesis,
  lift it using K and MP. The hypothesis case uses the five-line
  K/S identity proof; MP and generalization use S and the
  existing forall-distribution axiom respectively. Cache
  identical proof transformations.
- Propositional operations instantiate RH-PL-08 templates and
  derive contraposition from DNE, DNI, composition and the
  classical axiom. Conjunction introduction is also expanded
  through these operations.
- Universal instantiation: use the original capture-free axiom.
  Universal renaming is derived by instantiating a quantified
  hypothesis at a fresh variable, generalizing, discharging and
  applying MP. Alpha-equivalence is not a free proof rule.
- Existential introduction/elimination: expand exists as
  not forall not. Introduction uses universal instantiation
  under contraposition. Elimination derives not G -> forall x
  not F(x) from a witness derivation F(x) -> G, with an explicit
  eigenvariable check, then contraposes and uses DNE. Renaming
  is implemented by the derived universal bridge. The witness
  must be absent from the conclusion, existential formula's
  free variables, and all other assumptions used by the proof.

Only exact syntax sharing is used. A postorder traversal of
the root proof emits the reachable, assumption-free lines and
deduplicates literal formula IDs. Structural replay verifies
each actual parent inference and checks all nonpropositional
axioms with the original recognizer. Formula cost charges the
full expanded unary or compact serialization plus LF for
each line. No internal DAG pointer is charged as an encoded
proof line. The original checker can independently replay
the expanded proof when within the configured size cap.

## 3. Three induction instances and one exact D bridge

All three predicate proofs use one recognized separation
instance. The graph application predicate At(G,x,a) expands
membership of a Kuratowski pair (x,a) in G using the same
set-theoretic graph convention as the frozen arithmetic target.
Its binder slots are chosen fresh; it is not a byte-identical
copy of every graph occurrence in D.

Predicates:
- membership P(x) := x in parameter v4;
- no-zero-denominator P(x) := not At(v8,x,v4), with v8 the
  denominator graph slot and v4 a free zero-reference parameter;
- graph agreement P(x) := forall a b. (a in w and (b in w and
  (At(v8,x,a) and At(v5,x,b)))) -> a=b. The second graph slot is
  a generic comparison parameter, not asserted to be a second
  harmonic graph in the original D.

| Closed theorem | Lines | Unary bytes | Compact bytes | Separation unary/compact |
|---|---:|---:|---:|---:|
| Membership induction |3732|5958446|916447|66 / 36|
| No-zero-denominator induction |3733|35842233|3297478|2906 / 278|
| Graph agreement induction |3733|75328355|6150498|6694 / 568|
| Exact D -> membership induction (B,T remain antecedents) |3781|16374308|2450401|66 / 36|

The D bridge imports the exact open D->Omega(v0) proof from
RH-PL-09 and composes it with the membership induction theorem.
The imported derivation is rechecked; it is not treated as a
free lemma. The original D is unchanged.

The original string-based kernel accepted the full expanded
membership and D-bridge proofs in the main run, and both graph
instances in a separate enlarged-cap replay. The first main
receipt records the graph proofs as not replayed due to its
24 MB cap; induction_replay_receipt.json supersedes those flags.
There are four distinct expanded theorem replays in total.
All four also passed structural replay.

## 4. Conditional recurrence uniqueness theorem

recurrence_agreement.mjs derives the base and step premises
of graph-agreement induction from explicit assumptions about
two total graphs and a common update law. The root is closed.

Let G,H be graphs on the natural core w and c0 a common base
value. Write P(x) for agreement of every pair of natural-valued
outputs at x (the exact graph-agreement predicate above).
Assume the following six clauses:
1. Omega(w).
2. For every x in w there exists a in w with At(G,x,a).
3. The same totality for H.
4. For every empty x in w, every natural-valued G-output at x
   equals c0.
5. The corresponding common-base condition for H.
6. Coherent update: for x,y,a,b,c,d in w, if Succ(x,y),
   At(G,x,a), At(H,x,b), At(G,y,c), At(H,y,d), and a=b,
   then c=d.

All six clauses are literal first-order formulas. Clause 6 uses
a chain of implications so its individual premises can be
applied directly. It expresses the compatibility that follows
when both graphs obey the same deterministic recurrence, but
that implication from the concrete frozen recurrence definitions
has not yet been proved. In particular no new function symbol or
unverified mathematical theorem is introduced.

Base proof: for an empty x in w and arbitrary natural-valued
G-output a and H-output b, the base conditions give a=c0 and
b=c0. Derive c0=b using reflexivity and an atomic equality
substitution axiom; derive a=b with a second atomic substitution.
Generalize the output variables and discharge the base premises.

Step proof: assume x,y in w, Succ(x,y), and P(x). Choose natural
outputs a,b at x by the two totality conditions, using fresh
existential witnesses. P(x) gives a=b. For arbitrary natural
outputs c,d at y, coherence gives c=d. Eliminate both predecessor
witnesses, discharge and generalize to obtain the exact step
premise of the induction theorem.

Apply the checked induction theorem to the Omega, derived base
and derived step proofs. Discharge the conjunction of the six
assumptions and universally close all parameters. The conclusion
is agreement for every core input. Totality ensures this is
agreement of existing natural outputs, and the all-output-pairs
condition also implies uniqueness of natural-valued outputs for
both graphs under the declared premises.

The proof was generated and structurally replayed:
  lines: 6928
  unary: 175465041 bytes
  compact: 14246041 bytes
  closed conclusion: 21358 unary formula bytes
  axiom counts: propositional 3343, forall-elimination 35,
    forall-distribution 47, equality-reflexivity 1,
    equality-substitution 2, separation 1.
The full 175 MB unary proof was not materialized for original
string-checker replay. Its structural replay checks every
inference and each nonpropositional axiom with the original
recognizer. The separate expanded replays in Section 3 give
controls, not a substitute for this missing full replay.

## 5. Executed controls

Four deliberate failures rejected: variable capture in
substitution, generalization over a hypothesis's free variable,
separation-output variable collision, and an illegal existential
elimination with the witness escaping into the conclusion.
The main induction run generated 14,913 exact formula nodes
and 11,534 internal proof nodes, including local derivations.
The three induction instances, exact D bridge and recurrence
agreement theorem all passed structural replay. The four
induction/interface theorems passed expanded original replay
as described above.

Commands:
  node research/rh_pl01/induction.mjs
  node research/rh_pl01/induction_replay.mjs
  node research/rh_pl01/recurrence_agreement.mjs
  node research/rh_pl01/recurrence_agreement.mjs --target

Tests ran in the JS sandbox using fetched code and target.
No independent Node/CI run or Lean metatheory formalization
is claimed.

## 6. Next gate and interpretation

The next mathematical gate is to discharge the concrete
coherent-update and common-base assumptions for the harmonic
denominator recurrence using D's totality, multiplication and
zero/successor clauses. This requires alpha-aware graph interface
translation, functionality and equality transport for graph
relations. For simultaneous numerator/denominator recurrences,
use a joint agreement invariant. These are still arithmetic
reconstruction prerequisites; they do not prove the DMR
inequality or its analytic equivalence.

RH-PL-07 floors remain 570269 unary / 69411 compact bytes.
There is no finite verified RH proof upper bound here.
The complete candidate-calculus audit, serialized RH equivalence,
ordinary-ZFC reconstruction, independent CI, and full original
replay of the new large recurrence theorem are outstanding.
No paid compute was used.
