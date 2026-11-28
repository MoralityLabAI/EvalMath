#!/usr/bin/env python3
"""CPF-05 backend fingerprint: server props, GPU memory, cap compliance, usage and throughput.

Sends a few dev-split prompts (never test prompts) through the same request path as
run_cpf_suite.collect and writes a JSON fingerprint. Used before freezing the run config.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from urllib.request import urlopen

from run_cpf_suite import SYSTEM, call, read_jsonl


def get(url):
    with urlopen(url, timeout=30) as r:
        return json.load(r)


def gpu():
    out = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.used,memory.total,temperature.gpu,driver_version',
                          '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=15).stdout
    name, used, total, temp, driver = [x.strip() for x in out.strip().splitlines()[0].split(',')]
    return {'name': name, 'memory_used_mib': int(used), 'memory_total_mib': int(total),
            'temperature_c': int(temp), 'driver': driver}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', required=True)
    p.add_argument('--model', required=True)
    p.add_argument('--prompts', required=True, help='dev-split prompts.jsonl')
    p.add_argument('--n', type=int, default=4)
    p.add_argument('--checkpoint', help='weight file to record (sha256 taken from --sha256 or computed)')
    p.add_argument('--sha256')
    p.add_argument('--out', required=True)
    args = p.parse_args()
    config = json.loads(Path(args.config).read_text())
    model = config['models'][args.model]
    base = model['url'].rstrip('/')
    root = base[:-3] if base.endswith('/v1') else base
    record = {'schema': 'CPF-backend.1', 'model_key': args.model, 'config_model': model,
              'models_endpoint': get(base + '/models'), 'gpu_before': gpu()}
    try:
        props = get(root + '/props')
        record['props'] = {k: props.get(k) for k in ('build_info', 'model_path', 'total_slots', 'chat_template_caps')}
        record['props']['n_ctx'] = (props.get('default_generation_settings') or {}).get('n_ctx')
    except Exception as e:  # not every backend exposes /props
        record['props_error'] = repr(e)
    if args.checkpoint:
        path = Path(args.checkpoint)
        sha = args.sha256
        if sha is None:
            h = hashlib.sha256()
            with path.open('rb') as f:
                for chunk in iter(lambda: f.read(1 << 22), b''):
                    h.update(chunk)
            sha = h.hexdigest()
        record['checkpoint'] = {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha}
    calls = []
    for row in read_jsonl(args.prompts)[:args.n]:
        for cap in (config['budget'], config['budget'] // 2):
            r = call(model, row['prompt'], cap, 1, config['temperature'])
            t = r.get('timings') or {}
            calls.append({'id': row['id'], 'cap': cap, 'completion': r['completion'], 'prompt': r['prompt'],
                          'seconds': round(r['seconds'], 3), 'finish_reason': r['finish_reason'],
                          'content_chars': len(r['text']), 'reasoning_chars': len(r['reasoning'] or ''),
                          'decode_tps': t.get('predicted_per_second'), 'prefill_tps': t.get('prompt_per_second'),
                          'content': r['text'][:400]})
    record['calls'] = calls
    record['gpu_after'] = gpu()
    record['cap_violations'] = sum(c['completion'] > c['cap'] for c in calls)
    tps = [c['decode_tps'] for c in calls if c['decode_tps']]
    record['decode_tps_mean'] = sum(tps) / len(tps) if tps else None
    record['system_prompt_sha256'] = hashlib.sha256(SYSTEM.encode()).hexdigest()
    Path(args.out).write_text(json.dumps(record, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    for c in calls:
        print(c['cap'], c['completion'], c['finish_reason'], c['decode_tps'], repr(c['content'][:120]))
    print('cap violations', record['cap_violations'], 'mean decode tps', record['decode_tps_mean'],
          'gpu MiB', record['gpu_after']['memory_used_mib'])


if __name__ == '__main__':
    main()
