# AIRIS-07: chronology-sensitive causal discovery and DataGoblin curriculum

AIRIS-06 completed all nine CPU training runs:
https://github.com/MoralityLabAI/EvalMath/actions/runs/45282821342.
Long-history mean regrets (three seeds): tied .01183115, reset .00413154,
histogram .00505207, tied inference reset .00460510, fixed pulse .00508487,
uniform .01033330. Primary target (tied beats reset by .01 absolute regret)
failed. One grammar, PILOT_ONLY; no identified cause of the regression.
This motivates a controlled change to the task, not a claim that recurrence
will succeed.

## Environment

AIRIS-04 uses fixed target theta in F2^2. Now let theta evolve between
three-transition episodes: with probability k/4 resample a uniform target,
otherwise keep it. k in {0,1,2,3} is supplied publicly. Within an episode the
target is fixed and the independent hidden driver flips at rate 1/4.
The agent sees its three committed action bits and three observed bits.
The exact likelihood L_a(d|theta) of temporal differences is inherited from
AIRIS-04. Prior theta is uniform. The transition kernel is

    K_k(i,j) = (1-k/4) 1[i=j] + k/16.

For current unnormalized mass w, prediction is K_k^T w, and the observation
update is coordinatewise multiplication by L_a. The next-experiment score
is sum_d max_j [(K_k^T w)_j L_a(d|j)] / sum(w). The objective identifies the
mechanism active in the next episode, not an obsolete historical target.
Each candidate costs three transitions. No free observations or mechanism IDs.
The raw lift y0=0 is a deliberately selected public representation of each
difference pair, with no extra information under the model.

Evidence revocation replaces an observation by a missing likelihood factor
but retains its physical time slot and transition kernel. Deleting the slot
would change the modeled process. The independent oracle sums over all
hidden target paths and independently enumerated AIRIS-04 driver paths.

## Exact chronology lower bound

Consider paired histories h=(i,j,l), h'=(j,i,l) with i<j, where event IDs
range over the 8 schedules times 4 difference observations. Both histories
have the same multiset and last event. For an order-invariant policy (even
with the last event supplied) the action distribution must be identical
for the two inputs. With equal presentation weighting its average regret
is at least

    rho(h,h') = min_a [(max_b Q(h,b)-Q(h,a))
                       +(max_b Q(h',b)-Q(h',a))]/2.

This is an exact bound, including randomized policies since the loss is
linear in the shared distribution. rho>0 iff the optimal action sets are
disjoint. Stationary k=0 updates commute and rho=0 for every pair.
Positive rho establishes a representational separation on this interface;
it does not identify a neural mechanism. A last-event-only controller
also cannot separate these pairs. Recurrence is one way to encode chronology;
an order-aware feedforward control is essential in a future learned comparison.

Census: 15,872 paired histories at each rate (32 choose 2 times 32).
Report all pairs, strict pairs, their conditional mean lower bound and
maximum lower bound. These are exact constructed cases, not independent
experimental samples. Conditioning on strict pairs is deliberate curriculum
selection and cannot be used to claim prevalence on natural trajectories.

## DataGoblin handoff

Export two presentations per root per rate. For k=1 strict pairs, group by
canonical first-two permutation class including the last event; hash assigns
80% of groups to train candidates and the remainder to unlabeled development.
Include matched k=0 stationary presentations with the same group and split.
k=2 is an unseen development rate; remove any key occurring in training.
There are no k=3 strict pairs in this census. No evaluation or steward roots
are materialized. DataGoblin already has a separate AIRIS curation program;
this namespace is evalmath-airis07-candidate-v1.

Train rows contain public input and exact all-action rational teacher values,
plus the complete optimal action set. No target ID, hidden path, or evaluator
label on development rows. Every row has training_ready=false. Root IDs
bind the rate and observation group; group IDs enforce cross-rate split
isolation. Train manifest binds training JSONL bytes. Deliver only
train_candidates.jsonl and train_manifest.json to a builder; keep development
and research receipt in steward/research custody. Public oracle code makes
this a development benchmark, not a secret or sealed evaluation.
Candidate admission remains DataGoblin's responsibility.

Run:
    python -m unittest discover -s gyms/AIRIS -p test_nonstationary.py -v
    python gyms/AIRIS/curriculum.py --out /tmp/airis07

Next: train an order-sensitive router with identical observation budget,
compare with histogram+last (the structural null), matched ordered flat MLP,
and exact chronological filter. Include unbiased random histories and
counterfactual pairs as separate endpoints. Before mechanism claims,
design independent generator families and sham controls and use the
EvalMath preflight; no power claim from these related histories.
