# RH-PL-08: checked proof assembly and the upper-bound program

Status: executed exact proof-composition controls, 2026-11-25.
RH-PL-07 lower bounds remain 570269 unary / 69411 compact bytes for the
frozen arithmetic target and candidate calculus. No upper bound on the
length of a proof of that target has yet been obtained. The new concrete
upper bounds below are for logical calibration and definition-interface
theorems, whose proofs are checked by the existing Hilbert checker.

## 1. Upstream proof and dependency anchors

Use the original Alpoge-Claude release of 2026-11-20 and independent
verification receipts, rather than inferring proof size from source lines.

- Source archive SHA256:
  9631b4f020199e580ba86178cb56c6e9b09f690c2369a80dc4334aa93f49c7fc
  (239275554 bytes compressed, 175187 Lean modules).
- Lean toolchain v4.33.1; Mathlib commit 0df444a360eaa60ab8c11dca51a86af692955474.
- RH root theorem: riemannHypothesis : RiemannHypothesis.
- Rubinstein's RH-only transitive closure: 1478198 declarations.
  The combined five-root independent nanoda run checked 1484729 declarations.
  Counts refer to different closures; do not substitute one for the other.
- Sutherland's exported five-root proof: 61570595788 bytes, SHA256
  5ea74b912147c5c93cc2b6d70cc727cf908df2f62ac6a20480a3fa02f6be244e.
  Independent checks accepted the proof; his 2026-11-24 05:25 UTC status
  still listed a separate full Comparator run in progress.
- The 2026-11-25 Zhuk blueprint indexes 240 live declarations and gives
  a mathematical route through the argument. This is a reconstruction
  index, not a dependency-closed proof.
- Rubinstein's 265-page working reconstruction (2026-11-22) identifies
  13 remaining mathematical hypotheses for its central inequality.
  It is useful for decomposition; it does not establish a ZFC proof.

Sources (retrieved public verification metadata, not locally downloaded
or replayed archive):
https://alpo.ge/remark.pdf
https://math.mit.edu/~drew/grh/
https://mrubinst.github.io/grh-lean-verification/
https://www.math.uwaterloo.ca/~mrubinst/alpoge_claude_grh/
https://nasqret.github.io/riemann-rev/
https://github.com/nasqret/riemann-rev
https://hexagonmath.org/pdf/2611.01031v1
https://leanprover-community.github.io/blog/posts/riemann-hypothesis/

The Lean axiom audit reports propext, Classical.choice, Quot.sound.
This does not eliminate Lean's type-universe strength. Standard
set-theoretic semantics for Lean use finitely many inaccessible
cardinals for individual judgments. See Carneiro, Lean4Lean:
Formalizing the metatheory of Lean (2024),
https://www.mathematics.uni-bonn.de/him/video-recordings/tp_2024_02_seminar_video/slides/24_07_2024-carneiro.pdf
A generic conversion to ordinary ZFC cannot be inferred from an
arithmetical conclusion: e.g. a stronger theory can prove Con(ZFC)
when ZFC itself cannot, under the usual consistency hypotheses.
An actual universe-elimination or ordinary-ZFC reconstruction is needed.

## 2. Checked deduction theorem

The target in rh_target.txt (git blob
a55f16f293a784ca91d9d52d65cbaea1e89f80dc) is

  F = forall v0 ... v8. (D -> C).

D is the conjunction of the 22 top-level defining clauses;
C is the expanded integer RH assertion. All variables are explicit.
The local derivation contract is to produce C from assumption D,
using the existing logical and nonlogical axiom grammar, earlier
checked theorems, MP and legal generalization. Generalization under
a hypothesis may bind only a variable not free in that hypothesis.

assembler.mjs implements a standard Hilbert deduction theorem:

- H itself: derive H->H via five K/S lines.
- Axiom B (or previously checked theorem B): lift using K and MP.
- MP from A and A->B: use S to combine H->A and H->(A->B).
- Generalization of B: generalize H->B, apply the existing
  forall-distribution axiom with its free-variable side condition.

Every generated line is checked in an incremental proof book.
The emitted proof of H->C is verified by the original kernel, using
universal closure for an open conclusion. Imported theorems in a local
proof are permitted only as explicit interfaces: actual proofs for them
must be included in the final checked DAG. The output of discharge
with imports is a conditional assembly artifact, not by itself a theorem
certificate.

For additive ASCII line cost, write h=s(H), b=s(B), a=s(A), excluding LF.
Before deduplication, the generated blocks have these exact costs:

  H->H identity (5 lines): 23(h+1)
  axiom B lift including B (3 lines): 2h+4b+6
  lift of MP with antecedent A (3 new lines): 6h+3a+4b+13
  lift of generalization, B the quantified conclusion (3 new lines):
    4h+4b+8
  pre-lift imported theorem B (2 new lines): 2h+3b+5,
    in addition to its independently verified proof.

The sum bounds the emitted length from above; repeated lines can be
removed by the assembler. For the entire proof, charge each imported
theorem's proof once, including any shared prerequisites. This is an
explicit costed proof transformation, not a multiplier applied to
the Lean source size.

## 3. Dependency assembly

A chunk has an ID, declared direct dependency IDs, a formula AST
as its exact conclusion and a list of proof lines. Topologically
visit the reachable chunks. Verify each local list against only its
declared imported conclusions and earlier local lines. Verify and
deduplicate its lines in the global theorem book. Reject duplicate
chunk IDs, missing dependencies, dependency cycles, mismatched
conclusions and unjustified lines. Stop the emitted global proof at
the first occurrence of the root; verify that proof with the original
kernel (plus universal closure for an open root). The exact global
line cost is an upper bound on the shortest proof of its closed
root; for an open root, charge its universal closure if that is
the desired target.

