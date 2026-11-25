"""VAD-11 Lean runner: one fresh `lean` process per file, per toolchain.

Contract
  * every call of `run_lean` is exactly one verifier call (one process); calls are
    counted per toolchain in `CALLS` (thread-safe) and echoed in every result row;
  * wall time via time.perf_counter around Popen..wait; peak RSS via psutil polling
    of the child tree every ~4 ms, combined with the Windows peak working set of the
    last sample (`peak_wset`) when psutil exposes it; reported in MiB (Fraction-exact
    byte count in `peak_rss_bytes`);
  * timeout 120 s per file (the process tree is killed and the row is marked
    timed_out, ok False);
  * parallelism: `run_many` uses at most MAX_WORKERS=4 concurrent lean processes;
  * toolchains: the primary 4.35.0 and the CI pin 4.19.0, located under
    %USERPROFILE%\\.elan\\toolchains; olean modules are version specific, so the
    module cache lives in <cache>/<version>/ and is passed through LEAN_PATH;
  * axiom report: `#print axioms NAME` lines are parsed by `parse_axioms`; a result is
    'none' (does not depend on any axioms), 'standard' (subset of propext,
    Classical.choice, Quot.sound) or 'bad' (anything else, including sorryAx).
Nothing here interprets Lean output beyond exit code and the axiom lines; a file is
`ok` only when the exit code is 0, the output has no `error`, the source passes the
forbidden-token scan, and every requested target has a 'none'/'standard' report.
"""
import concurrent.futures as cf
import os
import re
import subprocess
import threading
import time
from collections import Counter
from pathlib import Path

import psutil

PRIMARY = '4.35.0'
VERSIONS = ('4.35.0', '4.19.0')
TIMEOUT = 120
MAX_WORKERS = 4
ALLOWED_AXIOMS = frozenset({'propext', 'Classical.choice', 'Quot.sound'})
FORBIDDEN = ('sorry', 'admit', 'native_decide', 'axiom', 'unsafe', 'implemented_by',
             'sorryAx', 'ofReduceBool', 'unsafeCast', 'opaque', 'extern', 'partial')
CALLS = Counter()
_LOCK = threading.Lock()


def lean_exe(version):
    home = Path(os.environ.get('USERPROFILE') or Path.home())
    return home / '.elan' / 'toolchains' / f'leanprover--lean4---v{version}' / 'bin' / 'lean.exe'


def strip_comments(text):
    text = re.sub(r'/-.*?-/', ' ', text, flags=re.S)
    return re.sub(r'--[^\n]*', '', text)


def forbidden_tokens(text):
    """Forbidden Lean tokens found in comment-stripped source (whole identifiers only)."""
    idents = set(re.findall(r"[A-Za-z_][A-Za-z0-9_'.!?]*", strip_comments(text)))
    found = set()
    for ident in idents:
        for part in ident.split('.'):
            if part in FORBIDDEN:
                found.add(part)
    return sorted(found)


_AX_NONE = re.compile(r"^'([^']+)' does not depend on any axioms\s*$", re.M)
_AX_SOME = re.compile(r"^'([^']+)' depends on axioms: \[([^\]]*)\]\s*$", re.M)


def parse_axioms(output):
    """{name: ('none', []) | ('standard', [..]) | ('bad', [..])} from lean stdout."""
    out = {}
    for name in _AX_NONE.findall(output):
        out[name] = ('none', [])
    for name, body in _AX_SOME.findall(output):
        axs = sorted(a.strip() for a in body.split(',') if a.strip())
        out[name] = ('standard' if set(axs) <= ALLOWED_AXIOMS else 'bad', axs)
    return out


_PROF = re.compile(r'^\t([A-Za-z \-]+?) ([0-9.]+)(ms|s)\s*$', re.M)


def parse_profile(output):
    """`set_option profiler true` cumulative table -> {phase: milliseconds} (empty if absent).
    work_ms = elaboration + type checking excludes process start-up and import time."""
    if 'cumulative profiling times' not in output:
        return {}
    block = output.split('cumulative profiling times', 1)[1]
    return {k.strip(): float(v) * (1000.0 if u == 's' else 1.0) for k, v, u in _PROF.findall(block)}


