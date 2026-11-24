# EM-MPT-01: Mathematical completion at fixed predictive loss

Draft 0.1, 2026-11-25. Evidence: algebraic identities in a synthetic independent-attempt mechanism and exact finite verified examples. No language model, Lean kernel, or empirical phase-transition experiment was run.

## Motivation

OpenAI's [Perplexity and Intelligence](https://openai.com/index/perplexity-and-intelligence/) (November 22, 2026) reports mathematical breakthroughs at approximately 0.76 log-perplexity on an internal code corpus, while expressly recognizing the limits of perplexity as an actionable measure and the effects of inference techniques. Anthropic's [Formalizing Fermat's Last Theorem](https://www.anthropic.com/research/formalizing-fermats-last-theorem) (September 4, 2026) reports formalization using Prove2Me, whose maintained dependency graph helped agents coordinate, reuse work, and manage memory. These are cited observations, not matched-compute causal comparisons. This note asks what a predictive-loss disclosure alone can certify when an inference harness can retain verifier feedback.

## Declared model

A known acyclic proof graph contains d required obligations, with the same obligations and topological order in every arm. An attempt at obligation i succeeds with probability p_i in [0,1], independently across attempts conditional on i. A successful attempt supplies a valid certificate; verification and persistence are assumed exact, with no hidden state, false acceptance, side information about the target, or storage overhead. One attempt costs one abstract unit; the budget B is an integer >=0. An empty proof is already complete. Actual verifier, retrieval, storage, generation and orchestration costs must be charged in an empirical test. A graph supplied with the correct dependencies may itself disclose useful structure; this model conditions on the graph and isolates retention.

## Theorem 1: completion law and static control

Let M_b(i) be the probability of having completed i obligations after b attempts, where d is absorbing. Initially M_0(0)=1. For i<d, M_{b+1}(i) receives M_b(i)(1-p_i) and, for i>0, M_b(i-1)p_{i-1}. The absorbing state receives M_b(d)+M_b(d-1)p_{d-1} for d>0. This is a partition on the next Bernoulli outcome. Hence R=M_B(d). In the homogeneous case p_i=p, the d-th success completes the graph, so R=Pr[Binomial(B,p)>=d], including d=0 and B<d.

For every fixed positive quota vector a with sum a_i<=B, the completion probability of the static quota controller is product_i [1-(1-p_i)^a_i]. Couple the arms using independent infinite Bernoulli streams for each obligation. Let G_i be the position of the first success (infinity when p_i=0). Static success requires every G_i<=a_i; on this event sum G_i<=B, which is precisely the condition for the persistent sequential controller to complete. Therefore persistent completion dominates every static quota controller, including the best one chosen with full knowledge of p_i. For the homogeneous restart-on-failure sham, a run of d successes in the first B trials implies at least d successes in those trials; hence persistent completion also dominates that restricted sham. No claim of dominance over all adaptive symbolic solvers is made.

For d=4, B=8, p=1/2: persistent 163/256, best static 81/256, restart sham 3/16. The finite verifier enumerates all positive static quotas; the best allocation in this example is two attempts per obligation.

## Theorem 2: aggregate log loss is insufficient

Assume p_i>0 and a corpus uniformly sampling one designated correct witness at each of d fixed contexts. Each predictor assigns probability p_i to that witness; all other outcomes fail. Its mean negative log probability is L=-(1/d) sum log p_i. With B=d, R=product p_i=exp(-dL). With B=d+1, success consists of completing without a failure or with exactly one failure before completion. Disjoint first-completion prefixes yield

R=(product p_i)(1+sum(1-p_i)).

At fixed L, the product is fixed and AM-GM minimizes sum p_i at equal p_i, which maximizes R. For (1/2,1/2) and (1,1/4), L=log 2 in both cases, yet at B=3 completion is respectively 1/2 and 7/16. These are exact identities within the witness corpus, not statements that real cross-entropy equals verifier success probability. Even with known loss on this task-specific corpus, an upper capability bound needs assumptions about heterogeneous error and the inference interface.

## Evaluation disclosure consideration

Report model checkpoint and fixed tokenizer/corpus loss; obligation-level success distributions and correlations; allowed feedback and graph provenance; persistence and scheduling policy; full inference/verifier/ledger costs; and sealed independent-root success curves. Calibrate a capability envelope over a declared controller family instead of transferring a loss threshold across scaffolds without evidence. A bound on a fixed controller need not bound the maximum over a richer controller class. For comparative evaluations include a budget-matched symbolic search ceiling, a matched graph-control with the same available statements but disabled persistent reuse, and an oracle graph arm labeled as privileged information. Negative results require matched overhead and a meaningful resolution floor.

## Reproduction

The DP is checked against independent enumeration of first-completion bit prefixes on 7,029 heterogeneous cases, with exact static quota optimization. A further 330 homogeneous cases check the binomial law and restart dominance. Three unit tests cover the equal-loss witness, the matched-budget witness, and boundaries. Probabilities use Fraction; logs are symbolic. Grid: d=0..4, B=0..8, p_i in {0,1/4,1/2,3/4,1}; homogeneous d=0..5, B=0..10, same p grid. The source-hashed receipt records both exact values and checks.

Run: PYTHONPATH=src python -m pytest -q tests/test_evaluation_math_persistence.py
Run: python scripts/verify_math_persistence.py
Run: python scripts/check_receipts.py --only math_persistence

## Empirical continuation (unregistered planning only)

Run a development-only proof search pilot in DataGoblin, not in EvalMath. Independent units are generator worlds, with all transformations, depths, checkpoint evaluations and controller repeats clustered by world. Use a pre-declaration environment frozen before the target theorem, reject target/self/descendant leakage, audit imported axioms, and preserve complete failure receipts. Compare persistent ledger, token/compute-matched static quotas, competent symbolic search, and shuffled or disabled reuse; do not give an oracle proof path to the main arm. Log predictive loss on the identical independently held-out corpus at several checkpoint losses. Record all token, verifier, FLOP and storage costs. Primary planned contrast is paired root closure at fixed total budget; proposed scientific floor 0.05 absolute probability, to be revised only before confirmation. A matched-sham floor, development effect, root-level power and family size must be established via the EvalMath mechinterp preflight before sealing any prospective sample. No pilot worlds or confirmation roots have been run; no empirical causal or safety-threshold claim follows. The next mathematical gate is a robust envelope under dependency-conditioned attempt probabilities and charged retrieval/ledger overhead, followed by a Lean fidelity proof of the finite identities.
