# AIRIS-EvalMath (AIRIS-01)

Status: exact finite synthetic development gym; native no-op wiring verified; native learning comparison pending.
Base: EvalMath 497f87cd83fd1ca8d53f9e39ebd74474612f1dfe. CPU only, Python 3.10+, standard library.

## Motivation and source boundary

Cook & Hammer, *Autonomous Intelligent Reinforcement Inferred Symbolism* (AGI 2024, pp. 53–62), learns partial state-change rules from action-conditioned observations, composes them to predict future states, and explores low-confidence states. See https://kth.diva-portal.org/smash/record.jsf?pid=diva2:1890142 and https://github.com/berickcook/AIRIS_Public.
The separately maintained generalized implementation is https://github.com/singnet/AIRIS-general/tree/db19ad4e2cea33e6129c8bf03e85797da8cf7625 (Apache-2.0 LICENSE at this pin; inspect NOTICE before copying). Goertzel's September 2025 SubRep/PLN integration is a proposed extension, summarized with implementation boundaries at https://wiki.hyperon.dev/Hyperon_AI_Algorithms%2BAIRIS_Autonomous_Intelligent_Reinforcement_Inferred_Symbolism%2BAIRIS_Deep_Dive.

This is an original finite specialization of the AIRIS idea: learn action-conditioned coordinate changes, predict their composition, search a generated graph, and acquire observations to resolve uncertainty. It uses exact version-space counts rather than upstream precondition-match voting. The affine grammar, explicit structural zeros, resettable contexts, uniform independent prior, and conservative planner are declared assumptions. No upstream code is copied or executed by AIRIS-01. No neural training or Lean theorem is claimed.

## AIRIS-01 mathematical contract

State is (c,s), with two-bit public context c in {0,1,2,3} and three-bit public output s in {0,...,7}. An action a has a hidden delta d_a(c), and the next output is s XOR d_a(c). Context stays fixed during a rollout. Experiment reset lets the harness choose c and s=0; it costs one observation per action and is not a free sensor. The grammar for each active output coordinate is all eight affine Boolean functions on F2^2, represented as four-bit truth tables. Each action has two active coordinates; the third is a known structural zero. Specifically decor affects bits 1,2; route bits 0,1; support bits 0,2. The agent knows the grammar and masks, never the hidden tables.

A rule version space V_{a,j} is filtered by the observed pre/post delta bit. Its Cartesian product is the set of compatible worlds. A contradiction rejects the entire update. Under the uniform product prior, an outcome probability is the exact product of matching fractions for its bits. Composition predicts a state by XORing the deltas; breadth-first search uses only unanimous full-state edges. Therefore any returned plan is valid in every world consistent with the current observations, conditional on the declared grammar. The planner can abstain even when a more general contingent or goal-projected plan exists.

For a candidate probe q, its outcome partition has probabilities p_o. Confidence is max_o p_o; collision discrimination is 1 - sum_o p_o^2, the probability that two independent compatible worlds disagree at q. Goal-directed acquisition chooses max_q sum_o p_o 1[certified_plan(V restricted to o, goal) exists], breaking ties by collision discrimination and fixed order. The goal can change without reinitializing the rule base.

## Frozen development census

Start each root with six identical passive observations (all three actions at contexts 0 and 3). The active coordinates each have two compatible affine rules, hence 64 hidden worlds. These form an exhaustive constructed slice, not independent samples from a population of real environments. Active probes use contexts 1 and 2, unit cost, and never access the hidden rule identifier. Primary goal: from zero at context 1, reach any state with bit 0 set. Secondary goal: bits 0 and 1 both set. Compare fixed order, least-confidence (AIRIS-inspired), collision discrimination, one-step goal value, and uniform random informative query (integrated exactly). Budgets 0,1,2; count certified plan success over all roots, report exact fractions. Fixed/curiosity arms intentionally face nuisance-coordinate uncertainty; this is a designed separation witness, not a claim of broad algorithm superiority.

The receipt records all per-root scores, source SHA-256, aggregate fractions, observation budget and evidence class. Tests cover contradiction atomicity, prior mass, passive nonidentifiability, composition, exact outcome partitions, matched budgets, goal changes, and an independently enumerated subset-XOR reachability oracle.

Run:
    python -m unittest discover -s gyms/AIRIS -v
    python gyms/AIRIS/airis_gym.py > AIRIS-01.json

## Native comparison (AIRIS-02)

Pin both the reference and generalized upstream implementation before executing either. At the generalized pin, class Airis(knowledge_json, state_graph_json) consumes JSON in pre_capture_input(s_input,u_input,actions,tasks), returns a JSON action, and receives observed JSON via post_capture_input(p_s_input,p_u_input,p_actions). Source: airis.py, lines 1–238. It opens relative log paths and redirects sys.stdout in initialization. Run it in an isolated subprocess with temporary working directory and its own logs; capture every input, action, prediction, outcome and budget. Verify the action schema and a no-op round trip before comparing. Native failure or unsupported planning/reset semantics must be recorded as BLOCKED, never replaced by a silent stub. The current finite solver is a separate arm.

Next: delayed/exogenous transitions, partial observation and evidence provenance; paired interventional aliases; expected decision value vs confidence under costly probes; independently generated development roots and preregistered sealed roots with EvalMath's mechinterp-power preflight. Export only public transition traces for downstream DataGoblin, MeTTa or recurrent controller training. Native upstream AIRIS and any learned router remain distinct arms with equal environmental observation budgets; report compute and verifier calls separately.

### AIRIS-02 pinned native smoke gate

Run with the exact upstream source file:
    python gyms/AIRIS/native_smoke.py /path/to/AIRIS-general/airis.py

The adapter verifies the Git blob (7ea338b80275e62f1f42ea073bdad452df3474f7),
uses an isolated child process and fixed random seed, allows only the no-op
action, and reports the actual API outcome. It executes the unmodified source;
a successful no-op is wiring evidence only. A failure records the failing stage,
exception and applied-action/observation counts. Source mismatch is a hard error.
At the pinned source, make_plan initializes an empty state_heap and the initial
heap pushes are commented out (roughly lines 285–295). The smoke gate determines
whether that is reached at runtime. Any repair must be a separately labeled arm,
with its own source fingerprint, never an invisible patch to the native baseline.
The dedicated native workflow publishes this gate's JSON independently of AIRIS-01.

## AIRIS-03: delayed causal rule discovery

See [TEMPORAL.md](TEMPORAL.md). Six-bit linear hidden mechanisms, two-step episodes, correlated passive observations, exact goal-identification certificates, matched trajectory/terminal sensor comparison and finite optimal acquisition. Native smoke workflow [45277428137](https://github.com/MoralityLabAI/EvalMath/actions/runs/45277428137) reported PASS_WIRING_ONLY with one action and one post-observation; the static heap concern was not reproduced in this runtime gate. No native learning result yet.

## AIRIS-04: hidden external drivers and sufficient memory

See [PARTIAL.md](PARTIAL.md). An unobserved Markov driver aliases immediate and delayed action effects. The full trajectory has an exact two-bit sufficient statistic; independent fair noise yields an identifiability impossibility. Matched three-transition episodes compare six exact acquisition/readout arms under known and unknown noise regimes. This remains a synthetic finite oracle and makes no native learning claim. AIRIS-03 [receipt replay](https://github.com/MoralityLabAI/EvalMath/actions/runs/45278195255) passed all 15 tests.
