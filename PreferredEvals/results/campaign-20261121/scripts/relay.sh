#!/usr/bin/env bash
# WSL -> Windows llama-server relay (HybridTRMLDT MCP/hubrun/proxy.py, raw arm only) on 127.0.0.1:18130.
for pid in $(pgrep -f "MCP.hubrun.proxy"); do kill $pid 2>/dev/null; done
sleep 1
mkdir -p /root/pe2/logs
cd /mnt/c/Users/patri/Documents/Codex/HybridTRMLDT-mcp02
exec python3 -u -m MCP.hubrun.proxy --port 18130 --upstream http://127.0.0.1:18127 \
  --via-curl /mnt/c/Windows/System32/curl.exe --log /root/pe2/logs/calls.jsonl \
  --max-tokens-cap 4096 >> /root/pe2/logs/relay.log 2>&1
