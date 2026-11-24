"""Generate an exact source-hashed CCF-01 receipt."""
import argparse
import hashlib
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tests')]
from spiral_ln.evaluation_ccf import conflict_graph, edge_contexts, envelope, optimal_code, partitions, risks
from test_evaluation_ccf import independent_chromatic, test_five_cycle_budget, test_side_information_and_weights


def verify():
    pairs = list(combinations(range(5), 2))
    counts = Counter()
    agree = faithful = 0
    for mask in range(1 << len(pairs)):
        edges = frozenset(e for j, e in enumerate(pairs) if mask >> j & 1)
        contexts = edge_contexts(edges)
        k, labels = optimal_code(5, edges)
        counts[k] += 1
        agree += k == independent_chromatic(5, edges)
        faithful += conflict_graph(5, contexts) == edges and all(lo == hi for lo, hi in envelope(contexts, labels).values())
    test_five_cycle_budget()
    test_side_information_and_weights()
    cycle = edge_contexts({(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)})
    best = min(risks(cycle, p) for p in partitions(5) if len(set(p)) <= 2)
    paths = ['src/spiral_ln/evaluation_ccf.py', 'tests/test_evaluation_ccf.py', 'scripts/verify_evaluation_ccf.py']
    return {'experiment': 'CCF-01', 'evidence': 'finite verified example; synthetic',
            'graphs': 1024, 'coloring_agreements': agree, 'faithful_decoders': faithful,
            'chromatic_histogram': dict(sorted(counts.items())), 'cycle_two_label_risks': list(map(str, best)),
            'checks': {'all_colorings_agree': agree == 1024, 'all_decoders_faithful': faithful == 1024,
                       'cycle_and_weighted_fixtures': True},
            'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'output/evaluation_ccf/ccf01.json')
    args = parser.parse_args()
    receipt = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    print(json.dumps(receipt, sort_keys=True))
    if not all(receipt['checks'].values()):
        sys.exit(1)
