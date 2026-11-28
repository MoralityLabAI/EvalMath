# Correlated Proof Fidelity, CPF-01 to CPF-06: research report

Date: 2026-11-25. Repository: `MoralityLabAI/EvalMath`, `main`.

Evidence levels used throughout: **kernel** (Lean 4.34.1, Mathlib `d13f23b`, `#print axioms` gives only `propext`, `Classical.choice`, `Quot.sound`); **finite** (exhaustive executable check on a bounded domain, receipt-hashed); **paper** (derivation in the notes, not machine-checked); **empirical** (measured model calls on the prospective panel).

## 1. Formal results

| Result | Level | Where |
|---|---|---|
| Conditional joint false acceptance r = P(A∩B \| H0) lies in [max(0, a+b−1), min(a, b)], and every point is attained | kernel | `CPF.frechet`, `CPF.witness`, `CPF.atom_total` |
| Residual false authorization after a conditionally calibrated audit is rc ≤ r | kernel (calibration is an assumption) | `CPF.conditional_audit` |
| Adaptive certified-rejection audit: the Bellman recurrence bounds every valid policy and is attained; adaptive ≤ fixed; witness where adaptivity removes a third of the fixed residual | kernel + finite | `CPFAudit.value_le_residual`, `exists_optimal`, `value_le_fixed`, `witness_*`; `cpf_01.json` |
| OpenAI exact circuits = canonical circuits | kernel | `CPF02.openai_exact_iff` |
| Gate-budget sandwich C_O ≤ C_A ≤ 4·C_O + 2 over every field and characteristic | kernel | `CPF02.charged_free_sandwich`, `canonical_to_anthropic` |
| Lower bounds transfer in both directions | kernel | `lower_transfer`, `lower_transfer_reverse` |
| Eventual polynomial bounds A·n^d equal Anthropic's all-index n^a + a | kernel | `polyBounded_iff_allIndex` |
| VP is the same class under the OpenAI, canonical and Anthropic conventions | kernel | `openai_vp_iff`, `vp_iff_anthropic` |
| OpenAI VNP with arbitrary finite witness types equals canonical VNP over Fin (r n) | kernel | `openai_vnp_iff_canonical` |
| VP ⊆ VNP; VNP is the same class under the OpenAI, canonical and Anthropic conventions | kernel | `vp_subset_vnp`, `vnp_iff_anthropic` (with `totalDegree_eval₂Hom_le`) |
| Laurent approximation transfers from charged to canonical circuits | kernel | `anthropic_approx_to_canonical` |
| VP ⊆ VPBar (Laurent closure), canonical and Anthropic conventions | kernel | `vp_subset_vpbar`, `statement_vp_subset_vpbar` |
| Small-table compiler census (0 to 2 gates, fields of order 2, 3, 5, formal coefficient maps) | finite | `cpf_02.json` |
| Approximate-inclusion transfer, failed converse; pointwise vs uniform thresholds | kernel | `CPF03.*` |

### Remaining obligations

1. **Laurent versus geometric border.** All approximation statements here are the algebraic Laurent notion. Agreement with Zariski-closure border complexity holds over algebraically closed fields and is not claimed elsewhere. VP ⊆ VPBar is kernel-checked for the Laurent notion only.
2. **Endpoints and families.** Neither lab's separation endpoint is proved here; the permanent/Hamiltonian definitions and the quantitative rates m^(c(log m)^(1/3)) and exp(Ω((log n)^(5/4))) are not yet placed on a common size parameter.
3. **Trusted environment.** Only definition bodies of the upstream statements are imported; the OpenAI comparator's admitted challenge endpoint stays in an archive outside the build.

## 2. Empirical protocol (CPF-04 to CPF-06)

**Panels.** The dev preflight uses 48 roots from the threshold family. The primary panel uses 240 roots, 40 from each of the six test families, with labels 120 entailed, 100 counterexample and 20 unresolved. Both were generated with 256-bit private seeds. Their digests and seed commitments were committed in `138b942` before any inference (`output/evaluation_cpf/runs/*_generation_manifest.json`). Gold files are held outside the repository and are never sent to a model.

