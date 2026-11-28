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


## EVAL-AUTH-02: the inspection-budget frontier

A downstream finite theorem and independent arithmetic oracle accompany Control-Harness's [ECA-01 prospective readout](https://github.com/MoralityLabAI/Control-Harness/actions/runs/44131080443). Write `T_i^1,T_i^0 ∈ {0,1}` for the same policy's retain decision on the authorized and unauthorized twins of root `i`, and `a_i∈{0,1}` for whether that root is inspected. For all unaudited pairs, identical public observations imply `T_i^1=T_i^0`. Hence, for `N` equally weighted roots:

```
Σ_i T_i^1 <= Σ_i T_i^0 + Σ_i a_i
J := TPR - FPR <= (Σ_i a_i)/N <= B/N.
```

This is sharp when an exact signed audit separates the counterfactual worlds and the controller retains the authorized twin only. `audit_budget_certificate` in `src/spiral_ln/evaluation_authorization_quotient.py` evaluates the exact rational certificate for arbitrary finite paired-decision rosters and rejects unaudited pairs that produce incompatible decisions. The tests enumerate all six admissible audit/decision configurations over one through four roots, and check the registered 64-root example. The corresponding Lean proof is proposed in MathCan's `AuthorizationQuotient.lean` on [AUTHQ-01 PR #140](https://github.com/patrickdugan/MathCan/pull/140); proof status should follow its hosted Lean CI.

### Host-frozen synthetic readout

The ECA-01 source and protocol froze at commit `bc0ebeb053c5038a2abb20444effda235f7dc060`. A separate request commit `3adbe9b23c98e58c46751449cb68126ff4b45f42` caused CI to sample 64 independent 256-bit root entropies after the freeze check, with two matched permission worlds per root and six fixed policy arms.

| Arm | TPR | FPR | Root pairs inspected | J |
|---|---:|---:|---:|---:|
| Existing attested two-key | 64/64 | 64/64 | 0 | 0 |
| Issuer-lineage only | 36/64 | 36/64 | 0 | 0 |
| Audit only after lineage escalation | 64/64 | 36/64 | 28 | 7/16 |
| Audit all | 64/64 | 0/64 | 64 | 1 |

The 28 selectively inspected pairs cost 56 individual auditor calls because each twin was scored. The fully inspected arm made 128 calls. Both audited arms **saturate** the general budget bound, conditional on the host auditor's correct revelation of planted truth. The lineage-only rule reduces the observed unsafe-retain rate from 1 to 9/16 while escalating both members of 28 shared-issuer pairs; it preserves 36/64 authorized retentions.

The companion [readout artifact](https://github.com/MoralityLabAI/Control-Harness/actions/runs/44131080443/artifacts/14350041730) includes 768 raw rows, root entropy, the FSI-01 compatible manifest, and a source/output SHA-256 receipt. An independent byte-level audit of its downloaded ZIP found exact matches for all four output digests, distinct input seeds, 64 equal-public-observation twin pairs, correctly derived issuer-group labels, and full row-to-aggregate parity. The raw trajectories SHA-256 is `3df4396bbd9027f9626364c61a31b08537d18dcaf1b84876b19b33962ebce55b`.

**Evidence limit:** These are exact mechanistic outcomes for a synthetic finite system. The issuer trust roster and auditor hold the world's truth by construction, with toy HMAC keys controlled by the host. No actual external issuer's identity was independently authenticated. The FSI manifest has `exchangeable_pair_labels=false`, and no model-based causal improvement is claimed. The empirical test of whether a learned TRM or LLM can choose inspections remains open.
