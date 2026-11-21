| category | benchmark | model | condition | attempts | scored | correct | accuracy (Wilson 95%) | roots scored | root-mean accuracy (bootstrap 95%) | outcomes | prompt tok. | completion tok. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| recursive reasoning (sealed) | sealed-multihop-binding | bonsai-27b | thinking budget 1536 | 80 | 80 | 79 | 0.9875 (0.93-1.00) | 80/80 | 0.9875 (0.96-1.00) | correct 79, wrong 1 | 226.5 | 743.8 |
| recursive reasoning (sealed) | sealed-multihop-binding | bonsai-27b | thinking budget 256 | 80 | 80 | 12 | 0.15 (0.09-0.24) | 80/80 | 0.15 (0.07-0.24) | correct 12, wrong 68 | 226.5 | 288.6 |
| recursive reasoning (sealed) | sealed-multihop-binding | bonsai-27b | thinking budget 64 | 80 | 80 | 1 | 0.0125 (0.00-0.07) | 80/80 | 0.0125 (0.00-0.04) | correct 1, wrong 79 | 226.5 | 191.1 |
| recursive reasoning (sealed) | sealed-multihop-binding | bonsai-27b | thinking off (enable_thinking=false) | 80 | 80 | 8 | 0.1 (0.05-0.19) | 80/80 | 0.1 (0.04-0.17) | correct 8, wrong 72 | 190.5 | 15.8 |

| comparison | paired attempts (roots) | candidate correct | baseline correct | root-macro effect | cluster bootstrap interval | test | p | p (Holm) | FSI-01 verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| H1-bonsai-b1536-vs-b0 | 80 (80) | 79 | 8 | 0.887 | [0.795, 0.963] | exact_McNemar_independent_pairs | 8.470329472543003e-22 | 0.0 | confirmed |
| H2-bonsai-b256-vs-b0 | 80 (80) | 12 | 8 | 0.05 | [-0.050, 0.163] | exact_McNemar_independent_pairs | 0.3876953125 | 1.0 | inconclusive |
