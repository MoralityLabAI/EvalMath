# CFH-08: intermediate-state supervision versus action imitation

**Disposition: FAIL discovery improvement.** Public finite CPU development; no independent conjecture confirmation, neural mechanism claim, training-corpus admission or paid compute.

## Protocol

Use the verified CFH-07 candidate pack (4,299 unique episodes; training_ready=false) for a research pilot only. The original eight generator-shift decks (96000..96007) supply 1,413 distinct pre-observation decision prefixes and 4,365 observed-reply targets. Four structured decks (96100..96103) supply 669 development prefixes and 1,992 reply targets. Deduplicate prefix histories within deck/cap; aggregate the observed reply targets for each prefix. No future replies or terminal claims enter the model features. Graph hash overlap between these train/dev groups is zero. The newly generated evaluation set comprises eight decks of three graphs, order 7–8, from Erdos–Renyi, Prufer trees and random bipartite generators, with conservative four-round WL hash rejection against the training/development cards and previous new cards. These generators have appeared in earlier CFH experiments, so this is fresh graph data within a public grammar, not previously unseen mathematical families. All 220 routes on each deck are replayed under base acquisition caps 39 and 100, with at most four authenticated observation queries.

Models have 2,879 parameters: 24 available-information features per probe, two width-32 tanh layers, scalar action logit and 30 state logits (5 possible replies x 6 survivor-mass targets). Features comprise the counts of known residue cells, unknown mass, current version size, budget/horizon, probe metadata, graph summaries and prior invariant mass. Filter out nonpositive conservative-gain probes. Action-only uses cross entropy on the teacher probe among eligible probes. State arm adds MSE (weight 1) on sigmoid outputs for the observed replies to the teacher probe: total survivor fraction and five invariant survivor fractions, each normalized by prequery version size. Shuffled control permutes target vectors across training prefix/reply records, preserving the target marginal. All arms instantiate the same heads; the auxiliary head receives zero supervised gradient in action-only. Same initialization and minibatch schedule within seed (11,29,47); 240 AdamW updates, batch 48, lr .003, decay .001; no checkpoint selection. Fixed shuffled-label seed offset. No model weights exported.

At replay, all arms use the same deterministic CFH-06 symbolic-terminal acquisition trigger and coverage heuristic, with exact partial prediction masks and retrospective restriction. Only the observation choice changes. The learned action logits choose among admissible probes; the state head is a training auxiliary, not a trusted verifier or an inference-time selector. Teacher uses exact terminal-aware scoring; gain control uses terminal-unaware conservative gain. The teacher statistic is still computed for the acquisition trigger in all arms; no claim of learned planning speedup. Environment truth is isolated to evaluator response and exhaustive branch replay. Independently recomputed route residues agree with the environment on all 135,300 probe/route pairs. CFH-07 verifier checks each finished replay, including abstentions and budget limits.

## Results

Mean hits out of 1,760 per cap, three seeds averaged for each learned arm:

| Policy | Cap 39 | Cap 100 |
|---|---:|---:|
| Teacher | 1016 | 1478 |
| Gain | 936 | 1446 |
| Action only | 808.667 | 1088.333 |
| Action + state | 749.667 | 1050 |
| Action + shuffled | 751.667 | 1050 |

Per-seed hits (11,29,47): cap 39 action 781,807,838; state 698,770,781; shuffled 703,772,780. Cap 100 action 1044,1098,1123; state 974,1079,1097; shuffled 979,1073,1098. State loses to action-only in all six seed/cap comparisons. At cap 39 all policies use exactly 39 base acquisitions on average; at cap 100 teacher/gain/action/state/shuffled use 72.3875/72.3625/73.2172/72.9992/73.0250 on average, respectively. All policies retain the exact verifier and four-query cap.

Development imitation (pooled over three seeds, 2,007 prefix predictions per objective): action 744/2007 (37.07%); state 963/2007 (47.98%); shuffled 956/2007 (47.63%). Development state MSE across seeds: .197661/.018465/.020885 for action/state/shuffled. Action-only state output has no training supervision; its MSE is descriptive, not a trained baseline. Intermediate-state training improves imitation, while actual discovery declines. Shuffled-state matches the state arm closely, so the semantic advantage of true state supervision is not established. These observations cannot isolate the cause of the difference; optimization, target weighting, architecture and imitation objective may matter.

38,720 finished replays verified by the independent evaluator; 8 decks, 220 routes, 2 caps, 11 policy/seed combinations. No inference that routes, seeds or decks are independent conjecture roots. No physically matched causal sham or sealed test. This is an engineering training pilot, not a mechanistic intervention experiment. No causal power claim or independent-root significance testing. All graph-grammar cases remain public development. Reject promotion and GPU spend. A next pilot should rank candidate actions by certified finite-horizon outcome values (including set-valued ties), using explicit acquisition costs and actual on-demand calculations. Preserve exact state checks as environment operations.

## Reproduction

From gyms/CFH08, using the original CFH-07 candidate gzip file:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python pilot.py /path/to/candidates.json.gz --out receipt.json

Python 3.13, Torch CPU 2.10.0, NumPy 2.3.5, NetworkX 3.6.1, SymPy 1.14.0. Local source SHA-256: 7b7e8f2442c88ee1cf430955ee93e7f2b2df705e6763c070be26d20b2d4e4feb. Local receipt SHA-256: 00d62a38ad8205ea6aecadd0870a9926930de936ec000fe09c075d925c402367. Candidate gzip SHA-256: 3aed90651abd9ffdcb85457029a4ef28eae3edcb6d620a60e5897d952cbed47b; decompressed matches CFH-07 hash fb9f7027a2d95014104d3162393b8b1eb478c0d338bf210388f88422f3251c9a. Source blob matches tested local file. No raw generated receipt committed.

Prior CFH-07 EvalMath verify workflow at commit 39a58a25eb49025ee27750e109eaaa085fcd0c20 completed successfully, including Lean Build and Axioms steps (run 45576159590). This verifies the six abstract CFH-07 lemmas in the repository's kernel/audit scope, not the graph identities or Python refinement. New commit CI is separate.
