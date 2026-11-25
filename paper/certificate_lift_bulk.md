# ZKL-20: bulk lifting cost profile and lookup equivalence

Evidence scope: algebraic identity and finite native conformance, with Lean proof candidates submitted to CI. The source relation is the same annotated de Bruijn Sort/Var/Pi/Lam/App grammar as ZKL-19. For natural cutoff k and nonnegative distances a,b, L(k,b)(L(k,a)t)=L(k,a+b)t by induction on syntax. A variable below cutoff remains unchanged; a variable above stays above. Sort is unchanged, Pi/Lam increase the cutoff only in the body, App applies the same cutoff to its children. Raw lookup identifies the original binder type; inductively, recursive step lookup agrees with raw lookup followed by one shift of i+1, including out-of-range lookup. The Lean module FeedbackChannel.CertificateLift formalizes these two identities on unbounded syntax; CI is required before claiming machine-checked status. Neither identity proves Nova circuit soundness. A bounded representation additionally needs canonical index, cutoff and distance ranges and capacity limits.

ZKL-19 measured 25,945 raw constraints per step and six verified compressed proofs on 185 rows; CI https://github.com/patrickdugan/zk-rusto-no-bitcoino/actions/runs/45586627039/job/139109768491 . ZKL-20 has 507 static local equations and an additional bounded distance field; actual constraint counts pending. Distinct state/domain/profile identity is required for comparison. Do not score a native row estimate as measured folding cost.

## Paired native diagnostics

Same 192 public roots as ZKL-19, then disjoint 192 roots with fixed generator and bulk semantics, seed bases 32000/33000/34000, 64 per family. All source goals and both certificates independently replayed; new certificates additionally satisfy selected linear equations. Exploratory, no learned candidate or statistical mechanism claim.

| family | original roots old | original roots bulk | fresh roots old | fresh roots bulk |
|---|---:|---:|---:|---:|
| weakening | 4260 | 4231 | 4150 | 4145 |
| dependent application | 14829 | 11678 | 14305 | 11294 |
| conversion | 6217 | 6226 | 6992 | 6985 |

On reused roots, total rows 25306 -> 22135; on fresh roots 25447 -> 22424. Dependent application improves on 58/64 roots in each cohort. Some small cases become longer as unit-lift memoization is replaced by distance-specific rows. This is generator-specific. Fit within 64 public objects and 64 proof rows stays 62/192 on the first cohort; fit256 increases 166 -> 173. Actual depth-9 profile for a selected 270-row dependent example is pending. Excluded roots stay in any fixed-budget score denominator.

For measured old per-step cost c0 and new c1, a matched set of proofs with row totals n0,n1 has lower raw step work iff c1*n1 < c0*n0. On the reused roots the allowable cost ratio c1/c0 is less than 25306/22135; on the dependent-only subset it is less than 14829/11678. These are break-even bounds, not actual measured savings. The new profile keeps syntax public and no privacy or production guarantee is made. See pinned implementation https://github.com/patrickdugan/zk-rusto-no-bitcoino/tree/15091c9160b262d393b453fd92050e315726003d/integrations/zkl-nova-calibration . No paid GPU or sealed benchmark roots.
