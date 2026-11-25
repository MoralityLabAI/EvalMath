-- Copyright 2026 Anthropic PBC
-- SPDX-License-Identifier: Apache-2.0
--
/-
Johnson/Goal/Skeleton/SoundOfVerifyAt.lean: `sound_of_verify_at`: soundness of `verify` with the
description's own parser (the goals' term `systemOfRecord (atSecondHashFunction theDescription) Z
(settingsOfRead pp)`) at one set of public files Z, in scope, read as pp, with exact match: WITH NO
FURTHER HYPOTHESIS. OVER THE PROOF FILE'S ENTRY TESTS' LIST OF FOURTEEN ROWS ALONE.

It is `sound_of_bare_laws_door_at` (Johnson/Goal/Skeleton/SoundOfBareLawsDoor.lean) with its one
hypothesis `kinds` proved by `kindsLaws_at_head` (Johnson/Goal/Skeleton/KindsLawsAtHead.lean, which
says field by field what proves what). `nearestSound_of_verify`: the same for all Z and pp, in the
nearby form `NearestSound` (Ladder/Package.lean). No cut of Johnson/Goal/Skeleton/KindsOfConds.lean
is spent.

Limits. CALLS ALONE: NOTHING IS PROVED IN THIS FILE. The one reading condition `owed` is not proved
from the other thirteen entry tests: `verify` itself asks its like, as the fourteenth, and
`owed_of_live` has it from that test's yes: so the theorem is of `verify` with that test. Beside the
kinds' lemmas the proof calls theorems that are no step's lemma, among them
`VerifierAndGoals.AtTheName.keySound_at_live_holds`, `FlashProve.entrySound`, `P5J.five_at_free2_laid2`,
`P5J.AtMgA.lastLeft_at_head_alone`, `Desc.K14.Law.k14_at_free_head`, `P5J.reply_leaves_at_mg`,
`P5J.three_at_free_head_alone`, `P5J.conds_of_laid`, `P5J.owed_of_live`,
`H2K12.lastTypedAt_of_live`, `P5J.headA_at_name`, `P5J.proofFileAt_at_all`,
`VerifierAndGoals.AtTheName.proofSound_record_of_rows`, `VerifierAndGoals.AtTheName.meaning`,
`VerifierAndGoals.AtTheName.carries`, `VerifierAndGoals.AtTheName.hext`, `VerifierAndGoals.AtTheName.errorAtBits`,
`VerifierAndGoals.theDescription_within`, `FlashProve.compilerSoundnessConditions_layoutsByPublicReading`, `VerifierAndGoals.Fit.soundForWith_system_of_toldO`,
`P5J.fin_at_term`, `P5J.pub_free_at_term`, `P5J.row0B_at_left`. What it is worth is what the called
theorems and the definitions in the statement are worth. The head under which the sixteen (fourteen
lemmas with content: the fields k14 and k15 are idle, these kinds having no place on the first
chain) are had is BUILT inside the top from the scope, the reading, the yes of `protocolDataWellFormed` and
`rowsRead`; where `protocolDataWellFormed` says no, `verify` rejects everything and the statement holds for that
reason. AT THE WRITTEN COPIES `protocolDataWellFormed` SAYS YES BY THEOREM (AtFullSide/Top/). AT THE RELEASE'S
FILES AS BYTES THAT, AND THE ACCEPT OF HONEST PROOFS THAT PROGRAMS MADE, ARE EVALUATED, NOT PROVED:
in one reference run of the step-by-step form (tied to `verify` by
`PV.Ride.verdictThe_is_theDescription`, Johnson/PVR/RideThe.lean; the run rode the file of which
that one is a port, and another, neither in this library: the tie from its print to the theorem is
by name and statement, not by bytes), over another text, on the parsed files, with synthetic
weights, at the real hash function. Soundness (index binding) alone: no opening-form binding, no
correctness of extraction, no completeness, nothing on hiding, nor anything else that names the
honest committer or prover. One set of public files at a time, fixed before the hash function is
drawn; the second hash is a fixed function; at the full size alone; the description's own parser.
Beneath five of the called theorems (the tenth and the twelfth kind's lemmas on the first chain, the
key file's, the one that gives the five rows, the shared chain's among them, and the one on the last
chain's rest) stand files on coding theory adapted from third-party Lean (lean/LIMITS.md, L15). A
yes of `protocolDataWellFormed` is no sign that `verify` accepts anything: the entry file's decision (`linkDecisionAtFiles`,
Johnson/Goal/Description/LinkDec.lean) has three rejecting branches of its own outside it
(`Desc.K15.linkDecisionAtParameterFile`, Johnson/Desc/Link/LinkWritten.lean); the limits of
Johnson/Goal/Description/Live.lean say the first half. That the Lean honest prover's proof is
accepted, in the random-oracle model, but for 2^-40, at public files in use and at well-formed
requests whose claimed output is the model's result: `completeAtWellFormedRequests`
(AtFullSide/Face/TheSixLines.lean), with the limits of AtFullSide/Face/FinalCompleteValue.lean. -/
import Johnson.Goal.Skeleton.SoundOfBareLawsDoor
import Johnson.Goal.Skeleton.KindsLawsAtHead

set_option autoImplicit false
set_option relaxedAutoImplicit false
set_option maxRecDepth 100000

attribute [-instance] Inst.Model.Scl.ref

noncomputable section

namespace VerifierAndGoals.AtTheName
open VerifierAndGoals FlashProve FlashProve
open P5J

/-- **SOUNDNESS AT ONE SET OF PUBLIC FILES, IN SCOPE, READ, WITH EXACT MATCH: NO FURTHER
HYPOTHESIS.** -/
theorem sound_of_verify_at (Z : VerifierAndGoals.PublicFiles) (pp : Inst.Model.ScalesAndPolicy)
    (scope : InScope Z = true) (read : readFiles Z = .ok pp)
    (exact : pp.pol = Inst.Model.AcceptancePolicy.exact) :
    VerifiableInference.Sound (systemOfRecord (atSecondHashFunction theDescription) Z (settingsOfRead pp))
      fun t => VerifierAndGoals.soundnessErrorInQueries t 1 :=
  sound_of_bare_laws_door_at Z pp scope read exact fun _ _ _ _ _ h => kindsLaws_at_head h

/-- The nearby form `NearestSound` (Ladder/Package.lean) of the description: the same for all Z and
pp. -/
theorem nearestSound_of_verify : NearestSound theDescription fun t => VerifierAndGoals.soundnessErrorInQueries t 1 :=
  fun Z pp scope read exact => sound_of_verify_at Z pp scope read exact

end VerifierAndGoals.AtTheName

#print axioms VerifierAndGoals.AtTheName.sound_of_verify_at
#print axioms VerifierAndGoals.AtTheName.nearestSound_of_verify
