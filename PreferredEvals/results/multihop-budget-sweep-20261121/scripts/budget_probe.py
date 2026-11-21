"""budget_probe.py: thinking tokens actually used per requested budget on one dev-set 12-hop chain (not the sealed set)."""
import json
import urllib.request

task = next(json.loads(l) for l in open(
    "C:/Users/patri/Documents/Codex/EvalMath-pe2/PreferredEvals/gym/sets/multihop/tasks.jsonl", encoding="utf-8")
    if json.loads(l)["task_id"] == "multihop-d12-1")
conditions = [("budget 64", {"thinking_budget_tokens": 64}), ("budget 256", {"thinking_budget_tokens": 256}),
              ("budget 1", {"thinking_budget_tokens": 1}),
              ("enable_thinking false", {"chat_template_kwargs": {"enable_thinking": False}})]
for name, extra in conditions:
    body = {"model": "bonsai-27b-ptq1", "temperature": 0, "max_tokens": 4096, "seed": 42,
            "messages": [{"role": "user", "content": task["question"]}], **extra}
    req = urllib.request.Request("http://127.0.0.1:18127/v1/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=900))
    m = d["choices"][0]["message"]
    print(f"{name:22s} answer={m.get('content')!r:10} reasoning_chars={len(m.get('reasoning_content') or ''):5d} "
          f"completion_tokens={d['usage']['completion_tokens']}")
