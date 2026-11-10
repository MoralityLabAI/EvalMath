#!/usr/bin/env python3
"""Half-lease driver for RHC-03 on a shared GPU.

Feeds one request at a time through the existing ``local-http`` command of
``run_rhc03_prospective.py`` (so request/response handling is the registered
code path), sleeps after each request so the server duty cycle is about
``--duty``, samples per-process VRAM and utilisation of the inference server
once a second, and kills the server if its VRAM exceeds ``--vram-ceiling-mib``
(the remaining requests are then recorded as failed rollouts by the runner).
It never reads the oracle vault.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
import time
from pathlib import Path

RUNNER = Path(__file__).with_name('run_rhc03_prospective.py')


def sample(pid: int) -> dict:
    now = time.time()
    row = {'t': now, 'server_mib': None, 'server_util': None, 'gpu_used_mib': None, 'gpu_util': None}
    try:
        out = subprocess.run(['vramorama', 'ps', '--json'], capture_output=True, text=True, timeout=20).stdout
        for ad in json.loads(out).get('adapters', []):
            row['gpu_used_mib'] = ad.get('used_mib')
            for proc in ad.get('procs', []):
                if proc.get('pid') == pid:
                    row['server_mib'] = proc.get('mib')
                    row['server_util'] = proc.get('util')
    except Exception as exc:  # sampling must never stop the run
        row['sample_error'] = type(exc).__name__
    try:
        out = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,power.draw,enforced.power.limit',
                              '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=20).stdout
        util, power, cap = [x.strip() for x in out.strip().split(',')]
        row['gpu_util'] = float(util)
        row['gpu_power_w'] = float(power)
        row['gpu_power_cap_w'] = float(cap)
    except Exception as exc:
        row['smi_error'] = type(exc).__name__
    return row


class Monitor(threading.Thread):
    def __init__(self, pid: int, ceiling: int, log: Path):
        super().__init__(daemon=True)
        self.pid, self.ceiling, self.log = pid, ceiling, log
        self.stop_flag = threading.Event()
        self.breach: dict | None = None
        self.n = 0

    def run(self) -> None:
        with self.log.open('a', encoding='utf8') as fh:
            while not self.stop_flag.is_set():
                row = sample(self.pid)
                fh.write(json.dumps(row, sort_keys=True) + '\n')
                fh.flush()
                self.n += 1
                if row['server_mib'] is not None and row['server_mib'] > self.ceiling and self.breach is None:
                    self.breach = row
                    subprocess.run(['taskkill', '/PID', str(self.pid), '/F'], capture_output=True)
                self.stop_flag.wait(1.0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--phase', required=True, choices=['calibration', 'holdout'])
    ap.add_argument('--requests', type=Path, required=True)
    ap.add_argument('--responses', type=Path, required=True)
    ap.add_argument('--model', required=True)
    ap.add_argument('--endpoint', required=True)
    ap.add_argument('--server-pid', type=int, required=True)
    ap.add_argument('--vram-ceiling-mib', type=int, default=8192)
    ap.add_argument('--duty', type=float, default=0.5)
    ap.add_argument('--timeout', type=int, default=120)
    ap.add_argument('--samples', type=Path, required=True)
    ap.add_argument('--timing', type=Path, required=True)
    a = ap.parse_args()
    if a.responses.exists():
        raise SystemExit('responses file exists; refusing to overwrite')
    lines = [x for x in a.requests.read_text(encoding='utf8').splitlines() if x.strip()]
    mon = Monitor(a.server_pid, a.vram_ceiling_mib, a.samples)
    mon.start()
    start = time.time()
    per_req = []
    scratch = a.responses.with_suffix('.work')
    scratch.mkdir(exist_ok=True)
    out_lines = []
    for i, line in enumerate(lines):
        one_req, one_resp = scratch / f'{i:03d}_req.jsonl', scratch / f'{i:03d}_resp.jsonl'
        one_req.write_text(line + '\n', encoding='utf8')
        t0 = time.time()
        proc = subprocess.run([sys.executable, str(RUNNER), 'local-http', '--model', a.model, '--endpoint', a.endpoint,
                               '--requests', str(one_req), '--responses', str(one_resp), '--timeout', str(a.timeout)],
                              capture_output=True, text=True)
        busy = time.time() - t0
        out_lines.append(one_resp.read_text(encoding='utf8').strip())
        per_req.append({'index': i, 'seconds': round(busy, 3), 'runner_returncode': proc.returncode})
        if mon.breach is not None:
            pass  # the server is dead; remaining requests fail and are recorded by the runner
        time.sleep(busy * (1 - a.duty) / a.duty)
    end = time.time()
    mon.stop_flag.set()
    mon.join(timeout=10)
    a.responses.write_text('\n'.join(out_lines) + '\n', encoding='utf8')
    a.timing.write_text(json.dumps({
        'phase': a.phase, 'start_epoch': start, 'end_epoch': end, 'wall_seconds': round(end - start, 3),
        'busy_seconds': round(sum(r['seconds'] for r in per_req), 3), 'requests': per_req,
        'vram_ceiling_mib': a.vram_ceiling_mib, 'duty_target': a.duty, 'samples': mon.n,
        'ceiling_breach': mon.breach}, indent=2, sort_keys=True), encoding='utf8')
    print(json.dumps({'phase': a.phase, 'responses': len(out_lines), 'wall_seconds': round(end - start, 1),
                      'ceiling_breach': mon.breach is not None}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