This is the interface for incremental ZFC reconstruction. Lean
declaration types or proof hashes alone cannot satisfy it. A Lean
declaration selected for reconstruction must be accompanied by a
translated set-theoretic formula and explicit verified derivation.

A small shared-prefix DAG control: 12 raw local lines, 141 unary /
92 compact bytes; deduplicated global proof 7 lines, 108 unary /
70 compact bytes. This is a synthetic bookkeeping control, not
the compression ratio of the RH proof.

## 4. Exact costs for the frozen target wrapper

| Component | Unary bytes | Compact bytes |
|---|---:|---:|
| D (excluding LF) |61099|8993|
| C (excluding LF) |52868|4858|
| D -> C (excluding LF) |113968|13852|
| Nine direct generalization lines (including LF) |1026096|124767|

If an unconditional proof pi of the exact open implication D->C
is obtained, append nine generalizations in reverse binder order.
Then the original checker verifies F and

  L_unary(F) <= cost_unary(pi) + 1026096,
  L_compact(F) <= cost_compact(pi) + 124767.

These overheads are exact for this direct append procedure, before
any reuse of already-present generalizations. They are not necessary
costs for all proofs. If a local proof of C under D is obtained,
apply the checked deduction theorem first and charge its actual
output. All costs are for the frozen fully expanded grammar.

Full-size controls:
- A proof of the tautological forall v0...v8.(D->D), using the exact D:
  14 lines, 2505475 unary / 368844 compact bytes.
- A proof of F->F with the exact frozen F:
  5 lines, 2622736 unary / 319033 compact bytes.
Neither control proves F itself.

184 parametric assumption/MP/generalization derivations were generated
and checked by the original kernel (66871 unary proof bytes in total).
Nine rejection cases cover illegal generalization, unjustified lines,
undeclared dependencies, cycles, wrong conclusion, duplicate IDs and
attempting to wrap an unproved RH body. All passed.

## 5. Checked definition interfaces

interfaces.mjs constructs propositional Hilbert templates for explosion,
double-negation elimination/introduction, and both projections of the
expanded conjunction A(P,Q)=not(P->not Q). It uses only K, S, the
classical axiom and the checked deduction theorem; no new axiom schema
is admitted. Each template is instantiated by substituting arbitrary
formula ASTs for its two atomic placeholders. Since the templates
are propositional, the substitution preserves K/S/classical instances
and MP. The original kernel rechecks every instantiated proof.

The left/right projection templates have 50/42 proof lines,
3541/3238 unary bytes for the small schematic calibration. All
72 substitution tests on small formulas, including quantified formulas,
pass.

For a right-associated definition conjunction, chaining projections
uses K/S to compose implications. The compiler splits D into exactly
22 top-level clauses and verifies that recombining them reproduces D
byte for byte. An initial receipt incorrectly counted 21 by retaining
the conjunction of the last two recurrence clauses as a single clause;
the source and receipt were corrected to 22. The two interface proofs
below were unaffected.

Two actual closed interface theorems were constructed, explicitly
generalized over all nine variables, and verified in the original
checker:

| Root (schematic notation, exact AST used) | Lines | Unary bytes | Compact bytes |
|---|---:|---:|---:|
| forall v0...v8. D -> Omega_is_least_inductive |59|11655148|1718205|
| forall v0...v8. D -> zero_in_Omega |106|24702350|3628419|

These are concrete proof-length upper bounds on the stated
definition-interface theorems only. Their cost is high because the
templates copy large subformulas repeatedly. They demonstrate that
reconstruction can produce verifiable first-order proof bytes and
that formula-level compression deserves attention. They do not establish
any numerical upper bound on L(F).

## 6. Reconstruction gates

A. Source closure audit: acquire the pinned RH-only export/closure,
   validate source/export hashes and root statement, traverse all
   type/value references, including recursors, inductives and relevant
   universe instantiations. Count by dependency class. Do not mistake
   max universe level or a successful axiom audit for a conservativity
   proof. The full 61.57 GB export was not downloaded or processed
   in this pass.

B. Choose a proof path through the blueprint and specialize the
   mathematical statements to zeta/RH where possible. Reconstruct
   each interface in ordinary ZFC using only explicitly charged
   definitions and prior theorems. For each translated chunk record
   exact Lean origin and source hash, formula bytes, direct imports,
   proof bytes, verification status, and any foundational obligation.
   Only count the union of verified reachable chunks for a completed
   root. The 240-entry blueprint is a reading index, not an axiom list.

C. Establish the exact analytic RH to DMR bridge (including existence
   and uniqueness of arithmetic operations in the frozen set encoding
   and the published analytic equivalence), with explicit checked
   implication proofs. The target's informal equivalence argument is
   not yet a proof artifact in the chosen calculus.

D. Complete and independently audit the candidate first-order calculus
   (including schema-variable renaming, substitution, equality logic
   and equivalence to a standard ZFC presentation). Verify the full
   assembled proof of the exact frozen F. Until then keep U_RH unknown
   and do not report a finite numerical proof-length upper bound or
   a certified optimality gap.

## 7. Reproduction and limits

  node research/rh_pl01/assembler.mjs
  node research/rh_pl01/interfaces.mjs

The tests actually ran in the JS sandbox using the fetched pinned
kernel, spine code and frozen target. The corrected clause census was
separately reconstructed and checked against the fetched target.
No Node/CI run, Lean kernel formalization, upstream proof replay,
standard-ZFC translation or paid compute is claimed. The modular
assembler is still a research prototype; independent review is needed.
