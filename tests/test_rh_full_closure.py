from pathlib import Path

import pytest
from spiral_ln.rh_full_closure import ImportGraph, module_name, module_file


def test_submodule_imports_and_shortest_path(tmp_path):
    src = tmp_path / "src"
    (src / "Development").mkdir(parents=True)
    (src / "Main.lean").write_text("import Mathlib\nimport Development.A\n")
    (src / "Development" / "A.lean").write_text("import Development.B\n")
    (src / "Development" / "B.lean").write_text("theorem b : True := True.intro\n")
    graph = ImportGraph(src)
    r = graph.closure("Main", targets=["Development.B", "Unknown"])
    assert r["modules"] == 3
    assert r["import_edges"] == 3
    assert r["external_imports"] == ["Mathlib"]
    assert r["paths"]["Development.B"] == ["Main", "Development.A", "Development.B"]
    assert r["paths"]["Unknown"] is None
    assert graph.imports("Development.B") == ()
    assert graph.closure("Development.A")["modules"] == 2


def test_bad_module_name_rejected(tmp_path):
    assert module_name("src/Development/Foo.lean") == "Development.Foo"
    with pytest.raises(ValueError):
        module_name("Development/Foo.lean")
    for m in ("../evil", "A..B", "C/D"):
        with pytest.raises(ValueError):
            module_file(tmp_path, m)


def test_unresolved_internal_count(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "Main.lean").write_text("import Development.Missing\n")
    r = ImportGraph(src).closure("Main")
    assert r["unresolved_internal_imports"] == ["Development.Missing"]
    assert r["modules"] == 1
