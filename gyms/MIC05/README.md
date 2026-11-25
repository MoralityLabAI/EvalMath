# MIC-05: maximal atomic decrement closure and learned proposals

Public CPU development follow-up to [MIC-04 draft #87](https://github.com/MoralityLabAI/EvalMath/pull/87). Original finite integer recurrence proxies. No manuscript bytes used. All public roots remain development-only.

## Exact block theorem

Assume M is a nonnegative integer matrix with row sums <=9, b is a positive integer vector, and p is a feasible nonnegative integer certificate satisfying 10p >= 10b+Mp. Let s=10p-10b-Mp. For positive integer t, p-t*1_S is feasible iff for all i in S, p_i>=t and s_i>=t(10-sum_{j in S} M_ij). For i outside S the slack can only increase. Thus feasibility of a block is preserved under unions: each retained coordinate gains support as the block expands.

Initialize S to all coordinates with p_i>=t (or restrict to a proposed set). Remove coordinates failing the threshold; repeat until stable. Every feasible subset of the initial set survives every deletion, by induction, and the final set is itself feasible. It is therefore the unique inclusion-largest feasible block. With precomputed sparse adjacency lists and slack, a queue with incremental support and reverse edges does O(n+m) work in the arithmetic-operation model: each coordinate removed once, each arc processed a constant number of times. The reference Python implementation accepts dense matrices, scans them and sorts active sets, so its actual preprocessing/runtime bound is not the sparse implementation bound.

For t=1, empty closure iff p is the componentwise least feasible certificate. Existence of the least point follows by iterating H_i(p)=b_i+ceil((Mp)_i/10) from zero, bounded above by any feasible integer p. To prove the nontrivial implication, let q be least, d=p-q>=0, D=max d>0, S={i:d_i=D}. For i in S, 10D <= s_i+sum_j M_ij d_j <= s_i+(D-1)sum_j M_ij+sum_{j in S}M_ij. Hence s_i+sum_{j in S}M_ij >= 10+(D-1)(10-sum_j M_ij)>=10, and p_i>=1. S is a nonempty feasible unit block. Contradiction if the maximal closure is empty. Repeated nonempty closures with verified positive jumps terminate because sum(p) strictly decreases among nonnegative integers. This is a completeness result for this finite certificate system, not a polynomial-time bound on the number of jumps or a general proof-search claim.

For fixed block S, its largest uniform decrement is min_{i in S}{p_i, floor(s_i/(10-sum_{j in S}M_ij))}. For each t, maximal t-closure maximizes cardinality and therefore objective decrease t*|S|. Search all t from 1 to max_i min(p_i,floor(s_i/(10-row_sum_i))) (stop at first empty block since feasible sets are nested as t increases). This exactly optimizes one uniform jump. At an integer fixed point, slack lies in [0,9], so at most nine thresholds are necessary. General feasible inputs can require a larger bound; bit complexity and full-solve complexity are unclaimed.

Largest unit block plus its maximum jump need not be globally best. Counterexample: M=diag(9,5), b=(1,1), p=(19,3), a fixed point. The largest unit block is both coordinates, jump 1, improvement 2. Coordinate 0 alone permits a jump of 9. Threshold closure finds this exact better jump.

## Public CPU study

Train six 1,761-parameter rankers (three seeds 17,29,43 per arm, 120 Adam full-batch steps). The two arms share parameters and recurrence depth; graph arm aggregates dependency-weighted hidden states, node-only arm passes each node's own state. Both see six local features, including total support and slack. No oracle labels at evaluation. Binary cross entropy is imbalanced: only 32/192 training roots have a nonempty unit block. Model threshold is logit >=0. Raw proposed blocks are checked, pruned to their maximal feasible subset, then committed only if valid. The graph message arm measures a graph-information intervention, not persistent reasoning memory.

Train ring and mixed two-component roots, seeds 0..95, n=6. Develop on ring, mixed, chorded and critical families, n=6 and n=8, seeds 1000..1015 (128 rows). Initial state is the upper fixed point. Four generator lineages; size pairs and three seed fits are repeated measures; no independent holdout sealed. Local PyTorch 2.10.0+cpu, one thread, model fits and evaluation 3.12 s.

| Family | Roots | Trapped | Exact first uniform-jump improvement (sum) | Graph verified productive model-root pairs |
|---|---:|---:|---:|---:|
| Ring | 32 | 0 | 0 | 0/0 |
| Mixed | 32 | 4 | 26 | 12/12 |
| Chord | 32 | 6 | 32 | 3/18 |
| Critical | 32 | 27 | 302 | 81/81 |
| Total | 128 | 37 | 360 | 96/111 |

Node-only abstains on all roots, 273/384 exact raw masks (empty-block cases), no useful reductions. Graph raw exact masks 294/384; 85 invalid raw proposals; pruned output exact block 369/384, 96/111 productive trap repairs, total reduction 1008 vs exact 3*360=1080. All committed proposals feasible by exact integer verification. Graph repairs yield the same objective across seeds after pruning, producing zero observed objective sham variation on these four lineages. Normalized mean improvement over node-only, divided by initial objective, 0.883836 pp, below inherited 5 pp floor. Chorded transfer is weak. No neural advantage over exact structural closure.

Exact closure plus largest jump matched the brute-force best uniform jump on all 128 sampled roots (not universal, see counterexample). Repeated maximal closures reached least certificate on 128/128, 0.421875 nonempty commits/root; SCC repair also 128/128. Average closure solve edge counter 45.671875/root including terminal empty check, vs SCC 118.1328125 internal row evaluations and 212.734375 nonzero terms/root, 1.25 atomic SCC commits. Exact one-jump threshold search averages 45.953125 edge-counter units/root. These are different counters: closure index/support/deletion visits omit dense input scanning, slack calculation, full checks and neural computation; SCC nonzero terms omit graph decomposition and global certificate checks. No matched-runtime or speedup claim. The shared initial upper-fixed-point computation is excluded from both. Full-solve complexity is not established.

## Replay

```sh
cd gyms/MIC05
python -m pytest -q test_mic05.py test_audit.py
python run.py > results.json
python audit.py > audit_results.json
cd ../..
python skills/evalmath-mechinterp-power/scripts/preflight.py --pilot gyms/MIC05/preflight_input.json --strict
```

Six tests passed, including exhaustive unit/t-block subset checks, arbitrary feasible starts with self dependencies, SCC and best-jump agreement, and an explicit counterexample. Actual planner blob 0ff062f76f5534d9f18425f986ae3e750397f50c copied into sandbox and executed (strict exit 2). REDESIGN_OR_PILOT_ONLY. Four grouped family effects, unverified independence and no calibrated 95/95 sham quantile despite zero observed seed-level objective sham. Inherited thresholds and one graph-vs-node comparison are retrospective planning inputs. No independent confirmation, no paid compute, no training promotion. Full repository CI remains unrun. Raw run files are generated locally rather than committed.

SHA-256 run.py 1dc3bf81ca7a06eb4434a4b9cb9cfe6107c3549de4290033e63dd5f70b1f5c5a; test_mic05.py 623be024242b08c0d17d73e27cdadaa726e5dccf58544957aef29060abcee39d; audit.py 4c0108ab325566cb20d746d4ec315d3f086b29639a48794c02c76696638f42be; test_audit.py 61f4b36016cefcf698d5e8000b364acfe41b171476c15086b6da3815f1c2e23a. Raw results SHA-256 4afb4c17fa921bfae713410762765427917e30f71812d87a4b6fcc2836b09208 (elapsed time varies); audit 31ab49fa86d53b0bdb55f6ca1eb905d55cd8e111c26938e5572aadb22ab4942f.

## Next gate

Move the structural closure theorem into MathCan/Lean and use it as an exact oracle for more general grouped proof-obligation tasks. To test learned routing, introduce disjunctive or signed dependencies where monotone closure no longer solves block discovery. Preserve independent exact enumeration on small problems, explicit work accounting, root-level splits, nontrivial matched baselines, and a separately sealed confirmation set. The original textual discovery-history experiment remains untested. Do not allocate training tokens to the public DLMST archive.
