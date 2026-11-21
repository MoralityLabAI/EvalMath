#!/usr/bin/env bash
# archive_attempt.sh <name>: stop leftover WSL eval processes and move runs/logs of a failed attempt aside.
for pid in $(pgrep -f "external.py|bin/vf-run|inkling_verify.benchmarks"); do kill $pid 2>/dev/null; done
sleep 2
A=/root/pe2/attempts/$1
mkdir -p $A
for d in /root/pe2/runs/*-bonsai /root/pe2/runs/plan-*-bonsai.json; do [ -e "$d" ] && mv "$d" $A/; done
for f in /root/pe2/logs/native-bonsai.log /root/pe2/logs/gsm8k-bonsai.log /root/pe2/logs/niah-bonsai.log /root/pe2/logs/sqlite-bonsai.log; do [ -e $f ] && mv $f $A/; done
cp /root/pe2/logs/calls.jsonl $A/calls_until_archive.jsonl 2>/dev/null
ls $A
