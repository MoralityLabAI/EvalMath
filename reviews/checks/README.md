# Referee checks

Independent executable checks written for `../FABLE_REFEREE_REPORT.md`. None imports `spiral_ln`;
each rebuilds the objects it tests from the notes' definitions. Exact arithmetic (`fractions`,
integers) except where the file says float/`mpmath` (the Gaussian constants and the sign-test power).
Recorded outputs are in `outputs/`.

```bash
python -I reviews/checks/check_multigen_two_gain.py          # ~3.5 min
python -I reviews/checks/check_selection_tie_rules.py        # 6 s
python -I reviews/checks/check_selection_any_rule.py         # ~1 min
python -I reviews/checks/check_selection_d5_sweep.py sweep 4 40 400      # ~1 min
python -I reviews/checks/check_selection_d5_sweep.py sweep 4 10 1500     # ~3 min
python -I reviews/checks/check_selection_d5_sweep.py sweep 41 50 400     # ~2 min
python -I reviews/checks/check_selection_d5_sweep.py gap 41 50 400 1160  # ~18 min
python -I reviews/checks/check_selection_d5_constants.py     # 12 s (mpmath)
python -I reviews/checks/check_leak_topology.py              # 1 s
python -I reviews/checks/check_pr1_capacity.py               # ~2.5 min
python -I reviews/checks/check_gold_four_rater.py            # ~1.5 min (sympy)
python -I reviews/checks/check_lattice_patching.py           # 1 s
python -I reviews/checks/check_mutation_chain_kl.py          # <1 s
```

`outputs/selection_heavy_summary.json` is extracted from a run of the repository's own
`scripts/verify_evaluation_selection_kl.py --heavy` (66/66 checks true); it is the only file here
produced by repository code.
