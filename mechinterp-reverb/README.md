# Mechinterp Reverb: Looped-Transformer BPD in EvalMath

This folder holds a **source-identical** snapshot of Behavioral Parameter Decomposition (BPD) from `MoralityLabAI/LoopedTransformers`, commit [`fb7b1e9f93a2`](https://github.com/MoralityLabAI/LoopedTransformers/commit/fb7b1e9f93a2c6ee810e5ae2a2a6a1892c4f3d73), proposed in [PR #96](https://github.com/MoralityLabAI/LoopedTransformers/pull/96). The 29 original BPD files sit under `mechinterp/bpd/`. [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) records every source Git blob ID for exact replay. The package prefix `mechinterp/` is kept so the original Python imports work without rewriting code.

The separate VPD mirror remains on its earlier snapshot because this session's GitHub integration rejected a branch write there. EvalMath is the writable destination for BPD and its reviewed methods. Source code and historical results are preserved; new scientific experiments require independent controls.

## Focused local validation

From the **EvalMath repository root**, install PyTorch and pytest in a suitable Python environment, then run:

```bash
PYTHONPATH=mechinterp-reverb python -m pytest -q mechinterp-reverb/mechinterp/bpd/tests/test_bpd_fable_preflight.py
python -m compileall -q mechinterp-reverb/mechinterp/bpd
```

The source-only preflight previously passed **5/5** using the same BPD source blobs in an independent EvalMath runner: [run 43717985878](https://github.com/MoralityLabAI/EvalMath/actions/runs/43717985878). The workflow in this repository rechecks the mirror's Git content hashes and repeats the CPU preflight.

Some original end-to-end BPD tests and adapters import `mechinterp.loopscope01` and `mechinterp.loopscope02` from LoopedTransformers, and full pretrained runs require those original dependencies and checkpoints. This mirror includes the BPD adapters and tests, while deliberately leaving unrelated LoopedTransformers packages out.

## Review status

See [Fable amendments](mechinterp/bpd/docs/amendments_2026-11-15_fable.md) for corrected `max` pooling, local fragility indexing, same-pass donor-activation item contrasts, descriptive rotation rank tests and B4 sham controls. The full [positive-control history](mechinterp/bpd/docs/positive_control_history.md) retains dense-control failures. The [original registration](mechinterp/bpd/docs/registration.md) remains available for audit. The exact baseline and models have not been retrained by this transfer, and a neural BPD mechanism-separation claim is still open.
