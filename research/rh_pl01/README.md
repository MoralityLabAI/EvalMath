# RH-PL-01: Proof-length frontier, obstruction packing

Status: exploratory registration and exact finite synthetic control, 2026-11-25.
No numerical RH/ZFC lower bound, ZFC derivation, or Lean kernel theorem is claimed.

## Target contract

The eventual target is the shortest additive-length proof of a fixed closed
first-order ZFC formula expressing RH. Proposed baseline: a Hilbert calculus
with modus ponens and generalization; logical and nonlogical axiom schemas
must be explicitly fixed. Use pure membership and equality, variables indexed
by natural numbers, ASCII prefix grammar (e/m for equality/membership, n for
negation, i for implication, a for universal quantification; variables v followed
by i copies of 1 and a terminating 0). Each proof line is one fully expanded
formula plus LF. Axioms and inference references are implicit and checked by
the verifier. Formula macros and external theorem libraries are excluded from
the charged proof. This is a candidate serialization, not a completed frozen
ZFC verifier. Freeze the exact axiom list, substitution conditions, target
bytes, equivalence proofs and verifier hash before reporting numeric results.

Use two targets: analytic RH and an arithmetic nonhalting formulation, each
expanded independently. Yedidia and Aaronson (2016) provide a 5,372-state
machine halting iff RH is false; pin the exact machine and verify its ZFC
equivalence before using it. The recent Lean proof and its declarations are
upper-bound search material, not a ZFC proof in this encoding. Its standard
type theory has a universe hierarchy; audit dependencies for elimination of
stronger assumptions.

## Exact finite reduction

Let V be a finite formula universe and R the complete set of ground
inference instances under consideration, each with a finite premise set,
one conclusion, and positive additive cost. Axiom rules have empty
premises. Start from the empty set. Premises may be reused. For each U
subset V containing the goal g, define delta(U) as the rules with conclusion
in U and all premises outside U.

Every proof uses at least one member of delta(U), by its first line in U.
Conversely if a selected rule set hits every delta(U), its least forward
closure contains g: otherwise the complement of that closure is a missed cut.
Consequently minimum proof cost equals the integer minimum of sum c(r)x(r)
subject to sum over delta(U) x(r) >= 1, x in {0,1}. Repeated conclusions and
repeated rules can be removed without losing derivability, and closure orders
the chosen rules. Costs must charge each inference, including its conclusion.
For the proposed Hilbert encoding they depend only on the conclusion bytes
plus LF. The result assumes no omitted global conditions; encode any needed
contexts explicitly as states.

A rational packing y(U) >= 0 with sum of y(U) over cuts crossed by each r
<= c(r) gives a lower bound sum y(U). With integer costs round upward.
To certify a lower bound B in the full calculus, the formula universe must
include every formula that could occur in a proof of cost <= B, and every
eligible inference instance. A subgraph of the known proof supplies only a
restricted optimum, not a global lower bound. Use a sound overapproximation
if full enumeration is impossible. For integer cut generation, compute the
closure of a candidate rule set and add its complement as a violated cut
when the goal is unreachable. Fractional separation needs its own oracle.

## Synthetic calibration

Each of k disjoint blocks has 3 source axioms and 3 elements, each element
derivable from either of 2 sources. Every source covers exactly 2 elements.
The sole goal rule requires all 3k elements. All rules cost 1.

Any proof needs 3k element lines, 1 goal line, and at least 2k sources
(one source covers only two elements per block). Choosing two per block
attains 5k+1.

Packing: weight 1 on {g}; for each element e, weight 1 on {g,e} and
weight 1/2 on {g,e} union its two source neighbors. Each rule has load <=1.
Total = 9k/2+1. The fractional primal x=1/2 on every source and element
rule and x=1 on the goal is feasible: if a cut includes no element, the
goal rule crosses; otherwise choose an element inside and for each of its
two sources either the source axiom or its element rule crosses. Thus the
dual packing optimum is exactly 9k/2+1 for every k. The integrality gap
persists after rounding for k>=2.

Local run (Python standard library, exact Fraction arithmetic):
| blocks | exact cost | optimal fractional packing | ceil | independent BFS |
|---:|---:|---:|---:|---:|
|1|6|11/2|6|6|
|2|11|10|10|11|
|3|16|29/2|15|not run|
|4|21|19|19|not run|

All 64 and 4096 target-containing cuts checked for k=1,2 respectively.
For k=3,4 exact source subset enumeration and dual feasibility checked;
all-cuts feasibility follows from the argument above. Overweight certificate
rejection passed. Reproduce: python research/rh_pl01/control.py.
Local source SHA256: b8b296ec210f0bae273deb34e28ce0c84abd5f5d30772a7b4ebd14c2f65ba12f.

## Transfer and next gates

In the additive Hilbert encoding, concatenating proofs of A and A->B and
appending B gives L(B) <= L(A)+L(A->B)+cost(B). Thus a lower bound for B
transfers to A after subtracting a certified upper bound on the implication
and the last line. The same sandwich compares RH encodings. Pudlak's finite
consistency lower bounds motivate targets, but RH-to-consistency implication
and its cheapness have not been established. No general matrix multiplication
circuit lower bound transfers without a resource-preserving reduction.

1. Freeze and test the pure first-order ZFC verifier and explicit arithmetic RH
   target; implement exhaustive small-formula controls including substitution,
   quantifier and equality errors.
2. Build a proof translation manifest for the Lean upper bound. Start with the
   240-declaration blueprint, audit universe levels, all external lemmas and
   exact dependency closure. Pin source hashes. Count expanded proof bytes only
   after translation and checking.
3. Build integer cut generation and exact rational certificate checking; test
   omitted-rule leakage and integer gaps. Any proposed symbolic cut family
   for RH must cover every permitted inference, including alternative lemmas.
4. Establish a bound beyond the syntactic target floor; separately report
   restricted-system bounds, unconditional global bounds, and conditional
   results. Register budgets before search. No model-score claim.

## Sources

- Michael Rubinstein, verification record and working reconstruction:
  https://www.math.uwaterloo.ca/~mrubinst/alpoge_claude_grh/
- Igor M. Zhuk, 240-declaration kernel index, 2026-11-25:
  https://hexagonmath.org/pdf/2611.01031v1
- Yedidia & Aaronson, A Relatively Small Turing Machine Whose Behavior Is
  Independent of Set Theory, 2016: https://scottaaronson.com/busybeaver.pdf
- Pavel Pudlak, finite consistency proof length:
  https://users.math.cas.cz/~pudlak/fin-con.pdf
- Sanford Buss, survey of Parikh's length-of-proof work:
  https://mathweb.ucsd.edu/~sbuss/ResearchWeb/parikh/paper.pdf
