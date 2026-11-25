"""Reproducible figures for the VAD consolidated paper. Reads committed receipts or recomputes the cheap ones.

    python scripts/make_vad_figures.py --out paper/figures        (needs matplotlib)
"""
import argparse
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
COL = {"a": "#2a6f97", "b": "#bc4749", "c": "#6a994e", "d": "#7b2cbf", "e": "#555555"}


def fig_amortization(out):
    import sweep_vad_lean as s
    summary = s.run()["summary"]
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    for arm, c in (("shape", COL["a"]), ("global_shape", COL["c"]), ("concrete", COL["b"])):
        pts = [(r["horizon"], r["gain"]) for r in summary if r["arm"] == arm]
        ax.plot(*zip(*pts), marker="o", color=c, label=arm)
    ax.axhline(1, color=COL["e"], lw=0.8, ls="--")
    ax.set_xscale("log", base=2)
    ax.set_xlabel("deployment horizon (targets)")
    ax.set_ylabel("cost gain over direct proof")
    ax.set_title("VAD-05A: amortization of a cached abstraction")
    ax.legend(frameon=False)
    fig.tight_layout(); fig.savefig(out / "fig1_amortization.png", dpi=160); plt.close(fig)


def fig_voi(out):
    import verify_vad_meta_cert as c
    r = c.run()
    rows = r["rows"]
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.4))
    ax = axs[0]
    ax.plot([x["horizon"] for x in rows], [x["policy"] - x["myopic"] for x in rows], marker="o", color=COL["d"])
    ax.set_xscale("log")
    ax.set_xlabel("families in horizon"); ax.set_ylabel("planned minus myopic value (utility)")
    ax.set_title("VAD-09C: value of cross-family exploration")
    ax = axs[1]
    hz = sorted({x["actual_hazard"] for x in r["shifts"]})
    gap = []
    for h_ in hz:
        v = {x["lookahead"]: x["value"] for x in r["shifts"] if x["actual_hazard"] == h_}
        gap.append(v[96] - v[1])
    ax.plot(hz, gap, marker="o", color=COL["b"])
    ax.axhline(0, color=COL["e"], lw=0.8, ls="--"); ax.axvline(0.05, color=COL["e"], lw=0.8, ls=":")
    ax.set_xlabel("true hazard (planner assumes 0.05)"); ax.set_ylabel("long-horizon minus myopic")
    ax.set_title("misspecified switching hazard")
    fig.tight_layout(); fig.savefig(out / "fig2_cross_family_value.png", dpi=160); plt.close(fig)


def fig_agenda(out):
    d = json.loads((ROOT / "output/verified_abstraction/vad_10.json").read_text())
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.3))
    ax = axs[0]
    pols = ["direct", "greedy0", "greedy1", "greedy2", "random"]
    w = 0.25
    for i, (cls, c) in enumerate((("modular", COL["a"]), ("layered", COL["c"]), ("correlated", COL["b"]))):
        ax.bar([j + (i - 1) * w for j in range(len(pols))],
               [float(F(d["sweeps"][cls]["policies"][p]["optimal_fraction"])) for p in pols], w, color=c, label=cls)
    ax.set_xticks(range(len(pols))); ax.set_xticklabels(pols, rotation=30)
    ax.set_ylabel("fraction exactly optimal"); ax.set_title("VAD-10 sweeps"); ax.legend(frameon=False, fontsize=7)
    ax = axs[1]
    sc = d["strategic_scan"]
    p = [float(F(r["p_direct"])) for r in sc]
    ax.plot(p, [float(F(r["optimal"])) for r in sc], color=COL["c"], label="optimal")
    ax.plot(p, [float(F(r["direct"])) for r in sc], color=COL["b"], label="direct pursuit")
    ax.set_xlabel("P(direct route exists)"); ax.set_ylabel("expected utility"); ax.set_title("strategic intermediate lemma")
    ax.legend(frameon=False, fontsize=8)
    ax = axs[2]
    ks = sorted(int(k) for k in d["chain_lookahead_needed"])
    ax.plot(ks, [d["chain_lookahead_needed"][str(k)] for k in ks], marker="o", color=COL["d"])
    ax.set_xlabel("chain length k"); ax.set_ylabel("lookahead needed"); ax.set_title("delayed payoff: needed depth = k-1")
    fig.tight_layout(); fig.savefig(out / "fig3_research_agenda.png", dpi=160); plt.close(fig)


def fig_neural(out):
    p = ROOT / "output/verified_abstraction/vad_12_gate.json"
    if not p.exists():
        return
    d = json.loads(p.read_text())
    fams = list(d["regret"])
    arms = ["direct", "greedy0", "greedy1", "greedy2", "trm", "memoryless", "fixed_depth", "ff", "trm_oracle_features"]
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    w = 0.8 / len(arms)
    for i, a in enumerate(arms):
        ax.bar([j + i * w for j in range(len(fams))], [d["regret"][f][a] for f in fams], w, label=a)
    ax.set_xticks([j + 0.4 for j in range(len(fams))]); ax.set_xticklabels(fams, rotation=15)
    ax.set_ylabel("mean regret vs exact optimum"); ax.set_title("VAD-12 neural gate (lower is better)")
    ax.legend(frameon=False, fontsize=6, ncol=2)
    fig.tight_layout(); fig.savefig(out / "fig4_neural_gate.png", dpi=160); plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--out", type=Path, required=True); a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    for f in (fig_amortization, fig_voi, fig_agenda, fig_neural):
        f(a.out)
    print("figures written to", a.out)
