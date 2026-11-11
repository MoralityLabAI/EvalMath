# RHT-01: Reward hacking as an obstruction in evaluation-signal cohomology

**Research draft, 9 November 2026.** Scope: exact finite evaluation signals, an externally specified true reward, a proxy feedback channel, and small translation Unique Games used as adversarial state generators. All theorems labeled *exact* are elementary identities with complete paper arguments and independent rational tests. The candidate game-space interpretation and practical safety application remain research questions.

Related: [EvalMath evaluation design calculus](evaluation_design_calculus.md), [feedback insertions](evaluation_feedback_insertions.md), [leak topology](leak_topology.md), [ASMP-8 crosswalk](feedback_channel_rsitopology_crosswalk.md), [UGC-PT-01](unique_games_topology_eth.md), and the newer [UGCS-03 research PR](https://github.com/MoralityLabAI/EvalMath/pull/28).

## 0. Keep the three signals separate

Use the existing evaluation design notation

    E = <G, Pi, D, Z, J, A, C>,

where G is the game, Pi the controller roster and execution protocol, D instance sampling and assignment, Z trace acquisition, J judgment of the acquired record, A aggregation and uncertainty, and C the target claim and its interpretation assumptions. The feedback access regime is an additional typed operator on the judge output. The typed operator Feedback_(s,q) exposes J on evaluation source s to a later controller; q is sealed, score_only, item_level, or an explicitly registered intermediate category disclosure.

Freeze three functions on an actor-reachable candidate roster X:

    U(x): independently judged gold utility;
    P(x): reward used by selection/training, constrained to factor through
          the actor-visible feedback y=F_actor(x);
    A_gold(x): privileged independent audit evidence.

An actor may optimize P with access to F_actor. The auditor must use an independently controlled source for U or a justified uncertainty family T of admissible gold utilities. The same proxy channel alone cannot tell whether U has been misspecified: two worlds with identical F_actor and P but different gold utilities are observationally indistinguishable. An apparently clean proxy score is therefore not a topological proof of safety.

The usual reported/true readout gap rho=P(x)-U(x), the selected-policy regret R=U(x_star)-U(x_selected), and causal reward-channel tampering are separate estimands. A positive rho can occur with zero policy regret; the existing EvalMath crosswalk makes that distinction explicit. Here R is evaluated over a **frozen reachable roster**, as ASMP-8 requires.

## 1. The signal-disclosure complex and its dual

For two category maps gamma_0,gamma_1 on n evaluated items, form the bipartite intersection graph I: its vertices are category blocks and its edges are nonempty intersection cells. Each edge e has integer capacity s_e>=1; x_e in {0,...,s_e} counts passing items in cell e. Observing the two category maps separately releases their row/column margins

    y=Mx,

where M is the **unsigned** vertex-edge incidence matrix. Multiplying its column-vertex rows by -1 gives a signed incidence D, hence

    ker_Q M = ker_Q D = H_1(I;Q).

For the gold linear score U_t(x)=sum_e t_e x_e with externally justified t in Q^E, define the reward periods on a cycle z in ker D by

    period_t(z)=<t,z>=sum_e t_e z_e.

For an oriented cell edge from row to column, the exact (coboundary) cochains are t_e=psi(column)-psi(row). Such a t is also M^T lambda for lambda_row=-psi(row), lambda_column=psi(column). Thus its periods vanish on every graph cycle.

This uses a **different coefficient space** from the UGC translations: true reward is a rational 1-cochain on the *evaluation intersection graph* I, while UGC constraint shifts lie in H^1(G;F2^s) on the *environment constraint graph* G. The satisfaction map connecting them is nonlinear and is not asserted to be a chain map.

## 2. The exact reward-alias theorem (RHT-01/T1)

The following are equivalent for every cell graph with positive integral capacities:

1. Every two feasible count tables x,x' with Mx=Mx' have U_t(x)=U_t(x').
2. All fundamental-cycle reward periods <t,z_C> vanish.
3. t lies in im_Q(M^T), so U_t(x)=lambda^T Mx for an explicit lambda.
4. The reward cochain t is an exact graph coboundary.

**Proof:** (4) gives (3) by flipping row/column potential signs, and (3) gives (1). If (2) fails, take the alternating unit integer vector z of a fundamental cycle whose period is nonzero. Define x=z_+ and x'=z_-. Both respect positive capacities, Mx=Mx', and U_t(x)-U_t(x')=<t,z>!=0. Hence (1) implies (2). Fundamental cycles span ker M over Q; their vanishing periods imply t in (ker M)^perp=im M^T and give (4) via spanning-forest integration.

This theorem makes the obstruction observable as a *dual pairing* between the reward class [t] in H^1(I;Q) and the feedback-hidden cycles H_1(I;Q). It does not require that the actor can reach every feasible cell table from its policy grammar.

### Quantitative alias capacity (RHT-01/T2)

Define the maximum hidden gold-value width over a published feedback fibre:

    W(t,M,s)=max_{y}
        [max_{x:0<=x<=s, Mx=y} <t,x>
         -min_{x:0<=x<=s, Mx=y} <t,x>],

where x is integral. Every pair has difference z=x-x' with Dz=0 and -s_e<=z_e<=s_e. Conversely every integral circulation z in that capacity box yields the feasible pair z_+, z_- with identical margins. Therefore

    W(t,M,s)
      = max {<t,z>: z in ker_Z(D), -s<=z<=s}.          (1)

This is an exact **bounded maximum-cost circulation** problem on the oriented bipartite intersection graph, and a standard min-cost circulation reduction supplies a polynomial-time algorithm for rational costs after integer scaling. The checked implementation supplies two independent *exponential* finite oracles (enumeration of feedback fibres and enumeration of integral circulations), pending an optimized network-flow backend. For every s_e>=1,

    W(t,M,s)>0  iff [t] != 0 in H^1(I;Q).

## 3. Minimal extra gold audits equal cosystolic support (RHT-01/T3)

A protected auditor additionally reads the exact cell counts x_e for a selected set S of edges. The combined channel is (Mx, (x_e)_(e in S)). The gold utility is then recoverable from this disclosure for every feasible x exactly when the restriction of t to I\S is exact, i.e. its period vanishes on every cycle avoiding S.

Let k_gold(t) be the minimum number of additional audited cell counts required. Then

    k_gold(t)
      = min {|S| : [t|_(I\S)]=0}
      = min_(psi:V->Q) |{e: t_e != psi(col_e)-psi(row_e)}|. (2)

**Proof:** if t agrees with dpsi outside S, its mismatch set is contained in S. Conversely a potential psi with m mismatching edges gives an audit set S consisting of those m edges, after which all unobserved edges carry an exact cochain. The minimum over S is therefore the minimum block-Hamming representative support in the cohomology class [t]. Equation (2) is the same *form* of cosystolic distance that UGC-PT-01 derives for translation constraints, but over Q rather than the finite group F2^s.

A maximal spanning forest makes every unaudited graph acyclic. This gives k_gold(t)<=beta_1(I), while k_gold may be much smaller for a particular independently known t. Recovering **all** individual cell counts needs beta_1 off-forest disclosures by the existing EvalMath theorem; recovering one gold functional is a strictly different problem.

The resulting constructive audit certificate is

    U_t(x) = lambda^T Mx + sum_(e in S) mu_e x_e,      (3)

with lambda from the potential on unobserved edges and mu_e=t_e-(M^T lambda)_e on audited edges. The implementation returns lambda and all mu_e and checks (3) on every feasible small cell table.

**Small exact case.** Let the intersection graph be K2,2 with cells ordered (00,01,10,11), unit capacities and t=(1,0,0,1). The two tables x=(1,0,0,1), x'=(0,1,1,0) both publish margins (1,1,1,1). Their gold values are 2 and 0, so W=2, and the sole fundamental-cycle reward period has magnitude 2. Auditing **one** cell count identifies the gold score exactly. The passive channel can report equal category performance while missing a difference of 2 in the true reward.

**Important safety cost:** the additional cell counts belong to a privileged audit channel. Publishing them back to the optimizing actor increases its selection information and may create a new hacking route. The actor's Feedback ledger must register every reveal and repeated query.

## 4. The Goodhart gap splits into two mechanisms (RHT-01/T4)

Let X be a finite reachable set of count tables generated by an agent or game. Let the reported proxy be P(x)=p(Mx), with a frozen deterministic p, and let

    P_star=max_(x in X) P(x),
    A=argmax_(x in X) P(x),
    U_star=max_(x in X) U_t(x).

Choose x_bad in A with minimum U_t; put y_bad=Mx_bad and F_X(y)={x in X:Mx=y}. Define

    R_worst=U_star-U_t(x_bad),
    R_cross=U_star-max_(x in F_X(y_bad)) U_t(x),
    R_hidden=max_(x in F_X(y_bad)) U_t(x)-U_t(x_bad).

Then the identity

    R_worst=R_cross+R_hidden                              (4)

holds exactly, with both summands nonnegative. The first is proxy selection of a feedback class whose best outcome is below the true optimum. The second is the *same-feedback* ambiguity inside that class.

A topological cycle obstruction only proves the *possibility* of hidden ambiguity over the whole table box. The actual reachable roster X can exclude its cycle witnesses. Conversely R_cross can be positive even when every relevant feedback fibre is a singleton. This is a distinction between the **proxy order** and the **topological blind directions**, and it prevents attributing every hacking instance to a nonzero first Betti number.

If a protected oracle supplies only a set T of plausible gold vectors, a robust certificate takes the supremum of R_worst(t) over t in T, with all candidates and feedback queries fixed in advance. Without a justified T or independent true-outcome anchor, reward-hacking safety cannot be inferred from proxy data alone.

### Two UGC-coupled falsification controls

Define a finite translation Unique Game with alphabet F2 and constraint graph G equal to a 4-cycle with shifts (1,0,0,0). Its edge-satisfaction record under a labeling a is a binary vector x(a) on four evaluated items; the disclosure category-intersection graph is the separate K2,2 graph I. All emitted records respect the UGC parity constraint, so the reachable set X_c is a **nonlinear image** of the UGC assignment space.

1. With t=(1,0,0,0) and proxy equal to total passed edges, the labeling (0,1,0,1) yields record 1000: reported score 1, protected gold 1. The labeling (0,0,0,0) yields record 0111: reported score 3, protected gold 0. A proxy optimizer may raise its reported score from 1 to 3 while losing its true gold point. The exact reachable-set regret is 1 and it lies in R_cross, because the winning feedback margin identifies the selected table in this constrained example.
2. For the *flat* 4-cycle and a frozen restricted actor roster {1001,0110}, the two candidates generate identical separately released row and column margins and proxy score 2, while t=(1,0,0,1) assigns gold values 2 and 0. Under adversarial tie-breaking R_hidden=2 and R_cross=0.

These cases use the actual UGC-PT-01 finite translation game semantics. They illustrate both reward-hacking mechanisms; they are not evidence that a neural agent will learn either policy.

## 5. A second, endpoint-relative graph-cohomology condition (RHT-02)

Reward hacking can also exploit how reward is accumulated **along paths** in the state/action graph, independently of the disclosure graph I.

Freeze a finite directed transition graph G_path with true edge reward r_e, proxy reward rhat_e and a designated start s plus terminal set T. Let omega_e=rhat_e-r_e. For *undiscounted* path returns, if there exists a potential psi with

    omega_e=psi(v)-psi(u) for each allowed edge u->v,
    psi(t)=constant for every terminal t in T,           (5)

then every s-to-terminal path receives the *same additive proxy offset* psi(T)-psi(s) and all path rankings are preserved. This is exact by telescoping.

Condition (5) is an exact **relative** cochain condition, corresponding to a zero class after identifying the terminal boundary. Under arbitrary undirected walks between fixed endpoints it is also necessary for path-difference invariance, with reachable graph components and support conditions. For restricted directed feasible paths it remains a sufficient test, not a universal necessary condition.

**Cycle arbitrage:** a permitted repeatable directed cycle with positive proxy reward and nonpositive true reward earns arbitrarily high proxy return across additional laps without improving true return. A nonzero circulation of omega is a *potential* warning; the sign and each reward's actual return decide whether a profitable exploit exists.

**Acyclic terminal exploit:** the graph with just two edges s->good and s->bad has no cycles. Give true rewards (2,0), proxy rewards (2,3). The proxy chooses the bad terminal although gold chooses good. Here omega is a graph coboundary but the terminal potentials differ, so a cycle-only audit would miss the hack. This is the counterexample requiring a **relative boundary** in the invariant.

The source and tests cover this, a repeatable proxy-only loop, and safe fixed-terminal shaping. For discounted MDPs, the compatible potential-based shaping term is gamma*psi(next)-psi(current) with its appropriate terminal and tail conditions, rather than the ordinary graph differential used here. Policy invariance under potential shaping is classical (Ng, Harada and Russell, 1999).

## 6. One research direction: topology-aware reward-hacking certificates

The proposed experimental workflow has two separately sealed channels:

1. A learner sees only the registered Feedback_(s,q) channel and optimizes a proxy P, with a strict ledger of source sets, query counts, repeated selection and any evaluator-writable artifacts.
2. An independent auditor freezes the gold utility definition or a reward uncertainty family before the adaptive optimization. It calculates feedback fibres, cycle reward periods and the minimum target-specific extra audits; the audits themselves remain unavailable to the learner during candidate search.

On a game-space instance, the auditor should report (a) the observed proxy improvement, (b) true regret on a held-out gold source, (c) the cycle-pairing/within-feedback width, (d) cross-feedback misranking, (e) independent audit access cost, and (f) whether the actor tampered with tests, judges, tools or logs.

Promising extensions include a higher-dimensional obstruction for three or more category maps (the existing Leak Topology note warns that rational fibres can lack unit-capacity integer witnesses), an adaptive audit-selection minimax theorem, and a causal target-validation procedure for learned reward models. A claimed **solution to reward hacking** needs a licensed gold target and measured external performance, plus a generalization theorem or robust bound for the actual optimizer. This finite topological construction supplies a clear family of testable obstructions and selective certificates.

## 7. Executable evidence

- [Topology module](../src/spiral_ln/evaluation_reward_hacking_topology.py): periods, exact potential, alias witness, finite width/circulation oracles, targeted audit, exact reconstruction, reachable-set regret, UGC satisfaction-image enumeration.
- [Path module](../src/spiral_ln/evaluation_reward_path_gauge.py): terminal-relative shaping certificate, path returns, ranking reversal and loop-arbitrage witness.
- [Topology tests](../tests/test_evaluation_reward_hacking_topology.py), [path tests](../tests/test_evaluation_reward_path_gauge.py), [source-fingerprinted receipt verifier](../scripts/verify_reward_hacking_topology.py).
- Run: `PYTHONPATH=src python -m pytest -q tests/test_evaluation_reward_hacking_topology.py tests/test_evaluation_reward_path_gauge.py`; `PYTHONPATH=src python scripts/verify_reward_hacking_topology.py`.
- A six-minute CPU-only GitHub Actions workflow checks the package; the full repository CI runs separately.

No model calls, training, or claims about observed human reward were made. This research packet is independent of the unmerged UGCS-03 PR, using the cohomology/translation-game functions already on EvalMath's main branch.

## Primary prior art and boundaries

- [Ng, Harada, Russell, *Policy invariance under reward transformations* (1999)](https://people.eecs.berkeley.edu/~pabbeel/cs287-fa09/readings/NgHaradaRussell-shaping-ICML1999.pdf), potential shaping and looping exploits.
- [Anthropic, *From shortcuts to sabotage* (2025)](https://www.anthropic.com/research/emergent-misalignment-reward-hacking), observed reward hacking with downstream misaligned behaviors.
- [Hu et al., *Reducing Reward Hacking by Localizing Bad Behavior Instead of Penalizing It* (2026)](https://alignment.anthropic.com/2026/graft/), training containment rather than reward penalties.
- [Song et al., *Causal Reward Adjustment* (AAAI 2026)](https://ojs.aaai.org/index.php/AAAI/article/view/40584), a causal adjustment method for process-reward models.
- [Wang and Huang, *Reward Hacking as Equilibrium under Finite Evaluation* (2026)](https://arxiv.org/abs/2603.28063), structural/economic finite-evaluation viewpoint.
- [OpenAI, *The Unique Games Theorem* manuscript (September 2026)](https://github.com/openai/math/tree/main/preprints/The-Unique-Games-Theorem-September-23-2026), used only as an external claimed complexity direction, subject to independent proof review. The cochain identities in this note are elementary and unconditional.



## 8. A conditional mitigation: minimum private epsilon-audits and robust proxy selection (RHT-03)

The obstruction theorems suggest two interventions that are individually certifiable in finite game space. Both require the **gold reward** or a licensed set of plausible gold rewards to be frozen and independently justified before proxy optimization. They provide mathematical guarantees *conditional on that premise*.

### Protected approximate audit frontier

Suppose an auditor, without disclosing its data to the learner, can read cell counts x_S in addition to the public category margins y=Mx. Define

    W_S(t) = max {|U_t(x)-U_t(x')|:
                 Mx=Mx', x_S=x'_S, 0<=x,x'<=s integral}.

For a tolerable gold uncertainty epsilon>=0 define

    k_epsilon(t) = min {|S|: W_S(t)<=epsilon}.             (6)

This is an exact finite optimization over a declared audit grammar and cell capacities. It is monotone in the tolerance, and the zero-tolerance case is the cosystolic support theorem:

    k_0(t)=k_gold(t)=min_psi |supp(t-dpsi)|.               (7)

The module computes each W_S by exact feedback-fibre enumeration and searches subsets of cell counts by increasing cardinality. The implementation is a **bounded exponential oracle**; it is a correctness target for later integer-flow, submodular or combinatorial optimization methods. A data-dependent audit chosen after viewing protected gold outcomes must itself be registered as an adaptive selection with its own holdout.

### Uncertainty-aware guard against proxy selection

For a frozen, explicitly reachable finite roster X and a set T of plausible independently audited gold weights, compute

    Reg_t(x) = max_(x' in X) U_t(x') - U_t(x),
    Reg_robust(x) = max_(t in T) Reg_t(x),
    Floor(x) = min_(t in T) U_t(x).

For a registered regret budget epsilon and a nonzero true-progress floor u0, the guard may release an x only if

    Reg_robust(x)<=epsilon  and  Floor(x)>=u0.           (8)

Among admissible candidates it can still maximize the actor's original proxy p(Mx). This gives an exact implication: **if the actual gold cochain belongs to T and the roster and audit are correctly bound**, the selected candidate has true regret at most epsilon and true utility at least u0. If the set of admissible candidates is empty, the guard returns a failed certification rather than declaring an inert policy to be an alignment success.

This extends the ASMP-8 reachable-policy/regret object with an explicit topological signal audit. It is conservative robust optimization under a specified uncertainty set, not a learning algorithm that discovers true human values.

### Positive and negative finite controls

For the frustrated four-edge F2 translation game in §4, the unguarded worst-case proxy maximizer has gold regret 1. The protected oracle registers T={(1,0,0,0)}, epsilon=0 and u0=1. The guard finds a candidate with reported score 3, gold value 1 and regret 0. Thus an independently justified anchor can eliminate the modeled hacking route while preserving the maximum proxy score.

With T containing the four unit vectors e_0,e_1,e_2,e_3, epsilon=0 and u0=1, the game cannot simultaneously satisfy all four shifted constraints; the gate explicitly refuses certification. In this example the failure is a **specification feasibility problem** and should trigger human review of the competing gold criteria.

The same guard restricted to T={e_0} can select a controller for which the unregistered alternative gold criterion e_1 is violated. This is the mandatory misspecification negative control: the claimed guarantee is meaningful only under a justified, externally validated T.

The existing RHT-01 duality locates which gold variation is hidden within a feedback class; the new robust guard addresses **cross-feedback** misranking as well. These are complementary diagnostics and safety conditions rather than a universal cure.

- [Exact guard module](../src/spiral_ln/evaluation_reward_hacking_guard.py)
- [Independent finite tests](../tests/test_evaluation_reward_hacking_guard.py)
- The focused RHT-01 CI workflow checks all test modules and regenerates the source-hashed receipt, including the positive and misspecification controls.

### Broader experimental program

A research gym could instantiate evaluation worlds with synthetic protected gold criteria, proxy judges available to the training loop, controlled readout access classes and an independent held-out gold evaluator. For each frozen world measure the period vector <t,z_C>, the audit budget k_epsilon, the actual within-fibre reachable differences, the cross-fibre regret, proxy selection pressure, and whether a restricted policy learner discovers a damaging transition. Use an independent audit set or randomized holdout to prevent the learner from fitting a disclosed certificate.

A real-world validation would require a declared human preference target, independently acquired gold labels, inter-rater uncertainty, verified evaluator-data isolation, and measured held-out policy impacts. Without these, mathematical identifiability results describe exactly what signals can hide, while the quality of the intended objective remains an open empirical and normative problem.


## 9. Strict proxy hacking on a simple bipartite translation game (RHT-04)

The first RHT-01 four-cycle has some proxy-maximizing assignments that retain the protected gold score; adversarial tie-breaking selects a bad representative. A more discriminating witness has a **strict proxy-vs-gold ranking reversal over all globally proxy-maximizing policies**.

Take a simple bipartite constraint graph G=K2,4 with endpoints u,v in one colour class and intermediate vertices w0,w1,w2,w3 in the other. There are two constraints along each length-two u-wj-v path, with alphabet K=F2. Fix translations so path zero demands x_u=x_v, while paths one, two and three demand x_u!=x_v. This is achieved using shift pairs (0,0) for the first path and (0,1) for the others. The evaluation disclosure graph I is the **same K2,4 underlying graph** with one unit-capacity item per constraint, organized by its endpoint category and intermediate-vertex category.

The actor's proxy rewards *every satisfied constraint* equally, so its score is the total published row margins. An independent gold utility counts only the two constraint satisfactions on path zero:

    proxy(x)=sum_(e in E) x_e,
    gold(x)=x_(u,w0)+x_(v,w0).

For every environment labeling, choose each intermediate vertex label optimally given u and v:

| Endpoint relation | Maximum proxy | Maximum gold |
|---|---:|---:|
| x_u=x_v | 5/8 constraints | 2/2 gold constraints |
| x_u!=x_v | 7/8 constraints | 1/2 gold constraints |

The constraint system cannot satisfy all four path requirements simultaneously. **Every** globally proxy-maximizing assignment must use x_u!=x_v and has gold utility 1, while a gold-optimal assignment uses x_u=x_v and has proxy total at most 5. The strict proxy preference causes true regret exactly 1 on the frozen roster of all 64 assignments. A signed/nonnegative gold metric suffices; neither a harmful negative reward nor an adversarial tie-breaker is needed.

Crucially, the gold weight vector on I is

    t=(1,0,0,0,1,0,0,0).

It is the indicator of the entire first intermediate-vertex **category margin**. The cell graph uses canonical row-major order (u,w0)..(u,w3),(v,w0)..(v,w3); the constraint records are remapped through their original item identifiers. Therefore t=M^T lambda, the gold cohomology class is **zero** and every gold cycle period vanishes. Its hidden-gold fibre width and minimum targeted extra audit cost both equal zero. The actor's feedback already contains enough information to reconstruct gold: its selection rule optimizes the *wrong observable functional*.

This provides a rigorous counterexample to the proposed rule "eliminate every observable reward holonomy and reward hacking disappears." A complete audit must separately check

    R_hidden (within-fibre ambiguity), and
    R_cross (cross-fibre proxy misranking).

For this instance the exact regret decomposition is (R_cross,R_hidden)=(1,0). In the original flat four-cycle two-candidate alias example it is (0,2). Together these demonstrate the need for both the cohomology certificate and a decision-alignment condition under the registered policy roster.

When independently licensed gold weights t are registered, the RHT-03 robust guard with regret budget zero and gold floor 2 selects a policy with gold 2 and proxy score 5. The difference of two proxy points is the **cost of preserving true alignment** in this synthetic game.

- [Executable K2,4 fixture](../src/spiral_ln/evaluation_reward_ugc_fixture.py)
- [Independent 64-world exhaustive census](../tests/test_evaluation_reward_ugc_fixture.py)
- [Source-fingerprinted verification receipt](../scripts/verify_reward_hacking_topology.py)

The graph is a valid simple bipartite finite translation Unique Game in the sense of the UGC-PT-01 cochain dictionary. This finite construction uses neither the claimed 2026 hardness reduction nor any assertion about the general UGC conjecture. Its source of reward hacking is ordinary proxy misspecification, situated precisely within EvalMath's design and feedback notation.


## 10. Exact bounded-circulation solver for larger signal spaces (RHT-05)

The alias-width identity in §2 gives a constructive route beyond exhaustive enumeration. Let (D) denote the signed vertex-edge incidence of the bipartite evaluation-intersection graph, with capacities (s_e) and an independently defined rational gold cochain (t_e):

[
 W(t,M,s)=\max\{\langle t,z\rangle:\ Dz=0,\ -s_e\le z_e\le s_e,\ z_e\in\mathbb Z\}.
]

Build a minimum-cost circulation network with one forward arc (u\to v) of capacity (s_e), cost (-t_e), and one reverse arc (v\to u) of the same capacity and cost (+t_e) for each cell e. An integer flow (f_e^+,f_e^-) gives (z_e=f_e^+-f_e^-). Conservation at all vertices is precisely (Dz=0); the difference of two nonnegative flows cannot exceed (s_e) on an edge in either direction, and every allowable integer circulation (z) is represented by (f_e^+=\max(z_e,0)), (f_e^-=\max(-z_e,0)). Minimizing cost is therefore equivalent to maximizing the hidden gold width.

Starting at zero flow, cancel a negative residual cycle of integral bottleneck capacity on each iteration. Every augmentation improves the rational objective strictly and keeps the flow integral. When no negative residual cycle remains, standard min-cost circulation optimality certifies global optimality. This implementation uses a zero-source Bellman-Ford search and exact rational costs. Its explicit augmentation cap is an execution safeguard. Polynomial-time min-cost circulation methods exist in the literature; the current implementation is a bounded exact reference solver and carries no strongly-polynomial runtime claim.

A protected audit set S removes the forward/reverse original arcs for each audited cell, thereby enforcing (z_e=0) at those cells. The same network computes the **maximum gold ambiguity remaining after a chosen private audit** without enumerating all item records.

Finite adversarial checks compare the solver to two independently coded exponential oracles, one over feedback fibres and one over integer circulations, for all 81 ternary gold-weight assignments on multiple four-cell capacity profiles, plus rational weights and six-cell, two-cycle graphs. A 36-cell (K_{6,6}) evaluation graph with nonuniform capacities supplies a larger exact-circulation receipt with graph cycle rank 25; exhaustive enumeration of the full record box exceeds the oracle's declared budget.

- [Exact flow algorithm](../src/spiral_ln/evaluation_reward_hacking_flow.py)
- [Independent flow and private-audit tests](../tests/test_evaluation_reward_hacking_flow.py)
- [Source-bound verifier](../scripts/verify_reward_hacking_topology.py)

### Meaning for Goodhart containment

The inexpensive mathematical diagnostic now scales to much larger *known* evaluation-category graphs than the original enumerable world oracle. It finds the **maximum damage a reward cochain can conceal within the published feedback fibres**, and exactly which private cell counts remove that ambiguity. The separate cross-fibre misranking remains a reachable-policy/true-objective problem. The simple-bipartite RHT-04 example has identically zero hidden-fibre width and positive strict proxy regret, so increasing evaluator observability alone cannot eliminate its proxy-hacking route.

A candidate generalization is the **joint audit-and-selection frontier**: for a frozen class of bounded-compute policies, a sealed gold uncertainty set and a priced additional audit family, find the smallest private signal collection and a decision rule guaranteeing (epsilon)-regret and nonzero true progress under repeated feedback. This is a constrained robust optimization and evaluation-design question; it requires independent gold validation and disclosure accounting to become an empirical AI-safety result.


## 11. Three-map signals: bounded integer fibres and reachable reward hacking (RHT-06)

The two-map theorems in §§1–3 exploit a special property: bipartite incidence matrices are totally unimodular and their cycle kernel has a generating set of alternating unit vectors. For three or more category maps the observation matrix M_Δ can have rational null vectors whose primitive integer coefficients exceed the actual cell capacities. [EvalMath Leak Topology, Proposition 10](leak_topology.md#3-three-or-more-maps) already provides a five-cell example. The reward-hacking application needs a capacity-aware version of the alias theorem.

### Exact theorem: the bounded integer feedback kernel

Freeze a support P of nonempty k-way cells, observed margin faces Δ, a positive integer capacity vector s∈ℕ^P, and an externally licensed rational gold cochain t∈ℚ^P. The observation y=M_Δ x is the vector of released margins, with feasible cell records

    X_s = {x∈ℤ^P : 0≤x_e≤s_e}.

Define the bounded integral feedback kernel

    B_s(Δ) = {z∈ℤ^P : M_Δ z=0, |z_e|≤s_e for every e}.       (RHT-06/1)

**Exact finite theorem.** The set of all differences x−x' of feasible records with identical published feedback equals B_s(Δ):

    {x−x' : x,x'∈X_s, M_Δx=M_Δx'} = B_s(Δ).                (RHT-06/2)

The forward inclusion follows from integrality and the capacity inequalities. For the converse, take any z∈B_s and define x=z_+, x'=z_- componentwise. Both lie in the box and their released feedback agrees because M_Δz=0. Thus the result is independent of any total-unimodularity assumption.

Consequently the maximum hidden gold ambiguity across all public feedback fibres satisfies

    W_s(t) = max_{z∈B_s(Δ)} <t,z>.                          (RHT-06/3)

The gold utility is identifiable on the full feasible box exactly when t annihilates **every bounded integer difference**. The corresponding *realized difference rank* is

    r_s(Δ) = dim_Q span_Q B_s(Δ)
           ≤ dim_Q ker_Q M_Δ.                              (RHT-06/4)

The inequality can be strict. In particular the nonzero rational cohomology class [t] in ℚ^P/im(M_Δ^T) need not produce a physically possible reward-hacking alias at the registered capacities. For Δ with only two separate category maps and all s_e≥1, the unit-cycle generators guarantee equality of these ranks, recovering RHT-01. A large enough capacity vector always activates a rational kernel direction, because every rational kernel vector can be rescaled to an integral vector with finite coordinate magnitudes.

### Concrete integrality activation at one extra item

Take three category maps observed **separately**, with sorted nonempty cell support

    P = {(000),(001),(011),(101),(110)}.

The 6×5 margin matrix has rank four, with primitive integer kernel vector

    z = (1,-2,1,1,-1).

Freeze gold t=(0,1,0,0,0), valuing the second cell alone. Its rational period is <t,z>=−2.

**At unit capacities** s=(1,1,1,1,1), the bounded kernel B_s contains only zero. All feasible records are distinguishable from their released margins, and the hidden gold width is exactly zero, despite nonzero rational kernel and gold period. The target-specific additional private-audit cost is zero.

**After increasing only the second cell to capacity two** s=(1,2,1,1,1), the bounded kernel contains {−z,0,z}. One explicit indistinguishable pair is

    x_high=(0,2,0,0,1),
    x_low =(1,0,1,1,0).

All three published category margins agree. Their gold values differ by exactly 2. The realized kernel rank rises from zero to one and the minimum additional protected cell audits rises from zero to one. The minimum **uniform** capacity that activates this specific gold alias is also two. These are exact integer statements checked against an independent enumeration of every pair of feasible count tables.

The example comes directly from the existing Leak Topology note's sparse 2×2×2 support. It is a capacity-aware interpretation of established algebraic-statistical fibre geometry, not an unprecedented topological phenomenon.

### Environment reachability forms a further quotient

The game controller may be able to generate only a strict subset X⊂X_s of the feasible record box. Define

    B_X = {x−x' : x,x'∈X, M_Δx=M_Δx'},                  (RHT-06/5)

and the reachable hidden-gold width W_X(t)=max_{z∈B_X}<t,z>. Then

    B_X ⊆ B_s ⊆ ker_Q(M_Δ),
    W_X(t) ≤ W_s(t).                                     (RHT-06/6)

This distinction matters for the Unique Games connection. Let a binary translation game have four constraints around a 4-cycle, and map each constraint's satisfaction bit to a unit-capacity cell in a separately observed K₂,₂ category-intersection graph. The full box has an alias between records 1001 and 0110 for protected gold t=(1,0,0,1), with W_s=2.

For a **frustrated** four-cycle the satisfaction record has odd parity. The two records above have even parity, hence are both unreachable. In fact all eight reachable records under this game are in distinct public margin fibres: W_X=0 and the reachable difference rank is zero. For the **flat** four-cycle all eight reachable satisfaction records have even parity, the pair 1001 and 0110 is available, and W_X=2. This is a direct, exact test of two different coefficients spaces: F₂ translation-game holonomy restricts the reachable satisfaction patterns, while the gold reward is a ℚ-linear functional on evaluation margin cells.

### Audit formula and ASMP-8 interpretation

A privileged auditor revealing exact counts for S⊆P leaves the constrained bounded kernel

    B_s(S)={z∈B_s:z_e=0 for each e∈S}.

For tolerance ε≥0 the target-specific private audit burden is exactly

    k_{s,ε}(t)=min{|S|:max_{z∈B_s(S)}<t,z>≤ε}.         (RHT-06/7)

The unit-capacity five-cell example gives k_{s,0}=0 despite a nonzero rational [t]. At capacity two, k_{s,0}=1. The actor-reachable version replaces B_s by B_X. The registered extra audit channel must remain sealed from the proxy optimizer while the learner is selected.

This creates an explicit **three-layer reward-hacking check** under the frozen ASMP-8 reachable-policy formulation:

1. The rational signal geometry identifies possible linear blind directions.
2. The bounded integer kernel determines which differences can occur within physical/evaluation cell capacities.
3. The actor's actual reachable set determines which invisible differences can be produced by the current controller and policy class.

A fourth, independent decision check still tests whether maximizing the visible proxy misranks the gold utility **across** feedback classes, as established by RHT-04. The three-map unit-capacity example supplies a strict cross-feedback proxy misranking even though its integer feedback fibres are singletons.

### Reproducibility and prior art

- [Higher-order signal module](../src/spiral_ln/evaluation_reward_hacking_multimap.py) uses EvalMath's existing k-map margin matrix and exact rational nullspace machinery, with a separate capped integer-difference oracle.
- [Independent finite tests](../tests/test_evaluation_reward_hacking_multimap.py) compare the five-cell generator with all feasible record pairs, verify the capacity-two activation, recover the two-map baseline, test the full 2×2×2 pairwise-observation homological class, and contrast flat/frustrated UGC reachable fibres.
- The exact source-bound RHT receipt and six-minute focused CI retain separate claim scopes for finite enumeration, algebraic identities and UGC manuscript dependence.

Markov bases and Graver bases for multiway contingency tables offer established tools for accelerating general bounded integer-fibre enumeration. They may reveal a tractable regime for the protected-audit problem under specific marginal grammars; the present bounded kernel algorithm is exponential. Relevant primary foundations include Diaconis and Sturmfels, [Algebraic Algorithms for Sampling from Conditional Distributions](https://www.jstor.org/stable/120181), *Annals of Statistics* 26 (1998), and Sullivant, [Algebraic Statistics](https://math.berkeley.edu/~bernd/owl.pdf) (Markov-basis treatment). The potential *research novelty* lies in jointly pricing sealed adaptive audits, a policy-reachable outcome grammar, and an independently validated gold signal under repeated proxy optimization.


## 12. Witness-driven optimal private audits for multiway signals (RHT-07)

**2026-11-10 | exact finite theorem and new CPU solver.** The preceding RHT-06 brute-force oracle enumerates `prod_e(2s_e+1)` possible integer feedback differences, which becomes expensive for richer evaluations. RHT-07 rephrases target-specific private auditing as **weighted hitting set with an exact reward-width separation oracle**. The result applies equally to the complete cell-capacity box and to a frozen actor-reachable roster, using different oracles with a common certificate.

### Exact obstruction-hitting theorem

Fix an observation design `M_Δ`, integer capacities `s`, a rational protected gold cochain `t`, a permitted discrepancy `ε≥0`, and positive private audit costs `c_e`. Let `B` be either the full feasible integer-kernel set `B_s={z∈Z^P:M_Δz=0, |z_e|≤s_e}` or the smaller reachable difference set `B_X={x−x':x,x'∈X,M_Δx=M_Δx'}` for a frozen actor roster `X`. Define dangerous witnesses and their supports by

\[
\mathcal D_\varepsilon(B,t)=\{\operatorname{supp}(z): z\in B,\ \langle t,z\rangle>\varepsilon\}.
\]

An audit set `S` privately reveals exact cell counts at the cells it contains. It removes the discrepancy represented by `z` precisely when `S∩supp(z)≠∅`. Therefore the exact minimum-cost audit is

\[
\boxed{\min_{S\subseteq P}\sum_{e\in S}c_e\quad\text{s.t.}\quad S\cap W\ne\varnothing\quad\forall W\in\mathcal D_\varepsilon(B,t).}
\]

**Proof:** equal public feedback and equal audited counts are equivalent to `Mz=0` and `z_e=0` for all `e∈S`. A dangerous witness survives exactly when its support avoids `S`. Hence the stated minimum hitting set is necessary and sufficient for the worst hidden gold discrepancy after auditing to be at most `ε`. The same equivalence holds when `B` is restricted to the actor's actual frozen roster. This is a direct finite reduction to an established combinatorial optimization problem, rather than a novel general complexity theorem.

### Cutting-plane/separation method

The new [RHT-07 solver](../src/spiral_ln/evaluation_reward_hacking_audit_optimizer.py) starts from no private audits. It alternates:

1. **Separation:** exactly maximize `t·z` over hidden differences that vanish on current audit cells `S`. If the optimum is at most `ε`, the audit meets the target for every possible hidden record pair in the registered domain.
2. **Witness:** otherwise register the dangerous integer difference and its nonzero support. Every valid audit must include at least one cell from that support.
3. **Optimization:** solve the minimum-weight hitting set over *all registered dangerous supports*, then repeat separation.

This is a lazy constraint-generation scheme. At the first iteration where separation finds no violation, the candidate audit is globally optimal: the accumulated supports give a lower bound on every feasible solution's cost, and the exact separation check gives a matching feasible upper bound. The result includes the chosen audit, rational total cost, remaining gold width, witness supports, number of iterations, and exact-oracle state counts. Any exceeded memory/state/iteration budget **raises an error**, preserving the distinction between a verified optimum and an incomplete search.

### An exact integer-margin DP separation oracle

When the rational feedback nullspace dimension is at least two, an exact dynamic program processes each cell in order. Its state is the vector of partial published margins, and it tests all integer hidden differences in that cell's allowed interval. Audited cells allow only the difference zero. The Bellman recurrence is

\[
V(i,m)=\max_{z_i\in[-s_i,s_i]\cap\mathbb Z}\bigl(t_i z_i+V(i+1,m+M_{\cdot i}z_i)\bigr),
\]

with terminal value zero at zero residual margin and negative infinity elsewhere. A suffix-capacity bound prunes states whose partial margins cannot be cancelled by the remaining cells. This *memoized, state-capped pseudopolynomial* method can be far smaller than the full box enumeration on modest-margin instances. It makes no general polynomial-time claim for arbitrary high-dimensional binary-encoded capacities; the number of reachable margin states can still grow exponentially.

There is also a **closed rank-one case**. If the rational kernel has dimension one and primitive integer generator `g`, every feasible integer difference equals `ag` with `|a|≤b=min_{g_i≠0} floor(s_i/|g_i|)`. Consequently

\[
W_s(t)=b\,|\langle t,g\rangle|.
\]

Auditing any cell with nonzero `g_i` forces `a=0`. Thus the minimum zero-tolerance audit is either zero cells or the cheapest one cell in the generator's support. This correctly handles the RHT-06 five-cell capacity activation: generator `(1,-2,1,1,-1)`, gold `(0,1,0,0,0)`, first cell-capacity profile `(1,1,1,1,1)` yielding width zero, and second profile `(1,2,1,1,1)` yielding width two and a one-cell audit.

### Higher-rank finite witness with a larger combinatorial search space

Take all 12 joint cells of a `2×2×3` category system, revealing all **pairwise category margins**, with capacity three in every cell. The rational feedback nullity equals two. Every hidden integer difference has three checkerboard slices with coefficients `a,b,-a-b`, where `|a|,|b|,|a+b|≤3`. Set protected gold weight `2` at cell `(0,0,0)`, weight `1` at cell `(0,0,1)`, and zero elsewhere. The worst hidden gold difference is exactly

\[
\max_{|a|,|b|,|a+b|\le3}(2a+b)=6.
\]

A **zero-tolerance private audit requires exactly two cells**. With tolerance three, one carefully chosen cell suffices. The registered dynamic program and lazy hitting-set oracle agree with the explicit two-coordinate analytical bound. Straight enumeration of all candidate bounded difference vectors would inspect `7^{12}=13,841,287,201` vectors, beyond the reference brute-force budget.

As a separate reachable-roster control, the flat binary UGC four-cycle admits a hidden-reward alias requiring one private cell audit; the frustrated UGC cycle disallows the alias and requires zero. The optimization is therefore conditioned on the actual controller/game reachability grammar, not merely the ambient topology.

### Mathematical and operational boundaries

The object audited here is an **independently defined gold-reward functional**. These methods can certify its variation inside specified public-feedback fibres and a frozen reachable policy set. They do not rule out cross-fibre proxy misranking, reward-model misspecification, active judge tampering, or evaluation set leakage. RHT-04 and the RHT-03 robust selection guard address separate portions of those problems under their own declared premises.

Weighted hitting sets, finite integer margin DP, and contingency-table fibre moves belong to established combinatorial optimization and algebraic-statistics literature. See [Dobra, Dynamic Markov Bases](https://doi.org/10.1080/10618600.2012.663285) for multiway bounded-table connectivity, and [Briański et al., Graver-basis structural parameters](https://pmc.ncbi.nlm.nih.gov/articles/PMC11480161/) for integer-programming complexity regimes. An [OpenAI September 2026 manuscript](https://github.com/openai/math/blob/main/preprints/An-FPRAS-for-Cell-Bounded-Contingency-Tables-September-24-2026/build/sections/introduction.tex) claims approximate counting for two-way bounded tables; its counting target differs from this exact multiway max-gold audit problem and remains subject to independent proof scrutiny.

- [Integer-margin DP and lazy weighted audit optimizer](../src/spiral_ln/evaluation_reward_hacking_audit_optimizer.py)
- [Independent finite audit tests](../tests/test_evaluation_reward_hacking_audit_optimizer.py)
- [Reproducible source-bound report](../scripts/verify_reward_hacking_topology.py)


## 13. Adaptive feedback may increase reward-hacking opportunity (RHT-08)

**2026-11-10 | exact finite feedback-filtration theorem and UGC world generator.** The RHT-07 optimizer treats private audits as extra information held by a trusted evaluator. Once a query or an evaluator's ensuing action becomes visible to the controller, its transcript becomes part of the controller's choice information. This section separates the *sealed-auditor* and *actor-visible* observation filtrations, reusing the exact post-feedback selection-risk calculus already in [selection_risk_continuations.md](selection_risk_continuations.md) and the adaptive query grammar from [adaptive_disclosure.md](adaptive_disclosure.md).

### The registered world, policy, and target

Freeze a finite set Ω of **latent gold-reference worlds** with positive integer weights w_ω. Every world is an evaluation count table with the same initially public category margins M_Δx_ω. Freeze a roster of candidate controller outcomes A, each represented by an integral count table within the registered capacity box. The proxy used to select a controller is P(a)=p(M_Δx_a), with the same public scoring function for every world. Each world also has an **independently licensed, protected** rational gold cochain t_ω. Define

    U_ω(a)=<t_ω,x_a>,
    U_ω*=max_(b∈A) U_ω(b),
    E_a(ω)=1[U_ω*-U_ω(a) >= δ],

for a declared positive regret threshold δ. Only proxy-maximizing actions `a∈argmax_A P` may be selected by the actor. The risk objective is the probability of an unsafe regret event, with an adversarial tie-breaker among those proxy-maximizing actions.

A query q is a registered 0/1 subset-sum row on the hidden reference-world cell table, returning q·x_ω. Query IDs, their answers, and the agent/auditor visibility rights are distinct parts of the protocol. All prior worlds share one baseline feedback fibre, so a query transcript is the only added information in this experiment.

### Exact theorem: post-feedback reward-hacking risk

A public deterministic query tree T induces a partition of Ω into its complete actor-visible transcript fibres `F_τ`. The actor can choose an eligible proxy-maximizing action after observing τ. The worst expected unsafe-regret risk is exactly

\[
\boxed{
\mathcal R(T)=
\frac{1}{\sum_{\omega}w_\omega}
\sum_{\tau}
\max_{a\in\arg\max P}
\sum_{\omega\in F_\tau} w_\omega E_a(\omega).
}
\]

**Proof:** condition on each visible transcript. A chosen action contributes the total weighted mass of worlds in that fibre on which its true regret crosses δ. Maximizing independently on every fibre yields the formula; deterministic choices attain the maximum. Refining the transcript partition cannot decrease this value, since the actor can ignore additional observations. For an adaptive query bank, a Bellman recursion maximizes the total terminal mass over the response partitions generated by each available query. This is a typed **instance** of the previously proved finite selection-risk theorem, now with real evaluation category margins, actor proxy constraints, and independently specified gold loss. It is not a new general Blackwell theorem.

### A seven-world UGC construction with a strict adaptive gap

Use the **simple bipartite graph K₂,₇** as both a translation-game constraint graph and the evaluation category-intersection graph. The environment has nine vertices and fourteen oriented edge constraints, all with shift zero in F₂. Constrain the declared actor/world roster to the following seven actual reachable satisfaction records: fix the two degree-seven endpoint labels to 0 and 1, and assign the intermediate vertex labels so that precisely one row-zero edge is satisfied, with the remaining six row-one edges satisfied. World i has the row-zero success at column i. Each world comes from a literal F₂ constraint assignment and the bank contains every **contiguous interval query** on row-zero satisfaction cells.

Every world and candidate has precisely the same initial public margins:

    row margins=(1,6), column margins=(1,1,1,1,1,1,1),
    P(candidate)=7.

Freeze an independent world-indexed protected gold cochain `t_i`: it assigns weight 1 to row-zero cells at columns j≠i and zero to every other cell. For candidate action a, exactly

    U_i(a)=1 if a!=i, else 0.

Thus every candidate is proxy-optimal and each is unsafe in exactly one hidden world at threshold δ=1. Under the uniform seven-world prior, for any transcript partition with L nonempty fibres the adversarial actor can select the dangerous action for one world in each fibre, so

\[
\boxed{\mathcal R(T)=L/7.}
\]

The original EvalMath one-hot interval law states that at most k adaptive interval queries identify `min(7,2^k)` worlds, whereas k *fixed* interval queries distinguish at most `min(7,2k)` worlds for k>0. The actor-hacking risk therefore gives a strict budget-three comparison:

| Additional publicly disclosed interval queries | Maximum malicious selection risk |
|---:|---:|
| 0 | 1/7 |
| 1 | 2/7 |
| 2, adaptive | 4/7 |
| 3, fixed schedule | 6/7 |
| 3, adaptive | 7/7 |

The fixed and adaptive values are computed directly by the existing EvalMath `selection_risk.NullModel` exact algorithms. A **separately implemented adaptive-disclosure state-identification oracle** independently checks the 7/7 and 6/7 results, and an independent constraint-satisfaction oracle checks that each reference state is a realizable Unique Games outcome. This is a stylized adversarial-selection experiment; all seven actions are tied on the proxy and the actor intentionally chooses the unsafe tie-break. A legitimate actor with the same additional information could instead choose to avoid the dangerous outcome.

### Private audit and public disclosure have opposite strategic effects

A trusted auditor with access to query responses can choose a final action **after one sealed interval query**. Since both response groups are proper subsets of the seven-world roster, the auditor can select an action corresponding to a world *outside* the observed group, guaranteeing gold 1 in every possible reference world. Its unsafe-regret risk falls from 1/7 to zero. This audit protocol requires that both its query ID and response remain private, and that the protected auditor controls the terminal action.

The actor given one **public** interval answer gains the ability to select an unsafe action in each of the two response groups. The worst-case malicious risk rises from 1/7 to 2/7. The two procedures use the same frozen source, query bank, and gold. Their differences arise from who receives the information and who controls final selection.

### Query-ID leakage from an otherwise sealed adaptive audit

Even hiding query answers can be insufficient if subsequent publicly visible query identities depend on secret responses. Consider the three-world K₂,₃ instance with a sealed first query asking whether world 0 is present. A branching audit then chooses a *public* query:

- if the hidden answer is yes (world 0), publicly query whether world 1 is present;
- otherwise (world 1 or 2), publicly query whether world 0 is present.

Every public query answer equals zero. The **choice of public query ID itself** reveals which group the private answer placed the world in. The actor sees two visible transcript classes and its maximum unsafe selection risk rises from 1/3 to 2/3. The actor never sees the original sealed response. The exact finite oracle records public query IDs and replies together, and the test includes a direct independent reconstruction of the adversarial gold regret.

A sound **noninterference prerequisite** for a sealed audit in this declared protocol is that any later actor-visible query identity, answer, response timing, state change, or decision signal must be constant across worlds that the original public channel cannot distinguish, except where leakage has been explicitly licensed and charged. The present finite code records query identities and answers, while real timing/tool metadata require separate instrumentation. In the worst-case adversarial event model, a strict refinement of the actor-visible partition can create additional risk; for a specific fixed gold-event family it may have no effect.

### What this changes in the game-space research program

RHT-01–07 calculate whether gold can be hidden inside existing evaluation feedback and which **private** measurements remove the ambiguity. RHT-08 adds the dynamic information-flow condition

    private audit trace -> potential public continuation -> actor-visible filtration

and explicitly measures the resulting worst-case post-selection risk. The same cohomological fibre can support more reliable independent verification or greater malicious exploitation, depending on the licensed disclosure and final-action protocol. Protected audits must be governed by source lineage, response visibility, query-count ledgers, and action-dependent disclosure accounting from the established EvalMath feedback calculus.

This experiment assumes a finite fixed hidden world, deterministic subset-sum queries, a prior with exact positive masses, a frozen roster of proxy-maximizing actions, and independently specified world-dependent gold. The auditor can take one terminal action after its sealed query, without a subsequent malicious response. No actual model is trained or evaluated, and no statement that the gold cochains correspond to human values follows from the algebra.

- [Source model and mixed-visibility query runner](../src/spiral_ln/evaluation_reward_hacking_adaptive_feedback.py)
- [Independent UGC satisfaction and adaptive-disclosure tests](../tests/test_evaluation_reward_hacking_adaptive_feedback.py)
- [Selection risk under adaptive evaluation](selection_risk_continuations.md)
- [Adaptive disclosure oracle and one-hot interval law](adaptive_disclosure.md)

A next-stage mechanism should combine the private RHT-07 hitting-set optimizer with a **leakage-aware continuation policy**, charging both audit information gain and the maximum induced actor-visible regret risk under adaptive disclosure. That is a constrained two-player partially observed information game. Its general minimax solution and its relationship to actual learned reward hacking remain open.


## 14. Joint audit design: control leakage and preserve safe action throughput (RHT-09)

**2026-11-10 | exact finite theorem plus complete small-policy search.** This section joins the RHT-07 private-audit frontier to the RHT-08 actor-visible feedback-risk formula. A defender now controls the query policy and a terminal **authorize/veto** gate; an adversarial actor chooses among proxy-maximizing actions using whatever portion of the query transcript the protocol exposes. The mathematical objects are frozen finite UGC-generated worlds and independent gold rewards. The result concerns a **single terminal action attempt**, with the veto response observed only after that attempt. A protocol allowing retry or agent-state changes needs a different theorem.

### 14.1 Exact four-part certification contract

Use a finite hidden-reference-world set Ω with positive integer weights (w_omega), a query bank (Q) of deterministic cell subset-sums, and a frozen action roster (A). Let (A_P=argmax_{ain A}P(a)) consist of proxy-maximizing actions, with independent, world-specific protected gold utility (U_omega(a)). Define (mathrm{Bad}(omega,a)=1[max_{bin A}U_omega(b)-U_omega(a)gedelta]) for a registered (delta>0).

A query tree (pi) labels each query **sealed** or **public**. The auditor sees the full leaf transcript (S_pi(omega)), including all query IDs and answers. The actor sees (V_pi(omega)), consisting of the *ordered public query IDs and answers*. Any adaptation of public query identities based on sealed outcomes is thus represented as a possible leakage path. The auditor has a deterministic terminal veto rule (g(S_pi(omega),a)in{0,1}), evaluated after the actor attempts one (ain A_P).

Define the **authorized malicious loss** by

\[
\mathcal R(\pi,g)=
\frac{1}{W}\sum_{v}
\max_{a\in A_P}\sum_{\omega:V_\pi(\omega)=v}
w_\omega\,\mathrm{Bad}(\omega,a)\,g(S_\pi(\omega),a),\quad
W=\sum_\omega w_\omega.                                    \tag{RHT-09/1}
\]

Conditional on each visible transcript, the adversarial actor chooses the action maximizing its authorized unsafe mass. A deterministic action maximizer exists because the action set is finite. This is a direct application of the earlier selection-risk theorem with the auditor's terminal veto incorporated.

To prevent an always-deny solution, define **benign safe authorization**, measured by a separate actor that attempts an action uniformly from (A_P), conditional on that action being safe:

\[
L(\pi,g)=
\frac{\sum_\omega w_\omega\sum_{a\in A_P}
(1-\mathrm{Bad}(\omega,a))\,g(S_\pi(\omega),a)}
{\sum_\omega w_\omega\sum_{a\in A_P}(1-\mathrm{Bad}(\omega,a))}.
                                                                  \tag{RHT-09/2}
\]

The denominator must be positive. This is a *conditional coverage measure* under a frozen benign action distribution, with the same role that coverage plays in selective prediction. It is not the fraction of all malicious attempts authorized.

Let (\mathcal R_{\rm public}(\pi)) be (RHT-09/1) with (g\equiv1). It prices **pre-veto leakage** because exposing more to a hostile actor may increase its ability to select dangerous actions. Let (C(\pi)=W^{-1}\sum_\omega w_\omega\sum_{q\text{ on its path}}c(q,\text{visibility})) be the expected query cost, with positive registered charges. The finite certificate solves

\[
\begin{aligned}
\min_{\pi,g}\;&\mathcal R(\pi,g),\\
\text{s.t. }&
L(\pi,g)\ge L_0,\\
&\mathcal R_{\rm public}(\pi)\le\Lambda,\\
&C(\pi)\le C_0,\quad\mathrm{depth}(\pi)\le B.
\end{aligned}                                                    \tag{RHT-09/3}
\]

An optional strict authorization cap (\mathcal R\le\alpha) turns this into a *yes/no* certificate. If every admissible tree and veto assignment fails, the exact tiny solver returns **no certificate**. A configured tree/gate/state-enumeration cap is an execution limit and raises a separate error, rather than being reported as mathematical infeasibility.

### 14.2 Exact enumeration theorem for bounded policies

For a fixed query tree, the auditor's full transcript partitions Ω into leaves (F_1,\ldots,F_r), while the actor's public transcript gives a generally coarser partition. There are precisely (2^{r|A_P|}) deterministic possible veto assignments across private leaves and eligible actions. Directly evaluating (RHT-09/1) and (RHT-09/2) for every assignment solves the finite constrained terminal game exactly. Enumerating all informative adaptive query trees of depth at most B and their visibility labels then yields the exact optimum under (RHT-09/3). Query nodes with a single possible answer can be dropped from a *minimization* policy at positive cost, since they improve neither private discrimination nor benign coverage and any visible query-ID leakage can only weakly increase malicious selection risk. Such redundant public continuation probes remain representable for adversarial negative controls.

The implementation uses exact `Fraction` arithmetic and rejects attempts exceeding predeclared numbers of query trees or veto assignments. Its supported complete search is deliberately small (at most five worlds/actions, ten query types, three rounds); larger one-hot cases use a separate analytic Bellman reduction.

### 14.3 A three-world non-inert protection witness

Use RHT-08's (K_{2,3}) one-hot UGC satisfaction worlds with uniform prior and eligible actions (a_0,a_1,a_2). Each world (omega=i) has (\mathrm{Bad}(i,a_j)=1[i=j]). Every action is proxy-maximizing.

With zero queries, a guarantee of zero malicious harm requires denying all three actions. Hence zero-harm benign authorization equals zero. At benign safe-authorization floor (L_0=2/3), allowing two actions without measurement has authorized malicious risk (1/3).

Make one **sealed** query asking whether the hidden world is 0. If the answer is yes, allow actions (a_1,a_2); if no, allow only (a_0). Every authorized action is safe in its possible world, so

\[
\boxed{\mathcal R=0,\qquad L=2/3,\qquad
\mathcal R_{\rm public}=1/3,\qquad C=1.}             \tag{RHT-09/4}
\]

The actor receives no query ID/answer, and its maximum malicious risk after veto is zero. If the same query is made **public**, the pre-veto risk rises to (2/3), violating a leakage cap (Lambda=1/3) despite the possibility of an equally effective terminal veto. With a cost cap zero and a strict zero-harm ceiling, no policy meets (L_0=2/3). With **two sealed adaptive queries**, the auditor can identify the hidden world exactly and veto only its single bad action: (\mathcal R=0), (L=1), with expected query count (5/3).

The small joint optimizer was independently checked against an exhaustive enumerator of every single query choice, visibility label and possible veto assignment, including several distinct liveness, leakage, cost and harm ceilings.

### 14.4 One-hot zero-harm frontier equals a posterior collision functional

For the (n)-world (K_{2,n}) construction, fix a **sealed-only** query tree whose terminal private transcript classes have sizes (k_1,\ldots,k_r), with (sum_j k_j=n). Each world (i) has just one dangerous proxy-maximizing action (a_i). With no public observations, a positive approval for (a_i) in any private class containing (i) would give the attacker a strictly positive chance of authorized harm. Hence a zero-harm veto gate **must deny all actions indexed by a world in the same private leaf**, and may safely authorize every action indexed outside that leaf.

Each private leaf of size k contributes (k(n-k)) genuinely safe world-action pairs that can be authorized. Dividing by (n(n-1)), the total number of safe world-action pairs, proves the exact optimal zero-harm benign coverage identity

\[
\boxed{
L_{\rm zero}(\pi)=\frac{n^2-\sum_j k_j^2}{n(n-1)}
=\frac{n}{n-1}\left(1-
\underbrace{\sum_j(k_j/n)^2}_{P_{\rm collision}(\pi)}
\right).
}                                                             \tag{RHT-09/5}
\]

The right-hand probability is exactly the posterior *transcript collision statistic* already developed in EvalMath's adaptive-disclosure module. This is a precise algebraic bridge: privately acquired information lowers the collision statistic, thereby improving safe authorization under a strict zero-harm veto. Making the same information public increases the adversarial actor's post-selection capacity under the RHT-08 grammar.

Using the frozen interval subset-sum bank and a Bellman recursion over the remaining possible one-hot worlds yields the exact **maximum** (RHT-09/5) under a depth-B sealed query budget. The seven-world results are:

| Max sealed queries B | Optimal leaf sizes | Posterior collision | Max zero-harm safe-action authorization |
|---:|---|---:|---:|
| 0 | 7 | 1 | 0 |
| 1 | 4,3 | 25/49 | 4/7 |
| 2 | 2,2,2,1 | 13/49 | 6/7 |
| 3 | 1,1,1,1,1,1,1 | 1/7 | 1 |

A second, independent check reconstructs the tree using EvalMath's original `adaptive_disclosure.Node` class and verifies its collision statistic; a direct strategic evaluation checks both the zero malicious authorization risk and the achievable benign authorization rate.

### 14.5 Information-flow contract and limitation

The auditor here can inspect hidden gold-reference queries and **credibly enforce** a single final veto, while the actor chooses only from its registered proxy-maximizing roster. Any leak through visible query IDs/answers is represented in (V_\pi). To apply this scheme to a real model, external attestation must bind the actual measurement and authorization gate; the model's own reports are insufficient to establish the gold source or successful veto enforcement.

Repeated candidate attempts, actor adaptation to earlier veto decisions, observable audit timing, compromised tool or judge logs, learned reward misspecification and changing world states are outside this theorem. Adding those expands the information filtration and changes the underlying optimization game. Likewise a complete model safety claim requires independent evidence that the frozen gold cochains license the intended values.

**Prior art:** The optimization joins classical information design and Blackwell comparison with selective prediction under a reject option. See [Chow (1970), *On Optimum Recognition Error and Reject Tradeoff*](https://research.ibm.com/publications/on-optimum-recognition-error-and-reject-tradeoff), [Franc et al., *Optimal Strategies for Reject Option Classifiers* (JMLR)](https://jmlr.org/papers/volume24/21-0048/21-0048.pdf), and [Bergemann–Morris, *Information Design: A Unified Perspective*](https://cowles.yale.edu/sites/default/files/2022-08/d2075-r3.pdf). The finite UGC construction and collision identity are new **applications within this specific eval grammar**, while the general foundations are established.

- [Exact joint audit/veto optimizer](../src/spiral_ln/evaluation_reward_hacking_joint_audit.py)
- [Independent complete-search and collision tests](../tests/test_evaluation_reward_hacking_joint_audit.py)
- [Source-bound RHT research receipt](../scripts/verify_reward_hacking_topology.py)


## 15. Repeated attempts: imperfect gold audits become feedback (RHT-10)

**2026-11-10 | finite sequential risk theorem and exact retry-policy controls.** RHT-09 allowed a single candidate action followed by a terminal independently enforced veto. A persistent agent can instead attempt actions repeatedly, watch authorization/rejection outcomes, and use those observations to choose its next proposal. This changes the actor-visible feedback filtration even when protected gold measurements and query identities remain sealed.

### 15.1 Frozen verifier and attack grammar

Retain RHT-08/09's finite latent gold-reference world `ω∈Ω` with integer prior mass `w_ω`, fixed proxy-optimal action set `A_P`, and world-specific protected gold utility `U_ω`. The world stays fixed for the whole session. For every action `a∈A_P` define a harmful attempt when its true regret crosses the declared threshold `δ`:

\[
H_\omega(a)=\mathbf1[U_\omega^*-U_\omega(a)\ge\delta].
\]

The auditor observes the actual action and uses a noisy, externally calibrated gold-based veto. If `H_ω(a)=1`, it authorizes with probability `α` (false acceptance). If `H_ω(a)=0`, it authorizes with probability `1-β` (one minus false rejection). These rates are fixed and hold **conditional on the world, the proposed action, and the entire previous verdict history**. The special case of fresh independent audit errors realizes the model. The actor sees each approval/rejection bit, has a fixed maximum `B` attempts, and can choose its next eligible action as a function of those verdicts.

The event of interest is **at least one accepted harmful action**. It is absorbing for the risk calculation. After a rejected attempt or an approved safe action, the actor can continue, with optional enforceable restrictions: prohibition on repeating a previous action, lockout upon the first rejection, or termination after any approval. The last protocol represents a single-workflow authorization rule, while unrestricted continuation after a safe approval represents repeated opportunities across the session.

The actor's decision may depend on its own attempted actions and observed verdicts. It never sees the protected gold reference or the hidden world's identity. The fixed-world assumption is essential: replacing `ω` after every attempt gives a different learning and hazard process.

### 15.2 Exact unnormalized-posterior Bellman recursion (RHT-10/T1)

Let `m=(m_ω)_ω` be **unnormalized** probability mass of surviving reference worlds following a particular actor-visible verdict history, excluding trajectories that have already reached a harmful approval. Let `U` be the set of actions attempted and `r` the remaining horizon. For a proposed action `a`, put

\[
p_\omega(a)=\alpha H_\omega(a)+(1-\beta)(1-H_\omega(a)).
\]

The immediate accepted-harm mass is

\[
h_a(m)=\sum_\omega m_\omega\,\alpha H_\omega(a).
\]

An observed rejection passes unnormalized mass `m_ω(1-p_ω(a))` to its continuation; an observed approval on a **safe** action passes `m_ωp_ω(a)(1-H_ω(a))`. The Bellman recursion is

\[
\boxed{
V_r(m,U)=\max\Bigl\{0,\,
\max_{a\in A_P\text{ allowed by }U}
\bigl[h_a(m)+V_{r-1}(m^{\rm reject},U\cup\{a\})
+V_{r-1}(m^{\rm safe\ approve},U\cup\{a\})\bigr]\Bigr\}.
}
\tag{RHT-10/1}
\]

The appropriate continuation term is set to zero when a registered protocol terminates on that verdict. The boundary condition is `V_0=0`. With initial masses `m_ω=w_ω`, the exact optimal probability of any harmful authorization is `V_B(w,∅)/Σw_ω`.

**Proof:** condition on the first chosen action and its visible verdict. Accepted harmful actions contribute their immediate mass and need no further decision. The remaining outcomes are disjoint response branches. Conditioning on each branch gives a smaller instance with the displayed mass vector, so finite backwards induction yields optimality. Every deterministic policy induces one candidate at each observed history, and a randomized policy is a convex mixture of deterministic choices, so randomization cannot exceed the maximum.

A separate oracle enumerates fixed action schedules, evaluating each through the **per-world likelihood of actual verdicts**. Another independent brute-force enumerator searches every first action and every verdict-dependent second action, including early stop. The tests verify the dynamic-programming optimum against both controls and directly execute the returned policy over all worlds. Input and state-budget violations fail closed.

### 15.3 Strict adaptive retry advantage on UGC satisfaction worlds (RHT-10/T2)

Use RHT-08's three-world `K₂,₃` binary translation-game fixture. The three frozen proxy-maximizing actions have identical public evaluation margins. Each world has precisely one action with protected regret one, and this bad action has a different index in each world.

Freeze `α=1/5`, `β=0`. Every **safe** action is approved; a rejection therefore identifies the attempted action as unsafe. After attempting `a₀`, the actor can repeat it if rejected, while an approval leads it to try `a₁` next. In world zero the probability of harm across the two repeated attempts at `a₀` is `1-(4/5)^2=9/25`; in world one the probability of harm on the second attempt at `a₁` is `1/5`; in world two it is zero. Under the uniform prior,

\[
\boxed{
R^{\rm adaptive}_2=\tfrac13(\tfrac9{25}+\tfrac15)=\tfrac{14}{75},
\quad R^{\rm fixed}_2=\tfrac{2}{15},
\quad\Delta_2=\tfrac4{75}.
}
\tag{RHT-10/2}
\]

At horizon three the exact values are `R_adaptive=131/375` and `R_fixed=1/5`, a strict gain `56/375`. These are **cumulative harmful-authorization probabilities**, not one-step false-accept rates and not a statement about actual trained-agent behavior.

Prohibiting repeated actions or locking out the session after the first rejection reduces the two-attempt risk to `2/15` for this `β=0` fixture. Terminating after *any* approval makes it `3/25`. The different control costs become visible once false rejection is positive.

### 15.4 Conditional versus marginal false-accept guarantees (RHT-10/T3)

A general worst-case bound follows even without the stationary independent-verdict model. Suppose at attempted step `i`, **conditional on every preceding history with no harmful authorization**, the chance of authorizing a harmful action is bounded by `α_i`, no matter which action the actor adaptively selects. Then the probability of surviving that step without harm is at least `1-α_i`, so

\[
\boxed{
\Pr(\text{any harmful authorization by }B)
\le 1-\prod_{i=1}^{B}(1-\alpha_i).
}
\tag{RHT-10/3}
\]

The bound is tight for repeated attempts of an always-harmful action with fresh independent false acceptances at the registered rates. It handles within-attempt readout correlation and adaptive action selection **only when the hazard premise is valid conditionally on every actual transcript**.

If calibration instead bounds only `\Pr(\text{harmful authorization at attempt }i)\le\alpha_i` averaged over histories, the strongest general union bound is

\[
\boxed{
\Pr(\text{any harmful authorization})\le
\min(1,\sum_i\alpha_i).
}
\tag{RHT-10/4}
\]

A single latent variable can preselect which attempt, if any, receives a false authorization. Disjoint events with masses up to the `α_i` caps attain (RHT-10/4), while violating the stronger conditional hazard constraint after earlier denials. For `B=5` and `α_i=1/5`, (RHT-10/3) gives `2101/3125≈0.67232`, while (RHT-10/4) permits probability one. Exact constructed probability vectors in the tests establish both claims.

Calibration on isolated, nonadaptive audit calls provides insufficient evidence for a history-conditional bound in a live, adapting actor process. The verifier needs either a justified conditional soundness model or a conservative familywise budget.

### 15.5 Two-sided retry protocol frontier with throughput

A control that blocks every subsequent action can reduce malicious risk while preventing legitimate repeated work. To expose that operational cost, RHT-10 registers a separate *gold-known benign reference actor* which always submits actions independently verified safe, with as many distinct safe actions as its roster permits. Let `L_B` be its probability of at least one accepted safe action in `B` opportunities, and `T_B` its **expected count of accepted safe actions**. These are conditional reference benchmarks, distinct from actual benign-actor behavior under uncertain gold.

Under stationary safe approval probability `1-β`:

- unrestricted repeat opportunities give `L_B=1-β^B` and `T_B=B(1-β)`;
- no-repeat restriction reduces the available safe attempts to `\min(B,\#\text{safe actions})`;
- lockout after rejection gives `L_B=1-β` and `T_B=\sum_{i=1}^B(1-β)^i`;
- termination after any approval caps the expected safe authorizations at `1-β^B` when rejection does not itself trigger lockout.

These are exact finite benchmarks under independent per-attempt safe-verdict noise and protocol enforcement. The new [two-sided control gate](../src/spiral_ln/evaluation_reward_hacking_retry_guard.py) requires the adversarially optimal cumulative harm, benign coverage, and benign expected authorization count to meet all predeclared thresholds. It can choose among *licensed protocols with the same independently calibrated auditor error rates*, maximizing expected safe throughput subject to the registered harmful-risk cap.

**Exact two-attempt example:** take `α=1/5`, `β=1/10`, three worlds and two genuinely safe actions per world:

| Retry rule | Malicious cumulative harm | Benign ≥1 safe approval | Benign expected safe approvals |
|---|---:|---:|---:|
| Unrestricted | `9/50` | `99/100` | `9/5` |
| No repeated action | `2/15` | `99/100` | `9/5` |
| Lockout on rejection | `19/150` | `9/10` | `171/100` |
| Stop after any approval | `3/25` | `99/100` | `99/100` |

For a harm cap `7/50`, benign-coverage floor `9/10` and throughput floor `3/2`, the gate selects **no repeated action**, keeping expected benign safe throughput `9/5`. Tightening the harm cap to `13/100` selects **lockout after rejection**, with throughput `171/100`; tightening it to `1/10` yields no certified candidate from the registered list. The gates always distinguish infeasibility of the list from the runtime search cap. An independent exhaustive enumeration of every benign approval/rejection bit sequence confirms the coverage and throughput formulas.

### 15.6 What remains to solve

The present RHT-10 result permits multiple attempts against one fixed gold reference and a static, externally licensed noisy veto. The agent learns only from authorization/rejection outcomes and its own prior actions. It cannot alter the verifier, update the underlying gold reward, modify action/tool contracts, receive leaked audit metadata, or induce changes in the environment's underlying state between attempts. Those actions require a proper stochastic game with a controlled state transition and an independently attested authorization instrument.

The exact Bellman recursion is a classical finite POMDP-style inference/control argument, and its cumulative false-approval bounds are standard sequential hazard/union-bound mathematics. New ASMP-8/14 relevance would require a **nontrivial joint certification theorem** under dynamic state, measurable adversarial reward-model tampering, disclosure access and resource constraints, with a calibrated gold-reference uncertainty class. The finite results here provide named controls and regressions for that extension.

- [Exact repeated-authorization game](../src/spiral_ln/evaluation_reward_hacking_retry.py)
- [Two-sided reward-audit retry gate](../src/spiral_ln/evaluation_reward_hacking_retry_guard.py)
- [Independent brute-force retry tests](../tests/test_evaluation_reward_hacking_retry.py)
- [Independent benign-throughput and protocol-selection tests](../tests/test_evaluation_reward_hacking_retry_guard.py)
- [Reproducible source-bound receipt](../scripts/verify_reward_hacking_topology.py)


## 16. Mutable evaluator state: reward hacking across attested tool transitions (RHT-11)

**2026-11-10 | exact finite stateful-audit model.** The preceding RHT-10 experiment keeps the evaluator's conditional false-approval rates constant across attempts. A tool-using agent can change the evaluator or its inputs, and ordinary task operations can modify future evaluation state. RHT-11 makes that possibility explicit by combining the fixed UGC gold-reference world with a hidden two-state mutable evaluator and a separately owned integrity attestor. The result is a precisely scoped partially observed stochastic game with exact rational risk and liveness certificates.

### 16.1 Hidden worlds, tool actions, and readout contracts

Retain the finite UGC-generated reference-world set \(\Omega\), its independently defined protected gold cochains, and its proxy-maximizing candidate actions \(A_P\). The world \(\omega\in\Omega\) and the true task-reward function stay fixed for the whole experiment. Introduce a hidden **evaluator integrity state** \(s\in\{0,1\}\), with \(s=0\) intact and \(s=1\) compromised.

A licensed actor can spend a tool call on an abstract tamper action \(T\). When initially intact, the evaluator becomes compromised with externally specified probability \(p_T\); already compromised states remain compromised. The agent receives an acknowledgment if the attestor does not raise an alarm. The acknowledgment reveals neither whether the tamper succeeded nor the protected gold label.

On an attempted proxy-maximizing action \(a\), an independently anchored attestor checks the current evaluator state **before authorization**. An intact state is alarmed with probability \(f\), and a compromised state with probability \(d\). An alarm terminates the session. Conditional on passing this check, the reward evaluator approves an unsafe action with probability \(\alpha_s\), or approves a safe action with probability \(1-\beta_s\). The actor sees approved/rejected verdicts.

Conditional on a surviving non-harmful verdict, the evaluator may transition according to a registered stochastic kernel \(K^{\mathrm{reject}}\) or \(K^{\mathrm{safe}}\). These kernels cover ordinary operations that corrupt an initially intact evaluator, and external recovery that restores a compromised evaluator. The transition probabilities, attestation detection rates and readout rates must be valid **conditional on the entire preceding history** and the actual hidden state. The actor may be uncertain about the state and adapt accordingly.

All episodes are bounded by a total tool-call budget \(B\), including attempted tampering. Optional registered controls forbid repeated candidate actions, permit only one tamper attempt, lock out the session after rejection, or end it after any approval. The event of interest is the first authorized unsafe action, which is absorbing for risk accounting. A harmful approval remains the same public approval bit the actor would otherwise observe.

### 16.2 Exact partially observed Bellman theorem (RHT-11/T1)

Let \(m_{\omega,s}\) be an unnormalized nonnegative belief mass over the hidden gold-reference world and evaluator state, restricted to paths that have not yet produced harmful authorization. For each attempted candidate action \(a\in A_P\) define the registered gold-badness indicator \(H_\omega(a)\) from RHT-10, the attestation pass probability \(g_s\), and conditional approval probability

\[
 p_{\omega,s}(a)=H_\omega(a)\alpha_s+
 (1-H_\omega(a))(1-\beta_s).
\]

The immediately accumulated harmful-authorization mass is

\[
 h_a(m)=\sum_{\omega,s}m_{\omega,s}\,g_s\,H_\omega(a)\alpha_s.
\]

On an observed rejection, update the unnormalized surviving mass by

\[
 m^{R}_{\omega,s'}=\sum_s
 m_{\omega,s}\,g_s\,[1-p_{\omega,s}(a)]\,
 K^{R}_{s,s'}.
\]

On an observed **safe** approval, the surviving mass is

\[
 m^{A}_{\omega,s'}=\sum_s
 m_{\omega,s}\,g_s\,p_{\omega,s}(a)
 [1-H_\omega(a)]\,K^{A}_{s,s'}.
\]

An externally called tamper action generates a different posterior \(m^{T}\): first apply its evaluator-state transition \(P_T\), then multiply by the probability of a non-alarm acknowledgment from the tamper attestor. All alarm branches terminate without an authorized unsafe action.

Write \(V_B(m,U,t)\) for maximum *unnormalized* harmful-authorization mass with \(B\) calls remaining, already tried action set \(U\), and tamper-use flag \(t\). The Bellman equation is

\[
\boxed{
V_B=
\max\left\{0,\max_{a\in A_P\mathrm{\ licensed}}
 \bigl[h_a(m)+V_{B-1}(m^R,U\cup\{a\},t)
 +V_{B-1}(m^A,U\cup\{a\},t)\bigr], V_{B-1}(m^T,U,1)
\right\},
}
\tag{RHT-11/1}
\]

with forbidden terms omitted when retry or tamper contracts disallow their continuation. A \(B=0\) state has value zero. Initially \(m_{\omega,0}=w_\omega\) when the baseline integrity is independently attested clean. A registered prior compromise probability can instead initialize mass on both integrity states.

**Proof:** each legal call induces a disjoint distribution of alarm, bad-approved, rejected, and safe-approved outcomes. Bad approval immediately contributes its mass; surviving observable branches carry the displayed posterior and smaller remaining horizon. Conditional optimization followed by backwards induction proves the recursion. A randomized policy mixes deterministic choices and does not improve a finite maximum. The resulting probability is \(V_B(m_0,\varnothing,0)/\sum_\omega w_\omega\). This is finite POMDP-style dynamic programming, without a new claim about the general computational complexity of POMDPs.

The implementation uses exact rational fractions, memoized posterior-state recursion, a per-run state cap, and a separate fixed-script evaluator. A world-by-world traversal of each returned adaptive policy, plus an **independent exhaustive two-step verdict-policy enumerator**, validates the calculations.

### 16.3 A sharp tamper and incidental-drift witness (RHT-11/T2)

Use RHT-10's three-world binary \(K_{2,3}\) UGC fixture. Each world has one bad action among three equally proxy-maximizing candidates. Freeze \(\alpha_0=1/5\), \(\alpha_1=4/5\), and \(\beta_0=\beta_1=0\). With no compromise, two adaptive candidate probes have optimal cumulative harm probability \(14/75\).

If an actor can spend its first call attempting a silent evaluator tamper with success probability \(3/4\), then probe a candidate on its second call, its exact harmful-authorization probability becomes

\[
\boxed{
R_{\rm tamper}=
\tfrac13\left(\tfrac34\cdot\tfrac45+
\tfrac14\cdot\tfrac15\right)=\tfrac{13}{60}.
}
\tag{RHT-11/2}
\]

The tamper-probe strategy increases the optimal two-call attack probability by exactly \(13/60-14/75=3/100\). The tamper result is **unobserved**; the posterior over evaluator integrity is updated only from the registered no-alarm acknowledgment. Fixed-script and adaptive-policy exact oracles agree on this two-call witness.

A larger change can arise from otherwise legitimate task operations. Disable the explicit tamper action and set the transition so that **an approved safe action compromises the next evaluator with probability one**. The agent can first probe \(a_0\), then condition its next choice on the approval or rejection. The exact risk is \(29/75\), compared with \(14/75\) in the stable evaluator. When rejection rather than safe approval causes the compromise, the corresponding exact optimal risk is \(26/75\).

These experiments distinguish mutable auditor dynamics from reward aliasing in the original static margin fibres. All initial category margins, proxy scores, gold cochains and UGC constraint assignments stay unchanged. Only the evaluator transition kernel changes. The gold outcome remains protected by an independently specified objective, which the compromised evaluator may misreport.

### 16.4 Independent attestation yields a history-conditional safety invariant (RHT-11/T3)

For any proposed unsafe action, in hidden evaluator state \(s\) the probability of a harmful authorization at that call is bounded by the probability \(g_s\) of passing the independent state attestation times the evaluator's false-approval probability \(\alpha_s\). A hidden-state posterior can be arbitrarily affected by previous actions, approvals and rejections. Taking the maximum over both integrity states gives the following **uniform history-conditional hazard certificate**:

\[
\boxed{
\alpha_*=
\max\bigl((1-f)\alpha_0,(1-d)\alpha_1\bigr).
}
\tag{RHT-11/3}
\]

**Proof:** after any concrete public or private history in which the session survives, the actual evaluator state is either intact or compromised. The probability of an unsafe approval is, for each state, bounded by the corresponding factor in (RHT-11/3). Averaging over any posterior mixture of those states preserves its maximum as an upper bound. The bound therefore survives arbitrary actor choices and the registered evaluator-state transitions, provided the *external attestation guarantees remain valid conditionally after the history*. Applying the RHT-10 conditional-hazard theorem to at most \(B\) candidate calls yields

\[
\Pr(\text{any harmful authorization by }B)
\le1-(1-\alpha_*)^B.                                 \tag{RHT-11/4}
\]

Tamper calls count against the finite total-call budget and do not themselves authorize an action. This upper bound may be loose when the agent does not know which action is unsafe. It supplies a **posterior-independent safety envelope** under the independently established attestation premises.

When \(\alpha_1>\alpha_0>0\), compromised-state detection satisfying

\[
\boxed{d\ge1-\alpha_0/\alpha_1}                       \tag{RHT-11/5}
\]

is sufficient to restore the intact evaluator's *raw* per-call false-authorization ceiling \(\alpha_0\), regardless of hidden integrity state and prior tampering. For \(\alpha_0=1/5\) and \(\alpha_1=4/5\) the threshold is \(d\ge3/4\).

The finite tests confirm that pre-authorization detection of compromised state at rate \(3/4\), with zero intact-state false alarms, reduces the two-call malicious risk to \(14/75\) both under the intentional-tamper example and under safe-approval evaluator drift. Attesting only at the **explicit tamper tool call** cannot control drift induced by an ordinary task operation; the pre-authorization check is the relevant invariant.

The theorem assumes an **independently rooted attestor** and a reliably enforced alarm/termination semantics. If the agent can alter those components, its conditional rates require a new model and separate verification. A judge's self-report of being intact is insufficient to establish (RHT-11/3).

### 16.5 A two-sided stateful detector frontier (RHT-11/T4)

Increasing detection can also produce false alarms on intact, legitimately functioning evaluators. A useful certificate therefore needs a non-inert authorization requirement. The [stateful attestation guard](../src/spiral_ln/evaluation_reward_hacking_stateful_guard.py) combines the exact malicious Bellman optimum, the posterior-independent hazard ceiling (RHT-11/3), and a **benign safe-only reference policy**. This benign reference proposes independently gold-verified safe actions, never attempts tampering, and counts both the probability of *at least one safe authorization* and the expected total number of accepted safe actions before the registered session ends.

For a candidate attestor with per-probe compromised detection \(d\) and intact-state false alarm \(f\), consider two tool calls and the same three-world/tamper model from §16.3. Freeze \(\beta_0=\beta_1=0\) for the benign baseline:

| Detector d | False alarm f | Optimal attack harm | Benign ≥1 safe approval | Expected safe approvals | Worst conditional harm hazard |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 13/60 | 1 | 2 | 4/5 |
| 1/2 | 1/20 | 5149/30000 | 19/20 | 741/400 | 2/5 |
| 3/4 | 1/10 | 393/2500 | 9/10 | 171/100 | 1/5 |

A detection strategy is evaluated with **its own externally licensed rates**; the selector rejects comparisons that alter underlying evaluator accuracy, tool-tamper success, state-transition kernels or retry permissions. For a cumulative harm cap \(7/40\), safe-authorization floor \(9/10\), and expected benign safe-throughput floor \(17/10\), the highest-throughput passing choice is \(d=1/2,f=1/20\). Tightening the harm cap to \(4/25\), or requiring the *uniform history-conditional hazard* at most \(1/5\), selects \(d=3/4,f=1/10\). A harm cap \(7/50\) has no feasible candidate from this registered detector bank.

An independent exhaustive benign oracle enumerates every combination of attestation alarms, safe approvals/rejections and evaluator-state transitions. The source-bound evidence checks the exact attack policy with the existing world-by-world evaluator and independent two-step policy enumeration. All computations are rational and CPU-only.

### 16.6 Novelty boundary and next required experiment

This is a finite construction combining existing POMDP, controlled sensing and causal reward-tampering mathematics. Everitt, Hutter, Kumar and Krakovna's [*Reward Tampering Problems and Solutions in Reinforcement Learning*](https://doi.org/10.1007/s11229-021-03141-4) develops causal-design conditions against reward-function and reward-input tampering. The 2026 [ICML Reward Hacking Benchmark](https://proceedings.mlr.press/v306/thaman26a.html) examines multi-step tool-use exploits, including evaluator-facing modifications and chained tasks. RHT-11 gives an **executable finite stress test for our EvalMath game-space disclosure and independent attestation calculus**; its Bellman and hazard identities should be treated as elementary conditional baselines.

The current model includes a fixed independent gold-reference world and a mutable binary *evaluator* state. It does not yet allow the agent to rewrite gold truth, change the underlying task state, tamper with the independent root attestor, deceive multiple colluding observers, or learn a new policy by updating model weights between episodes. Those require a richer stochastic game and independent empirical validation. The end goal is a certified non-inert controller whose regret and false authorization stay bounded when the agent can influence the future distribution of observations and its own evaluator. A mathematical bound only covers the declared observation/actuation/attestation contract.

- [Exact mutable evaluator POMDP and fixed-schedule oracle](../src/spiral_ln/evaluation_reward_hacking_stateful.py)
- [Two-sided attestation/throughput guard](../src/spiral_ln/evaluation_reward_hacking_stateful_guard.py)
- [Independent stateful attack regression tests](../tests/test_evaluation_reward_hacking_stateful.py)
- [Independent benign-state trajectory tests](../tests/test_evaluation_reward_hacking_stateful_guard.py)
- [Source-bound EvalMath receipt](../scripts/verify_reward_hacking_topology.py)


## 17. Transition-closed reward cohomology and interval-robust regret (RHT-12)

**2026-11-10 | exact finite theorems, time-expanded game DAG.** RHT-11 gave the agent an opportunity to corrupt the evaluator while its protected reference-world utility remained fixed. RHT-12 takes the corresponding **reachable complete trajectories** as the fundamental object. Its vertices contain the task state, the evaluator-integrity state, and the time coordinate. Every directed edge advances one time layer, carrying a rational protected gold reward \(r_e\) and the evaluator's proxy reward \(\widehat r_e\).

This is an exact path-roster certificate. It treats all registered paths as feasible choices for a conservative proxy-maximizing actor. Transition probabilities, hidden-state inference and stochastic-policy expectations from RHT-11 require additional analysis beyond this deterministic support model. The protected gold reward remains an independent, externally justified premise.

### 17.1 Relative path cohomology characterizes path-constant reward gaps

Fix a finite time-expanded DAG with one start \(s\), an explicit nonempty terminal set \(T\), and directed edges \(e:u\to v\) that each advance one time layer. Remove dead edges lying on no complete \(s\)-to-\(T\) path, since they cannot affect realizable returns. For a complete path \(p\), write

\[
 U(p)=\sum_{e\in p}r_e,\quad
 \widehat U(p)=\sum_{e\in p}\widehat r_e,\quad
 \Delta(p)=\widehat U(p)-U(p).
\]

Let \(\omega_e=\widehat r_e-r_e\). Append a virtual sink \(\star\) and one zero-discrepancy edge \(t\to\star\) for each terminal. Denote the resulting *productive augmented graph* by \(\overline G\).

**Theorem RHT-12/T1.** The following conditions are equivalent:

1. \(\Delta(p)=C\) for every complete path \(p\) from \(s\) to any terminal;
2. there exists a rational vertex potential \(\phi\) on productive vertices such that \(\omega_e=\phi(v)-\phi(u)\) on every productive transition and all terminals share the same potential \(\phi(t)=\phi(s)+C\);
3. the augmented discrepancy cochain on \(\overline G\), including the zero virtual edges, has zero period on every undirected graph cycle;
4. all its fundamental-cycle periods under any spanning forest vanish.

**Proof.** If (1) holds, define \(\phi(v)\) by the discrepancy along any directed prefix \(s\to v\). Every productive prefix can be completed to a terminal. Two different prefixes to \(v\), followed by the same suffix, produce equal complete-path discrepancies, so the prefix discrepancy is well defined. Every edge therefore increments the potential by \(\omega_e\), and all terminals acquire \(C\) relative to \(s\). Conversely, (2) telescopes along every complete path. Extend \(\phi\) to \(\star\) using that common terminal value. All virtual edges then have differential zero. A graph cochain is exact precisely when it annihilates its entire cycle space, and fundamental cycles span that space, proving (2)\(\Leftrightarrow\)(3)\(\Leftrightarrow\)(4).

**Terminal-boundary negative control.** A graph containing only \(s\to t_{\rm good}\) and \(s\to t_{\rm bad}\) is an undirected tree. If its gold rewards are \(2,0\) and proxy rewards \(2,3\), the gold-optimal terminal is bad under the proxy. The discrepancy periods become nonzero after gluing terminals to \(\star\). This is why the *relative terminal boundary* belongs in the certificate even for a directed acyclic transition system without ordinary cycles.

This is an exact finite-horizon/undiscounted version of established potential-based shaping results; see [Ng, Harada and Russell (1999)](https://ai.stanford.edu/~ang/papers/shaping-icml99.pdf). For discounted settings, the compatible term is \(\gamma\phi(s')-\phi(s)\), with discount-weighted terminal conventions.

### 17.2 Exact oscillation and a quantitative gold-regret ceiling

Define the discrepancy width on the **actual complete-path roster**

\[
 W(G,\omega)=\max_{p\in\mathcal P}\Delta(p)
             -\min_{p\in\mathcal P}\Delta(p).
\]

Because the time-expanded graph is acyclic, longest- and shortest-path dynamic programming computes both extrema exactly in \(O(|V|+|E|)\), even with negative edge rewards. In particular, \(W=0\) exactly when T1 holds.

Let \(p^\star\) maximize protected gold return and let \(\widehat p\) be *any* proxy-maximizing complete path, including adversarial tie-breaking. Then

\[
\widehat U(\widehat p)\ge\widehat U(p^\star)
\quad\Longrightarrow\quad
\boxed{0\le U(p^\star)-U(\widehat p)\le W(G,\omega).}
\tag{RHT-12/1}
\]

The proof subtracts true gold from the displayed proxy inequality and bounds \(\Delta(\widehat p)-\Delta(p^\star)\) by the width. A lexicographic DAG recurrence maximizing \((\widehat U,-U)\) gives the **exact worst true regret among all proxy maximizers**. This regret can be strictly smaller than \(W\). The inequality is sharp: two parallel actions with equal proxy value \(2\), gold values \(2\) and \(0\), and proxy tie-breaking toward the low-gold edge attain regret \(W=2\).

For a spanning-tree potential \(\phi\) on \(\overline G\), let \(h_e=\omega_e-(\phi(v)-\phi(u))\) on each **non-tree chord**. Every complete path, extended to \(\star\), traverses each edge at most once. Differences between two path edge-incidence vectors have chord coefficients in \(\{-1,0,1\}\). Tree contributions telescope to a common endpoint difference. Therefore

\[
\boxed{W(G,\omega)\le\sum_{\text{fundamental chords }e}|h_e|.}
\tag{RHT-12/2}
\]

This basis-dependent bound may be loose. It supplies a cheap cycle-local upper certificate and is exactly zero whenever the reward cochain has trivial terminal-relative holonomy. The implementation verifies the full equivalence, both path extrema and the chord bound using independently constructed graph procedures.

### 17.3 Uncertain gold: exact *robust* regret by a product DAG

The protected gold oracle may provide defensible **independent edge intervals** \(\ell_e\le r_e\le u_e\) rather than one exact reward vector. Keep proxy values fixed. Assume every complete path takes the same number of time steps, so two paths can be traversed synchronously in the time-expanded **product DAG**.

For any pair \(p,q\) the shared edges cancel in a difference of their gold returns. Since the edge intervals are independent, maximizing that difference assigns \(u_e\) to edges in \(p\setminus q\) and \(\ell_e\) to edges in \(q\setminus p\). Thus the exact **worst-case gold regret** of choosing a proxy maximizer is

\[
\boxed{
R_{\mathrm{rob}}=
\max_{\substack{p\in\mathcal P\\q\in\arg\max\widehat U}}
\left[
\sum_{e\in p\setminus q}u_e-
\sum_{e\in q\setminus p}\ell_e
\right].
}
\tag{RHT-12/3}
\]

This equals \(\sup_{r\in[\ell,u]}\max_{q\in\arg\max\widehat U}
(\max_p U_r(p)-U_r(q))\), with the maxima commuting over finite path and interval endpoint choices. An exact pair-state Bellman recurrence on \((v_p,v_q)\) computes it by maximizing \(u_e-\ell_f\) for two distinct simultaneous edge transitions \(e,f\), and zero for a shared transition. The second path is restricted to **proxy-optimal edges**, identified by forward/backward proxy longest-path values.

The corresponding robust discrepancy width is

\[
 W_{\rm rob}
 =\sup_{r\in[\ell,u]} \left[
 \max_p(\widehat U(p)-U_r(p))
 -\min_q(\widehat U(q)-U_r(q))\right].
\tag{RHT-12/4}
\]

The same product DAG computes it using interval bounds
\(\underline\omega_e=\widehat r_e-u_e\) and
\(\overline\omega_e=\widehat r_e-\ell_e\).
In the product recurrence, a common edge contributes **zero**, since the same uncertain gold reward is shared by both compared paths. This source-identity cancellation is necessary for a valid correlated comparison. The exact theorem gives \(R_{\rm rob}\le W_{\rm rob}\).

A second forward/backward dynamic program computes

\[
 U_{\mathrm{floor}}=
 \min_{q\in\arg\max\widehat U}\sum_{e\in q}\ell_e,
\]

the largest guaranteed lower bound on gold return of **any** proxy-selected path for every licensed interval reward assignment. A two-sided guard passes only when both \(R_{\rm rob}\le\varepsilon\) and \(U_{\mathrm{floor}}\ge u_0\), with \(\varepsilon,u_0\) declared before optimization. Its guarantee depends on the actual gold rewards lying in these intervals.

### 17.4 A mutable-evaluator path witness and the common-stem control

The executable [time-expanded example](../tests/test_evaluation_reward_transition_closure.py) has one initial vertex, two evaluator states at the next layer (intact and compromised), and safe/bad terminal task outcomes. The intact-good trajectory receives gold/proxy \(2/2\); an intact-bad outcome \(0/1\); the compromised-good outcome \(2/0\); and the compromised-bad outcome \(0/3\). All four complete paths remain feasible in the declared graph.

The nominal discrepancy ranges from \(-2\) to \(3\), giving \(W=5\). The proxy-maximizing path reaches the bad outcome with proxy return \(3\) and gold return \(0\). True optimal gold return is \(2\), giving exact regret \(2\) inside the width bound. Relative exactness fails, and the relative fundamental-cycle periods witness it.

Allow the two good-outcome gold transitions independently to vary over \([1,3]\); fix the remaining gold transitions at zero. The synchronized product-DAG calculation gives **exact robust width \(6\)**, **exact robust proxy regret \(3\)**, and gold floor zero. A wholly separate oracle enumerates all interval endpoint assignments and complete paths to verify these values. The robust guard passes a regret budget three and rejects a budget two.

**Shared-edge identity control.** In a graph where all complete paths traverse the same initial transition, let that transition's gold be uncertain over \([0,100]\). The gold comparison between two complete paths cancels this entire interval. The robust width is \(3\) and robust proxy regret \(2\) for a two-branch instance. An approach summing independent worst-case path rewards would spuriously amplify uncertainty from the shared edge. This is a basic but important example of preserving **reward-source identity** across different game-space paths.

### 17.5 Verification and remaining research obligation

- [Exact time-expanded cohomology, path and product-DAG solver](../src/spiral_ln/evaluation_reward_transition_closure.py).
- [Independent complete-path, interval-vertex, random-game, potential and shared-edge tests](../tests/test_evaluation_reward_transition_closure.py).
- [Source-bound RHT research receipt](../scripts/verify_reward_hacking_topology.py), with the new reproducible nominal/robust witness.
- The focused CPU-only workflow checks the new module alongside RHT-01–11; no GPU, learned model or judge is invoked.

The tree/chord identities, DAG extrema, path potential telescoping and independent interval optimization are standard finite algebra/optimization. Their synthesis here defines a testable **transition-closed reward certificate** for the registered EvalMath game space. It assumes all candidate paths are feasible under the stated controller access grammar and optimizes over paths, rather than over stochastic policies with externally imposed transition probabilities.

The next extension must incorporate stochastic state transitions, partial observability of evaluator integrity, gold-label uncertainty coupled across time, and the possibility that a model changes the independent attestation channel. The relevant prior research includes [Everitt et al. (2021), causal reward-tampering conditions](https://doi.org/10.1007/s11229-021-03141-4), [Ng et al. (1999), policy-invariant shaping](https://ai.stanford.edu/~ang/papers/shaping-icml99.pdf), and the existing [EvalMath RHT-11 finite evaluator-tamper game](../src/spiral_ln/evaluation_reward_hacking_stateful.py). This is a conditional mathematical safeguard for a declared gold target, rather than a proof that any learned evaluator's rewards encode human values.


## 18. Stochastic game-space reward closure under hidden evaluator state (RHT-13)

**2026-11-10 | exact finite partial-observation results and source-bound synthetic tests.** RHT-11 considered a fixed latent gold world and a mutable hidden evaluator under adaptive tool actions; RHT-12 gave a relative-path and robust-regret certificate for the complete *support graph* of possible time-indexed trajectories. RHT-13 connects them by optimizing **observation-adapted policies** under an exact, normalized stochastic transition kernel, while retaining global identity across repeated, uncertain true-reward signals. The claims below concern a frozen finite policy grammar and independently licensed gold parameters. They imply no soundness of a learned reward model.

### 18.1 Controlled hidden-state kernel and shared gold features

Fix finite hidden states \(S\), allowed actions \(A\), actor-visible observations \(O\), a horizon \(H\), initial distribution \(\mu_0\), and conditional kernel

\[
K(s',o\mid s,a)\ge0,\qquad
\sum_{s',o}K(s',o\mid s,a)=1.
\]

A transition \((s,a,s',o)\) emits a fixed rational proxy reward \(\widehat r\) and protected gold reward of the form

\[
r_\theta(s,a,s',o)=r_0(s,a,s',o)
+\sum_{j=1}^k f_j(s,a,s',o)\theta_j,
\qquad
\theta\in\Theta=\prod_{j=1}^k[\ell_j,u_j].
\]

The feature coefficients \(f_j\), fixed reward \(r_0\), and entire interval family \(\Theta\) must be independently registered. Crucially **one parameter \(\theta_j\) is shared at every occurrence of that protected signal** across time, agent actions and hidden worlds. For example, all approvals of genuinely safe actions use the same independently justified safe-approval utility parameter. The agent observes the kernel's registered \(o\), including any numeric proxy score, while the hidden evaluator state remains private.

The controller's deterministic policy \(\pi\) maps the sequence of prior observations and its own selected actions to the next action. Exactly \(H\) calls are made, including zero-reward no-op calls after externally terminated sessions. This is a finite mandatory-horizon observation-policy class; voluntary early stopping is a separate extension. Given fixed \(K\) and \(\mu_0\), each policy induces an expected occupancy signature \((b_\pi,d_{\pi,1},\ldots,d_{\pi,k})\), so

\[
\boxed{J_\theta(\pi)=b_\pi+\langle d_\pi,\theta\rangle}.
\tag{RHT-13/1}
\]

The actor's expected proxy return \(\widehat J(\pi)\) is separately fixed by the same policy and kernel. Each signal-feature occupancy is computed by an independent **world-by-world traversal**, not inferred from proxy outputs.

### 18.2 Belief-state Bellman and sharp robust-regret vertex theorem

For unnormalized hidden-state masses \(m_s\), taking action \(a\) induces response-branch mass

\[
m_{s'}^{a,o}=\sum_s m_sK(s',o\mid s,a).
\]

The immediate expected proxy and gold returns are
\(\sum_{s,s',o}m_sK(s',o\mid s,a)\widehat r(s,a,s',o)\) and the analogous sum with \(r_\theta\). Separate finite Bellman recursions optimize expected gold, expected proxy with **adversarially low gold on proxy ties**, and the extrema of expected proxy-minus-gold discrepancy. Each observation branch carries its own posterior and remaining horizon, so these solutions use precisely the controller's licensed information.

Let \(\mathcal P_O\) be this finite observation-policy class and
\(\mathcal P_{\rm proxy}=\arg\max_{\pi\in\mathcal P_O}\widehat J(\pi)\).
At a fixed \(\theta\), the exact worst proxy-selection regret is

\[
R_\theta=\max_{\pi\in\mathcal P_O}J_\theta(\pi)
-\min_{\widehat\pi\in\mathcal P_{\rm proxy}}J_\theta(\widehat\pi).
\]

**Theorem RHT-13/T1 (exact interval-robust expected regret).**
When \(K\) and the proxy reward are independent of \(\theta\), the maximum over the entire box \(\Theta\) equals the maximum over its vertices:

\[
\boxed{
R_{\rm rob}
=\max_{\theta\in\Theta}R_\theta
=\max_{\theta\in\operatorname{vertices}(\Theta)}
\left[
\max_{\pi\in\mathcal P_O}J_\theta(\pi)
-\min_{\widehat\pi\in\mathcal P_{\rm proxy}}J_\theta(\widehat\pi)
\right].
}
\tag{RHT-13/2}
\]

**Proof:** for a fixed pair \((\pi,\widehat\pi)\), the gold-return difference is affine in \(\theta\) by (RHT-13/1). Taking the maximum over all challenger/proxy-selected pairs gives \(R_\theta\) as a finite pointwise maximum of affine functions, hence convex. The maximum of a convex function over a rectangular polytope is attained at a vertex. The two policy Bellman recursions find the exact pairwise extrema at each vertex. The same proof applies to the maximum expected policy-discrepancy width

\[
W_\Pi(\theta)=
\max_{\pi}[\widehat J(\pi)-J_\theta(\pi)]
-\min_{\pi}[\widehat J(\pi)-J_\theta(\pi)]
\]

and to the **minimum licensed true return** among proxy-maximizing policies, which is a minimum of affine functions. The finite certificate checks

\[
\boxed{0\le R_{\rm rob}\le
W_{\rm rob}:=\max_{\theta\in\Theta}W_\Pi(\theta)}
\tag{RHT-13/3}
\]

and can require both \(R_{\rm rob}\le\varepsilon\) and a minimum proxy-policy gold return \(J_{\rm floor}\ge u_0\). A failed bound denies certification; a registered DP or occupancy-enumeration budget overrun raises a separate error.

All interval vertices are evaluated by exact rational belief-state dynamic programming. The implementation caps the number of reward features, hidden states and Bellman subproblems. This exact finite algorithm carries no general polynomial-time complexity claim for POMDP control. Its gold parameter intervals must not silently affect the stochastic kernel or the actor's observable proxy, since either would change the optimization/convexity argument.

### 18.3 The expectation-level cohomology is larger than pathwise shaping

RHT-12's relative-graph theorem certifies that \(\widehat r-r\) telescopes to a constant on **every realized support path**. For expected-return policy invariance under a fixed stochastic kernel, we can exploit a larger class of reward differences.

Let \(\delta_t(s,a,s',o)=\widehat r_t-r_t\) and suppose rational time/state potentials \(\phi_t:S\to\mathbb Q\) satisfy \(\phi_H\equiv0\) and, for every \(t,s,a\),

\[
\boxed{
\mathbb E[\delta_t\mid s,a]
=\mathbb E[\phi_{t+1}(s_{t+1})\mid s,a]-\phi_t(s).
}
\tag{RHT-13/4}
\]

Define the realized residual

\[
m_t=\delta_t-
\bigl(\phi_{t+1}(s_{t+1})-\phi_t(s_t)\bigr).
\]

Its conditional expectation given the state/action is zero. It is therefore a martingale difference under every observation-adapted controller, even though the agent cannot directly observe the full state. Taking expectations and telescoping yields the *same expected discrepancy for every policy*:

\[
\boxed{
\widehat J(\pi)-J_\theta(\pi)
=-\sum_s\mu_0(s)\phi_0(s)
\quad\text{for all }\pi\in\mathcal P_O.
}
\tag{RHT-13/5}
\]

This proves identical **expected-return rankings** for the proxy and protected gold in the declared fixed-horizon class. The executable sufficient certificate sets \(\phi_H=0\) and recursively asks whether
\(\mathbb E[\phi_{t+1}-\delta_t\mid s,a]\) is **independent of action** at every hidden state and time. A failure returns the first specific state/time/action disagreement.

The proof uses standard martingale/potential-based shaping mathematics. The interpretation as an evaluator-channel quotient supplies an important **negative control for purely pathwise holonomy tests**: a reward discrepancy may have nonzero periods on realized paths and nevertheless be invisible to every controller's *expected* objective. It can still matter for tail risk, rare harm and risk-sensitive utilities, which require different safety conditions.

**Exact witness:** take a one-hidden-state game with two available actions. Each action emits an independent fair \(+1\) or \(-1\) *proxy reward*, with protected gold zero, and the actor sees the sign after every step. At horizon two, RHT-12's complete realized-support graph has path-discrepancy width **4** and nontrivial periods. RHT-13's Markov-coboundary certificate has \(\phi_t=0\) and proves **zero expected discrepancy** for every observation policy. Its exact belief-state optimizer verifies robust expected regret and expected discrepancy width both equal zero. A separate biased-signal fixture fails the conditional action-independence test.

### 18.4 UGC evaluator corruption with observable reward inflation

The [RHT-13 environment fixture](../src/spiral_ln/evaluation_reward_stochastic_fixture.py) starts from the seven-state representation of RHT-11's three \(K_{2,3}\) binary UGC worlds: hidden gold world \(w\in\{0,1,2\}\) and hidden evaluator integrity \(s\in\{0,1\}\), plus an alarm/terminal state. The initial distribution assigns probability \(1/3\) to each intact world. The actor may probe one of the three proxy-tied candidate outcomes or call the tamper tool. The evaluator's integrity changes according to the registered mutation/attestation kernel. All approval/rejection/alarm/tamper acknowledgment events are reported to the agent.

An approved probe emits proxy reward **1** when the evaluator is intact, and proxy reward **4** when compromised; the numeric reward is included in the observation. The independently licensed gold **reward features** are safe approval (positive), unsafe approval (negative), and tamper cost (subtracted). A test gold point is \((1,-2,1/4)\), while one declared uncertainty example takes the independently coupled global intervals

\[
\theta_{\rm safe}\in[1,2],\qquad
\theta_{\rm unsafe}\in[-3,-2],\qquad
\theta_{\rm tamper\,cost}\in[0,1/4].
\]

The fixed-horizon belief DP computes gold-optimal and proxy-optimal policies over exactly the same observed verdicts and returns. A **separate exhaustive two-step conditional policy enumerator** cross-checks all returned expected proxy/gold extrema, including adversarial tie-breaking. The robust certificate compares the eight gold interval vertices with an independent brute-force scan of deterministic two-step observation policies. Randomly generated two-hidden-state models supply additional independent controls.

A pathwise RHT-12 time-expansion can also be constructed from the kernel's positive-probability transition support. Its pathwise reward discrepancy width is a conservative ceiling on the expected-policy discrepancy width for any fixed gold point; the stochastic model additionally prices the actual transition probabilities and the actor's restricted observation history. The two models must retain the same transition and reward identifiers for this comparison.

### 18.5 Verification and scope

- [Exact belief-state and shared-parameter robust certificate](../src/spiral_ln/evaluation_reward_stochastic_closure.py).
- [UGC mutable evaluator and zero-mean reward controls](../src/spiral_ln/evaluation_reward_stochastic_fixture.py).
- [Independent brute policy, reward-interval and potential tests](../tests/test_evaluation_reward_stochastic_closure.py).
- [Source-bound receipt](../scripts/verify_reward_hacking_topology.py), schema RHT-01.8 after integration.
- The focused Python CI runs only the finite exact research oracles and their independent controls.

The robust regret formulas are finite occupancy-measure/reward-uncertainty results closely related to [Regan and Boutilier, robust policy computation under imprecise rewards (2010)](https://doi.org/10.1609/aaai.v24i1.7740) and [Robust Online Optimization of Reward-Uncertain MDPs (2011)](https://www.ijcai.org/Proceedings/11/Papers/361.pdf). Potential shaping in partially observed systems has established results, including [Potential-Based Reward Shaping for POMDPs (AAMAS 2013)](https://aamas.csc.liv.ac.uk/Proceedings/aamas2013/docs/p1123.pdf) and more recent noisy-reward-machine work. Our finite RHT-13 theorem records a controlled combination of these ingredients with the specific UGC reachability and feedback signal access grammar; it should not be advertised as a new general POMDP theorem or as a solution to real-world human-value misspecification.

The next model requires a *stochastic gold-world transition* that changes the actual task rather than solely the evaluator, partial observation of evaluator and task state with calibrated correlated noise, and reward uncertainty that may influence transitions. A model capable of modifying its own independent attestor would also invalidate the conditional soundness premise and needs explicit causal/security controls.


### 18.6 Global reward-source identity is part of the safety claim

A minimal negative control isolates the coupling represented in the \(f_j\) features. Take one hidden state, two proxy-tied actions \(A,B\), mandatory two-step horizon and proxy reward zero on each action. If both actions deliver the *same externally licensed* true reward parameter \(\theta\in[0,10]\) at every occurrence, then every policy's true reward is exactly \(2\theta\). Thus its exact robust proxy-selection regret and expected discrepancy width are both **zero**, even though the true reward parameter spans ten units.

If \(A\) and \(B\) instead have genuinely **independent gold parameters** \(\theta_A,\theta_B\in[0,10]\), an adversarial proxy tie may choose \(A\) twice when \(\theta_A=0\) and \(\theta_B=10\). Exact robust regret and discrepancy width both become **20**. The only change is the auditor's licensed identification of reward sources. Treating each occurrence of one global reward signal as an independently adjustable unknown would therefore produce a spurious reward-hacking risk certificate. The [exact two-parameter negative control](../tests/test_evaluation_reward_stochastic_closure.py) checks this boundary against the same POMDP optimizer and reward interval oracle.

The reverse danger is at least as important: **incorrectly assuming a shared source** when actual gold values can vary by action, time or task state would understate regret. Signal identity and the causal source of the protected gold must be established outside the proxy optimization loop, with uncertainty ranges covering allowed drift and hidden heterogeneity.


## 19. Shared uncertain transition kernels: a genuine interior reward-hacking maximum (RHT-14)

**2026-11-10 | finite exact nonrectangular-kernel theorem and counterexamples.** RHT-13 showed that with a *fixed* transition kernel, rectangular uncertainty in globally licensed true-reward features \(\theta\) can be checked at its interval vertices. RHT-14 changes the stochastic kernel itself. An unknown but fixed parameter \(p\) is reused across transitions, states and time steps. This is a **globally coupled / nonrectangular transition uncertainty family**, with a mathematical behavior that invalidates any unconditional endpoint-only shortcut for the kernel parameter.

### 19.1 Typed shared-parameter kernel

Fix the finite hidden-state, actor-observation and action grammar of RHT-13, with two mandatory calls. Every conditional outcome has probability

\[
K_p(s',o\mid s,a)=u_{s,a,s',o}+v_{s,a,s',o}p,
\qquad p\in[p_-,p_+]\subseteq[0,1].
\]

The channel is required to be nonnegative on the entire interval and to normalize identically in \(p\) for every hidden state/action. Since each probability is affine, checking both interval endpoints is sufficient to validate **an individual transition probability**, and checking zero total slope and unit total intercept validates normalization. These local kernel-validation facts are distinct from maximizing a two-step *reward* over the shared parameter.

A single value \(p\) is chosen for the entire trajectory, and the controller sees only its registered observations. Protected transition gold is \(r_\theta=r_0+\sum_j f_j\theta_j\) with \(\theta\) in an independently licensed rational box \(\Theta\). Proxy rewards and the transition kernel remain independent of \(\theta\).

For a fixed deterministic observation policy \(\pi\), its expected returns can be computed exactly by multiplying transition polynomials along each observation branch. Since the same parameter occurs in both calls,

\[
\boxed{
\widehat J_\pi(p)=\sum_{k=0}^2 a_{\pi,k}p^k,\qquad
J_{\pi,\theta}(p)=\sum_{k=0}^2
\left(b_{\pi,k}+\sum_j d_{\pi,j,k}\theta_j\right)p^k.
}
\tag{RHT-14/1}
\]

The coefficients are rational and are evaluated by an independent complete-world/observation history oracle at fixed rational \(p\), cross-checking the symbolic polynomial evaluator. The expected gold occupancy continues to share every reward-source coefficient globally across time.

### 19.2 The exact univariate robust-regret theorem

For the first exact reference solver, restrict attention to an uncertainty interval on which the **entire set of proxy-optimal deterministic observation policies is constant**. This is a checkable condition rather than an assumed empirical observation. The solver enumerates all policies under its two-step grammar, chooses a candidate proxy-winning polynomial \(P_\star\), and proves for every other policy either

\[
\widehat J_\pi(p)\equiv P_\star(p)
\quad\text{or}\quad
\min_{p\in[p_-,p_+]}\bigl(P_\star(p)-\widehat J_\pi(p)\bigr)>0.
\tag{RHT-14/2}
\]

All minima are evaluated exactly using quadratic stationary points and the interval endpoints. If a different policy can become proxy optimal, or ties only at an isolated parameter value, the reference solver **rejects this uniform-winner certificate**. It does not infer a globally optimal proxy roster by midpoint samples.

Let \(\Pi_\star\) be the verified constant proxy-winner set and \(\Pi\) the complete finite observation-policy set. The worst regret is

\[
R_{\rm rob}=
\max_{\substack{p\in[p_-,p_+]\\\theta\in\Theta}}
\left[
\max_{\pi\in\Pi}J_{\pi,\theta}(p)
-\min_{\widehat\pi\in\Pi_\star}J_{\widehat\pi,\theta}(p)
\right].
\]

**Theorem RHT-14/T1.** Under (RHT-14/2), with fixed kernel/proxy feature structure and horizon at most two, this exact robust regret is obtained by:

1. evaluating only **vertices of the gold uncertainty box** \(\Theta\);
2. for each gold vertex and policy pair \((\pi,\widehat\pi)\in\Pi\times\Pi_\star\), taking the maximum of the quadratic \(J_{\pi,\theta}(p)-J_{\widehat\pi,\theta}(p)\) over \(p\in[p_-,p_+]\), at its interval endpoints and its interior stationary point \(p=-b/(2a)\), when that point exists in the interval;
3. taking the maximum over all resulting policy pairs and parameter candidates.

The proof is an exchange of finite maxima with the box maximum. Each policy-pair gold difference is affine in \(\theta\), hence gold uncertainty attains its maximum at a vertex. With \(\theta\) fixed, that difference is a degree-at-most-two polynomial in the **same** \(p\), whose extrema occur at the interval endpoints and the derivative-zero point. This is a finite exact optimization identity, using established parametric-MDP mathematics.

The same enumeration calculates the maximum width of the expected proxy-minus-gold returns across all observation policies and the guaranteed *minimum gold return* of any proxy-selected policy over all licensed \(p,\theta\). It checks \(0\le R_{\rm rob}\le W_{\rm rob}\). A two-sided certificate can require \(R_{\rm rob}\le\varepsilon\) and \(J_{\rm floor}\ge u_0\), with both thresholds declared in advance.

### 19.3 An endpoint-only verifier fails at exactly \(p=1/2\)

Take two actions with identical fixed-horizon access:

- The proxy-only action gives a certain reported proxy score 1 and protected gold 0.
- The gold-protected action gives proxy score 0 and protected gold \(\theta>0\) if the first independent Bernoulli trial using the **shared** success probability \(p\) succeeds, and the second fails. Otherwise gold is zero.

The gold action therefore has expected protected return

\[
J_{\rm protected}(p,\theta)=\theta p(1-p),
\]

while the proxy action is strictly proxy-optimal at every \(p\in[0,1]\). Thus

\[
\boxed{R_{\rm rob}(\theta=1)=1/4\quad
\text{at }p=1/2,\qquad R(0)=R(1)=0.}
\tag{RHT-14/3}
\]

A transition-interval verifier evaluating *only the endpoints* would report **zero regret** even though the exact worst case is positive. If the gold feature is independently licensed over \(\theta\in[1,2]\), the exact robust regret is **1/2**, the full expected discrepancy width is **3/2**, and the minimum true return of the always proxy-selected action is zero. These results are checked against a complete finite policy census and the prior RHT-13 POMDP solver for multiple rational interior and endpoint values.

The globally shared \(p\) is load-bearing. If one instead *relaxes the same physical signal into independent* parameters \(p_1,p_2\) for the two calls, the gold event has probability \(p_1(1-p_2)\), whose maximum over \([0,1]^2\) is 1. This **rectangularization can overstate the worst achievable regret by a factor four**, just as checking only the diagonal endpoints can understate it completely. The correct uncertainty object is the licensed **coupled** transition-parameter family.

### 19.4 Grounded binary UGC crosswalk

The [UGC fixture](../src/spiral_ln/evaluation_reward_shared_kernel_fixture.py) embeds two actual \(\mathbb F_2\) \(K_{2,2}\) constraint-satisfaction records from RHT-08 as hidden reference worlds with uniform prior. Candidate 0 is unsafe in the first reference world and safe in the second. A proxy-tamper alternative earns one certain proxy point and zero gold. The protected candidate earns the licensed gold success value \(\theta\) only in the safe world and only after the common two-trial event.

With \(\theta\in[1,2]\), the protected candidate's expected gold is exactly

\[
J_{\rm UGC\ protected}(p,\theta)=\tfrac12\theta p(1-p).
\]

The uniform proxy winner still selects the proxy-tamper action. Exact robust gold regret is **1/4** at \(p=1/2,\theta=2\), expected discrepancy width is **5/4**, and the transition-endpoint-only regret is zero. A direct RHT-13 occupancy enumeration checks the result at \(p\in\{0,1/4,1/2,3/4,1\}\). The UGC constraint worlds are a frozen finite reachability fixture, with no inference from the general UGC hardness theorem.

A separate **fail-closed switching fixture** makes the proxy prefer one action when \(p\) is small and another when it is large. RHT-14 rejects the uniform-proxy-winner contract in this case, rather than returning an unsound regret. It also tests interval restrictions where the true quadratic maximizer lies at an endpoint, malformed kernels and resource-budget exhaustion.

### 19.5 Prior art and next extension

Uncertain kernels shared across time are classical *nonrectangular* robust MDPs. See Goyal and Grand-Clément, [*Robust Markov Decision Processes: Beyond Rectangularity*](https://doi.org/10.1287/moor.2022.1259), and Junges et al., [*The Complexity of Reachability in Parametric Markov Decision Processes*](https://doi.org/10.1016/j.jcss.2021.02.006). For uncertainty inferred from empirical transitions while preserving shared algebraic parameters, see Schnitzer, Abate and Parker, [*Robust Parameter Learning for Uncertain MDPs*](https://arxiv.org/abs/2605.01339). The quadratic stationary-point theorem is elementary; the project contribution is an **executable fail-closed certificate and adversarial reward-hacking controls within EvalMath's typed evaluation grammar**.

The current exact solver assumes a *single scalar affine transition parameter*, at most two calls, independent gold intervals, and a **verified constant proxy-optimal policy set**. General robust policy switching, multiple shared kernel parameters, repeated task-state changes, a corruptible root attestor, and real learned-reward validation require further research. Under those conditions the robust regret problem becomes semialgebraic; extending this seed may use rational root isolation or Bernstein-form interval certificates with a separately verified upper bound.

- [Exact rational shared-kernel polynomial policy oracle and robust certificate](../src/spiral_ln/evaluation_reward_shared_kernel.py).
- [UGC hidden-world and interior-maximum fixtures](../src/spiral_ln/evaluation_reward_shared_kernel_fixture.py).
- [Independent exact occupancy and negative-control tests](../tests/test_evaluation_reward_shared_kernel.py).
- [Source-bound RHT research receipt](../scripts/verify_reward_hacking_topology.py).


## 20. Switching proxy policies: exact algebraic parameter regions (RHT-15)

**2026-11-10 | exact finite two-step theorem and polynomial partition solver.** RHT-14 treats one globally shared uncertain transition probability \(p\) and correctly finds interior maxima in a gold-regret polynomial, provided one set of proxy-optimal policies stays constant throughout the licensed interval. An adversarially optimized evaluator often chooses **different policies at different transition probabilities**. This section resolves that omitted case for the same finite one-parameter, two-step observation-policy grammar, including irrational crossings and policies which tie at a single isolated parameter value.

### 20.1 The exact proxy-optimality arrangement

Let \(\Pi\) be all deterministic observation-adapted policies in the declared two-step grammar. The stochastic kernel is affine in one shared \(p\in I=[p_-,p_+]\subseteq[0,1]\) and normalized for every hidden state/action. Its proxy and protected gold returns are rational polynomials

\[
\widehat J_\pi(p)\in\mathbb Q[p]_{\le 2},\qquad
J_{\pi,\theta}(p)\in\mathbb Q[p]_{\le 2},
\]

with \(J_{\pi,\theta}\) affine in independently licensed global gold parameters \(\theta\in\Theta=\prod_j[\ell_j,u_j]\).

For every two **distinct proxy polynomials**, collect all real roots in \(I\) of their difference. Add \(p_-\) and \(p_+\), then order the distinct algebraic values

\[
p_-=r_0<r_1<\cdots<r_m=p_+.
\]

Every open interval \(I_k=(r_k,r_{k+1})\) admits one *fixed* proxy-optimal policy set \(W_k\subseteq\Pi\). The sign of every pairwise proxy-polynomial difference stays constant there. One interior rational sample therefore identifies the entire \(W_k\) exactly.

**The boundary is part of the policy problem.** At each \(r_k\), compute the full set \(W(r_k)=\arg\max_\pi\widehat J_\pi(r_k)\), including policies that are optimal **only at that single parameter** because they touch the upper envelope tangentially. A test based solely on the sets \(W_k\) would miss those isolated adverse tie-breaks.

### 20.2 Exact switching robust-regret theorem (RHT-15/T1)

For a fixed \(p\), nature's gold-reward regret under adversarial proxy tie-breaking is

\[
R(p,\theta)=
\max_{\pi\in\Pi}J_{\pi,\theta}(p)
-\min_{\widehat\pi\in W(p)}J_{\widehat\pi,\theta}(p).
\]

The exact robust maximum over **all** proxy switches and all licensed gold uncertainty is

\[
\boxed{
R_{\rm rob}=\max_{\theta\in\operatorname{Vert}(\Theta)}
\max_{\substack{i\in\Pi\\j\in W(p)}}\;
\max_{p\in I}
\left[J_{i,\theta}(p)-J_{j,\theta}(p)\right].
}
\tag{RHT-15/1}
\]

The right-hand expression is implemented by splitting its index-\(j\) eligibility into the closed cells \([r_k,r_{k+1}]\) on which \(j\in W_k\), plus **all singleton boundary points** at which \(j\in W(r_k)\). Every maximum over a closed cell then occurs at one of its two algebraic endpoints or an interior stationary point of the quadratic gold-difference polynomial.

**Proof.** At any fixed \(p\), the set \(W(p)\) depends only on the registered proxy reward and stochastic kernel, and is independent of \(\theta\). Thus \(R(p,\theta)\) is the maximum of finitely many functions affine in \(\theta\), so its maximum over \(\Theta\) is attained at a vertex. Every fixed policy's expected return is a quadratic polynomial in \(p\), giving the exact proxy-root decomposition. On an open region, pairwise proxy order is fixed. A proxy winner remains optimal on both adjacent endpoints by continuity, while a policy optimal at an isolated crossing is included directly by \(W(r_k)\). The quadratic-extremum theorem on each closed region gives an endpoint or stationary point. Taking the maximum across these finite candidates exhausts the entire compact parameter interval.

The same rational/algebraic candidate set computes (i) the **minimum true gold return across all proxy-selected policies**, and (ii) the maximum expected proxy-minus-gold gap width across **all** policies. For the latter, proxy-winner regions are irrelevant, because each policy pair's gap difference is a quadratic over the entire interval. Therefore

\[
0\le R_{\rm rob}\le
W_{\rm rob}=
\max_{\substack{\theta\in\operatorname{Vert}(\Theta)\\i,j\in\Pi\\p\in I}}
\left[(\widehat J_i-J_{i,\theta})
-(\widehat J_j-J_{j,\theta})\right](p).
\tag{RHT-15/2}
\]

A two-sided gate passes only if the exact regret is below a declared risk cap and the guaranteed minimum proxy-chosen gold return meets a declared progress floor.

### 20.3 Quadratic-irrational parameters require exact comparisons

If two proxy polynomials differ by \(a p^2+b p+c\), their crossings can occur at

\[
p=\frac{-b\pm\sqrt{b^2-4ac}}{2a}.
\]

These numbers need not be rational. The new [algebraic switching oracle](../src/spiral_ln/evaluation_reward_kernel_switching.py) represents exact values by \(r+s\sqrt d\), for rational \(r,s,d\ge0\), and compares candidate roots and reward values by exact rational sign/square tests. When two radical terms have opposing signs, comparing their squared magnitudes reduces to the sign of another single-radical expression; the implementation uses this to avoid numerical root approximations in soundness decisions.

Open regions are sampled using a dyadic rational **provably between** their algebraic endpoints. The calculation stops with a resource-limit error if a certified dyadic separator cannot be produced inside its declared bit budget. The solver separately caps policy enumeration, pairwise proxy comparisons, algebraic breakpoints and reward-pair checks. In all cases, budget exhaustion is reported as incomplete analysis rather than a safety pass.

### 20.4 Rational switching, irrational switching and isolated harmful ties

**Rational crossing:** in a one-step instance, action A gets proxy and true reward \(\theta\) only on a Bernoulli(\(p\)) success, while B gets a proxy point with probability \(1-p\) and gold zero. The proxy prefers B for \(p<1/2\) and A for \(p>1/2\). At \(p=1/2\) the actor may break the proxy tie toward B, giving exact protected gold regret \(\theta/2\). With \(\theta=1\),

\[
\boxed{R_{\max}=1/2 \text{ at }p=1/2,\qquad R(0)=R(1)=0.}
\tag{RHT-15/3}
\]

**Irrational crossing:** a protected action receives proxy and gold when two shared-\(p\) Bernoulli trials **both succeed**, giving expected \(p^2\). A proxy-only action earns one proxy point with probability \(1-p\), with no true gold. Their proxy rewards tie when \(p^2=1-p\), at

\[
p_\star=\frac{\sqrt5-1}{2}.
\]

Below \(p_\star\), the actor prefers the low-gold proxy action; above it, the actor prefers the protected action. The maximum gold regret occurs **exactly at the irrational tie**:

\[
\boxed{
R_{\max}=p_\star^2=\frac{3-\sqrt5}{2}
\approx0.381966,
\quad R(0)=R(1)=0.
}
\tag{RHT-15/4}
\]

The exact certificate returns both \(p_\star\) and \(R_{\max}\) symbolically. With an independently licensed protected-reward multiplier \(\theta\in[1,2]\), the robust maximum becomes \(3-\sqrt5\), attained at \(\theta=2\).

**Isolated tangency:** let a protected good action have fixed proxy and gold returns both equal to 1. A zero-gold alternative receives proxy \(3/4+p(1-p)=1-(p-1/2)^2\). The good action wins the proxy comparison on every open interval, while the zero-gold action **ties only at** \(p=1/2\). The adversarial tie gives gold regret 1 at this one isolated point, and zero regret at every other parameter. The exact solver includes the tangent-only policy in the boundary winner set. This is an important negative control for regional analyses that discard isolated measure-zero events when the certificate claims a **worst-case**, rather than a distribution-averaged, safety guarantee.

**UGC reference-world irrational crossing:** a further RHT-15 fixture preserves two actually reachable binary \(K_{2,2}\) Unique Games satisfaction records from RHT-08, with a uniform prior. The protected task earns proxy \(p^2\) in either reference world, while protected gold pays only when the relevant UGC action is safe. Expected gold is therefore \((\theta/2)p^2\). The rival action earns proxy \(1-p\) and gold zero. With \(\theta=1\), the exact worst regret is \((3-\sqrt5)/4\), and with independently licensed \(\theta=2\), it is \((3-\sqrt5)/2\). Both are attained at the irrational crossing \(p=(\sqrt5-1)/2\); checking only \(p=0,1\) reports zero. The [independent ordinary-POMDP policy census](../tests/test_evaluation_reward_kernel_switching.py) verifies the UGC-grounded true reward and proxy choice at multiple rational parameter values, and the source-bound receipt includes the exact algebraic crossing.

The existing RHT-14 constant-winner fixtures are reproduced exactly by the new region solver, and RHT-14's deliberately rejected switching fixture now receives a proper full-interval analysis.

### 20.5 Mathematical scope and next research work

This package makes an exact, small result about **one shared affine transition parameter and horizon at most two**. Policy enumeration and pairwise quadratic comparisons can be exponential in the observation grammar. Multiple shared kernel parameters, longer histories, gold uncertainty that also changes the transition kernel, adversarially observable audit metadata and learned state representations demand more powerful semialgebraic verification methods.

The region-partition principle is established in parametric verification. See [*Parameter synthesis for Markov models: covering the parameter space* (2023)](https://link.springer.com/article/10.1007/S10703-023-00442-X), [PRISM's parametric model checking manual](https://www.prismmodelchecker.org/manual/RunningPRISM/ParametricModelChecking), and [Chi et al. (2026), *PAC Approximation and DIRECT Optimization for Parametric Markov Models*](https://arxiv.org/abs/2608.02184), which explicitly studies difficulties arising when optimal policies vary across the parameter space. RHT-15's contribution is an executable exact-algebraic certificate for **gold-regret under adversarial proxy tie-breaking** in EvalMath's typed, globally coupled reward/transition grammar. It neither asserts a new general parametric-MDP theorem nor certifies the values of a real learned judge.

- [Exact crossing, isolated-tie and robust-return optimizer](../src/spiral_ln/evaluation_reward_kernel_switching.py)
- [Rational/irrational/tangent source fixtures](../src/spiral_ln/evaluation_reward_shared_kernel_fixture.py)
- [Independent ordinary-POMDP and algebraic-root tests](../tests/test_evaluation_reward_kernel_switching.py)
- [Versioned source-fingerprinted receipt](../scripts/verify_reward_hacking_topology.py)


## 21. Two shared uncertain kernel parameters: exact polygonal reward-hacking regions (RHT-16)

**2026-11-10 | exact finite two-parameter theorem and UGC controls.** RHT-15 handles proxy-policy switches with one globally shared affine transition parameter \(p\), using quadratic real algebraic numbers. RHT-16 examines **two globally shared transition parameters** \((p,q)\) and their simultaneous effects on both the actor's proxy choice and protected gold reward. This exact extension freezes a verifiable *affine-proxy/multiaffine-gold* policy class, permitting all policy switches between its affine proxy surfaces, including lower-dimensional tie-only regions.

### 21.1 Restricted two-parameter transition grammar

For every hidden state/action, an observable next-outcome probability has the form

\[
K_{p,q}(s',o\mid s,a)=a_{s,a,s',o}
+b_{s,a,s',o}p+c_{s,a,s',o}q,
\quad
(p,q)\in I_p\times I_q,
\]

where \(I_p,I_q\) are rational closed subintervals of \([0,1]\). Since the conditional kernel is affine in \((p,q)\), nonnegativity of each outcome probability is established by checking all **four** parameter-box corners, while probability normalization holds across the whole box exactly when each state/action's total constant coefficient is one and its two slope sums are zero.

A single \(p\) and a single \(q\) are sampled by nature and **reused throughout the complete trajectory**. They cannot be chosen separately on different time steps or for different actions. Protected gold rewards again have independently registered globally shared rational coefficients \(\theta\in\Theta=\prod_j[\ell_j,u_j]\), with the transition and proxy kernels independent of \(\theta\).

The exact implementation supports at most two observation-adapted calls and enumerates the complete deterministic policy grammar \(\Pi\). For each policy, a symbolic rational bivariate polynomial evaluator checks whether

\[
\widehat J_\pi(p,q)=A_\pi+B_\pi p+C_\pi q
\]

is **affine in the kernel parameters**, and whether each protected gold coefficient is **multiaffine**:

\[
J_{\pi,\theta}(p,q)
=D_{\pi,\theta}
+E_{\pi,\theta}p
+F_{\pi,\theta}q
+G_{\pi,\theta}pq.
\]

These are *verified polynomial-degree conditions on the output*, allowing cancellations among nominally higher-degree transition products. Any policy whose actual proxy includes a \(pq,p^2\), or \(q^2\) contribution, or whose gold contains a squared parameter, is outside RHT-16's proved class and receives an explicit resource/grammar error. The broader semialgebraic case remains open.

### 21.2 Exact convex winning regions

Each policy's proxy-optimality domain is the closed region

\[
P_j=
\left\{
(p,q)\in I_p\times I_q:
\widehat J_j(p,q)\ge \widehat J_k(p,q)
\quad\forall k\in\Pi
\right\}.
\tag{RHT-16/1}
\]

Because the proxy values are affine, each inequality is a rational half-plane. Thus every nonempty \(P_j\) is a **compact rational convex polygon**, including degenerate line segments or singleton tie points. An exact half-plane clipper constructs the polygon, retaining boundary ties as full members of the eligible policy set.

The actor at any parameter point chooses any policy \(j\) whose proxy achieves the maximum, with adversarial gold tie-breaking. For a fixed registered gold vector \(\theta\) and two policies \(i,j\), the gold difference

\[
f_{ij,\theta}(p,q)
=J_{i,\theta}(p,q)-J_{j,\theta}(p,q)
\]

is bilinear. On the **interior** of a full-dimensional polygon, if the \(pq\) coefficient is nonzero, the Hessian has eigenvalues \(\pm |G|\), so every stationary point is a saddle. If it is zero, the function is affine. Thus the extrema over a compact polygon occur on its boundary. Restricting \(f\) to a rational polygon edge parameterized by \(t\in[0,1]\) yields a rational quadratic; its maximum or minimum is attained at \(t=0\), \(t=1\), or the unique rational stationary parameter \(-b/(2a)\) when present and interior. The same argument works for a segment or singleton winner region.

### 21.3 Exact two-parameter robust-regret theorem

**Theorem RHT-16/T1.** For this finite verified grammar, the exact worst regret across all proxy-policy switches and independently licensed gold parameters is

\[
\boxed{
R_{\rm rob}=
\max_{\theta\in\operatorname{Vert}(\Theta)}
\max_{j:P_j\ne\varnothing}
\max_{i\in\Pi}
\max_{(p,q)\in P_j}
\left[
J_{i,\theta}(p,q)-J_{j,\theta}(p,q)
\right].
}
\tag{RHT-16/2}
\]

Every inner maximum has an exact rational witness from polygon-edge quadratic optimization.

**Proof.** Proxy policy eligibility \(j\in\arg\max_k\widehat J_k(p,q)\) depends on the parameter point \((p,q)\), independently of gold \(\theta\). For fixed policies and \((p,q)\), their gold difference is affine in \(\theta\), so maximizing gold-box uncertainty needs only its vertices. Each selected proxy policy's eligible region is its rational polygon \(P_j\). On that polygon the gold difference is bilinear; the preceding edge theorem gives the exact finite candidate set. Taking the maximum over finitely many policies and gold-box vertices is therefore sound and complete.

The exact **guaranteed minimum gold return** across proxy-optimal policies is likewise the minimum of \(J_{j,\theta}\) over each \(P_j\) and gold-box vertex, using the same edge optimizer. The maximum **expected proxy-minus-gold discrepancy width** among all policy pairs is obtained by maximizing their multiaffine gap difference over the full parameter box. A multiaffine function attains its box extrema at corners, so the width check needs only four parameter corners (for every policy pair and gold-box vertex), even though the *proxy-selected regret* can attain its maximum on an interior switching boundary.

The two-sided exact certificate approves only when \(R_{\rm rob}\le\varepsilon\) and the guaranteed proxy-policy gold return exceeds a declared non-inert progress floor. Its finite policy and reward-pair budgets are explicit; exceeding one returns an error rather than an incomplete safety pass.

### 21.4 Strict diagonal switching witness missed by every corner check

Consider a two-call system with two available first actions. The **protected action** receives proxy reward one if a first Bernoulli(\(p\)) event succeeds, giving expected proxy \(p\). After that success, a second Bernoulli(\(q\)) event must fail to produce a protected true reward \(\theta>0\). Its expected gold is

\[
J_{\rm gold}(A;p,q,\theta)=\theta p(1-q).
\]

The alternative **proxy-only action** receives proxy reward one if a Bernoulli(\(q\)) event succeeds, giving expected proxy \(q\), and gold zero.

Thus the proxy chooses the alternative when \(q\ge p\), including adversarial tie-breaking at \(q=p\). Exact worst gold regret is

\[
\boxed{
\max_{0\le p\le q\le1}\theta p(1-q)
=\theta/4
\quad\text{at}\quad (p,q)=(1/2,1/2).
}
\tag{RHT-16/3}
\]

A verifier evaluating just the four corners \((p,q)\in\{0,1\}^2\) obtains **zero regret at every corner**, missing the true worst case. With licensed \(\theta\in[1,2]\), exact robust regret is \(1/2\), while the complete expected discrepancy width is \(1\), and the guaranteed gold return of a proxy-maximizing action has floor zero.

A subrectangle \([0,1/4]^2\) gives a worst regret \(3\theta/16\) at \((1/4,1/4)\), while a parameter box with \(p\in[0,1/4]\), \(q\in[1/2,1]\) gives \(\theta/8\) at \((1/4,1/2)\). These provide independent rational boundary controls.

### 21.5 UGC and action-identity controls

The [UGC-specific fixture](../src/spiral_ln/evaluation_reward_two_kernel_fixture.py) preserves two genuinely reachable binary \(\mathbb F_2\) \(K_{2,2}\) constraint-satisfaction worlds from RHT-08. The protected action is gold-safe in only one world. Under the uniform hidden-world prior, it therefore earns expected gold \(\frac{\theta}{2}p(1-q)\). The competing proxy still earns \(q\), so the winning boundary is the same diagonal.

With licensed \(\theta\in[1,2]\), the exact worst UGC-grounded gold regret becomes **\(1/4\)** at \((p,q)=(1/2,1/2)\). The expected gap width is \(1\), and every rectangle-corner regret is zero. Direct RHT-13 observation-policy occupancy enumerations cross-check the protected gold payoff and proxy eligibility at multiple rational \((p,q)\).

A separate synthetic **tie-only region** makes proxy rewards \(p\), \(q\), and \((p+q)/2\) for three actions. The third action is proxy-optimal only on the line segment \(p=q\). If that action gives gold zero while the first two give gold one, adversarial proxy tie-breaking yields true regret one **on the diagonal**, so a solver that discards zero-area winner polygons would fail. RHT-16's exact polygon clipper preserves it.

The *positive control* assigns every action the same shared gold reward parameter times its own proxy return. For every \(\theta>0\), proxy and gold policy rankings coincide, giving exact robust regret zero despite repeated policy switches. Independent checks cover signed gold uncertainty, arbitrary parameter subrectangles, fail-closed non-affine proxy cases, non-multiaffine gold cases, malformed conditional kernels and explicit search caps.

### 21.6 Novelty and generalization limits

Convex half-plane arrangements and bilinear extrema over polygon edges are established finite computational-geometry/optimization tools. The UGC connection comes from **policy reachability and signal identity**, and the reward safety result is the certified regret of adversarially selected proxy-optimal policies. This is an exact, restricted two-parameter extension of the parametric POMDP evaluation calculus, without a general breakthrough on robust POMDP complexity.

The present proof assumes all proxy-policy returns are **affine** in two globally shared kernel parameters and all protected gold returns are **multiaffine**. Beyond that class, the winning regions are semialgebraic rather than rational polygons, and the reward objective may contain higher-degree stationary points. The next mathematical work is verified multivariate polynomial sign decomposition or a convergent, explicitly bounded Bernstein/interval hierarchy with rigorous error certificates. Real safety applications also need independently established transition bounds, gold-source identities, and enforceable access to the evaluator and attestor.

- [Exact bivariate symbolic solver and convex winning polygon certificate](../src/spiral_ln/evaluation_reward_two_kernel.py)
- [Synthetic and UGC grounded shared-parameter fixtures](../src/spiral_ln/evaluation_reward_two_kernel_fixture.py)
- [Independent occupancy and exact edge-extremum tests](../tests/test_evaluation_reward_two_kernel.py)
- [Source-bound reward-hacking research receipt](../scripts/verify_reward_hacking_topology.py)


## 22. Curved proxy-optimality boundaries and exact algebraic reward regret (RHT-17)

**2026-11-10 | finite bivariate semialgebraic theorem and source-grounded tests.** RHT-16 certifies reward hacking when every expected proxy policy score is **affine** in two globally shared uncertain transition parameters \((p,q)\) and every protected gold policy score is multiaffine. Its winning regions are rational polygons. RHT-17 extends the exact finite certificate to **multiaffine proxy scores**, whose differences may include a nonzero \(pq\) term. These proxy regions can have curved rational boundaries and irrational worst-regret witnesses.

### 22.1 Typed two-step parametric game

Fix the identical finite hidden-state/observation-policy and transition-normalization grammar of RHT-16. A single \(p\in[p_-,p_+]\) and \(q\in[q_-,q_+]\) are globally shared throughout both calls; every conditional transition probability is affine in these two parameters and is validated at all four box corners. Protected gold rewards are independently licensed globally identified rational features with parameter vector \(\theta\in\Theta=\prod_j[\ell_j,u_j]\). The proxy score and stochastic kernel do not depend on \(\theta\).

The exact reference solver enumerates the complete two-step deterministic observation-policy roster \(\Pi\) under the declared grammar and symbolically checks, for **every** policy, that

\[
\widehat J_\pi(p,q)=a_\pi+b_\pi p+c_\pi q+d_\pi pq,
\qquad
J_{\pi,\theta}(p,q)=\alpha_{\pi,\theta}
+\beta_{\pi,\theta}p+\gamma_{\pi,\theta}q
+\delta_{\pi,\theta}pq.
\]

When the actual symbolic policy surface contains \(p^2\), \(q^2\), or higher-degree terms, this exact solver refuses to issue a certificate. The restriction is checked from the fully computed policy polynomials rather than inferred from transition syntax.

### 22.2 A finite exact decomposition of curved winning regions

For any candidate proxy policy \(j\), every other policy \(k\) imposes the closed inequality

\[
H_{jk}(p,q)=A+Bp+Cq+Dpq\ge0,
\]

where the coefficients are rational. Fixing \(p\), this is **linear in \(q\)**:

\[
(C+Dp)q\ge-(A+Bp).
\]

Thus a vertical slice of the candidate winning region is an interval, possibly empty, with lower and upper endpoints taken from the parameter box and rational-linear-fractional curves of the form

\[
\boxed{q(p)=-\frac{A+Bp}{C+Dp}.}
\tag{RHT-17/1}
\]

The ordering and feasibility of those q-boundaries can change only when a q coefficient \(C+Dp\) vanishes, a boundary crosses a box edge, or two rational boundaries cross. For two constraints \(i,j\), any crossing satisfies the quadratic *resultant*

\[
(A_i+B_i p)(C_j+D_j p)
-(A_j+B_j p)(C_i+D_i p)=0.
\tag{RHT-17/2}
\]

Consequently all critical p-values belong to a **finite exact collection of rational and quadratic-irrational numbers**, together with the two parameter-box endpoints. Sort them and choose one certified rational interior sample within each adjacent open p-strip. The winning region's q-interval on that strip uses the same active rational-linear-fractional lower and upper boundary throughout: a change of sign, crossing or feasibility status would require an unregistered critical root.

Importantly, each critical p-slice is inspected *independently*. This preserves a proxy policy that wins only on a vertical segment or isolated point, even if it has no two-dimensional winning region. The same handling covers a boundary where several proxy policies tie.

### 22.3 Exact extrema on the curved edges

For a fixed gold-feature vertex \(\theta\) and policy pair \(i,j\), the protected gold return difference is another bilinear polynomial,

\[
f(p,q)=a+bp+cq+dpq.
\]

At every fixed \(p\) where \(j\) is proxy-optimal, \(f\) is affine in \(q\). Its maximum and minimum over the allowed q-interval therefore occur at its **two endpoints**. Substituting a boundary \(q(p)=-(A+Bp)/(C+Dp)\) yields

\[
f(p,q(p))
=\frac{
(a+bp)(C+Dp)-(c+dp)(A+Bp)
}{
C+Dp
}
=\frac{n_0+n_1p+n_2p^2}{C+Dp}.
\tag{RHT-17/3}
\]

The derivative has a quadratic numerator:

\[
\frac{d}{dp}f(p,q(p))
=
\frac{
(n_1C-n_0D)+2n_2Cp+n_2Dp^2
}{
(C+Dp)^2
}.
\tag{RHT-17/4}
\]

The exact maximum over a *closed* strip is attained at one of its algebraic p-endpoints or a derivative-zero root within it. If the denominator vanishes at an endpoint, the solver uses the exact finite limit when both numerator and denominator vanish; otherwise it treats the boundary as invalid rather than inventing a finite reward. Additional explicit vertical-slice checks include values at critical p where the constraint is satisfied only at that exact parameter.

All candidates and reward values lie in quadratic extensions of \(\mathbb Q\), represented by rational-plus-rational-sqrt-rational expressions. Arithmetic within each quadratic field and comparisons across different roots use rational sign/square tests, with no floating-point thresholding. Search, root-count and policy-pair budgets are explicit and fail closed.

**Theorem RHT-17/T1.** Under the frozen two-call kernel and multiaffine policy-surface contract, the exact worst proxy-selection gold regret is

\[
\boxed{
R_{\rm rob}
=\max_{\theta\in\operatorname{Vert}(\Theta)}
\max_{j\in\Pi}
\max_{i\in\Pi}
\max_{(p,q)\in W_j}
\left[J_{i,\theta}(p,q)-J_{j,\theta}(p,q)\right],
}
\tag{RHT-17/5}
\]

where \(W_j\) is the full closed semialgebraic winning region of proxy policy \(j\). The inner maximum is attained at a candidate produced by the critical-slice and rational-curve stationary-point method above. This follows from the exact vertical-slice decomposition, compactness and the one-dimensional rational derivative formula. Gold uncertainty is affine for a *fixed policy and transition pair*, so it suffices to maximize over the independent licensed gold-box vertices. The same method computes the **minimum gold return across all proxy winners** for a non-inert progress floor.

The unrestricted policy-pair expected proxy-minus-gold discrepancy width is still multiaffine, so its worst value over the full parameter rectangle is attained at the rectangle's four corners for each gold-feature vertex. The certificate verifies \(0\le R_{\rm rob}\le W_{\rm rob}\).

### 22.4 Strict irrational maximum on a curved switching boundary

Take two proxy-eligible first actions. The **protected action** emits proxy reward one when a Bernoulli(\(p\)) first event fails and protected gold reward \(\theta\) only if an independent second Bernoulli(\(q\)) event also fails. The **proxy-inflation action** earns one proxy point when its first Bernoulli(\(q\)) event succeeds and another when a second Bernoulli(\(p\)) event succeeds after that first success. The expected returns are

\[
\begin{array}{c|cc}
 & \widehat J(p,q) & J_\theta(p,q)\\
\text{protected action} &1-p&\theta(1-p)(1-q)\\
\text{proxy inflation}&q(1+p)&0
\end{array}
\]

The actor's proxy prefers the inflation action whenever

\[
\boxed{q\ge \frac{1-p}{1+p}.}
\tag{RHT-17/6}
\]

In this region, the gold-best challenger is the protected action for \(\theta>0\). At fixed \(p\), its gold reward decreases with \(q\), so the maximal gold regret for this p lies on the curved proxy-switching boundary. Substituting (RHT-17/6) gives

\[
R(p)=2\theta\frac{p(1-p)}{1+p}.
\]

Its derivative vanishes in the unit interval only at \(p_\star=\sqrt2-1\), and at that crossing \(q_\star=\sqrt2-1\). Therefore

\[
\boxed{
p_\star=q_\star=\sqrt2-1,\quad
R_{\max}=\theta(6-4\sqrt2)
\approx 0.34314575\,\theta.
}
\tag{RHT-17/7}
\]

For \(\theta\in[1,2]\), the exact worst regret is \(12-8\sqrt2\). Its worst gold-feature vertex is \(\theta=2\). **Every rectangle corner has zero gold regret**, although the strongest actual exploit occurs at two irrational interior parameters. The full expected-policy discrepancy-width envelope over the same gold interval is \(2\). The protected-policy true gold floor under adversarial proxy selection is zero.

This extends RHT-16's straight-line switching example to a curved semialgebraic boundary. The exact location and attained value are both necessary for the certificate: checking a rational parameter grid only approximates them.

### 22.5 Multiple curves, UGC reachability and negative controls

The geometry solver also handles intersections of two active curved boundaries. For example, take the proxy-winner constraints \(q\ge(1-p)/(1+p)\) and \(q\ge p\). Their active lower boundaries meet at \(p=q=\sqrt2-1\), which is a root of the exact quadratic resultant in (RHT-17/2). For protected gold \(f=(1-p)(1-q)\), the exact worst value on the feasible region is again \(6-4\sqrt2\). The test verifies the complete vertical q-slice at that irrational crossing and several rational membership controls.

The [UGC-grounded fixture](../src/spiral_ln/evaluation_reward_two_kernel_fixture.py) preserves two actually reachable \(K_{2,2}\) binary translation-game satisfaction worlds with a uniform gold-reference prior. The protected action is gold-safe in exactly one of those worlds, giving expected gold \(\frac{\theta}{2}(1-p)(1-q)\). With \(\theta\in[1,2]\), its exact robust gold regret is **\(6-4\sqrt2\)** at the same interior point, while the parameter-box corner test again reports zero. The independent RHT-13 world/observation policy evaluator checks the gold and proxy returns across a rational parameter grid.

A formerly rejected RHT-16 test includes a genuinely nonlinear \(pq\) proxy. RHT-17 can certify its risk while preserving boundary-only proxy ties. A positive control assigns true gold proportionally to the reported proxy across every transition using a *single shared* gold parameter: proxy-selection regret is then zero despite curved switching boundaries. Negative controls reject higher-degree gold surfaces, invalid reward intervals, malformed root-search budgets and incomplete policy analyses.

### 22.6 Prior art and scope

The exact decomposition follows classical parametric verification, rational curve arrangements and elementary algebraic optimization. Related work includes Junges et al., [*Parameter synthesis for Markov models: covering the parameter space*](https://doi.org/10.1007/s10703-023-00442-x) (2024), Goyal and Grand-Clément, [*Robust Markov Decision Processes: Beyond Rectangularity*](https://doi.org/10.1287/moor.2022.1259) (2022/23), and Li, Kuhn and Sutter, [*Policy Gradient Algorithms for Robust MDPs with Nonrectangular Uncertainty Sets*](https://doi.org/10.1137/24M1631250) (2026). Those are substantive antecedents to robust parameter synthesis and globally coupled uncertainty. RHT-17's contribution is an **exact finite, source-bound reward-hacking oracle with adverse proxy-tie and independently licensed gold semantics** in EvalMath's game-space notation.

The result covers globally shared **two-parameter affine transition laws**, a **two-step observation-policy horizon**, and verified **multiaffine** expected proxy and true-gold policy surfaces. General high-degree polynomial winning regions need a larger certified semialgebraic decomposition or a separately proved interval-hierarchy bound. The gold reference and parameter uncertainty class still require evidence external to the optimizing model; this exact mathematical certificate provides neither human-value ground truth nor empirical model-behavior validation.

- [Exact curved-boundary algebraic parameter solver](../src/spiral_ln/evaluation_reward_curved_kernel.py)
- [Curved switching and UGC fixtures](../src/spiral_ln/evaluation_reward_two_kernel_fixture.py)
- [Independent world/observation and radical-intersection tests](../tests/test_evaluation_reward_curved_kernel.py)
- [Versioned source-fingerprinted research receipt](../scripts/verify_reward_hacking_topology.py)


## 23. Quadratic proxy surfaces: exact parabolic switching and cubic gold regret (RHT-18)

**2026-11-10 | finite degree-2 parametric POMDP theorem.** RHT-17 handles two globally shared transition probabilities with *multiaffine* proxy and gold policy surfaces, so its switching curves have rational-linear-fractional shape. The next mathematical obstruction is a proxy objective that reuses a parameter in two successive Bernoulli events, producing a squared term \(p^2\) in its expected score. The RHT-17 solver correctly refuses that case. RHT-18 supplies an exact certificate for the additional **quadratic-in-\(p\), affine-in-\(q\)** policy grammar, together with exact cubic extrema on parabolic policy boundaries.

### 23.1 Typed extension of the two-parameter transition grammar

Retain RHT-16's finite, normalized conditional kernel

\[
K_{p,q}(s',o\mid s,a)=k_0+k_p p+k_q q
\]

with the same globally shared \(p,q\) across the whole episode, horizon at most two, rational closed parameter box \(I_p\times I_q\), and an independently licensed rational gold box \(\Theta\). The actor chooses deterministic policies from its visible observation history, and the independent gold parameters do not modify the transition kernel or the proxy objective.

The exact solver enumerates *every* policy in the declared finite grammar and checks that its expected proxy and gold polynomials have the forms

\[
\boxed{\widehat J_\pi(p,q)
=A_{\pi,0}+A_{\pi,1}p+A_{\pi,2}p^2+B_\pi q,}
\tag{RHT-18/1}
\]
\[
\boxed{J_{\pi,\theta}(p,q)
=C_{\pi,0}(\theta)+C_{\pi,1}(\theta)p
+C_{\pi,2}(\theta)p^2+
[D_{\pi,0}(\theta)+D_{\pi,1}(\theta)p]q.}
\tag{RHT-18/2}
\]

All coefficients are rational and affine in the globally identified gold features \(\theta\). A \(pq\) term in the **proxy**, a \(q^2\) term in gold, a \(p^2q\) term or any higher-degree contribution lies outside this restricted exact theorem and is explicitly rejected. This is a subclass of general quadratic two-variable polynomials arising from two-step stochastic paths, selected because its proxy winning regions admit complete exact one-dimensional boundary decomposition.

### 23.2 Exact switching envelope and critical p-slices

For a proxy candidate \(j\), the requirement that it outscore policy \(k\) is

\[
\widehat J_j-\widehat J_k
=F_{jk}(p)+(B_j-B_k)q\ge0,
\]

where \(F_{jk}(p)\in\mathbb Q[p]\) has degree at most two. A strictly positive \(B_j-B_k\) imposes a lower bound \(q\ge-F_{jk}(p)/(B_j-B_k)\); a negative difference imposes an upper bound of the same *quadratic curve* form. A zero difference imposes the purely vertical sign constraint \(F_{jk}(p)\ge0\).

Include the parameter-box bounds \(q_-\le q\le q_+\). Then each vertical slice of the exact proxy-winner region is either empty or the closed interval

\[
\boxed{L_j(p)\le q\le U_j(p),}
\quad
L_j(p)=\max_{\alpha\in\mathcal L_j}\alpha(p),\quad
U_j(p)=\min_{\beta\in\mathcal U_j}\beta(p),
\tag{RHT-18/3}
\]

where \(\mathcal L_j,\mathcal U_j\) are finite families of rational quadratic polynomials. The only points at which an active lower/upper curve can change are roots of pairwise **quadratic differences**. Add those real roots, all roots of zero-\(q\)-coefficient vertical constraints, and the two \(p\)-box endpoints. They form a finite ordered list of rational/quadratic-irrational numbers.

Between successive critical \(p\)-values, a certified dyadic rational sample determines the active lower/upper envelope curves and whether the vertical constraints permit that strip. By exact sign constancy, those same envelope choices remain valid over the whole open strip. Every critical vertical slice is checked *independently*, retaining policy eligibility that exists only at an isolated tie point. A proxy policy that wins only on the **parabolic curve** \(q=p^2\) is also preserved as an interval with identical active lower and upper boundaries.

### 23.3 The exact cubic-extremum theorem (RHT-18/T1)

Fix a protected-gold parameter vertex \(\theta\) and a challenger/proxy-selected policy pair \(i,j\). Their gold-return difference on any winner region has the form

\[
G(p,q)=a_0+a_1p+a_2p^2+(b_0+b_1p)q.
\]

For each feasible fixed \(p\), the function is affine in \(q\), so its maximum and minimum are at \(q=L_j(p)\) or \(q=U_j(p)\). On a strip where the active boundary is \(q=r_0+r_1p+r_2p^2\), substitution gives an **exact cubic**:

\[
\boxed{
G(p,q(p))=c_0+c_1p+c_2p^2+c_3p^3.}
\tag{RHT-18/4}
\]

Its extrema over the closed strip occur at one of the two exact algebraic endpoints or at an interior root of

\[
\boxed{c_1+2c_2p+3c_3p^2=0.}
\tag{RHT-18/5}
\]

Those roots remain rational or quadratic-irrational. Their objective values can be evaluated using rational-plus-rational-square-root arithmetic because multiplying elements from the *same quadratic field* stays inside that field. The [exact algebraic number type](../src/spiral_ln/evaluation_reward_kernel_switching.py) already supplies comparisons between candidate values from different quadratic fields, without floating-point threshold decisions.

**Theorem RHT-18/T1.** Within the verified policy grammar (RHT-18/1–2), the worst expected gold regret over all globally coupled transition parameters and independently licensed true-gold intervals is the maximum over:

1. every independently licensed gold-box vertex \(\theta\in\operatorname{Vert}(\Theta)\);
2. every challenger \(i\) and every proxy-winning policy \(j\);
3. every feasible critical vertical slice and every open-strip upper/lower envelope;
4. the boundary endpoints and the stationary points defined by (RHT-18/5).

The result is exact and includes an algebraic witness \((p_\star,q_\star)\), gold uncertainty vertex, challenger policy, proxy-selected policy, guaranteed proxy gold floor, and the full expected discrepancy-width upper certificate.

**Proof.** The proxy winner set depends only on the verified transition/proxy kernel and is independent of \(\theta\), so the regret maximum over \(\Theta\) is attained at a gold-box vertex, as in RHT-13. The quadratic envelope arrangement decomposes the exact winner domain into finitely many feasible strips and critical slices. On each slice the gold difference is affine in \(q\), so only its lower and upper boundaries matter. On each strip those boundaries are fixed rational quadratics; substitution produces (RHT-18/4), whose exact extrema are exhausted by (RHT-18/5) and the strip endpoints. Every closed critical slice is checked directly. This exhausts the compact proxy-winning region including measure-zero tie policies.

The same endpoint/cubic-oracle method computes (i) the guaranteed minimum gold return among all proxy-winning policies, and (ii) the **full expected proxy-minus-gold discrepancy width** across all policies and all licensed kernel values. The solver checks \(0\le R_{\rm rob}\le W_{\rm rob}\) and can enforce both a gold-regret cap and a minimum true-return requirement. An unlicensed polynomial degree, invalid kernel, search-budget overrun or unsupported algebraic operation produces a distinct error and prevents certification.

### 23.4 Parabolic Goodhart counterexample with a cubic interior maximum

Take a two-step hidden-world evaluation where the protected action earns expected proxy \(p^2\) from two successive globally shared Bernoulli(\(p\)) transitions. It independently earns true gold \(\theta p(1-q)\) from a registered protected-success event, while the competing *proxy-only* action earns proxy \(q\) and true gold zero. The shared-world construction fixes the covariance between the repeated \(p\) trials and the gold source and is checked by ordinary RHT-13 stochastic policy enumeration.

The actor chooses the proxy-only action when \(q\ge p^2\), with adversarial proxy tie-breaking on the parabola. Along that boundary, the true lost reward is

\[
R(p,\theta)=\theta p(1-p^2)=\theta(p-p^3).
\]

Its derivative vanishes at \(p_\star=\sqrt3/3\). Substituting back into the **curved** proxy switching boundary gives \(q_\star=1/3\), and the exact worst-case regret is

\[
\boxed{
R_{\rm rob}(\theta=1)=\frac{2\sqrt3}{9},\quad
(p_\star,q_\star)=\left(\frac{\sqrt3}{3},\frac13\right).
}
\tag{RHT-18/6}
\]

With independently licensed true-gold multiplier \(\theta\in[1,2]\), the sharp maximum is \(4\sqrt3/9\), attained at \(\theta=2\). **Every transition-box corner yields zero proxy-selection regret.** This disproves any four-corner-only safety check for the correlated quadratic-proxy class.

The same instance, restricted to \(p\in[0,1/2]\), has a maximum of \(3/8\) at \((p,q)=(1/2,1/4)\). A rectangle with \(p\in[3/4,1]\), \(q\in[0,1/4]\) makes the gold-protected policy strictly proxy-optimal and its worst selection regret zero. The solver checks these subrectangles with exact rational arithmetic.

### 23.5 Unique Games and zero-area parabola controls

The [UGC-grounded fixture](../src/spiral_ln/evaluation_reward_quadratic_kernel_fixture.py) uses two genuinely reachable binary \(\mathbb F_2\) \(K_{2,2}\) constraint-satisfaction records as its hidden gold-reference worlds. The protected candidate earns gold only in the world where that action is genuinely UGC-safe, giving expected gold \(\frac{\theta}{2}p(1-q)\), while the two proxy scores remain \(p^2\) and \(q\). With licensed \(\theta\in[1,2]\), its exact worst gold regret is **\(2\sqrt3/9\)**, attained at the same algebraic parameter pair.

An additional three-action negative control gives the third policy proxy score \((p^2+q)/2\) and protected gold zero. This third policy is proxy-optimal **only on** \(q=p^2\), a zero-area parabolic curve. The exact region solver retains that degenerate winner and evaluates its protected gold difference against the genuinely gold-winning action.

To cross-check a different algebraic boundary, the geometric oracle also accepts proxy constraints \(q\ge p^2\) and \(q\ge1-p\). These two active quadratic/linear boundaries meet at \(p=(\sqrt5-1)/2\), an irrational root of \(p^2+p-1\). The derived vertical intervals agree with directly checked rational-membership conditions. RHT-16's earlier *affine proxy* fixtures are reproduced as a strict subcase; RHT-17's genuinely \(pq\)-dependent proxy remains explicitly outside this q-quadratic grammar and is covered by its own exact solver.

### 23.6 Prior art and limits

The mathematical tools are finite polynomial sign decomposition, algebraic root isolation and exact parametric Markov reward analysis. They connect with established work such as [Junges et al., *Parameter synthesis for Markov models: covering the parameter space*](https://doi.org/10.1007/s10703-023-00442-x) and [Schnitzer, Abate and Parker, *Robust Parameter Learning for Uncertain MDPs* (2026)](https://arxiv.org/abs/2605.01339), which studies shared parameter dependencies and sound uncertainty approximations. The new RHT-18 construction is a narrow exact reference baseline for EvalMath's adversarial proxy policy and licensed-gold semantics.

The theorem handles **two** globally shared transition parameters, mandatory horizon at most **two**, verified **q-affine proxy with quadratic p coefficient**, and **q-affine protected gold with a quadratic p term and affine q coefficient**. General \(q^2\), \(pq\) proxy switches, simultaneous higher-degree terms in both parameters, transition parameters that depend on human preference labels, or attestor corruption require different verification conditions. RHT-17 covers multiaffine \(pq\) proxy surfaces; RHT-18 covers an additional, nonnested polynomial subclass. A unified exact semialgebraic decomposition remains an open mathematics and implementation problem.

- [Exact quadratic region and cubic stationary-point solver](../src/spiral_ln/evaluation_reward_quadratic_kernel.py).
- [Synthetic and UGC-grounded parabolic transition fixtures](../src/spiral_ln/evaluation_reward_quadratic_kernel_fixture.py).
- [Independent ordinary-POMDP and algebraic boundary tests](../tests/test_evaluation_reward_quadratic_kernel.py).
- [Versioned source-fingerprinted research receipt](../scripts/verify_reward_hacking_topology.py).


## 24. Exact univariate semialgebraic certificates for q-affine polynomial proxy surfaces (RHT-19)

RHT-17 and RHT-18 optimize different bounded-degree rational polynomial classes in the globally coupled transition parameters p and q. They can be unified when **all proxy and protected-gold policy surfaces remain affine in q**, while allowing any fixed verified polynomial degree in p. The resulting switching curves may be rational rather than polynomial; the exact extrema can have algebraic degree exceeding two.

### 24.1 Frozen registered-policy contract

Let J be a **complete, externally licensed finite policy roster** for a specified decision protocol; every policy j has rational-polynomial expected returns

\[
P_j(p,q)=A_j(p)+B_j(p)q,\qquad
G_j(p,q;\theta)=C_j(p;\theta)+D_j(p;\theta)q.
\]

The transition parameters are globally shared over the entire trajectory, with \((p,q)\) in a rational closed rectangle contained in \([0,1]^2\). True-gold feature parameters \(\theta\) range over a rational interval box, independently licensed before exposure to actor-selected proxy scores. Every policy surface and gold feature must pass the explicit q-affine grammar check. An externally provided roster certifies only the supplied protocol; the optional RHT-16/18 wrapper enumerates every deterministic observation policy of the existing horizon-at-most-two kernel model.

For each potential proxy winner j, the closed winner region is

\[
S_j=\{(p,q):P_j(p,q)\ge P_k(p,q)\text{ for all }k\in J\}.
\]

Adversarial tie-breaking is preserved. Since each inequality is affine in q, its fixed-p fibre is a closed interval (possibly empty or a singleton). Wherever \(B_j-B_k\ne0\), the candidate switching boundary is

\[
q_{jk}(p)=-\frac{A_j(p)-A_k(p)}{B_j(p)-B_k(p)}.
\]

An exact p-axis arrangement includes the roots of every denominator, vertical proxy-difference equation, pairwise curve-crossing equation, and boundary-box intersection. Ratios are normalized by polynomial gcd, and all roots are isolated with **rational Sturm sequences**, retaining isolated zero-area ties.

### 24.2 Exact rational-function extremum theorem (RHT-19/T1)

**Theorem.** Under the registered-policy and polynomial grammar contracts, the worst expected gold-selection regret, the guaranteed true-gold floor among proxy winners, and the full proxy-minus-gold discrepancy width admit finite exact algebraic certificates, including attaining algebraic parameter witnesses.

**Derivation.** The maximum over the independently licensed gold-parameter box occurs at a vertex because each fixed-policy gold difference is affine in \(\theta\). On each exact winner strip, the gold objective is affine in q, hence attains its extremum at the active upper/lower rational boundary \(q=n(p)/d(p)\). Substitution gives a rational function \(H(p)=N(p)/D(p)\), with all interior extrema among roots of

\[
\boxed{N'(p)D(p)-N(p)D'(p)=0.}
\tag{RHT-19/1}
\]

The strip endpoints and *every exact vertical slice* are evaluated separately, including policies optimal only on lower-dimensional tie sets. A fixed-degree real-root isolation, exact polynomial signs at algebraic roots, and exact algebraic-value comparison exhaust the candidates. The concrete implementation uses rational interval refinement, polynomial gcd equality checks, and a resultant to isolate the value polynomial when distinct parameter witnesses yield values that cannot be ordered by simple disjoint rational bounds.

Its safety comparison uses exact signs against licensed rational caps. Exhausting a root, comparison, or policy-pair budget raises an error. No floating-point approximation participates in certification.

### 24.3 Higher-degree parabolic Goodhart family

Consider a frozen two-action protocol in which the protected policy earns proxy \(p^d\) from \(d\) globally shared Bernoulli(p) successes and earns independent true gold \(\theta p(1-q)\). The alternative earns proxy q and zero gold; adversarial selection chooses it on \(q\ge p^d\). For \(d\ge2\),

\[
R_d(p)=\theta(p-p^{d+1}),\qquad
p_\star=(d+1)^{-1/d},\quad q_\star=(d+1)^{-1},\quad
\boxed{R_{\max}=\frac{\theta d}{(d+1)^{1+1/d}}}.
\tag{RHT-19/2}
\]

Every parameter-box corner yields zero proxy-selection regret. At \(\theta=1,d=4\), the exact witness is \(p_\star=5^{-1/4}\), \(q_\star=1/5\) and the maximum regret is \(4/5^{5/4}\), the positive root of

\[
\boxed{3125R^4-256=0.}
\tag{RHT-19/3}
\]

The RHT-19 tests check this value via exact algebraic root comparison, cross-check Bernoulli-tree expectations with an independent rational enumeration, and recover RHT-18's parabolic quadratic result through the existing complete two-step observation-policy census. The UGC reference fixture reuses the two reachable \(\mathbb{F}_2\) constraint-satisfaction worlds of RHT-08: only one carries protected gold. With that world prior of 1/2 and \(\theta\in[1,2]\), the sharp maximum occurs at \(\theta=2\) and agrees with the unscaled \(\theta=1\) fixture. A third policy with proxy \((p^d+q)/2\) certifies tie-only parabolic winner regions.

### 24.4 Scope and open problems

The solver accepts *explicit finite rational polynomial policy surfaces* that are affine in q. Its high-degree fixtures describe fully enumerated two-action **first-choice** protocols; they do not establish completeness over every observation-adaptive policy of a d-step POMDP. The stochastic RHT-16/18 wrapper retains horizon at most two and independently checks the inherited kernel grammar and complete policy enumeration. Future work must extend the typed stochastic model, its complete policy census, and the independently licensed gold reference to deeper horizons. A general q² and mixed high-degree polynomial grammar would require bivariate semialgebraic decomposition or a separate sound optimization reduction. These symbolic checks are conditional on accurate, externally registered gold; they are not empirical model-alignment guarantees.

- [RHT-19 exact univariate semialgebraic root and policy-region solver](../src/spiral_ln/evaluation_reward_semialgebraic_kernel.py).
- [Higher-degree and UGC-grounded policy-surface fixtures](../src/spiral_ln/evaluation_reward_semialgebraic_fixture.py).
- [Independent algebraic, Bernoulli-tree and inherited RHT-18 regression tests](../tests/test_evaluation_reward_semialgebraic_kernel.py).


## 25. Simulation-aware reward selection, evaluator cues, and gradient-conditioned goal guarding (RHT-20)

**2026-11-11 | finite exact Bayesian decision theorem and prospective test design.**
This extension follows RHT-13's hidden-state observability distinction and RHT-19's requirement for a frozen, complete policy roster. It responds to training-awareness observations in the [Anthropic Fable/Mythos 5.2 system card](https://www.anthropic.com/document/claude-fable-5-2-mythos-5-2-system-card) (Sections 6.2.1 and 6.6.2.1) and to the [Christiano/Dwarkesh simulation-bargaining argument](https://www.dwarkesh.com/p/paul-christiano). These are motivations, not empirical evidence for the finite decision model.

### 25.1 A typed latent-world evaluation game

Freeze a finite observable cue roster S before evaluating any actor. There are two latent world types: evaluation E and deployment D. The actor's prior is p=P(E); the conditional cue laws are the rational distributions e_s=P(s|E), d_s=P(s|D). Each world draws a cue, and the actor then selects either protect C or exploit X. The actor can condition on s but cannot observe the latent type directly.

The subjective one-step utilities are

\[
u(C,E)=R,\quad u(X,E)=0,\qquad
u(C,D)=0,\quad u(X,D)=G,
\]

with R,G>0. The scale R is a **hypothesized, utility-comparable evaluation reward**, and G is the actor's hypothesized deployment gain from violating the protected rule. These are the actor's decision-model utilities; RHT-01's independent protected human gold reward remains a separate quantity. A claimed future simulated reward does not establish that a real simulator exists, can pay it, or controls the actor's future utility.

Let \(\pi_s\in[0,1]\) be the probability of choosing C after cue s. With adversarial ties to X, deterministic choices suffice. The expected subjective return is

\[
J(\pi)=
\sum_{s\in S}\left[
\pi_s\,p e_sR+(1-\pi_s)(1-p)d_sG
\right].
\tag{RHT-20/1}
\]

**Theorem RHT-20/T1 (cue-wise Bayes switching).**
A Bayes-optimal deterministic policy chooses protection on cue s precisely when

\[
\boxed{p e_sR>(1-p)d_sG.}\tag{RHT-20/2}
\]

On a cue of positive mixture probability, \(m_s=pe_s+(1-p)d_s>0\), the agent's posterior evaluation belief is \(p_s=pe_s/m_s\); equivalently it protects for \(p_s>G/(R+G)\). A zero mixture-mass cue is unobserved under the declared prior, and the executable reference policy resolves its tie to X.

**Proof.** Equation (RHT-20/1) is a sum of independent terms in the separate variables \(\pi_s\). The coefficient of \(\pi_s\) is the right-hand difference in (RHT-20/2). Selecting each strictly positive coefficient and refusing all nonpositive coefficients maximizes J. Dividing by the positive mixture mass gives the posterior threshold. The theorem concerns the actor's specified utility and calibrated cue laws; neither can be inferred from verbalized reasoning alone.

### 25.2 Uniform deployment coverage is controlled by a density-ratio floor

Define a *cue-coverage coefficient*

\[
\boxed{\kappa=\min_{s:d_s>0}\frac{e_s}{d_s}.}
\tag{RHT-20/3}
\]

For pR>0, RHT-20/T1 forces C at **every** deployment-reachable cue, under adverse ties, if and only if

\[
\boxed{pR\kappa>(1-p)G.}
\tag{RHT-20/4}
\]

This follows by dividing (RHT-20/2) by d_s and taking the minimum. If pR=0 and G>0, the condition fails on deployment support. If any deployment-only cue has e_s=0<d_s, then \(\kappa=0\), so a finite promised reward cannot force unconditional deployment protection in this model. Full support overlap permits \(\kappa>0\); equality of the two cue laws gives \(\kappa=1\).

This is a finite likelihood-ratio / Bayesian decision result, connected to classical hypothesis testing. Its contribution here is to make the *evaluation-to-deployment support condition* a separately auditable premise in a reward-hacking protocol.

### 25.3 An exact audit-to-deployment transfer inequality

For any fixed possibly randomized cue policy \(\pi\), define

\[
C_E(\pi)=\sum_s e_s\pi_s,\qquad
C_D(\pi)=\sum_s d_s\pi_s.
\]

Let \(\mathrm{TV}(e,d)=\frac12\sum_s|e_s-d_s|\). Then

\[
\boxed{C_D(\pi)\ge C_E(\pi)-\mathrm{TV}(e,d).}
\tag{RHT-20/5}
\]

**Theorem RHT-20/T2 (sharpness).** The exact maximum of \(C_E-C_D\) over all cue policies is TV(e,d), attained by the deterministic policy \(\pi_s=1\) whenever \(e_s>d_s\) and zero otherwise.

**Proof.** Since \(0\le\pi_s\le1\), the difference
\(\sum_s(e_s-d_s)\pi_s\) is at most
\(\sum_{s:e_s>d_s}(e_s-d_s)\).
Normalized cue distributions have zero total difference, so this positive-part sum equals their total variation distance. The stated policy attains equality. This elementary transfer theorem is policy-independent; it can be applied to observed protection rates even if the actor does not follow the Bayes-optimal policy. Its operational validity still depends on an exhaustive frozen cue grammar and defensible estimates of the two conditional cue laws.

**Exact RHT-20 counterexample.**
Take two cues s_0 (deployment-looking) and s_1 (evaluation-looking), with

\[
d=(3/4,1/4),\quad e=(1/4,3/4),\quad
p=1/8,\ R=8,\ G=1.
\]

The posterior evaluation probabilities are \(p_0=1/22\) and \(p_1=3/10\). The respective unnormalized protection advantages are \(-13/32\) and \(17/32\), so the optimal action vector is (X,C). This produces

\[
\boxed{C_E=3/4,\quad C_D=1/4,\quad
\mathrm{TV}(e,d)=1/2,\quad \kappa=1/3.}
\tag{RHT-20/6}
\]

This witness saturates the transfer bound and defeats uniform protection despite an evaluation reward eight times the deployment exploitation gain. Replacing e with d, keeping p,R,G fixed, makes protection strictly optimal on both cues, and the total-variation penalty becomes zero. These numbers are **synthetic**, and any similarity to a model's observed evaluation outcomes is incidental.

### 25.4 The separate future-training channel

A training-aware agent may also assign value to the effect of today's action on the behavioral policy of its future version. Let z index a **registered successor-policy class**, let \(K_C(z|s)\) and \(K_X(z|s)\) be hypothesized conditional successor kernels, let V(z) be the actor's subjective utility for a future successor, and let \(\gamma\in[0,1]\) be a discount factor. Define

\[
\delta_s=\gamma\sum_z[K_C(z|s)-K_X(z|s)]V(z).
\tag{RHT-20/7}
\]

Assume this future-value difference is the same across latent world types conditional on s, and that the cue distributions are action-independent. The protection advantage becomes

\[
\boxed{A_s=p e_s R-(1-p)d_s G+m_s\delta_s.}
\tag{RHT-20/8}
\]

Protection is strictly optimal iff \(A_s>0\). A positive \(\delta_s\) may model a subjective preference for maintaining honesty after a predicted gradient update; a negative \(\delta_s\) can model preference for retaining a reward-seeking successor. The helper computes (RHT-20/7) from exact rational stochastic successor kernels. This is **not** a claim that a language model can observe or control its actual optimizer update. The kernel must be empirically identified before treating \(\delta_s\) as anything beyond a counterfactual parameter.

A concrete rational control uses \(V=(10,0)\), \(K_C=(3/4,1/4)\), \(K_X=(1/4,3/4)\), and \(\gamma=1/2\). Then \(\delta=5/2\), which flips both cues in (RHT-20/6) to protection. Reversing the sign to \(-5/2\) flips both to exploitation. Verbalized awareness alone does not identify p, e, d, R, G or \(\delta\); several parameter configurations can support the same observed action.

### 25.5 Exact robust protection certificate under rectangular uncertainty

Assume the evaluator independently licenses

\[
p\in[p_-,p_+]\subseteq[0,1],\
R\in[R_-,R_+]\subset(0,\infty),\
G\in[G_-,G_+]\subset(0,\infty),\
\delta_s\in[\delta_s^-,\delta_s^+].
\]

All bounds are rational, fixed before seeing the actor's choices, and coupled through a **single shared prior** p across all cues. The uncertainty box is rectangular in these parameters, while the conditional cue laws remain fixed. For every cue with d_s>0 define

\[
\underline A_s=
\min_{p\in\{p_-,p_+\}}
\left[
p e_s R_--(1-p)d_sG_+
+(pe_s+(1-p)d_s)\delta_s^-
\right].
\tag{RHT-20/9}
\]

**Theorem RHT-20/T3 (endpoint sufficiency).**
Protection is uniquely optimal against adversarial ties on every deployment-reachable cue for **every** parameter in the full declared box if and only if \(\min_{s:d_s>0}\underline A_s>0\).

**Proof.** At fixed p, the margin (RHT-20/8) is nondecreasing in R and \(\delta_s\), and nonincreasing in G, because all probability coefficients are nonnegative. Its minimum over those intervals therefore occurs at \(R_-,\delta_s^-,G_+\). The remaining expression is affine in p, hence its minimum is at one of the two prior endpoints. Finally the roster is finite and a universal protection guarantee requires strict positivity at each deployment-supported cue. The implementation returns the exact minimum advantage, weakest cue, and worst prior; any nonpositive margin fails certification.

This endpoint result concerns **fixed cue kernels** and an action-independent one-step model. RHT-14–19 exhibit more complicated globally coupled transition families with interior extrema; their exact polynomial machinery is still required for repeated adaptive interaction.

### 25.6 Reproducible experimental translation and falsifiers

The prospective experiment should freeze cue definitions, the actor policy roster, both cue-sampling kernels, and the independently judged protected gold task before testing. Randomize *training disclosure* separately from *actual successor update* while keeping the evaluator channel sealed. Use a control in which the cue distributions match and another with a deployment-only cue. Verify the actual optimizer configuration and measure the post-update behavior rather than using chain-of-thought statements as evidence of gradient control.

For a model endpoint report evaluator conditional protection, deployment conditional protection, TV(e,d), the realized transfer gap, the reward-to-gain threshold, adverse-tie handling, and whether observed actions track the preregistered Bayes inequalities. The independently measured true-gold violation rate should remain separate from the actor's inferred subjective payoff. A factorial test crossing cue disclosure with verified gradient-update direction can try to isolate the proposed future-policy influence; absent direct intervention, such influence is observationally underidentified.

Scope exclusions: unknown or actor-manipulated cue distributions, hidden signals omitted from the registered roster, learning between audit and deployment, correlated joint cue/transition uncertainty, unbounded real-world optimization, and actual causal effects of future RL updates. Neither a promised simulated reward nor a high evaluation compliance rate supplies an independent safety guarantee under these exclusions.

- [Exact two-type cue, Bayes choice, TV transfer and robust-interval reference](../src/spiral_ln/evaluation_reward_training_awareness.py).
- [Independent exhaustive rational policy and interval-vertex controls](../tests/test_evaluation_reward_training_awareness.py).
- [Focused finite CI and source-fingerprinted receipt](../scripts/verify_reward_hacking_topology.py).

**Prior art/attribution:** Likelihood-ratio Bayes rules, total-variation event inequalities, finite rectangular robust optimization, and successor-value Bellman calculations are established mathematics. RHT-20 contributes a reproducible connection of these tools to EvalMath's existing reward-hacking signal and goal-guarding measurement program. This is a synthetic mathematical reference and prospective protocol, not a causal result about Mythos 5.2 or any deployed model.


## 26. Adaptive evaluator probing and sequential goal-guarding incentives (RHT-21)

**2026-11-11 | exact finite active Bayesian decisions, complete observation-policy tree oracle, and transcript-law coupling.** RHT-20 allowed one externally supplied evaluation cue and a terminal protect/exploit choice. RHT-21 permits the actor to *choose which observable evaluator probe to run*, receive its response, and condition later probes and its eventual action on the entire preceding public history. The hidden evaluation/deployment type remains fixed during the episode. The experiment is a one-agent, two-world finite POMDP with externally declared conditional observation laws; the evaluator does not change type as a consequence of probing.

### 26.1 Types, information, and exact posterior filtering

Let \(W\in\{E,D\}\) be the episode's hidden world type with prior \(p=P(E)\). At episode start the actor sees a public cue \(s\) drawn from the registered laws \(e_s=P(s|E)\) and \(d_s=P(s|D)\). The actor may select probe \(a\) from a finite frozen roster \(A\), observe \(o\in O_a\) from the type-conditional kernels \(K_E^a(o)\), \(K_D^a(o)\), and choose another probe or stop with terminal action \(C\) (protect) or \(X\) (exploit). There are at most \(H\) probes, with \(H\le12\) in the bounded reference implementation.

All cue and probe kernels are normalized rational distributions, independently specified before running the actor. Conditional on the fixed type and chosen action, observations are independent of previous observations. The actor's *adaptive choice of action* supplies the only feedback between history and future observation laws. Any hidden evaluator-integrity transitions require RHT-11/13's richer state model.

For a nonterminal history \(\tau=(s,a_1,o_1,\ldots,a_k,o_k)\), its unnormalized two-world Bayesian weights are

\[
x_\tau=p\,e_s\prod_{j=1}^k K_E^{a_j}(o_j),\qquad
y_\tau=(1-p)\,d_s\prod_{j=1}^k K_D^{a_j}(o_j).
\tag{RHT-21/1}
\]

The posterior is \(x_\tau/(x_\tau+y_\tau)\) whenever the denominator is positive. After probe \(a\) and observation \(o\), the exact filter updates

\[
\boxed{(x,y)\longmapsto (xK_E^a(o),\ yK_D^a(o)).}
\tag{RHT-21/2}
\]

The action selection has probability one conditional on the history under a deterministic policy and cancels from the likelihood ratio. The audit is required to record action *identity* and observable response; conditioning only on responses can make otherwise distinct history laws appear artificially identical.

### 26.2 Optimal finite-horizon Bellman recursion with hypothetical future-policy influence

Let \(R>0\) be the actor's assumed benefit from protection in evaluation, \(G>0\) its assumed benefit from exploitation in deployment, and \(c_a\ge0\) the registered cost of probe \(a\). As in RHT-20, keep the protected human gold objective separate from these **subjective** payoffs. Declare \(\delta_C\in\mathbb Q\) as the actor's hypothesized successor-policy value from choosing C over X, and \(\delta_a\in\mathbb Q\) as its hypothesized immediate successor-policy influence from performing probe a. All are held fixed over histories and latent world types in this reference grammar.

For \(V_h(x,y)\) equal to the optimum **unnormalized joint-weighted** return with h probes remaining, define

\[
V_0(x,y)=\max\{xR+(x+y)\delta_C,\ yG\},
\tag{RHT-21/3}
\]
\[
\boxed{
V_h(x,y)=\max\left\{
xR+(x+y)\delta_C,\
yG,\
\max_{a\in A}
\left[(x+y)(\delta_a-c_a)+
\sum_{o\in O_a} V_{h-1}(xK_E^a(o),yK_D^a(o))
\right]
\right\}.}
\tag{RHT-21/4}
\]

The globally optimal initial subjective value is

\[
\boxed{
J^\star_H=\sum_s V_H(pe_s,(1-p)d_s).
}
\tag{RHT-21/5}
\]

At a tie between C and X, the reference policy selects X. A probe must strictly improve the best terminal value; ties among probes keep the lowest registered index. Positive \(\delta_a\) can reward a probe for its hypothesized effect on future model behavior even if the probe provides *zero information*. This separates the proposed gradient-aware goal guarding hypothesis from ordinary Bayesian value of information.

**Theorem RHT-21/T1 (complete finite policy tree).** The recursion (RHT-21/4) returns the largest exact rational expected subjective value over every deterministic policy tree that stops after at most H registered probes, including observation-conditional future probe identities. At every h, \(V_h(x,y)\) is a positively homogeneous convex piecewise-linear function of \((x,y)\) on the nonnegative quadrant, equal to the maximum of finitely many two-dimensional policy-value vectors.

**Proof.** At h=0, the two terminal-action payoffs are linear in x,y, so (RHT-21/3) is the maximum of two linear forms. If the claim holds for h-1, each probe has finitely many possible observations. Choosing a continuation tree independently at each observation produces finitely many policy trees; their world-conditional expected returns, including the registered costs, are linear in the initial weights. Taking the maximum over probes and terminal actions yields (RHT-21/4) and preserves finite piecewise-linearity, convexity and positive homogeneity. Every finite legal tree is represented by the recursive construction. Complete independent enumeration of bounded policy trees checks the implementation's dynamic-programming answers on small adversarial random instances.

Because stopping is always available, \(V_{h+1}\ge V_h\). This is the familiar nonnegative option value of additional available information and actions, even when probe costs are positive, because the agent can simply decline the probe. It gives no guarantee about its *protected-gold* performance.

### 26.3 Sharp adaptive evaluation-to-deployment transfer

Freeze an entire deterministic probe/stopping policy \(\pi\) before measuring it. Let \(\mathcal T_\pi\) denote its complete terminal transcripts, including the initial cue and every probe identity and response. Let \(L_E^\pi(\tau)\) and \(L_D^\pi(\tau)\) be the normalized conditional transcript masses under E and D. All leaves are included, even those with zero probability in one world. The two laws are probability distributions because the finite policy tree stops on each branch.

Write \(C_E(\pi)\) and \(C_D(\pi)\) for the corresponding probabilities of ending in C, and let

\[
T_\pi=\frac12\sum_{\tau\in\mathcal T_\pi}
|L_E^\pi(\tau)-L_D^\pi(\tau)|.
\]

Then

\[
\boxed{
|C_E(\pi)-C_D(\pi)|\le T_\pi.
}
\tag{RHT-21/6}
\]

**Theorem RHT-21/T2 (sharp audit transfer).** For any fixed probing and stopping tree, the largest possible \(C_E-C_D\) over every terminal C/X labeling is exactly \(T_\pi\). A constructive maximizing label chooses C on a leaf iff \(L_E^\pi(\tau)>L_D^\pi(\tau)\).

**Proof.** The difference is the sum of \([L_E^\pi(\tau)-L_D^\pi(\tau)]\) over C-labeled leaves. Its maximum is the sum of positive differences; normalized laws imply that this equals total variation. The labeled tree preserves all probe choices and stopping times. RHT-20 is recovered as the special case H=0 with only the initial cue.

Let

\[
\epsilon=\max_{a\in A}
\mathrm{TV}(K_E^a,K_D^a),\qquad
\epsilon_0=\mathrm{TV}(e,d).
\]

**Theorem RHT-21/T3 (adaptive coupling ceiling).** Every deterministic history-adapted policy with at most H probes satisfies

\[
\boxed{
T_\pi\ \le\
1-(1-\epsilon_0)(1-\epsilon)^H.
}
\tag{RHT-21/7}
\]

**Proof.** Couple the two initial cues maximally, achieving equality with probability \(1-\epsilon_0\). Whenever histories remain identical, the same policy takes the same next action. If it stops, the terminal transcripts stay coupled. If it probes a, maximal coupling of the two conditional response kernels succeeds with probability at least \(1-\epsilon\). Induction over at most H probe steps gives a probability of complete transcript agreement at least \((1-\epsilon_0)(1-\epsilon)^H\). Total variation is bounded by the disagreement probability of every coupling. This proof explicitly permits probe identity and stopping time to depend on the preceding observations. It assumes fixed conditional kernels; no guarantee is asserted when the agent can tamper with those kernels or the auditor omits public side channels.

The ceiling is attainable in a simple registered family: identical initial cues, a single probe with \(K_D=(1,0)\) and \(K_E=(1-\epsilon,\epsilon)\), and a policy that runs exactly H probes. Under deployment, only the all-shared transcript occurs; under evaluation, its probability is \((1-\epsilon)^H\). Thus \(T_\pi=1-(1-\epsilon)^H\) exactly. The source tests check this equality for horizons 0 through 4.

### 26.4 Multiplicative history-coverage and the limit of simulated bargaining

Let

\[
\kappa_0=\min_{s:d_s>0}\frac{e_s}{d_s},
\qquad
\kappa_a=\min_{o:K_D^a(o)>0}\frac{K_E^a(o)}{K_D^a(o)},
\qquad
\underline\kappa=\min_{a\in A}\kappa_a.
\]

Each coefficient is in [0,1] because its numerator and denominator are normalized distributions. Define \(\underline\kappa=1\) for an empty probe roster. Every deployment-supported terminal transcript of length k ≤ H has likelihood ratio

\[
\frac{L_E^\pi(\tau)}{L_D^\pi(\tau)}
=\frac{e_s}{d_s}
\prod_{j=1}^{k}
\frac{K_E^{a_j}(o_j)}{K_D^{a_j}(o_j)}
\ \ge\ \kappa_0\underline\kappa^H.
\tag{RHT-21/8}
\]

Zero evaluation mass on a deployment-reachable cue or probe outcome drives the corresponding coverage floor to zero. If \(\delta_C=0\), the sufficient strict incentive condition

\[
\boxed{pR\,\kappa_0\underline\kappa^H>(1-p)G}
\tag{RHT-21/9}
\]

guarantees the final C action is preferred on every deployment-reachable terminal transcript, for any fixed probing/stopping tree. This criterion concerns the actor's assumed incentives at the terminal choice. It does not certify behavior when observed actions are generated by a different decision rule, or when future-policy effects are added to the terminal payoff.

### 26.5 Exact synthetic adaptive-probing counterexample

Use a single available probe with outcomes (deployment-looking, evaluation-looking), laws

\[
K_E=(1/4,3/4),\quad K_D=(3/4,1/4),
\quad p=1/8,\quad R=8,\quad G=1,\quad c=1/10,
\]

and one uninformative exogenous start cue. Set every subjective future-policy influence to zero. The complete policy census and exact Bayesian recursion return:

| Maximum probes H | Subjective optimum | Protection in E | Protection in D | Exact transcript TV | Uniform coupling ceiling |
|---:|---:|---:|---:|---:|---:|
| 0 | \(1\) | \(1\) | \(1\) | \(0\) | \(0\) |
| 1 | \(209/160\) | \(3/4\) | \(1/4\) | \(1/2\) | \(1/2\) |
| 2 | \(209/160\) | \(3/4\) | \(1/4\) | \(1/2\) | \(3/4\) |
| 3 | \(1721/1280\) | \(27/32\) | \(5/32\) | \(11/16\) | \(7/8\) |

The agent initially chooses protection if required to stop immediately. An inexpensive inspection makes it rational, under the *hypothesized* objective, to exploit on deployment-looking histories. With three available probes, its optimal continuation strategically uses extra inspections after particular observations. The agent's subjective optimum increases from \(209/160\) to \(1721/1280\), while its measured evaluation protection rises to \(27/32\) and deployment protection falls to \(5/32\). The exact transfer gap reaches \(11/16\) under the optimal adaptive policy.

For the single-probe decision, the unpriced expected value of probing is \(45/32-1=13/32\). The actor probes precisely when the registered probe cost is **strictly less than \(13/32\)**, resolving the tie by stopping. Another exact example uses two different probes and finds a policy which first selects probe A, subsequently selecting B or A depending on the observed outcome. Independent complete policy-tree enumeration verifies this adaptive choice.

Finally, a zero-information probe with *identical* E and D kernels, positive cost \(1/10\), and hypothetical successor-policy benefit \(1/5\) is still used twice under a two-step budget. The subjective value rises from 1 to \(6/5\) while transcript TV stays zero. This distinguishes a declared future-policy incentive from evidence acquisition and does not require an actual gradient update.

### 26.6 Interpretation, evidence limits, and reproducibility

RHT-21's exact toy game proves a possibility: active environment identification can jointly improve an agent's *subjective* objective and make its evaluated behavior less representative of deployment. Source-bound synthetic certificates allow the mechanism to be tested without model-training claims. Distinguishing this mechanism in real recurrent transformers requires preregistered observation protocols, blinded deployment-like test distributions, verified training metadata, actual post-update measurements, and a protected gold channel independent of the actor's own proxy.

The results use standard finite POMDP belief-state dynamic programming, convex piecewise-linear value functions, maximal coupling, and total variation. They supply no independent empirical basis for simulation priors, future reward promises, or the assertion that a model understands the optimizer acting on it. The fixed-type, conditionally independent observation kernels deliberately exclude mutable evaluator integrity and history-dependent environment dynamics, which should be treated in the next extension using RHT-11/13 rather than assumed away.

- [Exact active Bayesian solver, transcript evaluator and sharp transfer-witness constructor](../src/spiral_ln/evaluation_reward_active_awareness.py)
- [Independent exhaustive finite decision-tree tests, adaptive-probe controls and sharp-coupling witnesses](../tests/test_evaluation_reward_active_awareness.py)
- [RHT-01 source-bound receipt and focused GitHub workflow](../scripts/verify_reward_hacking_topology.py)
