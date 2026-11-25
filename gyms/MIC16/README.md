# MIC-16: Bayesian proof acquisition with a hidden certificate catalog

Public cloud CPU development following [MIC-15 #99](https://github.com/MoralityLabAI/EvalMath/pull/99). The protocol was written locally before the full sweep; a single smoke test ran first. No external manuscript bytes, no neural fits or paid GPU.

## Mathematical model

Three disjoint groups of exact integer entries, seven lemmas (three group sums, three pair sums, one triple sum). The four target rewards are distinct weighted improvements over public entry ceilings; overlapping targets do not define a single global bound. Direct verification costs the number of entries scanned; a composition uses previously acquired group sums and a declared positive cost. The hidden certificate catalog has eight possible static worlds with positive integer prior weights, a known availability/cost model and an unknown actual world. Cached proof attempts succeed or fail and cost one or two units; a paid catalog probe reveals one world bit. On success the independent replay checks the exact arithmetic reward and prerequisite contract. Availability and price are synthetic environment facts, not a cryptographic or Lean proof or measured proof-checking latency. The generated entries, rewards, prior and entire set of possible catalog worlds are known to the planner. Only the realized world is hidden from nonclairvoyant arms. The action observation is the tuple (success, cost, signal); the environment does not independently solve any new mathematical conjecture.

Let S be acquired lemmas, M the nonempty posterior support, B the remaining budget. All observations are deterministic given the world and action. M evolves by intersection with the worlds yielding the observed outcome, retaining their original relative weights. Each action is admitted only if every currently possible outcome costs <=B. Thus no hidden-world overdraft occurs. Actions whose only possible result has neither information nor acquisition progress can be removed because their positive cost is dominated by skipping them.

For a posterior mask M, let W(M) denote the sum of integer prior weights. The exact unnormalized weighted value is U(S,M,B)=max(0, max_a sum_o [W(M_o) r_o + U(S_o,M_o,B-c_o)]). The observations partition M, so the formula follows by conditioning; induction on B proves optimality (all costs are positive integers). Divide by W(M) to obtain expected reward. Receding-horizon depth h adds an action-count cap inside the Bellman recursion and replans after each actual observation. Clairvoyant receives the singleton true world at the start and is a nondeployable upper ceiling. Direct-only permits direct and composition rules but no cached attempts or probes. Bayes-no-probe permits all proof rules but no dedicated information probe. Neither is a pure memory ablation.

The posterior is sufficient in this static model: conditioned on acquired lemmas, posterior support and remaining budget, the exact sequence of earlier observations has no extra predictive value. The benchmark can test inference and compression of belief; it does not establish a causal benefit of ordering observations rather than keeping a sufficient statistic.

## Development sweep

48 roots (four synthetic local/shared/parity/mixed catalog patterns, seeds 16000..16011 per family), 3 budgets, 8 deterministic worlds per root, nonuniform positive prior weights. Each policy executes its own entire trajectory, with no oracle-provided continuation. No sealed confirmation or certified family independence. Primary budget 12 fixed in protocol before full sweep; strongest fixed receding-horizon comparator chosen from h=1..4 by aggregate mean regret. The direct-only exact control and exact no-probe comparator are separately descriptive. Declared proof acquisition cost is common; planning computation is extra, and cached computations shared across modes/worlds/budgets make timing and new-state counts unsuitable for speedup claims.

Mean percentage of exact Bayesian expected reward over the 48 roots per budget:

| Policy | 8 | 12 | 16 |
|---|---:|---:|---:|
| Direct/compose exact | 40.9381 | 48.8291 | 68.2023 |
| Greedy 1 | 68.2187 | 71.5796 | 70.0653 |
| Lookahead 2 | 89.0366 | 80.3947 | 77.0290 |
| Lookahead 3 | 94.0921 | 88.4877 | 85.8343 |
| Lookahead 4 | 99.5170 | 93.9361 | 90.3671 |
| Exact Bayes no probes | 99.9696 | 99.9412 | 99.9359 |
| Exact Bayes | 100 | 100 | 100 |
| Clairvoyant | 104.6069 | 102.9557 | 101.4655 |
| Posterior reset (retrospective) | 68.5479 | 69.4355 | 78.6559 |

The posterior-reset policy computes its next action from the same full Bayesian planner at the initial prior, retaining the acquired set and budget. It is permitted to repeat an uninformative attempt. Actual safety and posterior consistency are checked against the true observation history. It is a deliberately information-discarding ablation, not an optimized best policy under partial memory; it may underperform other limited-memory policies. Exact Bayes beats it on 48/48 roots at each budget. The gap combines changes in information-guided choices and robust budget admission. Explicit probes strictly improve over the exact no-probe policy on 1/48, 2/48 and 2/48 roots respectively. Cheap cached proofs and the information they convey are jointly valuable; the direct-only comparison does not isolate information alone.

At primary budget 12, mean regret versus the strongest fixed horizon-4 planner = 6.063927 pp, but only 8/48 (16.67%) have >=10% regret. Headroom protocol requires both >=5% mean relative regret and >=20% hard roots. FAIL_NO_FITS. Budget 16 has greater headroom (9.63% mean and 22/48 hard); do not switch the primary budget after observing the sweep. This can inform a separately registered future experiment with fresh roots and stronger controls. The repository planner strict exit 2 is REDESIGN_OR_PILOT_ONLY: only four unverified lineages, no independent sham calibration, no sealed holdout. Deterministic zero sham is a placeholder. This oracle headroom comparison is not a neural mechanism experiment.

## Verification and replay

Four targeted tests passed (0.73 s), including outcome partition and safe-budget tests, alternate explicit-world Bellman oracle, path/nonanticipation checks and receipt tampering. Primary run 22.390 s; independent audit 30.170 s. Replay checked all 10,368 trajectories including retrospective reset, 36,251 distinct within-policy observable-state action/stop checks (counted separately per root-budget-policy, not independent cases), and 112 exact optimum checks (Bayes and no-probe for every primary root, plus other budgets on one root per family) using separate tuple/frozenset-based Bellman enumeration. The nonanticipation check detects inconsistent actions at identical observed states; it is not a proof of arbitrary implementation secrecy. The oracle implementation and environment generator remain synthetic finite code. Full repo CI, independent confirmation, genuine measured work matching, and mathematical model verification in Lean outstanding.

From repository root:

    cd gyms/MIC16
    python -m pytest -q test_mic16.py
    python mic16.py > results.json
    python audit16.py
    cd ../..
    python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC16/preflight_input.json --strict

The last command intentionally exits 2 on this public diagnostic. Planner Git blob matched 0ff062f76f5534d9f18425f986ae3e750397f50c. Python 3.13.5; standard library for experiment and audit, pytest for tests. Local SHA256 mic16.py 350d22fe4ed8f0a769bfec2ea40a3447a1b1cc09f2c385777448f30ea36f8190, audit16.py abf46d594bfe9a8ee70171c2c0d97269ae361b29059957c573e4a37064e3429c, test_mic16.py 48da1a15117ccffe1e5e0352a2fd9e2c8a2749ec19d13aea96a16cabf324cb2a, protocol.json 1ba8fddfd8f4eb34e0e86d3af92713ca68c10f3205cd70041be68f0306aff0c6. Timing-dependent generated results.json c788a3f384fe3ee34628c1726ba6804c74a0ef92384cebe808bc815398a914f9; audit_results.json 65150b04bc94e2a11b15c014b1adf4001326fbf8e0c0f6561c5eadfc58208980. Raw files not committed.

## Next gate

Study compressed sufficient-statistic reconstruction and exact finite-state memory bounds, comparing posterior state, learned recurrence, fixed history window and optimized finite-memory policies. Design paired histories sharing acquired set and remaining budget but requiring different actions due to posterior evidence, and report the optimal aliasing regret using exact Bayes. Budget 16 is a development observation only; register a fresh evaluation before using the harder budget. Test whether observation evidence is actually recoverable, control for policy-induced acquisition and cost cues, and use stronger planning baselines and common measured resources. No training allocation or DLMST manuscript ingestion; the original textual discovery question remains untested.
