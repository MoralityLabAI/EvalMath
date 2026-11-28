# SCOUT-01: purchase information when it changes the decision

**Evidence:** Exact rational algebra for the declared finite binary signal model, independently enumerated on development grids. Five hand-authored source roots and twelve development cases are **diagnostics only**. No student learning, native game transfer, sealed evaluation or neural mechanism result is asserted.

## Game and value

A hidden good route G in {left,right} has prior P(G=right)=p. A direct choice earns 1 for the good route and 0 otherwise. Before choosing, the actor may purchase one conditionally independent binary scout signal S with fidelity q, at nonnegative cost c. The scout arrives before the final route choice. The actor has enough turns for scouting only when `scout_available` is true.

With p denoting the posterior **after existing public reports**, the first-action values are

```
V(commit_left)  = 1 - p
V(commit_right) = p
V(scout) = max(p*q, (1-p)*(1-q))
         + max(p*(1-q), (1-p)*q) - c
```

The two maxima are the optimal decisions in the two mutually exclusive scout observation branches, with the joint observation probabilities already included. If scout is unavailable it is an illegal action. The gross value of information is V(scout at c=0) - max(p,1-p); the optimal first move is any action attaining the maximum value. Ties are preserved as valid optimal actions. For p=1/2 and q=4/5, the gross information value is 3/10; c=1/10 yields V(scout)=7/10 versus 1/2 for a commitment. At c=3/10 all three first moves tie. At c=2/5 either commitment is optimal, with scout worth 2/5.

## Report ancestry and causal edits

Every published report declares `source_root`, its direction, and exact reliability. Repeating a report from one root relays **one noisy draw**. Distinct roots correspond to conditionally independent draws given G. Conflicting reports or reliabilities under the same root are invalid input. This is the actor-visible observation model: the environment privately grades from the same public information and never exposes the hidden route or gold action in the actor task.

Three identical left-favoring reports of reliability 3/5, all sourced from one witness, yield P(G=right)=2/5. Their posterior-optimal move is to scout at cost 1/10: V(scout)=7/10, V(commit_left)=3/5. Reassigning the reports to three independent witnesses changes P(G=right) to 8/35. Now V(commit_left)=27/35 exceeds V(scout)=7/10. A baseline that treats relays as independent suffers exact decision regret 1/10 on the shared-root case.

`cue_favors_right` is an attractive surface clue with no specified information about G. Flipping it is a sham and must preserve the oracle values. A conflicting informative report of reliability 4/5 favoring right makes a cue-following left commitment suffer regret 3/5. Changing the scout's cost, fidelity or availability can change the legal optimal first action.

## Playable state and integrity

`realized_reward` is a small deterministic simulator. Its owner supplies a hidden route and, following the scout purchase, the actually sampled report; the second decision is made from the updated posterior. `enumerated_expected_reward` independently averages the true route and scout branches and must equal the first-action Bellman value for every legal action, including ties and impossible observations. All math uses `Fraction`.

`development_cases` is a frozen 5-root / 12-case diagnostic grid. `development_views` emits play, causal revise, cosmetic hold-steady and repair views for two roots, with `parent_root` retained by the grader. These are **not** twelve or eight independent tasks. Training episodes built from the same source family, its alternative renderings, and all counterfactuals must share one train/dev/confirmation partition. These public development examples belong to `dev`. Future sealed task families remain outside the repository and should be registered before evaluation.

A model reports its first action and belief about the right route. Score action regret from its public posterior-information state, and belief calibration separately against the ex ante public distribution or realized hidden draws. Regret is unaffected by whether a sound stochastic decision happens to lose on one play. Source-root custody belongs to the grader; provenance ids of reports must remain visible to the actor. `public_task` omits the oracle values and generator root id. A render adapter must pass only its `public_task` payload, never a whole linked-view or grader record.

## Weak players and acceptance gates

`cue_following` tracks the irrelevant surface cue. `always_scout` pays for a report even when it costs too much or provides redundant evidence. `double_count_relays` mistakes three retellings for three independent sources. `always_commit` never buys information. `exact` is a transparent structural ceiling; it is a privileged algorithmic controller, not a learned agent. Baseline failures and cosmetic invariances are explicit source-hashed verifier checks.

This small preflight has 5 independent synthetic generator roots, 12 correlated cases and 8 linked views. Planned and actual trained-model comparisons are **zero**. Minimum meaningful downstream effect and matched neural sham floor are **unmeasured**. The evaluation therefore remains `PILOT_ONLY` under EvalMath's root-level power skill. Any proposed 50-family trained-student test requires independent family-level measurement, a preregistered meaningful performance improvement, a matched sham pilot, and a prospective sealed split. Match student initialization, tokens, verifier calls and frozen policies; account separately for advisory inference cost. Report native game returns when an exact oracle does not apply. Prevent cosmetic rewrites from earning independent-root credit.

## DataGoblin integration contract

- Export actor-visible `public_task` and separately store `private_grade`, `root_id`, `case_id`, `split`, and exact source hashes in the grader archive. `legal_actions` includes `scout` only when permitted.
- On `scout`, sample one fresh independent report from the declared signal law, expose it, debit the cost, and make the final commitment. Verify that action values and any training target use the **pre-action** information state.
- Retain all four linked views under the same parent root; preserve the bad move in repair. Train candidates must remain `training_ready=false` until source-rights, lineage and transfer checks finish.
- Later render the same math as a route-building game, a council witness hearing, and a cooperative message game. The current `cooperative` label is a narrative fixture only; no teammate message protocol or partner-policy transfer has been evaluated.

### Reproduce

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_evaluation_scouting_value.py' -q
PYTHONPATH=src python scripts/verify_evaluation_scouting_value.py --output /tmp/scout01_dev_v1.json
PYTHONPATH=src python scripts/check_receipts.py --only scouting_value
```

References: DataGoblin AGN-01 PR #50; GPTStoryworld HGW-05 causal benchmark; EvalMath HG-04 PR #41, HG-09 PR #48, and FSI-01. Exact development cases, source hashes and baseline regrets live in the generated receipt.
