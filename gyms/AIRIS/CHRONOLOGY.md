# AIRIS-08: learn the chronological filter

Status: registered public development pilot on the same finite grammar as
AIRIS-07. Not a sealed evaluation or a mechanistic claim. AIRIS-06 failed
its recurrent primary contrast. AIRIS-07 now supplies a strict representational
null: same multiset, same final event, disjoint optimal action sets.

## Data and custody

Start from AIRIS-07's fixed training/development curriculum. Discard training
presentations whose full event multiset occurs anywhere in paired development,
including across drift rates. Keep paired development unchanged. Add ordinary
simulated histories of three episodes using independent hidden noise and
hidden mechanism resampling. Draw 12,000 training candidates (half k=0, half k=1)
from fixed seeds 8200/8201. Retain non-development bags outside hash bucket 0.
Draw 4,000 ordinary development histories per rate k=0,1,2 from seeds
8300+k; retain bucket 0 and exclude all surviving curriculum bags. Retain
multiplicities of ordinary draws. This endpoint is a conditional random sample,
not an unbiased estimate of the unconditional environment distribution.
All history permutations across rates are grouped by full sorted event
multiset, with no train/development overlap. Paired rows repeat four times
in optimization; ordinary retained rows once. Report original and weighted
counts. Paired and ordinary development are distinct endpoints. k=2 is absent
from training. Data are synthetic research fixtures, not admitted DataGoblin
training assets; DataGoblin's candidate-only intake remains separate.

Each public event is encoded by the one-hot index of its action schedule and
two observed temporal differences (32 possibilities). This is an exact,
public sufficient observation statistic from AIRIS-04, given to every arm.
No hidden state, posterior, teacher choice or observation-group identity is
an input. The rate k/4 is public. Every history has 3 episodes, and the next
experiment costs 3 physical transitions. Teacher Q is the exact expected
next-mechanism MAP probability. Center per row and multiply by 32 before MSE.
Evaluate regret max Q - Q(chosen), including every tied optimum.

## Models

Gated recurrent: 21-dimensional bounded state, shared event embedding and
two tied inner gated visits per event; gate blends old state and a bounded
candidate. Ungated residual: 24-dimensional shared residual block as in
AIRIS-06, adjusted input embedding. Trained reset: same gated architecture
and budget, state reset before each event. Gated inference reset is a
distribution-shifting ablation, not a matched causal sham.
Ordered flat: all three one-hot event vectors in order and rate; two 21-wide
layers. Hist+last: multiset counts, last event and rate; two 27-wide layers.
Parameter counts 2,696/2,792/2,696/2,696/2,762. Matched capacity within 4%,
not matched compute; recurrent visits=6, flat hidden layers=2.
Exact full chronological filter, exact last-only selector, fixed pulse,
uniform expected regret and exact paired orderless optimum are references.
Orderless floor is attained by the paired oracle that knows the first-two
multiset and last event. Assert the trained histogram and both reset arms
make identical choices within each pair and cannot beat that floor.

Three seeds 101/103/107, 32 epochs, 256 batch, AdamW lr .003, wd .0001,
torch 2.6.0 CPU and one thread. All 15 training checkpoints are fixed before
evaluating the development scores, no selection or early stopping. Store
all model choices, rational per-row regrets, public inputs, checkpoints,
source hashes, epoch losses, split stats and parameter counts. In ordinary
evaluation report mean regret; in paired evaluation report mean regret,
oracle floor, fraction of pairs both optimal, and fraction of different choices.

## Registered interpretation

Primary: on k=1 strict paired development, mean gated regret across all
three seeds at least 0.0005 below the exact paired orderless floor and lower
than the trained reset. This is a descriptive target for the selected finite
pairs. Also report every seed against ordered flat and residual, plus all
ordinary, stationary, and unseen-rate results. No recurrence-specific win
if ordered flat does as well. No model claim if the primary gate fails.
The structural null floor is an exact bound, not a matched-sham empirical
confidence threshold. Independent generator family count=1. Multisets,
histories and training seeds share the grammar; do not use them as independent
causal replications. No mechanistic p-value, power calculation, sham
calibration or held-out causal transfer authorized. Before a stronger study,
register genuinely independent mechanisms (different delay, state dimension,
action-dependent transition kernels), matched memory perturbations, and
EvalMath's mechinterp-power preflight with sealed roots.

Run:
    python -m pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu
    python -m unittest discover -s gyms/AIRIS -p test_chronology.py -v
    python gyms/AIRIS/chronology_router.py --out airis08

DataGoblin integration: upstream AIRIS-07 training artifact was independently
checked in DataGoblin workflow 45285549008. AIRIS-08 is an EvalMath-local
synthetic development experiment; this does not authorize training admission
of the DataGoblin candidate bundle.

## AIRIS-08a: numerical inference contract

The first dedicated run [45285908794](https://github.com/MoralityLabAI/EvalMath/actions/runs/45285908794) stopped before optimization: a bitwise equality assertion on identical model-visible features was stricter than floating-point BLAS arithmetic. A local CPU reproduction observed differences of order 3e-8. The revised test uses a numerical tolerance for logits. To preserve the exact structural information bound at decision time (including a near tie), evaluate one representative per model-visible key and broadcast its selected action. Reset keys are (rate,last event); histogram+last keys are (rate,sorted multiset,last event); ordered keys are (rate,ordered events). No teacher value, group label or hidden state enters this mapping. The training data, architectures, optimization, seeds, exact scoring, and registered primary gate are unchanged. No training result from the aborted run exists.
