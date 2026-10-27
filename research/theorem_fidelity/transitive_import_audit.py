"""Deterministic source audit of an upstream Lean theorem's local import closure.

Usage: python transitive_import_audit.py --root upstream/lean --out closure.json
This is lexical provenance evidence. Compilation and #print axioms are separate.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path


def without_noncode(src: str) -> str:
    """Preserve line breaks; strip nested Lean comments and escaped strings."""
    chars = []
    i = 0
    depth = 0
    quoted = False
    while i < len(src):
        pair = src[i:i + 2]
        if depth and pair == '/-':
            depth += 1
            chars.extend('  ')
            i += 2
        elif depth and pair == '-/':
            depth -= 1
            chars.extend('  ')
            i += 2
        elif depth:
            chars.append('\n' if src[i] == '\n' else ' ')
            i += 1
        elif quoted and src[i] == '\\' and i + 1 < len(src):
            chars.extend('  ')
            i += 2
        elif quoted and src[i] == '"':
            quoted = False
            chars.append(' ')
            i += 1
        elif quoted:
            chars.append('\n' if src[i] == '\n' else ' ')
            i += 1
        elif pair == '--':
            end = src.find('\n', i)
            if end < 0:
                end = len(src)
            chars.extend(' ' * (end - i))
            i = end
        elif pair == '/-':
            depth += 1
            chars.extend('  ')
            i += 2
        elif src[i] == '"':
            quoted = True
            chars.append(' ')
            i += 1
        else:
            chars.append(src[i])
            i += 1
    if depth or quoted:
        raise ValueError('unterminated Lean block comment or string')
    return ''.join(chars)


IMPORT_RE = re.compile(r'(?m)^[ \t]*(?:public[ \t]+|private[ \t]+)?import[ \t]+([A-Za-z0-9_. \t]+)$')
FLAG_RE = {
    'placeholder': re.compile(r'\b(?:sorry|admit)\b'),
    'explicit_axiom': re.compile(r'\baxiom\b'),
    'unsafe': re.compile(r'\bunsafe\b'),
    'opaque': re.compile(r'\bopaque\b'),
    'native_decide': re.compile(r'\bnative_decide\b|\bLean\.ofReduceBool\b'),
    'partial_def': re.compile(r'\bpartial\s+def\b'),
}


def check_module_name(s: str) -> None:
    if not re.fullmatch(r'OAI(?:\.[A-Za-z0-9_]+)+', s):
        raise ValueError('expected OAI module identifier: ' + repr(s))


def scan(root: Path, start: str, max_modules: int = 10000) -> dict:
    """Walk every reachable in-repository OAI module and hash its source."""
    root = root.resolve()
    check_module_name(start)
    pending = [start]
    discovered = {}
    edges = []
    while pending:
        module = pending.pop()
        if module in discovered:
            continue
        if len(discovered) >= max_modules:
            raise ValueError('exceeded local-module traversal cap')
        check_module_name(module)
        relative = Path(*module.split('.')).with_suffix('.lean')
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError('escaped source root')
        if not path.is_file():
            raise FileNotFoundError(f'missing in-repository Lean import {module} at {relative}')
        raw = path.read_bytes()
        code = without_noncode(raw.decode('utf-8'))
        imports = sorted(set(name for group in IMPORT_RE.findall(code) for name in group.split()))
        local_imports = [imp for imp in imports if imp.startswith('OAI.')]
        flags = {label: [code.count('\n', 0, m.start()) + 1 for m in regex.finditer(code)]
                 for label, regex in FLAG_RE.items()}
        discovered[module] = {
            'path': relative.as_posix(),
            'sha256': hashlib.sha256(raw).hexdigest(),
            'blob_sha1': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\x00' + raw).hexdigest(),
            'bytes': len(raw),
            'direct_local_imports': local_imports,
            'flags': {k: v for k, v in flags.items() if v},
        }
        for dependency in local_imports:
            edges.append((module, dependency))
            if dependency not in discovered:
                pending.append(dependency)
    suspicious = {module: value['flags'] for module, value in discovered.items() if value['flags']}
    return {
        'schema': 1,
        'start_module': start,
        'local_modules': len(discovered),
        'direct_local_edges': len(edges),
        'total_source_bytes': sum(v['bytes'] for v in discovered.values()),
        'flagged_modules': suspicious,
        'files': dict(sorted(discovered.items())),
        'status': 'lexical source closure, not kernel or transitive external-package audit',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--start', default='OAI.Computability.UniqueGames.Theorem')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = scan(args.root, args.start)
    report = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False) + '\n'
    if args.out:
        args.out.write_text(report, encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
