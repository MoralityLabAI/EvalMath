"""Synthetic receipt plumbing tests; these deliberately do not claim cryptography."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location('score_zkl_batch', Path(__file__).resolve().parents[1] / 'scripts/score_zkl_batch.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def dump(path, value):
    path.write_text(json.dumps(value), encoding='utf8')
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture(d):
    batch = {'schema': 'zkl-affine-batch-v1', 'rule_depth': 5, 'memory_depth': 6, 'cases': []}
    receipt = {'schema': 'zkl-nova-batch-receipt-v1', 'nova': '0.76.0', 'rule_depth': 5,
               'memory_depth': 6, 'max_arity': 2, 'raw_step_constraints': 100, 'cases': []}
    (d / 'source-commit.txt').write_text(m.SOURCE)
    (d / 'vk.bin').write_bytes(b'test-vk')
    receipt.update(verification_key_bytes=7, verification_key_sha256=m.sha(b'test-vk'))
    for i, root in enumerate(m.ROOTS):
        for arm, n in zip(m.ARMS, (2, 4), strict=True):
            c = dict(root=root, arm=arm, goal=1, exact_rows=2, environment_id=f'test-{i}',
                     rules=[{}], steps=[{}] * n)
            batch['cases'].append(c)
            filename = f"proof-{len(receipt['cases'])}.bin"
            (d / filename).write_bytes(b'test-proof')
            receipt['cases'].append({k: c[k] for k in ('root', 'arm', 'goal', 'exact_rows', 'environment_id')} |
                                    dict(steps=n, rule_count=1, raw_step_constraint_sum=100*n,
                                         verified=True, wrong_count_and_initial_rejected=True,
                                         proof_file=filename, proof_bytes=10, proof_sha256=m.sha(b'test-proof')))
    bh = dump(d / 'batch.json', batch)
    receipt['transport_sha256'] = bh
    rh = dump(d / 'receipt.json', receipt)
    return bh, rh, receipt


def test_exact_score(tmp_path):
    bh, rh, _ = fixture(tmp_path)
    r = m.score(tmp_path, rh, expected_batch_sha256=bh)
    assert r['arms']['astar']['efficiency_lower'] == '1'
    assert r['arms']['weighted_tree_shared']['efficiency_lower'] == '1/2'
    assert r['arms']['astar']['total_raw_step_constraints'] == 800


@pytest.mark.parametrize('mutation', ['receipt_hash', 'batch_hash', 'proof', 'vk', 'missing', 'cost', 'invalid'])
def test_rejects_mutations(tmp_path, mutation):
    bh, rh, receipt = fixture(tmp_path)
    if mutation == 'receipt_hash':
        rh = '0'*64
    elif mutation == 'batch_hash':
        bh = '0'*64
    elif mutation == 'proof':
        (tmp_path / 'proof-0.bin').write_bytes(b'forged')
    elif mutation == 'vk':
        (tmp_path / 'vk.bin').write_bytes(b'forged')
    else:
        if mutation == 'missing':
            receipt['cases'].pop()
        elif mutation == 'cost':
            receipt['cases'][0]['raw_step_constraint_sum'] += 1
        else:
            receipt['cases'][0]['verified'] = False
        rh = dump(tmp_path / 'receipt.json', receipt)
    with pytest.raises(ValueError):
        m.score(tmp_path, rh, expected_batch_sha256=bh)
