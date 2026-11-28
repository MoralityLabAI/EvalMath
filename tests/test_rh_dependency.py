"""Sanity and adversarial tests for proof-expression graph format."""
import json
import pytest

from spiral_ln.rh_dependency import build_probe, parse_output, validate_names


def test_source_graph_keeps_type_and_proof_edges_separate():
    items = [
        {"name": "Example.bridge", "depth": 0, "kind": "theorem",
         "type_refs": ["True"], "value_refs": ["Example.upstream"]},
        {"name": "Example.upstream", "depth": 1, "kind": "theorem",
         "type_refs": ["True"], "value_refs": ["True.intro"]},
    ]
    log = "\n".join(["RHDEP1\t" + json.dumps(x) for x in items] +
                    ["RHDEPEND\t" + json.dumps({"visited": 2, "truncated": False})])
    graph = parse_output(log)
    assert graph["proof_term_data"] and len(graph["edges"]) == 4
    assert {"from": "Example.bridge", "to": "Example.upstream", "channel": "value"} in graph["edges"]


@pytest.mark.parametrize("log", [
    "", 'RHDEPEND\t{"visited":1}',
    'RHDEPEND\t{"visited":0}\nRHDEPEND\t{"visited":0}\n',
    'RHDEP1\t{"name":"x","kind":"theorem","type_refs":[],"value_refs":[]}\n',
])
def test_incomplete_or_duplicated_output_is_rejected(log):
    with pytest.raises((ValueError, KeyError)):
        parse_output(log)


def test_generated_lean_source_is_self_contained_and_sanitized():
    source = build_probe([], ["RHGraphToy.bridge"], 2, 12, ["RHGraphToy."], toy=True)
    assert "RHDepProbe.emit env" in source
    assert "theorem bridge : True := upstream" in source
    assert "allowOpaque := true" in source
    with pytest.raises(ValueError):
        validate_names(["Nat; unsafe"])
    with pytest.raises(ValueError):
        build_probe([], ["A"], -1, 1, ["A"])
