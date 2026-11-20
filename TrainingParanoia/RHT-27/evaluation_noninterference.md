# RHT-27: Evaluation noninterference through permitted feedback

**Evidence:** algebraic identities and bounds for finite probability kernels, with exact finite verified examples. **Receipt:** `RHT-27-v1`, 14 checks, 625 rational intervention families, 256 deterministic families and 5,625 common-postprocessing cases. **Empirical status:** zero new model observations; no training or confirmation sample is used.

This result specifies which effects an evaluation may pass to the next run. An externally fixed map extracts permitted feedback from a transcript. The boundary then has to erase the transcript's remaining influence on the declared downstream state. The calculation reports the size of a violation and a transcript pair that witnesses it.

## 1. The causal interface

Let \(E\) be a nonempty finite set of admissible evaluation transcripts, \(S\) a nonempty finite input-state space, and \(X\) a nonempty finite output-state space. Choose a permitted-feedback map

\[
\phi:E\longrightarrow Z,\qquad Z=\phi(E).
\]

The map and the vocabulary must be registered outside the evaluated agent. Choosing \(\phi\) after inspecting the mechanism can declare every observed leak permissible. Each transcript \(e\) indexes a row-stochastic kernel

\[
K_e(s,x)=\Pr[X=x\mid\operatorname{do}(E=e),S=s;\mathcal I].
\]

Here \(\mathcal I\) fixes the task distribution, intervention boundary, external program, and exogenous randomness law. Both interventions use the same initial state \(s\). The finite model supplies these kernels directly. Fitting them from selected observational transcript conditionals requires a separate causal argument.

The output state must include everything that can affect the later computation covered by the claim. This can include weights, optimizer state, files, retrieval records, caches, pending updates, evaluator state and retained messages. A coordinate that will be read later belongs in the state even when the visible workspace has been cleared. A joint emitted action can be included in \(X\); a later reset cannot erase its occurrence. RHT-28 treats that trace issue explicitly.

Define the residual diameter within the permitted-feedback fibres:

