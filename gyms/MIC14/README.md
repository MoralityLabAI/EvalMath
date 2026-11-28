# MIC-14: proof-history replay, opportunity balance, and a deterministic ceiling

Public cloud CPU development follow-up to [MIC-13 draft PR #97](https://github.com/MoralityLabAI/EvalMath/pull/97). The pinned MIC-13 checker and generator are included under reference/ from commit 1be391fa037899c43c0d92d3a770f6552976cca0. The source is original synthetic weighted binary constraint problems; no DLMST manuscript bytes or proof text are used.

## Replay contract

Verify the complete archived proof for each root and policy before extraction. The replay starts with the certificate's verified final feasible incumbent L and total weight as a trivial upper bound. This incumbent is intentionally provided to every arm; the task is retrospective proof acquisition and not original search or discovery from scratch. A frontier obligation has its raw active/required state, a bound inherited from revealed ancestors, and a provenance node ID. Revealing a node tightens its cap to the minimum of its inherited cap and verified local bound. A branch exposes both child obligations with that cap, unless it already lies below L. Terminal, pruned, infeasible and residual-optimum leaves close; unresolved open leaves retain their cap permanently. The global interval is [L, max(L, permanent open cap, outstanding inherited caps)]. This is sound because the MIC-13 proof checked all state reductions and branch partitions. The full archive replay interval equals the source interval on all 144 proofs. Alias cases are not supported by this extraction (the source archive has none).

Construct an artificial deterministic chronological replay, choosing the highest inherited cap, then highest raw active weight, then lowest node ID. This is NOT the original producer event chronology. At a state with >=6 previously revealed records and >=2 candidate obligations, take up to four candidates by that same rule. The exact one/two-reveal target for each first action is the best attainable global upper-bound reduction among one reveal or a second reveal selected from the same top-four rule after the first. This is a restricted oracle, not unrestricted proof search. A decision is consequential iff candidate utilities differ. Many all-tie states are present. Histories carry the last six records as 15-dimensional summaries. Candidates have 11 raw-state/cap features and five common state features; no future node kind, proof content, descendant, oracle label, step index or node ID is fed into the model. History records include realized past cap and frontier summaries, which can partly reveal relative order even after shuffling. Provenance and labels remain in the exported JSONL for audit; do not feed those fields indiscriminately into a learner.

Train conflict and mixed families, evaluate implication and disjunction; group both search policies and all decisions of the same root together. The 72 archive roots split 36/36, five training roots yield no eligible history rows, giving 31/36 represented roots. There are 34 informative development roots and only two development generator lineages. These are public, unsealed reused generator structures, not independent prospective math problems. Train twelve 2401-parameter GRU/MLP rankers per variant, three seeds (17,29,43), 90 full-batch Adam steps on informative training rows, tied-optimal set loss. Ordered and shuffled arms receive identical records and six shared GRU visits; shuffle the earlier five records and retain the latest, with independent seed-derived permutations. Latest-only and unordered pooling also execute six visits at the same parameter count, resetting hidden state. Evaluate the ordered checkpoint with shuffled history as a further intervention. No model rolls out a complete search; each predicts a first action on fixed replay states, and scoring grants the exact best second reveal. Accuracy and summed oracle-gain recovery are conditional offline diagnostics, not realized policy utility. The stronger deterministic first-action control is computed before considering learned performance.

## Results

All 144 MIC-13 certificates replayed during each extraction. 16,735 rows in each variant: 7,646 training, 9,089 development. In MIC-14a there are 721/604 informative training/development decisions. In MIC-14b there are 797/637. For the development data, 93.35% and 92.99% of states have equal utility among all candidate actions.

| Policy | MIC-14a informative accuracy % | MIC-14b informative accuracy % |
|---|---:|---:|
| First (highest inherited cap) | 100 | 100 |
| Highest cap then cheapest | n/a | 100 |
| Gap per byte | n/a | 82.575 |
| Latest | 64.294 | 69.911 |
| Chronological | 62.252 | 70.434 |
| Shuffled | 62.583 | 70.330 |
| Bag | 62.804 | 70.801 |
| Chronological checkpoint, shuffled at test | 62.528 | 70.277 |

Neural metrics average three seeds per arm. Chronological/shuffled oracle gain recovery: 84.160/84.416% for a and 80.689/82.609% for b. First recovers every oracle gain (6772 summed weight units in a, 5869 in b). Summed gain is a fixed-state score, not cumulative gain along a single trajectory. The ordinary chronological all-state accuracy 97.491% and 97.928% reflects the overwhelming proportion of ties.

MIC-14b is a post-hoc redesign after observing the first-arm ceiling in MIC-14a. It charges the canonical compact sorted-key JSON bytes of each node (2048 total across at most two reveals), with exact byte lengths supplied as public metadata; eligible candidates must fit remaining budget. Node byte size is a proof acquisition proxy, not verifier CPU work. The original behavior trajectory is retained; the budget constrains counterfactual one/two-action evaluations only. Stronger controls still attain the complete sampled ceiling. No general greedy-optimality theorem is asserted.

Family-level paired root-mean informative accuracy (ordered minus shuffled) is -0.52356 pp for a, -0.45425 pp for b. Worst within-arm seed variation on a root is 100 pp and 40 pp respectively; neither is an independently calibrated sham distribution. Both retrospective planner runs return REDESIGN_OR_PILOT_ONLY (strict exit 2), with two unverified lineages and no sealed confirmation. The scientific floor is 5 pp. Both tasks fail the deterministic-headroom gate. Do not use a larger learned model on these objectives or claim that discovery history is unhelpful in general.

## Verification and replay

Four targeted tests passed locally (1.44s), including small proof enumeration of the permitted one/two-reveal endpoints, monotone bounds, byte budget, and shuffle/mask and split contracts. The saved prediction audit exactly reproduces all 18 and 21 arm metrics. The initial combined extract+fit sandbox call timed out after completing extraction; training then ran separately from cached verified data. The extraction stages took 22.04 and 22.54 s, fitting/evaluation 11.90 and 12.61 s. No paid GPU. Full repository CI and formal proof of the replay implementation remain outstanding.

From the repository root, first regenerate the pinned archive (compressed hash includes gzip timestamps; its contents are independently checked):
```sh
cd gyms/MIC14/reference
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python mic13.py > results.json
cd ..
MIC13_SOURCE=./reference OMP_NUM_THREADS=1 python -m pytest -q test_mic14.py
for variant in a b; do
  extra=""
  if [ "$variant" = b ]; then extra="--cost"; fi
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python replay_experiment.py --stage extract --archive reference/proofs.jsonl.gz --source-dir reference $extra
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python replay_experiment.py --stage fit $extra
  python replay_experiment.py --stage audit $extra
done
cd ../..
python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC14/preflight_input.json --strict
python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC14/cost_preflight_input.json --strict
```

The original source archive SHA256 is 281200c167336532e0a3120629c61b5fad0b0ebd818b718ea80a001ef12fc6a5. Generated MIC-14a obligations/results SHA256 c305e2615c5b4935d94f744d69886f0becb4c4dd416477a414db02bcce380c50 / cfbb41b2eafce9a082883f145ad22f64c7360d7fca6b706eaaa18e83dd737292; MIC-14b obligations/results 4929cd610c936d51f4bc26d5064ee62544463e409767bdb9aeeb9b05766b251d / cf9c2736f1333f109fdce3af6b5d2d3e9d2a4a95c87b95bdd3c3bfb987d82bac. Raw datasets and predictions stay in generated sandbox artifacts; no corpus release or token allocation.

## Next gate

Before further training, construct longer-horizon and cost-constrained proof-acquisition tasks with multiple genuinely different useful continuation paths. Independently enumerate finite-horizon policies, require a meaningful oracle gap above deterministic cap-priority, cost-priority, and lookahead controls, and group all descendants and variants by root. Evaluate realized multistep utility with exact certificate costs and no oracle continuation. Require independent generator families, sham calibration and sealed confirmation before promotion. The original DLMST discovery-order hypothesis remains untested by this retrospective synthetic proxy.
