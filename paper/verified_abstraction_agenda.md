# VAD-10: research-agenda selection as a dependency-hypergraph control problem

2026-11-25. Exact finite oracle (`scripts/vad_agenda.py`), an independent history-tree evaluator (`scripts/vad_agenda_naive.py`), receipt `output/verified_abstraction/vad_10.json`, tests `tests/test_vad_agenda.py`. No learned model, no Lean in this note. Evidence levels: *algebraic identity* (Propositions 1, 3), *finite verified example* (counterexamples, sweeps), *synthetic mechanism result* (all instance classes).

## Model

Vertices are propositions 0..n-1 and hyperedges e=(A -> v, c_e) are legal inference rules with an integer attempt cost; premises have smaller index than the conclusion. A hidden world w fixes which edges exist. The prior over worlds may be any finite law, so edge existence can be correlated.

State: verified library L (a set of vertices, initially the facts), posterior pi over worlds, integer budget b. Actions: *attempt e* (premises in L, conclusion not in L, cost c_e <= b) reveals whether e exists, on success verifies the conclusion and pays its reward r(v) once; *experiment j* (cost, signal likelihood over worlds) updates pi; *stop*. Utility charges lambda per budget unit spent.

At stop the library is scored against the future: N iid future targets with law mu, each costing D_{L,w}(g) reference units, where D=1 for verified vertices and otherwise D(v) = min over existing edges of c_e + sum of D(premises), capped at `cap`. The value function is

    V(L,pi,b) = max( T(L,pi), max_a sum_y P(y) [ u(a,y) + V(L'_y, pi'_y, b - cost(a)) ] ),   T(L,pi) = -N E_{w~pi} E_{g~mu} D_{L,w}(g).

It is a function of exactly the objects the programme asks for: the verified library, the posterior over unknown relationships, remaining budget, and the future theorem distribution. Computation is by memoized recursion over (L, pi, b) in exact Fractions.

