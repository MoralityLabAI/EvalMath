# ZKL-16 paired certificate cost pilot: receipt scoring contract

Scope: four public diagnostic roots, each with an exact A* reference and weighted-tree-shared proof. No statistical, learned-policy or privacy claim. Pinned DataGoblin source e7394fced457c059f20ef54128dbc80b0cc747a5; Nova circuit candidate 26223c2775affe6d44eaa10e2c56acc2bdf1ae70. The local Python source replay produced 25 versus 28 total steps across four roots. The pinned transport SHA-256 is 2d305d145514b39111e2eb06570f91c4bf3d5a0c8ca66afbb9a1d366ae50fce3.

Receipt scoring: run PYTHONPATH=src python scripts/score_zkl_batch.py ARTIFACT_RESULTS --trusted-receipt-sha256 TRUSTED_DIGEST after obtaining and authenticating the CI evidence and its producing revision. The scorer checks the frozen transport digest, source pin, shape, paired cases, cost arithmetic, proof and VK artifact hashes and successful-verification flags. The trusted receipt digest and actual run provenance are required externally. The scorer does not verify the SNARK or independently establish the exact A* optimum. It rejects incomplete receipts for this strict conformance pilot; a future model evaluation should retain omitted/failed proofs as zero coverage in the frozen root manifest. No scores from synthetic fixture tests may be presented as cryptographic results.

Local synthetic plumbing tests: eight passed, including forged proof/VK bytes, cost and success flag tampering, incomplete receipts and wrong digests. Hosted actual Nova batch measurements have completed; see the verified result below. Cost profile uses measured raw R1CS constraints per fixed shape multiplied by proof rows. This is an explicit accounting objective rather than runtime, actual total folding constraints, or BitVM3 settlement cost. Exact reference efficiency is one by construction.

## Verified batch result

The hosted Nova job [45575163808/139071180804](https://github.com/patrickdugan/zk-rusto-no-bitcoino/actions/runs/45575163808/job/139071180804) completed successfully. The downloaded official artifact (ID 15004546056, ZIP SHA-256 9e23e7b20e91c1519bfeeaf271840e3c3feeaffb6837aad9bb0d6bb9039b3e46) was processed locally by the scorer, including actual proof/VK bytes and all hash checks. The generated score is retained at research/certificate_efficiency/zkl16_score.json. It is an external-artifact-derived result, rather than a self-contained arithmetic verifier receipt. Reproduction requires the official CI artifact and its receipt digest.

| arm | coverage | equal-root efficiency | total raw step constraints |
|---|---:|---:|---:|
| exact A* | 1 | 1 | 272025 |
| weighted tree with sharing | 1 | 25/28 | 304668 |

Fixed shape 10,881 raw constraints per step; 25 versus 28 steps. Actual raw cost savings 32,643 constraints. Aggregate folding times 4.723 versus 5.382 seconds, a diagnostic comparison with one execution per proof; Spartan compression took approximately 34 seconds per arm and both arms produced 11,032-byte proofs. The eight certificates also pass [Lean replay](https://github.com/MoralityLabAI/DataGoblin/actions/runs/45575521759/job/139072378667) with no axioms and explicit rule hypotheses. The exact reference obtains score one by construction. No statistical, privacy, production, neural or arbitrary-Lean theoremhood claim. Full repository CI for this commit remains to be checked.
