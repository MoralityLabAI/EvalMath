# MIC-17: exact compression of catalog evidence at one handoff

**Evidence: exact finite synthetic domain, public development.** Across the 48 registered development roots, an optimized message with four possible labels preserves all optimal continuation reward. Two labels preserve 99.7346% on average. The primary headroom gate returns `FAIL_NO_FITS`.

This follows the paired-history proposal in [MIC-16, draft PR #100](https://github.com/MoralityLabAI/EvalMath/pull/100). The [protocol and frozen environment](https://github.com/MoralityLabAI/EvalMath/commit/d7b1ca9a1d65625506d154586eb5f7d193d5b4ef) were committed before the pilot ran. The environment file is byte-identical to `gyms/MIC16/mic16.py` at commit `53e1118a75ccee9d7bd323b398909296dc82695c`; its SHA-256 is recorded in `protocol.json`.

## Controlled histories and the memory handoff

Each root has eight static catalog worlds with known positive integer prior weights. Only the realized world is initially hidden. The possible catalogs, exact arithmetic entries and reward rules come from the frozen MIC-16 generator.

Every world executes the same public prefix: probe bits 0, 1 and 2, in that order, at one budget unit per probe. All histories finish with zero acquired lemmas and nine units remaining from an initial budget of twelve. The full observations reveal the realized world. Acquisitions and elapsed cost carry the same information in every history.

At this point an encoder sends one label. A codebook partitions the eight possible histories into cells. The decoder knows the public root, the codebook and the remaining budget; it receives the label instead of the discarded history. Its posterior is the label's cell with the original prior weights restricted to that cell. Subsequent observations update that posterior normally, and future belief memory is unrestricted. A decoder may pay to probe a forgotten bit again.

The encoder and decoder share a root-specific codebook constructed from the complete known model. Its storage and construction cost are free side information. Thus a four-label result bounds the information needed at this particular handoff. A continuously constrained recurrent controller would require a separate experiment. A reward-preserving code can merge worlds with different predictions, so it need not reconstruct the posterior or remain sufficient for another reward function or budget.

## Exact optimization

Let `U(S,M,B)` be the unnormalized weighted optimal reward for acquired set `S`, posterior support `M` and remaining budget `B`. The reference planner computes this by an integer Bellman recurrence, admitting an action only when its worst possible cost fits the budget. Positive integer costs make the recursion finite.

For a codebook partition `P`, the value at the handoff is `sum(U(0,C,9) for C in P)`. The prior mass is already present in each term. Normalize after summing by the root's total prior mass.

The subset program finds the best partition into at most `K` cells. Its recurrence selects a nonempty cell containing the smallest remaining world, adds that cell's value and recurses on the rest with one fewer label. The empty remainder has value zero; a nonempty remainder with zero labels is infeasible. This enumerates every partition through a canonical cell order. The independent audit instead generates restricted-growth partitions and checks all 4,140 possibilities for each root.

All eight capacities `K=1..8` are reported. For comparison, fixed windows keep the last one or last two probe observations. Their respective capacities are two and four labels. The primary probe order stays `012`; the report retains window scores for all six orders. Full-history value is order invariant because every order reveals the same world. This supplies an identity control. It does not calibrate empirical sham variation.

## Results

The main sweep uses seeds `17000..17011` within each of the `local`, `shared`, `parity` and `mixed` catalog families. The pilot uses the separate seeds `16900..16902`. Both phases are development data, and the four generator lineages were used in MIC-16.

Each table entry is the mean, over 48 roots, of retained expected reward divided by full-history expected reward. The fixed prefix earns zero reward and consumes the same three units in every arm.

| Representation at handoff | Label capacity | Fixed-width message bits | Mean reward retained |
|---|---:|---:|---:|
| Discard all prefix evidence; exact adaptive continuation | 1 | 0 | 96.177671% |
| Optimal code | 2 | 1 | 99.734584% |
| Optimal code | 3 | 2 | 99.984102% |
| Optimal code | 4 | 2 | 100% |
| Full history | 8 | 3 | 100% |
| Last observation | 2 | 1 | 97.645192% |
| Last two observations | 4 | 2 | 98.718700% |

The optimal codebooks with five through eight labels also preserve 100%. Minimum capacities vary across roots:

| Minimum labels preserving full value | Number of roots |
|---|---:|
| 1 | 4 |
| 2 | 29 |
| 3 | 14 |
| 4 | 1 |

The registered primary contrast is the loss from the optimal two-label message. Its mean relative loss is **0.265416%**. Fifteen roots have positive loss; the largest is `137/5897`, or **2.323215%**, for `parity/17004`. Zero roots reach the registered 10% hard-root threshold. The gate required at least 5% mean loss and at least 20% hard roots, so it fails both criteria.

At `parity/17004`, the full-history weighted value is 5,897. The optimum with two labels is 5,760; three labels reach 5,852, and four reach 5,897. These are exact integers.

## A matched-history witness

The first recorded positive pair sharing the last two observations occurs at `local/17004`:

| World | Probe 0 outcome | Probe 1 outcome | Probe 2 outcome | Prior weight |
|---|---:|---:|---:|---:|
| 0 | 0 | 0 | 0 | 4 |
| 1 | 1 | 0 | 0 | 2 |

Both histories have acquired set zero and budget nine. Both fixed windows merge them. With full history, their optimal rewards are 287 and 232.

To isolate a decision conflict, require a common first action and then restore the true world immediately afterward. The calculation considers every physically legal action, including redundant probes and known failed attempts, plus stopping. Omitting such actions could hide an optimal tie when the budget has slack.

The best common first action directly verifies group 0. Even after world identity is restored, its rewards are 287 and 227. The weighted totals are therefore `4*287 + 2*232 = 1612` with full history and `4*287 + 2*227 = 1602` after the shared first choice. Dividing by prior mass six gives an exact expected penalty of **5/3 reward units**. The pair's ordinary merged-belief value also equals 1,602, so the optimistic bound is tight here.

The whole root admits a lossless two-label code: distinguish world 1 from the remaining seven worlds. This shows how a task-specific bit can preserve reward even when a fixed two-observation window loses useful evidence.

All 28 unordered pairs are reported for every root. There are 120 positive common-first-action penalties among 1,344 pairs, spanning 31 roots. In 24 roots a positive pair also shares the primary one-observation window. Pairs remain dependent observations within their roots.

## Independent verification

Six targeted tests pass under Python 3.12.14 using the standard library's `unittest` runner. They also support pytest discovery. The separate audit shares the frozen environment generator, while using its own explicit-world Bellman solver and partition enumeration. It retains all physically legal actions.

| Audit check | Verified count |
|---|---:|
| Posterior-support optimal values | 12,240 |
| Enumerated partitions across roots | 198,720 |
| Capacity optima | 384 |
| Window values across all probe orders | 576 |
| Complete continuation trajectories | 2,304 |
| Continuation actions replayed | 10,446 |
| Observable-state action/stop consistency checks | 9,717 |
| Pair alias bounds and optimal-action sets | 1,344 |
| World/probe-order identity checks | 2,304 |

Replay treats the compression boundary explicitly: it first verifies the full prefix evidence, then reconstructs the deliberately coarser controller posterior from the codebook. Every subsequent choice is checked for Bayes optimality under that retained posterior. The audit checks the planned root coverage and exact source hashes, then recomputes the summary. These checks establish the finite executable result; Lean verification is outside this experiment.

## Resolution planning and scope

| Required planning item | Recorded value |
|---|---|
| Unit and sample accounting | 48 development roots; 4 reused, unverified generator lineages; 12 separate pilot roots |
| Cases | 384 latent root/world cases; trajectories, pairs and probe orders repeat those cases |
| Primary contrast | Full-history value minus optimal two-label value, relative to full-history value |
| Intervention | One deterministic two-label handoff; future belief tracking unrestricted |
| Scientific variation floor | Preset 5% relative reward loss for future-design headroom |
| Sham calibration | Unavailable; recorded zero is an identity placeholder |
| Planned and actual primary comparisons | 1; all secondary capacities and windows retained |
| Readout exposure | Public development; no sealed confirmation population |
| Preflight outcome | `REDESIGN_OR_PILOT_ONLY`, strict exit 2 |
| Fits and training allocation | 0 |

The pilot's optimal two-label loss was 0.439028%. The planner reports an approximate resolvable effect of 5.08854 percentage points under its planning formula. Its reasons for holding prospective inference include the unsealed readout and unverified independence; sham quantiles lack calibration, and the pilot effect lies below the variation floor. The displayed plan for 128 confirmation units was not executed. No significance or population-equivalence claim follows from this calculation.

This finite sweep supports compact encoding of catalog evidence at the specified handoff. It supplies no neural mechanism result or result about textual mathematical discovery. All arithmetic rewards and costs remain the synthetic MIC-16 contracts. There were no model fits, paid compute allocations or manuscript ingestion.

## Reproduce

From this directory:

```bash
python -m unittest -v test_mic17
python mic17.py --phase pilot --out pilot_results.json
python ../../skills/evalmath-mechinterp-power/scripts/preflight.py --pilot preflight_input.json --strict --out preflight_output.json
# The preflight command intentionally exits 2 for this development study.
python mic17.py --phase development --out results.json
python audit17.py --input results.json --out audit_results.json
python summarize17.py
```

`summary.json` records every root's capacity values and the exact witness, together with source and data hashes. Full raw outputs are archived with the handoff and regenerate deterministically from the commands above. Their SHA-256 values are:

| Output | SHA-256 |
|---|---|
| `pilot_results.json` | `7e4a57216e04a4644e9f613cf7ce1ccfdba48027715a6fe12b803aa69e3c5ae0` |
| `results.json` | `43ac6cdee4317160ce66d71522980e9de4c8f2da6e1e4e237c44c060dfdad037` |
| `audit_results.json` | `e313e8b4fe875af37961709e5fbebf92a85f063e54a4459ffdf4bb4c00f6f816` |

The previous MIC-16 repository workflow passed 1,909 tests and 13 subtests. Its receipt stage failed because the inherited DCF-16 verifier points to an external local checkout; [the failing job](https://github.com/MoralityLabAI/EvalMath/actions/runs/45602721135/job/139165496866) is separate from this gym's targeted checks. MIC-17's own repository CI status should be read from its draft PR.

## Next decision

Keep model training on hold for this fixed catalog family. A further memory-capacity experiment would need a catalog with enough task-relevant hidden information to survive optimized message compression, together with an end-to-end controller whose state capacity is enforced throughout continuation. Any new protocol should account for the shared codebook and its construction cost before treating message size as total memory.
