"""Score a DCF-16 predictions file (JSONL: id, algorithm, action, optional p, claimed_ops).

Usage: python scripts/score_dcf16_decision.py HELDOUT.jsonl.gz PREDS.jsonl [--against OTHER.jsonl]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from spiral_ln.evaluation_dcf16_decision import jsonable, load_records, paired, report


def read_preds(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("records", type=Path)
    ap.add_argument("predictions", type=Path)
    ap.add_argument("--against", type=Path, help="second predictions file for a paired comparison")
    a = ap.parse_args()
    recs, preds = load_records(a.records), read_preds(a.predictions)
    out = {"report": report(recs, preds)}
    if a.against:
        out["paired_vs_against"] = paired(recs, preds, read_preds(a.against))
    print(json.dumps(jsonable(out), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
