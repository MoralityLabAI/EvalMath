"""Regenerate the exact finite arithmetic receipt."""
import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from spiral_ln.certificate_efficiency import CheckedCost, CostBounds, aggregate, interval


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=ROOT / 'output/certificate_efficiency/zkl_efficiency_v1.json')
    args = parser.parse_args()
    count = 0
    valid = True
    for c in range(1, 21):
        for optimum in range(1, c + 1):
            for lower in range(1, optimum + 1):
                for upper in range(optimum, 22):
                    a, b = interval(CostBounds('r', 'p', lower, upper), CheckedCost('r', 'p', c))
                    valid &= 0 < a <= Fraction(optimum, c) <= b <= 1
                    count += 1
    scored = aggregate([(CostBounds('a', 'p', 2, 2), CheckedCost('a', 'p', 4)),
                        (CostBounds('b', 'p', 1), None)])
    sources = ['src/spiral_ln/certificate_efficiency.py', 'tests/test_certificate_efficiency.py',
               'scripts/verify_certificate_efficiency.py']
    report = {'schema': 'zkl-certificate-efficiency/v1', 'scope': 'exact finite arithmetic checks',
              'interval_cases': count, 'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                                                         for p in sources},
              'checks': {'contains_exact_optimum': valid, 'failure_in_denominator':
                         scored['coverage'] == Fraction(1, 2) and scored['efficiency_lower'] == Fraction(1, 4)
                         and scored['efficiency_upper'] == Fraction(1, 4)}}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    if not all(report['checks'].values()):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
