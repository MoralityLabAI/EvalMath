"""Closed-bank Metamath reconstruction scorer. Never expose oracle to a model."""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path

SPLITS = ("train", "dev", "public_challenge")

def require(ok, message):
    if not ok:
        raise ValueError(message)

def read_rows(path):
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        x = json.loads(line)
        require(isinstance(x, dict) and isinstance(x.get("id"), str), "row schema")
        require(x["id"] not in rows, "duplicate ID")
        rows[x["id"]] = x
    return rows

def check_bundle(root):
    receipt = json.loads((root/"receipt.json").read_text())
    require(receipt["schema"] == "mm-gym-02-v1", "receipt schema")
    require(receipt["source_commit"] == "806509385370b29fe8b1723804777ac21b1ce194",
            "unexpected source snapshot")
    for name in ("inputs.jsonl", "oracle.jsonl"):
        actual = hashlib.sha256((root/name).read_bytes()).hexdigest()
        require(actual == receipt["artifact_sha256"][name], "artifact hash mismatch")
    inputs, oracle = read_rows(root/"inputs.jsonl"), read_rows(root/"oracle.jsonl")
    validate(inputs, oracle)
    require(len(inputs) == receipt["masked_tasks"], "task count mismatch")
    require({s:sum(x["split"] == s for x in inputs.values()) for s in SPLITS}
            == receipt["splits"], "split count mismatch")
    return inputs, oracle, receipt

def validate(inputs, oracle):
    require(inputs.keys() == oracle.keys(), "oracle ID mismatch")
    for id_, x in inputs.items():
        y = oracle[id_]
        bank = x["candidates"]
        require(isinstance(bank, list) and 4 <= len(bank) <= 12 and
                len(set(bank)) == len(bank), "invalid bank")
        require(all(isinstance(a, str) for a in bank), "non-string candidate")
        i = x["source_index"]
        require(type(i) is int and 1 <= i <= 600, "source index")
        split = "train" if i <= 200 else "dev" if i <= 400 else "public_challenge"
        require(x["split"] == split, "wrong source-order split")
        require(set(x["candidate_signatures"]) == set(bank), "signature coverage")
        accept, legal = set(y["accepted_actions"]), set(y["immediate_legal_actions"])
        require(y["reference_action"] in accept <= legal <= set(bank), "oracle invalid")

def report(inputs, oracle, predictions=None):
    validate(inputs, oracle)
    if predictions is not None:
        require(predictions.keys() <= inputs.keys(), "unknown prediction ID")
        for id_, row in predictions.items():
            rank = row["ranking"]
            require(isinstance(rank, list) and all(isinstance(a, str) for a in rank)
                    and len(rank) == len(set(rank)) and
                    set(rank) <= set(inputs[id_]["candidates"]), "invalid ranking")
    frequency = Counter(oracle[i]["reference_action"] for i,x in inputs.items()
                        if x["split"] == "train")
    out = {}
    for split in SPLITS:
        rows = [(i,x,oracle[i]) for i,x in inputs.items() if x["split"] == split]
        n = len(rows)
        if not n:
            out[split] = {"cases": 0}
            continue
        random_expected = 0.0
        hits = Counter()
        legal_calls = 0
        for i,x,y in rows:
            bank, valid = x["candidates"], set(y["accepted_actions"])
            random_expected += len(valid)/len(bank)
            freq_rank = sorted(bank, key=lambda a: (-frequency[a], a))
            hits["frequency_top1"] += freq_rank[0] in valid
            hits["first_bank_top1"] += bank[0] in valid
            # This is a verifier-assisted diagnostic, using up to all bank actions.
            # It is not a trainable or oracle-free baseline.
            local = set(y["immediate_legal_actions"])
            legal_calls += len(bank)
            local_rank = [a for a in bank if a in local]
            hits["prefix_legal_top1"] += bool(local_rank) and local_rank[0] in valid
            if predictions is not None:
                rank = predictions.get(i, {}).get("ranking", [])
                hits["prediction_present"] += bool(rank)
                hits["model_top1"] += bool(rank) and rank[0] in valid
                hits["model_top3"] += bool(valid.intersection(rank[:3]))
                hits["model_top5"] += bool(valid.intersection(rank[:5]))
                hits["model_any"] += bool(valid.intersection(rank))
        out[split] = {"cases": n, "random_top1_expected": random_expected/n,
                      "first_bank_top1": hits["first_bank_top1"]/n,
                      "train_frequency_top1": hits["frequency_top1"]/n,
                      "prefix_legal_top1": hits["prefix_legal_top1"]/n,
                      "prefix_legal_verifier_calls": legal_calls}
        if predictions is not None:
            for name in ("prediction_present","model_top1","model_top3","model_top5","model_any"):
                out[split][name] = hits[name]/n
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--predictions", type=Path)
    args = parser.parse_args()
    inputs, oracle, receipt = check_bundle(args.bundle)
    predictions = read_rows(args.predictions) if args.predictions else None
    print(json.dumps({"schema":"mm-gym-02-score-v1",
                      "source_sha256":receipt["source_sha256"],
                      "splits":report(inputs, oracle, predictions)},
                     indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
