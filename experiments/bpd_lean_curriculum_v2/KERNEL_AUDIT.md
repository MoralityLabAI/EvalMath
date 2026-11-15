# BPD-LG-02 independent six-file Lean kernel audit

**Date:** 2026-11-15. **Evidence:** [EvalMath CI run 43705790859](https://github.com/MoralityLabAI/EvalMath/actions/runs/43705790859). Public independent replay of the same generator blobs committed in the private LoopedTransformers branch.

- Exact source: EvalMath branch commit `a3032ba2055bd4847075bf8531fa133daecb18fb`.
- Lean: `Lean (version 4.19.0, x86_64-unknown-linux-gnu, commit 6caaee842e94, Release)`.
- All 7 independent Python source tests passed.
- 384 generated examples: 256 train, 64 dev, 64 test.
- **192 positive theorem scripts** and **192 negative refutation theorems** kernel-checked, six Lean source files.
- **384/384 empty axiom inventories**, each checked individually with `#print axioms`.
- All structural-role digests were unique across cases and no digest/group crossed the train/dev/test boundary under the generator's declared normalization. This does **not** establish general graph-isomorphism or semantic disjointness.
- The negative theorem has the form `¬ (∀ parameters, premises → goal)`, witnessed by an explicit satisfying assignment that falsifies the goal. This gives a Lean kernel-checked negation for the original universal claim, not a proof of irrelevance of a particular model component.

| Split | Positive proofs | Negative refutations | Positive source SHA-256 | Refutation source SHA-256 |
|---|---:|---:|---|---|
| train | 128 | 128 | `cfc85e99132c536d29e3c63751446f746068c8c012f2647c8a8f1c56e5fd21fe` | `ad52ba622b846f9b8da54779c6e51e5b3eb41eda673d7402812569be82430ef8` |
| dev | 32 | 32 | `63d7c17ecdd0319a3a2ef582dd958c39caf84a066de4bcad7d59de58eaf687e8` | `0b148f8b033cb515e625c10ea86bef3c4ccd6961f991fa3dcec51d5f3a85654c` |
| test | 32 | 32 | `05cdfa2c84286c32c91205dc373ffcae757067a794c168c83b5098270dcbd407` | `99bfb562599a200fb8a3a58c72a51a58bfcb6c0255624da3f7c0860d8447807f` |

The first CI attempt caught a missing parenthesis around the final `rcases` conjunct. The second revealed a negative-induction theorem parser defect and an unwanted use of `propext` by `simp` in the refutation witnesses. Both issues were repaired before this independent successful replay. Negative refutations now use constructive proof terms built from `True.intro`, `False.elim`, `And.intro`, and `rfl`.

**Research boundary:** finite Horn/equality reasoning proofs are kernel-certified. The curriculum has never trained a BPD/VPD neural decomposition and cannot distinguish latent mechanisms without measured model interventions. The exact symbolic graph algorithm is an expected 100% baseline. The original BPD-LG-01 training/test split remained defective despite an earlier successful Lean proof audit.
