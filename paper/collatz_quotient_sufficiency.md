# CLQ-01: Collatz quotient sufficiency and feedback collisions

Status: algebraic proofs below; finite verified examples in the generated receipt. No Lean kernel check or neural experiment has been run. Derived from the supplied three-page note *Three cycles and their exact basins in a Collatz-like map* and its quadratic-reciprocity extension; priority against the literature is open.

## Model and theorems

Fix a positive integer d = 1 mod 4 with gcd(d,6)=1. T(n) is n/2 for even n, 3n+d for n=1 mod 4, and n+d for n=3 mod 4. Let R be the next-odd map. Both odd branches produce multiples of four, so R(n) <= (3n+d)/4. For n>d this decreases n, and for n<=d it stays within the finite odd region S={1,3,...,d}. Thus every positive input reaches a cycle. The cycle label B(n) is its minimum (necessarily odd), and the period counts all individual T steps.

Let H=<2,3> in the units modulo d, acting on every residue, including zero and nonunits. Write Z(n) for the orbit of n mod d under H. Every T step multiplies the residue by 2^(-1),3, or 1. Thus Z is conserved. Every residue has a positive representative and hence its orbit contains at least one cycle. The number of orbits is

    sum_{q|d} [ (Z/qZ)^* : <2,3> ],

where q=1 contributes one. Indeed, the stratum gcd(n,d)=g=d/q identifies with units modulo q by dividing by g, and the action reduces to that of 2 and 3 modulo q. No assumption about commutation of the integer dynamics with division by g is needed.

The classifier B=f(Z) exists exactly when every orbit has a unique cycle. For a squarefree d with k prime factors, projecting H to the Legendre signs yields the weaker coprime lower bound 2^(k-rank_F2(v2,v3)). Higher power characters can also survive. For primes splitting completely in Q(zeta_lcm(4,r), 2^(1/r), 3^(1/r)), Chebotarev gives arbitrarily many p with d=p and coprime orbit count at least r. This uses the standard splitting theorem; no formalization or priority claim is made.

### Constructive obstruction for every fixed modulus

If two cycles a,b occupy the same Z orbit, then for every positive M there are positive odd x,y congruent modulo M in their distinct basins. This strengthens the simple quotient insufficiency statement into a witness generator for every modular classifier.

For k>=2 sufficiently large, A_k(n)=2^k*n-d is positive and 3 mod 4. One T step followed by k halvings sends A_k(n) to n. Its effect on the residue modulo d is multiplication by 2^k. Let t=ord_d(2), using t=1 for d=1. Varying k by multiples of t can realize multiplication by 2, any power of 2, or the identity.

To realize multiplication by 3^(-1), first apply A_k with k divisible by t if n is zero modulo 3; its result is nonzero modulo 3. For a nonzero n modulo 3 choose k>=2 with the parity making 2^k*n=d mod 3, and increase k by even increments until the following predecessor is positive. D_k(n)=(2^k*n-d)/3 is then 1 mod 4 and one T step plus k halvings returns n. Its effect modulo d is multiplication by 2^k/3; a subsequent A_l with l=-k mod t cancels the factor 2^k. Since the group is finite, these operations can reach every residue in the same orbit while remaining in the original basin. Lift b to y with y=a mod d and set x=a.

Write M=2^e*m with m odd, L=lcm(m,d). Choose k>=max(2,e) divisible by ord_L(2) and large enough for both predecessors to be positive. Applying A_k to x and y sends both to -d modulo 2^e and translates each residue modulo L by -d. Since their difference is divisible by d, repeat A_k on y exactly ((y-x)/d) mod (L/d) times, using the post-first-step x,y for this formula. The final x,y agree modulo L and modulo 2^e, hence modulo M. Every step is an inverse path in its original basin. This proves the claim, including noncoprime strata. Therefore an exact classifier periodic modulo some fixed positive modulus exists iff every quotient orbit contains one cycle. It says nothing about arbitrary nonperiodic binary automata or finite-state transducers.

## Evaluation feedback

Population U_d consists of odd integers in [1,2d-1], exactly one representative per residue mod d. This population is finite; its basin frequencies are not asserted to be natural densities when the quotient is insufficient. Define N(z,b)=#{n in U_d : Z(n)=z, B(n)=b}. The optimal exact 0-1 classifier receiving Z has accuracy sum_z max_b N(z,b)/d. In an ambiguous fibre, a balanced binary test of two different basins gives any Z-only predictor a 1/2 ceiling. All ceilings assume no other information about n reaches the predictor.

Reference cases: d=13,73,97,265,577,601,7081. The first is a collision control; 73/97/265/577 are sufficient; 601 has two ambiguous fibres and 7081 one. In the d=601 fibres, counts are 48:27 and 27:48, giving a 36% conditional error on each under U_d. For the entire population its ceiling is 547/601; for coprime inputs it is 91/100. For d=7081 the ceiling is 6805/7081.

## Reproducible certificate

The accelerated odd graph and an independent full-step walk agree on labels and exact periods. Census all positive d<=2001 satisfying the hypotheses, plus d=7081; check every odd lift in U_d. Validate inverse-path collisions across nine declared modulus choices for each ambiguous reference class. Check deterministic 64-, 256-, and 1024-bit inputs. Receipt includes source hashes and witness hashes (reconstruct witnesses via collision(d,a,b,M)).

    PYTHONPATH=src python -m unittest discover -s tests -p test_collatz_quotient.py -v
    python scripts/verify_collatz_quotient.py

These checks do not constitute a proof for all parameters; the algebraic proofs above have separate evidence status. A future Lean certificate should prove descent, residue action, finite orbit coverage, fibre criterion and both inverse branch identities, then formalize the arbitrary-M construction. No sorry/axiom or numerical-to-general substitution is acceptable.

## CLQ-02 prospective neural protocol (external gym)

Public diagnostic moduli are the seven examples above; exclude them and their multiples from the sealed split. Generate and freeze independent modulus-level train/validation/test manifests before training. Hold out entire moduli and track shared prime factors; report a separate factor-disjoint generalization split. Generate raw binary n,d and exact basin label, quotient label, full period, and step count with this oracle. Do not place target-derived information in raw-input prompts. For variable d use cycle minimum as the integer target or same-basin pair discrimination, not arbitrary class IDs that transfer poorly.

Compare a fixed-depth equal-parameter network, a tied recurrent network, an explicit modular quotient oracle (with its population-dependent ceiling), an accelerated symbolic oracle, and a finite-region lookup oracle with the cost of reaching that region charged. Report bit lengths, full and odd step counts, FLOPs/latency, accuracy by quotient sufficiency and ambiguous fibre, and abstention. Train on 8-32 bit n; evaluate 64/256/1024 bits, keeping arithmetic encoding consistent. For collision controls use exact same-residue pairs, both same-basin and different-basin, balanced labels, matched bit lengths and controlled branch/path length; the simple witness generator alone does not guarantee matching or balanced sampling. Keep construction metadata hidden. Include shortcut probes for d, n length, residue, and generation method. Test whether additional recurrence helps on ambiguous fibres at equal total compute. Probe Z and residual basin labels on held-out moduli; causally intervene on quotient activations using matched examples, with random-direction, norm-matched and sham interventions. A quotient probe alone does not establish mechanistic identification. No neural result is claimed here.
