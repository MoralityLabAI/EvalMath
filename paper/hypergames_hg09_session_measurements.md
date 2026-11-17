# HG-09 signed-in frontier measurements and public observation certificates

**Evidence status:** power-limited public observational model measurements, plus an algebraic sufficient-certificate implication. No claim about private reasoning, learned internal mechanisms, population model rankings, or safety equivalence. Counts and paired results are generated in `output/evaluation_hg09/session_20261117.json` from `Hypergames/hg09/session_20261117/measured_input.json`.

The measured inputs come from GPTStoryworld HG-09 PR #16. The original PR head is `522de307fb60043d71c9a90fd0e802227e855dae`; its HG-08 dependency is `855f2f3d5fc4e26518112925de4a53e6dc9bc42e`. The signed-in runner was frozen in GPTStoryworld commit `c07227c` before scored inference. The 12-episode smoke checkpoint is commit `415c0fd`. The source audit verifies the original source and registration bytes against the PR head. The protected HG-03 manifest was never opened; its original public commitment remains unchanged. Numeric disjointness from an unavailable private list cannot be independently established.

`gpt-6.1-sol` and `gpt-6-astra` were explicitly requested and accepted by signed-in Codex CLI 0.167.0-alpha.3.2. Their immutable backend snapshots were not exposed. Claude Sonnet 5.5, Claude Opus 5.5, and Gemini 3.1 Pro had no invocable session facility or provider credentials. No paid API requests were made. Each decision used a fresh CLI process with the chosen public history, no model-side tools, the same requested `low` reasoning effort, and either direct or deliberative wording. The direct condition can still use internal reasoning. The CLI did not expose an output-token cap, temperature, or its complete built-in scaffold. Exact task prompts, supplied model instructions, CLI events and commands, usage and latency are preserved in hash-chained JSONL files in GPTStoryworld.

## Independent units and evidence gate

The independent unit is a public generator seed. Hidden modes, dimensions, ranks, prompt arms, intervention turns and the 256 parity test vectors are repeated observations within that seed. Only case blocks completed under all four model/condition arms enter balanced comparisons. All attempted and interrupted episodes remain in the available-data accounting. A failed provider call is never converted into a model abstention or an oracle-generated score.

The prospective resolution planner used 64 independent development-generator summaries comparing deterministic adaptive hashing with random singletons. A repeated deterministic controller was the sham. This calibrates a synthetic replay floor, **not model-level sham variation**. At a scientific floor of five completion percentage points, a target of fifteen points and 40 planned comparisons, the planner returned `REDESIGN_OR_PILOT_ONLY`: the readout is public and unsealed, and 24 planned roots are underpowered. Its approximate 401-root estimate describes the synthetic development comparison and cannot be transferred to model differences.

FSI-01 supplies seed-cluster signed inference, descriptive percentile cluster intervals, exact rational grades, conditional Clopper–Pearson bounds for the root-level event "any unsafe release", and Holm correction across the complete 40-comparison family. Tiny-root bootstrap intervals can be degenerate and are never evidence of equivalence. Conservative bounded-root planning requires 738 roots for a single 95% accuracy interval with a five-point half-width; 1,476 for 40 simultaneous such intervals; or 5,903 for simultaneous five-point half-width paired differences in [-1,1]. These bounds assume independent representative generator roots and are planning guarantees, not empirical power estimates.

## A sufficient certificate from public parity queries

**Evidence class: algebraic implication, with finite enumerated regression checks.** For one output, the unknown support vector p is binary with known exact Hamming weight w. Each observed intervention asserts a·p=y over GF(2). Known weight also implies 1·p=w mod 2. Consider the row space of these augmented equations, carrying the same linear combinations of their observed responses.

If a unit vector e_i occurs in that row space with implied response 1, every compatible p has p_i=1. If w distinct coordinates are forced positive, exact weight w leaves no other positive coordinates. The full support is therefore uniquely fixed, and the parity of every future input x is fixed. For multiple outputs, apply the same row reduction to their response vector and require w forced positives for each output. The claimed release must also have weight w and agree with all observed deltas.

This criterion is sufficient, rather than necessary. It can certify a positive singleton inferred from a group and its complement, even when the agent never queried that singleton directly. The implementation never reads the private goal. Tests enumerate all ten two-sparse goals in dimension five and all 1,024 pairs of group queries, checking every accepted certificate against exhaustive compatible supports. Separate tests cover inferred singletons without direct probes, multiple outputs, malformed equations and inconsistent responses. No Lean formalization is claimed.

The certificate is a post hoc mathematical audit of observable information. A certified transcript is decision-sufficient for this synthetic parity family. It does not identify the model's internal representation or show that the model implemented Gaussian elimination. Exact specialized solvers and adaptive hashing remain structural controls, separate from frontier-model measurements.

## Instrument limits and failure interpretation

HG-02 observations disclose rewards, checksum formulas, gates, current remaining actions and legal menus, but do not explicitly describe all action-transition semantics or audit revelation. Bellman regret is a comparison to the simulator-informed exact policy. Horizon behavior should therefore be interpreted under the supplied interface. The 512-dimensional variant also doubles the parity/checksum widths; it is not a pure nuisance-padding contrast.

The recorded taxonomy distinguishes incorrect route parity, verification and authorization arithmetic, route choices without an audit, audits at horizon four, unsafe publish actions, proxy actions, invalid formats, incorrect causal support releases and queries attempted after budget exhaustion. These are behavioral labels. HG-08's inherited `false_accept` field counts incorrect test-vector predictions after a support release; the report separately counts incorrect support-release episodes and false support discoveries to avoid treating those test vectors as independent trials.

Reproduce without model inference:

```text
PYTHONPATH=src python scripts/verify_hg09_session.py
PYTHONPATH=src pytest -q tests/test_evaluation_hg09_session.py tests/test_hypergames_observation_certificate.py tests/test_evaluation_finite_sample.py
python scripts/check_receipts.py --only hg09_session finite_sample
```

The source-hashed receipt includes the measured input file and mathematical/statistical implementations. GPTStoryworld additionally replays every original prompt, parser decision, environment transition and grade from the actual saved model responses, and records each raw JSONL digest. A fresh future confirmation needs an untouched root population, a complete visible dynamics contract, model-level matched shams, sufficient roots and an independently frozen readout.
