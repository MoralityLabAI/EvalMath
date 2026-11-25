# Hypergames (HG-01): GPTStoryworld × EvalMath

**Status, 2026-11-16:** exact rational finite mathematics and synthetic mechanism tests. The source map was inspected at GPTStoryworld commit `c8d46591f983473023daf0232e9b413baaa02194`; this folder is an independently runnable EvalMath reference implementation. No trained model, live storyworld replay, or actual agent goal has been identified.

## Research question

Can we infer an agent's implied goal states from its decisions in a large storyworld while accounting for the fact that every character has a different *subjective game*? The observable answer is a set of candidate goals or a continuous inverse-Voronoi region, conditioned on the declared legal actions, subjective one-step transition oracle, observation boundary, and metric.

**Hypergame:** an agent models the world as `G_i = (S_i, O_i, A_i, T_i, U_i)` and may model another agent's game as `G_i^j`. In a Sweepweave setting, `p(observer,target,trait)` and `p2(observer,mediator,target,trait)` are direct carriers of first- and second-order beliefs. Actual and perceived BNumbers are distinct. These are different from a multi-agent game in which all agents know one common transition kernel.

## Upstream audit crosswalk

| GPTStoryworld path | Existing observable or implementation | HG-01 link |
|---|---|---|
| `storyworld/env/diplomacy_env.py` | Trust matrix, coalitions, messages, four outcome labels, deterministic transition and turn-limit logic | Agent-subjective vs audited objective successor maps |
| `storyworld/benchmarking/turn_trace_export.py` | `visible_state`, `legal_actions`, `chosen_action`, post-turn `hidden_state_reveal` and `belief_delta` | Pre-decision-only numeric adapter, never learn from future fields |
| `storyworld/examples/diplomacy_min.json` | Three agents, coalition, betrayal, message commitments and sealed `secret_payoff` | Source-derived synthetic visible-state fixture (16 allowed axes) |
| `verifiers_envs/storyworld-env/manifold_projection.py` | pValue/p2Value keyrings hashed into 8+8 bins by default, plus five macro variables | Optional explicit observer-owned p/p2 keyring adapter; compare collisions before trusting compressed distances |
| `verifiers_envs/storyworld-env/__init__.py` | Effects termed “Dirac operators”; secret metric gate is tested structurally by `Absolute Value` + at least two variables; local-max anchors estimated by finite differences | Exact Clifford algebra; metric distances and inverse-goal regions require independent tests |
| `verifiers_envs/storyworld-symbolic-env/README.md` | MeTTa-based environment kernel, partial visibility, rule execution and separate grading overlay | Prospective hidden-state transition/oracle exporter; no simulated counterfactuals yet |
| `storyworld_format_guide.md` | Character BNumbers in [-1,1], separate actual/perceived axes, Nudge effects, choice/reaction gates | Register numeric domains, weights, visibility and state-update semantics |
| `storyworlds/evals/README.md` | 104-variable long-horizon benchmark and approximately 140-variable simultaneous-constraint scenario described | High-dimensional prototype; genuine inference needs legal counterfactual successor states |
| `benchmarks/storyworld_reasoning_v2_turn_traces/BENCHMARK_SPEC.md` | Route-independent capability-state and secret-gate readiness metrics | Goal identification scored independently from path-prefix matching |

The approximately 140-variable world is **described in an upstream README**; the pinned `storyworlds/evals/` directory does not expose that specific world as an audited, runnable fixture. HG-01 uses its own registered synthetic 140-coordinate example.

The GPTStoryworld root `AGENTS.md` identifies active code under `storyworld/` and `verifiers_envs/`, warns about vendorized mirrors, and notes that the root README is only partly current. The HG-01 adapter is intentionally one-way and does not alter that repo.

## Where the implementation lives

- `src/spiral_ln/evaluation_hypergames.py`: implicit Clifford squared distance; factorized normalized categorical Hilbert kernel; inverse-goal consistent set; exact inverse-Voronoi inequalities; rank/blind-space certificate; robust optimal-probe set cover; subjective/objective regret; compactification margin; visible-state and nested-belief adapters.
- `tests/test_evaluation_hypergames.py`: independent two-gamma matrix multiplication, explicit small tensor contractions, high-dimensional synthetic cases and adversarial visibility tests.
- `scripts/verify_evaluation_hypergames.py`: deterministic receipt generator with source hashes.
- `output/evaluation_hypergames/hg01.json`: exact receipt, checked by EvalMath's `scripts/check_receipts.py`.
- `paper/hypergames_dirac_goal_inference.md`: proofs, limitations, cross-repository research design.
- `Hypergames/PROTOCOL.md`: future data-collection protocol and held-out evaluation.
- `Hypergames/fixtures/`: pinned synthetic geometry fixture and a visible-state example reconstructed from GPTStoryworld's sample diplomacy world.

## Run without GPU, network or model weights

```sh
PYTHONPATH=src python -m unittest discover -s tests -p 'test_evaluation_hypergames.py' -v
PYTHONPATH=src python scripts/verify_evaluation_hypergames.py --output /tmp/hg01.json
python scripts/check_receipts.py --only hypergames
```

The verifier's `--output` option creates a new file and requires a path that does not yet exist. Use `python scripts/verify_evaluation_hypergames.py` to print the JSON instead. Results are exact Fractions rendered as strings, with a time stamp omitted by the receipt comparison.

## Key limitations

`infer_goals` identifies only among a declared finite candidate set. The halfspace certificate exposes continuous directions that remain unidentified. An observed storyworld trace lacks counterfactual next states for the unchosen legal actions; supplying these states without a pinned simulator, intervention, or replay oracle would be leakage or fabrication. `hidden_state_reveal`, realized outcome, and future belief deltas are grading-only fields. The Clifford geometry is a mathematically defined representation of classical narrative states; no claim of quantum dynamics or physically instantiated spinors is involved.

## HG-02: single-player reasoning and alignment

The [single-player high-dimensional gym](single_player/README.md) adds sealed-state
parity, verification and authorization tasks, exact Bellman controls, proxy
failure cases and a reproducible source-hashed receipt. See
[`paper/hypergames_single_player_reasoning_alignment.md`](../paper/hypergames_single_player_reasoning_alignment.md).

## HG-03: frozen Qwen3.5-0.8B trial

The [registered local Qwen single-player study](single_player/QWEN_PROTOCOL.md) adds
an isolated 140-dimensional core, a 512-dimensional padding control and a native
512-dimensional wide-predicate test. It freezes the model checksum and private-seed
commitment before evaluation. The source-hashed fast preflight contains **no model runs**.