**Proposition 1 (three-part decomposition, algebraic identity).** For every action a at (L,pi,b), with b'=b-cost(a),

    Q(a) = V(L,pi,b') + E[u] + E[V(L',pi,b') - V(L,pi,b')] + E[V(L',pi',b') - V(L',pi,b')].

The terms are the budget-exhausted baseline, the immediate reward (net of lambda times cost), the reusable value of the changed library, and the information value of the changed posterior. Telescoping in the other order exchanges the last two terms for E[V(L,pi',b')-V(L,pi,b')] and E[V(L',pi',b')-V(L,pi',b')]; their difference is reported as an interaction. The split is order dependent and the "reuse" term includes the loss of still-unpaid rewards that the attempt exhausts, so a negative reuse term does not mean the lemma is useless. Both orders are asserted exact in every test and receipt row.

## Greedy research selection

Define greedy-k as: at each state take the first action of the best plan that follows it with at most k further actions (greedy-0 maximizes immediate net reward plus the stop value of the resulting state; it is Bayesian myopic value-of-information). Optimal is k unlimited; "direct" pursues the highest-reward unverified target and its prerequisites.

**Proposition 2 (modular class, theorem).** Suppose every edge has premises among the facts, distinct edges have distinct conclusions, edge existence is independent, there are no experiments, and all edge costs are equal to c. Then greedy-0 attains V. *Proof.* Because premises are facts and conclusions are distinct, T is additive over vertices, and verifying v changes only D(v). Attempting e_v from any reachable state therefore adds exactly u_v = p_v (r_v + N mu_v (D_v^0 - 1)) - lambda c to the stop value, independently of every other attempt and of past outcomes, where D_v^0 is the cost without v. Attempts reveal nothing relevant to other edges. The problem is a choice of at most floor(b/c) vertices maximizing the sum of u_v, solved by taking the largest positive u_v, which is exactly what greedy-0 does at each step (adaptivity adds nothing). QED. Verified in 60 test seeds and 150 receipt seeds (greedy-0 value equals V in all).

Dropping each of equal costs and the premises-among-facts structure breaks the theorem (finite verified counterexamples, all exact; "value" is expected utility, higher is better). We found no counterexample when dropping 'distinct conclusions' or 'no experiments' in 5,500 random trials and do not claim those are necessary; the correlated sweep mixes several departures and does not isolate independence:

* *Unequal costs.* Cost 2 vertex (net gain 3) against two cost-1 vertices (gain 2 each), budget 2: greedy-0 = 2, optimal = 3.
* *Complementary discoveries.* Two lemmas each cost 8; the future target is reachable cheaply only with both (deployment gives up at cap 10). Greedy-0 = stop = -30 because each lemma alone leaves the cap unchanged; optimal = greedy-1 = -12.
* *Delayed payoff (Proposition 3, algebraic).* A chain of k edges each present with probability p, only the end pays R and nothing else has reuse value; lambda = 0, N = 1, all future mass on a fact, budget at least k. V = p^k R - 1 for R p^k > 0 (stop value -1), and greedy-j attains V iff j >= k-1, with ties between equal-value actions broken toward stopping (the oracle's `best_action` keeps the earlier action, stop first); with ties broken toward attempting, lower-depth greedy also attains V. With lambda = 1/10 and k = 3 the value is 6.019, not 6.29. *Proof.* Every attempt except the last has zero immediate reward and zero change of T, so Q_j of the first attempt equals the stop value unless j further steps can reach the paying vertex, which needs k-1. Verified exactly for k=2..6 against the forward evaluation.
* *Correlated edges.* In 60 seeded instances with a latent good/bad regime and a noisy regime experiment, greedy-0 is optimal in 70%, greedy-1 in 93.3% and greedy-2 in 100%.
* *Misleading verifier feedback.* Two mutually exclusive routes to a rewarded target and a cheap automated check the planner assumes raises a flag with probability 9/10 if route A exists and 1/10 if route B exists. The planner's own claimed value is 8. If the check is in fact reversed (true reliabilities 1/5 and 4/5) acting on it yields 1, ignoring it yields 4, and the true optimum is 7. Sweeping the true reliability r in steps of 1/20, trusting beats ignoring only for r >= 11/20 (receipt field `trust_beats_ignoring_from_reliability`); at r=0 trusting yields -1. The kernel verifier is not misled in this model; the misleading object is a cheap heuristic signal, and any acceptance by the real verifier is treated as ground truth.
* *Failed investigation as information.* Exactly one of two equally likely routes exists. Attempting the first is an experiment for the second: the Q-decomposition has immediate 3, information 3/2, reuse -3/2 (reward exhaustion), total 5 over a continuation base of 2.

## A strategic intermediate theorem beats pursuing the best target

Vertices: fact 0, lemma M=1, target T=2 with reward 10, future problem G=3 (all future mass, N=4). T has a direct edge (cost 2, probability p) and a route through M (M costs 1 with probability 4/5; M -> T costs 1 with probability 4/5). From M, G is cheap (cost 4) rather than 10. Budget 3. At p=1/5, optimal value is -18; pursuing the target directly gives -23.44 (and random attempts -21.6, stopping -28). The optimal first action is M, whose immediate reward is 0 and whose Proposition 1 reuse term is 128/25; the direct attempt has immediate 2 and reuse 0. In the sweep p in {0,1/40,...,1} the optimal first action is M for p <= 31/40 and the direct edge for p >= 4/5 (receipt `strategic_scan`); at p=1 the optimal policy takes the target first and then M (-14.8) while the goal-directed baseline stops after the target (-18), so there the loss is forgone reuse, not a wrong first action. The regime is therefore: the highest-reward target is not the best research action whenever its direct route is unreliable relative to a cheap route through a lemma that also lowers future cost.

## Finite sweeps (public seeds 70000..70149, correlated 70000..70059)

Optimal-action fraction / mean regret (utility units) against the exact optimum; regret is exact in the receipt:

| Class (n) | direct | greedy-0 | greedy-1 | greedy-2 | random |
|---|---|---|---|---|---|
| modular (150) | 0.507 / 0.501 | 1 / 0 | 1 / 0 | 1 / 0 | 0.207 / 1.489 |
| layered DAG (150) | 0.613 / 0.438 | 0.787 / 0.322 | 0.960 / 0.019 | 0.993 / 0.0019 | 0.173 / 1.210 |
| correlated + regime experiment (60) | 0.583 / 0.261 | 0.700 / 0.410 | 0.933 / 0.037 | 1 / 0 | 0.150 / 0.910 |

Mean memoized Q-evaluations per forward evaluation of the policy: layered 12.4 / 22.8 / 29.6 for greedy-0/1/2 and 14.9 for the optimal plan, so lookahead depth buys near-optimality at planning costs of the same order as the full optimum on these tiny instances; no compute advantage of bounded lookahead over the exact oracle is shown here. These are finite synthetic instances with 5-7 vertices, 3-7 uncertain edges and budgets <= 5.

## Verification

    python scripts/verify_vad_agenda.py --out /tmp/vad10.json     # ~7 min; writes the receipt
    python -m pytest -q tests/test_vad_agenda.py                   # 11 tests, ~11 s

The independent evaluator recomputes posteriors from the prior at every node of an explicit history tree and uses fixpoint reference costs; it agrees with the Bellman recursion on 57 receipt instances (35+22) and 60+ test instances including the signal instances. Forward evaluation of the extracted optimal policy equals the Bellman value on every instance. Both evaluators share the Instance definition and the same modelling choices (deterministic attempts, deployment cost model), so agreement checks the algorithms, not the model.

## Limits

Instances are tiny and synthetic. Reuse is measured by a reference-cost model with a cap; it is not measured Lean compile time. Edge probabilities are given to the planner. The deployment phase has no further learning. Proposition 2 is for a deliberately simple class; no approximation theorem is claimed for general submodular settings (the adaptive-submodularity literature suggests one, cited from memory and not used here). The "verifier feedback" experiment models a heuristic signal, not a faulty kernel.
