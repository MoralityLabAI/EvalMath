#!/usr/bin/env bash
# Independent attempt to replay the official OpenAI Lean theorem/comparator.
# The original upstream sources, toolchain, and dependency lock are never edited.
set -Eeuo pipefail
export GIT_TERMINAL_PROMPT=0
export GIT_CONFIG_NOSYSTEM=1

readonly PIN='7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a'
readonly TOOLCHAIN='leanprover/lean4:v4.34.1'
readonly COMPARATOR_PIN='d03acab154d269c06e60e4de7e4cc85deebff94b'
readonly EXPORT_PIN='076e8e57707e813375e8f9da8bf989799ace9680'
readonly LANDRUN_PIN='5ed4a3db3a4ad930d577215c6b9abaa19df7f99f'
readonly PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
readonly RESULT_DIR="${ETH_REPLAY_OUTPUT:-$PROJECT_ROOT/output/upstream_eth_replay}"
readonly WORK_DIR="${RUNNER_TEMP:-/tmp}/openai-eth-pin-${PIN:0:12}"
readonly STATUS_TSV="$RESULT_DIR/stages.tsv"
mkdir -p "$RESULT_DIR" "$WORK_DIR"
: > "$STATUS_TSV"

record() {
  local name="$1" status="$2" detail="$3"
  printf '%s\t%s\t%s\n' "$name" "$status" "$detail" >> "$STATUS_TSV"
  echo "::notice title=ETH replay/$name::$status ($detail)"
}

run_stage() {
  local name="$1" max_sec="$2"; shift 2
  echo "===== ${name} (timeout ${max_sec}s) ====="
  local rc=0
  timeout --signal=TERM --kill-after=20s "${max_sec}s" "$@" > "$RESULT_DIR/$name.log" 2>&1 || rc=$?
  tail -n 14 "$RESULT_DIR/$name.log" || :
  if [[ "$rc" -eq 0 ]]; then
    record "$name" passed 'exit=0'
    return 0
  fi
  record "$name" failed "exit=$rc"
  return "$rc"
}

finalize() {
  local script_exit=$?
  trap - EXIT
  python3 - "$STATUS_TSV" "$RESULT_DIR/summary.json" "$script_exit" "$PIN" "$TOOLCHAIN" "$COMPARATOR_PIN" "$EXPORT_PIN" "$LANDRUN_PIN" <<'PY'
import json, pathlib, sys
stages = []
for line in pathlib.Path(sys.argv[1]).read_text().splitlines():
    name, status, detail = line.split('\t', 2)
    stages.append({'name': name, 'status': status, 'detail': detail})
pathlib.Path(sys.argv[2]).write_text(json.dumps({
    'schema_version': 1,
    'upstream_repo': 'openai/math',
    'upstream_commit': sys.argv[4],
    'lean_toolchain': sys.argv[5],
    'comparator_source_pin': sys.argv[6],
    'lean4export_source_pin': sys.argv[7],
    'landrun_source_pin': sys.argv[8],
    'script_exit_code': int(sys.argv[3]),
    'stages': stages,
    'kernel_verified': all(any(s['name'] == n and s['status'] == 'passed' for s in stages) for n in ('upstream_target_build', 'axioms_check', 'axiom_allowlist')),
    'comparator_verified': any(s['name'] == 'official_comparator' and s['status'] == 'passed' for s in stages),
}, indent=2) + '\n')
PY
  echo '===== RESULT SUMMARY ====='
  cat "$RESULT_DIR/summary.json"
  exit "$script_exit"
}
trap finalize EXIT

{ echo 'Source pin:' "$PIN"; echo 'Host kernel:'; uname -a; echo 'Available space:'; df -h .; echo 'Git:'; git --version; echo 'Go:'; go version || :; } > "$RESULT_DIR/environment.txt" 2>&1

if ! run_stage pinned_checkout 900 bash -c '
  set -euo pipefail
  git clone --quiet --filter=blob:none --no-checkout https://github.com/openai/math.git "$1/upstream"
  git -C "$1/upstream" checkout --quiet --detach "$2"
  test "$(git -C "$1/upstream" rev-parse HEAD)" = "$2"
  test "$(cat "$1/upstream/lean/lean-toolchain")" = "$3"
  git -C "$1/upstream" rev-parse HEAD
  git -C "$1/upstream" status --porcelain
' _ "$WORK_DIR" "$PIN" "$TOOLCHAIN"; then
  echo 'Upstream source checkout unavailable; cannot claim a replay.' >&2
  exit 10
fi

export PATH="$HOME/.elan/bin:$(go env GOPATH 2>/dev/null || echo "$HOME/go")/bin:$PATH"
if ! run_stage elan_install 900 bash -c '
  set -euo pipefail
  curl --retry 3 -sSfL https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -o "$1/elan-init.sh"
  sha256sum "$1/elan-init.sh"
  bash "$1/elan-init.sh" -y --default-toolchain none
  "$HOME/.elan/bin/elan" toolchain install "$2"
  "$HOME/.elan/bin/elan" default "$2"
  "$HOME/.elan/bin/lean" --version
  "$HOME/.elan/bin/lake" --version
