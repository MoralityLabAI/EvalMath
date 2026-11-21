#!/usr/bin/env bash
# Finer reasoning-budget grid (registration PE2-MULTIHOP-BUDGET-GRID-20261121). Git Bash on Windows.
# Waits until the RTX 5080 has no vramorama lease and under 1.5 GiB in use for 10 minutes in a row,
# then queues a 10 GiB lease for llama-server, runs the four budgets, scores them and stops the server.
set -u
P=/c/Users/patri/Documents/Codex/pe2-work
R=/c/Users/patri/Documents/Codex/EvalMath-pe2/PreferredEvals/gym
SET=$P/sealed/set
O=$P/grid
LOG=$P/logs/grid.log
URL=http://127.0.0.1:18127/v1
mkdir -p $O
say() { echo "$(date +%T) $*" >> $LOG; }

gpu_quiet() {
  vramorama leases 2>/dev/null | grep -q "(no leases)" || return 1
  local used=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1 | tr -d ' \r')
  [ "${used:-99999}" -lt 1536 ]
}

say "GRID BEGIN, waiting for a quiet GPU"
quiet=0
while [ $quiet -lt 20 ]; do
  if gpu_quiet; then quiet=$((quiet + 1)); else quiet=0; fi
  sleep 30
done
say "GPU quiet for 10 minutes"

: > $P/logs/llama-bonsai-grid.log
MSYS_NO_PATHCONV=1 vramorama run --vram 10G --owner pe2-grid-bonsai --guard-power 300 --restart 3 --max-commit 95 \
  -- "C:/Users/patri/tools/llama-prism-b10743/bin/llama-server.exe" \
  -m "C:/Users/patri/models/ternary-bonsai-2-27b/Ternary-Bonsai-2-27B-PTQ1_0.gguf" -ngl 99 -c 16384 -np 2 \
  --alias bonsai-27b-ptq1 --reasoning-format deepseek --reasoning-budget 1536 \
  --host 127.0.0.1 --port 18127 --jinja --no-webui --metrics > $P/logs/llama-bonsai-grid.log 2>&1 &
say "queued bonsai server (10G)"
until grep -q -E "listening|error|failed" $P/logs/llama-bonsai-grid.log; do sleep 10; done
say "server: $(grep -m1 -E 'listening|error|failed' $P/logs/llama-bonsai-grid.log | cut -c1-120)"

for b in 384 512 768 1024; do
  name=bonsai-b$b
  args=(run --tasks $SET/tasks.jsonl --benchmark sealed-multihop-binding --out $O/$name --model bonsai-27b-ptq1
        --base-url $URL --rollouts 1 --temperature 0 --seed 42 --max-tokens 4096 --timeout 1800
        --response-mode answer_only --concurrency 2 --request-extra "{\"thinking_budget_tokens\":$b}")
  [ -f $O/$name/run.json ] && args+=(--resume)
  say "start $name"
  python $R/runner.py "${args[@]}" >> $LOG 2>&1
  say "done $name"
done

powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='llama-server.exe'\" | Where-Object { \$_.CommandLine -like '*Ternary-Bonsai-2-27B*' } | ForEach-Object { \$p = Get-CimInstance Win32_Process -Filter ('ProcessId=' + \$_.ParentProcessId); if (\$p.Name -eq 'vramorama.exe') { Stop-Process -Id \$p.ProcessId -Force -ErrorAction SilentlyContinue }; Stop-Process -Id \$_.ProcessId -Force -ErrorAction SilentlyContinue }"
say "stopped server"
# Scoring happens only after all four conditions finish (sealed readout).
for b in 384 512 768 1024; do
  python $R/runner.py score --run-dir $O/bonsai-b$b --labels $SET/labels.jsonl --out $O/bonsai-b$b/scores.json >> $LOG 2>&1
done
say "GRID END"
