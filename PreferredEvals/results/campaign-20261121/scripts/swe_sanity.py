"""swe_sanity.py: gold patches wrapped as a model reply survive extract_diff; show why model patches failed."""
import glob
import json
import os

from datasets import load_dataset
from swebench.inference.make_datasets.utils import extract_diff

sel = json.load(open("/mnt/c/Users/patri/Documents/Codex/pe2-work/data/swe_selection.json"))
lite = {r["instance_id"]: r for r in load_dataset("SWE-bench/SWE-bench_Lite", split="test")
        if r["instance_id"] in sel["instance_ids"]}
for iid in sel["instance_ids"]:
    gold = lite[iid]["patch"]
    back = extract_diff("Here is the fix.\n<patch>\n" + gold + "\n</patch>\n")
    print(iid, "gold round-trips through extract_diff:", back.strip() == gold.strip())
for tag in ("bonsai", "qwen"):
    for log in sorted(glob.glob(f"/root/swebench-runs/logs/run_evaluation/pe2_swe_{tag}/*/*/run_instance.log"))[:3]:
        text = open(log, errors="replace").read()
        hits = [l for l in text.splitlines() if "patch" in l.lower() and ("fail" in l.lower() or "error" in l.lower()
                                                                          or "malformed" in l.lower() or "corrupt" in l.lower())]
        print(tag, os.path.basename(os.path.dirname(log)), "|", (hits[-1] if hits else "no patch error line")[:200])