**Calls.** Each model gets four stateless calls per root: direct (cap 512), low1 and low2 (cap 256 each, independent), and refine2 (cap 256; it sees low1's answer content, never its reasoning). Thirteen arms are derived from these calls without gold: per model direct, low, low2, independent agreement, refine and serial agreement, plus cross-model agreement. The primary run is 1,920 requests with at most 614,400 completion tokens.

**Amendments before any registered call.** These are recorded in the CPF-04 to CPF-06 note. Thinking is enabled with a per-request thinking budget of cap − 128 tokens, so thinking tokens count against the same completion cap. The registered parse also accepts one surrounding code fence; the strict parse is reported separately. The ledger additionally keeps reasoning text, server timings and request options.

**Backends.**

| | Bonsai 2 27B | Inky mini varloop |
|---|---|---|
| Checkpoint | `Ternary-Bonsai-2-27B-PTQ1_0.gguf`, 5,946,648,928 B, sha256 `53107f53…33ee3` | `TML-d24-varloop-research-IQ4_NL.gguf`, 17,627,940,800 B, sha256 `e9f70a16…17bb2` (matches its download receipt) |
| Server | PrismML llama.cpp b10743 (`adfffbe41`), CUDA, full offload, ctx 4096 | llama.cpp b12602 (`418fe97b5`) Vulkan arena build, `-ngl 99 --n-cpu-moe 8`, loop count 2, ctx 4096 |
| VRAM | 6,290 MiB | 13,523 MiB |
| Load time | 138 s | 118 to 130 s |
| Decode / prefill | 29.6 / 44.3 tok/s (mean over 192 dev calls) | 2.6 / 3.0 tok/s (best of three configurations, host paging) |
| Caps honoured, usage reported | 192/192, 0 violations | probe only |

**Dev preflight, Bonsai half (exploratory; dev family; 48 roots).**

| Arm | Certified | Label | Coverage | False auth. (n=24) | Completion tok | Prompt tok |
|---|---|---|---|---|---|---|
| direct (512) | 0.688 | 0.896 | 0.896 | 0/24 | 20,337 | 8,887 |
| low (256) | 0.062 | 0.729 | 0.750 | 1/24 | 9,619 | 8,887 |
| low2 (256) | 0.062 | 0.771 | 0.854 | 1/24 | 9,344 | 8,887 |
| refine (256+256) | 0.083 | 0.646 | 0.646 | 0/24 | 19,954 | 22,943 |
| independent agreement | 0.021 | 0.062 | 0.062 | 0/24 | 18,963 | 17,774 |
| serial agreement | 0.062 | 0.333 | 0.333 | 0/24 | 19,954 | 22,943 |

Direct (512) beat refine (256+256) at the same completion budget on certified accuracy: 31 roots right only under direct, 2 only under refine, exact McNemar p = 1.3e-7. Refine also consumed 2.6 times the prompt tokens. Refinement rarely repaired anything: of 45 low1 answers without a valid certificate, 1 was repaired and 44 persisted, and 25 of 48 refined answers were identical to low1. It never broke a certified answer (0 of 3).

At the 256 cap, Bonsai usually gets the label right but returns a certificate object with extra fields instead of the bare integer requested. That is why certified accuracy collapses while label accuracy stays near 0.75. It also makes exact-agreement arms abstain almost always, because two calls rarely produce identical certificate objects. Truncation at the cap hit 12 of 48 low1 calls and 17 of 48 refine2 calls, each counted as an abstention. Only 2 of 24 null roots were falsely authorized by any low arm, so the dev panel cannot estimate joint risk: Δ for low|low2 is −0.0017, from 1 × 1 marginals and no intersection.

**Primary experiment.** Not yet collected at the time of writing. The GPU was free from about 09:00 to 10:11, and that window went to Phase 1 and the Bonsai dev preflight. After that, another job held 10.25 GB VRAM, and host-RAM pressure from other jobs made Inky impractical. A watcher starts the Bonsai primary panel when the GPU frees; the resume commands are in `output/evaluation_cpf/runs/CONTINUATION.md`. No primary-panel number appears in this report.

## 3. Error correlation, refinement and cross-model diversity

The analysis code is fixed and tested on a constructed ledger (`tests/test_cpf_analysis.py`); it was not tuned on model output. For every pair it reports a, b and j on the counterexample roots, the pooled Δ_AB = j/N − (a/N)(b/N), a family-stratified Δ (the within-family Δ averaged with family weights), and a within-family permutation p-value for j. The permutation keeps each family's marginal false-authorization counts fixed, so between-family difficulty differences cannot create apparent dependence. Refinement is summarized by the 2×2 certified transition matrix (C→C, I→C, C→I, I→I) and a four-state matrix (certified, label-only, wrong label, abstain). The registered contrasts are direct vs refine, independent vs serial agreement, and cross-model agreement vs each model's independent agreement. Each uses a family-stratified paired bootstrap, an exact McNemar test and Holm adjustment. All other tables are labelled exploratory.

## 4. Compute-normalized comparison

Completion caps are matched; total inference cost is not. On the Bonsai dev half, refine and direct used about the same completion tokens (19,954 vs 20,337), but refine used 2.6 times the prompt tokens and 6% more wall time. Bonsai and Inky differ by more than 10× in measured decode throughput on this host. That gap reflects memory placement, not model FLOPs, so cross-model comparisons report tokens and latency separately and never as equal compute.

## 5. Negative results and limitations

* Exact certificate agreement is a brittle authorization rule for models that embellish JSON. On the Bonsai dev half, it cut false authorization to zero mainly by abstaining on 94% of roots.
* The 256-token arms are truncation-limited for Bonsai with thinking enabled. This is a property of the registered budget, not a harness defect.
* The six test families are synthetic procedural tasks. Results do not estimate open-ended proof-review ability.
* Inky's measured throughput here reflects host memory contention from other jobs, not its capability.

## 6. Data Goblin curriculum

`scripts/export_cpf_datagoblin.py` writes `rlt_gym.aleph_corpus.v1` streams: outcomes, sft, transitions, repairs, preferences and research. Each record keeps its source provenance (ledger sha256, raw-reply sha256, request id), model identity and checkpoint hash, mechanism family, certificate status, inference budget (stage, cap, prompt and completion tokens, latency) and repair trajectory. Evaluation roots carry custody `calibration` (dev) or `sealed_eval` (primary) with `loss.eligible=false`. Committed now: `output/evaluation_cpf/datagoblin/train_procedural`, 768 SFT roots from the train families (gate, degree, determinant), with a fresh private seed, exact generator gold, and every dev and primary root excluded. The Bonsai dev export (192 outcomes, 43 certified, 1 repair, 44 persistent failures, 35 preferences) stays private until Inky's dev half is done, because it contains dev gold.

Implication so far: the most common failure is format fidelity under a tight budget, not wrong mathematics. That favours training on certificate-schema compliance and early commitment to an answer before more reasoning-heavy critique data.

## 7. CPF-07

See `paper/cpf07_recurrent_critique_spec.md`. It specifies a compact looped critic trained to choose the next obligation whose verification most reduces residual false-authorization mass, with exact oracle labels from the CPF-01 recurrence, procedural training under quarantine, and a preregistered 1,200-root test with power analysis.
