# TFAF: Theorem Fidelity Under Adversarial Formalization

Exploratory EvalMath benchmark seed for semantic fidelity in Unique Games theorem statements. This does **not** verify or refute any external proof. The finite examples do **not** establish computational hardness.

## Run

```bash
python -m unittest discover -s research/theorem_fidelity -p 'test_*.py' -v
python research/theorem_fidelity/theorem_fidelity.py
```

| Case | Mutated contract | Exact check or illustration |
|---|---|---|
| TF-01 | Soundness over every labeling becomes existence of one bad labeling | Equality edge admits a score-zero labeling although OPT=1 |
| TF-02 | Unique permutation restriction removed | Universal relation is not a permutation |
| TF-03 | Completeness and soundness promises conflated | Opposed parallel edges give OPT=1/2 |
| TF-04 | 3SAT domain silently replaced by a trivial language | The formula (x) AND (NOT x) is unsatisfiable |
| TF-05 | Alphabet permitted to depend on input size | The sequence 2^n illustrates the violated fixed-alphabet promise |
| TF-06 | Polynomial reduction time promise removed | The sequence 2^n illustrates a permitted superpolynomial runtime |

**Evidence distinctions:** TF-01 to TF-03 use exact finite game witnesses. TF-04 is a propositional counterexample. TF-05 and TF-06 are contract illustrations only; the three sample input sizes cannot establish asymptotic growth properties. No external Lean artifacts are imported at this stage.

**Next gate:** Pin the upstream Unique Games theorem source and Lean commit. Inspect the fully elaborated theorem statement, imports, assumptions and axiom dependencies. Build mutation-specific Lean examples using the repository's Mathlib toolchain, and attach exact reproducibility receipts before scoring models.

The intended benchmark measures whether a system catches semantic weakening even when an altered proposition remains formally provable.
