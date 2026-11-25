# CFH-01 — Cross-paper counterexample discovery

**Evidence:** exact finite arithmetic on one published construction family; public development only. No trained-model results, Lean rebuild, sealed evaluation or causal claims.

## Sources and construction

- [Caiolo–Ferroni–Hoster, Conjecture 7.3 and Theorem 4.9](https://arxiv.org/html/2605.28474v1).
- [Bérczi–Coron–Eur–Li, hyperplane coalescence](https://arxiv.org/html/2610.17135v1).
- [Davis et al., proof and independent replay, pinned revision](https://github.com/1337isnot1337/solved-conjectures/tree/e1cf80b80c2fe9d22d83f1dc3673410a2ac1bf2e/results/caiolo-ferroni-hoster). The upstream proof claims the full family verified in Lean; external review pending.

Take the upstream rank-five truncation of the direct sum of the projective geometry over an eight-dimensional space and m free points, where m >= q^4 for prime power q. Keep the original q^4 labeled free points and add any extra points outside the coalescence blocks. Choose any b of the q^16 upstream blocks. The original pairwise intersection rank bound and flatness remain valid on adding free points and taking a subset. Thus the same coalescence argument applies. The removed geometric hyperplanes and geometric-three-space-plus-one-point hyperplanes are counted by b and b times the Gaussian coefficient [4 choose 3]_q. Remaining multiplicities are unchanged except for the new m. This is a mathematical reduction using the cited hypotheses, not a new Lean theorem.

For fixed q,m the flag counts and gamma coefficients are affine in b; write gamma = (u+ab,v+cb,w+eb). The discriminant is
D(b) = (c^2-4ae)b^2 + (2vc-4(ue+aw))b + v^2-4uw.
The derivative is affine, so strict negativity at both endpoints proves strict decrease over the interval. The oracle fails closed if this certificate fails. A negative D and positive gamma leading coefficient certify the claimed nonreal roots; D >= 0 alone is not a general certificate of real-rootedness. Boundary means first negative discriminant inside this construction family, not a global minimal matroid. No claim of priority for the extension.

## Replay

From this directory, Python 3.10+ with no dependencies:

    python cfh01.py > audit.json
    python check_incidence.py

Local CPU replay: 126 (q,m,polynomial) parameter cases, 22 with a negative-discriminant boundary, 104 with no such boundary; all 126 passed endpoint derivative checks and sampled direct quadratic identity checks. All 22 positive boundaries were checked directly at b and b-1. Independent arithmetic route: 466 expanded polynomial comparisons against incidence-algebra recursion passed. Both published q=17 integers reproduced. This is one conjecture genealogy, not 126 independent roots.

Source SHA-256: cfh01.py 0af3d9fb6990cbeca670706e3d944465e3330a1ed10fde40441b71f5e2b06dc2; check_incidence.py 5607b07c2e3956fd680859375a008d22db1db3a2cd697cbe01813b56fc1ce514. Generated audit.json SHA-256 c43b2c6fe734b6126e920f4e8f0b0dafe2cb9521deb60235f3e0324486c5f62c (not committed; regenerate). 

For m=q^4, dual Chow minimum b/q^16: q=17 0.9972786036729271; q=32 0.9605254209575768; q=64 0.9539092619187202; q=128 0.9591099833662444. Decimal display only. No sampled m=2q^4 or 4q^4 admitted a negative discriminant. No asymptotic or global optimality claim.

## Proposed K-level tasks

| Level | Input | Checked target |
|---|---|---|
| K1 | gamma coefficients | exact D and sign |
| K2 | valid q,m,b and definitions | gamma and D |
| K3 | q,m and oracle | first violating integer b plus adjacent certificate, or a certified absence |
| K4 | CFH target + BCEL construction | transfer argument and validity hypotheses |
| K5 | target + distractor papers | valid novel construction, independently checked |
| K6 | construction and proof goal | kernel-checked theorem and axiom audit |

K1–K3 have executable arithmetic scaffolding. K4–K6 need separate proof and adjudication harnesses. K3 is an optimization task: full coalescence is a trivial find-any baseline but not a minimality solution. Charge each actual verifier call; record candidate validity, exact objective gap, first hit, total budget, false-positive certificates, and final minimality. Compare full coalescence, uniform search, monotone bisection with derivative certificate, and algebraic quadratic solver (structural ceiling). For compact reasoners compare fixed versus recurrent and matched-token controls; log all attempted actions. Public development only. New independent construction families are required for confirmation, with a frozen manifest, development pilot, root-level preflight and matched sham if making causal claims. No synthetic accuracy or causal effect is reported.

## Attribution and license

The verifier uses mathematical formulas from the cited papers and adapts the upstream MIT-licensed arithmetic replay (especially the incidence recursion). The following upstream notice applies to adapted material:

MIT License

Copyright (c) 2026 Repository contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
