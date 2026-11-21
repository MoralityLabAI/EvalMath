#!/usr/bin/env bash
# Inkling Verify venv in WSL at the pinned clone, then prepare HLE and small NIAH grids.
set -u
W=/root/pe2
mkdir -p $W/venvs $W/data $W/logs
rm -rf $W/inkling-verify
cp -r /mnt/c/Users/patri/Documents/Codex/pe2-work/inkling-verify $W/inkling-verify
cd $W/inkling-verify
git rev-parse HEAD > $W/logs/inkling_commit.txt
if [ ! -x $W/venvs/inkling/bin/python ]; then uv venv -q $W/venvs/inkling --python 3.12; fi
VIRTUAL_ENV=$W/venvs/inkling uv pip install -q -r requirements.txt -e . > $W/logs/inkling_install.log 2>&1 && echo "install ok" || { echo "install FAILED"; tail -5 $W/logs/inkling_install.log; }
test -f /root/.cache/huggingface/token && echo "hf token file present" || echo "no hf token file in WSL"
