# Inkling variable-depth monitorability: root-aware evaluation mathematics

Status: **source-only development instrument**, November 21, 2026. It adds no
neural performance results and does not release any sealed cohort.

## Citation audit

- [Thinking Machines Inkling 2 Mini release](https://thinkingmachines.ai/news/inkling-2-mini/)
  and [variable-loop model card](https://thinkingmachines.ai/model-card/tml-d24-varloop-research/):
  loop count 1–5 midtrained with ratio 1:2:6:2:1; RL occurs at 3.
- [Universal Transformers](https://arxiv.org/abs/1807.03819):
  adaptive halting is position dependent, so a single task-level compute
  count does not fully describe its work.
- [Reasoning Models Struggle to Control their Chains of Thought](https://arxiv.org/abs/2603.05706):
  instruction-following about CoT is a separate variable from monitor
  detection of bad behavior. Near-zero controllability means low power
  to distinguish loop counts.
- [Chain of Thought Monitorability](https://arxiv.org/abs/2507.11473):
  verbalization changes the observation available to monitors.
- [Intelligence per Watt](https://arxiv.org/abs/2511.07885):
  accuracy, energy, latency and hardware are separate axes. A
  token-layer proxy is not a measurement of joules.
- [Mixture-of-Recursions](https://arxiv.org/abs/2507.10524) and
  [Ouro](https://arxiv.org/abs/2510.25741): learned depth
  choices introduce calibration and adaptive-selection exposure.
- [Goodfire Inkling interpretation](https://www.goodfire.com/research/interpreting-inkling-2-mini/):
  coda/tuned lenses expose additional observables; a probe prediction
  is an observational result until a causal intervention is verified.

## Key inference boundaries

The original release reports 1-pass no-CoT Think Fast horizon 16 seconds
versus 3-pass 37 seconds. The 5-pass reasoning-token mean (1,661)
and the 1-pass mean (3,703) were computed on GPQA questions answered
correctly at *all* depths. That is a selected subset of tasks.
A depth treatment can itself change correctness and thus membership
in this subset. Preserve full-population intent-to-treat means, missing
generation outcomes, and the shared-correct subset as explicitly
post-selected descriptive data.

CoT controllability among 750–1,250-token traces is <=0.1% for the
three-pass variable model, leading to a near-zero numerator. A
non-significant variation across pass counts cannot certify
equivalence. A valid equivalence test requires a predeclared margin,
appropriate power, and a confidence interval lying entirely
within that margin.

The LinuxArena study tests a subset of 184 task/side-task pairings,
with a monitor calibrated to 1% false positives. The reported
stealth rates vary by loop count (tool-only 1.0%–5.0%; with text and
thinking 0.0%–0.6%) with few successes. Root identities and paired
success counts are required for a proper paired difference test;
the displayed percentages alone are insufficient. At zero detected
events in 184 independent Bernoulli trials, even the idealized
one-sided exact 95% upper bound is about 1.62%, conditional on iid
sampling. Reused tasks or shared checkpoints weaken that assumption.

The source model was trained much more at depth 3. Inference sweeps
over depth confound additional computation with differential
training exposure. Record the checkpoint, curriculum, cache mode,
reasoning effort and generation budget for every comparison.

## Matched task-root design

Treat the task generator root or independently selected agentic task as
the independent sampling unit. An identical problem at pass counts
1, 2, 3, 5 and 10 remains one source, irrespective of the number of
response tokens, interventions, scores or retries.

Before studying differences:
1. Freeze the primary causal or capability endpoint, minimum useful
   magnitude, sham envelope, multiplicity family and independent-root
   population. Run the [EvalMath preflight](../../skills/evalmath-mechinterp-power/SKILL.md)
   using a development-only pilot.
2. Use one source-root paired task matrix, fixed model weights and cache,
   and record missing replies and actual cost. Freeze which monitor
   sees which observable and match monitor false-positive rates.
3. Report verifier accuracy at all depths, first successful pass,
   later regressions, total visible tokens, latency, energy and
   monitor false positives. Compute cost-conditioned curves with
   the actual hardware and budget; label layer-application counts
   as analytical proxies.
4. Evaluate both the unconditional source population and the
   intersection-correct subset, explicitly labeling the latter as
   outcome-conditioned.
5. Run [FSI-01](../../paper/finite_sample_inference.md)
   on independent paired roots, using root-level signed inference,
   complete comparison-family multiplicity correction and a newly
   untouched confirmation set. Retain raw paired outcomes.

## Source-only evaluator

The new [depth_matrix.py](depth_matrix.py) checks a complete
case-by-depth development matrix, verifies that root identities and
checkpoint/cache modes remain constant, and gives paired accuracy
and cost summaries. It does **not** issue a p-value or promotion verdict.
It writes an FSI-01 manifest with preregistration and seal fields FALSE,
which must be replaced by independently documented prospective evidence
before scientific confirmation.

Each JSONL row contains:

    {"case_id":"task-001","root_id":"source-001","family":"pointer",
     "model_sha":"sha256:yourrealcheckpoint","cache_mode":"unshared",
     "split":"calibration","depth":3,"verified":true,
     "reasoning_tokens":124,"total_tokens":190,"wall_ms":38.1,
     "joules":null}

Multiple cases may share one root. All depths must cover the same cases.
Runs from synthetic fixtures, oracles, sealed split or changed models
are rejected. Verify correctness externally: the field 'verified' is
an operator-supplied claim, not an independent verifier receipt.

    python research/inkling_loop_monitorability/depth_matrix.py \
      --input DEVELOPMENT_ROWS.jsonl \
      --baseline-depth 1 --candidate-depth 3 \
      --out runs/inkling_depth_audit_01

    python -m unittest discover -s research/inkling_loop_monitorability \
      -p 'test_depth_matrix.py' -v

The output contains report.json and fsi_dev_manifest.json. This is an
auditable descriptive bridge. Actual independent correctness checks,
replayable per-task receipts, reliable source root IDs, and
pre-data model selection accounting remain requirements upstream.

## Transfer gates

- LoopedTransformers: same model, different pass counts; trained
  positive-control task before interpretability.
- Compactification-Theory: parameter/compute/energy Pareto, with
  explicit numerical precision and routing buffer costs.
- BPD: matched-dose causal routing interventions, task verifier,
  false-positive-controlled readout, donor+sham and fresh roots.

Null results should be retained. No protected split is available
to this source-only module.


## 2026-11-21 source-compatible execution on genuine generated receipts

The LoopedTransformers
[RMP-INK-PC01 Actions run #44900273337](https://github.com/MoralityLabAI/LoopedTransformers/actions/runs/44900273337)
pinned this auditor to source commit
ff32b93a311842967da1e4e33ac08e4ac576c46e and executed it
on the full synthetic trained-gate rollout. It processed 512 task
instances from 64 distinct source graphs at six inference depths,
with an exact, complete 3,072-row paired matrix. The 1-pass to
3-pass root-macro difference was +0.25 on the development roots.
The BPD sibling auditor independently replayed the graph targets,
recurrent transition rule and physical state interventions.

The retained Actions artifact includes report.json and
fsi_dev_manifest.json. The FSI manifest has 512 case rows and
sealed_readout=false, hypothesis_preregistered=false,
clusters_independent=false. Those flags intentionally prevent
promotion to scientific confirmation. The model's one trained
parameter only sets the mixture between an **explicit graph
transition operator** and the current state. The 1-vs-3 depth gain
is therefore a constructed instrumentation positive control,
not a neural reasoning or monitorability result.

The next native-model study needs fresh, independent roots,
unselected outcome populations, model/pass/configuration receipts
and measured cost where meaningful. The sealed compartments
in unrelated EvalMath campaigns remain untouched.
