# RH-PL-09: exact formula-DAG proof compression

Status: executed synthetic and frozen-target interface controls,
2026-11-25. No new lower bound or finite upper bound for RH itself.
The frozen arithmetic target and the inference calculus are unchanged.
All byte counts include the LF at the end of each proof line.

## 1. Goal and baseline

RH-PL-08 produced explicit Hilbert proofs of two closed definition
interfaces of F = forall v0 ... v8. (D -> C), with D the 22-clause
arithmetic definition conjunction. The costs were 11,655,148 and
24,702,350 unary bytes. This pass asks how much the implementation
can save by slicing proofs, choosing different propositional
templates, and sharing the proof of each successive right suffix.

The independent baseline for the 22-interface comparison uses
RH-PL-08's original templates, with exact dependency slicing and
deduplication within each individual proof. This is a stronger
baseline than naively concatenating all original unsliced templates.

## 2. Exact structural arena

compression.mjs interns formula ASTs by constructor and ordered
child IDs; atomic indices and quantifier indices remain literal.
Two IDs are equal iff their complete formula trees are syntactically
equal. This follows inductively from constructor injectivity and
the interning map. In particular alpha renaming and logically
equivalent formula rewrites do not get free sharing.

For every node compute exact unary and compact encoded lengths.
Each atom's cost is the tag plus two encoded variable indices,
negation adds one tag, implication adds one tag and both child
lengths, and quantification adds one tag, its variable encoding
and its body length. Recursively shared children still contribute
their full lengths at every occurrence. Each emitted proof line
adds LF. Numeric accounting uses safe JS integer arithmetic at
the observed sizes; it is not an arbitrary-precision cost engine.

The structural proof book checks a subset of RH-PL-02:
K, S, classical contraposition, MP, and unrestricted universal
generalization of earlier theorems. Axiom recognition compares
exact child IDs for the corresponding schema patterns. For MP,
both antecedent and implication must already occur; generalization
requires the earlier body. No hypotheses or imported unproved
theorems are admitted by this book. Therefore each accepted
sequence expands to a valid proof in the original calculus.
The arena changes internal representation only. It introduces
no uncharged definition, axiom, or compressed proof rule.

Store a justified predecessor list for each line. Backward mark
all predecessors reachable from the selected roots, retain marked
lines in original order, and replay. Every retained inference has
all required predecessors earlier, so this is a sound proof slice.
It need not be a globally minimum slice: the book picks the first
available modus ponens justification. Repeated lines are emitted
once, and all reachable proof roots are present in the collection.

## 3. Projection template experiment

Compare three variants, each checked in the original checker on
atomic schematic inputs. They use the same classical Hilbert
axioms: baseline RH-PL-08 deduction, composition-based lifting,
and direct composition/contraction.

| Projection | Template | Raw lines | Raw unary bytes | Sliced lines | Sliced unary bytes | Sliced compact bytes |
|---|---|---:|---:|---:|---:|---:|
| Left | Baseline |50|3541|37|2812|1854|
| Left | Composed |48|3461|37|2812|1854|
| Left | Direct |37|2812|37|2812|1854|
| Right | Baseline |42|3238|31|2539|1663|
| Right | Composed |35|2941|31|2539|1663|
| Right | Direct |31|2539|31|2539|1663|

The alternate construction initially failed to improve the full
sliced proof. Retain this as a null result. After slicing, the
three variants have identical costs, and selection by either
encoding yields the same aggregate cost on the frozen 22-clause
target. The measured gain comes from pruning and shared proof
prefixes, not from discovering a more economical retained
propositional template.

## 4. Shared suffix compiler

Write D=T_0, T_j=(P_j and T_(j+1)), with the last suffix
T_21=P_21. For each j<21 construct T_j->P_j and, when needed,
T_j->T_(j+1). Compose the latter with the existing D->T_j
using K/S transitivity. Store D->T_(j+1) once. Compose the
left projection similarly to obtain D->P_j. Each interface
can remain an open theorem during assembly or be closed over
the nine original outer variables. The last interface uses
the final suffix theorem itself.

For fixed proof blocks before deduplication, let R_j be the
right-suffix derivation and composition cost, and L_j the left
projection, composition and (optional) closure cost of interface
j, with the final L block only closing its suffix. With m
clauses, independent assembly charges sum L_j plus
sum_{j=0}^{m-2}(m-1-j)R_j; shared assembly charges sum L_j
plus sum R_j. Exact syntax deduplication can save further
bytes across these blocks. This explains why a long sequence
of shared right-suffix implications is expensive to reconstruct
independently. The formula applies to the stated assembly
algorithm, not to shortest proofs in the calculus.

