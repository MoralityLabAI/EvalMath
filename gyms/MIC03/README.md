# MIC-03: dependency-aware and learned certificate scheduling

Public CPU development follow-up to [MIC-02 draft #85](https://github.com/MoralityLabAI/EvalMath/pull/85) and [MIC-01 draft #83](https://github.com/MoralityLabAI/EvalMath/pull/83). No upstream manuscript material copied. This experiment concerns coordinate scheduling on finite certificate problems, not the textual mathematical-history intervention.

## Method

Train on 48 five-coordinate acyclic recurrence roots and 48 sparse cover roots (seeds 0–47 per family). The separate development suite uses 24 new seeds per family and per size (1000–1023), five and six coordinates, four generator variants: DAG, cyclic-permitted recurrence, sparse cover, dense cover. The size pairs share seed identifiers; treat generator lineages as groups, not 192 independent mathematical families. No sealed confirmation. The recurrent and stateless 1,793-parameter rankers share architecture, same training examples and initial model seeds (17,29,43), use 100 full-batch Adam steps and optimal-action set likelihood. The stateless arm resets the GRU hidden state at every step; the recurrent arm retains it. Teacher forcing chooses the lowest-index optimal next action, and target masks include all tied optimal actions. No oracle labels at rollout.

All four policies scan every unused coordinate at each step, verify candidate certificates, and update each coordinate exactly once. Both learned arms receive the same ten candidate features; deterministic arms compute the same scan and features. Actual score-call counts are 36 (n=5) and 49 (n=6), including repeated baseline normalization checks. Equal update and score-call counts do not imply equal runtime or arithmetic cost. Exact schedule oracle enumerates all possible remaining action orders via memoized search; exact certificate oracle is the monotone least fixed point for recurrence and exhaustive integer-grid minimization for covers. Oracle costs are diagnostic and excluded from policy counts.

For recurrence, the map H(p)=b+ceil(Mp/10) is monotone; iteration from zero increases and is bounded by any feasible certificate. Integer coordinates and a finite feasible upper bound imply termination. By induction its limiting fixed point is componentwise least feasible. For a DAG, choosing an unresolved sink ensures its dependencies have been finalized, so a reverse topological pass obtains the least fixed point. The generator permits cycles in its cyclic variant; it does not require every sampled graph to be cyclic or strongly connected.

## Public results

192 evaluation rows, 96 training roots, six model fits, 100 epochs per fit, PyTorch 2.10.0+cpu. Local wall clock 4.929 s for training and evaluation (one CPU thread). Four targeted pytest tests passed, including independent exhaustive checks of schedule and cover oracles for 20 small roots, teacher labels and invalid proposals. Lower gap is better. Gap = (policy objective - budgeted schedule oracle objective)/initial objective. Average across roots, then model seeds; hits count each seed separately.

| Family | Greedy gap % | Dependency gap % | Stateless gap % | Recurrent gap % | Schedule-to-certificate budget gap % |
|---|---:|---:|---:|---:|---:|
| DAG | 0.83540 | 0 | 0.73925 | 0.73925 | 0 |
| Cyclic-permitted | 1.38897 | 0.90184 | 1.99562 | 1.95391 | 19.14378 |
| Sparse cover | 1.22192 | 0.26184 | 1.22192 | 1.22192 | 0.09375 |
| Dense cover | 1.38177 | 1.43519 | 1.01669 | 1.01669 | 0.19135 |
| All | 1.20702 | 0.64972 | 1.24337 | 1.23294 | — |

Dependency reaches the schedule oracle on 148/192 rows, greedy on 120/192. Learned stateless reaches it on 388/576, recurrent on 390/576 model-root pairs. Model repeats are not independent roots. Recurrent vs stateless mean benefit +0.010427 pp, versus dependency -0.583224 pp. Paired recurrent-vs-stateless benefits by seed: +0.012474, 0, +0.018808 pp. The positive dense-cover result is shared by stateless, so does not establish a recurrent-state mechanism.

The large cyclic budget gap is more important than scheduler differences. With every coordinate updated once, no scheduler can remove that gap. Investigate revisits and stopping criteria, including residual bounds and an exact dynamic-programming ceiling at matched visit budget. For covers, preserve the dense/sparse shift and compare learned rankers against improved competition and lookahead controls. Avoid paid compute pending a stronger effect.

## Replay

```sh
cd gyms/MIC03
python -m pytest -q test_mic03.py
python run.py > /tmp/mic03-results.json
```

Requires an optional local PyTorch CPU installation (tested 2.10.0+cpu); no dependency or weights downloaded by this script. Keep this optional experiment outside the default repository pytest paths.

Source SHA-256: 6c1355587920351afffb8860fa2a6844e48f5d95f7d790d1a28a4f43eb3e1336.
Test SHA-256: 5bbaf8ae6eeaffe6fbb3e0af82368f4c3a8382918c0b4035ef93a411a30a81c2.
Raw sandbox result SHA-256: 5f6fd8aa4b288f58583c169a4505f74a0488961b1ca20fa9683d5b7f379ec2ee (includes wall time, so full hash is not expected to recur). No raw run or checkpoint committed.

**Evidence class:** public development only, REDESIGN_OR_PILOT_ONLY. At most four generator lineages, no sealed families, no validated independence. Matched stateless-seed disagreement supplies an exploratory sham; maximum absolute per-root sham by family 4.321, 2.778, 0, 4.000 pp. Four grouped development effects cannot estimate a 95/95 sham tolerance bound, and the recurrence-state benefit is far below the inherited 5 pp scientific floor. Three model contrasts reported descriptively. No full repository CI or confirmed training promotion. The original DLMST reference materials remain quarantined for training. No paid inference or GPU used.


## Executed resolution planner

Copied the current repository planner into the sandbox and verified its Git blob identity (0ff062f76f5534d9f18425f986ae3e750397f50c) before running it on the grouped pilot. Strict exit 2. The frozen public pilot input and generated output are included. The planner lists unsealed holdout, unverified independence, uncalibrated sham quantile, too few pilot worlds, and observed effect below the mechanistic floor. The nominal normal-power estimate is invalid as a promotion argument because of these explicit failures.

From the repository root:

```sh
python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC03/preflight_input.json --strict
```

Input SHA-256: 091cb80bede494a49ba74a8fc2c9302284f49c6ecf6a36db581934ac9c56bb61. Output SHA-256: 63f38fad474aa49b7cc990eb538b7fd6d7e15fac107fcc8846b6847905ae3921.
