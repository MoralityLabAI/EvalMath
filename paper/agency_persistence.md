# FAW-02: persistent bounded agency in every hypothetical cryptographic world

**Draft 0.1, 2026-10-27.** Follow-up to [FAW-01](agency_without_cryptomania.md). This note concerns an *operational* definition of agency: useful information acquisition, choice under a declared budget, repeated fresh challenges and independent scoring. It makes no claim to detect consciousness, moral agency or divine intention. Its complexity-world statement is a **conditional independence argument**, not a proof that all five worlds are consistent or that our universe belongs to one of them.

## 1. Protocol and information boundaries

At epoch \(t\ge 1\), independently sample a uniformly random polarity \(\theta_t\in\{0,1\}\). For each calibration or test item, sample an independent uniform state \(s\), a noise bit \(e\) with \(P(e=0)=q=3/4\), and show the signal \(y=s\oplus\theta_t\oplus e\). Calibration supplies the true state \(s\); held-out testing reveals only \(y\) before a prediction. Correct predictions earn unit reward. **Test labels, correctness, rewards and all other grader feedback are sealed until the epoch is complete.** The epoch's polarity is freshly sampled, so past-epoch calibration has no predictive advantage on the new polarity.

Let \(n_t=t+1\) denote the number of independent held-out decisions. The **sufficient fixed schedule** buys

\[
m_t=5b_t,\qquad b_t=\lceil\log_2(t+1)\rceil=\operatorname{bit\_length}(t),\]

labeled calibration examples, each costing \(c=1/32\) reward units. The agent infers \(\theta_t\) by a majority vote over the observed calibration polarities \(s_i\oplus y_i\) (ties select 0), and predicts \(\hat s_j=y_j\oplus\hat\theta_t\) for each held-out item. The environment and success law are known; the *fresh* polarity and trial noises are not.

An agent with no current-epoch labels has success probability \(1/2\) on every test prediction despite its full earlier history. A polarity-informed oracle attains \(3/4\). Let \(A_m(q)\) denote the exact fresh-test success from FAW-01, and let \(p_m=1-\alpha_m(q)\) be the polarity inference error. For \(q=3/4\),

\[A_m(3/4)=3/4-\tfrac12p_m,\qquad r_m=3/4-A_m(3/4)=\tfrac12p_m.\]

**Information caveat.** Exposing any test reward during the epoch changes the game and may let the agent learn the polarity after testing starts. Keeping a fixed polarity across epochs similarly makes past labels informative. Both changes invalidate the stated chance baseline. This is the same distinction between player-facing feedback and post-play measurement emphasized in the parent EvalMath testbed.

## 2. The logarithmic-label theorem

**Theorem FAW-02/A (algebraic proof, not Lean formalized).** In the stated protocol, the scheduled agent's expected cumulative oracle regret \(R_T\) and total calibration labels \(L_T\) through epoch \(T\ge1\) obey

\[
R_T\le T/2,\qquad L_T\le5T\lceil\log_2(T+1)\rceil.
\]

There are exactly \(D_T=\sum_{t=1}^T(t+1)=T(T+3)/2\) held-out decisions. Consequently,

\[
\boxed{\frac{R_T}{D_T}\le\frac1{T+3}},\qquad
\boxed{\frac{L_T}{D_T}\le\frac{10\lceil\log_2(T+1)\rceil}{T+3}}.
\]

Both right-hand sides tend to zero. The error guarantee is population-expectation regret under the declared stochastic law, with independent *epoch* polarities and feedback sealing. It is neither pathwise regret nor a high-probability concentration theorem for the realized trajectory.

*Proof.* If \(K\) of \(m\) calibration bits are correctly polarized, then \(K\sim\mathrm{Binomial}(m,3/4)\). An erroneous majority requires \(K\le m/2\), including the possibility of an even-size tie. Markov's inequality applied to \(3^{-K}\) gives

