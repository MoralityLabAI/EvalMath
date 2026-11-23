# UGCS-01: four conjectures on finite translation-game space

Status: research protocol, 2026-11-09. Target repositories: OntologicalProofs for algebraic lemmas, EvalMath for finite oracles. The source is [OpenAI's claimed Unique Games theorem](https://github.com/openai/math/tree/main/preprints/The-Unique-Games-Theorem-September-23-2026), especially its F2^s translation-game output and its nonlinear latent-noise lemma. The manuscript and its Lean formalization are primary evidence; these new proposals have their own proof obligations. Upstream scholarly review is ongoing.

## Shared model and claim discipline

A finite *edge-occurrence* graph G=(V,E), including parallel edges when explicitly permitted, carries shifts c_e in K=F2^s. A labeling a satisfies e=(u,v,c) iff a_v=a_u+c_e. Define phi(c)=min_a |{e:a_v-a_u != c_e}|/|E|. The diagonal projector P_e on the Stone space K^V indicates satisfaction, and H_c=I-(1/|E|)sum_e P_e. Its exact ground energy equals phi(c). For a graph with no edges set phi=0 and H=0. Edge occurrences are counted with multiplicity; K-valued nonzero residuals cost one edge irrespective of bit count.

**Statuses:** identities stated as elementary theorems are accompanied by arguments and finite tests. Conjectures below are unproved. Float eigenvalues are numerical measurements. Full UGC hardness is never assumed by the finite computations.

## C1: dimension-free expansion versus twisted spectral frustration

On loopless connected bounded-degree graph families with Cheeger edge expansion at least h>0, define for each nontrivial character chi of K the signed adjacency A_chi with edge sign chi(c_e), and L_chi=I-D^(-1/2) A_chi D^(-1/2). Let Lambda(c)=average_{chi != 1} lambda_min(L_chi).

**Conjecture C1.** There is A(h,D)>0, independent of s, with A(h,D)phi(c)<=Lambda(c) on such expanding families. An elementary upper bound, valid without expansion, is

    Lambda(c) <= (|K|/(|K|-1)) phi(c).

To see the upper bound, take a best labeling a and the test vector f_v=chi(a_v); its Rayleigh numerator is 4 times the number of edges where chi sees a nonzero residual, and the denominator is 2|E|. Every nonzero residual is detected by |K|/2 of the |K|-1 nontrivial characters. The conjectured lower inequality must assemble character-wise eigenvectors into a single K-labeling; these eigenvectors may disagree. A sequence of bounded-degree expanders with Lambda/phi approaching zero as s grows would refute C1. The ratio must be measured on nonflat instances only.

C1 numerical census: C4/F2^2 (256 games, ratio 0.781049 on all nonflat instances), K4/F2 (64 games, ratio 1.527864..2), K3,3/F2 (512 games, ratio 1.315342..1.5). C4 is not a positive-expansion *family* in the asymptotic sense; these numbers are calibration examples.

## C2: first frustrated holonomy as a moment obstruction

Write mu_j(c)=|K|^(-|V|)sum_a H_c(a)^j. A *simple edge cycle* includes a self-loop (length 1) or a pair of parallel edges (length 2); cycles are counted by distinct edge sets. Let ell be the shortest cycle with nonzero sum of shifts and N_ell the number of such shortest cycles.

**Exact finite identity:** mu_j(c)=mu_j(0) for 0<=j<ell, and

    mu_ell(c)-mu_ell(0)
      = (-1)^(ell+1) ell! N_ell / (|E|^ell |K|^(ell-1)).

Proof sketch: expand H_c^j as products of satisfaction indicators. A set of fewer than ell edge occurrences has the same consistency rank as its flat analogue, because any cycle in the set has zero holonomy. At j=ell, precisely the products containing all edges of a shortest frustrated simple cycle contribute a difference. There are ell! permutations per edge set, and the flat cycle has satisfaction probability |K|^(-(ell-1)); the frustrated cycle has probability zero. All remaining contributions cancel. If all holonomies vanish, a gauge translation identifies the entire flat spectrum.

**Conjecture C2:** for random d-regular locally tree-like graphs (d>=3) and independent uniform K-translations, the quenched free-energy density of Z_c(z)=E_a (1+z)^(# satisfied edges) agrees with the flat model in a high-temperature interval and separates past a sharp z_c(d,|K|). Define z_c by limiting free-energy separation rather than finite-size crossover. This goes beyond the finite moment identity; transfer-matrix, Bethe, and finite-size-scaling checks are required.

C2 exact census: 256 four-cycle F2^2 connections, 192 with first obstructed cycle length 4; all tested coefficients equal -3/2048. Loop, double-edge, and triangle witnesses also pass.

## C3: a bounded-degree observability hierarchy

The upstream lemma constructs a K-equivariant nonlinear C:V->K with arbitrarily small change under its noise law mu, despite detection by sufficiently high-rank *linear* families. Its actual rank quantifiers should be preserved when attempting generalization.

**Conjecture C3:** for each fixed d>=2 and target stability p>0, some equivariant nonlinear code C of algebraic degree greater than d and independent noise mu achieve change probability <=p, while every polynomial observation family of degree <=d whose restriction to K has rank above a threshold r_d(p) detects noise with probability >=kappa_d>0, uniformly in the ambient dimension. A quantitative separation of C from low-degree polynomial approximants is likely necessary. The intended restriction-to-K is a linear map; a bare polynomial without a well-defined linear restriction is excluded.

**Necessary condition / negative control:** in the rank-one model V=F2 x F2^r, C(k,u)=k+q(u), a probe F(k,u)=k+q(u) has full rank on K and changes with exactly the stability probability. If deg(q)<=d, any alleged degree-d detection floor kappa_d>p fails. Our code enumerates all F=k+f(u) with deg(f)<=d on r<=3 and measures exact detection; the test is a small restricted probe family, not a check of the full upstream rank threshold.

C3 next falsification gate: search recursive nonlinear gadgets whose ANF degree exceeds d, then optimize all allowed degree-d probes. Report rank thresholds, approximation distance and observed minimum sensitivity separately.

## C4: approximate covering-degree versus base editing rank

For a connected base graph, holonomy is a homomorphism pi_1(G)->K with image H. The connected cover corresponding to its kernel has degree |H| and trivialized lifted connection. Every connected cover with a flat lift has degree divisible by |H|, by the subgroup index formula. Consequently the minimum **exact** flat-cover degree is |H|=2^rank(H). This is an elementary covering-space identity.

Let r_epsilon(c) be the minimum degree of a connected cover with lifted frustration <=epsilon. Let r_edit_epsilon(c) be the minimum |im(Hol_{c'})| after changing at most epsilon|E| base-edge translations. Pulling such a c' to its regular holonomy cover proves

    r_epsilon(c) <= r_edit_epsilon(c).

**Conjecture C4:** on bounded-degree expanding graph families there is a constant C(h,D) with r_edit_{C epsilon}(c) <= (r_epsilon(c))^C for sufficiently small epsilon, subject to C epsilon<1/2. This asks whether cheap approximate trivialization upstairs forces a controlled-rank repair downstairs. It may fail; a cover with inconsistent sheet-wise labelings is the natural adversarial family.

C4 exact tests: an obstructed C4 needs degree two and its double cover is flat. A K2,3 game with two independent F2^2 holonomies needs degree four for exact flattening; every connected degree-two cover has at least 1/6 frustrated lifted edges. Editing one base edge reduces image size from four to two for that witness. The tests enumerate all double-cover chord toggles in a spanning-tree gauge and verify an explicit lifted labeling for the regular cover.

## Reproduction and next gates

    PYTHONPATH=src python -m pytest -q tests/test_game_space_conjectures.py
    PYTHONPATH=src python scripts/verify_game_space_conjectures.py

The JSON receipt in `output/game_space_conjectures/UGCS-01.json` records the bounded census and SHA256 of its source, tests, verification script and protocol. Recompute it after changes. For deeper tests: implement a GLPK/ILP oracle for larger label graphs, signed-Laplacian Cheeger extremizers, a random-regular free-energy scan, and exact quadratic-cubic low-degree probe optimization. In the Lean repository, the local triangle holonomy, gauge and lifted-edge algebra have direct proof targets; the general moment and covering statements remain paper obligations until formalized.
