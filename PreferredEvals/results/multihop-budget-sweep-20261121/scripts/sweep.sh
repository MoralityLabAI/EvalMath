#!/usr/bin/env bash
# Multi-hop reasoning-budget sweep (registration PE2-MULTIHOP-BUDGET-20261121). Git Bash on Windows.
# For each model: queue a vramorama lease for llama-server, run four budget conditions, score, stop the server.
set -u
P=/c/Users/patri/Documents/Codex/pe2-work
R=/c/Users/patri/Documents/Codex/EvalMath-pe2/PreferredEvals/gym
SET=$P/sealed/set
O=$P/sweep
LOG=$P/logs/sweep.log
URL=http://127.0.0.1:18127/v1
mkdir -p $O
say() { echo "$(date +%T) $*" >> $LOG; }

start_server() {  # start_server <name> <vram> <server args...>
  local name=$1 vram=$2; shift 2
  local alias=$(printf '%s\n' "$@" | grep -A1 -x -- '--alias' | tail -1)
  if curl -s --max-time 5 $URL/models | grep -q "\"$alias\""; then say "server $name already serving $alias"; return; fi
  : > $P/logs/llama-$name-sweep.log
  MSYS_NO_PATHCONV=1 vramorama run --vram $vram --owner pe2-sweep-$name --guard-power 300 --restart 3 --max-commit 95 \
    -- "C:/Users/patri/tools/llama-prism-b10743/bin/llama-server.exe" "$@" --host 127.0.0.1 --port 18127 \
    --jinja --no-webui --metrics > $P/logs/llama-$name-sweep.log 2>&1 &
  say "queued $name server ($vram)"
  until grep -q -E "listening|error|failed" $P/logs/llama-$name-sweep.log; do sleep 10; done
  say "server $name: $(grep -m1 -E 'listening|error|failed' $P/logs/llama-$name-sweep.log | cut -c1-120)"
}

stop_server() {  # stop_server <model-file-substring>
  powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='llama-server.exe'\" | Where-Object { \$_.CommandLine -like '*$1*' } | ForEach-Object { \$p = Get-CimInstance Win32_Process -Filter ('ProcessId=' + \$_.ParentProcessId); if (\$p.Name -eq 'vramorama.exe') { Stop-Process -Id \$p.ProcessId -Force -ErrorAction SilentlyContinue }; Stop-Process -Id \$_.ProcessId -Force -ErrorAction SilentlyContinue }"
  sleep 5
  say "stopped $1"
}

run_cond() {  # run_cond <name> <model> <max_tokens> <mode> [extra-json]
  local name=$1 model=$2 maxtok=$3 mode=$4 extra=${5:-}
  local args=(run --tasks $SET/tasks.jsonl --benchmark sealed-multihop-binding --out $O/$name --model $model
              --base-url $URL --rollouts 1 --temperature 0 --seed 42 --max-tokens $maxtok --timeout 1800
              --response-mode $mode --concurrency 2)
  [ -n "$extra" ] && args+=(--request-extra "$extra")
  [ -f $O/$name/run.json ] && args+=(--resume)
  say "start $name"
  python $R/runner.py "${args[@]}" >> $LOG 2>&1
  python $R/runner.py score --run-dir $O/$name --labels $SET/labels.jsonl --out $O/$name/scores.json >> $LOG 2>&1
  say "end $name $(python -c "import json;d=json.load(open('$(cygpath -w $O/$name/scores.json)'));print(d['n_correct'],'/',d['n_scored'],d['statuses'])" 2>/dev/null)"
}

say "SWEEP BEGIN"
start_server bonsai 10G -m "C:/Users/patri/models/ternary-bonsai-2-27b/Ternary-Bonsai-2-27B-PTQ1_0.gguf" -ngl 99 \
  -c 16384 -np 2 --alias bonsai-27b-ptq1 --reasoning-format deepseek --reasoning-budget 1536
# Amendment 1: the server ignores thinking_budget_tokens=0, so budget 0 is enable_thinking=false.
run_cond bonsai-b0 bonsai-27b-ptq1 4096 answer_only '{"chat_template_kwargs":{"enable_thinking":false}}'
for b in 64 256 1536; do
  run_cond bonsai-b$b bonsai-27b-ptq1 4096 answer_only "{\"thinking_budget_tokens\":$b}"
done
stop_server Ternary-Bonsai-2-27B
start_server qwen 10G -m "C:/Users/patri/models/qwen3-4b-instruct-2507/Qwen3-4B-Instruct-2507-Q8_0.gguf" -ngl 99 \
  -c 24576 -np 2 --alias qwen3-4b-instruct-2507-q8
run_cond qwen-b0 qwen3-4b-instruct-2507-q8 4096 answer_only
run_cond qwen-b64 qwen3-4b-instruct-2507-q8 128 cot_final_line
run_cond qwen-b256 qwen3-4b-instruct-2507-q8 320 cot_final_line
run_cond qwen-b1536 qwen3-4b-instruct-2507-q8 1600 cot_final_line
stop_server Qwen3-4B-Instruct-2507
say "SWEEP END"
