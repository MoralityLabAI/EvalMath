"""Regenerate CPF-01 using exact arithmetic and an independent policy enumerator."""
import argparse
import hashlib
import json
import runpy
from itertools import product
from pathlib import Path
from fractions import Fraction as F
from spiral_ln.evaluation_cpf import bounds, coupling, optimal, fixed, example, residual

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("src/spiral_ln/evaluation_cpf.py", "tests/test_evaluation_cpf.py",
           "scripts/verify_evaluation_cpf.py", "paper/correlated_proof_fidelity.md",
           "lean/FeedbackChannel/CorrelatedProofFidelity.lean")


def report():
    brute = runpy.run_path(str(ROOT / SOURCES[1]))["brute"]
    count = 0
    for x,y,z in product(range(9), repeat=3):
        if x+y+z <= 8:
            a,b,r = F(x+y,8),F(x+z,8),F(x,8)
            assert coupling(a,b,r) == (r,F(y,8),F(z,8),F(8-x-y-z,8))
            for t in bounds(a,b):
                assert min(coupling(a,b,t)) >= 0
            count += 1
    policies = 0
    for cells in product(("reject","a","b"), repeat=6):
        rows = (cells[:3],cells[3:])
        w = (F(1,10),F(1,5))
        for k in range(3):
            assert optimal(w,rows,k) == brute(w,rows,k) <= fixed(w,rows,k)
            policies += 1
    w, rows = example()
    fa, ad = fixed(w,rows,2), optimal(w,rows,2)
    assert fa == F(3,100) and ad == brute(w,rows,2) == residual(F(1,20),F(2,5))
    return {"schema":"CPF-01.0", "scope":"synthetic conditional null laws; no upstream proof validation",
            "checks":{"coupling_census":True,"endpoint_witnesses":True,"independent_policy_oracle":True,
                      "adaptive_example":True},
            "counts":{"couplings":count,"policy_instances":policies},
            "example":{"joint_before":"1/20","fixed_two":str(fa),"adaptive_two":str(ad)},
            "source_sha256":{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES}}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    data = json.dumps(report(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding="utf-8")
    else:
        print(data, end="")
