# ACD-01C frozen pilot protocol

2026-11-25. Freeze before the simulation below. This is a synthetic algorithm
selection experiment, not a neural or Lean experiment. Prior ACD-01A/B worlds
are excluded by using new seeds and generators.

Three mathematical families (directed graph reachability, GF(2) affine
reachability, functional recurrence orbit membership). Each has independent
calibration and test seeds: 18 calibration and 36 test worlds, for 162 total.
State sizes are 8, 16, 32; world seed is 300000+10000*family_index+id+1 for
calibration, 800000+10000*family_index+id+1 for test. Test generators change
graph topology, GF(2) dependent generator counts, and affine multiplier
parity. Public structure can be read by the solver. Target/source streams
have hidden length chosen from 1,4,16,32 and variable source locality.
Each query is revealed sequentially. No solver gets the future queries
or horizon. Test targets use a separate deterministic PRNG stream.

Arms: fresh early stopping search, incremental per-source frontier cache,
eager specialized auxiliary, a frozen family-aware symbolic dispatch,
and online switch from lazy to specialized after k observed queries.
Specialized constructions are SCC condensation with component reach sets,
coefficient-carrying GF(2) elimination (with dual separators), and
functional graph cycle/preperiod orbit sets. Original problem certificates
are checked for every completed query. The online policy retains all
cost already paid before switching; old and new caches cannot be
credited as free. The dispatch and per-family switch threshold are
calibrated on calibration worlds only using total cost. Threshold library
k=0,1,2,4,8,infinity. The online threshold policy uses a one-unit decision
charge per revealed query; eager/lazy baselines do not pay this overhead.
Offline calibration cost is excluded and must be disclosed.

Primary endpoint: total held-out verified closures at budget equal to
actual requested queries times 128 abstract work units, per world. Secondary
budgets 32,512. Secondary endpoints: total work, paired wins/losses and worst
positive excess against the calibrated static family-aware dispatch; report
by family and horizon. Count only fully verified prefix completions under
the cap. The budget censoring is retrospective, not a live interruption.
Report unweighted per-category work (reads, writes, transitions/algebra,
checks), with all weights fixed to 1. Count construction, query work,
and certificate generation/checks. Standard abstract indexed/bitset
operations, not a claim about wall time, memory, or bit complexity.

Gate for useful online selection: strictly more verified closures than
both lazy and frozen family-aware dispatch at primary cap, with no increase
in aggregate work over dispatch. Otherwise report the exact negative result.
No retuning on test. This is a deterministic exploratory pilot with a
prospectively recorded policy library, not a statistical confirmation.
All test data are public once committed; future model evaluation needs new
sealed seeds. Require independent oracle checks for every possible source
and target in each finite world and malformed certificate rejection.
The pilot uses a common receipt with exact counters and source integrity
metadata. No neural training or GPU use.
