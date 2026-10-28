# Qwenputer cross-repository work, 2026-10-28

This entry links the additive QPC-01 exact reference in
`src/spiral_ln/qwenputer_contract.py`, its tests and
`paper/qwenputer_contract.md`. Run its source-hashed receipt checker:

    PYTHONPATH=src python -m unittest discover -s tests -p 'test_qwenputer_contract.py' -v
    python scripts/verify_qwenputer_contract.py --check output/qwenputer_contract_v1.json

Repeat with `python -O`. The finite checks use no GPU, model weights, external
runtime or paid service. They do not execute a RISC-V ISA or verify Qwenputer.

## Work allocation

| Destination | Addition | Publication boundary |
|---|---|---|
| EvalMath | Exact transition oracle, trace checks, negative controls and receipt | Local module ready for publication; inspect Git commit for publication evidence |
| percolation-interp | QPR-01 scoring helpers and frozen prospective recovery protocol | Independent of existing E10 |
| Control-Harness | QPA-01 authenticated evidence and idempotent toy dispatch | Existing policy and BitAgent owners unchanged |
| Compactification-Theory | QPC-T01 abstraction and coordinate-change note | Initial HTTP 403 resolved; published in its own repository |
| BlueBeam | QPB-01 tamper matrix and offline log verifier | Content write denied with HTTP 403; staged in Control-Harness |

The Compactification-Theory note lives at
`research/qwenputer_v1/README.md` in that repository. Its initial permission error
was resolved before publication. BlueBeam remains a staged handoff in
Control-Harness, with no destination push. Existing interventional-compactification
work and the active EvalLang owner remain untouched.

Upstream write-ups were checked on 2026-10-28:
[Qwenputer](https://divagr.com/blog/qwenputer),
[recurrent-state reasoning](https://divagr.com/blog/hybrid-models-can-hide-reasoning-in-their-rnn-state),
and [compiled oversight](https://divagr.com/blog/building-oversight-tools-into-a-models-weights).
Numerical performance figures remain author reports. Source-code revision and
checkpoint hashes must be pinned before real-model collection; those runs and
full-repository CI were not performed by this patch. No Lean compilation is claimed.
