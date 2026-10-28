"""Emit or check a deterministic receipt for the isolated exact fixtures."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from spiral_ln.qwenputer_contract import delta, key, matrix, matmul, overwrite
from fractions import Fraction as F


def receipt():
    u = matrix(((F(3, 5), -F(4, 5)), (F(4, 5), F(3, 5))))
    checks = 0
    for width in (1, 2):
        for flat in itertools.product((-1, 0, 1), repeat=2 * width):
            s = matrix((flat[:width], flat[width:]))
            for address, value in itertools.product(range(2), itertools.product((-1, 0, 1), repeat=width)):
                expected = overwrite(s, address, value)
                if delta(s, key(2, address), value) != expected:
                    raise ValueError('overwrite counterexample')
                rotated_key = tuple(row[address] for row in u)
                if delta(matmul(u, s), rotated_key, value) != matmul(u, expected):
                    raise ValueError('rotation counterexample')
                checks += 1
    sources = ['src/spiral_ln/qwenputer_contract.py', 'tests/test_qwenputer_contract.py',
               'scripts/verify_qwenputer_contract.py', 'paper/qwenputer_contract.md']
    return dict(schema_version=1, evidence_level='finite_verified_example',
                memory_cases=checks, overwrite_checks=checks, rotation_checks=checks,
                upstream_model_run=False, lean_kernel_check=False,
                source_sha256={p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sources})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    if args.out and args.check:
        parser.error('choose --out or --check')
    text = json.dumps(receipt(), indent=2, sort_keys=True) + '\n'
    if args.check:
        if args.check.read_text() != text:
            raise SystemExit('receipt or source mismatch')
        print('receipt verified')
    elif args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
