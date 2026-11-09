# UGCS-02: balanced-subgraph expansion, a cycle obstruction, and a covering lemma

**2026-11-09.** This extends [UGCS-01](game_space_conjectures_2026_11.md). Source: the 2026 [Unique Games theorem manuscript](https://github.com/openai/math/tree/main/preprints/The-Unique-Games-Theorem-September-23-2026), whose reduction outputs F2^s translation games. These finite identities do not require acceptance of the claimed hardness theorem.

## 1. Exact finite partition function

Let G=(V,E) be a finite oriented **edge-occurrence** multigraph and K=F2^s with q=|K|. Define P_e(a)=1[a(v_e)=a(u_e)+c_e] and

    Z_c(z) = q^(-|V|) sum_{a:V->K} prod_{e in E}(1+z P_e(a)).

For an edge subset F, let k(F) count connected components of (V,F), including isolated vertices. Call F **balanced** when every cycle has zero additive holonomy. Expand the product over edge subsets. A balanced F admits exactly q^{k(F)} labelings satisfying all its constraints, while an unbalanced F admits zero. Therefore the following is an **exact elementary identity**, including loops and parallel edges:

    Z_c(z) = sum_{F subset E, F balanced} z^|F| q^(k(F)-|V|).       (1)

The flat connection c=0 includes all subsets. This is a balanced-subgraph analogue of the random-cluster / Fortuin-Kasteleyn expansion; related gain-graph partition functions and balanced chromatic polynomials are established objects. The new use here is the specific testable game-space connection.

For z>=0, let the **flat q-random-cluster law** assign probability proportional to z^|F| q^(k(F)-|V|). Equation (1) implies

    Z_c(z)/Z_0(z) = Pr_{F ~ RC(G,q,z)}[F has zero holonomy].       (2)

Hence the per-edge free-energy difference is the balancedness large-deviation rate:

    (log Z_0(z)-log Z_c(z))/|E| = -log Pr_RC[balanced]/|E|.       (3)

This reframes C2 as an asymptotic threshold for **holonomy detection by a random-cluster edge subset**. Any claimed transition must state the random graph ensemble, order of limits, and quenched/annealed convention.

### First obstruction coefficient

Let ell be the shortest nonzero-holonomy cycle length and N_ell the number of such cycles as distinct edge sets. Then:

    [z^j](Z_c-Z_0)=0       for j<ell
    [z^ell](Z_c-Z_0)=-N_ell / q^(ell-1).                         (4)

The moment statement in UGCS-01 follows by changing variables from the satisfied-edge count to the frustration Hamiltonian H=1-(sum P_e)/m. More directly, at degree ell the only missing edge subsets are precisely shortest frustrated simple cycles, each with q^(1-ell) probability.

### Uniform random-gain average

With independent uniform c_e over K,

    E_c Z_c(z) = (1+z/q)^|E|.                                   (5)

Indeed a fixed edge subset F has balancedness probability q^(-( |F|-|V|+k(F) )), which cancels the graphic rank factor in (1). This is an **annealed** identity; a typical random game's log partition is governed by a different, quenched quantity. Finite exact enumeration checks (5).

## 2. Closed-form cycles give a needed negative control for C1

For a length-n cycle with one nonzero holonomy (n>=2), the transfer-matrix Fourier decomposition yields

    Z_frustrated(z)=(1+z/q)^n-(z/q)^n,
    Z_flat(z)=(1+z/q)^n+(q-1)(z/q)^n.                          (6)

Consequently their difference is exactly z^n/q^(n-1). For n>=2, the cosystolic frustration is phi=1/n. Each nontrivial character seeing the nonzero holonomy has an antiperiodic signed Laplacian with least eigenvalue 1-cos(pi/n); the other characters have eigenvalue zero. Exactly q/2 of the q-1 nontrivial characters detect it. Thus

    Lambda = q/(2(q-1)) (1-cos(pi/n))
    Lambda/phi = q n/(2(q-1)) (1-cos(pi/n))
               ~ q pi^2/(4(q-1)n) --> 0.                      (7)

This is a **rigorous non-expander counterexample** to any graph-independent C1 lower bound. The empirical 0.781049 ratio for C4/F2^2 is exactly (8/3)(1-cos(pi/4)). The expansion condition in C1 is essential.

Equation (2) becomes the exact random-cluster event

    Pr_RC[balanced] = (1-t^n)/(1+(q-1)t^n),   t=z/(q+z).        (8)

For every fixed finite z, this approaches 1 as n grows: bounded-length probes fail to see a single long frustrated cycle.

## 3. Partial covering-to-repair bound toward C4

**Proposition (paper proof, pending Lean).** Let G be connected with n vertices, m edge occurrences and maximum degree D. Suppose the edge isoperimetric inequality is |boundary(S)| >= h min(|S|,n-|S|) for nonempty proper vertex subsets S. If an r-sheeted connected graph cover admits a lifted labeling with at most B bad lifted edges, and B<h n/2, then there exists a base connection c' such that

    number of edited base edges <= B (1+D/h),
    |image(Hol_{c'})| <= r.                                     (9)

Because B<=r epsilon m, this gives r_edit_{(1+D/h) r epsilon}(c)<=r whenever the small-error condition holds.

**Argument.** Delete each base edge with at least one bad lift, leaving at most B removed base edges. If every resulting component were at most n/2 vertices, summing the expansion inequalities would give h n<=2B. Thus a component U has more than n/2 vertices. For T=V\U, every crossing edge was removed, and expansion gives |T|<=B/h. Retain all good edges internal to U; permit edits on every other edge, at most B+D|T| occurrences. For each v in U, collect the r lifted labels in its fiber as a multiset M_v over K. Every retained edge translates M_u to M_v by its shift, so there is a base potential p on U with M_v=M_root+p_v. Any retained cycle holonomy stabilizes M_root. The translation stabilizer H of an r-element multiset has cardinality dividing r, because translation acts freely on each K-orbit. Retain the good shifts, extend p arbitrarily outside U, and replace every other edge shift by dp. All cycle holonomies of the repaired base are in H, hence |image(Hol_{c'})|<=|H|<=r. The exact-cover statement is the B=0 case.

This yields a concrete quantitative bound with an r multiplier on the edit budget. Original C4 asks for an **r-independent edit-budget constant** in exchange for allowing polynomially larger holonomy image; that improvement remains a conjecture.

## 4. Tests and source references

    PYTHONPATH=src python -m pytest -q tests/test_game_space_partition.py

The eight tests check all 256 q=4 C4 shift assignments against independent direct labeling sums, three K2,3 cases, the closed-form cycles (including loops and parallel edges), annealed coefficients, random-cluster probabilities, and the spectral nonexpander control through n=24. The generic edge-subset algebra is independently formalized in `Neoplatonic/LTR/UniqueGamesPartition.lean` in the companion OntologicalProofs PR, conditional on its Lean CI.

Related prior work on gain graphs and signatures:
- Zaslavsky, *Gain graphs* and balanced chromatic polynomial lecture notes: https://people.math.binghamton.edu/zaslav/Tpapers/gaingraphs-lecture-notes.pdf
- Zaslavsky, *Totally frustrated states in the chromatic theory of gain graphs*: https://doi.org/10.1016/j.ejc.2008.02.004
- Lange, Liu, Peyerimhoff, Post, *Frustration index and Cheeger inequalities for discrete and continuous magnetic Laplacians* (2015): https://doi.org/10.1007/s00526-015-0935-x
