"""AIRIS-07 candidate curriculum. Separate labeled train and unlabeled dev."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from nonstationary import HAZARDS,census,pair_values,raw_event,optimal,orderless_floor

SCHEMA="evalmath-airis07-candidate-v1"
HERE=Path(__file__).parent


def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"))


def digest(x):
    return sha256(canonical(x).encode()).hexdigest()


def group_id(key):
    # Same first-two permutation class, including the final event, across rates.
    return digest([SCHEMA,"group",list(key)])


def row(key,k,variant,labeled):
    i,j,l=key
    history=(i,j,l) if variant==0 else (j,i,l)
    result={"schema":SCHEMA,"root_id":digest([SCHEMA,k,group_id(key)]),
            "group_id":group_id(key),"presentation":variant,
            "split":"train_candidate" if labeled else "development",
            "training_ready":False,
            "input":{"drift_resample_probability":f"{k}/4","driver_flip_probability":"1/4",
                     "history":[raw_event(e) for e in history],"next_episode_transition_cost":3,
                     "candidate_schedule_order":["".join(map(str,a)) for a in __import__("partial").SCHEDULES]},
            "provenance":{"generator":"EvalMath/gyms/AIRIS/nonstationary.py",
                          "evidence":"finite synthetic exact oracle"}}
    if labeled:
        q=pair_values(key,k)[variant]
        result["teacher"]={"action_values":[str(v) for v in q],"optimal_actions":optimal(q)}
    return result


def make_bundle():
    summaries={}
    strict={}
    for k in HAZARDS:
        summaries[str(k)],strict[k]=census(k)
    train=[]
    dev=[]
    # Split canonical paired observation classes before exporting any label.
    train_keys={key for key in strict[1] if int(group_id(key)[:8],16)%5!=0}
    for key in strict[1]:
        labeled=key in train_keys
        # Matched stationary presentations share exactly the same public raw
        # history and split. Rate is a declared input, not a hidden label.
        for k in (0,1):
            for variant in (0,1):
                (train if labeled else dev).append(row(key,k,variant,labeled))
    # Held-out drift rate: keep only keys absent from all training groups.
    for key in strict[2]:
        if key not in train_keys:
            for variant in (0,1):
                dev.append(row(key,2,variant,False))
    audit(train,dev)
    return train,dev,summaries


def audit(train,dev):
    if not train or not dev:
        raise ValueError("empty partition")
    seen=set()
    groups=[]
    for rows,labeled in ((train,True),(dev,False)):
        g=set()
        for r in rows:
            if r["schema"]!=SCHEMA or r["training_ready"] is not False:
                raise ValueError("invalid custody")
            if r["split"]!=("train_candidate" if labeled else "development"):
                raise ValueError("wrong split")
            if ("teacher" in r)!=labeled:
                raise ValueError("teacher label leakage")
            identity=(r["root_id"],r["presentation"])
            if identity in seen:
                raise ValueError("duplicate presentation")
            seen.add(identity)
            g.add(r["group_id"])
        groups.append(g)
    if groups[0]&groups[1]:
        raise ValueError("cross-split observation-group leakage")
    return {"train_rows":len(train),"development_rows":len(dev),
            "train_groups":len(groups[0]),"development_groups":len(groups[1]),
            "train_roots":len({r["root_id"] for r in train}),
            "development_roots":len({r["root_id"] for r in dev})}


def write(out):
    out.mkdir(parents=True,exist_ok=True)
    train,dev,summaries=make_bundle()
    paths={}
    for name,rows in (("train_candidates",train),("development_unlabeled",dev)):
        p=out/(name+".jsonl")
        p.write_text("".join(canonical(r)+"\n" for r in rows),encoding="utf-8")
        paths[p.name]=sha256(p.read_bytes()).hexdigest()
    # Builder manifest deliberately excludes development records, values,
    # evaluation seeds and oracle source. Full public development receipt
    # remains a research artifact, not a sealed evaluation.
    manifest={"schema":SCHEMA,"training_ready":False,"partition":"train_candidate",
              "rows":len(train),"groups":len({r["group_id"] for r in train}),
              "file":"train_candidates.jsonl","sha256":paths["train_candidates.jsonl"],
              "claim_boundary":"synthetic candidate proposals; no admission or learned result"}
    (out/"train_manifest.json").write_text(canonical(manifest)+"\n",encoding="utf-8")
    receipt={"experiment":"AIRIS-07","evidence":"exact finite designed pair census; PILOT_ONLY",
             "census":summaries,"split":audit(train,dev),"file_sha256":paths,
             "source_sha256":{name:sha256((HERE/name).read_bytes()).hexdigest()
                              for name in ("nonstationary.py","curriculum.py","test_nonstationary.py",
                                           "NONSTATIONARY.md","partial.py")}}
    (out/"AIRIS-07.json").write_text(canonical(receipt)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2,sort_keys=True))
    return receipt


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    write(p.parse_args().out)
