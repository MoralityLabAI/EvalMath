"""Offline source-fidelity checks, deliberately not an upstream kernel audit."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT/'research/ccf/source_archive'


def signatures(s):
    return {m[1]: ' '.join(m[2].split()) for m in re.finditer(
        r'^theorem\s+(\w+)\s*:\s*(.*?)\s*:=\s*by\b', s, re.M|re.S)}


def check_signatures(challenge, solution, names):
    a,b = signatures(challenge),signatures(solution)
    return set(a) == set(b) == set(names) and all(a[n] == b[n] for n in names)


def test_pinned_git_blobs():
    manifest = json.loads((ARCHIVE/'sources.json').read_text())
    for source in manifest['sources']:
        data = (ROOT/source['path']).read_bytes()
        assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\x00'+data).hexdigest() == source['blob_sha']


def test_openai_crosswalk():
    challenge = (ARCHIVE/'openai/challenge.lean').read_text()
    solution = (ARCHIVE/'openai/solution.lean').read_text()
    names = [n.rsplit('.',1)[-1] for n in json.loads((ARCHIVE/'openai/manifest.json').read_text())['theorem_names']]
    assert len(names) == 6
    assert check_signatures(challenge,solution,names)
    assert len(re.findall(r'^\s+sorry\s*$',challenge,re.M)) == 6
    assert not re.search(r'\bsorry\b',solution)
    mutations = [('2 ≤ n → ∀ p ε', '1 ≤ n → ∀ p ε'),
                 ('(0 < ε ∨ (p = 2 ∧ ε = 0))', '0 ≤ ε'),
                 ('0 < R → ∀ f', '0 ≤ R → ∀ f'),
                 ('1 < a → ∀ b', '1 ≤ a → ∀ b'),
                 ('δ ≤ 1 → ∀ f', 'δ ≤ 2 → ∀ f'),
                 ('0 < ε → ∃ C', '0 ≤ ε → ∃ C'),
                 ('< α →', '≤ α →')]
    for old,new in mutations:
        assert old in challenge
        assert not check_signatures(challenge.replace(old,new,1),solution,names)


def flash_scope(s):
    return all(x in s for x in ('(scope : InScope Z = true)',
        '(read : readFiles Z = .ok pp)', '(exact : pp.pol = Inst.Model.AcceptancePolicy.exact)',
        'soundnessErrorInQueries t 1'))


def test_flashprove_crosswalk():
    s = (ARCHIVE/'flashprove/sound.lean').read_text()
    assert flash_scope(s)
    for old in ('(scope : InScope Z = true)', '(read : readFiles Z = .ok pp)',
                '(exact : pp.pol = Inst.Model.AcceptancePolicy.exact)', 'soundnessErrorInQueries t 1'):
        assert not flash_scope(s.replace(old,'REMOVED'))
    doc = (ARCHIVE/'flashprove/output.md').read_text()
    assert 'WITHIN LIMITS: clipped-gap' in doc
    assert 'result-v1' in doc and 'next-token' in doc and 'NOT-A-VERIFICATION' in doc
