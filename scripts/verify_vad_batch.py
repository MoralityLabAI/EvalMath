"""VAD-13B: matched fresh-process vs one-process batch Lean benchmark.

Run in a pinned Lean environment. Generated sources only; no untrusted proof input.
A batch is precompiled in one frontend invocation, not an interactive Lean server.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import re
import statistics
import subprocess
import time
import vad_gym as G

ALLOWED = {"propext", "Classical.choice", "Quot.sound"}


def digest(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def report(output, names):
    none = set(re.findall(r"^'([^']+)' does not depend on any axioms\s*$", output, re.M))
    some = dict(re.findall(r"^'([^']+)' depends on axioms: \[([^\]]*)\]\s*$", output, re.M))
    return {n: n in none or (n in some and
            set(x.strip() for x in some[n].split(",") if x.strip()) <= ALLOWED)
            for n in names}


def render(specs, strategy):
    bodies = [G.build(s, strategy) for s in specs]
    needed = G.closure(sorted({u for body, _ in bodies for u in G.imports_for(body)}))
    held = G.held_out_names()
    audit = G.audit_decls(G.library_decls(), held)
    assert all(audit["unit:" + n]["ok"] for n in needed)
    text = "import Init\n" + G.HEADER
    names = []
    for n in needed:
        unit = G.LIB[n]
        text += unit.body + "\n"
        names.extend(unit.theorems)
    # Each target has its own namespace (including local helper definitions).
    # Generated source is fixed, and references to any held-out theorem are forbidden.
    for j, ((body, target), spec) in enumerate(zip(bodies, specs)):
        assert G.fidelity(spec)["python_true"] and G.fidelity(spec)["renderers_agree"]
        assert not re.search(r"\b(?:sorry|admit|native_decide|unsafe|axiom)\b", G.strip_comments(body))
        clean = re.sub(r"(?m)^theorem\s+" + re.escape(target) + r"\b", "theorem _", body)
        assert not G.referenced_names(clean, held)
        ns = "VAD13_" + str(j)
        text += "\nnamespace " + ns + "\n" + body + "\nend " + ns + "\n"
        names.append(ns + "." + target)
    text += "\n".join("#print axioms " + n for n in names) + "\n"
    return text, names, needed


def jobs(specs, strategy, batch):
    if batch:
        return [render(specs, strategy)]
    # Fully cold comparison: each target includes its own required library.
    # This deliberately measures no library persistence; compare batch direct vs
    # batch lemma for the primary economic estimand.
    return [render([s], strategy) for s in specs]


def check(cmd, source, names, path, timeout):
    path.write_text(source, encoding="utf-8")
    start = time.perf_counter()
    try:
        p = subprocess.run(cmd + [str(path.resolve())], capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=timeout)
        output = p.stdout + "\n" + p.stderr
        checks = report(output, names)
        return dict(ok=p.returncode == 0 and all(checks.values()), rc=p.returncode,
                    seconds=time.perf_counter()-start, axioms=checks,
                    source_sha256=digest(source), output_tail=output[-2000:])
    except subprocess.TimeoutExpired:
        return dict(ok=False, rc=None, seconds=time.perf_counter()-start,
                    axioms={}, source_sha256=digest(source), output_tail="timeout")


def run(out, cmd, families, horizons, repeats, timeout, cold):
    out.mkdir(parents=True, exist_ok=True)
    version = subprocess.check_output(cmd+["--version"], text=True).strip()
    rows = []
    for family in families:
        # Public, nested prefixes; descriptive timing pilot, not sealed testing.
        specs = [G.gen(family, seed, "test") for seed in G.split_seeds("test")[:max(horizons)]]
        assert len(specs) == max(horizons)
        direct = "S_direct" if family == "F5" else "S_decide"
        for n in horizons:
            arms = [("batch_direct", direct, True), ("batch_lemma", "S_lemma", True)]
            if cold:
                arms += [("cold_direct", direct, False), ("cold_lemma", "S_lemma", False)]
            for repeat in range(repeats):
                order = arms[:]
                random.Random(130000+n*31+repeat).shuffle(order)
                for arm, strategy, batch in order:
                    start = time.perf_counter()
                    files = jobs(specs[:n], strategy, batch)
                    generation = time.perf_counter()-start
                    checks = []
                    for j, (source, names, units) in enumerate(files):
                        path = out / f"{family}_{n}_{repeat}_{arm}_{j}.lean"
                        r = check(cmd, source, names, path, timeout)
                        r["units"] = units
                        checks.append(r)
                    rows.append(dict(family=family,horizon=n,repeat=repeat,arm=arm,
                                     generation_seconds=generation,lean_seconds=sum(r["seconds"] for r in checks),
                                     calls=len(checks),ok=all(r["ok"] for r in checks),checks=checks))
                    (out/"receipt.json").write_text(json.dumps(dict(protocol="VAD-13B",version=version,
                        source_sha256=digest(Path(__file__).read_text()),rows=rows),indent=2)+"\n")
    summary=[]
    for family in families:
        for n in horizons:
            rr=[r for r in rows if r["family"]==family and r["horizon"]==n]
            for arm in sorted({r["arm"] for r in rr}):
                rs=[r for r in rr if r["arm"]==arm]
                summary.append(dict(family=family,horizon=n,arm=arm,ok=all(r["ok"] for r in rs),
                    median_lean_seconds=statistics.median(r["lean_seconds"] for r in rs),
                    median_total_seconds=statistics.median(r["lean_seconds"]+r["generation_seconds"] for r in rs)))
    result=dict(protocol="VAD-13B",version=version,source_sha256=digest(Path(__file__).read_text()),
                gym_sha256=hashlib.sha256(Path(G.__file__).read_bytes()).hexdigest(),rows=rows,summary=summary)
    (out/"receipt.json").write_text(json.dumps(result,indent=2)+"\n")
    if not all(r["ok"] for r in rows):
        raise SystemExit("VAD-13B kernel or axiom failure; see receipt")
    return result


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--lean",nargs="+",default=["lean"])
    p.add_argument("--families",nargs="+",default=["F1","F5"])
    p.add_argument("--horizons",nargs="+",type=int,default=[8,32,128,256])
    p.add_argument("--repeats",type=int,default=3)
    p.add_argument("--timeout",type=int,default=180)
    p.add_argument("--cold",action="store_true")
    a=p.parse_args()
    run(a.out,a.lean,a.families,a.horizons,a.repeats,a.timeout,a.cold)
