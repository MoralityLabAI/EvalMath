"""Regenerate and verify the committed theorem-fidelity receipt.

Run with no arguments to check, or --write to regenerate after source edits.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.theorem_fidelity.theorem_fidelity import validate  # noqa: E402

OUTPUT = ROOT / "output/theorem_fidelity.json"
SOURCES = (
    "research/theorem_fidelity/theorem_fidelity.py",
    "research/theorem_fidelity/upstream_contract.py",
    "research/theorem_fidelity/upstream_pin.json",
    "lean/FeedbackChannel/TheoremFidelity.lean",
)
EVIDENCE = {
    "TF-01": "exact finite witness",
    "TF-02": "exact finite witness in relaxed relation model",
    "TF-03": "exact finite bipartite F2-translation witness",
    "TF-04": "exhaustive one-variable three-slot 3CNF",
    "TF-05": "symbolic unboundedness (Lean build required)",
    "TF-06": "constructive binomial bound plus tested finite certificate",
}


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def expected() -> dict:
    pin = json.loads((ROOT / "research/theorem_fidelity/upstream_pin.json").read_text("utf-8"))
    return {
        "schema": 1,
        "upstream_commit": pin["commit"],
        "source_blobs": {path: git_blob_sha((ROOT / path).read_bytes()) for path in SOURCES},
        "evidence": EVIDENCE,
        "witnesses": validate(),
        "scope": "finite semantic cases and source-contract audit; no UGC hardness proof",
    }


def main():
    want = expected()
    if sys.argv[1:] == ["--write"]:
        OUTPUT.write_text(json.dumps(want, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print(f"regenerated {OUTPUT}")
        return
    if sys.argv[1:]:
        raise SystemExit("usage: python scripts/check_theorem_fidelity.py [--write]")
    got = json.loads(OUTPUT.read_text(encoding="utf-8"))
    if got != want:
        raise SystemExit("theorem fidelity receipt mismatch; run --write and review the diff")
    print(f"theorem fidelity: {len(want['witnesses'])} cases, "
          f"{len(want['source_blobs'])} verified source blobs")


if __name__ == "__main__":
    main()
