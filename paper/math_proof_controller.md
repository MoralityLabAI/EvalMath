# EM-MPT-03: Bayesian proof-search controllers

2026-11-25. Extends [EM-MPT-01](math_proof_persistence.md) and [EM-MPT-02](math_proof_persistence_cost.md). Evidence: algebraic identities in a declared synthetic mechanism, exact finite verification. No trained model, Lean kernel, or physical cost measurement.

## State and information contract

There are d sequential required obligations, a fixed hidden type z in a finite set, and a known prior pi. At stage i each action a has an integer cost c(i,a)>0, charged whether it succeeds or fails, and a success probability p(i,a,z). Given z and the current stage/action, the outcome is a fresh Bernoulli draw independent of earlier outcomes. Success advances i, failure leaves i unchanged. All certificates are valid by assumption. Only the binary outcome is observed. Actions can represent ordinary generation, a strategy switch or retrieval plus generation; retrieval here supplies a success channel, not a separate diagnostic observation. No hidden graph, false accepts, extra observation channel, type drift, separate controller runtime, or learned costs. Both arms share identical actions and costs. Terminal reward is one for all obligations verified, zero otherwise.

## Exact optimal control

Let w_z=pi_z times the likelihood of the observed history. Let V(i,b,w) be the maximum unnormalized terminal success mass with b integer budget remaining. V(d,b,w)=sum_z w_z. If no affordable action exists (or w is zero), the nonterminal value is zero. Otherwise

    V(i,b,w) = max(0, max_{a:c<=b} [
        V(i+1,b-c,w * p(i,a)) + V(i,b-c,w * (1-p(i,a)))
    ]).

Multiplication is componentwise. Proof: conditional on the next action its two possible outcomes partition the mass. The continuations can be optimized separately, and each consumes a positive amount of budget, so backward induction proves the recurrence. A randomized choice is a convex combination and cannot improve the maximum. Induction also gives positive homogeneity V(i,b,lambda*w)=lambda V(i,b,w) for lambda>=0. Hence normalized posterior together with progress and remaining budget is sufficient under the stated observation and transition laws. The complete transcript remains necessary for audit and for recomputing the posterior if the model changes. This is exact in the declared model, not a sufficiency claim about arbitrary proof search.

Independent oracle: at each (i,b) enumerate conditional success vectors alpha indexed by type. The terminal set contains the all-ones vector and a nonterminal stopping policy gives zero. Every action combines vectors from its two continuation sets by p*alpha_success+(1-p)*alpha_failure. Componentwise dominated vectors can be discarded because both multiplication factors are nonnegative. By induction the remaining set contains a maximizer for every nonnegative prior; its largest dot product with w equals V. This is independent of the posterior recursion.

## Comparator and strict witness

The progress/clock-only controller commits to a deterministic table of actions indexed by (i,b), with no other history. Enumerate every feasible table and evaluate the mixture of conditional closure probabilities, taking the best. It is given the true prior and success model. Explicit stop is unnecessary in this terminal-reward-only problem: continuing with any affordable action cannot turn an already completed proof into failure and cannot reduce a zero reward from stopping early. A randomized policy that is a mixture of deterministic tables cannot improve the maximum; the same holds for fresh independent Markov randomization because each (i,b) is visited at most once. This is a strong comparator within its interface and is not a claim against arbitrary symbolic search.

Two types are equally likely; both stages have strategies A=(3/4,1/4), B=(1/4,3/4), retrieval R=(3/4,3/4). A and B cost 1, R costs 2 at stage zero and 3 at stage one. With d=2 and budget 4, the optimal posterior controller gives 205/256, while the optimal clock/progress controller gives 199/256. The difference is 3/128. An optimal policy begins A; following a failure it switches to B. There is a history collision at stage one with budget two. A success followed by A failure gives posterior (1/2,1/2), where A and B tie and the implementation chooses A; A failure followed by B success gives (1/10,9/10), where B is optimal. A third reachable history, A success followed by B failure, would have a posterior favoring A but is not taken by this selected optimal policy; the reported strict separation is established by the full policy enumeration, not by the tie witness alone. The two explicit histories illustrate distinct posterior state at identical progress and clock. At cheaper retrieval costs (1,2), optimal closure rises to 219/256, and the finite fixture's history advantage disappears. The selected costs and probabilities are illustrative, not empirical.

## Exact reproducibility

225 cases cross three strategy strengths (1/2,3/4,1), five prior weights (0,1/4,1/2,3/4,1), three first-stage retrieval costs (1,2,3), and five budgets (0..4). All agree with the independently enumerated alpha-vector optimum, all dominate the exhaustive clock/progress baseline, and point-mass priors give equality. Three unit tests pass. The receipt contains source hashes and exact fractions.

    PYTHONPATH=src python -m pytest -q tests/test_evaluation_math_controller.py
    python scripts/verify_math_controller.py
    python scripts/check_receipts.py --only math_controller

## Empirical continuation

The positive finite witness motivates a learned controller with a persistent representation of failed strategies across proof obligations. A strong empirical control should retain identical proof state, context, available tactics and verifier budget, with a matched history-shuffle or reset intervention and an independently optimized symbolic history-aware controller. Charge posterior computation, model inference, retrieval, verifier and ledger costs in both arms, and report action-conditional success calibration. The 2.34-point synthetic gain is smaller than the earlier proposed 5-point scientific floor, so it does not establish useful empirical power. Before any confirmation, run independent development roots through the mechanistic-resolution preflight; keep evaluation roots sealed, freeze the comparison family, and reject target/descendant leakage in the Lean environment. A next mathematical problem is identifying the smallest continuation-sufficient history summary when type dynamics or observation models vary, or robust control when the prior and success matrix are uncertain.
