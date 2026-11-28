"""CPU-only tests for the ChCore theorem-expression extraction contract."""
import pytest
from spiral_ln.rh_deep_analytic import TARGETS, SOURCE_BLOB, compact_summary, run


def test_source_roots_and_sha_pins():
    assert len(SOURCE_BLOB) == 40
    assert TARGETS["balance_core"]["constant"] == "Deduction.CharacterBalanceMoves.core"
    assert TARGETS["size_bound"]["constant"].endswith(".proposition_size_bound")


def test_summary_keeps_actual_proof_references_and_truncation():
    node = {"name": TARGETS["balance_core"]["constant"], "kind": "theorem",
            "type_refs": ["P"], "value_refs": ["Deduction.helper", "True.intro"]}
    dependency = {"name": "Deduction.helper", "kind": "theorem",
                  "type_refs": [], "value_refs": []}
    receipt = {
        "status": "source_pinned_compiled_reference_graph", "proof_term_data": True,
        "module_count": 85, "source": {"commit": "a"*40},
        "graphs": {"balance_core": {
            "nodes": [node, dependency],
            "scope": {"visited": 2, "queued": 2,
                      "truncated": False, "depth_limited": True},
        }}
    }
    result = compact_summary(receipt)
    assert result["roots"]["balance_core"]["direct_theorem_refs"] == ["Deduction.helper"]
    assert result["roots"]["balance_core"]["proof_value_ref_count"] == 2
    assert result["roots"]["balance_core"]["depth_limited"] is True


def test_source_and_budget_inputs_rejected_before_io(tmp_path):
    with pytest.raises(ValueError, match="invalid or empty"):
        run(tmp_path, {}, ["not_a_target"], max_depth=1, max_nodes=100,
            max_modules=150, timeout=60, plan_only=True)
    with pytest.raises(ValueError, match="invalid proof-reference"):
        run(tmp_path, {}, ["balance_core"], max_depth=-1, max_nodes=100,
            max_modules=150, timeout=60, plan_only=True)
