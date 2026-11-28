# EIM-01: Evaluation-to-mechanism coupling for looped Lean reasoning

**Research status, 2026-11-15:** source-bound synthetic experiment, actual BPD donor intervention training, deterministic held-out-family development evaluation. The factors are planted and known. This is a working experiment-design bridge, rather than an inference result for an independently trained language model.

## The identification problem

Ordinary correctness evaluates a final answer. If a superficially predictive cue agrees with the proof graph on every training example, a proof-chain mechanism and a cue-following shortcut predict identical labels. EvalMath BPD-01 puts these candidates in the same observational class.

EIM-01 extends the evaluation unit from a correct/incorrect answer to a **source-bound interventional effect**. Each measurement contains the source theorem/root, donor, component, recurrent pass, next readout, frozen model identity, verified label, observed route, and signed logit change. The code rejects unknown routing, uncertified labels, mixed readout clocks, and held-out samples in acquisition.

## Mathematical interface: two separate matrices

Fable's underlying circularity problem appears even at the level of a
linear readout. A measured output effect of component c already includes
the component's current readout coefficient. Using that effect as the
design matrix in d=A theta would reuse the unknown theta on both sides.

EIM-01 therefore records **two separate objects** from each same-pass
source/donor pair e:

1. Pre-readout geometry Q[e,c] = z_{t,c}(x)-z_{t,c}(x'), measured at the
   actual component-input site *before* multiplying by the current head.
2. End-to-end signed causal response E[e,c], measured by running the
   BPD component donor swap and subtracting positive-class logits at
   the specified next readout r>t.

In a known local linear circuit whose transport for row e is a scalar
kappa_e, define the design matrix X[e,c]=kappa_e*Q[e,c]. A joint swap has
signed logit displacement

\[
d_e = \sum_c X_{e,c}\theta_c,
\qquad E_{e,c} = X_{e,c}\theta_c.
\]

The second identity is a *hypothesis to check*, rather than a definition
of the design. Our planted relay has transport kappa=3.5*0.35*0.65,
independent of cue and proof graph at this penultimate-pass site.
The implementation measures Q and the actual joint-swap logit d
separately, and checks the residual in d=X theta under that known
transport. Observed per-component effects E are retained for causal
specificity audits. In a learned nonlinear model there may be no scalar
transport, and interactions must be estimated rather than assumed.

For the declared linear-response model d=X theta+epsilon, noiseless
coefficients are identifiable iff X has full column rank: otherwise all
theta+ker(X) agree. When X is full rank, least-squares satisfies

\[
\|\widehat{\theta}-\theta\|_2
\leq \frac{\|\epsilon\|_2}{\sigma_{\min}(X)}
\leq \frac{\sqrt n\,\delta}{\sigma_{\min}(X)}
\]

if n measurements have absolute error at most delta each. These are
classical inverse-problem stability identities. EIM-01 performs exact
finite two-row selection by the smallest singular value of X, subject to
source, route, provenance and clock checks. Full rank is conditional on
the model coordinates; a learned rotating dictionary needs a separate
subspace-level alignment protocol.

An aligned input pair changes graph and cue, giving pre-readout geometry
[a,b] with rank one. A cue-only pair fixes the graph and gives [0,b],
while a graph-only pair holds cue fixed and gives [a,0]. Their predicted
zeros are checked by *executed* BPD interventions. Both pre-readout
identifiability and output-effect specificity are independently reported.

## The closed loop actually implemented

The source is EvalMath's BPD-LG-02 corpus: 384 synthetic Lean/Horn/equality tasks whose positive proofs and negative refutations were independently kernel audited. A second recurrent graph-closure implementation reproduced all 384 host labels.

The test model is an explicit shared-weight two-factor graph relay. Factor 0 reads iterated graph reachability and factor 1 reads a deliberately misleading cue. The two output weights and a bias are trainable. The factor dictionary is frozen at its known planted values.

The training set uses 192 original BPD-LG-02 training cases from exact, rw, and rcases. Its cue is intentionally equal to the label, giving the model a shortcut. A development holdout uses 16 induction-family cases from test-root groups with the cue flipped. This creates an adversarial causal contrast, rather than a natural theorem-proving benchmark.

From the training corpus, three donor pairs are proposed. The source/donor geometry and the signed causal-response matrix are measured
separately using BPDModel activations at pass 20 with readout 21. The
two-intervention selector uses the **readout-independent input/transport
geometry**; the observed component effects provide an independent check.
It chooses graph-only and cue-only probe types.

The selected cue-only donor intervention preserves the verified graph label. On each training update the chosen BPD component is swapped at all 22 passes with activation from the same graph under the opposite cue. The optimization objective averages ordinary-label cross entropy with cross entropy on this internally intervened trajectory. **Gradient flows through the actual counterfactual rollout**, with BPD factors frozen and only output routing learned.

All four compared arms share the same initial 40-step cue-confounded head fit. They then receive 90 optimizer updates and 384 case-rollout records per update. The passive arm uses duplicate unmodified examples; input augmentation directly flips the visible cue; the intervention arm uses internal donor activations.

| Arm | Accuracy on 16 fourth-family cue-conflict development cases |
| --- | ---: |
| Starting shortcut-biased head | 0/16 |
| Passive continuation, compute matched | 0/16 |
| Input-level cue augmentation | 16/16 |
| BPD all-pass interchange intervention training | 16/16 |

Seven tests passed under Python 3.12 and CPU PyTorch 2.5.1. They cover 384/384 host graph-label agreement, source gating, finite rank and error bounds, component-specific real interventions, and the exact training comparison. A seventh test checks that joint factor swaps equal the sum of singles in the planted linear reference; this is a calibration, not a claim of general additivity. The workflow also archives a JSON receipt.

**Important interpretation:** contrastive evaluation repairs the deliberate shortcut, and training against internally swapped BPD activations is operational. The conventional input-level augmentation control reaches the same accuracy. This toy does not demonstrate a *unique benefit* from the BPD intervention, learned factor discovery, mechanistic generalization to a natural Lean theorem, or capability gains in an existing model. Development used this fourth-family test cohort repeatedly; a newly sealed confirmation cohort is necessary.

## Gate for a genuine mechinterp result

1. Train a compact recurrent Lean reasoner on original source-separated proof states. Independently replay tactic success through the Lean kernel. Keep unsuccessful and unprobed actions distinct.
2. Fit BPD factors without planting their identities. Compare against unrolled VPD, taxonomy lookup, input augmentation, and strong symbolic search.
3. Acquire source/donor pairs before unsealing a fresh family/root holdout. Use measured single-pass and persistent interventions to build the effect matrix, and test predictive effects on unknown joint cuts.
4. Include cases in which an input change and a hidden-state interchange induce different next-readout trajectories. A cue/source conflict with an independently held carried state is useful here.
5. Measure effect stability across decomposition seeds, matched rank, calibration costs, timing and state-matching tolerances. Treat rank after a deliberate mechanism is suppressed as a separate diagnostic from the pre-training acquisition rank.

## Reproduce

At the EvalMath root, with CPU PyTorch and pytest installed:

    PYTHONPATH=mechinterp-reverb:. python -m pytest -q mechinterp-reverb/eim01/test_eim01.py
    PYTHONPATH=mechinterp-reverb:. python -m eim01.gym

Sources: eim01/gym.py, eim01/design.py, BPD-LG-02 generator, the original BPD donor-swap implementation in mechinterp-reverb/mechinterp/bpd/components.py, and the EIM-01 Actions workflow.

Related foundations: Geiger et al., Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability, JMLR (2025), https://jmlr.org/beta/papers/v26/23-0058.html ; Zhang and Nanda, Towards Best Practices of Activation Patching in Language Models, ICLR (2024), https://proceedings.iclr.cc/paper_files/paper/2024/file/06a52a54c8ee03cd86771136bc91eb1f-Paper-Conference.pdf .