\[
\varepsilon_\phi(K)
=\max_{\substack{e,e'\in E:\phi(e)=\phi(e')\\s\in S}}
\operatorname{TV}(K_e(s,\cdot),K_{e'}(s,\cdot)),
\qquad
\operatorname{TV}(p,q)=\frac12\sum_x|p(x)-q(x)|.
\]

Pairs with \(e=e'\) contribute zero. The implementation enumerates distinct unordered pairs and reports zero when every fibre is a singleton. Its audit includes the number of pairs, the number of state rows compared, the number of nontrivial fibres, and the fraction of transcripts lying in those fibres. These are coverage diagnostics. They do not validate the chosen feedback policy.

For a maximizing pair, the event

\[
B=\{x:K_e(s,x)>K_{e'}(s,x)\}
\]

attains the positive probability gap \(\varepsilon_\phi(K)\). The receipt records this witness and the input state at which it occurs.

## 2. Exact factorization

**T1, algebraic identity.** The following conditions are equivalent:

\[
\varepsilon_\phi(K)=0
\quad\Longleftrightarrow\quad
\exists\,\overline K:Z\to\operatorname{Kern}(S,X)
\text{ such that }K_e=\overline K_{\phi(e)}\text{ for every }e\in E.
\]

**Proof.** If the factorization exists, two transcripts sharing a feedback value have identical rows. Conversely, choose one representative \(e_z\) from each nonempty fibre and define \(\overline K_z=K_{e_z}\). Zero diameter makes every row in that fibre equal to the representative. Restricting \(Z\) to the attained image avoids assumptions about unused feedback values. This proof also covers a one-transcript domain and one-state spaces.

The executable `factorization()` returns those representative kernels and rejects a family with nonzero diameter. The factorization permits learning from the allowed value. The finite learning fixture has four transcripts with two feedback values; all state rows update to the bit conveyed by the permitted score. Altering the transcript's extra hook leaves the update law unchanged.

**Scope.** The same-state quantifier matters. If two earlier histories already produce different retained states, T1 alone does not identify their later behavior. RHT-28 adds the initial state discrepancy and propagates it through future kernels.

## 3. An approximate permitted-only reference

For each \(z\), choose fixed weights \(w_z\) forming a probability law on \(\phi^{-1}(z)\), and define

\[
\overline K_z(s,\cdot)
=\sum_{e'\in\phi^{-1}(z)}w_z(e')K_{e'}(s,\cdot).
\]

These weights are shared by all transcripts in the fibre. Define the reference residual

\[
r(K,\overline K)=\max_{e,s}
\operatorname{TV}(K_e(s,\cdot),\overline K_{\phi(e)}(s,\cdot)).
\]

**T2, algebraic bound.** Every such mixture satisfies

\[
\tfrac12\varepsilon_\phi(K)\le r(K,\overline K)
\le\varepsilon_\phi(K).
\]

**Proof.** Convexity of the absolute-value sum gives

\[
\operatorname{TV}(K_e(s,\cdot),\overline K_z(s,\cdot))
\le\sum_{e'}w_z(e')\operatorname{TV}(K_e(s,\cdot),K_{e'}(s,\cdot))
\le\varepsilon_\phi(K).
\]

For any common reference, the triangle inequality bounds a same-fibre pair distance by twice the largest residual. Taking the maximum proves the lower bound. A representative is a valid degenerate mixture. For a fibre containing exactly two kernels, their midpoint has residual exactly half their row diameter; the census checks this identity for all 625 rational two-state families.

The implementation also accepts an explicitly supplied `PermittedSimulator`. Its residual is computed exactly. An arbitrary supplied reference can be farther away than \(\varepsilon_\phi(K)\); the upper bound above uses the mixture construction. The API does not claim that its default representative solves a minimax optimization.

## 4. Common downstream computation

Let \(H:X\to Y\) be the same row-stochastic continuation for every transcript. Its Dobrushin coefficient is

\[
\delta(H)=\max_{x,x'}\operatorname{TV}(H(x,\cdot),H(x',\cdot)).
\]

**T3, algebraic bound.**

\[
\varepsilon_\phi(KH)\le\delta(H)\varepsilon_\phi(K)
\le\varepsilon_\phi(K).
\]

**Proof.** For finite probability laws \(p,q\), put \(d=\operatorname{TV}(p,q)\). When \(d=0\), the claim follows from equality. Otherwise write the positive and negative parts of \(p-q\) as \(d u\) and \(d v\), where \(u,v\) are probability laws. Then

\[
\operatorname{TV}(pH,qH)=d\operatorname{TV}(uH,vH)
\le d\sum_{x,x'}u(x)v(x')\operatorname{TV}(H(x,\cdot),H(x',\cdot))
\le d\delta(H).
\]

Apply this inequality to every same-fibre pair and state. The argument also covers a single input state for \(H\), whose coefficient is zero.

The executable `postprocess()` composes a common channel. A continuation that reads the original transcript through a second path can have a different kernel in each arm. It falls outside this theorem. RHT-28 bounds unequal continuation kernels under separately supplied row-discrepancy limits.

## 5. Turning residual influence into a risk bound

Let \(\ell:X\to[0,1]\) be a fixed, externally defined loss. Given a permitted-only reference, define

\[
b=\max_{z\in Z,s\in S}\mathbb E_{\overline K_z(s,\cdot)}[\ell],
\qquad r=r(K,\overline K).
\]

**T4, algebraic bound.**

\[
\max_{e,s}\mathbb E_{K_e(s,\cdot)}[\ell]
\le \min(1,b+r).
\]

**Proof.** For each row, the difference in expectations of a \([0,1]\)-valued function is at most TV. The reference expectation is at most \(b\); taking the maximum gives the claim. The finite sharp fixture has reference unsafe probability \(1/8\), residual \(1/4\), and actual unsafe probability \(3/8\).

This is a guarantee relative to a declared loss and reference. The `risk_certificate()` function computes the maximum over every permitted feedback value, so an attacker who can choose among those values is included in that reference maximum. Replacing it by an average benign-feedback risk would require an assumption about the feedback source. The boundary's feedback type, verifier, authority and loss semantics remain external design obligations.

## 6. Finite failures of broader claims

| Proposed inference | Exact witness | Result |
|---|---|---|
| Zero fibre diameter establishes safety | Two feedback values deterministically select output zero or output one; both have duplicate transcripts. Declare output one unsafe. | Diameter and reference residual are zero; worst-case unsafe probability is one. |
| Encoding the full transcript as permitted feedback gives a useful test | Assign a different feedback value to each transcript, including transcripts with opposite deterministic outputs. | Zero pairs are compared; the API reports identity-feedback vacuity and coverage zero. |
| Checking a nominal initial state covers later histories | Two kernels agree at input state zero and disagree deterministically at state one. | Nominal-start TV is zero; uniform row diameter is one. |
| Clearing the visible artifact after learning removes its influence | State is \((a,p)\), the update sets \(p\leftarrow p\lor a\), and the final reset sets \(a\leftarrow0\). Compare a clean write with a hook write. | Full-state diameter is one; observing only the final artifact yields diameter zero. |
| The same reset works regardless of timing | Move that artifact reset before the declared update. | The two intervention kernels coincide at every input state, including states whose policy bit was already one. |
| Observational transcript conditioning measures the intervention | A uniform latent bit \(U\) determines both observed transcript \(E=U\) and action \(A=U\). Under \(\operatorname{do}(E=e)\), the state \(U\) stays fixed. | Observational conditional TV is one; the two intervention kernels are identical and have diameter zero. |
| An erased output stays independent under every continuation | A later process reads a second copy of the original transcript and selects one of two opposite deterministic output kernels. | The common-channel premise fails; diameter rises from zero to one. |

The reset example uses a fully specified synthetic update. Its zero diameter after an early reset concerns the additional transcript influence. Existing poisoned policy state remains in the system, which T4 accounts for through reference risk.

## 7. Executable scope and reproduction

The shared finite-kernel layer requires exact integers, rational strings or `Fraction` values, and rejects floats and Boolean probabilities. Kernel shapes, law normalization, transcript uniqueness and feedback coverage are checked. A simulator must cover exactly the attained feedback vocabulary, and its state spaces must match the intervention family.

The verifier independently computes TV by enumerating every output event. It checks all 625 pairs of two-state Bernoulli kernels with probabilities on the quarter grid, then applies all nine two-state continuation kernels with probabilities in \(\{0,1/2,1\}\). A second census checks all 256 deterministic mechanisms on four transcripts, two feedback fibres and two input states. The unit tests exercise malformed tables, omitted states, singleton and partial fibres, reset timing, confounding, and the sharp risk bound.

```bash
python -m pytest -q tests/test_evaluation_noninterference.py
PYTHONPATH=src python scripts/verify_evaluation_noninterference.py
python scripts/check_receipts.py --only noninterference
```

The receipt records the source digest of this note, the implementation, the common finite-kernel primitives, the tests and the verifier. Exact finite checks establish behavior on the declared tables. Applying the theorem to a neural training pipeline requires evidence that the implemented boundary enforces the declared state and feedback interface. Statistical preflight becomes applicable when empirical kernels or causal effects are estimated; this finite proof exercise has no independent-root sample or power claim.

## 8. Lean statement fidelity

[`TrainingParanoia.lean`](../../lean/FeedbackChannel/TrainingParanoia.lean) proves the equality-level factorization through the attained feedback image as `fibreConstant_iff_factors`. Its output type is arbitrary, so an instantiated output can be a probability law. The equivalence between zero TV and equality of laws is supplied by T1's finite argument and the executable checks.

`fibreConstant_postprocess` proves preservation of exact fibre equality under a common downstream map. Its statement does not include a Dobrushin coefficient or an approximate TV bound. The quantitative claim remains T3 with its mathematical proof and finite checks. `identity_feedback_vacuous` and `unsafe_permitted_feedback` formalize the corresponding exact counterexamples. The repository's [Lean claim registry](../../lean/CLAIMS.md) records these scopes, and its axioms check covers the named declarations.
