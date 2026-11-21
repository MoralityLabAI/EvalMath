#!/usr/bin/env bash
# verifiers 0.4.1 venv with the gsm8k and mcp-sqlite tasksets; then dry-run the gym's Prime plan.
set -u
W=/root/pe2
mkdir -p $W/envs $W/logs
for e in gsm8k mcp-sqlite; do rm -rf $W/envs/$e; cp -r /mnt/c/Users/patri/Documents/Codex/pe2-work/envs/$e $W/envs/$e; done
if [ ! -x $W/venvs/vf041/bin/python ]; then uv venv -q $W/venvs/vf041 --python 3.12; fi
VIRTUAL_ENV=$W/venvs/vf041 uv pip install -q "verifiers==0.4.1" -e $W/envs/gsm8k -e $W/envs/mcp-sqlite > $W/logs/vf041_install.log 2>&1 \
  && echo "install ok: $($W/venvs/vf041/bin/python -c 'import verifiers; print(verifiers.__version__)')" \
  || { echo "install FAILED"; tail -5 $W/logs/vf041_install.log; }
ls $W/venvs/vf041/bin | grep -E "^vf-" | tr '\n' ' '; echo
cd /tmp
# The gym's plan, verbatim flag spellings, as a dry run.
$W/venvs/vf041/bin/vf-run --env.taskset.id gsm8k -m dummy-model -n 6 -r 2 --env.agent.runtime.type subprocess \
  --client.base_url http://127.0.0.1:18130/raw/dry/v1 --client.api_key_var PREFERRED_EVALS_API_KEY \
  --output_dir /tmp/vf041-dry --dry-run > $W/logs/vf041_dry.log 2>&1
echo "dry-run rc=$?"; tail -15 $W/logs/vf041_dry.log | cut -c1-200
