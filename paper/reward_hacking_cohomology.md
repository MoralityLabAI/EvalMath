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
