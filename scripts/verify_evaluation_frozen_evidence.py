"""FRE-01 finite audit receipt. Values are synthetic; no benchmark is run."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from spiral_ln.evaluation_frozen_evidence import (
    SCHEMA, audit_frozen_evidence, canonical_bytes, input_identity, sha256,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    "src/spiral_ln/evaluation_frozen_evidence.py",
    "tests/test_evaluation_frozen_evidence.py",
    "scripts/verify_evaluation_frozen_evidence.py",
    "paper/frozen_evidence_audit.md",
)


def receipt() -> dict:
    query = [1, 0, 2]
    program = {"operator": "inverse", "degree": 2}
    identity = input_identity(query, program)
    source = {"experiment_id": "FRE-01-synthetic",
              "cases": [{"case_id": "fixture", "root_id": "fixture-root",
                         "query": query, "program": program}]}
    source_raw = canonical_bytes(source)
    attempt = {"schema": SCHEMA, "experiment_id": source["experiment_id"],
               "attempt_id": "first-fixture", "registration_sha256": "a" * 64,
               "sources_sha256": sha256(source_raw), "role": "original", "outcome": "fail",
               "previous_attempt_id": None, "previous_attempt_sha256": None,
               "arms": {"original": "in_call", "warm": "outside_call"},
               "timings": [{"case_id": "fixture", "repeat": 0, "arm": arm,
                            "elapsed_ns": ns, "context_sha256": "b" * 64,
                            "task_sha256": identity["task_sha256"]}
                           for arm, ns in (("original", 100), ("warm", 75))]}
    original_raw = canonical_bytes(attempt)
    anchor = {"schema": SCHEMA, "experiment_id": source["experiment_id"],
              "registration_sha256": "a" * 64, "sources_sha256": sha256(source_raw),
              "first_attempt_id": "first-fixture", "first_attempt_sha256": sha256(original_raw),
              "repeats": 1, "arms": attempt["arms"], "baseline_arm": "original",
              "unique_queries": True, "fresh_context_per_repeat": True,
              "excluded_task_sha256": []}
    original = audit_frozen_evidence(anchor, source_raw, [original_raw])
    attempt.update(attempt_id="diagnostic-fixture", role="diagnostic", outcome="pass",
                   previous_attempt_id="first-fixture", previous_attempt_sha256=sha256(original_raw),
                   reason="Synthetic successful follow-up after failed gate")
    retained = audit_frozen_evidence(anchor, source_raw, [original_raw, canonical_bytes(attempt)])
    changed_rejected = False
    try:
        audit_frozen_evidence(anchor, source_raw, [canonical_bytes(attempt)])
    except ValueError:
        changed_rejected = True
    duplicate_rejected = False
    source["cases"].append(dict(source["cases"][0], case_id="renamed", schema="v99"))
    duplicate_raw = canonical_bytes(source)
    duplicate_anchor = dict(anchor, sources_sha256=sha256(duplicate_raw))
    try:
        audit_frozen_evidence(duplicate_anchor, duplicate_raw, [original_raw])
    except ValueError as exc:
        duplicate_rejected = "task is duplicated" in str(exc)
    changed_program = input_identity(query, {"operator": "negate", "degree": 2})
    return {
        "schema_version": 1, "experiment": "FRE-01",
        "evidence_level": "finite verified code examples; synthetic timings and trusted-anchor fixtures",
        "checks": {
            "matched_fixture_audits": original["integrity_passed"] is True,
            "ratio_is_exact": original["original_ratio_of_sum_case_medians"]["warm"] == "3/4",
            "failed_first_is_preserved": retained["original_declared_outcome"] == "fail",
            "later_success_stays_diagnostic": retained["attempt_history"][1]["role"] == "diagnostic",
            "changed_first_bytes_rejected": changed_rejected,
            "renamed_wrapper_duplicate_rejected": duplicate_rejected,
            "query_identity_shared_across_programs": identity["query_sha256"] == changed_program["query_sha256"],
            "operative_program_changes_task_identity": identity["task_sha256"] != changed_program["task_sha256"],
        },
        "source_sha256": {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCES},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "output/evaluation_frozen_evidence/fre01_v1.json")
    args = parser.parse_args()
    result = receipt()
    if not all(result["checks"].values()):
        raise SystemExit("FRE-01 failed a finite check")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
