"""Score the pinned ZKL-16 public pilot from trusted Nova CI evidence.

This checks artifact integrity and the frozen cost contract, not a SNARK.
Obtain the receipt digest from a trusted run before invoking this scorer.
"""
import argparse
import hashlib
import json
from pathlib import Path

from spiral_ln.certificate_efficiency import CheckedCost, CostBounds, aggregate

SOURCE = 'e7394fced457c059f20ef54128dbc80b0cc747a5'
CIRCUIT = '26223c2775affe6d44eaa10e2c56acc2bdf1ae70'
BATCH_SHA256 = '2d305d145514b39111e2eb06570f91c4bf3d5a0c8ca66afbb9a1d366ae50fce3'
ROOTS = ('same-93000', 'same-93001', 'shift-94000', 'shift-94001')
ARMS = ('astar', 'weighted_tree_shared')


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


def positive(value):
    return type(value) is int and value > 0


def read(path, cap):
    with path.open('rb') as f:
        raw = f.read(cap + 1)
    check(len(raw) <= cap, f'artifact too large: {path.name}')
    return raw


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def score(directory, trusted_receipt_sha256, *, expected_batch_sha256=BATCH_SHA256):
    check((directory / 'source-commit.txt').read_text().strip() == SOURCE, 'wrong source revision')
    batch_raw = read(directory / 'batch.json', 262144)
    receipt_raw = read(directory / 'receipt.json', 262144)
    check(sha(batch_raw) == expected_batch_sha256, 'wrong frozen batch')
    check(sha(receipt_raw) == trusted_receipt_sha256, 'wrong trusted receipt digest')
    batch = json.loads(batch_raw)
    receipt = json.loads(receipt_raw)
    check(batch['schema'] == 'zkl-affine-batch-v1' and batch['rule_depth'] == 5
          and batch['memory_depth'] == 6, 'wrong batch shape')
    check(receipt['schema'] == 'zkl-nova-batch-receipt-v1' and receipt['nova'] == '0.76.0'
          and receipt['transport_sha256'] == sha(batch_raw) and receipt['rule_depth'] == 5
          and receipt['memory_depth'] == 6 and receipt['max_arity'] == 2, 'wrong receipt profile')
    step_cost = receipt['raw_step_constraints']
    check(positive(step_cost), 'invalid measured step count')
    profile = f'{CIRCUIT}:nova-0.76.0:affine:d6:r5:a2:raw-step-{step_cost}'
    vk = read(directory / 'vk.bin', 128 * 1024 * 1024)
    check(len(vk) == receipt['verification_key_bytes'] and sha(vk) == receipt['verification_key_sha256'],
          'verification key artifact mismatch')
    expected = [(root, arm) for root in ROOTS for arm in ARMS]
    check([(c['root'], c['arm']) for c in batch['cases']] == expected, 'wrong frozen cases')
    check([(c['root'], c['arm']) for c in receipt['cases']] == expected, 'incomplete or reordered receipt')
    all_rows = {arm: [] for arm in ARMS}
    totals = {arm: 0 for arm in ARMS}
    for i, (source, result) in enumerate(zip(batch['cases'], receipt['cases'], strict=True)):
        root, arm = expected[i]
        steps = len(source['steps'])
        optimal = source['exact_rows']
        check(positive(optimal) and optimal <= steps <= 64, 'invalid exact reference')
        if arm == 'astar':
            check(optimal == steps, 'reference arm inconsistent')
        else:
            reference = batch['cases'][i - 1]
            check(all(source[k] == reference[k] for k in ('goal', 'rules', 'environment_id', 'exact_rows')),
                  'paired environment mismatch')
        check(all(result[k] == source[k] for k in ('goal', 'environment_id', 'exact_rows'))
              and result['steps'] == steps and result['rule_count'] == len(source['rules'])
              and result['raw_step_constraint_sum'] == step_cost * steps, 'receipt/source mismatch')
        check(result['verified'] is True and result['wrong_count_and_initial_rejected'] is True,
              'missing successful verification evidence')
        filename = f'proof-{i}.bin'
        check(result['proof_file'] == filename, 'unexpected proof filename')
        proof = read(directory / filename, 16 * 1024 * 1024)
        check(len(proof) == result['proof_bytes'] and sha(proof) == result['proof_sha256'],
              'proof artifact mismatch')
        identity = f"{root}:{source['environment_id']}"
        cost = step_cost * steps
        bound = step_cost * optimal
        all_rows[arm].append((CostBounds(identity, profile, bound, bound), CheckedCost(identity, profile, cost)))
        totals[arm] += cost
    arms = {arm: {k: str(v) if k in ('coverage', 'efficiency_lower', 'efficiency_upper') else v
                  for k, v in aggregate(rows).items()} for arm, rows in all_rows.items()}
    for arm in ARMS:
        arms[arm]['total_raw_step_constraints'] = totals[arm]
    return {'schema': 'zkl-16-score-v1', 'cost_profile': profile, 'source_commit': SOURCE,
            'transport_sha256': sha(batch_raw), 'trusted_receipt_sha256': sha(receipt_raw),
            'scope': 'trusted CI receipt arithmetic and artifact integrity only', 'arms': arms}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--trusted-receipt-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(score(args.directory, args.trusted_receipt_sha256), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
