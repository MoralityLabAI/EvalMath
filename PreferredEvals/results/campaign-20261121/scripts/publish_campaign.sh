#!/usr/bin/env bash
# publish_campaign.sh <tag>...: copy native run artifacts for each model tag into the EvalMath results tree.
set -u
R=/mnt/c/Users/patri/Documents/Codex/EvalMath-pe2/PreferredEvals/results/campaign-20261121
W=/root/pe2
P=/mnt/c/Users/patri/Documents/Codex/pe2-work
mkdir -p $R/runs $R/receipts
for tag in "$@"; do
  for name in taste mmlupro multihop multihop-nocot; do
    src=$P/runs/$name-$tag
    [ -d $src ] || continue
    rm -rf $R/runs/$name-$tag; mkdir -p $R/runs/$name-$tag
    cp $src/run.json $src/rollouts.jsonl $src/scores.json $R/runs/$name-$tag/ 2>/dev/null
  done
  for name in gsm8k sqlite; do
    src=$W/runs/$name-$tag
    [ -d $src ] || continue
    rm -rf $R/runs/$name-$tag; mkdir -p $R/runs/$name-$tag
    d=$(dirname $(ls $src/*/traces.jsonl | head -1))
    cp $d/traces.jsonl $R/runs/$name-$tag/
    cp $d/configs/resolved/*.json $R/runs/$name-$tag/ 2>/dev/null
    cp $W/runs/plan-$name-$tag.json $R/runs/$name-$tag/plan.json 2>/dev/null
  done
  src=$W/runs/niah-$tag
  if [ -d $src ]; then
    rm -rf $R/runs/niah-$tag; mkdir -p $R/runs/niah-$tag
    cp $src/run.json $src/summary.json $R/runs/niah-$tag/ 2>/dev/null
    cp $src/grid.json $R/runs/niah-$tag/ 2>/dev/null
    (cd $src && find samples -name "*.json" -exec cp --parents {} $R/runs/niah-$tag/ \;)
    cp $W/runs/plan-niah-$tag.json $R/runs/niah-$tag/plan.json 2>/dev/null
  fi
  src=$W/runs/swe-$tag
  if [ -d $src ]; then
    rm -rf $R/runs/swe-$tag; mkdir -p $R/runs/swe-$tag
    cp $src/run.json $src/receipts.jsonl $src/predictions.jsonl $src/report.json $src/scores.json $R/runs/swe-$tag/ 2>/dev/null
    L=/root/swebench-runs/logs/run_evaluation/pe2_swe_$tag
    [ -d $L ] && mkdir -p $R/runs/swe-$tag/harness && (cd $L && find . \( -name "report.json" -o -name "test_output.txt" -o -name "patch.diff" \) -exec cp --parents {} $R/runs/swe-$tag/harness/ \;)
  fi
done
cp $W/logs/calls.jsonl $R/receipts/relay_calls.jsonl
cp $W/attempts/bonsai-attempt1/calls_until_archive.jsonl $R/receipts/relay_calls_failed_attempt1.jsonl 2>/dev/null
du -sh $R/runs/* | sort -h | tail -20
