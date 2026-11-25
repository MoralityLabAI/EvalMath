"""MIT-13 Lean 4 checker: string filter, standalone file, WSL Lean run, axiom audit. Core Lean only."""
import re, subprocess, tempfile, os
from pathlib import Path

LEAN = '~/.elan/toolchains/leanprover--lean4---v4.34.1/bin/lean'
DISTRO = 'Ubuntu-24.04'
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
FORBIDDEN = [
    (r'sorry', 'sorry'), (r'\badmit\b', 'admit'), (r'axiom', 'axiom'), (r'native_decide', 'native_decide'),
    (r'implemented_by', 'implemented_by'), (r'\bextern\b', 'extern'), (r'\bunsafe\b', 'unsafe'),
    (r'@\[', 'attribute'), (r'\bimport\b', 'import'), (r'\bopen\b', 'open'), (r'set_option', 'set_option'),
    (r'\b(macro|macro_rules|elab|syntax|notation|infix|infixl|infixr|prefix|postfix)\b', 'metaprogramming'),
    (r'run_cmd|run_tac|run_meta', 'metaprogramming'), (r'#', 'command'),
    (r'(?m)^\s*(theorem|lemma|def|instance|example|namespace|section|end|abbrev|structure|inductive|class|mutual|'
     r'variable|universe|private|protected|noncomputable|partial|opaque|initialize|attribute|local|scoped|deriving)\b',
     'top-level command'),
    (r'[\x00-\x08\x0b-\x1f]', 'control character'),
]


def filter_proof(name, proof):
    """Return a rejection reason, or None when the proof text passes the string filter."""
    if not isinstance(proof, str) or not proof.strip():
        return 'empty proof'
    for pattern, label in FORBIDDEN:
        if re.search(pattern, proof):
            return f'forbidden: {label}'
    if re.search(r'(?<![\w.])' + re.escape(name) + r'(?![\w])', proof):
        return 'self-citation'
    return None


def build_file(name, statement, proof):
    body = '\n'.join('  ' + line for line in proof.strip('\n').split('\n'))
    return f'{statement.rstrip()} := by\n{body}\n\n#print axioms {name}\n'


def parse_axioms(output):
    """Axiom names from `#print axioms` output, or None when the line is missing."""
    if 'does not depend on any axioms' in output:
        return []
    m = re.search(r'depends on axioms: \[(.*?)\]', output, re.S)
    return [a.strip() for a in m.group(1).split(',') if a.strip()] if m else None


def wsl_path(p):
    p = Path(p).resolve()
    return '/mnt/' + p.drive[0].lower() + p.as_posix()[2:]


def run_lean(source, timeout=180):
    """Run Lean on source through WSL; returns (returncode, combined output)."""
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / 'mit13.lean'
        f.write_text(source, encoding='utf-8', newline='\n')
        cmd = f'cd /tmp && timeout {timeout - 10} {LEAN} {wsl_path(f)} 2>&1'
        env = dict(os.environ, MSYS_NO_PATHCONV='1')
        p = subprocess.run(['wsl.exe', '-d', DISTRO, '--exec', 'bash', '-lc', cmd], capture_output=True,
                           timeout=timeout, env=env)
    return p.returncode, p.stdout.decode('utf-8', 'replace').replace('\0', '')


def check(name, statement, proof, runner=run_lean):
    reason = filter_proof(name, proof)
    if reason:
        return dict(ok=False, reason=reason, axioms=None, output='')
    try:
        code, out = runner(build_file(name, statement, proof))
    except (OSError, subprocess.TimeoutExpired) as e:
        return dict(ok=False, reason=f'lean_run_error: {type(e).__name__}', axioms=None, output='')
    if code != 0 or 'error' in out.lower():
        return dict(ok=False, reason='lean_error', axioms=None, output=out[-2000:])
    axioms = parse_axioms(out)
    if axioms is None:
        return dict(ok=False, reason='axiom_output_missing', axioms=None, output=out[-2000:])
    if not set(axioms) <= ALLOWED_AXIOMS:
        return dict(ok=False, reason='disallowed_axioms', axioms=axioms, output=out[-2000:])
    return dict(ok=True, reason='ok', axioms=axioms, output=out[-2000:])
