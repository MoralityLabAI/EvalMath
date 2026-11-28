# CFH-07: sound partial-evidence research transitions

Status: finite CPU verification complete. Lean proof candidates wired into repository build and axiom check; kernel status pending. Public development only, no independent conjecture confirmation, no model training or paid compute.

## Interface

Replay CFH-06 symbolic-terminal proposals on the original twelve public decks and caps 39 and 100, using all 220 canonical routes. Old CFH-06 receipts lack the exact acquisition history, so regenerate events. An evaluator-owned immutable Env supplies exact residues, validated sparse residues or unknown, probe-to-base-group mapping, and moduli. Call Env.validate before replay. Do not accept environment truth or hidden route supplied by a proposer. A purchase spends distinct group IDs and rechecks every prior authenticated reply with newly available predictions. An observation spends one new probe and must equal the evaluator's hidden-route residue. Each event's claimed remaining bit mask must equal the independently replayed mask. Unknown entries remain compatible; only known mismatches eliminate. A terminal claim is licensed exactly at a singleton, otherwise abstain. Early abstention is permitted and does not establish optimality. All event fields are checked, so hidden labels cannot be passed as extraneous proposal fields.

The abstract soundness claim: if the true route is in S and every available prediction for it agrees with the authenticated reply, restricting S to hypotheses with missing prediction or matching reply preserves the true route. Applying a list of such restrictions retains truth and yields a subset of the original S. A singleton final state identifies the true route. The weighted-sum lemma over a commutative ring proves that replacing unavailable entries by zero preserves a weighted evaluation when every omitted weight is zero and available entries are correct. Instantiate with modular residues for the CFH-06 sparse screening argument. Lean candidate file: lean/FeedbackChannel/CFH07.lean. The six statements are in the build and axiom audit; the sandbox had no Lean/Lake and could not reach GitHub to install them. These are uncompiled proof candidates locally. Full graph coefficient identities, derivative/translation coefficient derivation, acquisition-budget arithmetic, and the Python-to-Lean refinement remain outside those theorem statements.

## Exact local results

Independent reference: CFH-04 direct enumeration of graph subsets, disjoint edges and independent set partitions; repeated derivative coefficient recurrence and Horner polynomial translation, distinct from the CFH-05 direct binomial expansion. Reference residues agree with CFH-06 environment masks in 199,980/199,980 cases, including 133,698/133,698 sparse known predictions. This is finite evidence, not a general formal proof of the graph identities.

| Cap | Episodes | Identifications | Abstentions | Events | Base acquisitions | Observations |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
|39|2640|1574|1066|15419|102960|10139|
|100|2640|2167|473|17432|190657|10062|
|Total|5280|3741|1539|32851|293617|20201|

All 32,851 events verified, matching CFH-06's symbolic-terminal identification counts. 480 traces (every eleventh hidden ID per deck/cap) each mutated ten ways: corrupt mask, false promotion, missing finish, event after finish, repeated purchase, invalid group, over-budget acquisition, forged reply, invalid probe, over-budget observation. All 4,800 rejected. This is an exercised mutation set, not exhaustive adversarial verification.

Projection removes evaluator-only hidden IDs and separates policy proposal, environment reply and verified version set. Hex masks avoid loss of precision in JSON consumers. Exact duplicate histories within deck and cap are removed by content hash: 981 removed, 4,299 remaining with 26,405 events (3,741 singleton episodes). The trace pack is a development candidate only. Proposals are observed heuristic actions, not optimal-action gold. Do not feed entire episodes with future information as inputs; only prefix and current proposal target, followed by masked environment feedback and separately attributed verified state supervision. All decks and grammar variations belong to the public CFH family. Do not claim independent roots, training admission, or increase the existing token quota. Full split and rights audits, root-presentation caps, tokenizer counts, and a training adapter with causal prefix masking are required.

## Replay

With Python 3.13, NumPy, NetworkX, SymPy; pass the original CFH-06 gzip receipt path explicitly:

    cd gyms/CFH07
    OPENBLAS_NUM_THREADS=1 python audit.py /path/to/cfh06_receipt.json.gz > receipt.json
    python export_candidates.py receipt.json > candidates.json

The generated receipts and candidate pack are not committed. Hashes of locally replayed bytes (uncompressed):
- transition.py: 0faa666f2c02e361604151aa49d7c2353979b063f78b9a83738684969ba09305
- audit.py: fa6c04916b47a584a288b773760817ec8d902719f291c09f9741269063eef621
- export_candidates.py: 8dda6c7ae8bfa595966d6d6d89a00dc9db7a624dc9d807aa8249e43c800f0c15
- receipt.json: 296cf379dfd30ce7639ef1605b3123686810cad2a304081f8fa05eaa6ffe1157
- candidates.json: fb9f7027a2d95014104d3162393b8b1eb478c0d338bf210388f88422f3251c9a

All five remote Python source copies matched tested Git blob hashes. Repository-wide test suites, lint, and Lean kernel verification remain outstanding. No sealed test accessed. Candidate code copied into DataGoblin PR #65 for further development.
