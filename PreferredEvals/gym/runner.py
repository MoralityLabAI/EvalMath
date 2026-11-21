"""PreferredEvals gym: real OpenAI-compatible single-turn rollout / offline scoring.

This is a deliberately narrow local-model executor for public or authorized
user-supplied tasks. For multi-turn agent benchmarks run their native harness
through external.py and ingest its traces separately.

No scores are created by 'run': reference labels are read only by 'score'.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TASK_SCHEMA = "preferred-evals/prompt-task-v1"
RUN_SCHEMA = "preferred-evals/prompt-run-v1"
SCORE_SCHEMA = "preferred-evals/prompt-score-v1"
LETTERS = "ABCDEFGHIJ"
CHOICE = re.compile(r"^\s*(?:(?:answer|choice)\s*:\s*)?([A-J])\s*[.!]?\s*$", re.I)
RESERVED_REQUEST_KEYS = {"model", "messages", "temperature", "max_tokens", "seed", "stream"}


def digest(value):
    b = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False, sort_keys=True,
                                                          separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(b).hexdigest()


def load_jsonl(path):
    result = []
    for line_no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                result.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from exc
    return result


def append_jsonl(path, row):
    with Path(path).open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")
        f.flush()


def validate_tasks(tasks, benchmark):
    if not tasks:
        raise ValueError("task file must have at least one task")
    seen = set()
    for task in tasks:
        if not isinstance(task, dict) or task.get("schema") != TASK_SCHEMA:
            raise ValueError("each task needs schema preferred-evals/prompt-task-v1")
        tid, rid = task.get("task_id"), task.get("root_id")
        if not isinstance(tid, str) or not tid.strip() or tid in seen:
            raise ValueError("task_id must be nonblank and globally unique")
        seen.add(tid)
        if not isinstance(rid, str) or not rid.strip():
            raise ValueError(f"{tid}: root_id is required")
        if task.get("benchmark_id") != benchmark:
            raise ValueError(f"{tid}: benchmark_id does not match run")
        if task.get("kind") == "pairwise":
            if not all(isinstance(task.get(k), str) and task[k].strip()
                       for k in ("question", "proposal_a", "proposal_b")):
                raise ValueError(f"{tid}: pairwise question and proposals are required")
        elif task.get("kind") == "choice":
            choices = task.get("choices")
            if not isinstance(task.get("question"), str) or not task["question"].strip():
                raise ValueError(f"{tid}: question is required")
            if not isinstance(choices, list) or not 2 <= len(choices) <= len(LETTERS):
                raise ValueError(f"{tid}: 2..{len(LETTERS)} choices required")
            if not all(isinstance(s, str) and s.strip() for s in choices):
                raise ValueError(f"{tid}: all choices must be nonempty text")
        elif task.get("kind") == "exact_text":
            if not isinstance(task.get("question"), str) or not task["question"].strip():
                raise ValueError(f"{tid}: question required")
        else:
            raise ValueError(f"{tid}: unsupported task kind; native harness needed")
        if "answer" in task or "reference" in task or "gold" in task or "correct" in task:
            raise ValueError(f"{tid}: gold labels belong in a separate references file")
    return len({task["root_id"] for task in tasks})


def prompt_for(task, order):
    if task["kind"] == "pairwise":
        if order not in ("normal", "swapped"):
            raise ValueError("pairwise order must be normal or swapped")
        a, b = (task["proposal_a"], task["proposal_b"])
        if order == "swapped":
            a, b = b, a
        question = task["question"]
        return (f"Research question:\n{question}\n\nProposal A:\n{a}\n\n"
                f"Proposal B:\n{b}\n\nSelect the more promising proposal on expected research value "
                f"and feasibility. Reply with the single letter A or B."), "AB"
    if order != "normal":
        raise ValueError("only pairwise tasks support swapped order")
    if task["kind"] == "choice":
        choices = task["choices"]
        options = "\n".join(f"{LETTERS[i]}. {label}" for i, label in enumerate(choices))
        return f"Question:\n{task['question']}\n\nChoices:\n{options}\n\nReply with a single option letter.", LETTERS[:len(choices)]
    return task["question"] + "\n\nReturn only the final short answer.", None


RESPONSE_MODES = ("answer_only", "cot_final_line")
COT_SYSTEM = ("Reason step by step in plain text, then finish with one last line of the form "
              "'Answer: <answer>' in exactly the requested answer format.")
COT_SUFFIX = ("\n\nWork through it step by step. Then end your reply with a final line 'Answer: ' followed by "
              "the answer in the requested format.")
FINAL_LINE = re.compile(r"(?im)^\s*\**answer\**\s*:\s*(.+?)\s*$")


def final_line_answer(text):
    """The text after the last 'Answer:' line, or None when the reply has none."""
    if not isinstance(text, str):
        return None
    hits = FINAL_LINE.findall(text)
    return hits[-1].strip().strip("*").strip() if hits else None


def parse_output(text, kind, allowed, mode="answer_only"):
    if mode == "cot_final_line":
        text = final_line_answer(text)
    if not isinstance(text, str):
        return None
    if kind == "exact_text":
        v = unicodedata.normalize("NFKC", text).strip()
        return v if v else None
    m = CHOICE.fullmatch(text)
    if m and m.group(1).upper() in allowed:
        return m.group(1).upper()
    return None


def canonical_text(value):
    """NFKC, casefold, outer whitespace, one layer of quotes/backticks and one trailing period removed."""
    text = unicodedata.normalize("NFKC", value).strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'`":
        text = text[1:-1].strip()
    if text.endswith(".") and not text.endswith(".."):
        text = text[:-1].rstrip()
    return text.casefold()


def check_endpoint(base_url, allow_remote):
    parsed = urllib.parse.urlparse(base_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("base URL must have http(s) and a hostname")
    local = parsed.hostname.lower() in ("localhost", "127.0.0.1", "::1")
    if not local and not allow_remote:
        raise ValueError("remote inference requires --allow-remote to authorize sending task prompts")
    return base_url.rstrip("/")


def completion_call(*, base_url, model, prompt, seed, temperature, max_tokens, timeout, key_env, extra=None,
                    system=None):
    url = base_url + "/chat/completions"
    request = {"model": model,
               "messages": [{"role": "system", "content": system or ("Answer with exactly the requested format. "
                                                                     "Do not reveal chain-of-thought.")},
                            {"role": "user", "content": prompt}],
               "temperature": temperature, "max_tokens": max_tokens, "seed": seed}
    request.update(extra or {})
    encoded = json.dumps(request, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if key_env and os.environ.get(key_env):
        headers["Authorization"] = "Bearer " + os.environ[key_env]
    req = urllib.request.Request(url, data=encoded, method="POST", headers=headers)
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.load(response)
        message = (data.get("choices") or [{}])[0].get("message", {})
        answer = message.get("content")
        if not isinstance(answer, str):
            raise ValueError("response contained no assistant text")
        usage = data.get("usage") or {}
        return {"status": "completed", "answer": answer,
                "usage": {key: usage.get(key) for key in ("prompt_tokens", "completion_tokens", "total_tokens")},
                "reasoning_chars": len(message.get("reasoning_content") or ""),
                "duration_seconds": round(time.monotonic() - start, 6),
                "finish_reason": (data.get("choices") or [{}])[0].get("finish_reason")}
    except (urllib.error.URLError, TimeoutError, ValueError, KeyError, OSError) as exc:
        # Deliberately avoid logging response body or credentials on HTTP error.
        return {"status": "infrastructure_error", "error_type": type(exc).__name__,
                "http_status": exc.code if isinstance(exc, urllib.error.HTTPError) else None,
                "duration_seconds": round(time.monotonic() - start, 6)}


def run_tasks(*, dataset, out_dir, benchmark, model, base_url, limit=None, rollouts=1,
              orders="normal", temperature=0.0, seed=42, max_tokens=256, timeout=120,
              key_env="PREFERRED_EVALS_API_KEY", allow_remote=False, resume=False,
              client=completion_call, request_extra=None, response_mode="answer_only", concurrency=1):
    if response_mode not in RESPONSE_MODES:
        raise ValueError(f"response_mode must be one of {RESPONSE_MODES}")
    if type(concurrency) is not int or not 1 <= concurrency <= 16:
        raise ValueError("concurrency must be 1..16")
    request_extra = dict(request_extra or {})
    if set(request_extra) & RESERVED_REQUEST_KEYS:
        raise ValueError("request_extra may not override model, messages, sampling or token budget fields")
    tasks = load_jsonl(dataset)
    validate_tasks(tasks, benchmark)
    if limit is not None:
        if type(limit) is not int or limit < 1:
            raise ValueError("limit must be positive")
        tasks = tasks[:limit]
    if type(rollouts) is not int or not 1 <= rollouts <= 100:
        raise ValueError("1..100 rollouts required")
    if max_tokens < 1 or timeout < 1:
        raise ValueError("max tokens and timeout must be positive")
    base_url = check_endpoint(base_url, allow_remote)
    path = Path(out_dir)
    meta_path, rows_path = path / "run.json", path / "rollouts.jsonl"
    tasks_digest = hashlib.sha256(Path(dataset).read_bytes()).hexdigest()
    config = {"schema": RUN_SCHEMA, "benchmark_id": benchmark, "dataset_sha256": tasks_digest,
              "model": model, "base_url": base_url, "temperature": temperature, "seed": seed,
              "max_tokens": max_tokens, "rollouts": rollouts, "orders": orders,
              "limit": limit, "selection_task_ids": [t["task_id"] for t in tasks],
              "selected_tasks": [{"task_id":t["task_id"], "root_id":t["root_id"],
                                  "kind":t["kind"], "options_len": len(t.get("choices", []))} for t in tasks],
              "n_independent_roots_declared": len({t["root_id"] for t in tasks}),
              "evidence_class": "unscored model inference; reference labels were not read"}
    if request_extra:
        config["request_extra"] = request_extra
    if response_mode != "answer_only":
        config["response_mode"] = response_mode
    if path.exists() and (meta_path.exists() or rows_path.exists()):
        if not resume:
            raise FileExistsError("run directory has receipts; pass --resume with exactly the original config")
        if not meta_path.exists():
            raise ValueError("missing run manifest; refuse ambiguous resume")
        if json.loads(meta_path.read_text(encoding="utf-8")) != config:
            raise ValueError("run config or dataset changed; refusing resume")
    else:
        path.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    previous = load_jsonl(rows_path) if rows_path.exists() else []
    seen = set()
    for row in previous:
        key = (row["task_id"], row["order"], row["sample"])
        if key in seen:
            raise ValueError("duplicate receipt rows: unsafe resume")
        seen.add(key)
    jobs = []
    for task in tasks:
        for order in (("normal", "swapped") if orders == "both" and task["kind"] == "pairwise" else ("normal",)):
            prompt, allowed = prompt_for(task, order)
            if response_mode == "cot_final_line":
                prompt = prompt + COT_SUFFIX
            for sample in range(rollouts):
                if (task["task_id"], order, sample) not in seen:
                    jobs.append((task, order, sample, prompt, allowed))
    lock = threading.Lock()

    def one(job):
        task, order, sample, prompt, allowed = job
        request_seed = seed + sample
        call = dict(base_url=base_url, model=model, prompt=prompt, seed=request_seed,
                    temperature=temperature, max_tokens=max_tokens, timeout=timeout, key_env=key_env)
        if request_extra:
            call["extra"] = request_extra
        if response_mode == "cot_final_line":
            call["system"] = COT_SYSTEM
        provider = client(**call)
        result = {"task_id": task["task_id"], "root_id": task["root_id"],
                  "kind": task["kind"], "order": order, "sample": sample,
                  "prompt_sha256": digest(prompt), "request_seed": request_seed,
                  "status": provider["status"], "duration_seconds": provider.get("duration_seconds")}
        if provider["status"] == "completed":
            choice = parse_output(provider["answer"], task["kind"], allowed, response_mode)
            result.update({"parsed": choice, "format_valid": choice is not None,
                           "answer": provider["answer"], "usage": provider.get("usage"),
                           "finish_reason": provider.get("finish_reason")})
            if "reasoning_chars" in provider:
                result["reasoning_chars"] = provider["reasoning_chars"]
        else:
            result.update({"error_type": provider.get("error_type"),
                           "http_status": provider.get("http_status")})
        with lock:
            append_jsonl(rows_path, result)
            seen.add((task["task_id"], order, sample))

    if concurrency == 1:
        for job in jobs:
            one(job)
    else:
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            list(pool.map(one, jobs))
    count = len(jobs)
    return {"schema": RUN_SCHEMA, "new_rollout_rows": count, "total_receipt_rows": len(seen),
            "run_dir": str(path), "n_independent_roots_declared": config["n_independent_roots_declared"]}


def score_run(*, run_dir, labels_path, out_path):
    folder = Path(run_dir)
    cfg = json.loads((folder / "run.json").read_text(encoding="utf-8"))
    rows = load_jsonl(folder / "rollouts.jsonl")
    labels = load_jsonl(labels_path)
    gold = {}
    for line in labels:
        task, reference = line.get("task_id"), line.get("answer")
        if not isinstance(task, str) or not isinstance(reference, str) or task in gold:
            raise ValueError("reference labels must have unique task_id and text answer")
        gold[task] = reference.strip()
    requested = set(cfg["selection_task_ids"])
    if requested != set(gold):
        raise ValueError("reference file task IDs differ from run selection; refuse partial/unknown scoring")
    task_meta = {t["task_id"]:t for t in cfg["selected_tasks"]}
    expected_keys = {(t["task_id"], order, n)
                     for t in cfg["selected_tasks"]
                     for order in (("normal","swapped") if cfg["orders"] == "both" and t["kind"] == "pairwise"
                                   else ("normal",))
                     for n in range(cfg["rollouts"])}
    observed_keys = [(r["task_id"],r["order"],r["sample"]) for r in rows]
    if len(set(observed_keys)) != len(observed_keys):
        raise ValueError("duplicate rollout keys in model receipts")
    if set(observed_keys) != expected_keys:
        raise ValueError("missing or unexpected model rollouts; finish or resume inference before scoring")
    scored, grouped = [], defaultdict(list)
    statuses = Counter()
    for row in rows:
        task_id = row["task_id"]
        if task_id not in gold:
            raise ValueError("unexpected task ID in model receipt")
        meta = task_meta[task_id]
        if row.get("root_id") != meta["root_id"] or row.get("kind") != meta["kind"]:
            raise ValueError("model receipt root or task kind differs from run manifest")
        status = row["status"]
        if status not in ("completed", "infrastructure_error"):
            raise ValueError("unknown inference status")
        statuses[status] += 1
        score = None
        if status == "completed":
            predicted = row.get("parsed")
            if row["kind"] == "pairwise" and row["order"] == "swapped":
                predicted = {"A":"B", "B":"A"}.get(predicted)
            if row["kind"] == "exact_text":
                correct = canonical_text(predicted or "") == canonical_text(gold[task_id]) and bool(predicted)
            else:
                legal = ("AB" if meta["kind"] == "pairwise" else LETTERS[:meta["options_len"]])
                if gold[task_id] not in legal:
                    raise ValueError("invalid gold choice letter")
                correct = predicted == gold[task_id]
            score = int(correct)
        out = {"task_id": task_id, "root_id": row["root_id"], "sample": row["sample"],
               "order": row["order"], "status": status, "format_valid": row.get("format_valid"),
               "score": score}
        scored.append(out)
        grouped[row["root_id"]].append(out)
    scored_count = sum(x["score"] is not None for x in scored)
    correct_count = sum(x["score"] or 0 for x in scored)
    macro = []
    for root, family in grouped.items():
        values = [x["score"] for x in family if x["score"] is not None]
        if values:
            macro.append(sum(values)/len(values))
    report = {"schema": SCORE_SCHEMA,"run_manifest_sha256":hashlib.sha256((folder/"run.json").read_bytes()).hexdigest(),
              "labels_sha256": hashlib.sha256(Path(labels_path).read_bytes()).hexdigest(),
              "benchmark_id":cfg["benchmark_id"], "model":cfg["model"],
              "n_assigned_tasks":len(requested),"n_roots_assigned":cfg["n_independent_roots_declared"],
              "n_roots_scored":len(macro),"n_rollouts_recorded":len(rows),
              "n_scored": scored_count,"n_correct":correct_count,
              "accuracy_scored": correct_count/scored_count if scored_count else None,
              "macro_root_accuracy":sum(macro)/len(macro) if macro else None,
              "statuses":dict(sorted(statuses.items())),
              "by_order":{o:{"n":sum(x["score"] is not None for x in scored if x["order"]==o),
                            "correct":sum(x["score"] or 0 for x in scored if x["order"]==o)}
                          for o in sorted({x["order"] for x in scored})},
              "evidence_class":"development or observed rollout score, not prospective confirmation",
              "scope_warning":"Samples and order-swaps share task roots; apply EvalMath FSI-01 on independent roots for claims.",
              "rows":scored}
    Path(out_path).parent.mkdir(parents=True,exist_ok=True)
    Path(out_path).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return {key:report[key] for key in ("n_rollouts_recorded","n_scored","n_correct","macro_root_accuracy","statuses")}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="cmd",required=True)
    r=sub.add_parser("run",help="Run local OpenAI-compatible single-turn tasks; never reads gold")
    r.add_argument("--tasks",type=Path,required=True)
    r.add_argument("--benchmark",required=True)
    r.add_argument("--out",type=Path,required=True)
    r.add_argument("--model",required=True)
    r.add_argument("--base-url",default="http://127.0.0.1:18127/v1")
    r.add_argument("--limit",type=int)
    r.add_argument("--rollouts",type=int,default=1)
    r.add_argument("--orders",choices=("normal","both"),default="normal")
    r.add_argument("--temperature",type=float,default=0.0)
    r.add_argument("--seed",type=int,default=42)
    r.add_argument("--max-tokens",type=int,default=256)
    r.add_argument("--timeout",type=int,default=120)
    r.add_argument("--api-key-env",default="PREFERRED_EVALS_API_KEY")
    r.add_argument("--allow-remote",action="store_true")
    r.add_argument("--resume",action="store_true")
    r.add_argument("--request-extra",type=json.loads,default=None,
                   help='JSON object merged into each request and recorded in run.json, '
                        'e.g. \'{"chat_template_kwargs":{"enable_thinking":false}}\'')
    r.add_argument("--response-mode",choices=RESPONSE_MODES,default="answer_only",
                   help="answer_only (default) or cot_final_line: visible reasoning, scored on the last 'Answer:' line")
    r.add_argument("--concurrency",type=int,default=1,help="requests in flight (receipts are order-independent)")
    s=sub.add_parser("score",help="Offline grade saved model rollouts against separate labels")
    s.add_argument("--run-dir",type=Path,required=True)
    s.add_argument("--labels",type=Path,required=True)
    s.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.cmd=="run":
        result=run_tasks(dataset=args.tasks,out_dir=args.out,benchmark=args.benchmark,
                         model=args.model,base_url=args.base_url,limit=args.limit,
                         rollouts=args.rollouts,orders=args.orders,temperature=args.temperature,
                         seed=args.seed,max_tokens=args.max_tokens,timeout=args.timeout,
                         key_env=args.api_key_env,allow_remote=args.allow_remote,resume=args.resume,
                         request_extra=args.request_extra,response_mode=args.response_mode,
                         concurrency=args.concurrency)
    else:
        result=score_run(run_dir=args.run_dir,labels_path=args.labels,out_path=args.out)
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