## 5. Frozen payload results

The original target blob is a55f16f293a784ca91d9d52d65cbaea1e89f80dc.
The actual AST, including all 22 definition clauses, is decoded
from the fetched file. No synthetic substitute is used in this
comparison. All three selection modes reproduce the same costs.

| Checked interface collection | Lines | Unary bytes | Compact bytes |
|---|---:|---:|---:|
| Sum of 22 independently sliced closed proofs |9286|2068930810|303127357|
| One shared closed library, 22 roots |1343|197136008|28824678|
| One shared open library, 22 roots |1145|184480436|26961318|

Relative to the independent sliced baseline, the shared closed
library saves 1,871,794,802 unary bytes (90.47%) and
274,302,679 compact bytes (90.49%). Shared open interfaces
save a further 198 closure lines: 12,655,572 unary bytes
or 1,863,360 compact bytes. Open interfaces are valid theorems
with free variables under the assumption-free Hilbert rules,
not assumptions. A closed desired root must still be closed.
These numbers are the cost of a proof library containing the
specified conclusions, not the cost of a proof of RH.

Two closed actual interface proofs replayed in the original
checker, with exact expansion cost cross-checked:

| Interface | RH-PL-08 unary | Sliced unary | Sliced compact | Sliced lines |
|---|---:|---:|---:|---:|
| D implies least-inductive Omega |11655148|9920076|1461538|46|
| D implies zero belongs to Omega |24702350|19794021|2907791|82|

The three selection modes each replay these same two payloads,
so six successful replay calls represent two distinct roots,
not six independent mathematical theorems. All 22 individual
and shared proof sequences were checked and rechecked by the
exact structural subset verifier. The entire expanded shared
library was not materialized for replay in the original
string-based checker.

## 6. Independent recognizer and cost audit

compression_audit.mjs reuses the actual frozen target and
compares structural axiom recognition with the original
checker's recognition on every unary formula through 18 bytes:
38,232 formulas, including 16 propositional axiom instances.
For each formula both serialized lengths agree exactly.

The audit also checks 1,280 generated schema and perturbed
schema formulas (648 recognized, 632 rejected), including
quantifiers, negations, and extended compact variable indices
36 and 1296. Exact structural recognition and both byte
counts agree with the original checker on the entire panel.

A further actual depth-five interface (clause index 4,
zero-based) was materialized and replayed through the original
compact verifier. Its proof has 190 lines, 50,766,576 unary
bytes, 7,444,799 compact bytes. The compact serialization's
actual length agrees with structural accounting.

Additional controls in compression.mjs: six schematic template
checks; 126 propositional axiom cross-checks; negative missing
premise rejected. The structural representation had 3,120
distinct nodes during the main run. All computations executed
in the JS sandbox; independent Node/CI runs remain outstanding.
The mathematical justification of the restricted checker is the
syntactic correspondence above; finite tests are supporting controls.

## 7. Reproduction

  node research/rh_pl01/compression.mjs
  node research/rh_pl01/compression_audit.mjs
  node research/rh_pl01/compression.mjs --emit 0 > clause0.proof
  node research/rh_pl01/compression.mjs --emit 4 --compact > clause4.compact.proof

The emit mode expands a selected closed interface, line by line,
in the requested original encoding. The full set is represented
by a checked ordered library rather than an emitted single file.
No change to rh_target.txt, kernel.mjs or the target encoding.

## 8. Next gate

The costly logical wrapper is now better understood. Next
prioritize a genuine mathematical bridge theorem used by the
RH reconstruction: derive induction over the least inductive
set from a charged separation instance, then derive uniqueness
of the harmonic recurrences, or build an independently checked
translation of the DMR arithmetic equivalence. The current
nonstandard countermodels demonstrate precisely why an
induction theorem is needed. Quantified separation and
generalization under hypotheses must be checked, and a local
proof must include all prior verified dependencies.

The current RH lower floors remain 570269 unary / 69411 compact.
No finite RH upper bound or optimality gap is known in this
calculus. The calculus equivalence audit, serialized analytic
RH bridge, ordinary-ZFC reconstruction and independent CI
remain open. No paid compute used.
