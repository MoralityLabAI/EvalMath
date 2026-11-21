"""SWE-bench Lite, oracle-retrieval single-shot setting, graded by the official SWE-bench harness.

SWE-bench publishes ``princeton-nlp/SWE-bench_Lite_oracle``: each prompt holds the issue and the full
text of the files the gold patch edits, and asks for a patch. This module sends that prompt unchanged
to an OpenAI-compatible endpoint, keeps the raw reply, extracts the patch with SWE-bench's own
``extract_diff``, and writes a predictions file for ``swebench.harness.run_evaluation``. It is
SWE-bench's single-shot retrieval baseline, not an agentic SWE harness.

    python swebench_oracle.py select --gold-valid ids.txt --n 6 --max-prompt-chars 90000 --out sel.json
    python swebench_oracle.py generate --selection sel.json --model M --base-url URL --out RUN
    python -m swebench.harness.run_evaluation --dataset_name SWE-bench/SWE-bench_Lite \
        --predictions_path RUN/predictions.jsonl --instance_ids ... --run_id RUNID --max_workers 2
    python swebench_oracle.py score --run RUN --report <model>.<RUNID>.json

Needs ``datasets`` and ``swebench`` (5.x) installed; model calls use the standard library.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

DATASET = "princeton-nlp/SWE-bench_Lite_oracle"


def _load(revision: str | None):
    from datasets import load_dataset
    from huggingface_hub import HfApi

    revision = revision or HfApi().dataset_info(DATASET).sha
    return load_dataset(DATASET, split="test", revision=revision), revision


def select(gold_valid: list[str], n: int, max_prompt_chars: int, revision: str | None) -> dict:
    ds, revision = _load(revision)
    rows = {r["instance_id"]: r for r in ds if r["instance_id"] in set(gold_valid)}
    fitting = sorted((iid for iid, r in rows.items() if len(r["text"]) <= max_prompt_chars),
                     key=lambda iid: (len(rows[iid]["text"]), iid))
    chosen = fitting[:n]
    return {"dataset": DATASET, "revision": revision, "instance_ids": chosen,
            "prompt_chars": {iid: len(rows[iid]["text"]) for iid in chosen},
            "selection": f"the {n} shortest oracle prompts (at most {max_prompt_chars} characters) among "
                         f"{len(gold_valid)} instances whose gold patch resolves on this host",
            "gold_valid_pool": sorted(gold_valid), "missing_from_dataset": sorted(set(gold_valid) - set(rows))}


def _call(base_url: str, model: str, prompt: str, max_tokens: int, temperature: float, seed: int,
          timeout: int) -> dict:
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt}],
                       "max_tokens": max_tokens, "temperature": temperature, "seed": seed}).encode()
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.load(resp)
        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        return {"status": "completed", "answer": message.get("content") or "",
                "reasoning_chars": len(message.get("reasoning_content") or ""),
                "finish_reason": choice.get("finish_reason"), "usage": data.get("usage"),
                "duration_seconds": round(time.monotonic() - start, 3)}
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        return {"status": "infrastructure_error", "error_type": type(exc).__name__,
                "http_status": getattr(exc, "code", None), "duration_seconds": round(time.monotonic() - start, 3)}


def generate(selection: dict, model: str, base_url: str, out: Path, max_tokens: int, temperature: float,
             seed: int, timeout: int) -> dict:
    from swebench.inference.make_datasets.utils import extract_diff

    ds, _ = _load(selection["revision"])
    rows = {r["instance_id"]: r for r in ds if r["instance_id"] in set(selection["instance_ids"])}
    out.mkdir(parents=True, exist_ok=True)
    config = {"schema": "preferred-evals/swebench-oracle-run-v1", "model": model, "base_url": base_url,
              "max_tokens": max_tokens, "temperature": temperature, "seed": seed, "selection": selection}
    (out / "run.json").write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    receipts, predictions = [], []
    for iid in selection["instance_ids"]:
        prompt = rows[iid]["text"]
        result = _call(base_url, model, prompt, max_tokens, temperature, seed, timeout)
        patch = extract_diff(result["answer"]) if result["status"] == "completed" else ""
        receipts.append(dict(result, instance_id=iid, prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(),
                             patch=patch, patch_nonempty=bool((patch or "").strip())))
        predictions.append({"instance_id": iid, "model_name_or_path": model, "model_patch": patch or ""})
    (out / "receipts.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in receipts),
                                        encoding="utf-8")
    (out / "predictions.jsonl").write_text("".join(json.dumps(p) + "\n" for p in predictions), encoding="utf-8")
    return {"instances": len(receipts), "completed": sum(r["status"] == "completed" for r in receipts),
            "nonempty_patches": sum(r["patch_nonempty"] for r in receipts)}


def score(run: Path, report: Path) -> dict:
    receipts = [json.loads(line) for line in (run / "receipts.jsonl").read_text(encoding="utf-8").splitlines()]
    rep = json.loads(report.read_text(encoding="utf-8"))
    resolved = set(rep.get("resolved_ids", []))
    rows = []
    for r in receipts:
        iid = r["instance_id"]
        if r["status"] != "completed":
            outcome = "infrastructure_error"
        elif not r["patch_nonempty"]:
            outcome = "no_patch"
        elif iid in resolved:
            outcome = "resolved"
        elif iid in set(rep.get("error_ids", [])):
            outcome = "patch_failed_to_apply_or_run"
        else:
            outcome = "unresolved"
        rows.append({"instance_id": iid, "outcome": outcome, "score": int(outcome == "resolved")})
    summary = {"schema": "preferred-evals/swebench-oracle-score-v1", "report": report.name,
               "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
               "n": len(rows), "resolved": sum(r["score"] for r in rows),
               "outcomes": {o: sum(r["outcome"] == o for r in rows) for o in sorted({r["outcome"] for r in rows})},
               "harness_counts": {k: rep.get(k) for k in ("submitted_instances", "completed_instances",
                                                          "resolved_instances", "unresolved_instances",
                                                          "empty_patch_instances", "error_instances")},
               "rows": rows}
    (run / "scores.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {k: summary[k] for k in ("n", "resolved", "outcomes")}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("select")
    s.add_argument("--gold-valid", type=Path, required=True, help="file with one instance id per line")
    s.add_argument("--n", type=int, default=6)
    s.add_argument("--max-prompt-chars", type=int, default=90000)
    s.add_argument("--revision")
    s.add_argument("--out", type=Path, required=True)
    g = sub.add_parser("generate")
    g.add_argument("--selection", type=Path, required=True)
    g.add_argument("--model", required=True)
    g.add_argument("--base-url", required=True)
    g.add_argument("--out", type=Path, required=True)
    g.add_argument("--max-tokens", type=int, default=4096)
    g.add_argument("--temperature", type=float, default=0.0)
    g.add_argument("--seed", type=int, default=42)
    g.add_argument("--timeout", type=int, default=1800)
    c = sub.add_parser("score")
    c.add_argument("--run", type=Path, required=True)
    c.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    if args.cmd == "select":
        ids = [x.strip() for x in args.gold_valid.read_text().split() if x.strip()]
        result = select(ids, args.n, args.max_prompt_chars, args.revision)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif args.cmd == "generate":
        result = generate(json.loads(args.selection.read_text()), args.model, args.base_url, args.out,
                          args.max_tokens, args.temperature, args.seed, args.timeout)
    else:
        result = score(args.run, args.report)
    print(json.dumps(result, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
