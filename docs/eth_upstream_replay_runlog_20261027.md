# ETH upstream Lean replay: execution ledger, 2026-10-27

This log records independent attempts to check the pinned OpenAI formalization, not EvalMath's own Lean source. It does not claim ETH is refuted.

## Scope and pins

Source: OpenAI math commit **7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a**; upstream toolchain **Lean 4.34.1**; Mathlib lock **d13f23b723b8a846827a245b89c10fc7d3f11612**. Upstream Lake manifest declares **42** packages.

The official challenge is ComparatorChallenges/SubexponentialSAT.json and targets OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat, permitting only propext, Quot.sound, and Classical.choice.

## Attempt 1: tooling failure, resolved

[Run 40441014280](https://github.com/MoralityLabAI/EvalMath/actions/runs/40441014280) at commit 074bd7c **failed before any theorem was compiled or compared**.

The runner checked out the exact upstream SHA and successfully installed Lean 4.34.1 (Lean commit 5045d0056413266e57c625dcd7c365b10e377c52). A launcher call outside a project directory failed with "no default toolchain configured": the script installed Lean without selecting an elan default.

The machine-readable summary correctly recorded kernel_verified=false and comparator_verified=false. The [run artifact](https://github.com/MoralityLabAI/EvalMath/actions/runs/40441014280/artifacts/12706208524) retains all stage logs. No mathematical counterexample was observed.

Commit [8c9c488](https://github.com/MoralityLabAI/EvalMath/commit/8c9c488c54cb970b8a29ac0b05ed55bb528435d2) fixes the elan default, verifies the Mathlib SHA, and tightens kernel_verified to require the upstream theorem build, axiom inspection, and explicit axiom allowlist check.

## Attempt 2: verification in progress

[Run 40441313119](https://github.com/MoralityLabAI/EvalMath/actions/runs/40441313119) is the corrected attempt. Its independently pinned upstream replay was **in progress at the last inspection**, neither passed nor failed on its mathematical merits. It must produce separate outcomes for Comparator, the upstream theorem module and the final axiom check.

## Additional trust boundaries

The comparator and lean4export pins are d03acab154d269c06e60e4de7e4cc85deebff94b and 076e8e57707e813375e8f9da8bf989799ace9680, respectively. Their original toolchains target **Lean 4.34.0**, whereas OpenAI requires **4.34.1**. The harness uses the latter to compile these auxiliary tools without altering the upstream OpenAI project. Any auxiliary-tool compatibility failure is an **infrastructure/tooling result**.

Comparator also recommends a systemd-run user sandbox restriction in addition to landrun due to a known landrun weakness. This GitHub-hosted execution has not demonstrated an equivalent sandbox. Even a Comparator exit zero needs that trust caveat.

Only a completed upstream build, full axiom check and correctly scoped Comparator result can support a positive formal-verification verdict. An unavailable cache, incompatibility or pending workflow must never be treated as a mathematical error.

Related: [replay protocol](eth_upstream_replay_protocol.md) and [Mythos second-pass report](../paper/proof_fidelity_openai_eth.md).
