"""Report the *registered* eight-way development family with Holm correction.

Reads only recorded receipts. Every registered comparison appears, including
missing runs. Missing p-values are assigned p=1 for familywise multiplicity,
and the report refuses to infer missing outcomes. This is not confirmation.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

SCHEMA = "preferred-evals/campaign-eight-development-v1"

def registered(reg):
    if reg.get("schema") != "preferred-evals/campaign-registration-v1":
        raise ValueError("campaign registration schema mismatch")
    test=reg["test"]
    if str(test.get("minimum_effect")) != "0.10":
        raise ValueError("registered minimum effect must remain 0.10")
    if str(test.get("multiplicity", "")).lower() != "holm over the 8 comparisons above":
        raise ValueError("the frozen registration specifies eight-comparison Holm")
    comps=reg["comparisons"]
    if len(comps)!=7 or "within_model_comparison" not in reg:
        raise ValueError("registered family must contain seven between-model and one within-model comparisons")
    return [{"id":f"between-{i+1}","name":c["benchmark"],"type":"between_model"} for i,c in enumerate(comps)]+[
        {"id":"within-8","name":reg["within_model_comparison"]["benchmark"]+" (Bonsai reasoning vs no-CoT)","type":"within_model"}]

def holm(pvalues):
    """Holm adjustment across eight entries, treating unavailable p-values as 1."""
    n=len(pvalues)
    order=sorted(range(n),key=lambda i:(pvalues[i] if pvalues[i] is not None else 1.,i))
    out=[1.]*n
    running=0.
    for rank,i in enumerate(order):
        p=pvalues[i] if pvalues[i] is not None else 1.
        running=max(running,min(1.,(n-rank)*p))
        out[i]=running
    return out

def report(reg, index, base_dir):
    family=registered(reg)
    if index.get("schema")!="preferred-evals/campaign-receipt-index-v1":
        raise ValueError("invalid receipt index schema")
    source=index.get("comparisons")
    if not isinstance(source,dict) or set(source)!=set(x["id"] for x in family):
        raise ValueError("receipt index must name exactly all eight registered comparisons")
    rows=[]; raw=[]
    for x in family:
        item=source[x["id"]]
        if not isinstance(item,dict):
            raise ValueError(f"{x['id']}: index entry must be object")
        fpath=item.get("fsi_result")
        cpath=item.get("paired_receipt")
        def load_optional(path):
            if not path:
                return None
            file=(base_dir/path).resolve()
            if not file.is_relative_to(base_dir.resolve()):
                raise ValueError("receipt cannot escape campaign directory")
            if not file.is_file():
                return None
            return json.loads(file.read_text(encoding="utf-8"))
        fsi=load_optional(fpath)
        paired=load_optional(cpath)
        if fsi is not None:
            if abs(float(fsi.get("minimum_effect",-1))-.10)>1e-12:
                raise ValueError(f"{x['id']}: FSI result uses wrong minimum effect")
            if fsi.get("planned_comparisons")!=8:
                raise ValueError(f"{x['id']}: FSI result uses wrong comparison family")
            p=fsi.get("p_unadjusted")
            if p is not None and (type(p) not in (float,int) or not 0<=p<=1):
                raise ValueError("invalid p-value")
        else:
            p=None
        assigned=(paired or {}).get("total_assigned_rollouts")
        scored=(paired or {}).get("n_paired_scored")
        missing=(paired or {}).get("n_infra_or_missing")
        if paired is not None and isinstance(assigned,int) and isinstance(scored,int) and isinstance(missing,int):
            if assigned != scored+missing:
                raise ValueError(f"{x['id']}: assigned denominator does not match scored plus excluded")
        if fsi is not None and paired is not None and fsi.get("n_cases") != scored:
            raise ValueError(f"{x['id']}: FSI case count differs from paired score")
        status=("observed" if fsi is not None and p is not None else
                "unscorable" if fsi is not None else "missing_receipts")
        raw.append(p)
        rows.append({**x,"status":status,"reason":item.get("reason","") if status!="observed" else "",
                     "assigned":assigned,"paired_scored":scored,"missing_or_error":missing,
                     "independent_roots":fsi.get("n_clusters") if fsi else (paired or {}).get("n_roots_paired_scored"),
                     "candidate_correct":(paired or {}).get("candidate_correct_paired"),
                     "baseline_correct":(paired or {}).get("baseline_correct_paired"),
                     "macro_effect":fsi.get("cluster_macro_effect") if fsi else None,
                     "minimum_effect":.10,"raw_p":p,
                     "fsi_verdict":fsi.get("verdict") if fsi else None})
    adjusted=holm(raw)
    for row,p in zip(rows,adjusted):
        row["holm_p_eight"]=p if row["raw_p"] is not None else None
        row["familywise_imputation_for_missing"]=1.0 if row["raw_p"] is None else None
        row["effect_floor_met_descriptively"]=(
            row["macro_effect"]>=.10 if isinstance(row["macro_effect"],(int,float)) else None)
    return {"schema":SCHEMA,"campaign_id":reg["campaign_id"],
            "development_only":True,"minimum_effect":.10,"alpha":.05,
            "registered_comparisons":8,"multiplicity":"Holm (missing entries treated as p=1 for family size)",
            "completed_with_p":sum(x is not None for x in raw),"unobserved_or_unscorable":sum(x is None for x in raw),
            "comparisons":rows,
            "limitations":["The registration was written after partial Bonsai exposure.",
                           "Holm-adjusted p-values are exploratory; eight-comparison selection scope is preserved.",
                           "Missing runs retain an explicit row and are never inferred or scored zero.",
                           "FSI root assumptions and source/task provenance require independent checking."]}

def markdown(data):
    lines=["# PreferredEvals Bonsai vs Qwen: registered eight-comparison development ledger","",
           "This report is development evidence; the plan was written after partial Bonsai exposure.","",
           "| Contrast | Status | Assigned | Paired | Missing/error | Roots | Macro effect | Raw p | Holm p (8) |",
           "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    fmt=lambda v: "—" if v is None else (f"{v:.5g}" if isinstance(v,float) else str(v))
    for row in data["comparisons"]:
        vals=[row["name"],row["status"],row["assigned"],row["paired_scored"],
              row["missing_or_error"],row["independent_roots"],row["macro_effect"],
              row["raw_p"],row["holm_p_eight"]]
        lines.append("| "+" | ".join(fmt(x).replace("|","/") for x in vals)+" |")
    lines += ["",f"Effect floor: {data['minimum_effect']:.0%}. Registered tests: 8. Holm includes every registered arm; missing p-values contribute p=1 to the family.","",
              "Scored and missing denominators remain unreported wherever the corresponding receipt files were not published."]
    return "\n".join(lines)+"\n"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--registration",type=Path,required=True)
    p.add_argument("--index",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    p.add_argument("--out-md",type=Path,required=True)
    args=p.parse_args()
    result=report(json.loads(args.registration.read_text()),json.loads(args.index.read_text()),args.index.parent)
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    args.out_md.parent.mkdir(parents=True,exist_ok=True)
    args.out_md.write_text(markdown(result),encoding="utf-8")
if __name__=="__main__":
    main()
