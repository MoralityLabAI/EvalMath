"""PreferredEvals v2: strict planning-manifest lint, pure standard library.

A passing result means the declaration is coherent. It neither executes a
benchmark nor certifies true task independence, a correct grader or measured
model performance. FSI-01 remains the inferential authority.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SCHEMA = "preferred-evals/v2"
CATALOG_SCHEMA = "preferred-evals/catalog-v2"
STAGES = {"exploration", "development", "confirmation"}
HARNESSES = {"prime_v1", "swebench", "inkling_verify", "paperbench", "mle_bench", "custom"}
JUDGES = {"deterministic", "formal", "human", "llm", "hybrid"}
SHAS = re.compile(r"^[0-9a-f]{64}$")


def _sha(value):
    return isinstance(value, str) and bool(SHAS.fullmatch(value))


def _object(value, field, errors):
    if isinstance(value, dict):
        return value
    errors.append(f"{field}: object required")
    return {}


def _nonempty(obj, field, errors):
    v = obj.get(field)
    if not isinstance(v, str) or not v.strip():
        errors.append(f"{field}: nonempty text required")
    return v


def catalog_check(data):
    errors = []
    if data.get("schema") != CATALOG_SCHEMA:
        errors.append("catalog schema must be preferred-evals/catalog-v2")
    categories = data.get("categories")
    benchmarks = data.get("benchmarks")
    if not isinstance(categories, list) or not categories:
        errors.append("catalog categories required")
        categories = []
    if not isinstance(benchmarks, list) or not benchmarks:
        errors.append("catalog benchmarks required")
        benchmarks = []
    slugs = [x.get("slug") for x in categories if isinstance(x, dict)]
    if len(slugs) != len(set(slugs)):
        errors.append("duplicate category slug")
    ids = [x.get("id") for x in benchmarks if isinstance(x, dict)]
    if len(ids) != len(set(ids)):
        errors.append("duplicate benchmark ID")
    for item in benchmarks:
        if not isinstance(item, dict):
            errors.append("catalog benchmark must be an object")
            continue
        if item.get("category") not in slugs:
            errors.append(f"unknown category for {item.get('id')}")
        if not str(item.get("url", "")).startswith("https://"):
            errors.append(f"benchmark {item.get('id')} requires https source")
        if item.get("access") is None or item.get("provider") is None:
            errors.append(f"benchmark {item.get('id')} lacks access or provider")
    return errors


def lint(spec, catalog):
    """Return errors, warnings and planning eligibility for one intended run."""
    errors, warnings = [], []
    if not isinstance(spec, dict):
        return {"schema": SCHEMA, "errors": ["manifest must be an object"], "warnings": [],
                "decision": "INVALID"}
    if spec.get("schema") != SCHEMA:
        errors.append("schema must be preferred-evals/v2")
    _nonempty(spec, "experiment_id", errors)
    stage = spec.get("stage")
    if stage not in STAGES:
        errors.append("stage must be exploration, development or confirmation")

    benches = {x["id"]: x for x in catalog.get("benchmarks", []) if isinstance(x, dict) and "id" in x}
    name = spec.get("benchmark_id")
    benchmark = benches.get(name)
    if benchmark is None:
        errors.append("benchmark_id must match a registered catalog benchmark")
    elif benchmark["access"] == "tasks_withheld":
        errors.append("benchmark tasks withheld: only original method may be cited, register an open proxy separately")
    elif benchmark["access"] == "permissioned_dataset":
        source = spec.get("provenance")
        if not isinstance(source, dict) or source.get("dataset_authorized") is not True:
            errors.append("permissioned benchmark requires provenance.dataset_authorized=true before evaluation")
    elif benchmark["access"] in {"restricted_verifiers", "public_subset_review_required"}:
        warnings.append("external benchmark has restricted or task-quality-limited access; certify source version and task rights")

    claim = _object(spec.get("claim"), "claim", errors)
    _nonempty(claim, "target_population", errors)
    _nonempty(claim, "primary_outcome", errors)
    if claim.get("planned_comparisons", 0) not in range(1, 100000):
        errors.append("claim.planned_comparisons must be a positive integer")
    for key in ("alpha", "minimum_effect"):
        x = claim.get(key)
        try:
            from fractions import Fraction
            if isinstance(x, bool) or not isinstance(x, (int, str)):
                raise ValueError()
            v = Fraction(x)
            if key == "alpha" and not (0 < v < 1):
                raise ValueError()
            if key == "minimum_effect" and not (0 <= v <= 1):
                raise ValueError()
        except (TypeError, ValueError, ZeroDivisionError):
            errors.append(f"claim.{key}: probability rational in range required")
    if type(claim.get("causal")) is not bool:
        errors.append("claim.causal explicit boolean required")

    samples = _object(spec.get("sampling"), "sampling", errors)
    _nonempty(samples, "independent_unit", errors)
    roots = samples.get("root_ids")
    if not isinstance(roots, list) or not roots or not all(isinstance(x, str) and x.strip() for x in roots):
        errors.append("sampling.root_ids: nonempty list of root strings required")
        roots = []
    if len(roots) != len(set(roots)):
        errors.append("sampling.root_ids: duplicates violate unit accounting")
    if type(samples.get("samples_per_root")) is not int or samples["samples_per_root"] < 1:
        errors.append("sampling.samples_per_root must be positive integer")
    for key in ("heldout_sealed", "selection_frozen", "root_independence_attested"):
        if type(samples.get(key)) is not bool:
            errors.append(f"sampling.{key} requires explicit true/false")
    _nonempty(samples, "split_name", errors)
    _nonempty(samples, "exposure", errors)
    if samples.get("exposure") not in {"development", "public_reused", "sealed"}:
        errors.append("sampling.exposure must be development, public_reused or sealed")
    if stage == "confirmation":
        if not samples.get("heldout_sealed") or samples.get("exposure") != "sealed":
            errors.append("confirmation requires sealed readout with no prior selection exposure")
        if not samples.get("selection_frozen"):
            errors.append("confirmation requires frozen selection and preregistered controls")
        if not samples.get("root_independence_attested"):
            errors.append("confirmation requires attested independent roots")
        if len(roots) < 20:
            errors.append("confirmation requires >=20 independent roots under default FSI-01 policy")
    elif samples.get("heldout_sealed") and samples.get("exposure") != "sealed":
        errors.append("sealed flag conflicts with exposure")
    if stage in {"exploration", "development"}:
        warnings.append("development or exploratory manifest: no prospective capability confirmation permitted")

    runner = _object(spec.get("runner"), "runner", errors)
    if runner.get("harness") not in HARNESSES:
        errors.append("runner.harness unknown")
    _nonempty(runner, "harness_version", errors)
    if runner.get("harness") == "prime_v1" and runner.get("api") != "verifiers.v1":
        errors.append("Prime adapter requires explicit verifiers.v1 API (not old import verifiers)")
    for key in ("model_id", "provider_id"):
        _nonempty(runner, key, errors)
    if not _sha(runner.get("harness_config_sha256")):
        errors.append("runner.harness_config_sha256 requires 64 hex characters")
    if runner.get("max_completion_tokens", 0) not in range(1, 100000000):
        errors.append("runner.max_completion_tokens must be positive integer")
    if type(runner.get("sampling_seed")) is not int:
        errors.append("runner.sampling_seed must be integer")
    resources = _object(runner.get("resources"), "runner.resources", errors)
    for base in ("cpu", "ram_gb"):
        floor, ceiling = resources.get(f"{base}_floor"), resources.get(f"{base}_ceiling")
        if not isinstance(floor, (int, float)) or isinstance(floor, bool) or floor <= 0:
            errors.append(f"runner.resources.{base}_floor must be positive")
        if not isinstance(ceiling, (int, float)) or isinstance(ceiling, bool) or ceiling <= 0:
            errors.append(f"runner.resources.{base}_ceiling must be positive")
        if isinstance(floor, (int, float)) and isinstance(ceiling, (int, float)) and floor > ceiling:
            errors.append(f"runner.resources.{base}_floor exceeds hard ceiling")
    if resources.get("network") not in {"disabled", "allowlisted", "enabled"}:
        errors.append("runner.resources.network must be declared")
    if type(resources.get("timeout_seconds")) is not int or resources["timeout_seconds"] < 1:
        errors.append("runner.resources.timeout_seconds must be positive integer")

    grader = _object(spec.get("grader"), "grader", errors)
    if grader.get("kind") not in JUDGES:
        errors.append("grader.kind unknown")
    _nonempty(grader, "version", errors)
    if not _sha(grader.get("sha256")):
        errors.append("grader.sha256 requires 64 hex characters")
    if grader.get("kind") in {"human", "llm", "hybrid"} and not grader.get("adjudication_or_calibration"):
        errors.append("non-deterministic grader requires adjudication_or_calibration reference")
    if grader.get("infra_failure_policy") != "separate":
        errors.append("infra_failure_policy must be separate from model failure")
    if grader.get("invalid_task_policy") not in {"report_all", "pre_audited"}:
        errors.append("invalid_task_policy must be report_all or pre_audited")
    if stage == "confirmation" and benchmark and benchmark.get("category") == "software-engineering":
        if grader.get("gold_check") not in {"passed", "not_applicable"}:
            errors.append("confirmation of SWE tasks requires a passed gold sanity check or justified not_applicable")
    if stage == "confirmation" and grader.get("invalid_task_policy") != "pre_audited":
        errors.append("confirmation requires invalid task set fixed by pre-score audit")

    controls = _object(spec.get("controls"), "controls", errors)
    _nonempty(controls, "baseline_id", errors)
    if claim.get("causal") and not controls.get("matched_sham_id"):
        errors.append("causal claim requires a physical matched sham control")
    if stage == "confirmation" and type(controls.get("registration_frozen")) is not bool:
        errors.append("controls.registration_frozen requires explicit true/false")
    if stage == "confirmation" and not controls.get("registration_frozen"):
        errors.append("confirmation requires frozen control registry")

    provenance = _object(spec.get("provenance"), "provenance", errors)
    for key in ("taskset_sha256", "runner_sha256", "selection_manifest_sha256"):
        if not _sha(provenance.get(key)):
            errors.append(f"provenance.{key} requires 64 hex characters")
    if type(provenance.get("hashes_verified")) is not bool:
        errors.append("provenance.hashes_verified requires explicit true/false")
    if stage == "confirmation" and not provenance.get("hashes_verified"):
        errors.append("confirmation requires externally verified hash provenance")
    elif not provenance.get("hashes_verified"):
        warnings.append("hash strings are unverified declarations, not provenance certificates")

    if errors:
        decision = "INVALID"
    elif stage == "confirmation":
        decision = "ELIGIBLE_FOR_EXTERNAL_CONFIRMATION_REVIEW"
    elif stage == "development":
        decision = "PILOT_ONLY"
    else:
        decision = "EXPLORATION_ONLY"
    return {"schema": SCHEMA, "experiment_id": spec.get("experiment_id"),
            "benchmark_id": name, "decision": decision,
            "n_independent_units_declared": len(roots),
            "planned_case_rows": len(roots) * samples.get("samples_per_root", 0)
            if type(samples.get("samples_per_root")) is int else None,
            "errors": errors, "warnings": warnings,
            "limits": "Manifest validation does not run a model, verify independence, or certify a result."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path(__file__).with_name("catalog.json"))
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    catalog = json.loads(args.catalog.read_text(encoding="utf-8"))
    errors = catalog_check(catalog)
    report = ({"catalog_schema": CATALOG_SCHEMA, "entries": len(catalog.get("benchmarks", [])),
               "errors": errors} if args.manifest is None
              else lint(json.loads(args.manifest.read_text(encoding="utf-8")), catalog))
    if errors and args.manifest is not None:
        report["errors"].extend("catalog: " + x for x in errors)
        report["decision"] = "INVALID"
    output = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 2 if report["errors"] and args.strict else 0


if __name__ == "__main__":
    raise SystemExit(main())
