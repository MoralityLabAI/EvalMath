# CPF-05/06 continuation ledger

Private material (seeds, gold, call ledgers, server logs) lives in `%USERPROFILE%\cpf-private`, outside the repository. Committed here: panel digests and seed commitments (`*_generation_manifest.json`), the frozen run config (`configs/cpf_suite_models.json`) and preflight receipts.

## State on 2026-11-25

| Stage | Bonsai 2 27B (PTQ1_0) | Inky mini varloop (IQ4_NL) |
|---|---|---|
| Backend probe | done: 0 cap violations, usage on every call, 29.6 tok/s decode, 6.3 GB VRAM | three launch configurations measured at 0.65 to 2.6 tok/s under host-RAM pressure; no ledger calls |
| Dev preflight, 48 roots × 4 stages | done, 192/192 calls (`dev48_preflight_bonsai.json`) | not started |
| Primary panel, 240 roots × 4 stages | not started; GPU watcher armed | not started |
| Scoring, analysis, Data Goblin ledger export | after both models complete | after both models complete |

Blockers met during the run:

1. Host RAM. Other jobs held about 41 of 47 GB. Inky keeps expert layers on the CPU and paged at up to 21,400 pages/s.
2. GPU. From 10:11 another session's Inkling-2-Mini LoRA server (port 18320) held 10.25 GB VRAM. The admission check in `cpf_serve.ps1` refuses to load while any other compute process holds the GPU.

## Resume commands (PowerShell, from the repository root)

Each command is idempotent. It starts the model if it is not already serving, then resumes the ledger from the last fsynced call.

```powershell
powershell -File scripts/cpf_stage.ps1 -Model bonsai -Panel primary240
```

```powershell
$env:CPF_INKY_CPU_MOE = '8'; powershell -File scripts/cpf_stage.ps1 -Model inky -Panel dev48 -Probe
```

```powershell
powershell -File scripts/cpf_stage.ps1 -Model inky -Panel primary240
```

Score once, after both models have completed the primary panel:

```powershell
$env:PYTHONPATH = "src;scripts"; $P = "$env:USERPROFILE\cpf-private\primary240"
python scripts/analyze_cpf_suite.py --prompts $P\prompts.jsonl --gold $P\gold.jsonl --generation-manifest $P\manifest.json --calls $P\calls.jsonl --out $P\analysis.json
```

Then export the quarantined evaluation corpus:

```powershell
python scripts/export_cpf_datagoblin.py ledger --prompts $P\prompts.jsonl --gold $P\gold.jsonl --generation-manifest $P\manifest.json --calls $P\calls.jsonl --custody sealed_eval --fingerprints "$env:USERPROFILE\cpf-private\fingerprints.json" --out "$env:USERPROFILE\cpf-private\goblin_primary240"
```

After scoring, publish the dev and primary seeds and gold so the panels can be reproduced against the committed commitments.

## Ordering note

Bonsai's primary panel may run before Inky's dev preflight, because Inky was blocked by hardware. The run config, including Inky's entry, was frozen before any primary call, and no primary output is scored until both models finish. If Inky's preflight forces a config change, the primary ledger manifest check fails closed. Bonsai's primary panel would then be re-collected under the new config, with the old ledger kept and labelled.
