# CFH-02: certificate discovery and invariant fidelity

Status: public finite development, deterministic algorithmic pilot, no trained-model or independent-conjecture generalization evidence. No paid compute. Companion to CFH-01; motivated by selecting the dual gamma certificate rather than blindly searching the coalescence parameter.

## Task contract

A task supplies six valid labeled graphs of common order and a target invariant. Find a graph whose polynomial has a nonreal root or prove every polynomial in the finite deck has only real roots. An abstention is correct behavior when the budget cannot resolve the deck. Absence is local to the deck and does not establish the corresponding universal conjecture. The five targets are independent-set enumerator, clique enumerator, matching-size enumerator, chromatic polynomial (proper-coloring count), and dominating-set enumerator. Constructors: path, cycle, star, complete, balanced complete bipartite, disjoint matching, wheel, barbell, edgeless and seeded recursive tree. Orders 4..9, 20 shuffled decks per order, six candidates per deck, all five target invariants. The 600 tasks and all related graphs are public development. Relabeling does not create independent mathematical roots. No sealed set exists.

The verifier binds the proposed invariant ID to the task target, recomputes exact integer coefficients from the graph, and counts distinct real roots of the squarefree part with exact Sturm root counting. Graph structure and coefficient derivation are separately auditable. Matching-size enumerator is distinguished from the conventional signed matching polynomial. Chromatic coefficients come from partitions into independent color classes expanded in falling factorials. For polynomial tests strip zero factors, and normalize sign or substitute -x only if the resulting coefficients are all nonnegative. Newton's normalized inequality is necessary for real-rootedness under that premise. A violation certifies a nonreal root; passing is unknown. Degree at most one and a quadratic discriminant provide exact decisions. Reciprocal quartic/quintic polynomials admit the CFH gamma reduction when the expansion checks; a negative gamma discriminant with nonzero leading gamma coefficient supplies a nonreal-root certificate. Remaining cases require exact Sturm counts. No real-root claim is inferred from Newton passing.

## Replay

Python 3.10+, SymPy (tested 1.14.0). Run from gyms/CFH02:

    python discovery.py > receipt.json

The local run produced 12,000 policy/budget rows, 600 tasks, 372 witness decks, 228 absence decks, 2,190 distinct labeled graph-invariant pairs. Exact small-graph identity controls cover stars, complete-graph matchings, path colorings, and two artificial reciprocal gamma-discriminant examples. The reciprocal gamma branch did not fire on the graph deck itself. 465 of 635 nonreal graph-polynomial examples were caught by Newton; the remaining 170 required Sturm. All cheap certificates checked against exact root counting; all non-abstaining deck conclusions checked against the full deck. 2,190 flipped-truth, 2,190 tampered-coefficient, 8,760 wrong-route, and 8,584 unequal wrong-coefficient claims were rejected. Among wrong-route cases, 176 different invariant pairs have equal coefficient vectors: coefficient equality alone cannot establish semantic route fidelity. The explicit route ID check rejects these as well, although it does not prove the reasoner actually used the claimed derivation.

## Policy results (Sturm budget 2 per deck)

| Policy | Witness / 372 | Absence / 228 | Abstain | Coefficient queries | Sturm queries |
|---|---:|---:|---:|---:|---:|
| Direct | 238 | 0 | 362 | 1035 | 1035 |
| Degree rank + direct | 300 | 0 | 300 | 1023 | 1023 |
| Newton only | 325 | 0 | 275 | 2460 | 0 |
| Certificate ladder | 346 | 131 | 123 | 2460 | 400 |
| Degree rank + ladder | 372 | 131 | 97 | 2319 | 386 |

Rank is descending maximum degree, sum of d(d-1), then edge count; no gold labels used. Ladder scans up to six candidates for cheap certificates then escalates unresolved candidates. Direct policies stop at the Sturm budget. These are unequal coefficient budgets; the table compares two-resource tradeoffs, not identical total compute. Logical calls, not measured latency. At budget 6, degree-ranked direct and degree-ranked ladder both resolve 600/600 decks: direct uses 2,025 coefficient and 2,025 Sturm calls, ladder 2,319 coefficient and 629 Sturm calls. In the two-cost abstraction with per-call costs c and s, ignoring certificate scan overhead, ladder beats ranked direct exactly when s/c > 294/1396. No wall-clock claim. Newton-only leaves 47 witness decks unresolved and every absence deck unresolved. At budget 1 the ranked ladder finds 354 witnesses and certifies 88 absences.

## Next protocol

Use the structured target-to-construction-to-coefficient-to-certificate trace as a DataGoblin training schema, after rights and split review. A model-facing harness must distinguish invariant ID accuracy, formula fidelity, construction validity, verifier calls, and verified witness discovery. A wrong route, incomplete certificate, or budget exhaustion cannot be hard-promoted. Current code compares deterministic algorithms; it does not call an LLM or fit a recurrent model. Real cross-paper transfer needs independently curated conjecture genealogies, prospectively withheld constructions, and separate proof adjudication. Follow EvalMath's root-level preflight with independently sampled pilot roots and matched sham before neural causal claims. No power calculation or independent-root statistical inference is claimed here. No training or protected-split access.

Local source SHA-256: 5729c7e826a304f6e81c18a42f08f64fad491c08d5b028f31942861cd02b389e. Local generated receipt SHA-256: 241cc79b3fb0e06657baf83ff0282bed38690a2795a50ea7891106f4d5f5e0db. Receipt generated locally, not committed. Full repo CI and Lean build not run.
