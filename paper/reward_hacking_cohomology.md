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
