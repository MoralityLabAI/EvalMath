# SRG-08: Formula-hole synthesis and temporal belief-state reasoning

2026-11-25. Evidence: finite executable SWMD reference controls, exhaustive binary gate checks, and mock stateless memory protocol. No language model inference, neural training, production TypeScript editor build, or Lean claim.

## 1. Authoring synthesis contract

SRG-07 repairs an inverted gate while a related complementary formula remains in the world. SRG-08 gives a source with a single Boolean hole (FALSE) and a lower-priority unconditional fallback. The author must write a complete typed expression from an explicit mathematical specification and six representative labelled inputs. Restrict edits to the named reaction's G field; reject new records, undeclared state, event pseudo-coordinates and malformed expressions. The verifier evaluates both the expression and its selected reaction. Accept functionally equivalent expressions on the finite declared test domain.

For K=4,8,16, use three families:
- signed weighted linear score, with explicit inclusive threshold;
- Euclidean ball gate, sum of squared coordinate residuals about a signed center, with inclusive squared radius;
- signed pairwise-product interactions, sum over disjoint pairs, with inclusive zero threshold.

The reference uses ordinary numerical arrays and independent scalar arithmetic. Source formulas use the typed SRG/2 evaluator. Every coordinate has an influence witness on the binary equal-magnitude domain: there is a pair of inputs differing only in that coordinate whose classification changes. Multilevel probes use dyadic values from {-0.75,-0.5,-0.25,0,0.25,0.5,0.75}; the exhaustive binary test uses ±0.5. Neither test proves universal correctness on the continuous cube. Truth functions are not balanced by construction in this experiment; report the empty-gate baseline and class proportions. Three family splits are public training (linear), public calibration (metric) and reserved evaluation template (interaction). All three were exercised with PUBLIC control seeds. No fresh private evaluation instances were generated. The procedural family definitions themselves are public, so private generation reserves instances, not secret mathematical concepts.

Nine generated worlds, 626/626 numerical probes, 626/626 runtime branch outcomes and 197424/197424 exhaustive binary assignments match the reference. The unfilled gate passes 321/626 multilevel probes, the inverted reference gate zero. All 84 coordinate witnesses pass by reference truth table. Every scope-injection test rejects.

The metric-ball family is a useful bridge to storyworld Hilbert geometry. Rather than reward a superficially diverse operator set, specify the intended acceptability region, choose appropriate coordinates and weights, and measure the decision boundary on matched inputs. These controls use equal unit weights; future variants should change the metric and record the conditioning and margin of the gate. The interaction family tests formulas whose decision can depend on joint input products. An effect or score may move substantially in state space without crossing a consequential boundary; geometry and control influence remain distinct.

## 2. Explicit temporal memory

Let X be a uniformly distributed K-bit vector. The SWMD engine starts with X hidden. Forced read actions copy one hidden coordinate at a time to a public cue register, then a forced archive action clears that register before a final report. The final public query is either the parity task or the one-based index J (uniform and independent of X under the reference prior). For the index task, the final report asks X_J. No hidden coordinates are exported to the player. A complete transcript exposes the earlier cues; the current-only observation does not. The player receives an explicit rule, observation, and legal option IDs. Sampled test masks and cyclic query indices form finite diagnostic probes; the ideal prior is specified separately.

Parity: two memory states suffice, by XOR accumulation. One bit is necessary for deterministic exact reporting when the final observation is otherwise identical. Indexed recall: any deterministic retained state M with fewer than 2^K possible values maps at least two distinct input strings to the same state. Choose an index at which they differ; the final decoder cannot answer both correctly. Thus perfect deterministic accuracy for all strings and indices requires at least K bits. K bits suffice. This is a statement about a causal external memory protocol with a query revealed after encoding; it is not a neural parameter or context-window lower bound. For b prefix bits stored, the explicit policy returns a known bit if queried and a random guess otherwise, giving (K+b)/(2K); this is a feasible accuracy curve, not an optimum for lossy encoders.

