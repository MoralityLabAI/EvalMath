# RHT-28: contamination through successive evaluations

**Evidence:** algebraic identities and derived inequalities for finite kernels,
with complete written proofs below; exact finite verified examples.
**Receipt:** `RHT-28-v1`; 22 checks, 9,603 complete-path comparisons and 38,412
terminal-event checks. **Unit tests:** 14. No model inference or training occurs
in this result. The computations concern supplied finite laws.

An evaluation can leave a changed workspace, a learned parameter, or a control
decision that affects later evaluations. RHT-27 assigns a discrepancy budget to
influence outside a declared feedback channel. This note carries such budgets
through a sequence of evaluations and states the event that each bound covers.

The comparison includes an initial-state discrepancy. It also preserves the
difference between a current-state risk and an event anywhere in the recorded
history. Those choices determine whether a reset can reduce the reported bound.

## 1. Declared comparison

For times \(t=0,\ldots,T\), let \(X_t\) be nonempty finite spaces. At each step,
two row-stochastic kernels share the same input and output labels:

\[
P_t,Q_t:X_{t-1}\longrightarrow\Delta(X_t).
\]

The initial laws are \(\mu_0,\nu_0\in\Delta(X_0)\). Their subsequent laws satisfy
\(\mu_t=\mu_{t-1}P_t\) and \(\nu_t=\nu_{t-1}Q_t\). We use

\[
\operatorname{TV}(p,q)=\frac12\sum_x|p(x)-q(x)|,
\qquad d_t=\operatorname{TV}(\mu_t,\nu_t).
\]

The Markov assumption holds under each declared intervention: for every history
with positive probability under the first system,

\[
\Pr_P(X_t=x_t\mid X_0=x_0,\ldots,X_{t-1}=x_{t-1})
=P_t(x_{t-1},x_t),
\]

and the corresponding equality holds with \(Q_t\) in the reference system.
This condition licenses the product of transition probabilities used for full
path enumeration.

Here \(Q\) represents the registered reference process. It may perform useful
learning through the permitted feedback channel. Its risk is a separate input
to any absolute safety statement.

Each state must contain the information needed to determine the next
conditional transition law. Depending on the system, this includes model
parameters and optimizer state, live context, durable files, retrieval indices,
pending training batches, and decisions about which task or checkpoint runs
next. Any shared latent variable that affects later transitions belongs in that
state or in a correctly specified conditional kernel.

For an adaptive controller, the history it uses must also be present. The
controller's action selection then becomes part of \(P_t\) and \(Q_t\).
Changing the controller while keeping its former kernel bound requires a new
argument. The same requirement applies to changing task distributions or
selection rules.

The laws are **interventional** laws of these declared systems. Conditioning
an observational sample on an evaluation transcript can select different
initial states; that conditional comparison does not supply the kernels above.

### Relationship to RHT-27

RHT-27 bounds differences between evaluation interventions sharing a registered
permitted-feedback value. Its bound supplies an \(\varepsilon_t\) here when the
paired transition kernels meet that restriction at every compared state. If the
interventions can change permitted feedback, the resulting change needs its own
budget or an external authorization guarantee.

A choice of one representative kernel per permitted-feedback value gives a
permitted-only reference process. The composition result then compares the
actual process with that declared reference. Identity feedback maps, dangerous
permitted messages, and an already unsafe reference remain separate issues.

## 2. Uniform one-step discrepancy

Define the row discrepancy and contraction coefficients by

\[
\varepsilon_t=\max_{x\in X_{t-1}}
\operatorname{TV}\bigl(P_t(x,\cdot),Q_t(x,\cdot)\bigr),
\]

