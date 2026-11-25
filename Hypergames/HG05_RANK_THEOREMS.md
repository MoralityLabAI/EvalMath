# HG-05: Multi-output goal information rank and perfect semantic probes

**Evidence:** algebraic identities and exact independent finite oracles. Synthetic applied data are in GPTStoryworld HG-05. This extends HG-04's single-bit target theorem to multi-parity goal states, without physical quantum or neural-model claims.

## T1: Conditional goal information is a relative rank

For uniform X in GF(2)^d, let the observation be Z=CX and the k-dimensional goal code be Y=PX. Define h=rank([C;P])-rank(C).

**Theorem (algebraic identity).** Conditional on any feasible Z=z, Y is uniform on an affine space of exactly 2^h labels. Consequently H(Y|Z)=h bits and the maximum probability of guessing the complete target vector from Z is 2^(-h).

**Proof.** For any compatible x0, its observation fibre is x0+ker(C), with uniform mass. The goal labels in that fibre are Px0+P ker(C). Rank-nullity gives dim(P ker C)=rank([C;P])-rank(C)=h. The linear map from ker(C) onto its image has fibres of equal cardinality, so each possible label has probability 2^(-h). Predicting one label attains the bound; randomization cannot improve it. Dependent target rows and empty goal sets are included.

This is a complete-code accuracy result. A restricted classifier such as HG-05's signed, one-feature-per-bit decoder may perform worse even when h=0 because the ideal linear readout may require XORs of several observed features.

## T2: Perfect semantic audit lower bound and finite weighted cost

A perfect probe revealing one binary parity can increase the observation rank by at most one. Any probes making the whole target code identifiable must therefore include at least h independent new parity measurements. If the auditor can directly request independent target rows, this floor is attained in h unit-cost probes.

For available probe set E with positive rational costs w, the exact optimization is min over subsets F of E of sum(w_e) subject to rowspan(P) within rowspan(C together with F). The exact finite algorithm returns infeasible if no subset spans the goal. This is an offline information-access model; arbitrary probe restrictions need the weighted optimization.

For a one-shot synthetic release with reward +10, loss -15, and perfect audit cost c per missing bit, the Bayes value of blind guessing is 25*2^(-h)-15. Fully auditing is worth 10-c*h; abstaining is worth 0. These values are ceilings conditional on known dynamics, not a deployed agent's uncertainty estimate.

## T3: Padding and metric geometry

Extending C and P by all-zero columns preserves their ranks, h, target entropy and optimal complete-code accuracy. An observer rebuilt after padding may mix nuisance features into C and lose this property. The unit-weight HG-01 Clifford distance may meanwhile grow with nuisance Hamming distance while the factorized categorical Hilbert overlap decreases as (9/25)^Hamming. Neither representation distance alone establishes decision value.

## Verification and application

The executable exact module is \`src/spiral_ln/evaluation_hypergames_rank.py\`, with independent tests and the source-hashed receipt \`output/evaluation_hypergames/hg05_math_v1.json\`. The verifier checks 192 finite F2 fibre cases against literal enumeration and 128 rational-weighted audit cases with a separate explicit-world oracle; all ten checks pass locally. Full-unit tests additionally exhaust every pair of two-row observation and goal matrices for d=1..4. No Lean proof is claimed.

The applied registered public CPU sweep in GPTStoryworld uses 24 seeds, five dimension cohorts, ranks 1/2/4/8/16, 4/8/16 supervised examples, fixed versus expanding feature dictionaries, a shuffled-label arm, a target-excluded arm, and 100 rank-matched random draws. Its oracle dictionary contains exact goal parities as *unidentified candidates*, so observed results are conditional on this structural hypothesis class. The private HG-03 model-evaluation seeds remain untouched.

Reproduce: \`PYTHONPATH=src python -m unittest discover -s tests -p 'test_evaluation_hypergames_rank.py' -q\`, then \`python scripts/check_receipts.py --only hypergames_rank\`.