def _tree_rss(proc):
    total = 0
    try:
        procs = [proc] + proc.children(recursive=True)
    except psutil.Error:
        return 0
    for p in procs:
        try:
            mi = p.memory_info()
            total += max(getattr(mi, 'peak_wset', 0) or 0, mi.rss)
        except psutil.Error:
            pass
    return total


def run_lean(path, version=PRIMARY, lean_path=None, olean_out=None, targets=(), timeout=TIMEOUT):
    """Check one file in a fresh process. `lean_path` is the olean dir, `olean_out` an
    output .olean path (library modules), `targets` the theorem names whose axiom report
    must be present and clean."""
    path = Path(path)
    text = path.read_text(encoding='utf-8')
    bad_tokens = forbidden_tokens(text)
    cmd = [str(lean_exe(version))]
    if olean_out:
        cmd += ['-o', str(Path(olean_out).resolve())]
    cmd.append(str(path.resolve()))
    env = dict(os.environ)
    if lean_path:
        env['LEAN_PATH'] = str(Path(lean_path).resolve())
    with _LOCK:
        CALLS[version] += 1
        n_calls = CALLS[version]
    t0 = time.perf_counter()
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
                            cwd=str(path.parent), text=True, encoding='utf-8', errors='replace')
    ps = psutil.Process(proc.pid)
    outbox = {}
    reader = threading.Thread(target=lambda: outbox.update(zip(('out', 'err'), proc.communicate())))
    reader.start()
    peak, timed_out, cpu = 0, False, 0.0
    while reader.is_alive():
        peak = max(peak, _tree_rss(ps))
        try:
            ct = ps.cpu_times()
            cpu = max(cpu, ct.user + ct.system)
        except psutil.Error:
            pass
        if time.perf_counter() - t0 > timeout:
            timed_out = True
            for p in ps.children(recursive=True) + [ps]:
                try:
                    p.kill()
                except psutil.Error:
                    pass
            break
        reader.join(0.004)
    reader.join()
    seconds = time.perf_counter() - t0
    out, err = outbox.get('out', '') or '', outbox.get('err', '') or ''
    axioms = parse_axioms(out)
    missing = [t for t in targets if t not in axioms]
    bad_ax = [t for t in targets if t in axioms and axioms[t][0] == 'bad']
    rc = proc.returncode
    prof = parse_profile(out + '\n' + err)
    has_error = bool(re.search(r'\berror\b', out + err))
    ok = (rc == 0 and not timed_out and not has_error and not bad_tokens and not missing and not bad_ax)
    kinds = {axioms[t][0] for t in targets if t in axioms}
    return {'file': path.name, 'version': version, 'ok': ok, 'rc': rc, 'timed_out': timed_out,
            'seconds': round(seconds, 4), 'cpu_seconds': round(cpu, 4), 'profile_ms': prof,
            'work_ms': (round(prof.get('elaboration', 0) + prof.get('type checking', 0), 3) if prof else None),
            'peak_rss_bytes': int(peak),
            'peak_rss_mb': round(peak / 1048576, 2), 'verifier_call_index': n_calls,
            'verifier_calls': 1, 'axioms': {t: axioms[t] for t in targets if t in axioms},
            'axiom_class': 'bad' if 'bad' in kinds else ('standard' if 'standard' in kinds else ('none' if kinds else None)),
            'forbidden': bad_tokens, 'missing_axiom_report': missing,
            'stdout': out[-1500:], 'stderr': err[-1500:]}


def run_many(jobs, workers=MAX_WORKERS):
    """jobs: list of kwargs for run_lean; returns results in order. <= 4 concurrent."""
    workers = max(1, min(int(workers), MAX_WORKERS))
    if workers == 1:
        return [run_lean(**j) for j in jobs]
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(lambda j: run_lean(**j), jobs))


def versions_info():
    out = {}
    for v in VERSIONS:
        exe = lean_exe(v)
        try:
            r = subprocess.run([str(exe), '--version'], capture_output=True, text=True, timeout=30)
            out[v] = r.stdout.strip()
        except OSError as e:
            out[v] = f'unavailable: {e}'
    return out
