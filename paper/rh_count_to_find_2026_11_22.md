# RH-CRYPTO-26 / RH-05: what a point-count theorem does and does not buy

**Evidence class:** exact finite-domain synthetic control. **Scientific aim:** distinguish existence/counting theorems from constructive algorithms in the finite-field settings relevant to cryptographic polynomial systems.

The negative-control family is an affine equation \`a*x+b*y=c\` over \`F_p\` for nonzero \`(a,b)\`. Every instance has exactly \`p\` solutions in a domain of \`p^2\` points. Because the coefficients are explicit, a one-query witness can be constructed using a modular inverse. This is deliberately easy.

The lexicographic first-witness search cost can nevertheless range from **1** to **\`p^2-p+1\`** queries while the solution count stays exactly \`p\`. The late vertical instance \`x=p-1\` attains the worst-case bound. For uniformly random sampling without replacement, the expected first hit is \`(p^2+1)/(p+1)\`, as an exact rational number. A solution-count theorem alone provides no guarantee that a specific algorithm will find a witness quickly. This demonstration concerns the chosen black-box query order, not the intrinsic complexity of affine systems.

## Protocol

- Development primes: 17 and 31, with four linked tasks per prime.
- Confirmation primes: 43 and 53, reserved for a later independent execution.
- Each task records exact affine coefficients, exhaustive count, first lexicographic hit, a constructive witness checked by the same field equation, the extremal \`N-M+1\` bound, and the random-order expectation.
- Grading accepts only explicit field-point query sequences and reports the first verified hit. It charges the number of witness queries. Algebraic preprocessing and arithmetic cost are **outside** this pedagogical score.
- Independent unit for any empirical extrapolation is the prime/instance generator family, not all repeated point queries. Here \`n_units=2\` per phase, with eight correlated cases. No statistical generalization or causal mechanism claim is made.
- The exact count is verified by enumerating every point. The underlying combinatorial first-hit inequality follows from placing \`M\` marked items as late as possible among \`N\` slots. The rational expectation is the negative-hypergeometric minimum-order-statistic identity.

## Execution

\`\`\`bash
PYTHONPATH=src python -m spiral_ln.rh_count_to_find --phase dev --output output/rh_count_to_find_dev.json
PYTHONPATH=src pytest -q tests/test_rh_count_to_find.py
\`\`\`

An external solver can submit a JSONL line such as:

\`\`\`json
{"id":"RHCF-dev-p17-late_vertical","queries":[[16,0]]}
\`\`\`

and grade it with \`--submissions /path/to/queries.jsonl\`. The grader does not execute submitted programs or accept an unsupported proof string.

## Transfer research gate

To extend beyond affine controls, select explicit nonlinear finite-field varieties with certified cardinalities, record uniformity and degree/dimension of any point-count theorem, and add solver baselines (enumeration, random search, Gröbner/SAT or other exact algebra). Measure full field arithmetic, memory, witness verification and preprocessing. Use the independent confirmation family only after the task generator and algorithm-selection policy are frozen.

For Semaev relation search, the key question is whether a theorem about point count or prime-character cancellation yields a *constructive, lower-cost* relation acquisition algorithm. An existence theorem has to be paired with an effective extraction procedure to become a cryptanalytic improvement.

**Statistical preflight:** EvalMath's \`evalmath-mechinterp-power\` procedure was reviewed. This module is an exact synthetic math control with no neural intervention, effect threshold, sham causal measurement, or inference target. Sample power and model-specific mechanistic resolution are inapplicable. Future trained-model comparisons would need independent family-level pilot roots and the standard preflight protocol before allocating confirmation data.

Mathematical assumption ledger: [MathCan RH-CRYPTO-26](https://github.com/patrickdugan/MathCan/tree/research/rh-crypto26-assumptions-20261122/research/rh_crypto26).
