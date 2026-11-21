#!/usr/bin/env bash
# Convert the official Qwen3-4B-Instruct-2507 bf16 snapshot to a Q8_0 GGUF with the PrismML llama.cpp converter.
set -u
SNAP=/mnt/d/huggingface_cache/hub/models--Qwen--Qwen3-4B-Instruct-2507/snapshots/cdbee75f17c01a7cc42f958dc650907174af0554
LC=/mnt/c/Users/patri/Documents/Codex/llama.cpp-prism
OUT=/mnt/c/Users/patri/models/qwen3-4b-instruct-2507
mkdir -p $OUT
export PYTHONPATH=$LC/gguf-py
nice -n 10 /root/goblin-cuda/bin/python $LC/convert_hf_to_gguf.py $SNAP --outtype q8_0 \
  --outfile $OUT/Qwen3-4B-Instruct-2507-Q8_0.gguf > /root/pe2/logs/convert_qwen.log 2>&1
echo "rc=$?"; tail -3 /root/pe2/logs/convert_qwen.log | cut -c1-200
ls -la $OUT; sha256sum $OUT/Qwen3-4B-Instruct-2507-Q8_0.gguf
cd $SNAP && sha256sum model-*.safetensors config.json tokenizer.json 2>/dev/null
