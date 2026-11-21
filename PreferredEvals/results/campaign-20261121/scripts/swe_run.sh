#!/usr/bin/env bash
# swe_run.sh <model> <tag>: SWE-bench Lite oracle single-shot generation via the relay, official harness, score.
set -u
W=/root/pe2
G=/mnt/c/Users/patri/Documents/Codex/EvalMath-pe2/PreferredEvals/gym
SEL=/mnt/c/Users/patri/Documents/Codex/pe2-work/data/swe_selection.json
model=$1; tag=$2
RUN=$W/runs/swe-$tag
PY=/root/swebench-venv/bin/python
[ -f $RUN/DONE ] && exit 0
mkdir -p $RUN /root/swebench-runs
$PY $G/swebench_oracle.py generate --selection $SEL --model $model --base-url http://127.0.0.1:18130/raw/swe-$tag/v1 \
  --out $RUN --max-tokens 4096 --temperature 0 > $W/logs/swe-$tag.log 2>&1 || { echo "generate failed"; exit 1; }
IDS=$(python3 -c "import json;print(' '.join(json.load(open('$SEL'))['instance_ids']))")
cd /root/swebench-runs
$PY -m swebench.harness.run_evaluation --dataset_name SWE-bench/SWE-bench_Lite --split test \
  --predictions_path $RUN/predictions.jsonl --instance_ids $IDS --max_workers 3 --run_id pe2_swe_$tag --timeout 1800 \
  > $W/logs/swe-harness-$tag.log 2>&1
rep=$(ls /root/swebench-runs/*.pe2_swe_$tag.json 2>/dev/null | head -1)
[ -n "$rep" ] && cp "$rep" $RUN/report.json && $PY $G/swebench_oracle.py score --run $RUN --report $RUN/report.json >> $W/logs/swe-$tag.log 2>&1 \
  && date +%FT%T > $RUN/DONE
tail -12 $W/logs/swe-$tag.log
