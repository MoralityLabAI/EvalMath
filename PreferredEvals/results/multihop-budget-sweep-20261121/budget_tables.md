| model | budget | depth | correct / scored | accuracy (Wilson 95%) | cap-truncated | no answer | completion tokens per hop (median, correct) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bonsai-27b | 0 | 2 | 6 / 20 | 0.3 (0.14-0.52) | 0 | 0 | 1.5 |
| bonsai-27b | 0 | 4 | 1 / 20 | 0.05 (0.01-0.24) | 0 | 0 | 0.8 |
| bonsai-27b | 0 | 8 | 1 / 20 | 0.05 (0.01-0.24) | 0 | 0 | 0.4 |
| bonsai-27b | 0 | 12 | 0 / 20 | 0.0 (0.00-0.16) | 0 | 0 | None |
| bonsai-27b | 64 | 2 | 1 / 20 | 0.05 (0.01-0.24) | 0 | 0 | 34.0 |
| bonsai-27b | 64 | 4 | 0 / 20 | 0.0 (0.00-0.16) | 0 | 0 | None |
| bonsai-27b | 64 | 8 | 0 / 20 | 0.0 (0.00-0.16) | 0 | 0 | None |
| bonsai-27b | 64 | 12 | 0 / 20 | 0.0 (0.00-0.16) | 0 | 0 | None |
| bonsai-27b | 256 | 2 | 10 / 20 | 0.5 (0.30-0.70) | 0 | 0 | 130.0 |
| bonsai-27b | 256 | 4 | 1 / 20 | 0.05 (0.01-0.24) | 0 | 0 | 65.0 |
| bonsai-27b | 256 | 8 | 1 / 20 | 0.05 (0.01-0.24) | 0 | 0 | 32.5 |
| bonsai-27b | 256 | 12 | 0 / 20 | 0.0 (0.00-0.16) | 0 | 0 | None |
| bonsai-27b | 1536 | 2 | 20 / 20 | 1.0 (0.84-1.00) | 0 | 0 | 246.0 |
| bonsai-27b | 1536 | 4 | 20 / 20 | 1.0 (0.84-1.00) | 0 | 0 | 142.0 |
| bonsai-27b | 1536 | 8 | 20 / 20 | 1.0 (0.84-1.00) | 0 | 0 | 93.6 |
| bonsai-27b | 1536 | 12 | 19 / 20 | 0.95 (0.76-0.99) | 0 | 0 | 89.3 |

| model | depth | smallest budget with accuracy >= 0.8 |
| --- | --- | --- |
| bonsai-27b | 2 | 1536 |
| bonsai-27b | 4 | 1536 |
| bonsai-27b | 8 | 1536 |
| bonsai-27b | 12 | 1536 |
| qwen3-4b | 2 | none tested |
| qwen3-4b | 4 | none tested |
| qwen3-4b | 8 | none tested |
| qwen3-4b | 12 | none tested |
