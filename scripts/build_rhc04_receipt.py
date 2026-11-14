#!/usr/bin/env python3
"""GPU resource receipt for RHC-04 from the sampled per-phase files."""
import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
TOTAL = 15915
phases = {}
for t in sorted((OUT / 'resource').glob('M_*_timing.json')):
    name = t.name[:-len('_timing.json')]
    timing = json.loads(t.read_text())
    rows = [json.loads(x) for x in (OUT / 'resource' / (name + '_gpu_samples.jsonl')).read_text().splitlines()]
    srv = [r['server_mib'] for r in rows if r.get('server_mib') is not None]
    util = [r['server_util'] for r in rows if r.get('server_util') is not None and 0 <= r['server_util'] <= 100]
    dropped = sum(1 for r in rows if r.get('server_util') is not None and not 0 <= r['server_util'] <= 100)
    used = [r['gpu_used_mib'] for r in rows if r.get('gpu_used_mib')]
    if timing.get('requests') is None:
        timing['requests'] = sum(len(json.loads(l)['requests']) for l in (OUT / 'actor_raw' / (name + '_actor.jsonl')).read_text().splitlines())
    phases[name] = {'wall_seconds': timing['wall_seconds'], 'episodes': timing.get('episodes'), 'requests': timing.get('requests'),
                    'samples': len(rows), 'util_samples_dropped_as_counter_glitch': dropped, 'server_peak_vram_mib': max(srv), 'server_mean_gpu_util_percent': round(sum(util) / len(util), 2),
                    'card_peak_used_mib': max(used), 'min_free_vram_mib': TOTAL - max(used), 'ceiling_breach': timing['ceiling_breach'],
                    'power_cap_w': sorted({r['gpu_power_cap_w'] for r in rows if 'gpu_power_cap_w' in r})}
peak = max(p['server_peak_vram_mib'] for p in phases.values())
receipt = {'schema': 'rhc04_gpu_resource_receipt_v1', 'date_utc': '2026-11-14',
           'gpu': 'NVIDIA GeForce RTX 5080 Laptop GPU, 15915 MiB, shared; no other job was interrupted',
           'budget': {'server_vram_ceiling_mib': 8192, 'min_free_vram_mib': 8192, 'duty_cycle': 0.5, 'requests_in_flight': 1, 'max_tokens': 64},
           'phases': phases, 'peak_server_vram_mib': peak, 'peak_within_ceiling': peak <= 8192,
           'min_free_vram_mib_overall': min(p['min_free_vram_mib'] for p in phases.values()),
           'requests_total': sum(p['requests'] or 0 for p in phases.values()),
           'note': 'Per-process VRAM and utilisation are vramorama samples taken every few seconds; the KV cache is allocated at server start so the peak is flat. Whole-card figures include other sessions.'}
(OUT / 'gpu_resource_receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + chr(10), encoding='utf8', newline=chr(10))
print(json.dumps({'peak_server_vram_mib': peak, 'min_free': receipt['min_free_vram_mib_overall'], 'requests': receipt['requests_total']}))