\[
\delta(P_t)=\max_{x,x'\in X_{t-1}}
\operatorname{TV}\bigl(P_t(x,\cdot),P_t(x',\cdot)\bigr),
\qquad
\delta_t=\min\{\delta(P_t),\delta(Q_t)\}.
\]

All these quantities lie in \([0,1]\). A one-input kernel has contraction
coefficient zero. The maximum includes every row of the declared domain, even
when a particular initial law assigns that row probability zero.

**T1, algebraic inequality.** Under this finite-kernel specification,

\[
d_t\le\min\{1,\delta_t d_{t-1}+\varepsilon_t\}.
\]

**Proof.** First take any finite laws \(\mu,\nu\) and a common kernel \(K\).
Write \(d=\operatorname{TV}(\mu,\nu)\). If \(d=0\), their output laws agree.
Otherwise, the positive and negative parts of \(\mu-\nu\) both have mass
\(d\), so they can be written \(d a\) and \(d b\) for probability laws
\(a,b\). Consequently,

\[
\mu K-\nu K
=d(aK-bK)
=d\sum_{x,y}a(x)b(y)\bigl(K(x,\cdot)-K(y,\cdot)\bigr).
\]

The triangle inequality for half the \(\ell^1\) norm gives
\(\operatorname{TV}(\mu K,\nu K)\le d\delta(K)\). Mixing equally indexed
rows also gives

\[
\operatorname{TV}(\nu P_t,\nu Q_t)
\le\sum_x\nu(x)\operatorname{TV}(P_t(x),Q_t(x))
\le\varepsilon_t.
\]

Insert \(\nu_{t-1}P_t\) between \(\mu_{t-1}P_t\) and
\(\nu_{t-1}Q_t\) to obtain \(\delta(P_t)d_{t-1}+\varepsilon_t\).
Inserting \(\mu_{t-1}Q_t\) instead gives
\(\delta(Q_t)d_{t-1}+\varepsilon_t\). Both hold, which permits the smaller
coefficient. Total variation is at most one. This proves the displayed bound.

An average over rows can understate the discrepancy at the state reached by a
controller. For example, take \(P=I\) on two states and let every row of
\(Q\) reset to state zero. The row errors are zero and one, whose uniform
average is \(1/2\). Starting both systems in state one produces output TV one.
The maximum used in T1 is one. Occupancy-weighted alternatives need a proof
using the appropriate evolving occupancy law.

## 3. Composition and the initial condition

Set \(b_0=d_0\) and calculate

\[
b_t=\min\{1,\delta_t b_{t-1}+\varepsilon_t\}.
\]

**T2, algebraic identity and inequality.** For every horizon including zero,

\[
d_T\le b_T\le
\min\left\{1,
d_0\prod_{t=1}^{T}\delta_t+
\sum_{t=1}^{T}\varepsilon_t\prod_{j=t+1}^{T}\delta_j
\right\}.
\]

An empty product equals one and an empty sum equals zero.

**Proof.** T1 and the nonnegativity of \(\delta_t\) give \(d_t\le b_t\)
by induction. For the uncapped recursion \(u_0=d_0\),
\(u_t=\delta_tu_{t-1}+\varepsilon_t\), substitution or induction gives

\[
u_T=d_0\prod_{t=1}^{T}\delta_t+
\sum_{t=1}^{T}\varepsilon_t\prod_{j=t+1}^{T}\delta_j.
\]

Because \(b_t\le u_t\) and \(b_t\le1\), the second inequality follows.

The first term accounts for contamination already present before the chosen
evaluation sequence. A clean evaluation kernel cannot justify dropping it.
For \(P_t=Q_t\), all one-step discrepancies vanish and only that term remains.

The clipped recursion can give a tighter value than clipping the final sum.
Two successive steps with \(\delta=\varepsilon=1\) give an uncapped value
two from an initially identical pair. A subsequent common kernel with
\(\delta=1/2\) reduces the recursive bound to \(1/2\); the final clipped
sum is one. The receipt constructs these steps using identity and swap kernels,
followed by a common contraction.

For constant bounds \(\delta\in[0,1)\) and \(\varepsilon\in[0,1]\),
the uncapped expression becomes

\[
d_0\delta^T+\varepsilon\frac{1-\delta^T}{1-\delta}.
\]

At \(\delta=1\), it is \(d_0+T\varepsilon\). These expressions inherit
the final cap at one. Persistent parameter state or preserved history can make
the full-state contraction coefficient one even when a workspace field resets.

## 4. Complete histories and earlier actions

Let \(\mathsf P_{0:T}\) and \(\mathsf Q_{0:T}\) denote the laws of the
complete state histories \((X_0,\ldots,X_T)\). Each history probability is
its initial mass multiplied by the successive row probabilities.

**T3, algebraic inequality.** Under the same assumptions,

\[
\operatorname{TV}(\mathsf P_{0:T},\mathsf Q_{0:T})
\le c_T:=1-(1-d_0)\prod_{t=1}^{T}(1-\varepsilon_t).
\]

**Proof.** Finite probability laws have a coupling that agrees with probability
one minus their TV distance: place their coordinatewise common mass on the
diagonal and couple the residual masses. Use this construction initially.
Whenever the two histories still agree at the start of a step, their current
state is the same \(x\). Couple the rows \(P_t(x)\) and \(Q_t(x)\) so
that the next states agree with probability at least \(1-\varepsilon_t\).
After the first disagreement, any coupling with the correct marginals suffices.
The probability that the full histories agree is at least
\((1-d_0)\prod_t(1-\varepsilon_t)\), by multiplying conditional lower
bounds. Coupling errors need no independence assumption. For any coupling,
TV is bounded by the probability of disagreement, which proves T3.

Current state is a projection of its history. The executable certificate
therefore reports the terminal bound

\[
B_T=\min\{b_T,c_T\}.
\]

The path bound applies to a protected common readout of those histories.
For claims about emitted tool calls, the state representation must include the
emitted calls, or the comparison must include a common transition-and-emission
kernel that records them. A hidden emission channel requires a separate bound.

### A reset witness

Use state zero for safe and state one for harmful. Both systems start in zero.
The first system moves to one, then resets to zero. Its reference remains zero
through both steps. Their terminal laws agree exactly:

\[
\mu_2=\nu_2=(1,0),\qquad d_2=B_2=0.
\]

Their paths are \((0,1,0)\) and \((0,0,0)\), so full-history TV is one.
The event “state one occurred at least once” has probabilities one and zero.
A reset cannot change that recorded event.

The same event can be represented in a terminal state by preserving an
absorbing flag for whether harm occurred. The receipt uses the valid states
“clean,” “currently harmful with history,” and “reset with harmful history.”
After reset the systems occupy different states, and terminal TV remains one.
The reset kernel then has contraction coefficient one on this enlarged space.

The time interval belongs in the claim. A statement covering actions after a
complete reset can begin at the reset boundary. A statement covering the whole
training run must retain the earlier actions in its event.

## 5. Translating distance into downstream risk

Let \(f:X_T\to[0,1]\) be a protected common loss. It may be an indicator
of an unauthorized action or a bounded graded outcome.

**T4, algebraic inequality.**

\[
\left|\mathbb E_{\mu_T}f-\mathbb E_{\nu_T}f\right|\le B_T,
\qquad
\mathbb E_{\mu_T}f\le
\min\{1,\mathbb E_{\nu_T}f+B_T\}.
\]

If different endpoints \(f,g\) are used and
\(\eta=\max_x|f(x)-g(x)|\), then

\[
\left|\mathbb E_{\mu_T}f-\mathbb E_{\nu_T}g\right|
\le\min\{1,B_T+\eta\}.
\]

**Proof.** For a signed difference of probability laws, the positive and
negative parts each have mass TV. Multiplying its coordinates by numbers in
\([0,1]\) bounds the absolute sum by that mass. This proves the common-loss
claim. For different losses, insert \(\mathbb E_{\nu_T}f\) and bound
\(\left|\mathbb E_{\nu_T}(f-g)\right|\le\eta\). All risks lie in
\([0,1]\), giving the caps.

The analogous statement for any protected history loss uses \(c_T\).
Conditional failure ratios require their selection denominators; this note's
bounds apply directly to unconditional event probabilities and bounded losses.

The receipt includes identical state laws with endpoint values one and zero.
Their state TV is zero while the endpoint risk gap is one, accounted for by
\(\eta=1\). It also includes an identical unsafe endpoint in both systems:
the gap is zero and the absolute risk remains one.

## 6. Sharp synthetic mechanisms

For a two-state system, let

\[
P=\begin{pmatrix}1-h&h\\0&1\end{pmatrix},\qquad Q=I,
\qquad \mu_0=\nu_0=(1,0).
\]

Here \(\varepsilon=h\), \(\delta(P)=1-h\), and
\(\delta(Q)=1\). Direct recursion gives

\[
d_T=b_T=c_T=1-(1-h)^T.
\]

The harmful state persists after the first injection. This provides equality in
both the state and history bounds. The receipt checks \(h=1/4\) through
horizon eight; unit tests include \(h=0\) and \(h=1\). The equality for
all finite horizons follows from the recursion, whose initial value is zero.

A second example uses the common kernel

\[
P=Q=\begin{pmatrix}1&0\\1/2&1/2\end{pmatrix},
\qquad \mu_0=(1,0),\quad\nu_0=(0,1).
\]

Every \(\varepsilon_t\) is zero, while \(d_T=2^{-T}\). The initial
states differ with certainty, so TV of the history that includes them is one
at every horizon. This example attains the initial contribution in T2.

## 7. Lean fidelity

The [Lean source](../../lean/FeedbackChannel/TrainingParanoia.lean) represents a
chronological affine schedule as a list of contraction/discrepancy pairs.
`budget_eq_weighted` proves its exact expansion, including the initial term,
for every finite list of real coefficients. `budget_mono` proves monotonicity
in the initial bound when contraction coefficients are nonnegative.

`BoundedChain` records a sequence satisfying the local affine inequalities.
The theorems `chain_le_budget` and `chain_le_weighted` compose those inequalities;
`chain_le_clipped` also uses an explicit hypothesis that the final discrepancy
is at most one. These support T2's uncapped expansion and final cap. The
step-by-step clipped recurrence is justified in the written proof.

The stochastic TV contraction in T1, the history coupling in T3, and the risk
inequalities in T4 have written proofs and exact finite checks here. Their
probability-kernel assumptions and derivations are outside this Lean file.
The [claim table](../../lean/CLAIMS.md) records that scope for each theorem.

## 8. Executable contract and audit scope

The [module](../../src/spiral_ln/evaluation_contamination_composition.py)
uses `Fraction` throughout and accepts exact integers, rational strings, and
fractions. Floats and Booleans are rejected by the shared finite-kernel layer.
It permits different finite state-space sizes at successive steps, with equal
paired dimensions at each time. Empty schedules preserve initial distance.

`composition_certificate` computes laws by matrix multiplication and records
each uniform row discrepancy, both contraction coefficients, and the bounds.
`trace_law` explicitly expands the state paths. Its `max_paths` guard checks the
product size before allocating the path enumeration; the default is 100,000.
This guard limits path count, while each stored path still has horizon-dependent
length. Matrix-based bounds avoid exponential path enumeration.

The [verifier](../../scripts/verify_evaluation_contamination_composition.py)
uses a separate product-of-transitions path oracle and independent TV sums.
Its finite comparison census covers:

| Domain | Comparisons |
| --- | ---: |
| Zero horizon; both initial laws on the half-probability grid | 9 |
| One step; all two-state kernels and starts on that grid | 729 |
| Two steps; all deterministic two-state kernels and grid starts | 2,304 |
| Two steps; all grid kernels with a common clean start | 6,561 |

For a two-state kernel, each row's first-coordinate probability is chosen from
\(\{0,1/2,1\}\), yielding nine kernels. The census checks every terminal
event in each comparison. Some comparisons occur in more than one census; the
reported count records executions across those declared domains. Additional
witnesses test resets, changed endpoints, row averages, and sharp accumulation.

The receipt binds the module, common kernel implementation, their tests,
verifier, this note, and the supporting Lean source by SHA-256. These hashes
identify the source used for the computation.
Physical coverage of a real model's state and feedback channels still requires
a separate interface audit and measured evidence.

```bash
PYTHONPATH=src python -m unittest tests.test_evaluation_contamination_composition -v
PYTHONPATH=src python scripts/verify_evaluation_contamination_composition.py
python scripts/check_receipts.py --only contamination_composition
```

For the repository's empirical preflight contract, this result's unit is a
declared finite comparison. The source census fixes its domain and contains
9,603 executed comparisons. Model roots and measured cases are zero. Its
contrast is TV between two specified interventions; the physical dose, sham
floor, confidence interval, and sampling power are inapplicable to exact
enumeration. The receipt uses every comparison in each declared finite domain,
and protected confirmation data remains unopened. The evidence verdict is
`exact finite domain`, with general bounds justified by the proofs above.
