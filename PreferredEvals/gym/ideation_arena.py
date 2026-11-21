"""Convert authorized Ideation Arena expert judgments into PreferredEvals tasks.

Reads the two distinct JSON files individually. Requires explicit NC license
acknowledgment and never includes expert labels in model-facing prompt tasks.
Uses query context as clustering root, so repeated proposals/papers are not
automatically independent beyond that grouping.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

SCHEMA="preferred-evals/prompt-task-v1"
BENCHMARK="ideation-arena-human-pairs-dev"

def rows(path):
    path=Path(path)
    if path.stat().st_size>100_000_000:
        try:
            import ijson
        except ImportError as exc:
            raise RuntimeError("Large Ideation Arena files require ijson: pip install ijson") from exc
        with path.open("rb") as fp:
            yield from ijson.items(fp,"item")
    else:
        data=json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data,list):
            raise ValueError("expected JSON top-level list; inspect dataset format")
        yield from data

def extract(path,*,dimension="D4",limit=24,license_ack=False):
    if not license_ack:
        raise ValueError("CC BY-NC 4.0 is noncommercial; pass --ack-noncommercial after checking intended use")
    if dimension not in {f"D{i}" for i in range(5)}:
        raise ValueError("judge dimension must be D0...D4; confirm paper's semantic mapping")
    tasks,labels,skipped=[],[],{"tie":0,"missing":0,"incomplete":0}
    for i,row in enumerate(rows(path)):
        if len(tasks)>=limit:
            break
        if not isinstance(row,dict):
            skipped["incomplete"]+=1;continue
        dims=row.get("dimension_results") or {}
        gold=dims.get(dimension) if isinstance(dims,dict) else None
        if gold in ("Tie","tie","TIE"):
            skipped["tie"]+=1;continue
        if gold not in ("A","B"):
            skipped["missing"]+=1;continue
        a,b=row.get("response_a"),row.get("response_b")
        query=row.get("query_text")
        if not all(isinstance(x,str) and x.strip() for x in (a,b,query)):
            skipped["incomplete"]+=1;continue
        root="query-"+hashlib.sha256(query.encode()).hexdigest()[:20]
        ident=f"arena-{i:07d}"
        tasks.append({"schema":SCHEMA,"task_id":ident,"root_id":root,"benchmark_id":BENCHMARK,
                      "kind":"pairwise","question":query,"proposal_a":a,"proposal_b":b})
        labels.append({"task_id":ident,"answer":gold})
    return tasks,labels,skipped

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--comparisons",type=Path,required=True,help="Path to final_ideation_results_with_response.json; NOT queries.json")
    ap.add_argument("--out-tasks",type=Path,required=True)
    ap.add_argument("--out-labels",type=Path,required=True)
    ap.add_argument("--dimension",default="D4")
    ap.add_argument("--limit",type=int,default=24)
    ap.add_argument("--ack-noncommercial",action="store_true")
    args=ap.parse_args()
    if args.limit<1:raise ValueError("limit must be >=1")
    tasks,labels,skipped=extract(args.comparisons,dimension=args.dimension,limit=args.limit,license_ack=args.ack_noncommercial)
    if not tasks:raise ValueError("No labeled proposal pairs extracted")
    if args.out_tasks.resolve()==args.out_labels.resolve():
        raise ValueError("tasks and labels require distinct files")
    for p,content in ((args.out_tasks,tasks),(args.out_labels,labels)):
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text("".join(json.dumps(x,ensure_ascii=False)+"\n" for x in content),encoding="utf-8")
    print(json.dumps({"labeled":len(tasks),"unique_context_roots":len({x["root_id"] for x in tasks}),
                      "skipped":skipped,"dataset_license":"CC BY-NC 4.0",
                      "scope":"development-only, human comparison agreement"}))
if __name__=="__main__":main()
