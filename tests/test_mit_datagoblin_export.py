"""MIT-14 DataGoblin export: record shape, payload hashing, split hygiene."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'gyms' / 'MathematicalInstrumentTransfer'))
import datagoblin_export as dx

REQUIRED = {'item_id', 'schema_version', 'content_sha256', 'source_kind', 'purpose_id', 'lawful_basis', 'allowed_uses',
            'data_residency_region', 'sensitivity_class', 'license_status', 'consent_status', 'personal_data_status',
            'redacted', 'contains_secret', 'contains_hidden_reasoning', 'contains_model_weight', 'evaluation_material',
            'sealed_evaluation', 'model_generated', 'generator_id', 'evidence_type', 'asserted_by', 'verified_by',
            'verification_receipt_sha256', 'verification_subject_sha256', 'verification_custody', 'provenance_refs',
            'dedup_group', 'intended_split', 'retention_days', 'deletion_requested', 'public_metadata'}
FORBIDDEN_PUBLIC = {'content', 'raw_content', 'text', 'filesystem_path', 'path', 'secret', 'credential', 'password', 'token'}


from functools import lru_cache


@lru_cache(None)
def fixtures():
    return tuple(dx.fixture_records({}))


def rows():
    return list(fixtures()) + dx.witness_records({})


def test_records_complete_and_hashed():
    rs = rows()
    assert len(rs) == 1026
    for r in rs:
        rec = r['record']
        assert set(rec) == REQUIRED
        assert rec['content_sha256'] == dx.sha(r['payload']) and len(rec['content_sha256']) == 64
        assert not (set(rec['public_metadata']) & FORBIDDEN_PUBLIC)
        assert rec['model_generated'] is False and rec['sealed_evaluation'] is False
        assert rec['dedup_group'] == r['payload']['root_id']


def test_split_by_root_not_row():
    by_root = {}
    for r in fixtures():
        by_root.setdefault(r['payload']['root_id'], set()).add(r['record']['intended_split'])
    assert all(len(s) == 1 for s in by_root.values())


def test_confirmation_refused():
    with pytest.raises(ValueError):
        dx.record('x', dict(root_id='r'), kind='k', split='confirmation', model_generated=False, generator_id=None,
                  evidence='SIMULATED', verified_by=None, receipt_sha=None, evaluation=False, meta={})


def test_validates_with_datagoblin_when_present():
    dg = ROOT.parent / 'DataGoblin'
    if not (dg / 'src' / 'datagoblin').exists():
        pytest.skip('DataGoblin checkout not beside EvalMath')
    assert dx.validate(dx.witness_records({}), dg) == 2
