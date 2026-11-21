#!/usr/bin/env bash
# native_runs.sh <model> <tag> <niah-data-dir>: GSM8K (Prime gsm8k), NIAH (Inkling) and mcp-sqlite (Prime)
# through the PreferredEvals gym's external.py, against the relay at 127.0.0.1:18130.
set -u
W=/root/pe2
G=/mnt/c/Users/patri/Documents/Codex/EvalMath-pe2/PreferredEvals/gym
export PREFERRED_EVALS_API_KEY=local
model=$1; tag=$2; niah=$3
mkdir -p $W/runs $W/logs
U=http://127.0.0.1:18130/raw
VF=$W/venvs/vf041/bin
step() { echo "$(date +%T) $*" >> $W/logs/native-$tag.log; }

if [ ! -f $W/runs/gsm8k-$tag/DONE ]; then
  step start gsm8k
  PATH=$VF:$PATH $VF/python $G/external.py --profile prime-v041 --taskset gsm8k --harness null --model $model \
    --base-url $U/gsm8k-$tag/v1 --out $W/runs/gsm8k-$tag --limit 6 --rollouts 2 --max-tokens 4096 \
    --temperature 0.6 --concurrency 2 --workdir $W/runs --write-plan $W/runs/plan-gsm8k-$tag.json --execute \
    > $W/logs/gsm8k-$tag.log 2>&1 && date +%FT%T > $W/runs/gsm8k-$tag/DONE
  step end gsm8k rc=$?
fi
if [ ! -f $W/runs/niah-$tag/DONE ]; then
  step start niah
  $W/venvs/inkling/bin/python $G/external.py --profile inkling-niah --model $model --base-url $U/niah-$tag/v1 \
    --out $W/runs/niah-$tag --limit 8 --rollouts 1 --data-dir $niah --max-tokens 4096 --temperature 0 \
    --concurrency 2 --workdir $W/inkling-verify --write-plan $W/runs/plan-niah-$tag.json --execute \
    > $W/logs/niah-$tag.log 2>&1 && date +%FT%T > $W/runs/niah-$tag/DONE
  step end niah rc=$?
fi
if [ ! -f $W/runs/sqlite-$tag/DONE ]; then
  step start sqlite
  PATH=$VF:$PATH $VF/python $G/external.py --profile prime-v041 --taskset mcp-sqlite --harness taskset \
    --model $model --base-url $U/sqlite-$tag/v1 --out $W/runs/sqlite-$tag --limit 8 --rollouts 1 \
    --max-tokens 4096 --temperature 0.6 --concurrency 2 --workdir $W/runs \
    --write-plan $W/runs/plan-sqlite-$tag.json --native-arg=--env.taskset.task.judges --native-arg='[]' \
    --native-arg=--env.agent.max-turns --native-arg=20 --execute \
    > $W/logs/sqlite-$tag.log 2>&1 && date +%FT%T > $W/runs/sqlite-$tag/DONE
  step end sqlite rc=$?
fi
step all done
