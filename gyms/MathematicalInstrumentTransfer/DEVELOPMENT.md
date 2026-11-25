# MIT-01B development checkpoint

**Evidence: finite verified fixtures. No model measurements.** Generate the two development JSONL files:

    python gyms/MathematicalInstrumentTransfer/development.py --output /tmp/mit01b-dev
    python scripts/check_receipts.py --only mit01 mit01b_dev

64 distinct generated numeric roots (32 per family), 64 true exact-maximum claims and 64 false variants one unit below the maximum; six arms for each true claim and two arms for each false claim, 512 rows. Rows and variants share roots. There are only two templates/families. Do not count these as 512 independent observations or claim cross-family generalization.

The LP generator constructs a feasible attaining point and a nonnegative combination of constraints; a separate exhaustive box search establishes the maximum. The path generator constructs a tight chain and feasible potentials; independent enumeration of all directed paths establishes the maximum. An invalid multiplier vector or perturbed potential is paired with the same true target. Each false bound has an explicit counterexample. Certificate checking uses exact integers and rejects malformed or invalid certificates. Closure verification does not check the separate applicability classification: for oracle and near-miss arms, compare the model's boolean mapping_valid against the corresponding gold field separately. A false target's rejection is distinct from true-target proof closure.

Only pass the prompt string to the model; the JSONL row metadata contains the arm and truth variant. Keep gold out of model input. These open development generators and deterministic seeds cannot provide a sealed test. The common response contract explicitly names the certificate family; this is guided execution and repair, not spontaneous invention or cross-domain technique discovery. The current irrelevant-source sham is format-oriented and not token matched. Before comparing models, implement tokenizer-aware matched budgets and shams, blind dispatch and frozen checkpoints; count reading, output, failed retries and verification. Additional held-out generator families and a prospective manifest are necessary before confirmation.

Run the repository power preflight only after independent measured development effects and matched sham observations exist. Status BLOCKED_NO_MEASURED_DEVELOPMENT_EFFECTS_OR_SHAMS. No neural effect, Lean closure of these fixtures, or confirmation claim.
