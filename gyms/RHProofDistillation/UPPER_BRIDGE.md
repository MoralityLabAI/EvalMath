# Upper bridge: theta integrals, covolumes and the character-window theorem

Provenance: Lean community mirror at commit `f150e02623b1e2bbe1f1da8eab5ffee5e930a6a3`.
This note describes **direct source observations**; the complete compiled proof-term graph is still pending.

## The conjunction that finishes the character theorem

In `ThetaCorrespondence/ThetaPairLifts/ThirdPlaceSeries/EveryCharacterOfLiteratureOfVWin.lean`,
the declaration `UpperTheory.LiteratureTheorems.every_character_of_literature_of_vWin`
calls `UpperTheory.Lit.every_character_of_theta_integrals_local_matching`.
It supplies a covolume estimate from `SelfIntersectionVolumeEstimates.topCovolSlim2_use_alt_alt`,
theta-integral compatibility from `theta_integrals_agree_and_local_matching_of_literature`,
and a local Langlands hypothesis from `local_langlands_gl_recT_exists_of_literature`.
Additional published arithmetic and geometric input assumptions occur in the same expression.
That theorem takes `OpenLiteratureStatements` and `UpperTheory.Top.VWin` as premises.

## How VWin and Galois representations enter

`AutomorphicVarieties/ModularityArgument/ThresholdArguments/DenseThresholdCases/VwinOfRow.lean`
defines `UpperTheory.One.vwin_of_row`, applying `automorphic_window_of_inputs`
to an `OpenImageCondition.mk` built from a Galois row parameter
and the `BaseChangeIdentities.baseChangeN` input.

`Foundations/GaloisRepresentations/IntegralStructures/RowSrc.lean`
provides `galoisLocalGlobalStrong_recParameter` by applying
`galoisRepresentations_of_thetaLift` to `tLiftK`.

`CharacterBoxes/MainConclusion.lean` then calls
`every_character_of_literature_of_vWin` using the row parameter and `vwin_of_row`.
Thus a specific, source-observed junction combines theta matching,
local Langlands, a geometric covolume statement and an automorphic window.

## How this relates to the character-sum bound

The other source strand starts from `ChainTied` in
`Formalism/SharpRestriction/GlobalSchurBounds/TieGlobal.lean`,
which contains `TiePts`, `TieGlobal`, `TieLocal` and `TieArith` witnesses
along with size, cost and error-window bounds.
`level_gm_le_on_family_scales` transports these into the family-level
prime-sum inequality via `tiedCore_of_chainTied` and `core_gm`.

The entire path by which the arithmetic-geometric constructions supply
the `ChainTied` conditions needs a theorem-level proof-expression trace.
The upper-bridge audit identifies the named interfaces that such a trace
must inspect and records their upstream Git blob hashes.

CI stages this investigation in `rh-pinned-source.yml` using a sparse
source checkout. No upstream Lean proof artifacts are executed.

## An explicit duplicate premise in the literature interface

The pinned file defines `OpenLiteratureStatements : Prop` with exactly three fields: `caraianiLocalGlobalDual : UpperTheory.One.M.Row`, `localLanglandsExists : UpperTheory.Zero.LLC.RecTExists`, and `galoisRepOfPolarizedPairLit : UpperTheory.One.M.Row`. The two Galois-row fields share a proposition, so this interface is equivalent to the conjunction of one row witness with the local-Langlands existence witness. That structural equivalence is modeled by proxy task `RH-D-007`. The upstream code provides these witnesses through the Galois row and `recTExists`; this observation does not discharge any hidden arithmetic or geometric proof obligations.

Task `RH-D-008` models the existential-index projection performed by `tiedCore_of_chainTied`, with geometric assertions left as explicit parameters. Both are independent miniature Lean tasks, never the upstream proofs themselves.
