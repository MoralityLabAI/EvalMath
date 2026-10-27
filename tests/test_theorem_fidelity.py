"""Wire the independent TFAF standard-library tests into EvalMath's pytest CI."""
import subprocess
import sys
from pathlib import Path


def test_theorem_fidelity_offline_suite():
    root = Path(__file__).resolve().parents[1]
    command = [sys.executable, "-m", "unittest", "discover", "-s",
               "research/theorem_fidelity", "-p", "test_*.py", "-v"]
    p = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
    assert p.returncode == 0, p.stdout + "\n" + p.stderr
    assert "Ran 8 tests" in p.stderr


def test_theorem_fidelity_receipt():
    root = Path(__file__).resolve().parents[1]
    p = subprocess.run([sys.executable, "scripts/check_theorem_fidelity.py"],
                       cwd=root, capture_output=True, text=True, check=False)
    assert p.returncode == 0, p.stdout + "\n" + p.stderr
