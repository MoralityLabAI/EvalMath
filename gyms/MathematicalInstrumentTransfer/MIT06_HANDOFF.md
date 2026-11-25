# Local checkpoint handoff

The four-family development runner is present. From this directory, with NumPy and pytest installed:
```
python higher_order.py
python proof_pilot.py --output proof
python -m pytest -q check_suite.py
```
All five checks passed locally. The model transcript scorer is separate; no model runs occurred. Use a fresh context for each row; dispatch only the prompt string (row_id leaks arm and truth). Never expose proof_private.jsonl to the model. Freeze checkpoint, template, sampling parameters and total token budget before the experiment. Match actual tokenizer counts for source vs sham before comparing. Return each response as a JSONL row with row_id, tokens_in, tokens_out and response object. Include all retries in token accounting; missing or overbudget rows fail. Run:
```
python score_model.py --private proof/proof_private.jsonl --responses responses.jsonl --output scores.json --budget 2048 --checkpoint CHECKPOINT_HASH
```
2048 is an illustrative development budget, not a frozen confirmation parameter. This evaluator checks finite certificates and records adapter-reported tokens, not authentic server usage. Actual model comparisons and prospective sealing remain blocked. No changes to central exact receipts or Lean claims.
