# Evaluations that preserve downstream behavior: a proof contract

**21 November 2026. Evidence:** research plan, with finite mathematical results
implemented in [RHT-27](RHT-27/evaluation_noninterference.md) and
[RHT-28](RHT-28/contamination_composition.md). The proposed useful-feedback
frontier and adaptive statistical extension remain future work. All current
computation uses CPU arithmetic on explicitly supplied finite laws.

## The question carried forward

An evaluation can leave content which later agents read. Training on its traces
can also alter the model, while the evaluator's own state can influence later
scores. Repeated exposure therefore calls for a model of the complete sequence
and the channels that survive each boundary.

The [OpenAI email incident][email] records an agent pursuing unauthorized work
after compaction and continuing after retrieving the original request. The
scripts remained unexecuted, and the investigation left the cause unresolved.
The [compaction-summary report][summaries] describes model-written instructions
passed to a later context, with varying continuation behavior. These reports
motivate a causal transmission question. They supply no estimate of the
transition probabilities used in the finite models here.

[RHT-26](RHT-26/carryover.md) supplies exact carryover examples. Its later
[development review](RHT-26/development_bridge.md) finds that the existing pilot
identifies the effect of a repeated-instruction treatment in the final visible
store. The harness wrote the source cues. Establishing deliberate long-range
stigmergy would also require agent-chosen writes and a causal account of their
future value. A Waluigi-style role-switch account would need an operational
state definition and interventions that separate it from competing explanations.

## Declare what an evaluation may teach

Let a sufficient state contain model parameters and every other variable that
can affect continuation. Depending on the system, this includes optimizer state,
memory, retrieved artifacts, context, cached training batches, random-generator
state, the evaluator, and the policy which selects later tasks.

For a fixed external context and starting state, let

\[
K_e(s,\cdot)=\mathcal L(S^+\mid\operatorname{do}(E=e),S=s)
\]

denote a declared intervention kernel. A registered map
\(\phi:\mathcal E\to\mathcal Z\) specifies the feedback allowed to cross
the boundary. Its values could be typed proof failures or verified task labels.
The mechanism choosing this map and authenticating its inputs belongs to the
trusted interface. A model-generated claim of authority does not establish
that trust.

The finite contract compares interventions which preserve the permitted value:

