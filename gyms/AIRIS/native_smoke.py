"""Unmodified upstream AIRIS smoke gate; a native failure remains BLOCKED."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile

UPSTREAM_COMMIT = "db19ad4e2cea33e6129c8bf03e85797da8cf7625"
UPSTREAM_BLOB = "7ea338b80275e62f1f42ea073bdad452df3474f7"
STATE = {"board": [[0, 0, 0, 0, 0]]}
ACTIONS = {"noop": None}


def blob_id(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def worker(source):
    if blob_id(source) != UPSTREAM_BLOB:
        raise ValueError("upstream source fingerprint mismatch")
    result = {"experiment": "AIRIS-02-smoke", "upstream_commit": UPSTREAM_COMMIT,
              "upstream_blob": UPSTREAM_BLOB, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "adapter_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "seed": 0, "max_actions": 1, "status": "BLOCKED_NATIVE",
              "state": STATE, "available_actions": ACTIONS, "tasks": {},
              "actions_applied": 0, "post_observations": 0}
    stdout = sys.stdout
    stage = "import"
    try:
        spec = importlib.util.spec_from_file_location("pinned_airis", source)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        random.seed(0)
        stage = "initialize"
        agent = mod.Airis(None, None)
        stage = "pre_capture_input"
        action = json.loads(agent.pre_capture_input(json.dumps(STATE), "{}",
                                                     json.dumps(ACTIONS), "{}"))
        result["proposed_action"] = action
        stage = "action_validation"
        if action not in (["noop", "None"], ["noop", None]):
            raise ValueError("unrecognized native action")
        # The simulator owns the only transition. A no-op leaves every bit fixed.
        result["actions_applied"] = 1
        stage = "post_capture_input"
        agent.post_capture_input(json.dumps(STATE), "{}", json.dumps(ACTIONS))
        result["post_observations"] = 1
        stage = "postcondition"
        if agent.time_step != 1:
            raise AssertionError("expected one native timestep")
        result["status"] = "PASS_WIRING_ONLY"
    except Exception as exc:
        result.update(failure_stage=stage, exception=type(exc).__name__, message=str(exc))
    finally:
        redirected = sys.stdout
        sys.stdout = stdout
        if redirected is not stdout:
            redirected.close()
    return result


def run(source):
    source = source.resolve(strict=True)
    if blob_id(source) != UPSTREAM_BLOB:
        raise ValueError("upstream source fingerprint mismatch")
    with tempfile.TemporaryDirectory(prefix="airis-native-") as tmp:
        cwd = Path(tmp)
        for name in ("airis logs", "training logs"):
            (cwd / name).mkdir()
        env = {"PATH": os.environ.get("PATH", ""), "PYTHONHASHSEED": "0",
               "PYTHONIOENCODING": "utf-8", "HOME": tmp}
        try:
            child = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                    str(source), "--worker"],
                                   cwd=cwd, env=env, capture_output=True, text=True,
                                   check=True, timeout=20)
        except subprocess.TimeoutExpired:
            return {"experiment": "AIRIS-02-smoke", "upstream_commit": UPSTREAM_COMMIT,
                    "upstream_blob": UPSTREAM_BLOB, "status": "BLOCKED_NATIVE_TIMEOUT",
                    "actions_applied": None, "post_observations": None,
                    "timeout_seconds": 20}
        return json.loads(child.stdout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    print(json.dumps(worker(args.source) if args.worker else run(args.source),
                     sort_keys=True, indent=2))
