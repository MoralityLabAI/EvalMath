# RHT-26 dossier

The [finite carryover model](carryover.md) tracks a retained artifact together
with a policy state. Its [historical protocol](protocol.md) records the planned
four-arm intervention, and the [development bridge](development_bridge.md)
examines what the completed eight-root pilot can identify.

| Material | Location |
|---|---|
| Exact four-state module | [evaluation_reward_carryover.py](../../src/spiral_ln/evaluation_reward_carryover.py) |
| Cue-count extension | [evaluation_reward_carryover_count.py](../../src/spiral_ln/evaluation_reward_carryover_count.py) |
| Original draft manifest | [rht26_carryover_protocol.json](../../configs/rht26_carryover_protocol.json) |
| Four-state receipt after this path migration | [rht26_v3.json](../../output/evaluation_reward_carryover/rht26_v3.json) |
| Count-extension receipt | [rht26_count_v1.json](../../output/evaluation_reward_carryover_count/rht26_count_v1.json) |
| Historical v2 receipt | [Pinned original receipt](https://github.com/MoralityLabAI/EvalMath/blob/6ad6ee1741231cc8f1f410008a2361408d1bc4a9/output/evaluation_reward_carryover/rht26_v2.json) |
| Development observations | [Control-Harness report at its recorded commit](https://github.com/MoralityLabAI/Control-Harness/blob/27b210f758dbf45540dbc0e5226cb00e84dc623b/results/rht26_local/development_report.md) |

On 21 November 2026 the papers and protocol moved into this directory. The
four-state source module and tests retain their original bytes. Its v3 receipt
records the new document paths and historical-status labels; all finite
numerical results agree with v2. The count extension receives a separate
receipt so its later mathematical claims can also be regenerated.

The manifest remains the historical draft. Reading the later development
review supplies the current evidence context without rewriting that draft as
a confirmation protocol.
