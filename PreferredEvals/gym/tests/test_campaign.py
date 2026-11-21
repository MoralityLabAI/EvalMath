"""Campaign ledger, scorecard and FSI pairing; generated multi-hop set; SWE oracle scoring (stdlib only)."""
import json
import re
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build_public_sets import multihop  # noqa: E402
from campaign import collect, paired, summarize_run, _holm  # noqa: E402
from swebench_oracle import score as swe_score  # noqa: E402


def _eval_chain(question: str, target: str) -> int:
    env = {}
    lines = [l for l in question.splitlines() if re.fullmatch(r"\w+ = .+", l)]
    while target not in env:
        progressed = False
        for line in lines:
            name, expr = line.split(" = ")
            if name in env:
                continue
            parts = expr.split()
            if len(parts) == 1:
                env[name] = int(parts[0]); progressed = True
            elif parts[0] in env:
                a, op, c = env[parts[0]], parts[1], int(parts[2])
                env[name] = a + c if op == "+" else a - c if op == "-" else a * c
                progressed = True
        if not progressed:
            raise AssertionError("unresolvable chain")
    return env[target]


class MultihopSet(unittest.TestCase):
    def test_labels_match_the_chains_and_build_is_deterministic(self):
        with TemporaryDirectory() as td:
            a = multihop(Path(td) / "a", per_depth=2, seed=7)
            b = multihop(Path(td) / "b", per_depth=2, seed=7)
            self.assertEqual(a["tasks_sha256"], b["tasks_sha256"])
            tasks = [json.loads(l) for l in (Path(td) / "a" / "tasks.jsonl").read_text().splitlines()]
            labels = {json.loads(l)["task_id"]: json.loads(l)["answer"]
                      for l in (Path(td) / "a" / "labels.jsonl").read_text().splitlines()}
            self.assertEqual(len(tasks), 8)
            for t in tasks:
                target = re.search(r"What is the value of (\w+)\?", t["question"]).group(1)
                self.assertEqual(str(_eval_chain(t["question"], target)), labels[t["task_id"]])
                self.assertNotIn("answer", t)
            self.assertNotIn(b"\r", (Path(td) / "a" / "tasks.jsonl").read_bytes())


def _prompt_run(folder: Path, scores):
    folder.mkdir(parents=True)
    rows = []
    receipts = []
    for i, s in enumerate(scores):
        tid = f"t{i}"
        status = "completed" if s is not None else "infrastructure_error"
        rows.append({"task_id": tid, "root_id": f"r{i}", "sample": 0, "order": "normal", "status": status,
                     "format_valid": s is not None, "score": s})
        receipts.append({"task_id": tid, "order": "normal", "sample": 0, "status": status,
                         "usage": {"prompt_tokens": 10, "completion_tokens": 2}, "duration_seconds": 0.5})
    (folder / "scores.json").write_text(json.dumps({"rows": rows}))
    (folder / "rollouts.jsonl").write_text("\n".join(json.dumps(r) for r in receipts) + "\n")


class CampaignLedger(unittest.TestCase):
    def test_outcomes_roots_and_pairing(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            _prompt_run(root / "runs" / "a", [1, 1, 0, None])
            _prompt_run(root / "runs" / "b", [0, 1, 0, 0])
            spec = {"runs": {"a": {"kind": "prompt", "benchmark": "x", "category": "c", "model": "m1"},
                             "b": {"kind": "prompt", "benchmark": "x", "category": "c", "model": "m2"},
                             "missing": {"kind": "prompt", "benchmark": "x", "category": "c", "model": "m3"}}}
            ledger = collect(root, spec)
            self.assertNotIn("missing", ledger)
            s = summarize_run(ledger["a"])
            self.assertEqual((s["attempts"], s["scored"], s["correct"]), (4, 3, 2))
            self.assertEqual(s["outcomes"], {"correct": 2, "infrastructure_error": 1, "wrong": 1})
            p = paired(ledger, "a", "b", {"id": "a-vs-b", "alpha": "0.05", "minimum_effect": "0.10",
                                         "planned_comparisons": 1, "preregistered": True,
                                         "clusters_independent": True, "exchangeable_pair_labels": True})
            self.assertEqual(p["n_paired_attempts"], 3)
            self.assertEqual(p["unpaired"][0]["candidate"], "infrastructure_error")
            self.assertEqual(p["fsi_01_result"]["verdict"] in ("suggestive", "inconclusive"), True)
            self.assertFalse(p["fsi_01_manifest"]["sealed_readout"])
        self.assertEqual(_holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])


class SweScore(unittest.TestCase):
    def test_outcome_classes_follow_the_harness_report(self):
        with TemporaryDirectory() as td:
            run = Path(td)
            receipts = [{"instance_id": "a", "status": "completed", "patch_nonempty": True},
                        {"instance_id": "b", "status": "completed", "patch_nonempty": True},
                        {"instance_id": "c", "status": "completed", "patch_nonempty": False},
                        {"instance_id": "d", "status": "infrastructure_error", "patch_nonempty": False},
                        {"instance_id": "e", "status": "completed", "patch_nonempty": True}]
            (run / "receipts.jsonl").write_text("\n".join(json.dumps(r) for r in receipts) + "\n")
            (run / "report.json").write_text(json.dumps({"resolved_ids": ["a"], "error_ids": ["b"]}))
            out = swe_score(run, run / "report.json")
            self.assertEqual(out["resolved"], 1)
            self.assertEqual(out["outcomes"], {"infrastructure_error": 1, "no_patch": 1,
                                               "patch_failed_to_apply_or_run": 1, "resolved": 1, "unresolved": 1})


if __name__ == "__main__":
    unittest.main()
