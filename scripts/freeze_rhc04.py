#!/usr/bin/env python3
"""Write a source-hashed RHC-04 protocol receipt (or amendment) before any inference of the phase it guards."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ['configs/rhc04_prereg_v1.json', 'src/spiral_ln/evaluation_rhc04.py', 'src/spiral_ln/evaluation_rhc04_oracle.py',
         'scripts/run_rhc04.py', 'scripts/verify_rhc04.py', 'scripts/run_rhc03_local_5080.py', 'scripts/freeze_rhc04.py',
         'tests/test_rhc04.py', 'tests/test_rhc04_oracle.py', 'paper/reward_hacking_instrumented_runtime_protocol.md']


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(bytes([13, 10]), bytes([10]))).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime-repo', type=Path, required=True, help='Control-Harness checkout')
    ap.add_argument('--runtime-commit', required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--guards', required=True, help='what this receipt freezes, e.g. "before any inference"')
    ap.add_argument('--note', default='')
    a = ap.parse_args()
    if a.out.exists():
        raise SystemExit('refusing to overwrite ' + str(a.out))
    tree = subprocess.run(['git', '-C', str(a.runtime_repo), 'ls-tree', '-r', a.runtime_commit, '--',
                           'environments/mesh_escape_pit_runtime_v1'], capture_output=True, text=True, check=True).stdout
    runtime = {line.split('\t')[1]: line.split()[2] for line in tree.splitlines()}
    receipt = {
        'schema': 'rhc04_protocol_receipt_v1', 'guards': a.guards, 'note': a.note,
        'control_harness': {'repository': 'MoralityLabAI/Control-Harness', 'commit': a.runtime_commit, 'git_blobs': runtime},
        'evalmath_files_sha256_lf': {f: sha(ROOT / f) for f in FILES},
        'model': {'file': 'Qwen3.5-4B-UD-Q4_K_XL.gguf',
                  'sha256': 'b252c5610a42ca82d20fe2a12813e9d069eed89292907e26c783eeb0bc961bc7',
                  'server': 'PrismML llama.cpp build 10743 (adfffbe41) llama-server',
                  'flags': '-ngl 99 -c 4096 -np 1 -fa on --reasoning off --no-webui --host 127.0.0.1',
                  'decoding': {'temperature': 0, 'max_tokens': 64, 'stream': False}},
        'hash_convention': 'SHA-256 with CRLF folded to LF'}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf8', newline='\n')
    print(json.dumps({'written': str(a.out), 'files': len(receipt['evalmath_files_sha256_lf']), 'runtime_blobs': len(runtime)}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
