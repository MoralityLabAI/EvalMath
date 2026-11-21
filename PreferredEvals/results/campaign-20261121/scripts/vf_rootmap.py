"""vf_rootmap.py <traces.jsonl> <out.json>: map each episode's task key to a root named after it (one root per task)."""
import json
import sys

roots = {}
for line in open(sys.argv[1], encoding="utf-8"):
    ep = json.loads(line)
    task = ep["task"]
    data = task.get("data") or {}
    key = task.get("key") or data.get("id") or data.get("name") or str(data.get("idx"))
    roots[key] = "root-" + str(key)
json.dump(roots, open(sys.argv[2], "w"), indent=1, sort_keys=True)
first = json.loads(open(sys.argv[1], encoding="utf-8").readline())
print(len(roots), "roots; episode keys:", sorted(first.keys()))
print("task keys:", sorted(first["task"].keys()), "data keys:", sorted((first["task"].get("data") or {}).keys())[:12])