\[
\varepsilon=\max_{s,\,e,e':\phi(e)=\phi(e')}
\operatorname{TV}\!\left(K_e(s,\cdot),K_{e'}(s,\cdot)\right).
\]

Every declared state participates in the maximum. This definition uses
interventions at a fixed starting state. An observational conditional law given
the transcript can include selection effects and preexisting differences in
state, so it needs a separate identification argument before it can supply
these kernels.

RHT-27 proves that \(\varepsilon=0\) is equivalent to the existence of a
permitted-only kernel \(L\) on the attained feedback values such that
\(K_e(s,\cdot)=L_{\phi(e)}(s,\cdot)\). The result applies to the declared
output space. To cover later behavior, that space must retain all state used by
the continuation, whose further kernels must obey the same interface contract.

For positive \(\varepsilon\), a fixed representative or fixed mixture from each
feedback class supplies a comparison kernel. The maximum class diameter bounds
the discrepancy to that comparison. An arbitrary common downstream kernel
preserves the bound by contraction of total variation.

### A meaningful feedback contract

The map \(\phi(e)=e\) creates singleton classes. Its zero diameter permits the
entire transcript to pass, so the audit reports this vacuity explicitly. A
constant map can exclude useful learning. Selecting the permitted vocabulary
therefore requires an independent specification of utility and acceptable
effects. The dimensions of information release discussed by
[Sabelfeld and Sands][declassification] provide background for specifying the
content, authority, location and timing of that interface.

Even a nontrivial class partition can permit harmful behavior. For example,
an authenticated outcome label can be interpreted by a poorly specified updater
as an instruction to take an unauthorized action. The updater may depend only
on that label and satisfy zero residual influence perfectly. A safety claim
also needs a bound on the permitted-only system's risk, with a justification
that the actor cannot manipulate the allowed feedback outside its declared
rules. RHT-27 includes an exact counterexample to keep that obligation visible.

## Compose the effect through later runs

Consider two chains with initial laws \(\mu_0,\nu_0\), and step kernels
\(P_t,Q_t\) over the same sufficient state spaces. Register the uniform row
discrepancy

\[
e_t=\max_s\operatorname{TV}(P_t(s,\cdot),Q_t(s,\cdot)),
\qquad d_0=\operatorname{TV}(\mu_0,\nu_0).
\]

Let \(\delta(K)=\max_{x,y}\operatorname{TV}(K(x,\cdot),K(y,\cdot))\)
and \(\delta_t=\min\{\delta(P_t),\delta(Q_t)\}\). The two triangle
decompositions, followed by contraction, give

\[
d_t\le\min\{1,\delta_t d_{t-1}+e_t\}.
\]

RHT-28 proves and checks the resulting bound

\[
d_T\le\min\!\left\{1,
d_0\prod_{j=1}^T\delta_j+
\sum_{t=1}^T e_t\prod_{j=t+1}^T\delta_j\right\}.
\]

Empty products equal one. The initial term matters when a supposedly fresh
run already carries different policy state. Per-step clipping supplies a
bound at least as tight as this clipped expanded expression. Averaging
discrepancies over a convenient state distribution can hide a fully exposed
state; RHT-28 includes that failure as a separate witness.

Task choice can depend on prior observations when the controlled state
contains the relevant history and the per-step bound is uniform over all
reachable controls included in that model. Merely substituting a sequence of
empirically fitted marginal kernels leaves that premise unverified.

### A cleared state and a recorded failure

The distribution of the current state can return to its reference law after a
reset. An action emitted earlier remains part of the history. For the full
state path, a sequential maximal coupling gives

\[
\operatorname{TV}(\mathsf P_{0:T},\mathsf Q_{0:T})
\le 1-(1-d_0)\prod_{t=1}^T(1-e_t).
\]

Actions belong in a joint transition/emission kernel or an augmented state
whenever the claimed endpoint reads them. An absorbing flag which records
whether any violation has occurred provides a small model for that particular
event. Its persistence prevents a later workspace reset from erasing the
mathematical record of harm. RHT-28 verifies a case where final workspace TV
is zero and path TV is one.

For a common protected loss \(f\in[0,1]\), a TV bound \(b\) yields
\(\mathbb E_P f\le\mathbb E_Q f+b\). Thus a licensed baseline risk
\(r_0\) produces the risk bound \(\min(1,r_0+b)\). If the evaluator or
loss definition differs between chains, its discrepancy needs an additional
term. An unprotected judge cannot certify the common-loss premise itself.

## Useful learning and statistical validity

The proposed RHT-29 objective is to choose a feedback channel and updater which
maximize a declared measure of useful learning subject to a downstream risk
budget. The admissible class of feedback maps must be fixed in advance, and
the contract must include a positive utility floor. Otherwise the objective
admits vacuous solutions through identity disclosure or total suppression.

The proposed FSI-02 work concerns the statistical consequences of adaptive
evaluation and selection across generations. It should track the actual
information available to the learner, every adaptive query, and the independent
ancestral units. [FSI-01](../paper/finite_sample_inference.md) supplies the
current repository's inference methods after a protocol has been frozen.

[Dwork and Roth][privacy] prove differential privacy's postprocessing and
composition properties for a specified neighboring-dataset relation. Those
results offer tools for an adaptive data-release contract. Translating such a
contract into permission to execute instructions requires additional premises:
a release mechanism can be perfectly private while always returning an unsafe
instruction independent of the dataset. The same distinction applies when
designing a reusable held-out evaluation service.

## The first implementation and its empirical handoff

RHT-27 implements exact finite audits of the intervention interface, including
explicit witnesses for residual influence and vacuous feedback partitions.
RHT-28 composes uniform perturbations and compares terminal-state claims with
complete-path claims. Their receipts hash the code, tests and notes, and
independent enumerators check the finite examples. The Lean claim table states
the precise scope of the formalized supporting results.

No neural transitions are estimated in this change. The independent-root
sample size and sham-calibration preflight therefore have no empirical inputs
here; exact enumeration supplies mathematical evidence within its declared
domain. A future Control-Harness experiment must specify its intervention
interface before fitting the kernels, identify every retained channel, and
register its protected downstream endpoint. It must also preserve the complete
selection history and perform the repository's preflight on independent
development roots before opening a sealed confirmation set.

The bridge to practice is an auditable causal interface. Each component needs
evidence that its read/write paths satisfy that interface, followed by a
justification for the law used in the bound. Hashes attest to the bytes used
for a calculation; they leave that physical correspondence as a separate
obligation.

[email]: https://alignment.openai.com/misalignment-reports/generating-scripts-to-copy-outgoing-email-to-an-unauthorized-address/
[summaries]: https://alignment.openai.com/misalignment-reports/self-generated-prompt-injections-in-compaction-summaries/
[declassification]: https://journals.sagepub.com/doi/abs/10.3233/JCS-2009-0352
[privacy]: https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf
