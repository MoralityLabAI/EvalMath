# EvalMath

Exact mathematics of evaluation feedback channels: what a training or evaluation loop can learn from
an eval it reads, when a reported score separates from the true one, and what an evaluator has to
publish for that gap to be bounded. Every result is exact arithmetic on declared quantities, carries an
evidence level, and is backed by a module, tests, a verifier that regenerates a receipt, and, where
formalized, a Lean 4 proof. No model, judge or grader is run anywhere in this repository.

**Start with [`paper/feedback_channel_findings.md`](paper/feedback_channel_findings.md)**, the synthesis.
It states each result, its evidence level and its Lean theorem, and lists what is open. A rendered copy
of the notes is published at <https://moralitylabai.github.io/EvalMath/>.

New: [capacity-sensitive leakage](paper/leak_capacity.md) certifies when a positive rational
feedback fibre produces an actual binary-record collision at declared cell capacities,
and computes exact collision probabilities with two independent finite algorithms.

New: [adaptive disclosure](paper/adaptive_disclosure.md) derives exact pathwise
feedback fibres, conditional collision reductions and an optimal-query recurrence.
For a uniform one-hot item on a line, k adaptive interval queries identify up to
2^k locations, versus 2k with fixed queries (within the number of locations).
The paper includes independent exact enumeration and the reproducible receipt.

New: [adaptive selection risk and continuation sufficiency](paper/selection_risk_continuations.md)
computes exact false-authorization risk after a feedback transcript, with an independently
enumerated two-query example rising from 5% pre-query risk to 7.5% under fixed
queries and 10% under adaptive queries. A finite procedural state machine
demonstrates why source-revocation identity and amendment chronology must
survive compression under its declared future-event contract.

New: [bounded covert-feedback risk](paper/covert_feedback_risk.md) establishes
an exact weighted maximum-coverage law for the information that a hidden message
can add after a public feedback transcript. With at most L hidden symbols,
false-authorization risk is at most L times public risk, a sharp bound. The
finite oracle distinguishes message capacity from the number of unseen
candidate outcomes inspected, and independently checks 210 hidden-message
cases and 80 complete adaptive query policies. A finite Bellman recurrence
optimizes public query choices and terminal covert messaging jointly.

New: [stochastic feedback and full-filtration ordering](paper/stochastic_full_filtration.md)
extends adaptive selection risk to rational noisy query responses and private
signals arriving before or after query selection. Two individually 5%-calibrated
events yield 7.5% post-selection risk with an early private signal, versus
6.25% with the same signal received after one public query. A separate exact
stopping-time witness demonstrates why one-step expectation validity must
be checked in the actor's full information filtration. The source-hashed
receipt verifies independent finite oracles; no physical acquisition claim
is made.

New: [validity under the actor's filtration](paper/dynamic_filtration_validity.md)
answers when a public e-process stays safe for decisions taken with private
information. Pointwise-valid factors on clean kernels are immune to any private
information about the latent state and to any information received after the
draw it concerns, but not to a pre-peek; factors calibrated only to the public
posterior are immune to nothing. Otherwise a private signal inflates the stopped
expectation by at most exp of its maximal leakage from the public transcript,
at most its alphabet size, with an exact closed form for the information value
and a per-process exact worst case. A source revocation recorded before its
source is viewed is free; recorded after, it is a post-selection with exact
cost (3/2 for one fair bit). The Bayesian belief state is not
revocation-sufficient: a static world needs one projective likelihood per
source, a Markov latent state the subset filters, none of which is redundant
for two sources. No Lean theorem, no acquisition-time attestation.

**New (2026-10-27):** [Cryptomania assumption audit](paper/cryptomania_assumption_audit.md)
tracks the five-world implication graph, evidence-gated ETH/3SUM/APSP hardness routes,
exact-rational Bayesian scenarios and an exact toy-#SAT control.
Reproduce with `PYTHONPATH=src python -m pytest -q tests/test_cryptomania_audit.py`
and `PYTHONPATH=src python scripts/verify_cryptomania_audit.py`.

Reviewers: see [`REVIEW.md`](REVIEW.md).

## Self-designed evaluation and FRC

The [HRC-FRC-01 extension](paper/frc_harmonic_self_evaluation.md) studies
recursive evaluation design, the lower-limit resource floor, exact hidden-trigger
oracle bounds and false-resonance training controls. Its spectral counterpart
is in `MoralityLabAI/RSITopology/HarmonicConsciousness`.

## Layout

| Path | Contents |
|---|---|
| `paper/` | The notes. Each states its results with evidence levels and the commands that reproduce them. |
| `src/spiral_ln/` | The exact modules, one per note (`evaluation_*.py`). Pure Python with `fractions.Fraction`. |
| `tests/` | One test file per module. |
| `scripts/` | One verifier per module (`verify_*.py`), each writing a receipt; `check_receipts.py` reruns them all. |
| `output/` | The committed receipts: every check, exact values, and the SHA-256 of the sources that produced them. |
| `configs/` | Manifests read by the atlas verifiers. |
| `lean/` | Lean 4 + Mathlib formalizations; [`lean/CLAIMS.md`](lean/CLAIMS.md) maps each to its claim with a fidelity label. |
| `site/` | The static site builder. |
| `docs/` | The journey map and the redacted session log of the investigation that produced this work. |

## Evidence levels

- *Algebraic identity*: proved for every parameter.
- *Finite verified example*: checked exactly on the enumerated cases only.
- *Synthetic mechanism result*: a property of a stated toy chain.
- *Cited*: taken from the literature and not reproved here.

A regularity seen on an exhaustive grid is never called a theorem. Twice in this work such a regularity
failed one size beyond the grid; the notes record both.

## Reproduce

```bash
python -m pip install -e ".[test]"
pytest -q                               # about 8 minutes
python scripts/check_receipts.py        # regenerates the fast receipts and compares
python scripts/check_receipts.py --all  # adds the two slow ones (about 40 minutes)
```

Lean (needs [elan](https://github.com/leanprover/elan); the Mathlib cache download is a few GB):

```bash
cd lean
lake exe cache get
lake build
lake env lean axioms_check.lean        # every listed theorem: propext, Classical.choice, Quot.sound only
```

`lean/wsl_direct.sh` is the author's script for a machine with a prebuilt Mathlib; Lake is the
portable route. The GitHub Actions workflow in `.github/workflows/verify.yml` runs all of the above on
every push.

## Provenance

This repository was spun out on 2026-10-14 from commit [`0de7073`](https://github.com/patrickdugan/Spiral/tree/0de707381f7b153d2a4b50719be76ea94a0e3ae4) of the branch `feedback-channel-and-rsi-atlas` of
[`patrickdugan/Spiral`](https://github.com/patrickdugan/Spiral), whose history holds the commit-by-commit
record. The Python package keeps its Spiral name, `spiral_ln`, so the source paths and hashes recorded
in every receipt, and the paths in the session log, stay valid. The design-calculus note, the game
testbed and the Prime Intellect atlas predate this programme and come from Spiral's `main`; where they
mention other Spiral modules (the hive lab, the identity attestation notes), those live in Spiral.


## External proof-fidelity case study

The [OpenAI ETH claim crosswalk](paper/proof_fidelity_openai_eth.md) compares the
headline, manuscript theorem and sharper tensor bounds with the actual Lean
endpoint and admitted comparator specification. It archives ten original
upstream sources at a pinned Git commit, including implementation-side runtime definitions and
all manuscript input files. The case has 29 substantive structural checks,
eighteen pytest cases, adversarial overclaim tests, and a source-hashed receipt.
The comparator signature match is syntactic; elaborated type equivalence requires Lean.

`python scripts/check_receipts.py --only openai_eth_fidelity`
rechecks the archive offline. This tests source integrity and claim fidelity;
it is not a mathematical referee report or a substitute for a full Lean rebuild.

## Cryptomania and bounded agency (research draft)

The [FAW-01 finite agency witness](paper/agency_without_cryptomania.md),
[FAW-02 persistence and regret proofs](paper/agency_persistence.md), and
[FAW-03 unknown-reliability Bayesian experiment design](paper/agency_unknown_reliability.md)
study resource-bounded decision-making without cryptographic hardness premises.
FAW-03 distinguishes one-label nonidentifiability from two-label channel
identification and derives a finite-horizon adaptive stopping policy that
improves reward by conserving calibration labels. These are synthetic exact
probability and paper arguments, without empirical model runs, Lean proofs or
conclusions about theological claims.
The associated [draft PR #16](https://github.com/MoralityLabAI/EvalMath/pull/16)
remains open for review.

## License

Apache License 2.0; see [`LICENSE`](LICENSE).
