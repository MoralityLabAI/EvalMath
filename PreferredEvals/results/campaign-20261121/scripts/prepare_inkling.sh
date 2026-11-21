#!/usr/bin/env bash
# Prepare native Inkling Verify data: text-only HLE (gated cais/hle at the pinned revision) and two small NIAH grids.
set -u
W=/root/pe2
PY=$W/venvs/inkling/bin/python
cd $W/inkling-verify
QWEN3_TOK=/mnt/d/huggingface_cache/hub/models--Qwen--Qwen3-4B-Instruct-2507/snapshots/cdbee75f17c01a7cc42f958dc650907174af0554
QWEN35_TOK=/mnt/c/Users/patri/models/Qwen3.5-4B
$PY -m inkling_verify.benchmarks.hle prepare --data-dir $W/data/hle > $W/logs/prepare_hle.log 2>&1 && echo "hle ok" || { echo "hle FAILED"; tail -4 $W/logs/prepare_hle.log; }
for pair in "qwen3:$QWEN3_TOK" "qwen35:$QWEN35_TOK"; do
  name=${pair%%:*}; tok=${pair#*:}
  $PY -m inkling_verify.benchmarks.niah prepare --data-dir $W/data/niah-$name --tokenizer $tok \
    --context-lengths 4000 16000 --depths 25 75 --samples-per-cell 2 > $W/logs/prepare_niah_$name.log 2>&1 \
    && echo "niah $name ok" || { echo "niah $name FAILED"; tail -4 $W/logs/prepare_niah_$name.log; }
done
ls -la $W/data/*/ 2>/dev/null | head -30
