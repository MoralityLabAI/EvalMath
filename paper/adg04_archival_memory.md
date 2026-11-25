# ADG-04: Revision-aware working memory for archival agents

**Evidence:** trained-controller synthetic development, with post-hoc equal-epoch extensions. No real archival validation, language-model inference, or sealed confirmation.

The public environment emits an initial key, timestamped signed/unsigned notices, four reference slots, authentication results and one globally available retry. A signed strictly newer notice changes the key; stale and unsigned claims do not. The explicit reducer consumes public observations only. The generator excludes equal-version conflicting signatures. The symbolic resolver is a structural ceiling under this contract.

All four arms share 2,048 training worlds, depths 1–4, 10,146 supervised decisions, three seeds (17,29,43), 576 development roots at depths 1,2,4,6,8,12, and depth+3 acquisition budget. 187 development roots have actual changes. The raw arms get zeroed typed-memory features. Flat models have 19,543 parameters; two-update GRUs have 19,495. Equal epochs, unequal FLOPs. Seed ranges are disjoint but generator-family independence has not been established.

## Results

| Arm | Route completion at 16 epochs | At 64 epochs | Actual revision roots at 64 | Depth 12 at 64 | Certified at 64 |
|---|---:|---:|---:|---:|---:|
| Symbolic | 100% | 100% | 100% | 100% | 27.26% |
| Flat raw | 20.31% | 38.25% | 9.27% | 1.39% | 10.24% |
| GRU raw | 15.97% | 43.35% | 9.09% | 3.13% | 11.75% |
| Flat + memory | 45.31% | 98.03% | 95.90% | 94.44% | 26.68% |
| GRU + memory | 27.60% | 95.78% | 90.02% | 87.50% | 26.16% |

The 64-epoch extension retrained all four arms from scratch on the same data and reused the exposed development panel. Raw GRU beats raw flat on all three seeds; flat-memory beats GRU-memory on all three. Explicit memory produces a much larger gain than the raw recurrent advantage. The lower initial scores substantially reflected undertraining. Forced retry at the middle hop at 64 epochs: flat-memory 96.30%, GRU-memory 94.56%. Joint slot and notice order reversal: 97.57%, 96.47%. False assertion rates 1.91%, 1.85%, symbolic 1.91%; failures can suppress opportunities for incorrect assertions.

## Interventions

At the final routing observation after a teacher prefix, replace only the current typed memory key with an alternate one-hot key matching a distractor slot. Compare a second alternative key of equal perturbation norm. At 64 epochs, flat-memory selects the donor target 95.43% versus 1.33% with the alternate key. GRU-memory: 90.22% versus 1.62%. Removing the final memory vector drops final-step correctness to 29.11% and 55.67% (clean 99.25% and 98.73%). This establishes input dependence under the synthetic contract, not neuron-level decomposition.

Frozen ADG-03 two-update checkpoints: depth-specific ridge probes fit 768 fresh training prefixes and score 192 fresh test prefixes per depth. Key recovery before the final observation at depths 2,4,6,8,12: 100%, 96.18%, 91.67%, 86.81%, 76.91%. Designed matched-prefix hidden-state transplants hold slot lists and final observation fixed while changing initial key. Donor target rates: 94.62%, 89.93%, 82.47%, 80.56%, 71.70%. Alternate donor same-target rates: 1.39%, 3.82%, 6.08%, 7.81%, 9.03%. Matched-prefix states are not norm-matched and the designed panel is not representative of random histories. Ridge readout is observational; the transplant is a targeted intervention under the controlled contract.

## Preflight and next gate

16-epoch primary contrast GRU-memory minus flat-memory completion: -17.71 points; structural order reversal 95/95 sham upper tolerance bound 2/3. Scientific minimum 5 points, target 15 points, six planned comparisons, 240 proposed confirmation roots. REDESIGN_OR_PILOT_ONLY; negative contrast, target below variation floor, no seal and independence unverified. The post-hoc tail is exploratory.

Use exact pointer selection score(slot_i) = inner_product(onehot(key),onehot(slot_i)) where identity is established. For independent hops with success p and one retry success q, route completion over d hops is p^d + d(1-p)p^(d-1)q; this is a toy reliability law, not a fit to observed correlated failures. Spend learned computation on uncertain evidence, conflicting provenance, source dependencies, and search value. Extend the generator to fallible signatures, equal-version disputes, source revocation and branching retrieval. Compare exact and learned reducers, tied and flat planners with equal memory interface and measured compute. Freeze independent source families before confirmation.

## Artifact audit

19 focused tests passed; eight checks in the 16-epoch receipt passed. CPU only; no paid compute. The ADG04_archival_memory.zip session artifact contains all executable sources, the four raw receipts, per-root intervention results, 24 newly trained weights and three frozen reference weights. The local preflight source is from the ADG-03 bundle; upstream mismatch remains unresolved. Full repository CI and global receipt integration not run. This commit is the research note; the executables and weights remain in the session bundle.

Reproduction commands (PYTHONPATH=src):
- python -m pytest -q tests/test_archival_memory.py tests/test_archival_controller.py tests/test_archival_gym.py tests/test_abductive_discovery.py
- python scripts/verify_archival_memory.py
- python scripts/probe_adg03_reference.py
- python scripts/adg04_training_tail.py
- python scripts/adg04_raw_tail.py

Receipt SHA-256:
- ADG-04: 9aec2bf6bcfad9a42e86a04ea14831c0acce920a59e928d59ca6e26af4adb127
- Memory tail: 5f9deb4cb1e2cae7d0abe1ff1ee045e6e38b903ad1544b5ce4766b6e1c0d290c
- Raw tail: 69fa81acbf828be98b3b1ce052fa939a51df1c14864b2a68bfa198e2c210dd54
- Reference probe: f782ae4a19b48380d75784b5309f8ea9a485a7574750b2619c1a4110fddee4ae
