# ProofCompactBench v1 — certificate-graded proof compaction

Status: exact synthetic development gym; native cost lane requires a successful trusted Lean receipt. CPU only. No model evaluation or corpus admission yet.

Companion research: [Compactification-Theory PR #324](https://github.com/MoralityLabAI/Compactification-Theory/pull/324), [MathCan PR #300](https://github.com/patrickdugan/MathCan/pull/300), [DataGoblin PR #125](https://github.com/MoralityLabAI/DataGoblin/pull/125). This gym is separate from RHProofDistillation, which scores Lean reconstruction.

## Exact families

| Family | Submission | Validity | Optimization |
|---|---|---|---|
| factoring | helpers | admissible capture, helper and parent-size cap | total modeled closure cost |
| scheduling | order | topological order, all nodes once | peak live weight |
| retention | keep | inclusive interval capacities | minimum extra reloads |
| uniform | basis | independent rows with identical common kernel | rank |
| continuation | classes | observation/successor congruence | minimum classes |
| repair | order | corrected legal schedule | peak live weight |

Synthetic cost models are defined in each packet. They are not measured Lean costs. The gold oracle uses subset DP versus exhaustive topological orders; interval greedy versus exhaustive subsets; factoring subsets versus an independent parent-budget DP; rank-nullity versus state enumeration; and explicit-state partition refinement versus invariant row-space closure. Alternative valid optima receive full credit. Invalid or missing answers score zero; feasible suboptimal answers receive 0.5+0.5*(optimum+1)/(cost+1). Report validity, exact optimum rate, mean score and per-family results separately.

96 public roots grouped into train (64 roots/384 tasks), calibration (16/96), development test (16/96). All 576 public prompts are unique. Test roots use larger structural dimensions. The public generator/gold are visible; this is not a sealed benchmark. An extra 32 stress roots passed all 192 tasks. A separate operator-held seed and private root generation provide fresh instances, but 32-bit seeds and shared generator families do not establish contamination resistance. Check private prompt collisions and keep gold outside the model's context. Hold out new structural families for scientific generalization. No real GRH proofs are included in training examples.

## Commands (Node >= 20; no dependencies)

    cd gyms/ProofCompactBench
    node bench.mjs self-test
    node bench.mjs build-public /new/pcb-public
    node bench.mjs build-private /new/pcb-private OPERATOR_SEED 64
    node bench.mjs grade /path/dev_test.gold.jsonl /path/predictions.jsonl /new/score.json
    node bench.mjs export-train /path/train.gold.jsonl /new/train-candidates.jsonl

Give only the corresponding public JSONL packets to the model. Predictions are JSONL objects with exactly id and answer; the answer is the typed certificate described in the packet. Unknown/duplicate IDs fail closed. Public and gold artifacts are separate and hash-pinned in the build manifest. Export refuses calibration/test/private roots. DataGoblin candidates must undergo its own tokenizer, collator, deduplication and mixture admission; admitted_tokens=0.

## Native proof-cost lane

Native validation stays in Compactification-Theory's pinned Lean 4.35.0 workflow. Its matched inline/factored fixtures use identical statements, exact baseline axiom set, independent module replay, 3 compile trials, local reachable closure object count, parent count, .olean size and RSS/time. The source transformation is a trusted restricted action menu, not arbitrary model-submitted Lean. Import only an operator-trusted successful CI artifact with externally recorded SHA-256; do not let a model supply its own receipt/hash. The menu grader checks receipt shape, pair identities, replay, equal allowed axiom sets, and metric accounting. It does not rerun the kernel or attest artifact provenance by itself.

    node native.mjs self-test
    node native.mjs packets /path/native-factoring.json TRUSTED_SHA256 > native.public.jsonl
    node native.mjs grade /path/native-factoring.json TRUSTED_SHA256 predictions.jsonl

The six native tasks choose inline or factored to minimize total local closure objects. Smaller parent size alone cannot win. Compile wall time, peak process RSS and file bytes are separate measured secondary outcomes, not rewarded noisy single-trial estimates. Both actions must already pass validation to admit a fixture; incomplete/failed receipts fail closed. No claims about real GRH proof equivalence, verifier savings, or trained model performance. Native receipt tests use mock data only; the actual Compactification-Theory native run must be green before admitting cost labels.

For Aleph post-training: compare fixed recurrent depth, learned stopping, matched visits, and exact solver baselines on fresh roots. Meter valid/optimal answers, recurrent visits, and verifier cost separately. Train on permitted verified certificates only. A native proof-writing task (rather than restricted choice) requires sandboxed Lean execution, exact challenge comparison and axiom audit, separate authorization, and fresh holdouts.

## Evidence

The core self-test executed in the session JS engine: 576/576 public reference certificates, 192/192 additional stress certificates; 9 rejection/relabel/missing-answer controls. Native menu receipt validator passed 8 synthetic controls, including a smaller parent with larger closure. Hosted CI separately replays actual CLI operations. See receipt.json.