\[
\begin{aligned}
p_m&\le P(K\le m/2)\\
&\le 3^{m/2}\,\mathbb E[3^{-K}]\\
&=3^{m/2}\left(\tfrac34\cdot\tfrac13+\tfrac14\right)^m\\
&=\left(\tfrac{\sqrt3}{2}\right)^m.
\end{aligned}
\]

The last expression is bounded using only an integer certificate:

\[
\left(\tfrac34\right)^5=\frac{243}{1024}\le\frac14.
\]

For \(m=m_t=5b_t\), squaring the upper bound yields \(p_{m_t}^2\le(243/1024)^{b_t}\le(1/4)^{b_t}\). Thus \(p_{m_t}\le2^{-b_t}\le1/(t+1)\). Each epoch's regret is at most \((t+1)\cdot p_{m_t}/2\le1/2\). Summing gives \(R_T\le T/2\). The budget bound follows from monotonicity of integer bit length. Dividing by the exact \(D_T\) gives both displayed normalized inequalities. \(\square\)

### Reward after calibration expense

Define the net gain over the uncalibrated chance policy by

\[G_T=\sum_{t=1}^T n_t\big(A_{m_t}(3/4)-1/2\big)-cL_T.\]

Because \(G_T=D_T/4-R_T-cL_T\), the theorem yields

\[
\frac{G_T}{D_T}\ge\frac14-\frac1{T+3}-\frac{10c\lceil\log_2(T+1)\rceil}{T+3},\quad
\lim_{T\to\infty}\frac{G_T}{D_T}=\frac14.
\]

The upper limit follows from the oracle's accuracy ceiling and nonnegative label cost. The calibration fraction and its normalized cost vanish while the per-test net gain over the chance policy approaches a positive constant.

**Proposition FAW-02/B (positive net gain every epoch).** At the specified \(c=1/32\), even each *individual* epoch has strictly positive expected net gain over chance. The epoch-level lower bound is

\[g_t\ge\frac{8(t-1)-5b_t}{32}.\]

For \(t\ge3\) this lower bound is positive: the integer numerator equals 6 at \(t=3\), and each increment in \(t\) raises it by \(8-5(b_{t+1}-b_t)\ge3\). The two exceptions, \(t=1,2\), have exact positive net gains \(123/512\) and \(95449/262144\), verified by finite binomial sums. The proof is valid for all positive integers \(t\), while the computer enumerates only finitely many examples.

## 3. A bounded agent that chooses its calibration budget

A second agent solves the exact finite planning problem

\[
m_t^*\in\operatorname*{argmax}_{0\le m\le m_t}
\big[n_t\big(A_m(3/4)-\tfrac12\big)-cm\big].
\]

In a tie, it selects the smallest number of labels. This is an agent choosing its *evaluation acquisition budget* under a stated utility function, with the stochastic law supplied in advance. It is not autonomous task discovery, training-weight editing, or evidence of actual RSI.

**Theorem FAW-02/C (cost-optimized agent).** Let \(R_T^*\) be this agent's cumulative expected oracle regret. For each epoch, comparing the chosen policy against the feasible scheduled policy gives

\[n_t r_{m_t^*}+cm_t^*\le n_t r_{m_t}+cm_t\le\tfrac12+cm_t.\]

Since costs are nonnegative, summing yields

\[
\boxed{\frac{R_T^*}{D_T}\le\frac1{T+3}+\frac{10c\lceil\log_2(T+1)\rceil}{T+3}\longrightarrow0.}
\]

Its expected net value is at least the fixed schedule's value at *every epoch* by construction, so Proposition B gives a strictly positive epoch-level net advantage for the specified cost. The planner's exact finite search requires at most \(m_t+1\) candidate budgets and rational binomial calculations; the theorem charges for purchased labels, and it leaves planning computation outside the reward accounting.

## 4. A fixed acquisition cap prevents vanishing regret

