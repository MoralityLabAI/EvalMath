# ADG-03: Learning a typed archival-chain controller

Evidence: trained-controller synthetic development pilot; no real archival validation, LLM inference, or sealed confirmation.

The environment extends ADG-02 conceptually. It generates an eight-valued route marker shown only at the first observation, a chain of four-choice records, and available, missing, outsider or forged final documents. A wrong reference terminates the route. Two synthetic authentication tests each cost one unit and have sensitivity and specificity 3/4, conditionally independent given the document regime. Certification requires correct attribution and two positive tests. Names are abstracted into the submit-current-document action.

The flat controller encodes observations and uses causal prefix means plus first and latest observation features. The tied GRU controller uses one or two updates per observation; it is TRM-inspired, not a canonical TRM. Parameter count is matched to within eight parameters; FLOPs are not matched.

Training: 4,096 synthetic worlds, 19,226 supervised decisions, depths 1–4, AdamW, 24 epochs, seeds 17,29,43, CPU PyTorch 2.10.0. Development: 576 disjoint generated roots (96 per depth 1,2,4,6,8,12; four balanced regimes), paired across the training seeds. No protected confirmation roots. Teacher imitation during training, closed-loop greedy rollouts at evaluation. These are new typed trajectories, not training on the ADG-02 text transcripts.

| Policy | Parameters | Certified | Route failure | False assertion | Illegal |
|---|---:|---:|---:|---:|---:|
| Scripted teacher | -- | 27.78% | 0% | 1.74% | 0% |
| Flat | 14,319 | 21.01% | 24.48% | 1.39% | 0% |
| Tied 1 | 14,311 | 11.23% | 56.13% | 0.98% | 0% |
| Tied 2 | 14,311 | 18.46% | 29.98% | 1.33% | 0% |
| Tied 2, reverse slots | same | 19.50% | 29.11% | 1.50% | 0% |
| Tied 2, one update at inference | same | 0% | 78.88% | 0% | 45.66% |

Exact overall certification fractions: teacher 5/18, flat 121/576, tied1 97/864, tied2 319/1728, reverse slots 337/1728, inference-only one update 0. Two updates improve certification by 7.23 percentage points (64.43% relative) against one update, in all three training seeds. Flat exceeds tied2 by 2.55 points overall. At depth 12, certification is 15.97% flat, 9.03% tied2 and 1.04% tied1. The teacher is a conservative heuristic, not a global policy optimum. Low false assertion rates can be caused by failed retrieval. The inference-only loop removal is an out-of-distribution intervention and cannot alone establish a causal mechanism.

Preflight: primary contrast tied2 minus flat certification, paired root mean across three seeds. Mean -0.025463, root standard deviation 0.169477, scientific floor 0.05, target 0.15, 95/95 slot-order sensitivity bound 1/3. REDESIGN_OR_PILOT_ONLY; no sealed holdout, independence unverified, target below variation floor, observed effect below floor. The slot reversal is a structural order sensitivity diagnostic, not a physically matched neural sham. No inference about historical research or canonical TRMs. The initial-observation skip is a strong flat baseline and tests the recurrent compression design choice; compute and information-access costs are not matched.

Four ADG-03 tests and ten earlier focused ADG tests passed, and six receipt checks passed. Local full receipt SHA-256: 3f86dd1fadc9d0ca11aece2c610c2cf8ef188c7a8f1ed769d99865729e2f0632. Source SHA-256: module b6da395fb59e4b7a01ed1ed8be128a9d6719db5f0a03f7d70000a88f982313c6; runner b23055d829be4b526d9a874f38f87a07a66046c87bb1d0b353caddf8b5295584; tests 65c0063a20cc9614e62332324d8ba0f622eaa9aad7710b642947fa2bf77fa12d; local preflight e044d7def0b7f0eaa449d162d2e2d7d5800c9d9c55072108c7039688fcb91e2b.

The downloadable ADG03_archival_controller.zip from the research session contains the executed source, tests, exact local preflight implementation, all nine weights, raw per-root receipt and compact summary. This note records the pilot; full receipt and binary weights are local artifacts, not committed by this note. The previously observed local/upstream preflight blob mismatch remains unresolved. No paid compute.

## ADG-04

Test explicit typed working memory for the persistent marker before allocating GPU budget. Use a direct symbolic resolver and a parameter-matched flat controller with the same memory interface. Introduce changing route keys, conflicting references and bounded backtracking. Probe hidden-state marker recoverability by depth and use donor-marker interventions with matched random directions. Keep authentication and routing outcomes separate, match compute, and freeze fresh source-family-disjoint confirmation roots before any confirmatory experiment.
