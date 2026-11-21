"""Strict ingest of the public verifiers.v1 trace shape used by Prime Hub tools.

This ingests a pinned *serialized subset*, not the entire verifiers API.
Never infer root independence from a trace's task name: supply an explicit map.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def import_trace_rows(raw_rows, root_map, *, metric="task_success"):
    """Expand v1 task->traces rows to root-tagged, auditable summary records."""
    if not isinstance(root_map, dict) or not root_map:
        raise ValueError("explicit task-to-independent-root map required")
    out, case_ids = [], set()
    for record in raw_rows:
        if not isinstance(record, dict):
            raise ValueError("trace row must be object")
        task = record.get("task")
        data = task.get("data") if isinstance(task, dict) else None
        task_id = data.get("name") if isinstance(data, dict) else None
        if not isinstance(task_id, str) or task_id not in root_map:
            raise ValueError("every trace requires task.data.name mapped to an independent root")
        traces = record.get("traces")
        if not isinstance(traces, list) or not traces:
            raise ValueError(f"{task_id}: nonempty traces list required")
        for i, tr in enumerate(traces):
            if not isinstance(tr, dict):
                raise ValueError("trace must be object")
            cid = f"{task_id}#rollout-{i}"
            if cid in case_ids:
                raise ValueError("duplicate task and rollout identity")
            case_ids.add(cid)
            errs = tr.get("errors") or []
            if not isinstance(errs, list):
                raise ValueError("errors must be a list")
            metrics = tr.get("metrics") or {}
            if not isinstance(metrics, dict):
                raise ValueError("metrics must be object")
            rewards = tr.get("rewards") or {}
            if not isinstance(rewards, dict):
                raise ValueError("rewards must be object")
            outcome = metrics.get(metric)
            if outcome is not None and (not isinstance(outcome, (float, int)) or isinstance(outcome, bool)):
                raise ValueError("primary metric must be numeric or missing")
            weighted = 0.0
            for v in rewards.values():
                if not isinstance(v, dict):
                    raise ValueError("reward must be a score/weight object")
                weighted += float(v.get("score", 0)) * float(v.get("weight", 0))
            out.append({"schema":"preferred-evals/prime-v1-import/v1",
                        "task_id":task_id,"case_id":cid,"root_id":root_map[task_id],
                        "rollout_index":i,"ok":tr.get("ok"),
                        "stop":tr.get("stop_condition"),"errors":len(errs),
                        "primary_metric":outcome,"weighted_reward":weighted,
                        "metrics":metrics,
                        "model_calls_count":len(tr.get("model_calls") or []),
                        "source_scope":"serialized v1 example shape; verify upstream version"})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--traces", type=Path, required=True, help="JSONL with top-level task and traces")
    ap.add_argument("--root-map", type=Path, required=True, help="JSON mapping exact task names to root IDs")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    rows = [json.loads(line) for line in args.traces.read_text().splitlines() if line.strip()]
    result = import_trace_rows(rows, json.loads(args.root_map.read_text()))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(json.dumps(row, sort_keys=True) for row in result) + "\n")


if __name__ == "__main__":
    main()
