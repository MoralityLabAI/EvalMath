# AIRIS-06: tiny tied recurrent experiment selector

Registered CPU development pilot, one finite synthetic grammar. No sealed
independent generator families, no mechanistic inference or AGI claim.
AIRIS-05 native MeTTa checks the causal memory contract; this model is trained
on AIRIS-04's independently tested exact teacher, with no native calls in
the training loop. It predicts experiment values from raw public histories.

## Data and target

Use AIRIS-04 mixed prior over twelve hidden models. Independent simulated
episodes follow the declared Markov-driver grammar. Draw one hidden model
per history and sample public schedules uniformly; sample fresh hidden
noise per episode. Each event supplies six raw bits (three actions and
three observations), no true coefficients, noise regime, sufficient
statistic, posterior vector, root index or teacher choice in the input.

Generate 12,000 short candidate histories (length uniformly 1–3) using
seed 106; deduplicate exact public histories. Compute a canonical posterior
weight vector by dividing by the GCD. Hash the canonical vector to a fixed
train/short-development split (bucket 0 of 5 is short). Generate 4,000 long
candidate histories (length 4–6) with seed 107; exclude every canonical
posterior that occurs in the short pool. Deduplicate. The split prevents
exact posterior leakage, including order and raw-complement equivalences.
Different posteriors still share one generator grammar; these are not
independent held-out task families. Archive counts, hashes and public histories.
The long set is a compositional/length diagnostic, not a sealed confirmation.

Given public history h and action a, Q(h,a) is the expected MAP recovery
probability after one more three-transition experiment. Label all eight
candidate schedules exactly with integer numerators and common denominator.
Train on 16*(Q - mean_action(Q)) using MSE; the centering/scaling preserves
argmax. Score exact regret max(Q)-Q(chosen) including all tied optimal actions.
Per-row rational regret is archived; aggregate mean and macro means over
posterior groups are floating-point summaries. No hidden-label accuracy
or teacher top-1 agreement is the primary endpoint.

## Matched controls

Tied: 24-wide state, six-bit event embedding, two iterations of the same
residual block per event. Its parameters are tied across all inner visits
and outer history positions. This is an original tiny residual recurrent
controller, not a claimed implementation of a published TRM architecture.
Reset: same architecture and count, trained with memory reset before each
event. Tied inference reset: same trained tied checkpoint with the history
state zeroed before each event, a distribution-shifting diagnostic only.
Histogram: order-invariant counts over all 64 possible raw event types,
two 22-wide layers; nearly matched parameters (2,120 vs 2,144), and access
to all events. This is a strong control because exact AIRIS-04 likelihood
products are order-independent. Compute is reported as two tied inner visits
per valid event vs a two-layer MLP; parameter matching does not imply equal
FLOPs. Exact full and last-episode Bayes selectors, fixed pulse and uniform
random action expected regret are reference baselines.

Train the three models for 24 epochs, batch 256, AdamW lr .003, weight
decay .0001, seeds 101/103/107, fixed schedule, no early stopping or test-driven
checkpoint selection. CPU, torch 2.6.0, one thread. Archive all nine final
checkpoints, epoch losses, public data, all chosen actions, all per-case exact
regrets, and source hashes. Uniform reference uses expected per-case regret;
its zero-regret fraction counts histories on which every action is optimal.

## Preflight and limits

Per EvalMath mechinterp-power: this is PILOT_ONLY. Independent generator
family count = 1; rows and posterior groups are clustered observations,
seeds are repeated training runs. Primary contrast = long-history regret
of tied vs trained reset; minimum useful development gain = 0.01 absolute
regret; histogram and fixed pulse are additional registered competitors.
The inference reset dose is full 24-D state zeroing before each event
(excluding the current event); no donor/null or matched sham calibration
exists. No mechanistic floor, power, p-value, familywise confidence or
causal-memory claim is authorized. Report all comparisons and seeds;
use independent development families and matched shams with the preflight
planner before opening any separately registered confirmation roots.
The structural exact oracle is a ceiling, not a neural achievement.

Run:
    python -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
    python -m unittest discover -s gyms/AIRIS -p test_router.py -v
    python gyms/AIRIS/router.py --out airis-router-output

Future AIRIS-07: export a teacher/student public trace curriculum to
DataGoblin, including mechanism-changing generator families, evidence
revocation and nonstationary hidden dynamics. Freeze prospective roots
before any training on those families.
