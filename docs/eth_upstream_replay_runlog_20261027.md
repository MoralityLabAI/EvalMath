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

## Attempt 2: failed tooling probe and timed-out build, inconclusive

[Run 40441313119](https://github.com/MoralityLabAI/EvalMath/actions/runs/40441313119) completed with workflow conclusion **failure**. Pinned upstream checkout, Lean 4.34.1 installation, Mathlib cache (8,908 files), and Comparator binary compilation (16 jobs) passed. Landrun itself installed, but the subsequent `landrun --help | head -n 10` probe exited **141 (SIGPIPE)** under `pipefail`; the Comparator did not execute. The upstream target build reached 9,824 / 12,014 jobs when its 1,800-second stage timeout fired (**exit 124**). Therefore `axioms_check` was blocked. The receipts recorded `kernel_verified=false` and `comparator_verified=false`. See [artifact 12708020001](https://github.com/MoralityLabAI/EvalMath/actions/runs/40441313119/artifacts/12708020001). This is a tooling/runtime failure, **not** evidence of a substantive mathematical proof error.

## Attempt 3: repaired replay awaiting CI verdict

The follow-up patch avoids the SIGPIPE probe, adds a syntax preflight, gives both Comparator and the upstream target build 90-minute stage budgets within a 210-minute job, checks the axiom allowlist for **both** theorem endpoints, and returns a failing workflow conclusion if Comparator never passed. Upstream OpenAI and verification-tool source pins remain unchanged. An independent proof-verification claim requires successful measured stages with the recorded sandbox limitations.

## Additional trust boundaries

The comparator and lean4export pins are d03acab154d269c06e60e4de7e4cc85deebff94b and 076e8e57707e813375e8f9da8bf989799ace9680, respectively. Their original toolchains target **Lean 4.34.0**, whereas OpenAI requires **4.34.1**. The harness uses the latter to compile these auxiliary tools without altering the upstream OpenAI project. Any auxiliary-tool compatibility failure is an **infrastructure/tooling result**.

Comparator also recommends a systemd-run user sandbox restriction in addition to landrun due to a known landrun weakness. This GitHub-hosted execution has not demonstrated an equivalent sandbox. Even a Comparator exit zero needs that trust caveat.

Only a completed upstream build, full axiom check and correctly scoped Comparator result can support a positive formal-verification verdict. An unavailable cache, incompatibility or pending workflow must never be treated as a mathematical error.

Related: [replay protocol](eth_upstream_replay_protocol.md) and [Mythos second-pass report](eth_second_pass_20261027/REFEREE_REPORT_second_pass_20261027.md).
