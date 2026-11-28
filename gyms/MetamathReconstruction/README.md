# Metamath proof reconstruction (MM-GYM-02)

Companion to [MathCan PR #290](https://github.com/patrickdugan/MathCan/pull/290) and its pinned [MM-GYM-02 protocol](https://github.com/patrickdugan/MathCan/blob/09bc1b03557eadb58b2d2d8961ee956574e450ec/research/metamath_gym/MM02.md).

This standalone scorer consumes the MathCan CI artifact (inputs.jsonl, oracle.jsonl, receipt.json). It validates ID correspondence, source snapshot, source-order split, candidate bank and SHA-256. Scores count every verifier-accepted completion, including alternatives to the reference. Oracle is private to the scorer; a model gets inputs only. Prediction files use one JSON object per line: {"id":"theorem-label","ranking":["candidate-label",...]}. Partial coverage is scored as failures on missing rows. Baselines: expected uniform, first-in-bank, train-only reference frequency, and prefix-legality diagnostic using one verifier call per candidate. The prefix diagnostic uses oracle fields and is explicitly verifier-assisted. Report top-1/3/5, any hit and coverage. No model or training outcome is claimed.

Run: python gyms/MetamathReconstruction/score.py /path/to/mm-gym02-corpus [--predictions predictions.jsonl]

Tests: python -m unittest discover -s gyms/MetamathReconstruction -p 'test_*.py' -v

The public challenge is source-order-separated only. Candidate banks include the reference; earlier theorem labels remain available. Related dependency families can cross splits, and public proofs may be in model pretraining. Do not interpret a high score as independent theorem discovery. The scorer trusts the pinned extraction receipt and upstream verifier labels; a digest gives integrity relative to that receipt, not external attestation. Real proof repair with an unrestricted action set and dependency-family held-out evaluation are separate gates.

## DataGoblin handoff

Treat inputs as observations, ranked candidate labels as actions, verifier-accepted final proof as reward. Keep the oracle outside model context. Record candidate queries, exact final replays, inference tokens, peak RAM and wall time separately. BPD steering trials should use identical roots, candidate banks and verifier budgets across ordinary, task-guided and matched-sham training arms. Do not use the public challenge to select interventions. First run non-neural baselines and verify receipt; then preregister family-held-out data before claims about generalization.
