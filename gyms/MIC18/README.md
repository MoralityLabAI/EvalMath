# MIC-18: memory constrained at every update

**Evidence:** exact finite domain, with elementary counting arguments stated
separately. Protocol commit:
[`9bf11c5`](https://github.com/MoralityLabAI/EvalMath/commit/9bf11c5e55b0fd5bc14390a3cfacfd11fd73070d).
Tested shared source commit:
[`cbab906`](https://github.com/MoralityLabAI/EvalMath/commit/cbab90625887153f57af5f1211d4307e053232b7).

The primary finite example separates a bounded message from the online memory
needed to compute that message. For three observed bits and a two-code alphabet,
an unrestricted final encoder reaches **18/24** correct deferred-coordinate
answers. A controller restricted to two codes after every observation reaches
at most **17/24**. The exact difference is **1/24**, or 4.1667 percentage points.

The independent audit passed all 16 exact synthesis cases, 12 unrestricted
handoff cases and 42 constructive cases. It replayed 3,856 word trajectories,
23,612 decisions and 27,972 updates, enumerated 133,509 labeled transition
tables, and checked 72,738 labeled handoff assignments. Ten unit tests pass.
Raw trajectory rows remain available through the evidence archive and can be
regenerated with the commands below. `audit_results.json` pins their SHA-256.

## Task and accounting

A word contains J independent uniform bits. The controller sees them in
MSB-first order, one per phase. Its retained code starts at zero and evolves by

\[
z_{t+1}=F_t(z_t,x_t),\qquad z_t\in\{0,\ldots,K-1\}.
\]

Phase, task and word width are public. Each phase has a static transition table.
After acquisition, a query q identifies a coordinate to recall. The decoder
receives only q and the final code. The report scores every word and every q
uniformly. A second task asks for the XOR parity of the word.

The interface excludes a history tape, an observation bypass to the decoder,
intermediate outputs and external retrieval. Static transition and decoder
tables are shared across all words. Each report counts these entries separately
from the dynamic alphabet: K codes require at most ceil(log2(K)) binary storage
coordinates. Public phase and query inputs are also declared. Counts exclude
Python representation, interpreter costs and runtime overhead.

This distinction matters for MIC-17's single-handoff result. An encoder with
free access to the complete history can send a final chosen action using one
bit on a two-action task. MIC-18 requires each intermediate update to preserve
enough information to perform the remaining computation.

## Primary witness

The lexicographically selected optimal online controller stores

\[
z_1=x_1,\quad z_2=x_1\lor x_2,\quad
z_3=(x_1\lor x_2)\land x_3.
\]

Its final decoder predicts z3 for every coordinate. Across the eight words and
three queries, it answers 17 questions correctly. The unrestricted encoder
sends the majority bit and answers 18 correctly.

The online search covers 44 reachable final partitions of the eight histories.
The unrestricted encoder has 128 partitions into at most two cells. Complete
enumeration certifies the respective optima on this domain. Majority itself
cannot be maintained with two codes through the second observation: prefixes
with zero, one and two ones require different continuation functions of the
last bit. This argument explains the computation constraint; the exhaustive
search supplies the best attainable approximate recall score.

## Finite synthesis results

| Observed bits J | Codes K | Optimal online recall | Reachable final partitions |
|---:|---:|---:|---:|
| 1 | 2 | 1 | 2 |
| 2 | 2 | 3/4 | 8 |
| 3 | 2 | 17/24 | 44 |
| 4 | 2 | 21/32 | 260 |
| 5 | 2 | 101/160 | 1,556 |
| 6 | 2 | 39/64 | 9,332 |
| 2 | 3 | 7/8 | 14 |
| 2 | 4 | 1 | 15 |
| 3 | 3 | 19/24 | 590 |
| 3 | 4 | 5/6 | 2,795 |

The six K=1 cases each score exactly one half. These are finite values for
deterministic, phase-dependent controllers under uniform query weighting.
The table does not establish a formula outside the enumerated grid. For J=3,
the K=3 and K=4 online values equal the unrestricted handoff values, so the
primary separation is specifically a two-code result.

## General counting arguments and constructive controls

**Perfect deferred recall.** Let E map a complete word to its final code and
suppose D(E(x),q)=xq for every word and query. If E(x)=E(y), their decoder answers
agree at every coordinate, hence x=y. Therefore E is injective and K is at
least 2^J. A J-bit shift register attains this bound with causal updates.
The finite suite replays that construction at J in {1,2,3,4,6,8}.

**Parity.** A two-code XOR accumulator computes parity at every length. Both
parity outcomes occur, so a one-code decoder cannot achieve zero error. Under
uniform words a constant answer scores one half. This gives a task that needs
access to every input while requiring only one retained bit.

**Suffix windows.** Retaining the last b bits answers b coordinates perfectly;
each omitted coordinate remains balanced. Its exact mean accuracy is

\[
\frac{b+(J-b)/2}{J}=\frac12+\frac{b}{2J}.
\]

Every b from zero through J is replayed at each declared constructive width.
The audit checks that the controller code describes exactly the suffix at
every phase. Full-register cases also pass injective-decoding checks.

These arguments use exact mathematics over binary inputs. Their accompanying
Python checks cover the declared finite suites. Lean kernel compilation and
trained-model testing are outside the delivered evidence.

## Search and independent audit

The producer maintains a partition of all prefixes at each phase. A successor
code depends only on the previous code and the new bit. Restricted-growth
strings enumerate every partition of those input pairs, up to state renaming.
Equivalent resulting prefix partitions have the same future possibilities, so
one causal witness per partition suffices for the terminal-only objective.
The decoder predicts the majority target in each final cell, resolving ties
to zero. The first lexicographic optimal partition wins a score tie.

The auditor implements a separate search. It enumerates every labeled update
table, computes the resulting prefix partition, and then canonicalizes labels.
It checks scores and reachable-partition counts, reconstructs all trajectories,
checks causal closure, and rejects extra controller fields. Source hashes,
protocol digest, all registered cases, memory counts and every reported output
are verified. The source itself contains the frozen protocol digest.

A resource guard stops synthesis if a phase exceeds 300,000 reachable
partitions. Such a run raises `SearchLimitExceeded` and supplies no optimality
certificate. The complete declared grid stayed below this guard.

## Preflight and limits

`pilot.json` contains the separate J=2 query and parity diagnostic, each with
a zero online-versus-handoff gap and an identity sham. The strict planner
returned `REDESIGN_OR_PILOT_ONLY` with exit code 2. There are two constructed
task families, zero independent model roots, and an unsealed empirical
readout. Sham-tail calibration and population power remain unresolved.

The protocol's 1/20 scientific floor and 1/10 hypothetical target are inputs
for a future empirical design. Its two confirmation units are an explicit
planner placeholder. None of these fields authorizes model fitting or turns
the complete finite rows into independent samples. The exact primary
criterion is a positive rational gap, evaluated within the full finite domain.
One primary comparison and 15 secondary query searches were retained, along
with every registered handoff and constructive control. No p-values are used.

The protocol was committed before the primary search. Independent small-case
unit checks followed that freeze. The producer's main suite followed the
strict preflight. Documentation and audits were tightened after implementation;
the final raw receipt pins the final checked source bytes.

## Reproduce

Python 3.12 and its standard library suffice. From the repository root:

```bash
python -m unittest discover -s gyms/MIC18 -p test_mic18.py -v
python gyms/MIC18/run18.py --pilot --out /tmp/mic18-pilot.json
python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot /tmp/mic18-pilot.json --out /tmp/mic18-preflight.json --strict
```

The last command is expected to return 2, preserving the empirical gate.
Then run the finite diagnostic:

```bash
python gyms/MIC18/run18.py --out /tmp/mic18-results.json
python gyms/MIC18/audit18.py --input /tmp/mic18-results.json --out /tmp/mic18-audit.json
cmp gyms/MIC18/audit_results.json /tmp/mic18-audit.json
```

## Application interfaces

`finite_memory.py` supplies `compile_exact`, `evaluate`, `storage`,
`handoff_optimum`, `make_window`, `make_register`, `make_parity` and
`make_constant`. `compile_exact` returns a wrapper containing `controller`,
integer score and denominator, reachable-partition counts and an explicit
optimality flag. Ports retain the exact source digest and Apache-2.0 license.

DataGoblin uses actor-local permit observations and a deferred final query to
turn the memory bound into a curriculum attribute. SelfModels applies causal
state updates to its existing fixed diagnostic tapes while keeping reward
and robust-certificate coverage separate. A constructed ReLU register in
LoopedTransformers provides a physical realization with declared public gates.
BPD uses that same register for reachable donor interventions with matched
component doses. Those ports carry their own fixtures, receipts and scope.
