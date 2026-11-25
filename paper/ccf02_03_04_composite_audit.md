# CCF-02/03/04: Pinned source crosswalk and certified evaluation scope

2026-11-25. Evidence: source-pinned structural crosswalk; exact finite synthetic checks. No independent upstream kernel rebuild, FlashProve execution, real model run, or estimate of deployed error rates.

## 1. OpenAI local smoothing (CCF-02)

Pinned openai/math at f5702854040e97fa7675c21ba37a9608f5f92dd3. Archive: research/ccf/source_archive/openai. The comparator manifest specifies six fully qualified theorem names and the permitted standard axioms. All six reference/solution signatures agree after whitespace normalization. The reference challenge has six admitted bodies; the solution's bodies invoke the underlying results and contain no literal sorry. This is a syntactic statement check, not elaborated type equality or an axiom audit. The two compilation units have separate import contexts. The challenge's admitted declarations are expected and are not a finding of a flaw in the proof.

| Endpoint | Scope conditions represented in rational fixtures |
|---|---|
| euclidean_local_smoothing | integer dimension at least 2, real finite p at least 2, positive epsilon or p=2 and epsilon=0, Schwartz data, observation interval [1,2] |
| bochner_riesz | extended p at least 1 including infinity, delta strictly above the stated threshold, positive radius, Schwartz data |
| spherical_restriction | extended a>1 including infinity, both strict b thresholds, sphere Lp membership |
| kakeya_maximal | positive epsilon, radius in (0,1], L^n membership |
| kakeya | unit segment in every direction; no additional measurability requirement |
| stein_square | finite p>=2, alpha strictly above max(1/2,n(1/2-1/p)), Schwartz data |

The archive checker tests six signature matches, original Git blob digests and seven statement mutations (dimension, epsilon loss, positive radius, input exponent, scale, positive loss, strict Stein threshold). An out-of-scope fixture is denied certification by this endpoint; it need not be mathematically false. The code does not decide real function membership or compare numeric constants in an actual proof, and does not prove manuscript equivalence. Source archive tests are registered in pytest; only the crosswalk was executed directly through the connector, while the archived Python tests await CI.

## 2. FlashProve (CCF-03)

Pinned anthropics/FlashProve at 9e2bdd8ff5bf9c62f18263d7dac189b0400b260c. Archive: research/ccf/source_archive/flashprove. Anthropic's Nov 2 report describes provable inference for integer-model greedy output. The repository's theorem source is more precise: VerifierAndGoals.AtTheName.sound_of_verify_at takes public files Z, parsed pp, InScope Z=true, readFiles Z=.ok pp, and exact policy, with conclusion Sound for the specified system and error function soundnessErrorInQueries t 1. The theorem documentation describes its random-oracle experiment, query accounting, model/format and file restrictions, and the distinction between the mathematical verifier and the fast C++ executable. Its bound is about q/2^124+2^-101, not a blanket security level or claim of real-hash implementation correctness. Read the archived definitions for exact semantics. We did not independently build the protocol, reproduce its soundness derivation, or verify a real proof.

The executable result contract has materially different verdicts: exact-match versus clipped-gap, next-token versus a checked span. A successful exit alone cannot authorize a whole transcript. The expected ID must come from a trusted source, and request identity, checked coverage, policy and configuration must be compared with independently registered expectations. A build digest printed by the binary is not independent binary attestation. An empty proof or refusal does not certify a correct refusal. The source check verifies four exact theorem-statement anchors and tests their deletion; the documented verdict tokens are also checked. The paper/Lean/executable crosswalk is structural only.

## 3. Combined strict contract (CCF-04)

A proposed policy for a benchmark that requires full exact-match provenance AND kernel-certified mathematical scope. Each of 12 facts is independently attested; the code is a Boolean consumer of such attestations, not a cryptographic parser or verifier. Attestation providers and authenticated joins remain integration work. The contract requires registration, trusted model commitment, request identity, in-scope config, exact match, full token coverage, accepted inference verification, artifact identity, translation fidelity, a kernel-checked solution, theorem scope and frozen authorization contract. A separate formal-security claim additionally needs the random-oracle and setup assumptions of the upstream theorem; the policy does not infer those assumptions from a runtime verdict.

37 rational boundary cases (11 admissible) pass. Exhaust all 4096 Boolean configurations: exactly one passes the strict policy. The two-gate proxy (accepted inference verification and kernel attestation) admits 1024 configurations, 1023 of which are outside the strict contract. These are logical combinations, not sampled frequencies, and equal weighting is not claimed. Deleting any gate from the strict policy admits a one-fault witness; missing or non-Boolean gate inputs fail closed. No claim is made that all configurations are physically realizable.

## 4. Coverage-adjusted score: a sharp finite theorem

Let N>0 be the number of preregistered requests, V be the number with valid full receipts and trustworthy outcome labels, K of the V be correct. Without any assumption about missingness, the registered population accuracy A satisfies K/N <= A <= (K+N-V)/N. Proof: the number of correct unverified cases is an integer between 0 and N-V, and every value is feasible in an unconstrained binary completion. The uncertainty width is exactly (N-V)/N. E.g. N=100,V=90,K=81: published verified-only accuracy is 90%, while registered accuracy belongs to [81%,91%]. A service can choose what to certify, so verified-only accuracy is not in general population accuracy. For five tasks, enumerate all 32 truth vectors times all 32 coverage vectors; the 21 count classes attain every integer in the indicated interval. The theorem assumes a frozen denominator, unique task identity, trustworthy labels on verified items and no other restriction on missing items. A refusal is counted as missing unless the evaluation contract explicitly scores it as failure.

## 5. Formalization status

The existing exact-code iff is now imported in the umbrella module. CertificateRisk.lean adds finite policy bound/attainment, two-scenario mixture convexity given cell maximizers, a pointwise finite union indicator bound and integer missingness bounds. All seven theorem names are registered in axioms_check.lean. The pinned Lean toolchain is not installed in the local execution environment; these are submitted proof scripts pending CI. The sharp circle coupling theorem and finite graph-coloring cardinality theorem remain handwritten proofs, not kernel-verified claims. Do not merge until the full kernel and axiom checks are green.

## 6. Reproduce and acceptance

    PYTHONPATH=src python -m pytest -q tests/test_evaluation_ccf_scope.py
    python scripts/verify_evaluation_ccf_scope.py
    python scripts/check_receipts.py --only ccf01 ccf01b ccf01c ccf04
    PYTHONPATH=src python -m pytest -q tests/test_evaluation_ccf_upstream.py
    cd lean && lake build && lake env lean axioms_check.lean

The targeted CCF-04 tests and receipt ran locally. The source crosswalk was executed from pinned GitHub blobs. Remote CI must rerun everything. For Control-Harness integration, build adapters that derive each gate from verified evidence rather than actor assertions; bind the inference transcript, translated statement and kernel artifact by independent content identities; record every registered task including refusals; publish verified coverage and accuracy interval. Do not use this synthetic suite as evidence of deployed safety. Before a deployment experiment, freeze the registration manifest, expected commitment, exact claim and trust model.
