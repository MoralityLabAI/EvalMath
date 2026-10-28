# OpenAI ETH: independent second-pass review (2026-10-27)

This directory preserves the second-pass Mythos Max referee assessment of OpenAI's *The Exponential Time Hypothesis is False*, along with an independent finite Hermite valuation probe.

**Scope and provenance.** The report reviews `openai/math@7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a` and historical EvalMath PR #10 head `898a0d1d8eb1cfc58a8a7af4153dd392fd03f84b`. The EvalMath PR has subsequently advanced to `896b775c7b8459b13dcbd846b003f37e9c5fcfcd`, where its own fast-receipt, Python and Lean CI runs were green at the time of filing. **The referee's 27-check/15-test counts belong to the older reviewed head**, not to later commits with 29 checks and 18 tests.

The Markdown report in this directory is a readable text export of that original, not a bytewise-authoritative replacement. The original supplied report's SHA-256 is `cb9bd03e81b175b06b5f22a2831acc516649c0bcdb97dd1172c1017f9d92b32b`.

## Two logically independent verdicts

**EvalMath PR #10:** the reviewer regards the source-fidelity audit as merge-ready *within that limited scope*. The original source pins, comparator definitions, receipt and specified finite checks survived the independent inspection. It does not prove the ETH theorem.

**OpenAI's ETH refutation:** the reviewer found no counterexample in the portions examined, but did **not** independently compile the pinned upstream Lean project, print the endpoint axioms, or run the comparator. The sharper tensor bounds are manuscript-only. The report therefore does not certify the ETH refutation or the finite-size performance of any SAT attack.

The report's estimated asymptotic crossover for the tensor proof is an inference of the referee, not an independently established numerical security or cryptanalytic benchmark.

## Reproduction and evidence hierarchy

The companion `hermite_probe.py` is verbatim from the reviewer's uploaded `scripts/hermite_probe.py` (Git blob `3f400f39a6fcff1bf0d2db1ffd0d3ca19bf479cf`). With standard-library Python, run `python hermite_probe.py` for the nominal and extended valuation grids. A smaller local confirmation, `probe(max_a=4, m_window=5)`, returned **864 cases**, with worst ratio **29/48**. The original referee bundle also contains `attack_hermite.py`, `attack_recursion.py`, `compare_declarations.py`, `mutation_sweep.py`, `recheck_tokens.py`, `run_a3.py`, and five logs.

During intake, we independently executed `attack_hermite.py 3`: **54/54** recoveries passed at the lemma and exact precision budgets; **12/12** deliberately failed one bit below the tight requirement. We also ran `run_a3.py 4` without Python's isolated import mode: its six reduced recursion fixtures agreed **6/6**. These are finite checks, not proofs for arbitrary parameters. The full 129,258-case referee sweep and 68 random-network experiments are **reported by the reviewer**, not claimed as independently rerun during this intake.

The original uploaded ZIP and machine logs remain the full reproducibility package. A public repo checkout alone does not include every uploaded script and log unless they are subsequently added; do not mistake this one-probe companion for the entire original experimental corpus.

## Open, decisive obligations

1. Build upstream `OAI.Algorithms.SubexponentialSAT.Main` at the pinned commit with the pinned toolchain and dependencies, inspect `#print axioms` for the final theorem, and run the upstream comparator.
2. Audit the arbitrary-density reduction's main-text lemmas independently.
3. Review the manuscript-only tensor-contraction theorem, its asymptotic precision preconditions, and whether the claimed bound has any plausible finite-size cryptanalytic implications.

The first obligation is the critical distinction between a faithful-looking source formalization and a kernel-accepted proof. This directory does not convert one into the other.
