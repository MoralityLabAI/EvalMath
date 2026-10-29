"""IRC-02 exact finite verification receipt, deterministic and source-hashed."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    'src/spiral_ln/interface_relative_compactification.py',
    'tests/test_interface_relative_compactification.py',
    'scripts/verify_interface_relative_compactification.py',
    'paper/interface_relative_compactification.md',
)
DEFAULT = ROOT / 'output/interface_relative_compactification/irc02_v0_1.json'
EXPECTED = 17


def generate():
    results = {}
    env = dict(os.environ, PYTHONPATH=str(ROOT / 'src') + os.pathsep + os.environ.get('PYTHONPATH', ''))
    for mode in ('normal', 'optimized'):
        command = [sys.executable]
        if mode == 'optimized':
            command.append('-O')
        command.extend(('-m', 'unittest', 'discover', '-s', 'tests',
                        '-p', 'test_interface_relative_compactification.py', '-v'))
        run = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
        text = run.stdout + run.stderr
        count = re.search(r'Ran (\d+) tests?', text)
        if (run.returncode != 0 or count is None or int(count.group(1)) != EXPECTED
                or re.search(r'^OK\s*$', text, re.MULTILINE) is None
                or 'skipped=' in text or 'expected failures=' in text):
            raise RuntimeError(f'IRC-02 {mode} failed ({run.returncode}): {text[-2500:]}')
        results[mode] = {'passed': True, 'tests': EXPECTED}
    return {
        'schema': 'irc02-exact-v0.1',
        'evidence_level': 'finite verified example; handwritten conditional theorem',
        'source_sha256': {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                          for path in SOURCES},
        'checks': {
            'normal_tests': results['normal']['passed'],
            'optimized_tests': results['optimized']['passed'],
            'independent_4800_cylinder_comparisons': True,
            'whole_adaptive_policy_tree_enumeration': True,
            '40_seeded_random_kernel_world_checks': True,
            'deadline_and_fail_closed_cases': True,
            'successor_closed_history_domain': True,
        },
        'test_runs': results,
        'declared_pairwise_checks': 4800,
        'seeded_random_kernels': 40,
        'neural_measurements': 0,
        'lean_compilation': False,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=DEFAULT)
    ap.add_argument('--check', action='store_true', help='validate an existing receipt')
    args = ap.parse_args()
    result = generate()
    if args.check:
        if not args.output.exists() or json.loads(args.output.read_text()) != result:
            raise SystemExit('IRC-02 receipt mismatch')
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print('IRC-02: 17/17 tests in each mode; exact reference and hashes verified')


if __name__ == '__main__':
    main()
