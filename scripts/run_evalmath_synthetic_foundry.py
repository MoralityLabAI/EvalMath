"""ESF-01: source-pinned referee packets and independent synthetic-data gym.

Run in a local EvalMath checkout. Paid calls, if explicitly authorized, use the
existing DataGoblin shared budget ledger; no API key is read by offline commands.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from decimal import Decimal

from spiral_ln.evaluation_synthetic_foundry import (
    FAMILIES, PROFILES, canonical, digest, generate, write_pack,
)

PIN = "3c9afc089d4e3ef57b876d19952a270fe44944dc"
DG_PIN = "2b472ec6c63c46c29b62616c58314d5cb9c70d8a"
PANELS = {
    "feedback": r"feedback_(signal|lattice|multigen|composition|insertions)|training_signal|selection_law|leak_(topology|capacity)|ppt_adaptive|gold_calibration|judge_measurement",
    "filtration": r"adaptive_disclosure|selection_risk|covert_feedback|stochastic_full|dynamic_filtration|noisy_authorization|frozen_evidence|finite_sample|scouting_value",
    "fidelity": r"cpf|correlated_proof|proof_fidelity|agency_|cryptomania|metaprune",
    "mechanisms": r"bpd|mechanism|nw01|interface_relative|quotient|collatz|spectral|recurrent",
    "recursive": r"frc|hypergame|harmonic|evaluation_design|game_|rsi|cogentic|dcf16",
    "frontier": r".*",
}
LANES = {
    "feedback": ["judge","patch","reuse","capacity"],
    "filtration": ["selection","covert","disclosure","revocation","adaptive_risk","filtration","private_stopping"],
    "fidelity": ["cpf","audit","judge","adaptive_cpf"],
    "mechanisms": ["bpd","paired","revocation"],
    "recursive": ["selection","audit","covert","disclosure","adaptive_risk","private_stopping"],
    "frontier": list(FAMILIES),
}
SYSTEM = """You are Fable acting as EvalMath's mathematical referee and independent
scientific research planner. Review the source-pinned research program as
mathematics, not marketing. Distinguish universal proofs, finite witnesses,
synthetic mechanisms and empirical results. Identify false generalizations,
missing hypotheses, inadequate gold, circular evaluation, contaminated splits,
weak baselines, and open mathematical questions. Propose concrete fixes to
EvalMath and a synthetic dataset curriculum for scientific reasoning and
training looped transformers. Use explicit mathematics, falsifiers and
computable independent gold. Do not claim that an excerpt is a full proof.
No generated code is executed. Research-only response; no training export.
Return a JSON object: {"review_markdown": string, "claims": [{"source": string,
"statement": string, "evidence": string, "gap": string}], "ranked_repairs":
[{"target": string, "mathematical_reason": string, "test": string}],
"proposed_generators": [{"family": string, "input_contract": string,
"gold_algorithm": string, "counterexamples": string, "split_strategy": string}],
"decision_proxy": string, "action": {"family": string, "profile": string},
"predictions": string}. The action must be one of the registered families and
profiles in the packet. Prioritize novel discriminating tests over additional
prose. Freeze predictions before results."""
FOLLOWUP = """You are the independent reviewer of a prior research proposal.
Given actual bounded CPU receipts, assess which predictions were tested,
which remain unsupported, and whether the exact generator is useful.
Provide a corrected mathematical specification, adversarial fixtures,
and ranked implementation tickets. No unmeasured performance claims.
Return JSON with review_markdown, claim_updates, repairs and next_experiments.
Research-only; do not request execution or access to private confirmation data."""


def git(root, *args):
    return subprocess.check_output(["git","-C",str(root),*args])


def source(root, ref, path):
    raw=git(root,"show",f"{ref}:{path}")
    return raw.decode("utf-8"), hashlib.sha256(raw).hexdigest(), git(
        root,"rev-parse",f"{ref}:{path}").decode().strip()


def inventory(root, ref):
    paths=git(root,"ls-tree","-r","--name-only",ref).decode().splitlines()
    selected=[p for p in paths if p.startswith("paper/") and p.endswith(".md")]
    selected += [p for p in paths if p.startswith("gyms/") and
                 Path(p).name in {"README.md","THEORY.md","PROTOCOL.md","RESULTS.md"}]
    selected += [p for p in paths if p.startswith(("research/","experiments/","Hypergames/")) and Path(p).name in {"README.md","THEORY.md","PROTOCOL.md","RESULTS.md","REPORT.md"}]
    selected += [p for p in paths if p.startswith("skills/") and p.endswith("/SKILL.md")]
    selected += [p for p in ("README.md","lean/CLAIMS.md","reviews/FABLE_REFEREE_REPORT.md",
                 "reviews/FABLE_RESEARCH_PRIORITY.md","scripts/check_receipts.py") if p in paths]
    return sorted(set(selected))


def panel_for(path):
    for name, pattern in PANELS.items():
        if re.search(pattern,path,re.I):return name
    raise AssertionError(path)


def excerpt(text, limit):
    """Deterministic heading + substantive paragraph excerpts; preserve line ranges."""
    lines=text.splitlines()
    if len(text)<=limit:
        return [{"first":1,"last":len(lines),"text":text}]
    starts=[i for i,l in enumerate(lines) if re.match(r"^#{1,3} ",l)]
    starts=sorted(set([0]+starts))
    # Cover distributed sections, with head and late limitations retained.
    if len(starts)>8:
        starts=[starts[round(i*(len(starts)-1)/7)] for i in range(8)]
    per=max(180,limit//max(1,len(starts)))
    out=[]
    for i in starts:
        j=i
        size=0
        while j<len(lines) and size+len(lines[j])+1<=per:
            size+=len(lines[j])+1;j+=1
        if j>i:out.append({"first":i+1,"last":j,"text":"\n".join(lines[i:j])})
    return out


def write(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")


def prepare(args):
    root=args.repo.resolve()
    paths=inventory(root,args.ref)
    if not paths:raise ValueError("empty inventory")
    groups={k:[] for k in PANELS}
    entries=[]
    for path in paths:
        txt,sha,blob=source(root,args.ref,path)
        panel=panel_for(path)
        groups[panel].append((path,txt,sha,blob))
        entries.append({"path":path,"git_blob_sha":blob,"sha256":sha,"chars":len(txt),"panel":panel})
    dg_context=[]
    if args.datagoblin:
        for path in ("configs/dg_srs_01/expanded_catalog_100.json",
                     "reports/dg_rpg_01/GOBLINWORLD_RESEARCH_ATLAS.md",
                     "reports/dg_rpg_01/ranked_followup_gyms.json",
                     "reports/dg_srs_01/DG_SRS_01_REPORT.md"):
            try:txt,sha,blob=source(args.datagoblin,args.dg_ref,path)
            except subprocess.CalledProcessError:
                dg_context.append({"path":path,"status":"missing_at_pin"});continue
            if path.endswith("expanded_catalog_100.json"):
                rows=json.loads(txt)["roots"]
                body=[{k:r[k] for k in ("id","title","family","question","evidence_status") if k in r}
                      for r in rows]
                # Complete root-title roster; avoid placing all source contents in every packet.
                body=[{"id":r.get("id"),"title":r.get("title"),"family":r.get("family")} for r in body]
            else:body=excerpt(txt,4500)
            dg_context.append({"path":path,"sha256":sha,"git_blob_sha":blob,"content":body})
    out=args.out
    out.mkdir(parents=True,exist_ok=False)
    tree=git(root,"ls-tree","-r",args.ref).decode().splitlines()
    full_inventory=[{"git_blob_sha":line.split("\t",1)[0].split()[2],"path":line.split("\t",1)[1]}
                    for line in tree if "\t" in line and line.split("\t",1)[1].startswith(
                        ("paper/","lean/","src/spiral_ln/","tests/","scripts/","gyms/","research/","experiments/","Hypergames/","skills/"))]
    write(out/"full_source_inventory.json",{"evalmath_ref":args.ref,"entries":full_inventory})
    requests=[]
    for name,rows in groups.items():
        if not rows:continue
        # A fixed aggregate character cap keeps the remaining promo budget predictable.
        per=max(650,min(14000,42000//len(rows)))
        data=[{"path":p,"sha256":s,"git_blob_sha":b,"source_chars":len(t),
               "excerpts":excerpt(t,per)} for p,t,s,b in rows]
        missing=[r["path"] for r in data if not r["excerpts"]]
        packet={"schema":"evalmath.esf01.review_packet.v1","evalmath_ref":args.ref,
                "panel":name,"sources":data,"sources_without_excerpt":missing,
                "source_scope":"distributed excerpts; claims may need full source review",
                "complete_math_inventory_sha256":digest(full_inventory),
                "whole_program_index":entries if name=="frontier" else
                    [{"path":e["path"],"panel":e["panel"]} for e in entries],
                "datagoblin_context":dg_context if name in {"frontier","mechanisms"} else
                    [{"path":d["path"],"sha256":d.get("sha256")} for d in dg_context],
                "datagoblin_ref":args.dg_ref,"allowed_families":LANES[name],
                "allowed_profiles":list(PROFILES),"research_only":True}
        packet["packet_sha256"]=digest(packet)
        write(out/f"{name}.packet.json",packet)
        requests.append({"custom_id":f"esf01_r1_{name}_{packet['packet_sha256'][:12]}",
                         "root_id":name,"system":SYSTEM,"user":canonical(packet)})
    manifest={"schema":"evalmath.esf01.review.v1","evalmath_ref":args.ref,"datagoblin_ref":args.dg_ref,
              "source_count":len(entries),"source_inventory":entries,"requests":requests,
              "max_output_tokens":args.max_tokens,"effort":"high","custody":"research_only",
              "training_eligible":False,"paid_calls":0,
              "source_review_required":"Review actual excerpts for privacy, rights and evaluator leakage before approval."}
    manifest["request_sha256"]=digest(manifest)
    write(out/"requests.json",manifest)
    print(json.dumps({"requests":len(requests),"source_count":len(entries),
                      "request_sha256":manifest["request_sha256"],"out":str(out)},indent=2))


def make(args):
    families=args.family or list(FAMILIES)
    public,gold=generate(families,args.profile,args.count,args.seed,args.split)
    print(json.dumps(write_pack(args.out,public,gold,seed=args.seed,split=args.split,profile=args.profile),indent=2))


def existing_ledger(path):
    if not path.is_file():raise ValueError("existing shared DataGoblin ledger required")
    from datagoblin.training_gym.dg_cotp_02.budget import BudgetLedger
    return BudgetLedger(path,cap_micro_usd=int(json.loads(path.read_text())["cap_micro_usd"]))


def check_manifest(path):
    doc=json.loads(path.read_text(encoding="utf-8"))
    supplied=doc.pop("request_sha256")
    if digest(doc)!=supplied:raise ValueError("request digest mismatch")
    doc["request_sha256"]=supplied
    if doc["custody"]!="research_only" or doc["training_eligible"] is not False:
        raise PermissionError("wrong custody")
    return doc


def submit(args):
    from datagoblin.training_gym.dg_cotp_02.budget import estimate_max_cost_micro_usd
    from datagoblin.training_gym.dg_cotp_02.fable_client import submit_fable_batch
    doc=check_manifest(args.requests)
    if not args.confirm_paid or args.approved_sha!=doc["request_sha256"]:
        raise PermissionError("confirm credits, review exact packets, approve digest before paid submission")
    ledger=existing_ledger(args.ledger)
    fresh=[r for r in doc["requests"] if not ledger.has_request(r["custom_id"])]
    if not fresh:raise ValueError("already reserved: reconcile existing batches, do not resend")
    if not all(r["custom_id"].startswith("esf01_") for r in fresh):raise ValueError("foreign request")
    cap=int(args.max_new_usd*1_000_000)
    if cap<=0:raise ValueError("positive approved spending cap required")
    est=sum(estimate_max_cost_micro_usd(
        input_tokens_est=max(256,int((len(r["system"])+len(r["user"]))/3.2)),
        max_output_tokens=doc["max_output_tokens"],mode="batch") for r in fresh)
    if est>cap or est>ledger.summary()["remaining_usable_micro_usd"]:
        raise ValueError(f"reservation {est} exceeds approved or shared usable budget")
    # Same single-writer operator and existing ledger; never run concurrently with other campaigns.
    result=submit_fable_batch(ledger=ledger,wave_name="esf01_review",
        requests_spec=fresh,out_dir=args.out,effort=doc["effort"],
        max_tokens=doc["max_output_tokens"])
    print(json.dumps(result,indent=2))


def collect(args):
    from datagoblin.training_gym.dg_cotp_02.fable_client import poll_and_collect_fable_batch
    ledger=existing_ledger(args.ledger)
    batch=ledger.data["batches"].get(args.batch_id)
    if not batch or not all(c.startswith("esf01_") for c in batch["custom_ids"]):
        raise ValueError("batch is not registered to this gym")
    print(json.dumps(poll_and_collect_fable_batch(ledger=ledger,batch_id=args.batch_id,
          out_dir=args.out,poll_interval_seconds=10,max_wait_seconds=30),indent=2))


def continue_review(args):
    manifest=check_manifest(args.requests)
    results=json.loads(args.results.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True,exist_ok=False)
    decisions=[]; follow=[]
    for r in manifest["requests"]:
        cid=r["custom_id"]; panel=r["root_id"]; row=results.get(cid,{})
        write(args.out/f"{panel}.provider_result.json",row)
        try:
            if row.get("status")!="succeeded" or row.get("stop_reason")!="end_turn":
                raise ValueError("missing or truncated response")
            body=json.loads(row["visible_text"])
            action=body["action"]
            family=action["family"]; profile=action["profile"]
            if family not in LANES[panel] or profile not in PROFILES:
                raise ValueError("action outside registered menu")
            if not isinstance(body.get("decision_proxy"),str) or not body["decision_proxy"].strip():
                raise ValueError("missing pre-action rationale")
            if not isinstance(body.get("predictions"),str) or not body["predictions"].strip():
                raise ValueError("missing frozen predictions")
            frozen={"request_id":cid,"response_sha256":digest(row),"decision_proxy":body["decision_proxy"],
                    "predictions":body["predictions"],"action":action,"custody":"research_only"}
            frozen["freeze_sha256"]=digest(frozen)
            write(args.out/f"{panel}.frozen.json",frozen)
            # A decision selects a real pre-existing generator/profile. Its output is
            # never automatically admitted into training, nor teacher-authored gold.
            seed=int(digest({"cid":cid,"operator_seed":args.seed})[:12],16)
            public,gold=generate([family],profile,args.count,seed,"development")
            gold_hash=digest(gold)
            obs={"family":family,"profile":profile,"requested":args.count,
                 "actual":len(public),"unique":len({x["task_id"] for x in public}),
                 "gold_sha256":gold_hash,"source":FAMILIES[family][0],
                 "evidence":"exact finite generator checks; no model capability result",
                 "public_examples":public[:2],"gold_examples":gold[:2]}
            obs["observation_sha256"]=digest(obs)
            write(args.out/f"{panel}.observation.json",obs)
            decisions.append({"panel":panel,"status":"executed","freeze_sha256":frozen["freeze_sha256"],
                              "observation_sha256":obs["observation_sha256"]})
            follow.append({"custom_id":f"esf01_r2_{panel}_{obs['observation_sha256'][:12]}",
                           "root_id":panel,"system":FOLLOWUP,
                           "user":canonical({"original":body,"observation":obs,
                                             "source_packet_sha256":digest(r)})})
        except (ValueError,KeyError,TypeError,AssertionError) as e:
            decisions.append({"panel":panel,"status":"rejected","reason":str(e)})
    write(args.out/"decisions.json",{"decisions":decisions,"teacher_selected_training_export":False})
    # Follow-up is optional: allow selecting the highest-value panels in a reviewed new manifest.
    doc={"schema":"evalmath.esf01.review.v1","requests":follow,
         "max_output_tokens":args.max_tokens,"effort":"high","custody":"research_only",
         "training_eligible":False}
    doc["request_sha256"]=digest(doc)
    write(args.out/"followup_requests.json",doc)
    print(json.dumps({"decisions":decisions,"followup_request_sha256":doc["request_sha256"]},indent=2))


def preflight(args):
    from datagoblin.training_gym.dg_cotp_02.budget import estimate_max_cost_micro_usd
    doc=check_manifest(args.requests)
    ledger=existing_ledger(args.ledger)
    rows=[]
    for r in doc["requests"]:
        if ledger.has_request(r["custom_id"]):continue
        est=estimate_max_cost_micro_usd(
            input_tokens_est=max(256,int((len(r["system"])+len(r["user"]))/3.2)),
            max_output_tokens=doc["max_output_tokens"],mode="batch")
        rows.append({"custom_id":r["custom_id"],"estimated_max_micro_usd":est})
    total=sum(r["estimated_max_micro_usd"] for r in rows)
    remaining=ledger.summary()["remaining_usable_micro_usd"]
    print(json.dumps({"request_sha256":doc["request_sha256"],"requests":rows,
                      "estimated_max_micro_usd":total,"remaining_usable_micro_usd":remaining,
                      "fits":total<=remaining,"paid_calls":0},indent=2))


def synthesize(args):
    """One integrated whole-program review with actual first-wave and followup evidence."""
    records=[]
    for p in args.results:
        rows=json.loads(p.read_text(encoding="utf-8"))
        for cid,row in sorted(rows.items()):
            if not cid.startswith("esf01_"):continue
            record={"custom_id":cid,"status":row.get("status"),"stop_reason":row.get("stop_reason"),
                    "response_sha256":digest(row)}
            if row.get("status")=="succeeded" and row.get("stop_reason")=="end_turn":
                try:
                    body=json.loads(row["visible_text"])
                    record["review"]=excerpt(str(body.get("review_markdown","")),2500)
                    for k in ("ranked_repairs","proposed_generators","repairs","next_experiments","claim_updates"):
                        if k in body:
                            record[k]=excerpt(canonical(body[k]),2200)
                except (ValueError,TypeError):record["parse_error"]=True
            records.append(record)
    if not records:raise ValueError("no source results")
    prompt=("Write a mathematically substantive integrated referee report on the whole EvalMath program. "
            "Rank ten concrete repairs and ten independent exact synthetic generators, specifying domains, "
            "input schemas, oracle derivations, boundary cases, counterexamples, independent verification, "
            "family-disjoint split plans and expected scientific transfer to DataGoblin and looped models. "
            "Separate source-supported findings, conditional claims and open questions; distinguish proposal "
            "from test. Recommend a curriculum with explicit difficulty axes. Return JSON with review_markdown, "
            "ranked_repairs, proposed_generators, open_mathematics, experiment_plan. Research-only.\n\n"
            +canonical(records))
    doc={"schema":"evalmath.esf01.review.v1","custody":"research_only","training_eligible":False,
         "effort":"high","max_output_tokens":args.max_tokens,
         "requests":[{"custom_id":f"esf01_synthesis_{digest(records)[:12]}","root_id":"synthesis",
                      "system":FOLLOWUP,"user":prompt}]}
    doc["request_sha256"]=digest(doc)
    write(args.out,doc)
    print(doc["request_sha256"])


def main():
    p=argparse.ArgumentParser()
    sp=p.add_subparsers(dest="cmd",required=True)
    a=sp.add_parser("prepare");a.set_defaults(fn=prepare)
    a.add_argument("--repo",type=Path,default=Path("."));a.add_argument("--ref",default=PIN)
    a.add_argument("--datagoblin",type=Path);a.add_argument("--dg-ref",default=DG_PIN)
    a.add_argument("--max-tokens",type=int,choices=(16384,24576,36000),default=24576)
    a.add_argument("--out",type=Path,required=True)
    a=sp.add_parser("generate");a.set_defaults(fn=make)
    a.add_argument("--family",choices=list(FAMILIES),nargs="+");a.add_argument("--profile",choices=PROFILES,default="baseline")
    a.add_argument("--count",type=int,default=32);a.add_argument("--seed",type=int,default=137)
    a.add_argument("--split",choices=("discovery","development"),default="discovery");a.add_argument("--out",type=Path,required=True)
    a=sp.add_parser("preflight");a.set_defaults(fn=preflight)
    a.add_argument("--requests",type=Path,required=True);a.add_argument("--ledger",type=Path,required=True)
    a=sp.add_parser("synthesize");a.set_defaults(fn=synthesize)
    a.add_argument("--results",type=Path,nargs="+",required=True);a.add_argument("--max-tokens",type=int,choices=(16384,24576,36000),default=24576);a.add_argument("--out",type=Path,required=True)
    a=sp.add_parser("submit");a.set_defaults(fn=submit)
    a.add_argument("--requests",type=Path,required=True);a.add_argument("--approved-sha",required=True)
    a.add_argument("--ledger",type=Path,required=True);a.add_argument("--max-new-usd",type=Decimal,required=True)
    a.add_argument("--confirm-paid",action="store_true");a.add_argument("--out",type=Path,required=True)
    a=sp.add_parser("collect");a.set_defaults(fn=collect)
    a.add_argument("--ledger",type=Path,required=True);a.add_argument("--batch-id",required=True)
    a.add_argument("--out",type=Path,required=True)
    a=sp.add_parser("continue");a.set_defaults(fn=continue_review)
    a.add_argument("--requests",type=Path,required=True);a.add_argument("--results",type=Path,required=True)
    a.add_argument("--count",type=int,default=16);a.add_argument("--seed",type=int,default=20261129)
    a.add_argument("--max-tokens",type=int,choices=(16384,24576,36000),default=16384)
    a.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    args.fn(args)


if __name__=="__main__":main()
