# EvalMath

Exact mathematics of evaluation feedback channels: what a training or evaluation loop can learn from
an eval it reads, when a reported score separates from the true one, and what an evaluator has to
publish for that gap to be bounded. Every result is exact arithmetic on declared quantities, carries an
evidence level, and is backed by a module, tests, a verifier that regenerates a receipt, and, where
formalized, a Lean 4 proof. No model, judge or grader is run anywhere in this repository.

**Start with [`paper/feedback_channel_findings.md`](paper/feedback_channel_findings.md)**, the synthesis.
It states each result, its evidence level and its Lean theorem, and lists what is open. A rendered copy
of the notes is published at <https://moralitylabai.github.io/EvalMath/>.

Reviewers: see [`REVIEW.md`](REVIEW.md).

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
endpoint and admitted comparator specification. It archives seven original
upstream sources at a pinned Git commit and includes 22 structural checks,
eleven pytest cases, adversarial overclaim tests, and a source-hashed receipt.

`python scripts/check_receipts.py --only openai_eth_fidelity`
rechecks the archive offline. This tests source integrity and claim fidelity;
it is not a mathematical referee report or a substitute for a full Lean rebuild.

## License

Apache License 2.0; see [`LICENSE`](LICENSE).
