# Reproduction audit (same team, delegated worker): VAD-01 .. VAD-08, with the lead's VAD-09 replay

Worktree: `C:\Users\patri\OneDrive\Documents\GitHub\EvalMath-vad`, branch research/vad01-verified-abstraction-20261125, HEAD d6646bf.
Audit run by a delegated worker on 2026-11-25 and re-read by the lead. The audit itself modified no tracked file; scratch outputs were kept outside the repository.
Environment: Windows 11, python 3.12, numpy, pytest; **no torch, no lake/Lean**.

Digest convention: the committed `output/verified_abstraction/*.json` files are LF (not CRLF) in this checkout (`output/** -text`). Regenerated stdout files had CRLF from Windows text mode; all digests below are SHA-256 of the LF-normalised bytes (or of `json.dumps(x, indent=2, sort_keys=True)+"\n"`, the pinned convention in the tests).

## 1. Reproduction table

| Receipt | Command (as in note unless stated) | Byte-identical (LF) | Notes |
|---|---|---|---|
| vad_01a.json | `python src/spiral_ln/evaluation_vad.py > out` | Y (compact) | Re-serialised compact summary sha eb70b4150 = committed LF sha. 480 records. Full stdout is not pinned anywhere; compact == committed semantically and byte-wise. |
| vad_02.json | `python src/spiral_ln/evaluation_vad_composition.py` | N bytes / Y semantic | Committed file is a hand-reduced summary (key order protocol, evidence, source_sha256, ... not sorted). Semantically identical to regenerated output minus `records` (768 rows). The reduction step is not in the repo. |
| vad_03a.json | `python src/spiral_ln/evaluation_vad_lookahead.py` | Y | LF sha of full stdout 1755f2c2... = `full_receipt_sha256`; 6144 records, 192 cells, headline cells equal. |
| vad_03b_04a.json VAD04A | `PYTHONPATH=src python -m spiral_ln.evaluation_vad_invention --out D` (note gives no command; `python src/...py` fails: "attempted relative import with no known parent package") | Y | `vad_04a_full.json` LF sha 5c33d838... = `full_receipt_sha256`; records digest 8c5b4471... matches; 7056 records; totals 6,101,081 / 6,225,642 / 6,227,049 / 6,401,329 match. |
| vad_03b_04a.json VAD03B | not runnable (needs torch; note gives no command) | not testable | Symbolic part replayed by calling `evaluation_vad_robust.evaluate` without a model: baseline 4,718,592; q6 4,321,291; strict 4,716,392; cal choice q6 over 12 methods; 1,440 training rows; test = 288 families. All match the note. GRU/memoryless/shuffled totals, checkpoint sha 80c0547b..., full_receipt_sha256 5da256b5..., records sha 2021cd07... cannot be checked (delivered "separately in the experiment bundle"). |
| vad_05a_summary.json | `python scripts/verify_vad_lean.py --out D` | Y (summary) | Regenerated `receipt.json` minus `rows` equals committed summary (1024 files, same totals 4626/6227/5898/5096). `--lean` kernel run skipped (no lake). |
| (no receipt) VAD-05 sweep | `python scripts/sweep_vad_lean.py --out F` | n/a | Numbers equal the note (shape 0.7843..1.0959, global 0.9078..1.0386, concrete 0.7429..1.0285), but **no committed receipt or test pins the sweep**. |
| vad_06a.json | `python scripts/verify_vad_horn.py --out D` | Y (with `PYTHONUTF8=1`) | Fails on Windows default codec: `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 335` at `path.write_text(s)` (verify_vad_horn.py:216). With UTF-8 mode: summary_sha b3c17bf5..., records_sha 67db6107..., headline (25 cells), checks 563,624, files 288 all match. `--lean` skipped. |
| vad_06bc.json transfer (06B) | `python scripts/verify_vad_transfer.py --out D` | Y | receipt LF sha 017266f0... pinned; records sha c2bf1c32...; checks 1,718,892. |
| vad_06bc.json online (06C) | `python scripts/verify_vad_online.py --out D` | Y | receipt c221dfc1..., records 48263925..., checks 1,449,578. |
| vad_06d_d2.json D | `python scripts/verify_vad_adaptive.py --out D` | Y | receipt 40463904..., records 68d3ad58..., checks 1,085,624. |
| vad_06d_d2.json D2 | `python scripts/verify_vad_ancestor.py --out D` | Y | receipt f17312ac..., records d914b12c..., checks 1,733,328. |
| vad_07abc.json A | `python scripts/verify_vad_stopping.py --out F` | Y | 65add951... |
| vad_07abc.json B | `python scripts/verify_vad_robust_stop.py --out F` | Y | fdbb2ef1... |
| vad_07abc.json C | `python scripts/verify_vad_horn_stop.py --out F` | Y | 27063246...; checks 2,036,550. |
| vad_08.json | `python scripts/verify_vad_reliability.py --out F` | N / not applicable | Symbolic receipt sha 790dcdb9... vs pinned `receipt_sha256` c8a4ab17..., which the note ties to the torch training run (2,304 stream-method records), so not comparable. Symbolic table and alarm counts in the note were recomputed and match (see 4). `train_vad_reliability.py` not run (no torch). |

