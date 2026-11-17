# HG-07: raw-state observability and parity-learning bounds

Companion mathematical task for GPTStoryworld's frozen HG-07 public CPU trial. Characterize exact GF(2) posterior uncertainty of sparse goal parities after n labeled random raw state examples. In particular, if X (n×d) is the training design and p the unknown parity vector, the consistent hypothesis fibre is p+ker(X); its cardinality is 2^(d-rank(X)). Given an independent fresh uniform x, any two distinct parity hypotheses differ in label with probability 1/2. When the prior is uniform on all parity masks, the optimal posterior test-label prediction under nonzero nullity has accuracy 1/2 on genuinely novel non-rowspace observations.

For a prior restricted to six-sparse masks, finite label collision bounds follow from a union bound over (choose(d,6)-1) false masks with 2^-n collision probability. This is a sufficient sample bound for sparse identification, not an assertion that the neural solver recovers the mask. Verify independent small d finite enumerations, zero padding, n=0, zero rank and full-rank cases. Report closed-form sample bounds and separate trained-model measurement.

All proposed theorems should remain exact-rational or finite-enumeration checked; no Lean proof is claimed until separately kernel checked.
