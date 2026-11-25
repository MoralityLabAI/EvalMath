"""VAD-13C: paired physical batch timing and calibration-frozen strategy selection.
Linux GNU time is required; no persistent interactive server is claimed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import time

import vad_gym as G
import verify_vad_batch as B

ARMS = ("direct", "lemma")


def splits(family, block, h):
    # Both blocks use test-template distribution; disjoint seed ranges, not
    # the earlier template-disjoint VAD-11 calibration distribution.
    start = 910000 + block * 10000
    return {s: [G.gen(family, start + offset + i, "test") for i in range(h)]
            for s, offset in (("cal", 0), ("test", 5000))}


def measured(cmd, source, names, path, timeout):
    path.write_text(source, encoding="utf-8")
    metrics = path.with_suffix(".time")
    start = time.perf_counter()
    try:
        p = subprocess.run(["/usr/bin/time", "-f", "%U %S %M", "-o", str(metrics.resolve()),
                            *cmd, str(path.resolve())], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        elapsed = time.perf_counter() - start
        out = p.stdout + "\n" + p.stderr
        checks = B.report(out, names)
        try:
            u, s, rss = metrics.read_text().split()[-3:]
            cpu, rss = float(u) + float(s), int(rss)
        except (OSError, ValueError):
            cpu = rss = None
        return dict(ok=p.returncode == 0 and all(checks.values()) and cpu is not None,
                    rc=p.returncode, wall=elapsed, cpu=cpu, peak_rss_kib=rss,
                    axiom_checks=len(checks), axiom_pass=sum(checks.values()),
                    source_sha256=B.digest(source), output_tail=out[-1500:])
    except subprocess.TimeoutExpired:
        return dict(ok=False, rc=None, wall=time.perf_counter()-start, cpu=None,
                    peak_rss_kib=None, source_sha256=B.digest(source), output_tail="timeout")


def median(rows, key):
    return statistics.median(r[key] for r in rows)


def choose(rows):
    assert all(r["ok"] for r in rows)
    return min(ARMS, key=lambda a: (median([r for r in rows if r["arm"] == a], "total_wall"),
                                    ARMS.index(a)))


def summarize(rows, frozen):
    result = []
    for f, block, h in sorted({(r["family"], r["block"], r["horizon"]) for r in rows}):
        key = f"{f}/{block}/{h}"
        rr = [r for r in rows if (r["family"], r["block"], r["horizon"]) == (f, block, h)]
        if not all(r["ok"] for r in rr) or key not in frozen:
            result.append(dict(family=f, block=block, horizon=h, ok=False))
            continue
        cal = [r for r in rr if r["split"] == "cal"]
        test = [r for r in rr if r["split"] == "test"]
        a = frozen[key]
        d = [r for r in test if r["arm"] == "direct"]
        l = [r for r in test if r["arm"] == "lemma"]
        sel = [r for r in test if r["arm"] == a]
        if not d or not l or not sel:
            continue
        base, alt, picked = (median(x, "total_wall") for x in (d,l,sel))
        # One actual calibration run per strategy is necessary. Report both
        # all experimental repetitions and a median-one-run-per-arm sensitivity.
        cal_all = sum(r["total_wall"] for r in cal)
        cal_one = sum(median([r for r in cal if r["arm"] == x], "total_wall") for x in ARMS)
        saving = base-picked
        paired = [x["total_wall"]-y["total_wall"] for x,y in zip(
            sorted(d,key=lambda r:r["repeat"]),sorted(sel,key=lambda r:r["repeat"]))]
        result.append(dict(family=f,block=block,horizon=h,ok=True,chosen=a,
                           direct_wall=base,lemma_wall=alt,selected_wall=picked,
                           gain_lemma=base/alt,gain_selected=base/picked,
                           calibration_all_wall=cal_all,calibration_one_wall=cal_one,
                           gain_charged_all=base/(picked+cal_all),
                           gain_charged_one=base/(picked+cal_one),
                           break_even_sessions_one=(cal_one/saving if saving>0 else None),
                           break_even_sessions_all=(cal_all/saving if saving>0 else None),
                           paired_savings=paired, direct_cpu=median(d,"cpu"),
                           selected_cpu=median(sel,"cpu"),
                           direct_peak_rss_kib=max(r["peak_rss_kib"] for r in d),
                           selected_peak_rss_kib=max(r["peak_rss_kib"] for r in sel)))
    return result


def run(out,cmd,families,horizons,repeats,blocks,timeout):
    out.mkdir(parents=True,exist_ok=True)
    # Include the entire fresh split namespace in the existing renderer audit.
    original_held = G.held_out_names
    new_held = {f"vad_t_{family}_{910000+block*10000+5000+i}"
                for family in families for block in range(blocks)
                for i in range(max(horizons))}
    G.held_out_names = lambda per=None: original_held(per) | new_held
    version=subprocess.check_output(cmd+["--version"],text=True).strip()
    rows=[]; frozen={}
    meta=dict(protocol="VAD-13C",version=version,platform=platform.platform(),
              machine=platform.machine(),logical_cpus=os.cpu_count(),
              source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              dependency_sha256={Path(m.__file__).name:hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest()
                                 for m in (G,B)},horizons=horizons,repeats=repeats,blocks=blocks)
    def save():
        (out/"receipt.json").write_text(json.dumps(dict(**meta,frozen=frozen,rows=rows,
                                                        summary=summarize(rows,frozen)),indent=2)+"\n")
    for family in families:
        direct="S_direct" if family=="F5" else "S_decide"
        for block in range(blocks):
            spec=splits(family,block,max(horizons))
            for h in horizons:
                key=f"{family}/{block}/{h}"
                for split in ("cal","test"):
                    cell=[]
                    for rep in range(repeats):
                        order=list(ARMS)
                        random.Random(130300+block*10000+h*31+rep*2+(split=="test")).shuffle(order)
                        for arm in order:
                            start=time.perf_counter()
                            src,names,units=B.render(spec[split][:h],direct if arm=="direct" else "S_lemma")
                            generation=time.perf_counter()-start
                            path=out/f"{family}_{block}_{h}_{split}_{rep}_{arm}.lean"
                            row=measured(cmd,src,names,path,timeout)
                            row.update(family=family,block=block,horizon=h,split=split,repeat=rep,arm=arm,
                                       generation=generation,total_wall=generation+row["wall"],units=units)
                            rows.append(row);cell.append(row);save()
                    if not all(r["ok"] for r in cell):
                        raise SystemExit(f"Kernel or measurement failure: {key}/{split}")
                    if split=="cal":
                        frozen[key]=choose(cell);save()
    save()
    return dict(**meta,frozen=frozen,rows=rows,summary=summarize(rows,frozen))


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--lean",nargs="+",default=["lean"])
    p.add_argument("--families",nargs="+",default=list(G.FAMILIES))
    p.add_argument("--horizons",nargs="+",type=int,default=[8,32,128,256])
    p.add_argument("--repeats",type=int,default=5)
    p.add_argument("--blocks",type=int,default=2)
    p.add_argument("--timeout",type=int,default=600)
    a=p.parse_args()
    run(a.out,a.lean,a.families,a.horizons,a.repeats,a.blocks,a.timeout)