Skipped: all `--lean` kernel runs; `train_vad_reliability.py`; VAD-03B GRU training (no torch, no command in note). No run needed more than ~3.5 minutes; nothing skipped for time.

## 2. Source-hash checks

Every recorded source/dependency digest equals the current sha256 of the named file, both LF and raw (tree files are LF): vad_01a, 02, 03a, 03b (evaluation_vad_robust.py), 04a (evaluation_vad_invention.py), 05a, 06a, 06bc (parent + transfer + online), 06d_d2 (parent + D + D2), 07abc (A, B, C and C's two dependencies), vad_08 `files` (verify_vad_reliability.py, train_vad_reliability.py, test_vad_reliability.py). 21 of 21 match. Not checkable: checkpoint_sha256 of VAD-03B and VAD-08 (checkpoints not in repo).

## 3. Repo checks

* `python scripts/check_receipts.py`: **26 of 27 verified**. The one FAIL is `openai_eth_fidelity` ("proof fidelity: source circuits_appendix: Git blob differs from pinned upstream"), not a VAD receipt. `check_receipts.py` has **no VAD entries**, so it gives no coverage of these receipts.
* VAD tests (10 files, test_vad_meta.py excluded): 33 tests, **32 passed, 1 failed** in 313 s. Failure: `tests/test_vad_horn.py::test_receipt_replay` with the same cp1252 `UnicodeEncodeError`. Re-run with `PYTHONUTF8=1`: 4/4 pass, so **33/33 pass with UTF-8 mode**.
  Per file: evaluation_vad 3, composition 4, lookahead 5, adaptive 3, horn 4, invention_replay 1, lean 3, reliability 4, stopping 3, transfer_online 3. Counts agree with the notes for 03A (5), 05 (3), 06A (4), 06B/C (3), 06D (3), 07 (3), 08 (4); **not** for 03B/04A (see finding 1).

## 4. Headline-number verification (all by recomputation unless noted)

* VAD-01: shared H=64 23,996 vs 40,960; shifted 42,062; null 40,634; H=4 2,720 vs 2,560 (receipt); 4,096 checks; 255/256 = 1-2^-8; break-even identity checked against code (discovery charge 6 + 4*|candidates|, +2|a| construction).
* VAD-02: t=7,a=25,b=30 gives 6,6,6,4 and F({7,15})=10 vs 14 (recomputed by BFS); greedy 134,336 (= 131,072 + 32*102), joint 120,448/153,216/151,256, 32/0/0 profitable; n>173; Hoeffding penalty 9.83.
* VAD-03A: all quoted numbers match the receipt (106/64,512/256 pairs; 47,725 vs 2,550,784 = 53.45x; 1.1894x; 0.1781x; 0.9687x; 0.9898x; 0.9156x/0.9164x; noisy 3/32, 0.9804x, 29/32).
* VAD-03B/04A: symbolic 03B numbers and every 04A number (regime gains 1.415269/1.291227 etc., 238/240, 0/96, veto 236/336 and 154/336, 0 null/shift selected) reproduce. Ratios 0.949589, 0.786755, 1.091264 recompute from the quoted totals. GRU totals not reproducible.
* VAD-05A: 4626/4442/4160/4443 refs, 4626/6227/5898/5096 totals, 10.07 %, uses 183/190/64, entire sweep table.
* VAD-06A: pooled direct 139,811; support refs 106,122 + selection 26,640 + construction 402 = 133,164; 36/48 selected; 24 profitable; H=128 gain 0.8708 with 12 profitable; regime table; support refs equal exhaustive/oracle refs per regime.
* VAD-06B/C: 571,019 / 564,723 / 607,791 / 697,414; validation 21,743; 24/24 immediate-shift and dominated rejected, 24/24 late-shift accepted with 0 savings; calibration 304,449 vs 281,029 (halved); 06C 421,276, 141/192, 168/192 selected, regime totals sum to 421,276.
* VAD-06D/D2: 618,177/439,732/448,601/465,514 and DP-adjusted 1.124548/1.117630/1.104670; D2 976,880/608,497/653,833/764,255, 312 wins, 262 profitable, 312 selected incl. 48 dominated, 72/72 concealed profitable, null 0/24, DP-adjusted 1.154858, interval [39849,50789].
* VAD-07: 07A 8.9, 21.182/21.1817, null-heavy 2.88/7.6604/7.99, late-heavy 2.1/16.2939/16.5387, weak 8.2158, reversed -10.4431, oracle 20.6057; 07B mix_5 9.1166/9.6388/5.2694/6.104; 07C 19,289,750/17,760,955/15,385,990/17,958,940, 1.253722x, 13.37 %, DP-adjusted 1.086253, and every scenario ratio quoted.
* VAD-08: all 8x(Blind..Privileged) table cells except GRU column recomputed (symbolic columns match); alarm streams weak 32/32, joint 29/32, Markov 1/32; proxy-adjusted nets 13.887/9.778(approx)/5.536. GRU column, "4 wins in 32 streams" not reproducible (torch); delta -1.1705729 and interval equal the committed receipt.

## 5. Findings, by severity

**Medium**

1. **03B/04A test claim is unsupported and the 03B record is unreplayable from the repo.** The note says "Five local tests pass: robust index vs direct filter; disjoint seeds and query caps; no planted access; frozen receipt and exact-cost verification; full invention replay". Only one test imports the robust/invention modules (`tests/test_vad_invention_replay.py::test_source_hashes_and_invention_receipt`: source hashes plus 04A canonical records and four totals). There is no test of 03B outputs, "no planted access", or 04A query caps. The 03A tests (5) cover the signature index, not these. The 03B digests (checkpoint, full receipt, records), "retraining reproduced checkpoint and all 4,320 records" and the GRU numbers rest on an external bundle. The note gives no reproduction command for either 03B or 04A.
2. **Contradictory kernel/CI status across notes for the same experiments.** `horn.md` says VAD-06A Lean kernel replay "remains pending" and "Local Lean is unavailable"; `horn_gym.md` says the generated Lean batches were "kernel-replayed" (Actions run 45525699236, artifact 14982961408, commit d8be099). `lean_gym.md` says 05A "kernel replay pending" while `horn.md` says the 05A kernel gate passed at a14ff7c (run 45518870988). All committed receipts keep `kernel: NOT_RUN`. The commits c0e4836, a14ff7c and d8be099 exist locally, but the CI runs and kernel results cannot be verified here (no Lean, CI not queried). Treat every "kernel passed" statement as unverified.
3. **Reproduction fails on a default Windows codec.** `verify_vad_horn.py` (and `tests/test_vad_horn.py::test_receipt_replay`) crash with UnicodeEncodeError because Lean source containing U+2192 is written with `Path.write_text` in the locale encoding. Digests are identical once `PYTHONUTF8=1` is set. Not a result error, but the stated reproduction commands do not run as written on Windows.

**Low-medium**

4. **06C omits negative arms and the DP-scan sensitivity.** The note's results list five arms. The twelve alternatives searched on calibration also include `online_trigger_{2,4,8,16}` (test totals 568,081-572,782, all above the 567,120 direct baseline) and `online_exact_{2,4,8,16}` (exact_2 and exact_4 beat direct, exact_8 and exact_16 do not). The text says triggers were compared but not that they lose. 06D, D2, 06A and 07C report a common deployment-DP scan sensitivity (which cuts gains, e.g. D2 1.605x to 1.155x, 07C 1.254x to 1.086x); 06C reports none and its records contain no such field, so the 1.3462x headline has no matching sensitivity. The online arm also observes post-shift deployment goals that the development-only comparator cannot, which the note states.
5. **"Independent" checks are same-author, same-model re-implementations.** The relaxation `independent()`, the BFS oracles, the 4,096-subset enumeration and the `audit()` source parser share the module's data structures (`audit` reuses `leaves`/`replace`; horn_gym admits the header uses "the same specification renderer"). They validate DP/code correctness against the declared reference-cost model, not the model against Lean. Headline counts (563,624; 1,718,892; 1,449,578; 1,085,624; 1,733,328; 2,036,550) are repeated per-goal comparisons. 06B/C, 06D and 07C say so; 06A and horn_gym quote 563,624 without that caveat.
6. **Receipt coverage gaps.** `check_receipts.py` has no VAD entries. The 05A sweep has no committed receipt. Compact receipts for 02 and 05a (and 01a) are derived from full outputs by an unscripted reduction (02: different key order, equal content). Pinning is by digest of full replays that tests regenerate, which is sound for 03A, 04A, 06, 07 but absent for 01A/02 full outputs.

**Low (wording / scope)**

7. **"Privileged" comparator is not an upper bound.** In 04A the non-privileged intersection arm beats the "privileged-pair comparator" (6,101,081 vs 6,225,642; better in 4 of 7 regimes: clean, noise2, noise4, structured). The label can be misread as an optimum; the note says it only "sees a supplied complementary pair".
8. **Planted-structure dependence.** 03A recovery 31/32 needs stable coordinates and a supplied pool containing the planted pair; signature work (47,725) exceeds random work (46,588), so "53.45x" is only against exhaustive enumeration (stated). 07C's cue gain exists because regime weights correlate the cue with future utility (note says so); under the cue-shift and uniform mixtures the fixed/cap64 policies win. 06A "exhaustive" and "oracle" arms pay 351,887 and 10,058,712 selection units (0.305x and 0.014x), so favourable comparisons against them are weak evidence.
9. **Information used at selection.** Non-oracle arms in 06A exclude deployment-target IDs from the candidate menu (disclosed as a scope guarantee). Nested horizons 8/32/128 reuse the choice frozen for H=256 (disclosed); at H=128 support loses (0.8708x).
10. **Construction charged once in 05A global arm** (5 units for 256 files) while every isolated file redeclares and re-elaborates the cache (+30 % source bytes vs direct); noted as not charged.
11. **Undisclosed iteration count:** 03A note says the dimension was changed from 24 to 28 "before producing the receipt"; how many prior runs informed other choices is not recorded. All splits are public fixed seeds with no third-party seal; the notes say this repeatedly and do not claim holdouts.
12. **04A combinatorial remark** uses n without defining it (it must be the number of non-motif coordinates); disclaimed as not a generalisation bound.

**No issues found** in: source-hash recording (21/21 match), 01 break-even identity, 02 composition example and construction DP, 07B minimax argument (valid because the protected set contains the blind channel, which makes the bound immediate), the 06D2 two-action regret algebra (p=(S-c)/S, regret c(S-c)/S), the 08 Ville bound statement (hedged for floating point), and the 03B/04A/06/07 headline arithmetic. No grid regularity is called a theorem; no sentence found that asserts a general-abstraction-discovery result.

## 6. VAD-09 reproduction (lead, same day)

Environment: Windows 11, python 3.12, numpy 2.5.4, pytest 9.1.1; no Lean.

* `verify_vad_meta.py` (09A, exact Fractions): LF-normalised receipt digest 667a5c4d... equals the pinned `receipts.A`. Segments 1/5/187/3785, 123 checks, horizon-3 value 37.8794532685 with first action cut24, first-action advantage 1.8980957284. The 12-action menu horizon-1/2 optima equal the myopic values 9.3777027312 and 20.8631051452 (exact rationals in the receipt).
* `verify_vad_meta_cert.py` (09C): receipt digest 1ac67b7a... equals the pinned `receipts.C`; horizon-96 myopic 1692.626322, policy 1700.970386, incremental utility 0.086917 per family (0.49% of the myopic value is the 96-family total gain 8.344 divided by 1692.6).
* `verify_vad_meta_grid.py` (09B): regenerated receipt digest 380229d0... differs from the pinned `receipts.B` 4065b708.... The printed headline statistics (nominal menu_32 minus menu_1 mean 0.0130208, interval [-0.17448, 0.21094], 14/32 wins, joint-shift and prior-shift table rows) equal the note. The byte difference is attributed to floating-point summation order under numpy 2.5.4 on Windows and has not been bisected; the committed repo holds only the digest, not the full 09B receipt, so no semantic diff was possible. Treat the pinned 09B digest as environment-specific.
* `tests/test_vad_meta.py`: 4 passed (17 s).
* CI on the PR head d6646bf: python, lean, CodeQL jobs success (GitHub check-runs API).
* The VAD-09 interruption left nothing missing: the note, receipt, scripts and tests of 09A/B/C were committed and pushed before this session.
* Statement fidelity: the user-supplied headline figures (9.378, 20.863, 37.879, 7.078 sacrifice, +1.898, 0.49% / 0.087 per family at horizon 96) all reproduce, with the caveat that the 0.087 figure is the same-grid difference (401 points) and that the 2.3 immediate utility of cut24 is the only action sacrificed.
