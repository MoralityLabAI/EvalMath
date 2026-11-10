# ARG-01: Independent algebraic reasoning oracle

**Status:** exact CPU reference implementation. Owner: EvalMath. The model wrapper and the experimental comparison belong in `Compactification-Theory/research/algernon/algebraic_reasoning_gym/`.

A public task contains two normalized integer formal-series input/output demonstration pairs truncated through `q^12`, a topology label (`fork`, `cascade`, `additive`, `hadamard`), and a fresh query input. The withheld answer is the query output through `q^32`. A candidate program is a three-token list over `I` (identity), `N` (sign substitution), `S` (degree doubling), `R` (formal reciprocal). The four graph layouts respectively compute `c(a(F)*b(F))`, `c(a(F)*b(a(F)))`, `c(a(F)+b(F)-1)`, and `c(a(F) hadamard b(F))`, with constant coefficient normalized to 1 for the additive and Hadamard joins.

The exact interpreter and verifier are independent of the RRC neural checkpoints. A paid candidate query executes both demonstrations through degree 12 and returns acceptance and first mismatch degree. `search()` charges each distinct program once and never sees the withheld future. `grade()` can compare the selected program with the future only after selection.

Training/decision calibration may use the 36-case `calibration` roster (12 per known source family). The 168 positive test cases have 24 examples per source family; signed, product and sparse sources were represented in prior RRC training, while rational, squared, sign-twisted product and lacunary inputs serve as distribution shifts. Twelve selected observed-prefix negatives require the complete 64-program bounded solver to abstain. Six pairs of different degree-15 futures share all observable data, giving a finite-prefix impossibility control. Inputs are generator-disjoint at the visible signature level apart from the explicit pairs. RRC-19 and older public test rosters are already known, so this is **fresh seeded evaluation**, not an externally blinded or preregistered evaluation.

The interpreter provides a complete reference over *64 syntax programs at the given observation horizon*. It proves observed coefficient equality, not infinite-series equality or the future continuation. Even full search can select the wrong continuation when candidate programs coincide through degree 12.

## Run

```sh
PYTHONPATH=src python -m unittest discover -s tests -p 'test_algebraic_reasoning_oracle.py' -v
PYTHONPATH=src python -m spiral_ln.algebraic_reasoning_oracle --out fixtures/algebraic_reasoning_oracle_v1.json --check
```

The fixture records SHA256 hashes of all deterministic rosters, accepted programs and withheld-future correct counts. Source hash is pinned separately by the downstream model harness and Git commit. All arithmetic uses Python integers without model downloads, GPU execution or external services. Independent model training and profiling are separate work.
