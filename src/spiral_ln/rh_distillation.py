"""CPU-only source audit and optional Lean-kernel reconstruction gym.

Import traversal is a *module* graph, not a proof-term dependency graph.
No external source is downloaded or silently trusted by this module.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import time


INTERNAL_ROOTS = frozenset({
    "Development", "Formalism", "GroundTheory", "ReciprocityTheory",
    "CompanionTheory", "PositivityTheory", "Lemmata", "Supplements", "BuildAid",
    "Statements", "Main",
})
BANNED = re.compile(r"\b(?:sorry|admit|axiom|unsafe|native_decide)\b")
DECL_PREFIX = re.compile(r"\b(?:theorem|def)\s+")
MODULE_NAME = re.compile(r"^[\w.]+$", re.UNICODE)


def git_blob_sha(raw: bytes) -> str:
    """Git's content blob hash, which is distinct from an ordinary SHA-1."""
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def parse_imports(source: str) -> list[str]:
    imports: list[str] = []
    for line in source.splitlines():
        line = line.split("--", 1)[0]
        match = re.match(r"^\s*import\s+(.+?)\s*$", line)
        if match:
            imports.extend(part for part in match.group(1).split() if MODULE_NAME.fullmatch(part))
    return imports


def module_path(src: Path, module: str) -> Path:
    return src.joinpath(*module.split(".")).with_suffix(".lean")


def family(module: str) -> str:
    name = module.lower()
    for label, terms in (
        ("analytic", ("landau", "dedekindl", "primitivecoset", "characterbox")),
        ("theta", ("theta", "weil", "fock")),
        ("galois", ("galois", "cohomology", "iwasawa", "crystalline")),
        ("arithmetic_geometry", ("abelianvariety", "moduli", "hilbertsamuel", "covolume", "toroidal")),
        ("representation", ("representation", "langlands", "automorphic")),
    ):
        if any(term in name for term in terms):
            return label
    return "other"


def walk_imports(src: Path, roots: list[str], limit: int = 1000) -> dict:
    """BFS module imports, bounded by limit (0 means unlimited)."""
    todo = deque((root, None) for root in roots)
    visited: set[str] = set()
    parents: dict[str, str | None] = {}
    edges: list[tuple[str, str]] = []
    unresolved: set[str] = set()
    external: set[str] = set()
    while todo and (limit == 0 or len(visited) < limit):
        module, parent = todo.popleft()
        if module in visited:
            continue
        path = module_path(src, module)
        if not path.is_file():
            (unresolved if module.split(".")[0] in INTERNAL_ROOTS else external).add(module)
            continue
        visited.add(module)
        parents[module] = parent
        for dep in parse_imports(path.read_text(encoding="utf-8")):
            edges.append((module, dep))
            if dep not in visited:
                todo.append((dep, module))
    return {
        "mode": "module_imports_only",
        "visited_modules": len(visited),
        "import_edges": len(edges),
        "truncated": bool(todo),
        "unresolved_internal_imports": sorted(unresolved),
        "external_imports": sorted(external),
        "family_counts": dict(sorted(Counter(map(family, visited)).items())),
        "parents": parents,
    }


def anchor_audit(repository_root: Path, manifest: dict) -> list[dict]:
    results: list[dict] = []
    for anchor in manifest["anchors"]:
        path = repository_root / anchor["path"]
        if not path.is_file():
            results.append({"id": anchor["id"], "status": "missing"})
            continue
        raw = path.read_bytes()
        content = raw.decode("utf-8")
        decl = anchor["declaration"]
        expression = DECL_PREFIX.pattern + re.escape(decl) + r"(?![\w'])"
        results.append({
            "id": anchor["id"],
            "status": "match" if git_blob_sha(raw) == anchor["blob_sha"] and re.search(expression, content) else "mismatch",
            "blob_sha": git_blob_sha(raw),
            "declaration_present": bool(re.search(expression, content)),
        })
    return results


def validate_tasks(tasks: list[dict]) -> None:
    seen: set[str] = set()
    for task in tasks:
        identifier = task["id"]
        if identifier in seen:
            raise ValueError(f"duplicate task: {identifier}")
        seen.add(identifier)
        if task["template"].count("__PROOF__") != 1:
            raise ValueError(f"one proof hole required: {identifier}")
        if BANNED.search(task["template"]):
            raise ValueError(f"forbidden declaration in template: {identifier}")


def render_proof(template: str, proof: str) -> str:
    if not proof.strip() or BANNED.search(proof):
        raise ValueError("empty or forbidden proof")
    return template.replace("__PROOF__", "\n".join("  " + line for line in proof.strip().splitlines()))


