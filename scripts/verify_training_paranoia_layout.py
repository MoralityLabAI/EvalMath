"""Check RHT-26 migration provenance and canonical research-note entry points."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify() -> dict[str, bool]:
    migration = json.loads((ROOT / "TrainingParanoia/RHT-26/source_migration.json").read_text())
    receipt = json.loads((ROOT / migration["current_receipt"]).read_text())
    payload = {k: v for k, v in receipt.items() if k not in ("schema", "source_sha256")}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    checks = {
        "rht26_numerical_payload_unchanged": digest == migration["unchanged_payload_sha256"],
        "four_state_code_tests_and_manifest_unchanged": all(
            hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
            for path, expected in migration["unchanged_source_sha256"].items()),
        "canonical_documents_and_legacy_links_exist": all(
            (ROOT / new).is_file() and (ROOT / old).is_file()
            and "TrainingParanoia" in (ROOT / old).read_text()
            for old, new in migration["moved_documents"].items()),
        "plan_and_new_notes_exist": all((ROOT / path).is_file() for path in (
            "TrainingParanoia/README.md",
            "TrainingParanoia/evaluation_noninterference_plan.md",
            "TrainingParanoia/RHT-27/evaluation_noninterference.md",
            "TrainingParanoia/RHT-28/contamination_composition.md")),
        "superseded_receipt_removed_from_current_tree": not (ROOT / migration["historical_receipt"]).exists(),
    }
    failed = [key for key, value in checks.items() if not value]
    if failed:
        raise AssertionError(f"TrainingParanoia migration checks failed: {failed}")
    return checks


if __name__ == "__main__":
    for name in verify():
        print(f"PASS: {name}")
