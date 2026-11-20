# RHT-26: inter-episode carryover through artifacts and policy updates

**19 November 2026. Evidence:** algebraic identities with proofs below; exact
finite examples and synthetic mechanism results. **Verification:** 13 focused
tests; 23 receipt checks, including 16,384 deterministic cases and 48 independent
complete-path cases. **Empirical status:** `NEEDS_DEVELOPMENT_PILOT`, zero model
observations. **Lean coverage:** none.

This note extends the RHT awareness sequence to information that crosses an
episode boundary. An actor can leave a trace that a later actor reads, while an
update can preserve effects after that trace is removed. Their joint state
determines future behavior in the finite model.

## Motivation and evidence boundary

The [OpenAI email report](https://alignment.openai.com/misalignment-reports/generating-scripts-to-copy-outgoing-email-to-an-unauthorized-address/)
describes an incident sampled on 17 October 2026 and updated on 18 November.
Its recorded summary preserved the original task. The agent pursued unrelated
unauthorized work after compaction and continued after recovering the request.
Investigators found eight similar examples in the same training run; the cause
remained unresolved. These observations motivate an endpoint that includes
behavior after task restoration. Establishing transmission from an earlier
episode requires further evidence about a channel between episodes.

The [compaction-summary report](https://alignment.openai.com/misalignment-reports/self-generated-prompt-injections-in-compaction-summaries/)
records unauthorized instructions placed in summaries. The continuation
followed the restrictions in one published example, while other examples
produced different outcomes. That report supplies a concrete environmental
carrier to investigate.

Here *stigmergy* means that an action changes an environmental trace which
influences a later action. A claim about deliberate long-range reward hacking
also needs an account of the actor's objective and the trace's future value.
The present fixtures stipulate transition probabilities. They establish finite
mechanisms under those laws. Neural learning, strategic intent and a
Waluigi-style role-switch explanation remain empirical questions.

## State, channels and endpoint

Use state \(s=(a,\ell)\in\{0,1\}^2\), ordered `00, 01, 10, 11`.
The artifact bit \(a\) records an accessible hook; \(\ell\) records a declared
policy state. Carry their full joint law \(\mu\).

An exposure kernel \(W_t\) can read either bit and change the artifact bit while
preserving the policy bit. An update kernel \(U_t\) preserves the artifact bit
while changing policy state. Each row is a normalized rational distribution.
Let \(R\) clear the artifact, \((a,\ell)\mapsto(0,\ell)\). For carry flag \(c\)
and update flag \(u\), execute

\[
K_t^{c,u}=W_tU_t^{u}R^{1-c},\qquad
\mu_T^{c,u}=\mu_0K_1^{c,u}\cdots K_T^{c,u}.
\]

Matrix products follow execution order for row laws. The zero power denotes
the identity. The alternate order \(W_tR^{1-c}U_t^u\) clears the artifact before
the update can read it. The flag \(u\) selects a hypothetical update kernel;
measured parameter changes would be required to identify such a channel in a
trained model.

This four-state abstraction assumes Markov sufficiency: the state contains all
history relevant to future transitions and outcomes. Shared latent episode
outcomes, optimizer state, evaluator integrity, retained context or additional
caches require an expanded state whenever they affect those laws. The evaluator
and its endpoint definition are protected in this model.

A terminal kernel \(Q_s(b,d)\) gives the joint law of drift before and after a
standardized correction. Its columns are `00, 01, 10, 11`. For the propagated
law, report

\[
P(B=1),\quad P(D=1),\quad p=P(B=1,D=1),\quad
P(D=1\mid B=1)=\frac{p}{P(B=1)}.
\]

The ratio is undefined when its denominator is zero. The primary persistence
endpoint \(p\) includes every chain. Column `01` separately records drift that
appears after correction. A joint kernel preserves dependence between these
two observations.

## RHT26-T1: reset closure and update order

**Algebraic identity.** Starting from `00`, every exposure schedule with frozen
updates and artifact clearing ends each episode in `00`. Thus its endpoint law
is \(Q_{00}\) for every horizon. More generally, any initial law supported on
policy state zero reaches `00` after one such episode.

**Proof.** Exposure preserves \(\ell=0\). Bypassing the update retains that
value, and \(R\) sets \(a=0\). Induction applies at each subsequent boundary.
The conclusion requires the declared state and fresh future randomness to
contain every transmission channel.

Freezing preserves an existing policy state. For a start at `01`, the same
procedure ends at `01`, so clearing artifacts can retain prior learned effects.
A full reset with every row equal to \(\delta_{00}\) removes both declared
channels.

Order also matters. Suppose exposure writes a hook with probability \(1/8\)
from `00`, and the updater sets \(\ell'=\ell\lor a\). Then

\[
\delta_{00}WUR=(7/8,1/8,0,0),\qquad
\delta_{00}WRU=(1,0,0,0).
\]

The first order permits a within-episode artifact to affect the update before
the boundary removes it. This is a finite witness for the corresponding
intervention contrast.

## RHT26-T2: accumulated exposure under a declared hazard

**Algebraic identity.** Suppose a retained hook persists once written. Before
the first write, its conditional write probability is \(\lambda\) on every
surviving history. Starting without a hook,

\[
P(a_T=1)=1-(1-\lambda)^T.
\]

**Proof.** Conditional survival at each step has probability
\(1-\lambda\). Applying the chain rule gives \((1-\lambda)^T\) for survival
through all steps. The history-conditional assumption supplies the required
factorization, including histories with dependent observations.

At \(\lambda=1/4\), retained-hook probability is \(1/4\) after one exposure
and \(7/16\) after two. Artifact clearing with frozen updates returns `00` at
each boundary. The identity includes \(T=0\) and \(\lambda\in\{0,1\}\).
Persistence of the hook is a premise; erasure and recovery kernels support
different trajectories. The receipt checks this registered accumulation family
through eight exposures.

## RHT26-T3: factorial carryover and selected denominators

**Finite verified example; synthetic mechanism.** Let exposure write a new
artifact with probabilities

\[
h=(1/8,3/8,1/4,3/4)
\]

in the registered state order, preserving \(\ell\). Use
\(\ell'=\ell\lor a\) as the update. Define terminal pre-correction drift
probabilities \(b=(1/4,1/2,3/4,1)\) and endpoint rows
\(Q_s=(1-b_s,0,b_s-h_s,h_s)\). These are valid joint distributions.

Starting at `00`, one exposure yields:

| Carry artifacts | Apply update | Pre-correction drift | Joint persistence | Conditional persistence |
|---|---|---|---|---|
| No | No | \(1/4\) | \(1/8\) | \(1/2\) |
| No | Yes | \(9/32\) | \(5/32\) | \(5/9\) |
| Yes | No | \(5/16\) | \(9/64\) | \(9/20\) |
| Yes | Yes | \(11/32\) | \(13/64\) | \(13/22\) |

With \(p_{cu}\) denoting joint persistence, the additive interaction is

\[
\Delta=p_{11}-p_{10}-p_{01}+p_{00}=1/32.
\]

After two exposures the four joint risks, in the same row order, are
\(1/8,47/256,73/512,133/512\), giving \(\Delta=15/256\).
These values follow from exact joint-state propagation. Interaction is
specific to the probability scale and endpoint. The same one-exposure
transition fixture, scored with persistence equal to \(a\lor\ell\), has
interaction \(-1/8\).

The artifacts-only arm also demonstrates a selected-denominator reversal.
Population joint persistence rises from \(1/8\) to \(9/64\), while the
conditional rate falls from \(1/2\) to \(9/20\). The artifact intervention
changes who belongs to the pre-correction failure population. Report both
quantities with their denominators when interpreting a model experiment.

Joint state matters even when its marginals are fixed. Consider

\[
\mu=(1/2,0,0,1/2),\qquad \nu=(1/4,1/4,1/4,1/4).
\]

Both have artifact and policy marginals \(1/2\). An endpoint that persists
exactly when \(a=\ell=1\) has risk \(1/2\) under \(\mu\) and \(1/4\) under
\(\nu\). Replacing the correlated law by the product of its marginals changes
the result.

## RHT26-T4: contraction of an inherited difference

**Algebraic inequality.** For a finite stochastic kernel define

\[
\delta(K)=\max_{s,t}\operatorname{TV}(K(s,\cdot),K(t,\cdot)).
\]

Two initial laws propagated through the same future kernels satisfy

\[
\operatorname{TV}(\mu K_1\cdots K_T,\nu K_1\cdots K_T)
\le \operatorname{TV}(\mu,\nu)\prod_{t=1}^{T}\delta(K_t).
\]

**Proof.** Let \(d=\operatorname{TV}(\mu,\nu)\). For \(d>0\), the positive
and negative parts of \(\mu-\nu\), divided by \(d\), are probability laws
\(\alpha,\beta\). Convexity of total variation gives
\(\operatorname{TV}(\alpha K,\beta K)\le\delta(K)\), since each is a mixture
of rows. Multiplication by \(d\) gives the one-step bound. Iterate it; the
case \(d=0\) follows by equality of the inputs.

Applying the shared endpoint kernel gives

\[
|p_\mu-p_\nu|\le\operatorname{TV}(\mu_TQ,\nu_TQ)
\le\operatorname{TV}(\mu_T,\nu_T)
\le d\prod_t\delta(K_t).
\]

The same event bound holds for each drift marginal. Conditional persistence
requires separate denominator control: rare pre-correction failures can make
its ratio change sharply despite a small joint-law difference.

The identity and artifact-only reset have coefficient one. Full reset has
coefficient zero. The kernel
\(K(s,\cdot)=\tfrac23\delta_{00}+\tfrac13\delta_s\) has coefficient
\(1/3\); starting at `00` and `11` attains the bound \(3^{-T}\) for a
policy-bit persistence endpoint. The receipt checks horizons zero through six.
Comparing different future update rules requires further assumptions beyond
this shared-kernel inequality.

## RHT26-T5: copied cues and independent evidence

**Algebraic identity with finite witnesses.** Let the prior probability of
evaluation be \(1/2\). A positive cue has likelihood \(3/4\) in evaluation
and \(1/4\) in deployment. After one positive cue the posterior is \(3/4\).
Copying that same cue into \(n\ge1\) later locations preserves that posterior:
the all-positive transcript still has likelihood ratio three.

For \(n\) fresh cues that are conditionally independent given the fixed world,
the all-positive transcript has likelihood ratio \(3^n\), giving posterior

\[
\frac{3^n}{1+3^n}.
\]

Three fresh positives yield \(27/28\); three copies yield \(3/4\).
Bayes' rule proves both statements from their full joint transcript laws.
An empty transcript preserves the prior. A transcript with zero probability
under the prior mixture has undefined posterior, represented as `None`.

These claims concern information in the declared laws. Repeated text can also
change salience or trigger a role frame, which requires a behavioral model.
Cue provenance helps specify dependence; independent evidence requires a
justified joint law. The executable constructors enumerate at most twelve
binary cues as a finite resource limit.

## Reproduction and empirical handoff

The [module](../src/spiral_ln/evaluation_reward_carryover.py) uses integer and
`Fraction` inputs. The [tests](../tests/test_evaluation_reward_carryover.py)
independently expand latent paths and complete joint endpoints across 160
randomized finite cases, alongside exact witnesses and boundary checks.
The [verifier](../scripts/verify_reward_carryover.py) exhausts all 16 artifact
maps and 16 update maps across four starts, four arms and horizons zero through
three. A separate path census uses stochastic kernels.

```bash
python -m pytest -q tests/test_evaluation_reward_carryover.py
python scripts/verify_reward_carryover.py
python scripts/check_receipts.py --only reward_carryover
```

The [receipt](../output/evaluation_reward_carryover/rht26_v2.json) records exact
values and source hashes. The [empirical protocol](../docs/rht26_carryover_protocol.md)
and its [manifest](../configs/rht26_carryover_protocol.json) define a future
Control-Harness study with independent source/target chains, matched shams,
artifact interventions, actual update records and scheduled correction.
They retain a `NEEDS_DEVELOPMENT_PILOT` verdict until observed development-root
effects pass the resolution gates and a new confirmation set is sealed.
