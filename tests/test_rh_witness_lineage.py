import pytest
from spiral_ln.rh_witness_lineage import BOUNDARIES, DECL, scan

def test_identifier_boundaries():
    assert BOUNDARIES["SizeWindows"].search("SizeWindows C ε x")
    assert not BOUNDARIES["SizeWindows"].search("SizeWindowsSomething")
    assert DECL.match("theorem Foo.test : True := by").group(1) == "Foo.test"

def test_declarations_and_references(tmp_path):
    folder = tmp_path / "src" / "Formalism"
    folder.mkdir(parents=True)
    (folder / "Test.lean").write_text(
        "def SizeWindows : Prop := True\n"
        "theorem uses (h : SizeWindows) : True := True.intro\n"
        "def SmallCosts : Prop := True\n")
    result = scan(tmp_path)
    assert result["symbols"]["SizeWindows"]["total_hits"] == 2
    assert len(result["symbols"]["SizeWindows"]["declarations"]) == 1
    assert result["symbols"]["SmallCosts"]["total_hits"] == 1

def test_invalid_limit(tmp_path):
    with pytest.raises(ValueError):
        scan(tmp_path, limit=0)


def test_gate_catalog_pins_read_only_original_source():
    from spiral_ln.rh_witness_lineage import GATE_CHECKS, GATE_FILES
    assert len(GATE_CHECKS) == 7
    assert all(len(blob) == 40 for _, blob in GATE_FILES.values())