| Relevant cue count | Parity exact-memory bits | Indexed-recall exact-memory bits |
|---:|---:|---:|
| 4 | 1 | 4 |
| 8 | 1 | 8 |
| 16 | 1 | 16 |

Under the specified independent prior, both tasks have final-current-only optimum 1/2 and full-history optimum 1. The causal meaning of K therefore depends on task and observation history. 288 executable traces checked the cue sequence, cleared register and correct/wrong report outcomes (576 final branch checks). A mock callback through the actual stream runner reproduces 288/288 reference decisions using one bit for parity and K for index. The mock uses the known task family and reference coding rule; it is not model performance. The stream arm starts a fresh request for each observed cue, passes a bounded integer register and no transcript/future index, then passes the final query with the retained integer. Reject out-of-range memory and record failures. Actual server isolation/caching must be checked when running models.

## 3. Contingent finite-horizon planning

The hidden regime R is equally likely positive or negative. A direct correct commitment pays 8, incorrect pays 0. Settlement pays 5. Survey followed by a correct informed commitment pays 6, incorrect or unfinished pays 0; survey completion takes H=2,3,5 actions. At the opening, survey can reveal R, or the matched missing-cue variant does not reveal it. A visible-root variant reveals R before the opening choice. The utility is explicitly declared, independent of prose and gate scores.

For a history cell B, a multiset of latent states with equal unit prior masses, define W_h(B) as maximal summed payoff under the available action budget. Terminal cells sum their realized payoff, and W_0 counts only terminal rewards. For nonterminal cells,
    W_h(B)=max_a sum_o W_{h-1}({T(s,a):s in B, O(T(s,a))=o}).
Initial expected value is the sum across initial observation cells divided by total prior mass. This recursion follows by conditioning on the first action and observed successor. It uses exact integer mass for these deterministic small fixtures and assumes common legal menus in each cell. There is no privileged full-state continuation in the hidden-root arm.

| Information regime | Budget 1 | Full survey horizon | Optimal full-horizon first action |
|---|---:|---:|---|
| Hidden, survey informative | 5 | 6 | survey |
| Visible at root | 8 | 8 | correct direct commitment |
| Hidden, survey uninformative | 5 | 5 | settlement |

After a revealing survey, the two observation cells choose different correct commitment actions and value 6. Without its cue the single cell's best expected commitment payoff is 3. This paired intervention measures the value of evidence and contingent future action, beyond merely delayed reward. All 54 initial-budget and 27 post-survey oracle controls reproduce. Utility magnitude and horizon are fixed design choices, not inferred from narrative. The fixture is a controlled planning problem rather than a full social storyworld.

## 4. Data custody and next experiment

Public task/gold records are separate. Each split per replicate has 3 author formula tasks, 192 memory questions and 24 planning tasks. Memory and planning templates recur across splits; fresh seeds create different instances but not independent families. Private generation uses a local random nonzero uint32 seed outside the repository, excludes public seeds and retains verifier manifests separately from model input. The seed is not a cryptographic secret. The model runner is loopback-only and reads only model input, records caller-declared checkpoint digest, server label and pass count. Architectural pass count is metadata, not a server configuration mechanism.

The Data Goblin exporter materializes 123 train-only reference supervised examples (3 synthesis, 96 full-history memory, 24 identifiable planning). Current-only memory labels are excluded because the same observation can imply conflicting labels. Calibration, smoke and evaluation are excluded. Keep world siblings together. The committed Git-blob manifest and local SHA256 manifest describe deterministic reference supervision, not measured model-generated repairs. No live model or GPU was available; exact core/scoring and mock callback controls were executed in an isolated JavaScript runtime. Standalone Node filesystem and HTTP execution, production TypeScript integration and full CI remain outstanding.

See integrations/sweepweave-ts/srg08/README.md for commands, verifier and output contracts. SRG-09 should introduce noisy conflicting cues, belief ownership and interaction-based decision margins, then test native compact reasoners on identical frozen inputs. Register memory, planning, inference passes and wall-time budgets separately. No Godot dependency.
