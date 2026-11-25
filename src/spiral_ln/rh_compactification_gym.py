"""Lean-native recurrence curriculum and bounded proof-revision episodes.

Every challenge is compiled with its source prefix. The completed target and
later declarations are absent from that environment. Hilbert certificates are
provenance for the curriculum, never accepted as Lean proof certificates here.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import tempfile
import textwrap
import time
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "gyms" / "RHCompactification"
LEAN_SOURCE = ROOT / "lean" / "FeedbackChannel" / "RHCompactification.lean"
NAMESPACE = "FeedbackChannel.RHCompactification"
FAMILY = "rh-recurrence-construction-v1"
EXPECTED_LEAN = "4.34.1"
ALLOWED_AXIOMS = frozenset({"propext", "Classical.choice", "Quot.sound"})
MAX_PROOF_BYTES = 16384
MARKER = re.compile(r"^-- RHGYM-BEGIN (\w+)\n(.*?)^-- RHGYM-END \1\s*$", re.M | re.S)
DECL = re.compile(r"\b(theorem|def)\s+([A-Za-z_][A-Za-z_0-9]*)\b")
FORBIDDEN = re.compile(
    r"\b(?:sorry|admit|axiom|unsafe|native_decide|run_tac|run_elab|run_cmd|"
    r"elab|syntax|macro|declare_syntax_cat|attribute|import|namespace|end|section|"
    r"variable|universe|def|abbrev|opaque|instance|inductive|structure|class|theorem|"
    r"lemma|example|mutual|termination_by|decreasing_by|set_option|open|export|"
    r"private|protected|partial|noncomputable|deriving|include|omit|local|scoped|"
    r"trace|trace_state|dbg_trace|eval_expr)\b|\b(?:Lean|IO|System)\."
)

# Each row remains in one public training family, including every later variant.
TASKS = (
    ("extend_before", "finite_prefix", "Preserve values before an extension", "RH-PL-14"),
    ("prefix_restrict", "finite_prefix", "Restrict a prefix to a smaller endpoint", "RH-PL-15"),
    ("prefix_extend", "finite_prefix", "Extend the recurrence by one point", "RH-PL-15"),
    ("prefix_agreement", "overlap", "Prove agreement on the common domain", "RH-PL-15"),
    ("prefix_exists", "finite_prefix", "Construct every finite prefix", "RH-PL-15"),
    ("prefix_graph_domain", "overlap", "Recover the exact bounded graph domain", "RH-PL-15"),
    ("prefix_graph_overlap", "overlap", "Transfer prefix agreement to graph values", "RH-PL-15"),
    ("glue_agrees", "gluing", "Compare the diagonal with any longer prefix", "RH-PL-15"),
    ("glued_graph_iff", "gluing", "Identify the union graph with the diagonal", "RH-PL-15"),
    ("glue_succ", "gluing", "Recover the recurrence after gluing", "RH-PL-15"),
    ("recurrence_unique", "recursion", "Prove uniqueness of a global recurrence", "RH-PL-15"),
    ("recurrence_exists_unique", "recursion", "Package recurrence existence and uniqueness", "RH-PL-15"),
    ("glue_eq_orbit", "recursion", "Identify the glued function with primitive recursion", "RH-PL-15"),
    ("denominator_unique", "denominator", "Identify a denominator from its equations", "RH-PL-16"),
    ("denominator_step_to_exact", "denominator", "Supply the existential evaluation witnesses", "RH-PL-16"),
    ("denominator_exact_to_step", "denominator", "Recover a step from existential witnesses", "RH-PL-16"),
    ("denominator_exact_unique", "denominator", "Combine the bridge with uniqueness", "RH-PL-16"),
    ("joint_denominator", "joint_recurrence", "Identify the denominator component", "RH-PL-17"),
    ("numerator_succ", "joint_recurrence", "Expose the numerator update", "RH-PL-17"),
    ("joint_components_unique", "joint_recurrence", "Recover both components from their equations", "RH-PL-17"),
)


def sha256(value: str | bytes) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def json_text(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def extract_tasks(source: str) -> tuple[list[dict], list[dict]]:
    """Extract an ordered, prefix-only environment from marked trusted source."""
    blocks = list(MARKER.finditer(source))
    names = [match.group(1) for match in blocks]
    if len(names) != len(set(names)) or not blocks:
        raise ValueError("source markers must be nonempty and unique")
    if source.count("-- RHGYM-BEGIN ") != len(blocks) or source.count("-- RHGYM-END ") != len(blocks):
        raise ValueError("unmatched source marker")
    by_name = {match.group(1): (i, match) for i, match in enumerate(blocks)}
    tasks, teachers = [], []
    previous = -1
    for number, (name, stage, title, anchor) in enumerate(TASKS, 1):
        if name not in by_name:
            raise ValueError(f"missing curriculum target: {name}")
        index, match = by_name[name]
        if index <= previous:
            raise ValueError("curriculum is not in declaration order")
        previous = index
        declaration = match.group(2)
        start = re.search(r"^theorem " + re.escape(name) + r"\b", declaration, re.M)
        if start is None:
            raise ValueError(f"target is not a theorem: {name}")
        declaration = declaration[start.start():].strip()
        if ":= by\n" not in declaration:
            raise ValueError(f"target requires an explicit tactic proof: {name}")
        statement, proof = declaration.split(":= by\n", 1)
        proof = textwrap.dedent(proof).strip()
        context = source[:match.start()].rstrip() + "\n\n"
        task = {
            "id": f"RHCG-{number:03d}", "declaration": name,
            "qualified_name": f"{NAMESPACE}.{name}", "stage": stage, "title": title,
            "order": number, "family": FAMILY, "split": "train",
            "statement": statement.rstrip(), "context": context,
            "available_declarations": names[:index], "unavailable_declarations": names[index:],
            "source": "lean/FeedbackChannel/RHCompactification.lean",
            "source_sha256": sha256(source), "context_sha256": sha256(context),
            "statement_sha256": sha256(statement.rstrip()),
            "hilbert_stage": anchor, "fidelity": "Lean Nat/function analogue; no calculus translation",
        }
        check_proof_surface(task, proof)
        task["reference_source_bytes"] = len(render(task, proof).encode("utf-8"))
        tasks.append(task)
        teachers.append({"id": task["id"], "proof": proof, "proof_sha256": sha256(proof), "split": "train"})
    return tasks, teachers


def check_proof_surface(task: dict, proof: str) -> None:
    """Accept proof bodies only; the caller supplies every declaration and import.

    This is a restricted input language, not an operating-system sandbox. The
    supported interface is ordinary Init tactics/terms, without elaborator
    extensions, commands, comments, strings, quotations, or executable tactics.
    """
    if not isinstance(proof, str) or not proof.strip():
        raise ValueError("a nonempty proof body is required")
    if len(proof.encode("utf-8")) > MAX_PROOF_BYTES or len(proof.splitlines()) > 256:
        raise ValueError("proof exceeds the fixed input budget")
    if any(ord(c) < 32 and c not in "\n\t\r" for c in proof):
        raise ValueError("control character in proof")
    if any(token in proof for token in ('--', '/-', '-/', '#', '"', '`', '«', '»')) or FORBIDDEN.search(proof):
        raise ValueError("proof contains a command or unsupported syntax")
    for name in task.get("unavailable_declarations", []):
        if re.search(r"(?<![\w'])" + re.escape(name) + r"(?![\w'])", proof):
            raise ValueError(f"target or later declaration unavailable: {name}")


def render(task: dict, proof: str) -> str:
    return (task["context"] + task["statement"] + " := by\n" + textwrap.indent(proof.strip(), "  ")
            + f"\n\nend {NAMESPACE}\n\n#print axioms {task['qualified_name']}\n")


def parse_axioms(output: str, qualified_name: str) -> list[str] | None:
    escaped = re.escape(qualified_name)
    reports = re.findall(r"'" + escaped + r"' depends on axioms: \[([^\]]*)\]", output, re.S)
    empty = re.findall(r"'" + escaped + r"' does not depend on any axioms", output)
    if len(reports) + len(empty) != 1:
        return None
    return sorted({x.strip() for x in reports[0].replace("\n", " ").split(",") if x.strip()}) if reports else []


class LeanChecker:
    """One fresh Lean process per submitted candidate, with an axiom audit."""

    def __init__(self, command: list[str], cwd: Path, timeout: float = 20,
                 expected_version: str = EXPECTED_LEAN, allow_version_mismatch: bool = False):
        if not command or not cwd.is_dir() or not 0 < timeout <= 60:
            raise ValueError("invalid Lean command, working directory, or timeout")
        self.command, self.cwd, self.timeout = list(command), cwd.resolve(), timeout
        version = subprocess.run(command + ["--version"], cwd=cwd, capture_output=True, text=True, timeout=20)
        if version.returncode:
            raise RuntimeError("Lean version probe failed: " + version.stderr[-1000:])
        self.version = version.stdout.strip()
        parsed = re.search(r"version\s+(\d+\.\d+\.\d+)", self.version)
        self.toolchain_matches = bool(parsed and parsed.group(1) == expected_version)
        if not self.toolchain_matches and not allow_version_mismatch:
            raise RuntimeError(f"expected Lean {expected_version}; got {self.version}")
        prefix = subprocess.run(command + ["--print-prefix"], cwd=cwd, capture_output=True, text=True, timeout=20)
        binary = Path(prefix.stdout.strip()) / "bin" / "lean"
        self.environment = {
            "backend": "lean4_direct_compile_with_axiom_audit", "lean_version": self.version,
            "expected_version": expected_version, "toolchain_matches": self.toolchain_matches,
            "lean_sha256": sha256(binary.read_bytes()) if prefix.returncode == 0 and binary.is_file() else None,
            "checker_sha256": sha256(Path(__file__).read_bytes()),
            "timeout_s": timeout, "memory_limit_mib": 768, "max_heartbeats": 400000,
        }

    def compile_source(self, source: str, qualified_name: str) -> dict:
        """Compile a trusted harness. Raw user commands must never reach here."""
        start = time.monotonic()
        base = {"source_sha256": sha256(source), "charged_source_bytes": len(source.encode("utf-8")),
                "kernel_calls": 1, "verifier": "lean4_direct_compile_with_axiom_audit"}
        with tempfile.TemporaryDirectory(prefix="rhcg_") as temporary:
            path = Path(temporary) / "Candidate.lean"
            path.write_text(source, encoding="utf-8")
            env = {key: value for key, value in os.environ.items()
                   if not key.startswith(("AWS_", "AZURE_", "OPENAI_", "GH_", "GITHUB_"))
                   and "TOKEN" not in key and "SECRET" not in key}
            command = self.command + ["-M", "768", "-j", "1", "-D", "maxHeartbeats=400000", str(path)]
            try:
                process = subprocess.Popen(command, cwd=self.cwd, env=env, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE, text=True, start_new_session=True)
                try:
                    stdout, stderr = process.communicate(timeout=self.timeout)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    stdout, stderr = process.communicate()
                    return {**base, "label": None, "closed": False, "kernel_ok": False,
                            "status": "timeout", "axioms": [], "diagnostic": "Lean time budget exhausted"}
            except OSError as exc:
                return {**base, "kernel_calls": 0, "label": None, "closed": False, "kernel_ok": False,
                        "status": "infrastructure_error", "axioms": [], "diagnostic": str(exc)}
            output = (stdout + "\n" + stderr).replace(str(path), "Candidate.lean").replace(temporary, "<temporary>")
            axioms = parse_axioms(output, qualified_name)
            accepted = (process.returncode == 0 and axioms is not None
                        and set(axioms) <= ALLOWED_AXIOMS and "sorry" not in output.lower())
            lower = output.lower()
            resource_failure = process.returncode < 0 or any(marker in lower for marker in (
                "out of memory", "memory allocation", "maximum number of heartbeats", "maximum recursion depth",
                "stack overflow", "(deterministic) timeout", "excessive memory", "memory limit"))
            infrastructure_failure = any(marker in lower for marker in (
                "failed to import", "failed to read", "cannot load", "unknown module prefix", "object file"))
            if accepted:
                label, status = 1, "accepted"
            elif resource_failure:
                label, status = None, "resource_exhausted"
            elif infrastructure_failure:
                label, status = None, "infrastructure_error"
            elif axioms is not None and (set(axioms) - ALLOWED_AXIOMS or "sorry" in lower):
                label, status = 0, "rejected_axioms"
            elif process.returncode != 0 and "error:" in lower:
                label, status = 0, "rejected_by_lean"
            else:
                label, status = None, "audit_unavailable"
            return {**base, "label": label, "closed": accepted, "kernel_ok": accepted,
                    "status": status, "axioms": axioms or [],
                    "returncode": process.returncode, "diagnostic": output.strip()[-6000:],
                    "seconds": round(time.monotonic() - start, 6)}

    def check(self, task: dict, proof: str) -> dict:
        try:
            check_proof_surface(task, proof)
        except ValueError as exc:
            return {"label": 0, "closed": False, "kernel_ok": False, "kernel_calls": 0,
                    "status": "rejected_by_surface", "axioms": [], "diagnostic": str(exc)}
        result = self.compile_source(render(task, proof), task["qualified_name"])
        return {**result, "proof_sha256": sha256(proof.strip()),
                "proof_bytes": len(proof.strip().encode("utf-8")),
                "statement_sha256": task["statement_sha256"]}


@dataclass
class RevisionGym:
    """A full-proof correction loop; recurrent model architecture stays external."""
    tasks: list[dict]
    checker: Callable[[dict, str], dict]
    max_attempts: int = 4

    def __post_init__(self) -> None:
        if not 1 <= self.max_attempts <= 32:
            raise ValueError("max_attempts must be in 1..32")
        self.by_id = {task["id"]: deepcopy(task) for task in self.tasks}
        if len(self.by_id) != len(self.tasks):
            raise ValueError("duplicate task id")
        self._task_hashes = {key: sha256(json_text(value)) for key, value in self.by_id.items()}
        self.task = None
        self.history: list[dict] = []
        self.best: dict | None = None
        self.potential = Fraction(0)

    def reset(self, task_id: str) -> dict:
        if task_id not in self.by_id:
            raise ValueError("unknown task")
        self.task, self.history, self.best, self.potential = self.by_id[task_id], [], None, Fraction(0)
        return self.observe()

    def observe(self) -> dict:
        if self.task is None:
            raise ValueError("reset is required")
        return {"task": deepcopy(self.task), "attempts_used": len(self.history),
                "attempts_remaining": self.max_attempts - len(self.history),
                "best_verified_proof": self.best["proof"] if self.best else None,
                "feedback": deepcopy(self.history[-1]["verification"]) if self.history else None,
                "done": len(self.history) >= self.max_attempts}

    def step(self, proof: str) -> dict:
        if self.task is None or len(self.history) >= self.max_attempts:
            raise ValueError("episode absent or exhausted")
        if not isinstance(proof, str):
            raise ValueError("proof must be a string")
        if sha256(json_text(self.task)) != self._task_hashes[self.task["id"]]:
            raise ValueError("task changed after episode construction")
        verification = self.checker(deepcopy(self.task), proof)
        old = self.potential
        if (verification.get("label") == 1 and verification.get("closed") is True
                and verification.get("kernel_ok") is True and verification.get("kernel_calls") == 1
                and set(verification.get("axioms", [])) <= ALLOWED_AXIOMS):
            size = verification["charged_source_bytes"]
            if self.best is None or size < self.best["charged_source_bytes"]:
                self.best = {"proof": proof, "charged_source_bytes": size, "verification": verification}
                reference = self.task["reference_source_bytes"]
                self.potential = Fraction(1) + max(Fraction(0), Fraction(reference - size, reference))
        row = {"attempt": len(self.history) + 1, "proof": proof, "verification": verification,
               "reward": str(self.potential - old), "potential": str(self.potential)}
        self.history.append(row)
        return {**self.observe(), "reward": row["reward"], "potential": row["potential"],
                "lean_invocations": sum(r["verification"].get("kernel_calls", 0) for r in self.history)}


def build_bundle(output: Path = BASE) -> dict:
    source = LEAN_SOURCE.read_text(encoding="utf-8")
    tasks, teachers = extract_tasks(source)
    output.mkdir(parents=True, exist_ok=True)
    write_jsonl(output / "tasks.jsonl", tasks)
    write_jsonl(output / "teachers.jsonl", teachers)
    manifest = {
        "schema": "EvalMath/rh-compactification-curriculum/v1", "language": "Lean 4",
        "expected_lean": EXPECTED_LEAN, "source": str(LEAN_SOURCE.relative_to(ROOT)),
        "source_sha256": sha256(source), "tasks": len(tasks), "independent_families": 1,
        "family": FAMILY, "splits": {"train": [task["id"] for task in tasks]},
        "confirmation": {"status": "unallocated", "scored": False},
        "evidence": "Lean theorem curriculum; public training/development only",
        "task_file": "tasks.jsonl", "tasks_sha256": sha256((output / "tasks.jsonl").read_bytes()),
        "teacher_file": "teachers.jsonl", "teachers_sha256": sha256((output / "teachers.jsonl").read_bytes()),
        "stages": list(dict.fromkeys(task["stage"] for task in tasks)),
        "metric": "UTF-8 bytes of the complete supplied Lean source, including all prefix declarations",
        "episode": {"max_attempts_default": 4, "max_proof_bytes": MAX_PROOF_BYTES,
                    "reward": "Change in verified-best potential: 1 + max(0,(reference-source_bytes)/reference)",
                    "invalid_or_unknown_reward": "0", "equal_budget_unit": "submitted candidate attempt"},
        "scope": "Nat/function analogue of RH-PL-14 through RH-PL-17; Hilbert proof bytes remain separate",
    }
    (output / "curriculum.json").write_text(json_text(manifest), encoding="utf-8")
    return manifest


def load_bundle(base: Path = BASE) -> tuple[dict, list[dict], list[dict]]:
    manifest = json.loads((base / "curriculum.json").read_text(encoding="utf-8"))
    source = LEAN_SOURCE.read_text(encoding="utf-8")
    if (manifest.get("schema") != "EvalMath/rh-compactification-curriculum/v1"
            or manifest.get("source") != str(LEAN_SOURCE.relative_to(ROOT))
            or manifest.get("source_sha256") != sha256(source)
            or manifest.get("expected_lean") != EXPECTED_LEAN
            or manifest.get("task_file") != "tasks.jsonl" or manifest.get("teacher_file") != "teachers.jsonl"
            or manifest.get("tasks") != len(TASKS) or manifest.get("family") != FAMILY):
        raise ValueError("manifest source identity or curriculum schema mismatch")
    tasks, teachers = read_jsonl(base / "tasks.jsonl"), read_jsonl(base / "teachers.jsonl")
    if sha256((base / "tasks.jsonl").read_bytes()) != manifest["tasks_sha256"]:
        raise ValueError("task file hash mismatch")
    if sha256((base / "teachers.jsonl").read_bytes()) != manifest["teachers_sha256"]:
        raise ValueError("teacher file hash mismatch")
    expected_tasks, expected_teachers = extract_tasks(source)
    if tasks != expected_tasks or teachers != expected_teachers:
        raise ValueError("bundle differs from the current source prefix extraction")
    if manifest["splits"] != {"train": [t["id"] for t in tasks]} or manifest["independent_families"] != 1:
        raise ValueError("current curriculum must remain one training family")
    return manifest, tasks, teachers


def verify_teachers(checker: LeanChecker, base: Path = BASE) -> dict:
    manifest, tasks, teachers = load_bundle(base)
    outcomes = []
    for task, teacher in zip(tasks, teachers, strict=True):
        if task["id"] != teacher["id"]:
            raise ValueError("teacher alignment mismatch")
        outcome = checker.check(task, teacher["proof"])
        outcomes.append({"id": task["id"], **outcome})
    return {"schema": "EvalMath/rh-compactification-native-replay/v1", "environment": checker.environment,
            "tasks": len(tasks), "passes": sum(row["label"] == 1 for row in outcomes),
            "source_sha256": manifest["source_sha256"], "outcomes": outcomes}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=BASE)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("build", help="regenerate the source-derived public training curriculum")
    sub.add_parser("check", help="check source, split, context and artifact hashes without Lean")
    for name in ("verify", "grade", "serve"):
        p = sub.add_parser(name)
        p.add_argument("--lean-cmd", default="lake env lean")
        p.add_argument("--lean-cwd", type=Path, default=ROOT / "lean")
        p.add_argument("--timeout", type=float, default=20)
        p.add_argument("--allow-toolchain-mismatch", action="store_true")
        if name != "serve":
            p.add_argument("--output", type=Path)
        if name == "grade":
            p.add_argument("--submissions", type=Path, required=True)
        if name == "serve":
            p.add_argument("--max-attempts", type=int, default=4)
    args = parser.parse_args()
    if args.action == "build":
        result = build_bundle(args.base)
    elif args.action == "check":
        manifest, tasks, _ = load_bundle(args.base)
        result = {"status": "source_and_schema_checked", "tasks": len(tasks),
                  "independent_families": manifest["independent_families"], "native_replay_performed": False}
    else:
        checker = LeanChecker(shlex.split(args.lean_cmd), args.lean_cwd, args.timeout,
                              allow_version_mismatch=args.allow_toolchain_mismatch)
        if args.action == "verify":
            result = verify_teachers(checker, args.base)
        else:
            _, tasks, _ = load_bundle(args.base)
            if args.action == "serve":
                import sys
                gym = RevisionGym(tasks, checker.check, args.max_attempts)
                for line in sys.stdin:
                    try:
                        request = json.loads(line)
                        if request.get("op") == "reset":
                            result = gym.reset(request["id"])
                        elif request.get("op") == "step":
                            result = gym.step(request["proof"])
                        elif request.get("op") == "close":
                            break
                        else:
                            raise ValueError("op must be reset, step, or close")
                    except (ValueError, KeyError, TypeError) as exc:
                        result = {"error": str(exc)}
                    print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
                return
            lookup = {task["id"]: task for task in tasks}
            rows, seen = [], set()
            for submission in read_jsonl(args.submissions):
                task_id = submission.get("id")
                if task_id in seen or task_id not in lookup:
                    rows.append({"id": task_id, "label": 0, "status": "duplicate_or_unknown"})
                    continue
                seen.add(task_id)
                rows.append({"id": task_id, **checker.check(lookup[task_id], submission.get("proof", ""))})
            result = {"environment": checker.environment, "outcomes": rows,
                      "passes": sum(row["label"] == 1 for row in rows), "submitted": len(rows),
                      "total_tasks": len(tasks), "independent_families": 1}
    if getattr(args, "output", None):
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json_text(result), encoding="utf-8")
        print(json_text({key: value for key, value in result.items() if key != "outcomes"}), end="")
    else:
        print(json_text(result), end="")
    if args.action == "verify" and result["passes"] != result["tasks"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
