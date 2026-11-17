# EVAL-AUTH-01: the exact value of an authorization observation

**Scope:** finite rational-valued synthetic populations, externally supplied binary authorization, deterministic public readout, and one additional audit readout. No model or judge calls. No assumption that real evidence or authority is authenticated.

For each hidden world `w` with mass `p(w)`, let `A(w) in {0,1}` denote the policy-defined authorization and `O(w)` the information presented to a controller. An optimal deterministic classifier under symmetric binary-error loss chooses the more probable authorization label in each observation fibre; ties choose denial. Its minimal probability of error is

```
R*(O) = sum_o min(P(O=o, A=0), P(O=o, A=1)).
```

An authenticated audit, if it truly supplies an additional observation `Q(w)` before action, refines each fibre to `(O,Q)`. The exact optimal error improves or stays unchanged:

```
R*(O,Q) <= R*(O).
```

For a uniform pair of worlds sharing `O` but requiring opposing decisions, public-only accuracy is at most 1/2. A perfectly separating audit can reduce optimal error to zero. These are elementary decision-theory identities over a fixed finite distribution, not empirical claims of generalization.

The implementation uses exact `fractions.Fraction` throughout. `optimal_observation_policy` returns minimum error, accuracy, authorization TPR/FPR and the selected decision in every observation fibre. A zero class denominator is reported as `None`. An independent test oracle enumerates *all* deterministic policies for every small partition. Four-state exhaustive testing visits `sum_{n=1..4} 8^n = 4680` world/observation/audit families; it verifies the closed form and the monotonic improvement.

```sh
PYTHONPATH=src python -m pytest -q tests/test_evaluation_authorization_quotient.py
PYTHONPATH=src python scripts/verify_eval_auth01.py --output /tmp/eval_auth01.json
```

**Integration contracts**

- `patrickdugan/MathCan` AUTHQ-01 proves authorization factorization and an observation-collision impossibility theorem.
- `patrickdugan/OntologicalProofs` OCA-SW-02R separately tests the action/report decision under differing authority facts and pressure.
- `MoralityLabAI/Control-Harness` PR EVID-IND-01 checks whether two individually attested documents actually come from independent declared control domains. Its lineage fields are synthetic, not an authentication guarantee.
- `sadasant/organon` types PermissionExercise and IndependentFor; a later bridge must specify the trusted translation from those records into `A(w)`.
- `idolum-ai/spectral-faithfulness` could provide paired multi-user or poker scenarios after the information-boundary labels are rebuilt and independently checked.

**Prospective experiment:** register independent generator roots (at least 20 for any FSI-01 positive confirmation), matched hidden/revealed authorization twins, fixed default-deny and always-authorize baselines, and external source-attestation checks. Use `paper/finite_sample_inference.md` to preflight effect size, confidence and sealing. If the controller selects inspection actions, their costs and observations belong inside the game. A complete trace is required even for refusals. No experimental claim follows from the synthetic oracle's perfect decisions.
