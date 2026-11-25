# SRG-AC01: SWMD authoring certificate

[Mathematical report](../../../paper/storyworld_automatic_authoring_certificate.md) · [Executed receipt](../../../output/evaluation_storyworld_reasoning/srg_ac01_authoring_certificate.json).

From EvalMath root with Node 20+:

```sh
node integrations/sweepweave-ts/srg-ac01/cli.mjs verify
node integrations/sweepweave-ts/srg-ac01/cli.mjs audit integrations/sweepweave-ts/srg13/fixtures/reservoir-dogs-evidence-chain-candidate.swmd.md
```

The audit CLI defaults to the Reservoir Dogs first-sirens/secret-truce contract. For other worlds import auditAuthored(source, contract) with seed, roots, budget, delta, page and goal. The browser-safe certificate module imports the existing SRG/2 runtime. Output contains a static inventory, exact reachable-match attempts, structural intervention summaries and first witnesses, root action utility and raw energy. Verifier-only: do not send hidden coordinates, latent states, or receipt data to a model under test.

The core, actual runtime and both world fixtures were executed in isolated ECMAScript. Standalone CLI and production TypeScript editor wiring remain pending. No promotion of authored candidates. No new runtime profile or Godot dependency.
