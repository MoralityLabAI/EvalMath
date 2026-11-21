"""Source audit tests with deliberate tampering and Unicode declarations."""
from pathlib import Path
import pytest
from spiral_ln.rh_source_audit import REQUIRED, match_name, region, verified_file

def test_exact_lean_symbol_boundaries():
    assert match_name("theorem UpperTheory.Comparison₂.core_gm : True", "core_gm")
    assert match_name("theorem UpperTheory.Comparison₂.core_gm : True", "Comparison₂.core_gm")
    assert not match_name("core_gm_more", "core_gm")
    assert not match_name("mycore_gm", "core_gm")

def test_source_slices_fail_closed():
    with pytest.raises(ValueError, match="missing declaration"):
        region("theorem sample", "def CoreAtH", "def pcOf")
    with pytest.raises(ValueError, match="missing boundary"):
        region("def CoreAtH : Prop := True", "def CoreAtH", "def pcOf")

def test_blob_mismatch_is_fatal(tmp_path):
    p = tmp_path / "src" / "Test.lean"
    p.parent.mkdir()
    p.write_text("theorem test : True := True.intro\n")
    with pytest.raises(ValueError, match="Git blob differs"):
        verified_file(tmp_path, Path("src/Test.lean"), "0" * 40)
    _, record = verified_file(tmp_path, Path("src/Test.lean"))
    assert len(record["sha256"]) == 64

def test_contract_has_named_arithmetic_obligations():
    assert len(REQUIRED) == 16
    assert "C.eDiv ≤ eD" in REQUIRED.values()
    assert "C.eLoss ≤ eL" in REQUIRED.values()
    assert "HostAddCharCompatible H ell" in REQUIRED.values()
    assert "ErrWindows Dd C Xpp" in REQUIRED.values()