' _ "$WORK_DIR" "$TOOLCHAIN"; then
  exit 11
fi

if ! run_stage lake_cache 1800 bash -c '
  set -euo pipefail
  cd "$1/upstream/lean"
  lake exe cache get
  echo "mathlib-ref=$(git -C .lake/packages/mathlib rev-parse HEAD)"
  test "$(git -C .lake/packages/mathlib rev-parse HEAD)" = "d13f23b723b8a846827a245b89c10fc7d3f11612"
' _ "$WORK_DIR"; then
  record official_comparator blocked 'lake cache unavailable'
  record upstream_target_build blocked 'lake cache unavailable'
  record axioms_check blocked 'lake cache unavailable'
  exit 12
fi

# Comparator is run first, before independently compiling the proof.
comparator_tools_ok=1
if ! run_stage landrun_install 900 bash -c '
  set -euo pipefail
  go install "github.com/zouuup/landrun/cmd/landrun@$1"
  landrun_bin="$(go env GOPATH)/bin/landrun"
  test -x "$landrun_bin"
  "$landrun_bin" --version
  "$landrun_bin" --help > "$2/landrun-help.txt"
  sed -n '1,10p' "$2/landrun-help.txt"
' _ "$LANDRUN_PIN" "$WORK_DIR"; then
  comparator_tools_ok=0
fi
if ! run_stage comparator_tool_build 1200 bash -c '
  set -euo pipefail
  git clone --quiet https://github.com/leanprover/lean4export.git "$1/lean4export"
  git -C "$1/lean4export" checkout --quiet --detach "$2"
  cp "$1/upstream/lean/lean-toolchain" "$1/lean4export/lean-toolchain"
  (cd "$1/lean4export" && lake build lean4export)
  git clone --quiet https://github.com/leanprover/comparator.git "$1/comparator"
  git -C "$1/comparator" checkout --quiet --detach "$3"
  cp "$1/upstream/lean/lean-toolchain" "$1/comparator/lean-toolchain"
  (cd "$1/comparator" && lake build comparator)
' _ "$WORK_DIR" "$EXPORT_PIN" "$COMPARATOR_PIN"; then
  comparator_tools_ok=0
fi

if [[ "$comparator_tools_ok" -eq 1 ]]; then
  if ! run_stage official_comparator 5400 bash -c '
    set -euo pipefail
    export COMPARATOR_LANDRUN="$(go env GOPATH)/bin/landrun"
    export COMPARATOR_LEAN4EXPORT="$1/lean4export/.lake/build/bin/lean4export"
    cd "$1/upstream/lean"
    lake env "$1/comparator/.lake/build/bin/comparator" ComparatorChallenges/SubexponentialSAT.json
  ' _ "$WORK_DIR"; then
    echo 'Comparator did not pass; inspect log and classify the failure.'
  fi
else
  record official_comparator blocked 'comparator/landrun tools unavailable'
fi

if ! run_stage upstream_target_build 5400 bash -c '
  set -euo pipefail
  cd "$1/upstream/lean"
  lake build OAI.Algorithms.SubexponentialSAT.Main
' _ "$WORK_DIR"; then
  record axioms_check blocked 'upstream target build unavailable'
  exit 13
fi

cat > "$WORK_DIR/upstream/lean/IndependentEthAxiomAudit.lean" <<'LEAN'
import OAI.Algorithms.SubexponentialSAT.Main
#check @OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat
#print axioms OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat
#print axioms OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_eth
LEAN
if ! run_stage axioms_check 600 bash -c '
  set -euo pipefail
  cd "$1/upstream/lean"
  lake env lean IndependentEthAxiomAudit.lean
' _ "$WORK_DIR"; then
  exit 14
fi

run_stage axiom_allowlist 30 python3 - "$RESULT_DIR/axioms_check.log" <<'PY'
import pathlib, re, sys
log = pathlib.Path(sys.argv[1]).read_text()
names = (
    'OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat',
    'OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_eth',
)
allowed = {'propext', 'Quot.sound', 'Classical.choice'}
for name in names:
    found = re.search(r'(?m)^' + re.escape(name) + r'\s+depends on axioms:\s*\[([^\]]*)\]', log)
    no_axioms = re.search(r'(?m)^' + re.escape(name) + r'\s+does not depend on any axioms', log)
    if not found and not no_axioms:
        raise SystemExit(f'No axiom report for {name}; cannot assert kernel axiom status')
    actual = {s.strip() for s in found.group(1).split(',') if s.strip()} if found else set()
    if not actual.issubset(allowed):
        raise SystemExit(f'{name}: unexpected axioms {sorted(actual - allowed)}')
    print(f'{name}: accepted axioms {sorted(actual)}')
PY

# A passing kernel build cannot conceal a failed or blocked Comparator stage.
# Persist all measured kernel results before exiting with an inconclusive verdict.
if ! awk -F '\t' '$1 == "official_comparator" && $2 == "passed" {ok=1} END {exit !ok}' "$STATUS_TSV"; then
  echo 'Comparator unavailable or failed; inspect its stage log and trust boundary.' >&2
  exit 15
fi