**Theorem FAW-02/D (nonadaptive within-epoch lower bound).** Let \(q\in(1/2,1)\) be fixed and rational. Suppose every epoch starts with a fresh fair polarity, the number of calibration labels \(m_t\le M\) is chosen before seeing that epoch's calibration data, and rewards stay sealed. Any polarity inference rule based on those labels has oracle gap at least

\[
\boxed{\epsilon(q,M)=(2q-1)\min\{\tfrac12,(1-q)^M\}>0.}
\]

*Proof.* For \(m=0\), the Bayes error in the fair hidden polarity is \(1/2\). For \(m\ge1\), majority is Bayes-optimal in the symmetric binary channel. The event that *every* observed calibration polarity is flipped has probability \((1-q)^m\), and majority chooses the wrong polarity on that event. Thus its Bayes error is at least \((1-q)^m\ge(1-q)^M\). Any competing decoder has Bayes error at least that of majority. The held-out correctness gap against an informed oracle is \((2q-1)\) times polarity error. Past epochs are independent of the fresh polarity, so choosing a sample count using old-epoch information leaves the bound intact. \(\square\)

The lower bound quantifies an **acquisition lower bound under a fixed label cap**. Adaptive stopping based on current-epoch labels, a changed observation process, long-lived polarity, and revealed test rewards need independent analysis. It is a statement about statistical information and bounded decisions; it does not imply NP hardness, one-way functions or public-key encryption.

## 5. Evidence ledger and falsifiers

| Claim | Evidence level | Boundary |
|---|---|---|
| FAW-02/A: vanishing expected regret with logarithmic labels | Algebraic proof above; finite exact fixture | Assumes refreshed polarity and sealed rewards |
| FAW-02/B: positive net reward in each epoch | Algebraic inequality + exact first two cases | Specific \(q=3/4\), \(c=1/32\), \(n_t=t+1\) |
| FAW-02/C: cost-optimized budget retains a vanishing regret bound | Algebraic comparison + exact finite optimizer | Optimizer knows the reward law and has restricted choices |
| FAW-02/D: fixed nonadaptive label cap incurs positive regret | Algebraic lower bound + exact controls | Within-epoch adaptive sampling outside this proof |
| Model survives Algorithmica, Heuristica, Pessiland, Minicrypt and Cryptomania as a conditional toy construction | Independence from cryptographic assumptions | Does not establish the consistency or truth of any world |
| Any implication from persistent *functional* progress to divine enjoyment of struggle | Philosophical bridge axiom | No mathematical or observational proof supplied |

Three pre-registered failure checks alter the protocol. Under \(q=1/2\), calibration yields no population advantage. If \(\theta_{t+1}=\theta_t\), information from a previous epoch transfers, changing the no-current-calibration baseline. If held-out success or labels are leaked during the epoch, the observation channel changes and the original expectation formula needs revision. The verifier checks the first two with exact rational controls; the last is excluded by the declared protocol.

The five-world context follows [Impagliazzo's interview](https://www.quantamagazine.org/the-researcher-who-explores-computation-by-conjuring-new-worlds-20240327/) and the definitions in [the Sorbonne quantum information explainer](https://qics.sorbonne-universite.fr/en/impact-quantum-computers-impagliazzos-five-worlds). The separate hierarchy result \(P\subsetneq EXP\) used in FAW-01 is explained in [UIC lecture notes](https://www.cs.uic.edu/~block/courses/cs505-spring2025/lecture-07.html). FAW-02 relies only on the direct binomial derivations above.

## Reproduce

```sh
PYTHONPATH=src python -m pytest -q tests/test_agency_worlds.py tests/test_agency_persistence.py
PYTHONPATH=src python scripts/verify_agency_persistence.py --output /tmp/agency_persistence.json
python scripts/check_receipts.py --only agency_persistence
```

The receipt records source hashes and exact rational finite evidence. It is regenerated, never edited by hand. Every theorem here is a **paper proof**, and no Lean build or empirical AI experiment is claimed. The PR remains a draft pending independent review of the quantifiers and adversarial protocol edits.
