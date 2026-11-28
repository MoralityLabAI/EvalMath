# AIRIS-04: hidden drivers and the causal value of memory

Evidence class: exact finite synthetic development. The native upstream agent and
neural controllers are separate future arms. AIRIS-03 allowed independent
intervention on external drivers; here the agent can never see or set the driver.

## Contract

For three transitions in one episode, observe

    y_t = alpha*a_t XOR beta*a_(t-1) XOR u_t

with a_(-1)=0 and fixed unknown theta=(alpha,beta) in F2^2. The hidden driver
starts each episode as a fresh fair bit. It flips independently at each of the
two internal steps with probability p in {0,1/4,1/2}. The regime is fixed across
episodes; it may be known, or inferred under a uniform prior on all three
regimes. The target prior is uniform and independent of the regime.
The agent commits a binary three-action schedule before the episode starts.
It may adapt schedules across episodes using only public observations.
Every episode costs three physical transitions; no free queries or hidden
driver access. Readout modes change the information supplied after the same
intervention schedule. These are sensor/representation ablations; a learner
given a complete trajectory would be free to compute any statistic of it.

## Exact memory theorem

Since u_t is marginally fair, the final y is independent of theta and p for
every fixed schedule, including schedules selected from earlier episodes.
For fresh independent episode resets, repeated last-only observations cannot
update the target prior. Full iid fair noise (p=1/2) makes even a full trajectory
independent of theta. This also holds for causal within-episode action policies
in that regime: conditional on the prior public history and chosen next action,
the fresh fair noise makes the next observation fair.

For a fixed schedule a=(a0,a1,a2), take d=(y0 XOR y1,y1 XOR y2).
Let f1,f2 be the driver flips. Then

    d1 = alpha*(a0 XOR a1) XOR beta*a0 XOR f1
    d2 = alpha*(a1 XOR a2) XOR beta*(a0 XOR a1) XOR f2.

The initial fair bit makes y0 independent of (theta,p,d), hence the full
trajectory likelihood is exactly half the likelihood of its two-bit
difference statistic. This is sufficiency for the joint target-and-regime
posterior, and it persists across independent episodes and adaptively selected
schedules. A learner can compute this online using the previous observation
and an accumulator, with the schedule and episode clock supplied. The retained
terminal statistic has two bits; the online transducer's working memory is a
separate question.

At p=0, the pulse (0,1,0) gives (alpha,alpha XOR beta) exactly. With four
equally likely targets, any single-episode zero-error terminal code must have
at least four distinguishable symbols, i.e. two bits. The last-only statistic
has zero information; keeping just the first difference identifies alpha
and leaves beta unknown. At p=1/2, even unlimited history cannot help under
this model. For 0<p<1/2 the pulse gives two independent noisy parity
measurements; repetition improves inference, but exact finite certification is
impossible because every possible target has positive likelihood.

## Registered exact comparison

Four regime priors: each of the three known rates and the uniform mixture
(12 models). Six acquisition/readout arms: repeated pulse with both differences,
only first difference, last observation, repeated passive zero actions with
both differences, greedy one-episode expected MAP, finite-horizon Bellman
optimal expected MAP. The last two use both differences and choose among all
eight action schedules before each episode. Ties use the declared order with
pulse first. Compare 0–3 episodes (0–9 transitions). All methods spend the
full registered budget. No statistical sample-size or generalization claims.

Integer likelihood rows have common denominator 16. The posterior weight vector
is kept exactly without normalization. At termination, sum weights by target;
the maximum target mass is the expected correct-decision numerator. For
Bellman-optimal acquisition, recurse over the outcomes, sum their values, and
maximize over the eight schedules. Divide by prior total mass times 16^N.
This is an exact finite optimal policy among episode-committed schedules.
Certificate success counts posterior fibres supported on a single target.
The optimal/greedy arms choose according to MAP, even when reporting certificates.
Independent path enumeration checks every likelihood cell, sufficiency, and
fixed-pulse expected MAP over every transcript up to three episodes.

Under the mixed prior, the p=1/2 regime remains compatible with every finite
transcript for every target, so there is no zero-error certificate even when
posterior MAP is high. A future gym should report regime misspecification and
certification separately rather than treating high confidence as ground truth.

Run:
    python -m unittest discover -s gyms/AIRIS -v
    python gyms/AIRIS/partial.py > AIRIS-04.json

The receipt contains all channel matrices, their model ordering, exact policy
scores, and source fingerprints. This finite domain is development-only. No
sealed evaluation, trained memory, native AIRIS learning, or Lean theorem
claimed. For a recurrent implementation, expose the raw ordered y stream and
schedule only, compare learned compression to the exact sufficient statistic,
and split independent generator families before training. Test longer delays,
nonstationary regimes, hidden state with action-dependent transition kernels,
and out-of-grammar noise. The two-bit representation is a structural ceiling
for this particular grammar, not an empirical target for general cognition.
