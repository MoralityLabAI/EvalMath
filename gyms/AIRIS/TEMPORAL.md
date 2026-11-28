# AIRIS-03: delayed causation, interventions and temporal readout

Evidence: exact algebraic argument and exhaustive finite synthetic development.
This is an EvalMath reference mechanism, separate from the native AIRIS arm.

## State and cost

Let x_t=(a_t,u_t,v_t) in F2^3. The scalar cumulative observable follows

    s_(t+1) = s_t + alpha*a_t + beta*a_(t-1)
                       + gamma*u_t + delta*u_(t-1)
                       + epsilon*v_t + zeta*v_(t-1)     over F2.

The fixed hidden vector w=(alpha,beta,gamma,delta,epsilon,zeta) is uniformly
distributed over all 64 vectors. Each episode starts with s=0 and previous
input zero, then consumes two transitions. The simulator can independently set
all three inputs for active probes. This is a strong explicit intervention
contract, not an assumption about real external drivers. Passive training
consists of the two-step correlated episode x=(1,1,1) twice, with both cumulative
observations. Every policy receives that same episode. Active probes are the 64
ordered pairs of three-bit inputs. A trajectory probe reports both cumulative
observations; a terminal probe reports just the final cumulative state. Both
cost two transitions, and reset is a declared free boundary operation.
A budget is a maximum; stop early on a certificate and log actual costs.
No noise, unknown delays, latent drivers, or distribution shift yet.

## Algebra

A query returns linear functionals of w. Let R be the F2 row span of all
observed design rows. The compatible worlds form an affine fibre w0+R^perp.
For T=span(e_alpha,e_beta), the agent's two-tap response is identified exactly
iff T is contained in R. Proof: a linear functional is constant on a nonempty
fibre iff it annihilates R^perp, and (R^perp)^perp=R. More generally the set
of compatible target responses has cardinality 2^(dim(T)-dim(T intersect R)).

The passive trajectory has rank 2, intersection rank 0 with T, and four fibres
of 16 worlds each. All four action-response vectors remain possible in every
fibre. Under the uniform prior, a new query with row-rank gain d has 2^d
equiprobable outcomes, and pairwise collision discrimination 1-2^(-d).
Therefore uncertainty reduction in the full world vector can be irrelevant to
the agent's own causal action response.

An action-only pulse with both cumulative readouts gives alpha then alpha+beta,
identifying both coefficients in two transitions. A terminal-only episode adds
at most one row, so it cannot identify the two missing target dimensions in
one episode. Two suitably chosen episodes suffice (action pulse plus action only
on the second step). This is an exact lower bound under the declared interface.
It isolates the cost of temporal observation without changing the action budget.

## Registered development census

Compare fixed informative order (nuisance pulses first), uniform informative
ordered input pairs, collision-optimal with uniform random tie-breaking,
target-intersection-greedy, and finite Bellman-optimal. Primary endpoint is
certification of the two-tap action response. Budgets 0/1/2 active episodes,
both readout modes. Every trajectory counts as one root, not two replicates.
No confidence intervals or empirical claims are inferred from the finite census.
The row-space Bellman recurrence is valid here because available design rows
and target identifiability do not depend on the observed values. Its exact
randomized-policy values integrate all choices rather than sampling a seed.
The independent simulator enumerates literal compatible worlds to check
the row-span certificate, probability partitions, and the returned response.

The receipt contains exact rational policy values, all 64 roots' goal-directed
traces at both modes and budgets, source fingerprints, and actual active costs.
Public histories are separate from hidden root IDs; any downstream learner must
receive only the public history and a split-specific label, never the hidden
coefficient index. No sealed split or neural training is claimed.

Run:
    python -m unittest discover -s gyms/AIRIS -v
    python gyms/AIRIS/temporal.py > AIRIS-03.json

## Next experiment

AIRIS-04: remove intervention access to one driver, hide its observations,
and test whether finite histories suffice to identify the action effect.
Compare an exact partially observable version-space agent, a memoryless
predictor, and a history-aware rule learner. Freeze independent generator
families and sham controls before using a learned router.
