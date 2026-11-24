# VAD-02: compositional verified abstraction discovery

Status: 2026-11-25. Exact finite synthetic control; no neural execution or Lean kernel replay. Extends VAD-01A, not the prospective VAD-01B gym.

## Cost and composition law

For a finite library A of distinct nonzero GF(2) vectors, the shortest reference cost is

    C_A(t) = 2 min_{S subseteq A} (|S| + wt(t XOR XOR(S))).

Any repeated generator cancels in pairs; after selecting the cached references, the primitive references must be precisely the residual support. Conversely each such subset produces a derivation with that cost. Savings relative to the primitive basis are nonnegative and monotone in A. They need not be submodular: t=7, a=25, b=30 gives C_empty(t)=C_{a}(t)=C_{b}(t)=6 and C_{a,b}(t)=4. The marginal saving from adding b increases from zero to two when a is already available. The construction cost also matters.

For acyclic construction using previously constructed caches, the exact optimal construction cost satisfies

    F(empty)=0
    F(A)=min_{a in A} [F(A minus {a}) + C_{A minus {a}}(a)].

Every valid construction has a last member and a preceding order; minimize over that last choice, then use the optimal preceding order. Conversely concatenate the preceding optimal order with its cheapest final construction. Example: F({7,15})=10 versus 14 if each is built directly. The DP does not model shared physical computation, memory or general proof dependencies.

For a fixed library and charged selection work D, positive aggregate savings occur iff sum_t(C_empty(t)-C_A(t))>D+F(A). This extends the one-cache break-even law.

## Exact finite audit

The independent BFS oracle uses all primitive and library generators as edges of the XOR Cayley graph. Compare all 16 targets for every library of size 0 through 3 in dimension 4: 9,216 comparisons. Independently enumerate construction permutations using BFS costs: 576 comparisons. All pass.

Each seeded family uses dimension 24, a four-bit motif, three common noise bits, and a pair of five-bit abstractions whose XOR is the motif. The pool supplies these two and four decoys. Eight development roots include the motif and exclude its noise. There are 256 held-out roots of weight eight, sampled without replacement and disjoint from development. Three paired regimes: persistent motif, shifted disjoint motif, uniform weight-eight null. Seeds 0 through 31 are public development controls. No independence assumption across horizons or regimes.

Greedy forward search stops if no candidate improves the projected 256-root savings less exact construction cost. Joint search scores the empty set, all singles and all pairs on those same eight development roots, with fixed tie-break and the same cap of two caches. A score probe charges one unit per residual enumerated per development root, plus every residual enumeration in the subset-DP construction-cost calculation; already scored libraries do not incur a duplicate charge. The pool is given for free and both selection policies see identical candidates. The resulting per-family charge is 102 for greedy and 672 for joint. The selected joint pair costs 20 to construct. For shared roots it saves four per deployment target. Therefore the exact strict break-even is n>173, or 174 roots. Selection costs are charged even when greedy abstains. The public synthetic pair is constructed to expose complementarity; this is not a demonstration of general abstraction invention.

At 256 roots, pooled baseline cost is 131,072. Greedy costs 134,336 in all regimes and selects no pair. Joint selects the planted pair in all regimes using identical development data: shared cost 120,448 (32/32 profitable), shifted 153,216 (0/32), null 151,256 (0/32). Earlier horizons are nested. The source-hashed receipt records 24 aggregate cells and the verifier emits 768 family/method/horizon rows.

    PYTHONPATH=src python -m pytest -q tests/test_evaluation_vad_composition.py
    python src/spiral_ln/evaluation_vad_composition.py > /tmp/vad_02_full.json

## Feedback-channel implication

Correctness of a cached abstraction and the probability it pays off on future work are distinct. For a fixed finite menu of M libraries, assume iid calibration roots from the deployment distribution and per-root saving in [0,B]. Hoeffding's inequality and a union bound give, simultaneously over the menu with probability at least 1-delta,

    mu(A) >= mean_calibration(A) - B sqrt(log(M/delta)/(2m)).

Subtract the actual selection and construction charges when testing projected net gain: H times the lower bound on expected savings must exceed D+F(A). This controls expected deployment utility, not realized deployment savings. It applies under the stated fixed-menu iid assumptions, not automatically to the without-replacement synthetic control or an adaptively invented candidate library. For adaptive invention use a separately frozen proposal library and independent calibration; log all queries and report the subsequent untouched deployment sample. At m=8, M=21, B=16, delta=0.05 the bound's penalty exceeds 9.8 cost units, greater than the planted per-root saving of four. The eight-root pilot is consequently a constructive cost counterexample and no statistical certificate for future utility.

## Next prospective gate

Compare joint enumeration, beam lookahead, and a recurrent proposer using the same pool, calibration data, and fully charged score-evaluation budget. Include candidate-invention arms with separately metered costs. Freeze roots, toolchain, claims, allowed premise imports, physical inference/kernel budgets, and candidate selection before sealed evaluation. Require single-cache-negative/pair-positive tasks, nested abstractions and negative controls. Assess gains at matched verified closure, transfer under shifted motifs, proposal and rejection counts, build DAG size, and the marginal value of delayed credit. A TRM can be tested for learning to preserve initially unrewarded intermediate lemmas in a persistent library. It must beat the strongest matched symbolic comparator and survive shuffled-memory and family-label ablations. No model has yet done so.
