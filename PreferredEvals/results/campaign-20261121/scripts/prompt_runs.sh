#!/usr/bin/env bash
# prompt_runs.sh <model> <tag> <base-url> [no-think-extra-json]: gym runner sets for one model, then scoring.
set -u
R=/c/Users/patri/Documents/Codex/EvalMath-pe2/PreferredEvals/gym
S=$R/sets
O=/c/Users/patri/Documents/Codex/pe2-work/runs
model=$1; tag=$2; url=$3; nothink=${4:-}
mkdir -p $O
log=/c/Users/patri/Documents/Codex/pe2-work/logs/prompt-$tag.log
run() {  # run <set> <name> <orders> [extra json]
  local set=$1 name=$2 orders=$3 extra=${4:-}
  local bench=$(grep -o '"benchmark_id": "[^"]*"' $S/$set/provenance.json | cut -d'"' -f4)
  local args=(run --tasks $S/$set/tasks.jsonl --benchmark $bench --out $O/$name-$tag --model $model --base-url $url
              --rollouts 1 --orders $orders --temperature 0 --seed 42 --max-tokens 4096 --timeout 900)
  [ -n "$extra" ] && args+=(--request-extra "$extra")
  [ -f $O/$name-$tag/run.json ] && args+=(--resume)
  echo "$(date +%T) start $name" >> $log
  python $R/runner.py "${args[@]}" >> $log 2>&1
  python $R/runner.py score --run-dir $O/$name-$tag --labels $S/$set/labels.jsonl --out $O/$name-$tag/scores.json >> $log 2>&1
  echo "$(date +%T) end $name rc=$?" >> $log
}
run iclr2026-pairs taste both
run mmlu-pro-science mmlupro normal
run multihop multihop normal
if [ -n "$nothink" ]; then run multihop multihop-nocot normal "$nothink"; fi
echo "$(date +%T) all done" >> $log
