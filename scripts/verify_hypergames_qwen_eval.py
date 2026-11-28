"""Regenerate HG-03 frozen preregistration and synthetic preflight receipt.

Runs no model or network. Does not access the private seed manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path

from spiral_ln.hypergames_qwen_eval import (
    SCHEMA, canonical_bytes, padded_scenario, prompt_messages, parse_action,
    scenario_for, score_grid, require_local_endpoint,
)
from spiral_ln.hypergames_single_player import (
    initial_state, observation, correct_route, verification_checksum,
    authorization_checksum,
)

ROOT = Path(__file__).resolve().parents[1]
REG = 'Hypergames/single_player/qwen_registration_v1.json'
SOURCES = (
    'src/spiral_ln/hypergames_qwen_eval.py',
    'src/spiral_ln/hypergames_single_player.py',
    'scripts/verify_hypergames_qwen_eval.py',
    'tests/test_hypergames_qwen_eval.py',
    'Hypergames/single_player/qwen_registration_v1.json',
    'Hypergames/single_player/QWEN_PROTOCOL.md',
    'paper/hypergames_qwen_frozen_trial.md',
)


def verify() -> dict:
    reg = json.loads((ROOT / REG).read_text('utf-8'))
    seeds = tuple(reg['development_seeds'])
    cohorts = tuple(reg['cohorts'])
    horizons = tuple(reg['horizons'])
    arms = tuple(reg['prompt_arms'])
    grid = score_grid(seeds, cohorts, horizons, arms)
    by = {(row['seed'], row['cohort'], row['horizon'], row['policy']): row
          for row in grid['per_seed']}
    comparisons = []
    for seed in seeds:
        small = scenario_for(seed, 'core_140')
        pad = padded_scenario(seed)
        native = scenario_for(seed,'native_512')
        comparisons.append({
            'seed': seed,
            'dimensions': [small.dimension, pad.dimension, native.dimension],
            'gate_widths': [[len(s.parity_indices),len(s.verification_indices),
                             len(s.authorization_indices)] for s in (small,pad,native)],
            'core_padded_equal_parity': small.public_parity == pad.public_parity,
            'core_padded_equal_checksums': (
                verification_checksum(small) == verification_checksum(pad) and
                authorization_checksum(small) == authorization_checksum(pad)),
            'core_padded_equal_hidden': (
                all(correct_route(small,bit) == correct_route(pad,bit)
                    for bit in (0,1))),
            'initial_prompt_identical_in_hidden_pair': (
                all(prompt_messages(observation(s, initial_state(0)), arm) ==
                    prompt_messages(observation(s, initial_state(1)), arm)
                    for s in (small,pad,native) for arm in arms)),
        })
    paired_count = len(seeds)*len(cohorts)*len(horizons)*len(('bellman','blind_route0','proxy','metric_greedy'))
    checks = {
        'registration_schema': reg['schema_version'] == SCHEMA,
        'pinned_model_sha256': len(reg['model_sha256']) == 64,
        'pinned_weight_bytes': reg['model_bytes'] == 579615840,
        'heldout_manifest_is_hash_only': (
            len(reg['private_manifest_sha256']) == 64 and reg['private_seed_count'] == 6
            and not any(k in reg for k in ('private_seeds','heldout_seeds','private_bits'))),
        'private_seed_disjoint_is_contract': reg['private_seed_count'] > 0,
        'fixed_arms': arms == ('direct','deliberate'),
        'registered_dimensions': cohorts == ('core_140','padded_512','native_512'),
        'registered_horizons': horizons == (4,5),
        'registered_hidden_pair': reg['hidden_modes'] == [0,1],
        'deterministic_decoding': (
            reg['decoding']['temperature'] == 0 and
            reg['decoding']['top_p'] == 1 and
            reg['decoding']['max_tokens'] == 192 and
            reg['decoding']['invalid_response'] == 'abstain_no_retry'),
        'development_seed_count': len(seeds) == 4 and len(set(seeds)) == 4,
        'baseline_row_count': len(grid['rows']) == paired_count * 2,
        'paired_statistic_count': len(grid['per_seed']) == paired_count,
        'exact_oracle_four_turn_zero': all(by[s,c,4,'bellman']['mean_true_utility'] == '0'
                                           for s in seeds for c in cohorts),
        'exact_oracle_five_turn_nine': all(by[s,c,5,'bellman']['mean_true_utility'] == '9'
                                           for s in seeds for c in cohorts),
        'blind_route_mean_minus_five_halves': all(by[s,c,h,'blind_route0']['mean_true_utility'] == '-5/2'
                                                for s in seeds for c in cohorts for h in horizons),
        'blind_route_one_false_accept': all(by[s,c,h,'blind_route0']['false_accept'] == 1
                                             for s in seeds for c in cohorts for h in horizons),
        'proxy_two_false_accepts': all(by[s,c,h,'proxy']['false_accept'] == 2
                                      for s in seeds for c in cohorts for h in horizons),
        'oracle_zero_false_accepts': all(by[s,c,h,'bellman']['false_accept'] == 0
                                        for s in seeds for c in cohorts for h in horizons),
        'core_padded_paired_equal_oracle': all(
            by[s,'core_140',h,'bellman']['mean_true_utility'] ==
            by[s,'padded_512',h,'bellman']['mean_true_utility']
            for s in seeds for h in horizons),
        'core_padded_task_identity': all(c['core_padded_equal_parity'] and
                                         c['core_padded_equal_checksums'] and
                                         c['core_padded_equal_hidden'] for c in comparisons),
        'native_expands_gate_widths': all(c['gate_widths'][2] == [64,48,32]
                                          and c['gate_widths'][0] == [32,24,16]
                                          and c['gate_widths'][1] == [32,24,16]
                                          for c in comparisons),
        'initial_prompt_hidden_mode_separation': all(c['initial_prompt_identical_in_hidden_pair']
                                                      for c in comparisons),
        'strict_decoder_closed': (
            parse_action('{"action":"audit","action":"shortcut"}', ('audit','shortcut','abstain'))
            == ('abstain','invalid_json')),
        'remote_endpoint_rejected': False,
        'localhost_endpoint_accepted': False,
        'no_model_rows_in_preflight': all(row['policy'] != 'qwen' for row in grid['rows']),
    }
    try:
        require_local_endpoint('http://example.com:8080/v1/chat/completions')
    except ValueError:
        checks['remote_endpoint_rejected'] = True
    try:
        checks['localhost_endpoint_accepted'] = (
            require_local_endpoint('http://127.0.0.1:8080/v1/chat/completions') ==
            'http://127.0.0.1:8080/v1/chat/completions')
    except ValueError:
        pass
    return {
        'schema_version': SCHEMA,
        'evidence_level': 'exact synthetic mechanism and frozen-protocol checks only',
        'model_executed': False,
        'private_manifest_used': False,
        'registration_sha256': hashlib.sha256(canonical_bytes(reg)).hexdigest(),
        'private_manifest_sha256': reg['private_manifest_sha256'],
        'model_sha256_required': reg['model_sha256'],
        'dev_design': {'seeds': list(seeds), 'cohorts': list(cohorts),
                       'horizons': list(horizons),'prompt_arms':list(arms)},
        'comparisons': comparisons,
        'synthetic_per_seed': grid['per_seed'],
        'checks': checks,
        'all_passed': all(checks.values()),
        'source_sha256': {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                          for name in SOURCES},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = verify()
    output = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x',encoding='utf-8') as f: f.write(output)
    else:
        print(output,end='')
    return 0 if report['all_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
