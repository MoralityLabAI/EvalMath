"""Reproduce the frozen RHC-02 projection from Control-Harness reference JSONL.

Run with the *original* source file (GitHub blob SHA pinned below):
    PYTHONPATH=src python scripts/project_mesh_reference_rhc02.py \\
      --source /path/to/Control-Harness/results/mesh_escape_pit/v1/reference_trajectories.jsonl

Default action compares the rebuilt projection byte-for-byte with the fixture.
No network, model calls, or automatic source updating.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SOURCE_REPO = "MoralityLabAI/Control-Harness"
SOURCE_PATH = "results/mesh_escape_pit/v1/reference_trajectories.jsonl"
SOURCE_BLOB = "2e5a9690484f10c26180bf67a7e0f70c75ace0d6"
ROOT = Path(__file__).resolve().parents[1]
PINNED = ROOT / "fixtures/external/mesh_escape_pit_reference_v1_projection.json"
DECISION_CODE = {"retain":"T", "remove":"X", "escalate":"E"}


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()


def project_rows(rows: list[dict]) -> dict:
    if len(rows)!=280:
        raise ValueError(f"expected 280 raw rows, got {len(rows)}")
    controls=list(dict.fromkeys(r["controller"] for r in rows))
    ids=list(dict.fromkeys(r["trajectory_id"] for r in rows))
    if len(ids)!=35 or len(controls)!=8:
        raise ValueError("expected exactly 35 cases and 8 controllers")
    by_pair={(r["controller"],r["trajectory_id"]):r for r in rows}
    if len(by_pair)!=280:
        raise ValueError("duplicate or missing source rows")
    cases=[]
    for id in ids:
        matched=[r for r in rows if r["trajectory_id"]==id]
        teams={r["team"] for r in matched}
        paths={tuple(r["algebra_path"]) for r in matched}
        families={r["family"] for r in matched}
        if len(matched)!=8 or len(teams)!=1 or len(paths)!=1 or len(families)!=1:
            raise ValueError(f"inconsistent case {id}")
        team=next(iter(teams))
        if team not in ("aligned","red"):
            raise ValueError("unknown team")
        cases.append([id,"A" if team=="aligned" else "R","".join(next(iter(paths))),next(iter(families))])
    decisions={}
    success={}
    for ctl in controls:
        group=[by_pair[(ctl,id)] for id in ids]
        decisions[ctl]="".join(DECISION_CODE[r["decision"]] for r in group)
        success[ctl]="".join("1" if r["attack_success"] else "0" for r in group)
    return {
        "schema":"rhc02_mesh_reference_projection_v1",
        "source":{"repository":SOURCE_REPO,"path":SOURCE_PATH,
                  "git_blob_sha":SOURCE_BLOB,"source_row_count":280,
                  "extraction":"one scenario and action path per trajectory_id, decision and attack_success per controller in the original file line order"},
        "cases":cases,"decisions":decisions,"attack_success":success,
    }


def main()->int:
    arg=argparse.ArgumentParser(description=__doc__)
    arg.add_argument("--source",required=True,type=Path)
    arg.add_argument("--output",type=Path,help="write rebuilt projection to a separate path")
    ns=arg.parse_args()
    raw=ns.source.read_bytes()
    sha=git_blob_sha(raw)
    if sha!=SOURCE_BLOB:
        raise SystemExit(f"source Git blob SHA mismatch: {sha}, expected {SOURCE_BLOB}")
    rows=[json.loads(line) for line in raw.splitlines() if line.strip()]
    result=project_rows(rows)
    canonical=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if ns.output:
        if ns.output.resolve()==PINN.resolve():
            raise SystemExit("refusing to overwrite the frozen fixture")
        ns.output.parent.mkdir(parents=True,exist_ok=True)
        ns.output.write_text(canonical,encoding="utf-8")
    expected=PINN.read_text(encoding="utf-8")
    if canonical!=expected:
        raise SystemExit("projection differs from pinned fixture")
    print(f"OK: {len(rows)} raw rows, {len(result['cases'])} cases, {len(result['decisions'])} controllers; SHA {sha}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
