"""Build public or generated prompt-task sets for the gym, with separate label files and provenance.

Sets:
  iclr2026-pairs    Public research-taste proxy: pairs of ICLR 2026 submissions from the same primary area,
                    one accepted as an oral and one rejected, title and abstract only. The label is the
                    venue decision, not an expert taste judgment, and this is not Anthropic TASTE.
                    Source: Hugging Face JerMa88/ICLR_Peer_Reviews_2026 (OpenReview records; ICLR
                    submissions are CC BY 4.0).
  mmlu-pro-science  Public multiple-choice science questions (physics, chemistry, biology) from
                    TIGER-Lab/MMLU-Pro (MIT). A stand-in while text-only HLE is gated; not HLE.
  multihop          Generated variable-binding chains (2 to 12 hops) with distractor chains and an exact
                    integer answer, for recursive-reasoning and no-chain-of-thought comparisons.
                    Development control: generated here, not an external benchmark.

    python PreferredEvals/gym/build_public_sets.py iclr2026-pairs --out DIR --n 12 --seed 2026
    python PreferredEvals/gym/build_public_sets.py mmlu-pro-science --out DIR --n 8 --seed 2026
    python PreferredEvals/gym/build_public_sets.py multihop --out DIR --per-depth 3 --seed 2026

The two public sets need `datasets` and network access; multihop is stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import defaultdict
from pathlib import Path

SCHEMA = "preferred-evals/prompt-task-v1"
LETTERS = "ABCDEFGHIJ"


def _rank(seed: int, key: str) -> str:
    return hashlib.sha256(f"{seed}:{key}".encode()).hexdigest()


def _write(out: Path, benchmark: str, tasks: list[dict], labels: list[dict], provenance: dict) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    for task in tasks:
        task.setdefault("schema", SCHEMA)
        task["benchmark_id"] = benchmark
    # Bytes, not text mode: the recorded hashes must not depend on the platform's newline convention.
    (out / "tasks.jsonl").write_bytes("".join(json.dumps(t, ensure_ascii=False, sort_keys=True) + "\n"
                                              for t in tasks).encode("utf-8"))
    (out / "labels.jsonl").write_bytes("".join(json.dumps(l, sort_keys=True) + "\n" for l in labels).encode("utf-8"))
    provenance = dict(provenance, benchmark_id=benchmark, n_tasks=len(tasks),
                      n_roots=len({t["root_id"] for t in tasks}),
                      tasks_sha256=hashlib.sha256((out / "tasks.jsonl").read_bytes()).hexdigest(),
                      labels_sha256=hashlib.sha256((out / "labels.jsonl").read_bytes()).hexdigest())
    (out / "provenance.json").write_bytes((json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return provenance


def _hf_revision(repo: str) -> str:
    from huggingface_hub import HfApi

    return HfApi().dataset_info(repo).sha


def iclr_pairs(out: Path, n: int, seed: int) -> dict:
    from datasets import load_dataset

    repo = "JerMa88/ICLR_Peer_Reviews_2026"
    revision = _hf_revision(repo)
    ds = load_dataset(repo, split="train", revision=revision)
    papers: dict[str, dict] = {}
    decisions: dict[str, int] = defaultdict(int)
    for row in ds:
        pid = row["paper_id"]
        if pid in papers or not row.get("abstract") or not row.get("title"):
            continue
        try:
            content = json.loads(row["api_raw_submission"]).get("content", {})
        except (TypeError, json.JSONDecodeError):
            content = {}
        area = (content.get("primary_area") or {}).get("value") if isinstance(content, dict) else None
        decision = str(row.get("decision") or "").strip()
        decisions[decision] += 1
        papers[pid] = {"id": pid, "title": row["title"].strip(), "abstract": " ".join(row["abstract"].split()),
                       "decision": decision, "area": area}
    by_area: dict[str, dict[str, list]] = defaultdict(lambda: {"oral": [], "reject": []})
    for p in papers.values():
        if not p["area"]:
            continue
        low = p["decision"].lower()
        if "oral" in low and "accept" in low:
            by_area[p["area"]]["oral"].append(p)
        elif low.startswith("reject"):
            by_area[p["area"]]["reject"].append(p)
    areas = sorted((a for a, g in by_area.items() if g["oral"] and g["reject"]), key=lambda a: _rank(seed, a))
    tasks, labels, used = [], [], []
    for i in range(n):
        area = areas[i % len(areas)]
        group = by_area[area]
        taken = {p for pair in used for p in pair}
        oral = sorted((p for p in group["oral"] if p["id"] not in taken), key=lambda p: _rank(seed, p["id"]))
        reject = sorted((p for p in group["reject"] if p["id"] not in taken), key=lambda p: _rank(seed, p["id"]))
        if not oral or not reject:
            raise ValueError(f"not enough unused papers in area {area}")
        a, b = oral[0], reject[0]
        used.append((a["id"], b["id"]))
        accepted_first = int(_rank(seed, a["id"] + b["id"]), 16) % 2 == 0
        first, second = (a, b) if accepted_first else (b, a)
        tid = f"iclr26-pair-{i + 1:02d}"
        tasks.append({"task_id": tid, "root_id": tid, "kind": "pairwise",
                      "question": f"Two machine-learning research submissions in the area '{area}'. "
                                  "Which is the stronger contribution?",
                      "proposal_a": f"{first['title']}\n\n{first['abstract']}",
                      "proposal_b": f"{second['title']}\n\n{second['abstract']}",
                      "source_ids": [first["id"], second["id"]]})
        labels.append({"task_id": tid, "answer": "A" if accepted_first else "B"})
    return _write(out, "public-proxy-iclr2026-oral-vs-reject", tasks, labels, {
        "source": f"huggingface:{repo}@{revision}", "origin": "OpenReview ICLR 2026 records",
        "license_note": "ICLR submissions on OpenReview are CC BY 4.0; forum ids are in source_ids",
        "label_semantics": "venue decision (accepted as oral vs rejected); a public proxy, not expert taste labels",
        "not": "not Anthropic TASTE; not withheld or expert-judged",
        "selection": f"seeded hash order over primary areas with both an oral and a rejected paper; seed {seed}",
        "decision_counts_seen": dict(sorted(decisions.items())), "papers_seen": len(papers),
        "contamination_note": "ICLR 2026 decisions (January 2026) postdate Qwen3-4B-Instruct-2507 (July 2025); "
                              "a later model may have seen them"})


def mmlu_pro(out: Path, n: int, seed: int) -> dict:
    from datasets import load_dataset

    repo = "TIGER-Lab/MMLU-Pro"
    revision = _hf_revision(repo)
    ds = load_dataset(repo, split="test", revision=revision)
    pool = [r for r in ds if r["category"] in ("physics", "chemistry", "biology")]
    pool.sort(key=lambda r: _rank(seed, str(r["question_id"])))
    tasks, labels = [], []
    for row in pool[:n]:
        tid = f"mmlu-pro-{row['question_id']}"
        tasks.append({"task_id": tid, "root_id": tid, "kind": "choice", "question": row["question"],
                      "choices": list(row["options"]), "category": row["category"], "src": row.get("src")})
        labels.append({"task_id": tid, "answer": LETTERS[int(row["answer_index"])]})
    return _write(out, "public-mmlu-pro-science", tasks, labels, {
        "source": f"huggingface:{repo}@{revision}", "license_note": "MMLU-Pro is MIT licensed",
        "selection": f"physics, chemistry and biology test questions in seeded hash order; seed {seed}",
        "not": "not HLE; a public multiple-choice science stand-in while cais/hle is gated"})


NAMES = ["kappa", "lumen", "sorrel", "vesper", "quill", "tamsin", "orrin", "pallas", "wren", "ysolde", "brisk",
         "cobalt", "delve", "ember", "fable", "garnet", "hollis", "iris", "jasper", "kestrel", "linden", "marlo",
         "nimbus", "opal", "pike", "quorra", "rowan", "sable", "thorne", "umber", "vale", "willow"]


def multihop(out: Path, per_depth: int, seed: int, depths=(2, 4, 8, 12)) -> dict:
    rng = random.Random(seed)
    tasks, labels = [], []
    for depth in depths:
        for k in range(per_depth):
            names = rng.sample(NAMES, 2 * depth + 2)
            target, distract = names[: depth + 1], names[depth + 1:]
            lines, value = [], rng.randint(2, 9)
            lines.append(f"{target[0]} = {value}")
            for prev, cur in zip(target, target[1:]):
                op = rng.choice(["+", "-", "*"])
                c = rng.randint(2, 5)
                value = value + c if op == "+" else value - c if op == "-" else value * c
                lines.append(f"{cur} = {prev} {op} {c}")
            d = rng.randint(2, 9)
            lines.append(f"{distract[0]} = {d}")
            for prev, cur in zip(distract, distract[1:]):
                lines.append(f"{cur} = {prev} + {rng.randint(2, 5)}")
            rng.shuffle(lines)
            tid = f"multihop-d{depth:02d}-{k + 1}"
            tasks.append({"task_id": tid, "root_id": tid, "kind": "exact_text", "hops": depth,
                          "question": "Each line assigns a variable. Evaluate the assignments.\n"
                                      + "\n".join(lines) + f"\nWhat is the value of {target[-1]}? "
                                      "Reply with the integer only."})
            labels.append({"task_id": tid, "answer": str(value)})
    return _write(out, "dev-multihop-binding", tasks, labels, {
        "source": "generated by build_public_sets.py multihop", "generator_seed": seed,
        "depths": list(depths), "per_depth": per_depth,
        "not": "development control generated here; not an external benchmark"})


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("set", choices=("iclr2026-pairs", "mmlu-pro-science", "multihop"))
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--per-depth", type=int, default=3)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    if args.set == "iclr2026-pairs":
        result = iclr_pairs(args.out, args.n, args.seed)
    elif args.set == "mmlu-pro-science":
        result = mmlu_pro(args.out, args.n, args.seed)
    else:
        result = multihop(args.out, args.per_depth, args.seed)
    print(json.dumps(result, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