def compile_lean(source: str, cwd: Path, command: str, timeout: float) -> tuple[bool, str, float]:
    start = time.monotonic()
    fd, file_name = tempfile.mkstemp(prefix="rh_distill_", suffix=".lean", dir=cwd)
    path = Path(file_name)
    try:
        import os
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(source)
        try:
            proc = subprocess.run(shlex.split(command) + [str(path)], cwd=cwd,
                                  text=True, capture_output=True, timeout=timeout, check=False)
            output = (proc.stdout + "\n" + proc.stderr)[-1800:]
            return proc.returncode == 0 and "declaration uses 'sorry'" not in output, output, time.monotonic() - start
        except (OSError, subprocess.TimeoutExpired) as exc:
            return False, str(exc), time.monotonic() - start
    finally:
        path.unlink(missing_ok=True)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def score(tasks: list[dict], submissions: list[dict], checker) -> dict:
    """Only checker may grant a pass; the normal checker invokes Lean."""
    validate_tasks(tasks)
    reference = {task["id"]: task for task in tasks}
    seen: set[str] = set()
    outcomes: list[dict] = []
    for submission in submissions:
        identifier = submission.get("id")
        if identifier in seen:
            outcomes.append({"id": identifier, "status": "duplicate", "pass": False})
            continue
        seen.add(identifier)
        if identifier not in reference:
            outcomes.append({"id": identifier, "status": "unknown", "pass": False})
            continue
        try:
            source = render_proof(reference[identifier]["template"], submission.get("proof", ""))
        except ValueError as exc:
            outcomes.append({"id": identifier, "status": "rejected", "pass": False, "detail": str(exc)})
            continue
        passed, detail, seconds = checker(source)
        outcomes.append({"id": identifier, "status": "compiled" if passed else "compile_failed",
                         "pass": passed, "seconds": round(seconds, 4), "detail": detail})
    return {"kind": "lean_kernel_compile", "total_tasks": len(tasks),
            "submitted": len(submissions), "passes": sum(x["pass"] for x in outcomes),
            "outcomes": outcomes}


def main() -> None:
    base = Path(__file__).resolve().parents[2] / "gyms" / "RHProofDistillation"
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="action", required=True)
    pre = sub.add_parser("preflight", help="validate manifest and task structure without Lean")
    pre.add_argument("--manifest", type=Path, default=base / "anchors.json")
    pre.add_argument("--tasks", type=Path, default=base / "tasks.json")
    audit = sub.add_parser("audit", help="verify source blobs and bounded module-import DAG")
    audit.add_argument("--source-root", type=Path, required=True, help="checkout root containing src/")
    audit.add_argument("--manifest", type=Path, default=base / "anchors.json")
    audit.add_argument("--limit", type=int, default=5000)
    audit.add_argument("--output", type=Path)
    grade = sub.add_parser("grade", help="grade proof submissions using the Lean kernel")
    grade.add_argument("--tasks", type=Path, default=base / "tasks.json")
    grade.add_argument("--submissions", type=Path, required=True)
    grade.add_argument("--lean-cwd", type=Path, default=Path("lean"))
    grade.add_argument("--lean-cmd", default="lake env lean")
    grade.add_argument("--timeout", type=float, default=45)
    grade.add_argument("--output", type=Path)
    grade.add_argument("--require-all", action="store_true", help="exit 1 unless every task compiles")
    args = ap.parse_args()
    if args.action == "preflight":
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        tasks = json.loads(args.tasks.read_text(encoding="utf-8"))
        validate_tasks(tasks)
        assert len({a["id"] for a in manifest["anchors"]}) == len(manifest["anchors"])
        assert all(len(a["blob_sha"]) == 40 for a in manifest["anchors"])
        result = {"status": "preflight_pass", "source_commit": manifest["mirror_commit"],
                  "anchors": len(manifest["anchors"]), "proxy_tasks": len(tasks),
                  "lean_compiled": False}
    elif args.action == "audit":
        if args.limit < 0:
            ap.error("--limit must be nonnegative")
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        audit_result = anchor_audit(args.source_root, manifest)
        result = {"source_commit_expected": manifest["mirror_commit"],
                  "anchors": audit_result,
                  "import_graph": walk_imports(args.source_root / "src", ["Main"], args.limit),
                  "note": "Module import closure does not establish theorem/term dependencies"}
    else:
        tasks = json.loads(args.tasks.read_text(encoding="utf-8"))
        submission = read_jsonl(args.submissions)
        cwd = args.lean_cwd.resolve()
        if not cwd.is_dir():
            ap.error(f"Lean working directory not found: {cwd}")
        result = score(tasks, submission, lambda src: compile_lean(src, cwd, args.lean_cmd, args.timeout))
    encoded = json.dumps(result, indent=2, sort_keys=True)
    output = getattr(args, "output", None)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    if args.action == "grade" and args.require_all and result["passes"] != len(tasks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
