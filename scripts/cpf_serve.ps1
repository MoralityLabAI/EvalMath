# CPF-05 model servers: one model resident on the RTX 5080 at a time.
# Usage:  powershell -File scripts/cpf_serve.ps1 -Model bonsai|inky [-LogDir <dir>]
#         powershell -File scripts/cpf_serve.ps1 -Stop
# Refuses to start if another process holds GPU memory or a llama-server is already running.
param([ValidateSet('bonsai', 'inky')][string]$Model, [string]$LogDir = "$env:USERPROFILE\cpf-private\servers", [switch]$Stop)
$ErrorActionPreference = 'Stop'

if ($Stop) {
    # Only servers listening on the CPF ports; other jobs' llama-servers are left alone.
    Get-NetTCPConnection -LocalPort 18110, 18111 -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        ForEach-Object { Stop-Process -Id $_; "stopped $_" }
    return
}
if (-not $Model) { throw 'pass -Model bonsai or -Model inky' }
# Expert layers kept on the CPU for Inky; fewer means more VRAM and less host RAM.
if (-not $env:CPF_INKY_CPU_MOE) { $env:CPF_INKY_CPU_MOE = '8' }

$servers = @{
    bonsai = @{
        exe   = 'C:\Users\patri\tools\llama-prism-b10743\bin\llama-server.exe'
        model = 'C:\Users\patri\models\ternary-bonsai-2-27b\Ternary-Bonsai-2-27B-PTQ1_0.gguf'
        sha256 = '53107f530aa52eb00912263ab1ee29bd199261c87cd7b4ad4ca1318c1fe33ee3'
        port  = 18110
        env   = @{}
        args  = @('--alias', 'bonsai-2-27b-ptq1_0', '-ngl', '99', '-c', '4096', '-np', '1', '--jinja',
                  '--reasoning-format', 'deepseek', '--seed', '523', '--no-context-shift')
    }
    inky = @{
        exe   = 'D:\Codex-offload\mcp05-pocket-goblin-bench-20261124\bin-inky-arena\llama-server.exe'
        model = 'C:\Users\patri\Documents\Codex\2026-11-14\3-4-rectified-looped-transformer-https\work\inkling-varloop-local-20261121\q4-pilot\weights\TML-d24-varloop-research-IQ4_NL.gguf'
        sha256 = 'e9f70a167e54794bebce2d456b2118730b74fa7c35e23cb1abd4378f66b17bb2'
        port  = 18111
        env   = @{}
        args  = @('--alias', 'inky-mini-varloop', '--ctx-size', '4096', '--threads', '6', '--threads-batch', '8',
                  '-b', '512', '-ub', '128', '--device', 'Vulkan1', '-ngl', '99', '--n-cpu-moe', $env:CPF_INKY_CPU_MOE,
                  '--fit', 'off', '--parallel', '1', '--no-mmproj', '--no-context-shift',
                  '--cache-ram', '0', '--jinja', '--seed', '523', '--override-kv', 'inkling2_loop.loop.count=int:2',
                  '--no-warmup')
    }
}
$s = $servers[$Model]

if (Get-Process llama-server -ErrorAction SilentlyContinue) { throw 'a llama-server is already running; stop it first (-Stop)' }
$apps = (& nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader) | Where-Object { $_.Trim() }
if ($apps) { throw "GPU admission refused, compute processes present: $apps" }

New-Item -ItemType Directory -Force $LogDir | Out-Null
foreach ($k in $s.env.Keys) { Set-Item "env:$k" $s.env[$k] }
$argv = @('-m', "`"$($s.model)`"", '--host', '127.0.0.1', '--port', $s.port) + $s.args
$watch = [Diagnostics.Stopwatch]::StartNew()
$p = Start-Process -FilePath $s.exe -ArgumentList $argv -WindowStyle Hidden -PassThru `
    -RedirectStandardOutput "$LogDir\$Model.out.log" -RedirectStandardError "$LogDir\$Model.err.log"
while ($watch.Elapsed.TotalSeconds -lt 900 -and -not $p.HasExited) {
    try { if ((Invoke-RestMethod "http://127.0.0.1:$($s.port)/health" -TimeoutSec 3).status -eq 'ok') { break } } catch {}
    Start-Sleep 3
}
if ($p.HasExited) { throw "server exited; see $LogDir\$Model.err.log" }
$mem = & nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits
[pscustomobject]@{ model = $Model; pid = $p.Id; port = $s.port; load_seconds = [math]::Round($watch.Elapsed.TotalSeconds, 1);
    gpu_memory_used_mib = [int]$mem; checkpoint_sha256 = $s.sha256; args = ($argv -join ' ') } | ConvertTo-Json |
    Set-Content "$LogDir\$Model.start.json"
Get-Content "$LogDir\$Model.start.json"
