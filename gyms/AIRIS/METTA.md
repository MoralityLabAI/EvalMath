# AIRIS-05: native MeTTa causal memory

The previous exact oracle (AIRIS-04) is now a target for a symbolic memory
interface using Hyperon 0.2.10, the version also used by the project's
metta-storyworld courier bridge at 4cfe1713d73b4e508833b668477921adfbe570a6.

A public evidence event has a unique ID, a committed binary action schedule and
three ordered observed bits. A hypothesis is one of the twelve candidate
action-effect/noise-regime pairs. The true hypothesis is never furnished to
the agent. MeTTa derives the two-bit temporal code, looks up the integer
likelihood, and recursively multiplies the prior weight over active evidence
IDs. Python orchestrates storage, sums target weights and scores every
candidate schedule using the native likelihoods and posterior. The exact
AIRIS-04 greedy acquisition rule checks all proposal scores and the tie-break.
This is a hybrid native-symbolic bridge, not an implementation of PLN or
SubRep. The likelihood table is generated from the declared mathematical
grammar; native inference does not induce new likelihoods from data.

A native runtime instance has a fixed hypothesis/likelihood space and a
separate active evidence set. Reload removes every old evidence atom and
checks atom counts. A repeated event ID is rejected. Independent episodes
with identical content have different IDs and contribute multiplicatively.
Revocation/amendment recomputes from the remaining evidence, never divides
by a possibly zero likelihood. Event order and source identity are bound
into the public receipt hash. The likelihood table and rule source are also
bound. This makes the memory contract suitable for later audit and
continuation-sufficiency experiments; it does not attest physical provenance.

The native engine is checked against the independent literal hidden-driver
path enumeration (full raw trajectory likelihood times two, because the
initial fair bit is independent). The native factor table must agree for
all 384 likelihood cells. The census covers all 64 public one-episode
schedule/raw-observation pairs, and six evidence lifecycle cases, at the
mixed prior. Additional tests exercise known persistent-driver prior,
impossible histories, and input validation. Each proposal uses all eight
candidate schedules, no hidden labels. All weights are exact integers; the
bound of eight evidence events keeps multiplication within 64-bit range.
Every zero-mass history fails closed.

Run from repo root:
    python -m pip install hyperon==0.2.10
    python -m unittest discover -s gyms/AIRIS -p test_metta_bridge.py -v
    python gyms/AIRIS/metta_bridge.py > AIRIS-05.json

A dedicated CPU workflow installs Hyperon, tests and generates two receipts,
compares them byte-for-byte, and publishes one. Ordinary stdlib-only AIRIS
tests skip native tests when Hyperon is absent. Dedicated native CI cannot
pass on a missing runtime: its direct receipt generation requires the import.

Next: train a recurrent experiment-selection router on public action/readout
histories. Use the exact posterior as a teacher, report regret against all
eight schedule values rather than top-1 agreement on tied choices, and
reserve separate generator families for prospective evaluation. MeTTa owns
the checked evidence representation. No trained router, native original
AIRIS learning comparison, or generalization claim is made here.
