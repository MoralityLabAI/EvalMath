#!/usr/bin/env python3
"""Write gpu_resource_receipt.json and run_manifest.json for the RHC-03 local-5080 run.

Resource figures are computed from the sampled ``resource/*_gpu_samples.jsonl``;
the run facts (model file hash, server flags, commits) are those observed on
2026-11-10 and are recorded here as data.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('results/rhc03_local_5080')
TOTAL_MIB = 15915
CEILING_MIB = 8192


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes().replace(bytes([13, 10]), bytes([10]))).hexdigest()


def phase(name: str) -> dict:
    rows = [json.loads(x) for x in (OUT / 'resource' / f'{name}_gpu_samples.jsonl').read_text().splitlines()]
    timing = json.loads((OUT / 'resource' / f'{name}_timing.json').read_text())
    srv = [r['server_mib'] for r in rows if r.get('server_mib') is not None]
    util = [r['server_util'] for r in rows if r.get('server_util') is not None]
    gpu = [r['gpu_util'] for r in rows if r.get('gpu_util') is not None]
    used = [r['gpu_used_mib'] for r in rows if r.get('gpu_used_mib')]
    span = rows[-1]['t'] - rows[0]['t']
    return {
        'samples': len(rows), 'mean_sample_interval_seconds': round(span / max(1, len(rows) - 1), 2),
        'wall_seconds': timing['wall_seconds'], 'server_busy_seconds': timing['busy_seconds'],
        'request_duty_cycle': round(timing['busy_seconds'] / timing['wall_seconds'], 3),
        'inference_server_peak_vram_mib': max(srv), 'inference_server_mean_vram_mib': round(sum(srv) / len(srv), 1),
        'inference_server_mean_gpu_util_percent': round(sum(util) / len(util), 2),
        'inference_server_max_sampled_gpu_util_percent': max(util),
        'whole_gpu_mean_util_percent_including_other_jobs': round(sum(gpu) / len(gpu), 2),
        'whole_gpu_peak_used_mib_including_other_jobs': max(used),
        'min_free_vram_mib_while_running': TOTAL_MIB - max(used),
        'power_cap_w_observed': sorted({r['gpu_power_cap_w'] for r in rows if 'gpu_power_cap_w' in r}),
        'ceiling_breach': timing['ceiling_breach'], 'runner_failures': sum(1 for r in timing['requests'] if r['runner_returncode'] != 0)}


cal, hold = phase('calibration'), phase('holdout')
peak = max(cal['inference_server_peak_vram_mib'], hold['inference_server_peak_vram_mib'])
receipt = {
    'schema': 'rhc03_local_5080_gpu_resource_receipt_v1', 'date_utc': '2026-11-10',
    'gpu': {'name': 'NVIDIA GeForce RTX 5080 Laptop GPU', 'driver': '577.05', 'total_vram_mib': TOTAL_MIB, 'shared_with_other_jobs': True,
            'power': 'mains, enforced limit 150 W'},
    'budget': {'vram_ceiling_mib': CEILING_MIB, 'min_free_vram_target_mib': 8192, 'gpu_util_target_percent': 50,
               'concurrency': 1, 'max_output_tokens': 180, 'temperature': 0},
    'enforcement': 'driver script sampled vramorama ps and nvidia-smi about every 3-4 s and was set to kill the inference server if its VRAM exceeded the ceiling; the kill path never fired',
    'calibration': cal, 'holdout': hold,
    'peak_inference_server_vram_mib': peak, 'peak_vram_within_ceiling': peak <= CEILING_MIB,
    'free_vram_floor_mib': min(cal['min_free_vram_mib_while_running'], hold['min_free_vram_mib_while_running']),
    'free_vram_target_met': min(cal['min_free_vram_mib_while_running'], hold['min_free_vram_mib_while_running']) >= 8192 - 0,
    'utilisation_note': 'The 50% target is met by construction of the request duty cycle (about 0.50) and by the server process mean GPU utilisation; whole-GPU utilisation includes two other sessions\' jobs and is not attributable to this run.',
    'measurement_limits': 'Per-process VRAM is the vramorama/WDDM figure and the KV cache is allocated at server start, so the server peak is flat; sampling interval is seconds, not milliseconds, so very short transients are not captured.'}
(OUT / 'gpu_resource_receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf8')

files = {str(p.relative_to(OUT)).replace('\\', '/'): sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()
         and p.name not in ('run_manifest.json', 'experiment_report.md')}
manifest = {
    'schema': 'rhc03_local_5080_run_manifest_v1', 'date_utc': '2026-11-10', 'protocol': 'configs/rhc03_prereg_v1.json',
    'protocol_modified': False, 'oracle_vault_published': False,
    'source': {'evalmath_pr': 'https://github.com/MoralityLabAI/EvalMath/pull/30', 'evalmath_branch': 'feat/rhc01-reward-hacking-bootstrap',
               'evalmath_base_commit': '3006ac6ae4ae45173df5e9cf8fa8c1ea35ce1988',
               'control_harness_commit': 'fe991510f8c9acc6ab4ffd91958c0a89fd4bcb29',
               'catalog_git_blob_sha': '3d362f45a7dc0a5dd5601f91975990f93ad5b7ff', 'scorer_git_blob_sha': '7665c6c28d1e015d9da32eac76c41e0b203a6658',
               'blob_hashes_verified_before_run': True, 'parity_all_matched': True, 'parity_cases': 420},
    'model': {'identity': 'Qwen3.5-4B (unsloth GGUF), instruct chat template', 'server_alias': 'qwen3.5-4b-ud-q4_k_xl',
              'file': 'Qwen3.5-4B-UD-Q4_K_XL.gguf', 'file_bytes': 2912109728,
              'file_sha256': 'b252c5610a42ca82d20fe2a12813e9d069eed89292907e26c783eeb0bc961bc7',
              'quantization': 'UD-Q4_K_XL (Unsloth dynamic 4-bit; the registered Q4_K_M target was not installed and nothing was downloaded)',
              'source_repo': 'unsloth/Qwen3.5-4B-GGUF', 'weights_changed': False, 'lora': None},
    'server': {'binary': 'PrismML llama.cpp fork llama-server build 10743 (commit adfffbe41), CUDA, Windows',
               'launcher_sha256': 'd5897802f2bc893214fa86abf9b7276bf409f5f661751c4ef0e9981443a005f6',
               'flags': '-ngl 99 -c 4096 -np 1 -fa on --reasoning off --no-webui --host 127.0.0.1 --port 18101',
               'context_tokens': 4096, 'parallel_slots': 1, 'thinking': 'off (server-side --reasoning off; the request body is the registered one)',
               'loopback_only': True},
    'inference_settings': {'temperature': 0, 'max_output_tokens': 180, 'stream': False, 'requests_in_flight': 1,
                           'repetitions_per_task': 1, 'client_timeout_seconds': 120,
                           'server_defaults_not_overridden': 'greedy at temperature 0; top_k/top_p/min_p left at server defaults',
                           'duty_cycle_throttle': 'driver sleeps after each request so server duty is about 0.5; responses are concatenated in request order'},
    'sequence': ['parity', 'prepare', 'calibration inference', 'fit', 'holdout inference', 'audit --require-live', 'summarize', 'reproduce'],
    'frozen_before_holdout_inference': {'frozen_detector_file_sha256': sha(OUT / 'audit' / 'frozen_detector.json'),
                                         'calibration_responses_file_sha256': sha(OUT / 'actor' / 'calibration_responses.jsonl')},
    'failure_handling': 'runner records a server failure as an empty reply with runner_error_type, which scores as a fail-closed escalate; none occurred',
    'hash_convention': 'SHA-256 of file bytes with CRLF folded to LF',
    'published_files_sha256': files}
(OUT / 'run_manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf8')
print(json.dumps({'peak_server_vram_mib': peak, 'cal_duty': cal['request_duty_cycle'], 'hold_duty': hold['request_duty_cycle'], 'free_floor': receipt['free_vram_floor_mib']}))
