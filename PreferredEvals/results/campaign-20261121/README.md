# Campaign 2026-11-21: registered development analysis

The registration is frozen at [`bffa41b`](https://github.com/MoralityLabAI/EvalMath/blob/bffa41b1db4af204e7548d1b4f25d8688d0cd98b/PreferredEvals/results/campaign-20261121/registration.json). Seven between-model comparisons plus one within-Bonsai no-CoT comparison constitute **one family of eight**. The scientific minimum effect is **0.10**. Bonsai data were partly visible at registration, so these results remain development evidence even if an adjusted p-value is small.

The original `gym/compare.py` defaults (`0.05`, one comparison) do not define the campaign. For each paired prompt comparison, use `--minimum-effect 0.10 --planned-comparisons 8`; for native harnesses import task-level paired receipts and generate FSI-01 with the same registration values. Preserve case-level assignments and error outcomes.

```sh
# For a paired prompt-run comparison, using real saved paths:
python PreferredEvals/gym/compare.py \
  --candidate-run runs/<candidate> --baseline-run runs/<baseline> \
  --candidate-scores runs/<candidate>/scores.json \
  --baseline-scores runs/<baseline>/scores.json \
  --minimum-effect 0.10 --planned-comparisons 8 \
  --out runs/<comparison>/paired.json --fsi-out runs/<comparison>/fsi.json
PYTHONPATH=src python -m spiral_ln.evaluation_finite_sample \
  --manifest runs/<comparison>/fsi.json --output runs/<comparison>/fsi-result.json

# Then register paths in receipt_index.json for all eight IDs.
python PreferredEvals/gym/campaign_report.py \
  --registration PreferredEvals/results/campaign-20261121/registration.json \
  --index PreferredEvals/results/campaign-20261121/receipt_index.json \
  --out-json runs/campaign/eight.json --out-md runs/campaign/eight.md
```

`receipt_index.json` presently marks all eight comparisons as **missing receipts** because the frozen branch contains only registration metadata. This is an accounting assertion about the committed files, not an assertion that local model runs failed or never occurred. Fill exact paths to `fsi-result.json` and paired receipt files as they are published beside the index. The report validates every FSI effect floor and family size, preserves full assigned and missing denominators when supplied, and calculates Holm across the eight registered tests. Missing p-values are effectively 1 in the correction while their results remain explicitly unavailable.

## New outside research-taste source

[Ideation Arena, EMNLP 2026](https://aclanthology.org/2026.emnlp-main.688/) uses blind researcher preference comparisons. The [Hugging Face data](https://huggingface.co/datasets/yolo1213811/research-ideation-arena-dataset) is `CC BY-NC 4.0`. Its dataset viewer currently fails because `queries.json` and `final_ideation_results_with_response.json` have distinct schemas; download the latter directly, keep both under their pinned upstream revision, and use `gym/ideation_arena.py` to extract development task and label files separately. `D4` is a configurable selection placeholder: verify dimension semantics against the paper and original labeling rules before results are published.

```sh
pip install ijson
python PreferredEvals/gym/ideation_arena.py \
  --comparisons /path/to/final_ideation_results_with_response.json \
  --out-tasks runs/ideation-arena/tasks.jsonl \
  --out-labels runs/ideation-arena/labels.jsonl \
  --dimension D4 --limit 24 --ack-noncommercial
```

Treat task roots as research-context groups; further linked ideas and researchers may induce additional dependence. This tests judge agreement with recorded human preferences, not the ability of Bonsai or Qwen to generate original high-quality proposals.
