# CTS-02 development: certificate-directed routing
Status: REDESIGN_OR_PILOT_ONLY. CPU, exact rational certificates; no model training, independent confirmation or mechanism claim.

## Reproduction
Run `python research/cts02/cts02.py /tmp/cts02.json`. The summary of that output equals summary.json. The generator uses seeds 10000–10063 (lens), 11000–11063 (zonotope), 12000–12063 (circle), each transformed by a seeded invertible integer affine map. All these roots are exposed development examples.

A sorted normal fan is shared by the policies. Global binary search (G), angular rank proposal plus binary fallback (R), local cone walk (L), local-first hybrid (H), and per-start randomized local/global route (S) share K=6 abstract search probes. The exact certificate is checked once for each root's common optimal support. These are simulated stopping costs, not timing or FLOP equivalence; sorting, integer/rational bit complexity and certificate checks are outside the probe ledger. All 7,410 starts agree on the optimal support when run to completion.

## Results
Equal-root success: G 2/3; R 31/48; L ~0.3505; S ~0.5082; H ~0.0985. H-G = -0.5681669259582244. Raw counts are also recorded but starts within a root are correlated. R has more raw successes than G, while G has higher equal-root success.

Development resolution preflight, four comparisons, 192 planned confirmation roots, alpha .05, 95%/95% sham envelope. Random route vs G is a routing variation control, not a mechanistic sham. Observed envelope .45; target .15; sigma .4460; approximate resolvable effect .55749. Required confirmation count undefined because target is below variation floor. Independence unverified, holdout unsealed, pilot effect below floor. No confirmation or training authorized by this receipt.

## Next experiment
Exploit the sorted normal fan explicitly. Compare interpolation with binary fallback, adaptive budget-aware routing, and a size-matched deterministic strategy; charge preprocessing, certificate verification and arithmetic costs separately. Freeze a target metric before exposing any new roots. Include higher-dimensional cases in which the cyclic ordering shortcut is unavailable. Treat CTS-02 as a failed development pilot and preserve it; do not relabel the same roots as confirmation.
