# Independent Lean replay protocol: OpenAI ETH preprint

**Scope:** reproducible verification attempt, not a claim that ETH is disproved. This workstream is separate from EvalMath's theorem *fidelity* audit at PR #10. The original source files and theorem statements are not modified. No success should be inferred from a successful script upload or a successful EvalMath Lean build.

## Reproducible inputs

- OpenAI repository: `openai/math` at **`7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a`** (October 26, 2026 merge).
- Upstream Lean toolchain: **Lean 4.34.1**, from `lean/lean-toolchain`; source-provided dependency lock: upstream `lean/lake-manifest.json` and `lean/lakefile.lean` (Mathlib pin `d13f23b723b8a846827a245b89c10fc7d3f11612`).
- Official comparison target: `lean/ComparatorChallenges/SubexponentialSAT.json`, theorem `OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat`, permitted axioms `propext`, `Quot.sound`, `Classical.choice`.
- Comparator source (experimental executable): `leanprover/comparator@d03acab154d269c06e60e4de7e4cc85deebff94b`.
- Lean export tool: `leanprover/lean4export@076e8e57707e813375e8f9da8bf989799ace9680`, built against the upstream's 4.34.1 toolchain.
- Landrun: `zouuup/landrun@5ed4a3db3a4ad930d577215c6b9abaa19df7f99f`.

The comparator tool versions follow publicly documented pins in `leanprover/lean-eval`, and are **not upstream OpenAI pins**. Compatibility with the precise pinned upstream toolchain must be demonstrated, not presumed. The elan installer is fetched from the official repository and its SHA-256 is logged; it is not pinned to a fixed commit in this exploratory workflow. The runner environment and GitHub-hosted binaries remain in the trusted-computing-base.

## Steps and separately audited results

1. `git checkout --detach` the pinned **OpenAI** commit. Reject any wrong HEAD or `lean-toolchain` value.
2. Install upstream toolchain and fetch Mathlib cache with the *pinned* Lake project, without running `lake update`.
3. Attempt official Comparator **before** independently compiling the solution's module. Its trusted comparator statement is self-contained. `landrun` is attempted, but the broader comparator sandbox assumptions (including the user `systemd-run` isolation recommended by its developers) must be assessed separately. Even a comparator exit 0 is therefore scoped to the recorded execution environment.
4. Compile `OAI.Algorithms.SubexponentialSAT.Main` with Lake. If the build passes, import the compiled theorem in an extra local source file and run `#check` and `#print axioms` on `exact_count_and_sat` and `exact_count_eth`.
5. Parse the printed axioms for **both endpoints**, failing if either report is absent or includes anything outside `{propext, Quot.sound, Classical.choice}`.

Scripts live at `scripts/replay_openai_eth_upstream.sh`. The job uploads raw per-stage logs, a status ledger, and `summary.json` **even if stages fail**. `summary.json`'s `kernel_verified` and `comparator_verified` booleans are only true when the corresponding measured stages pass; otherwise use the failure codes and logs.

## Evidence interpretation

- **Source checkout passed:** source SHA and toolchain pin confirmed, not a proof.
- **Upstream target build passed + axiom check passed:** independently compiled theorem in the recorded Lean environment with recorded axioms, but statement correctness relative to the intended mathematics remains a separate review.
- **Official comparator passed:** same statement and axiom allowlist accepted under the recorded comparator setup (subject to its sandbox and toolchain trust conditions).
- **Cache, tool install, build or comparator failure:** classify as infrastructure/compatibility or mathematical error only after examining the exact log. Failed setup is **not** a counterexample.

GitHub CI job time budget is 210 minutes. Comparator and upstream-target build each have a 90-minute timeout; the other stages have separate limits. A nonzero Comparator conclusion yields a failing workflow even when kernel and axiom stages separately pass. The first failure is recorded. The target exists in a very large Lean/Lake repository with numerous third-party dependencies. This workflow intentionally does *not* change those dependencies to make a result easier to obtain, and may be resource constrained.

Source: https://github.com/openai/math/tree/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/lean
Comparator: https://github.com/leanprover/comparator
