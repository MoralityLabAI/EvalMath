# CPF-05 resumable inference stages with sequential GPU residency.
# Usage: powershell -File scripts/cpf_stage.ps1 -Model bonsai|inky -Panel dev48|primary240 [-Probe]
# Stops any CPF llama-server, starts the requested model, optionally records a backend fingerprint
# on dev prompts, then collects (resuming from the ledger) for that model only.
param([Parameter(Mandatory)][ValidateSet('bonsai', 'inky')][string]$Model,
      [Parameter(Mandatory)][ValidateSet('dev48', 'primary240')][string]$Panel,
      [switch]$Probe, [string]$Private = "$env:USERPROFILE\cpf-private")
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = "$repo\src;$repo\scripts"
$sha = @{ bonsai = '53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3';
          inky = 'e9f70a167e54794bebce2d456b2118730b74fa7c35e23cb1abd4378f66b17bb2' }
$port = @{ bonsai = 18110; inky = 18111 }

$live = $false
try { $live = ((Invoke-RestMethod "http://127.0.0.1:$($port[$Model])/v1/models" -TimeoutSec 3).data.id).Count -gt 0 } catch {}
if (-not $live) {
    & powershell -NoProfile -File "$PSScriptRoot\cpf_serve.ps1" -Stop
    Start-Sleep 5
    & powershell -NoProfile -File "$PSScriptRoot\cpf_serve.ps1" -Model $Model
    if ($LASTEXITCODE) { throw "server start failed for $Model" }
}
if ($Probe) {
    python "$repo\scripts\cpf_backend_probe.py" --config "$Private\models.json" --model $Model `
        --prompts "$Private\dev48\prompts.jsonl" --n 3 --sha256 $sha[$Model] --out "$Private\probe_$Model.json"
    if ($LASTEXITCODE) { throw "probe failed for $Model" }
}
# Start-Process keeps the collector's stderr out of PowerShell's error stream and logs it for diagnosis.
$log = "$Private\servers\$Model.$Panel.collect"
$c = Start-Process python -NoNewWindow -Wait -PassThru -RedirectStandardOutput "$log.out.log" -RedirectStandardError "$log.err.log" `
    -ArgumentList @("`"$repo\scripts\run_cpf_suite.py`"", 'collect', '--prompts', "`"$Private\$Panel\prompts.jsonl`"",
                    '--config', "`"$Private\models.json`"", '--calls', "`"$Private\$Panel\calls.jsonl`"", '--only-model', $Model)
Get-Content "$log.out.log"
if ($c.ExitCode) { throw "collect failed for $Model on $Panel, see $log.err.log (rerun this command to resume)" }
