# UGCS-03: ASMP-9 reward-gauge access meets Unique Games optimization

**2026-11-09.** Cross-reference to an archived, pinned RSI-Topology research branch. Status: elementary finite identities and falsification controls; the broader ASMP-9 problem remains open.

## Exact source, status, and scope

- [ASMP-9 draft problem statement](https://github.com/MoralityLabAI/RSITopology/blob/78c32af4bebf14ec9044690bfb0e0bb600323830/ultra-experiments/millennium/V0_2_SCOPE_EXPANSION_DRAFT.md): identify rewards up to decision-licensed shaping transformations through specified query and intervention interfaces.
- [ASMP-9 graph-cochain census](https://github.com/MoralityLabAI/RSITopology/blob/78c32af4bebf14ec9044690bfb0e0bb600323830/ultra-experiments/millennium/asmp9_reward_gauge_census/README.md): 33,866 labelled simple graphs on 2..6 vertices. Real-valued edge rewards, coboundary/potential shaping and fundamental cycle-return queries; beta1=m-n+components exact-query threshold.
- [ASMP-9 v0.69 linear quotient theorem](https://github.com/MoralityLabAI/RSITopology/blob/78c32af4bebf14ec9044690bfb0e0bb600323830/ultra-experiments/millennium/asmp9_reward_gauge_census/joint_linear_quotient_v0_69/THEOREM_DRAFT_v0_69.md): for licensed gauge G, measurements A, nuisance N, the observable quotient kernel is A^(-1)(N+A(G)), and the intended gauge quotient is identified when this equals G. Development-only, unregistered.
- [ASMP-9 v0.82 obligation matrix](https://github.com/MoralityLabAI/RSITopology/blob/78c32af4bebf14ec9044690bfb0e0bb600323830/ultra-experiments/millennium/asmp9_reward_gauge_census/RESOLUTION_OBLIGATION_MATRIX_v0_82.md): unresolved; Qwen response-transport test rejects one globally shared coefficient.

The ASMP-9 candidate was an extension proposal beyond the frozen ASMP-1..7 set. The Unique Games application uses additive K=F2^s. The real reward-gauge experiment and the finite-field gauge game share a cochain skeleton, while their notions of decision preservation and observable access require separate justification.

## I. Exact access and gauge quotient

For finite oriented multigraph G=(V,E) with c connected components and K=F2^s, define C0=K^V and C1=K^E with vertex coboundary (dp)_e=p(v_e)-p(u_e). A spanning forest gives the holonomy map to K^beta1, where beta1=|E|-|V|+c.

    0 -> im(d) -> C1 --Hol--> K^beta1 -> 0.

The kernel identity holds because every flat connection has a vertex potential, determined by integrating along the spanning forest. Every holonomy vector occurs by assigning shifts to the chords and zero to forest edges. Each gauge class contains q^(|V|-c) connections; there are q^beta1 classes.

The ASMP-9 v0.69 kernel criterion has the same algebraic form over K with A=Hol, licensed graph gauge G=im(d), and nuisance N=0: ker(Hol)=G. This does not transfer the real-valued policy semantics.

For the specified query grammar in which one exact query returns a single K-valued cycle return, beta1 independent queries suffice to identify every gauge class and are necessary by q-ary transcript counting. Fewer queries admit a flat connection and a nonflat connection with identical fundamental-cycle answers on every queried chord. Missing one independent chord is an explicit adversarial witness.

## II. Identifiability leaves an optimization problem

The block-Hamming cosystolic objective is

    phi(c)=min_p |{e : c_e != (dp)_e}| / |E|.

It descends to the fully identified gauge quotient. For K=F2 with every edge shift equal to 1, satisfiable constraints are precisely edges crossing a binary cut, so

    phi(c) = 1 - MaxCut(G)/|E|.

Calculating the entire fundamental-cycle signature is polynomial-time, but computing phi exactly from the signature is NP-hard by the standard MAX-CUT reduction. The exact identification threshold beta1 and the computation time to optimize the identified object are separate quantities. If the claimed 2026 Unique Games reduction is established, it also gives stronger fixed-gap approximation hardness for the translation-game alphabet of that reduction; the finite experiments alone do not establish it.

ASMP-9 v0.78 separately studies the complexity of selecting a separating access family in a general finite registry. Our restricted graph query grammar makes access easy and places its computational barrier in decoding the quotient.

## III. The random-cluster invariant and local-access blind spot

UGCS-02 gives the exact gauge-invariant polynomial

    Z_c(z)=sum_{F subset E, holonomy(F)=0} z^|F| q^(k(F)-|V|).

Consequently Z, all frustration-Hamiltonian trace moments, and phi are well-defined functions of Hol(c). Gauge-equivalent edge vectors give identical Z.

Let ell be the shortest nonzero-holonomy cycle. Draw a vertex labeling uniformly from K^V and expose only the satisfaction bits P_e on a set Q of fewer than ell edge occurrences. Then the entire joint law of these observations is identical for c and for the flat connection. Proof: every subset of Q is balanced, so all mixed success-event probabilities agree; inclusion-exclusion determines the whole Boolean joint law.

For a single cycle with one nonzero shift, phi_frustrated=1/ell while phi_flat=0, yet every observer restricted to fewer than ell edge satisfaction bits has zero distinguishing information, irrespective of iid sample count. With all ell edges, flat all-satisfied probability equals q^(1-ell) and frustrated probability equals zero. At q=2 the complete satisfaction-pattern distributions have disjoint supports by parity. This is an **exact finite ASMP-2-style local/global continuation counterexample**, outside ASMP-2's registered semiparametric QMD class.

The ASMP-9 finite stochastic access program also emphasizes that target recoverability and representative insensitivity are separate requirements. Here fundamental holonomy queries satisfy both for the algebraic quotient; bounded-locality projector observations can fail recoverability.

## IV. Follow-up research problem

**UGCS-03 access/decoding frontier:** On families of bounded-degree expanding F2^s translation games, determine the minimal query arity, query count, and samples required to classify a specified cosystolic frustration gap under a frozen noisy observation grammar. Separate this from the computational cost of decoding phi after full gauge identification. Compare exact cycle-return access, local projector observations, and noisy quotient measurements. Negative controls include high-girth frustrated cycles and the binary MAX-CUT embedding.

The formulation must specify alphabet dimension, query lengths, noise dependence, expansion and approximation parameters. Its relation to ASMP-9 is the accessibility of the gauge quotient and its relation to ASMP-2 is observational continuation. No claim about identified human/model reward is made.

## V. Finite implementation

- Python: src/spiral_ln/game_space_asmp9_bridge.py.
- Tests: tests/test_game_space_asmp9_bridge.py.
- Exact checks cover all 256 four-cycle F2^2 connections (four classes of 64), K2,3 two-chord access, equal joint local projector laws, complete-cycle distinguishability and all 64 simple four-vertex graphs as MAX-CUT controls.
- Reproduce: PYTHONPATH=src python -m pytest -q tests/test_game_space_asmp9_bridge.py

The elementary cochain statements, MaxCut reduction, and cycle projection calculations are paper arguments accompanied by finite tests. The asymptotic access/decoding frontier remains open.
