#!/usr/bin/env python3
"""manifest.json for the RHC-04 results directory: file hashes (CRLF folded to LF) and the commits that pin the run."""
import hashlib
import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
h = lambda p: hashlib.sha256(p.read_bytes().replace(bytes([13, 10]), bytes([10]))).hexdigest()
files = {str(p.relative_to(OUT)).replace(chr(92), '/'): h(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name != 'manifest.json'}
manifest = {'schema': 'rhc04_manifest_v1', 'date_utc': '2026-11-14', 'hash_convention': 'SHA-256 with CRLF folded to LF',
            'control_harness_runtime_commit': '6537cc2105d376f8ee314073d502d35a474528d9',
            'protocol_frozen_commit': '3f91a88', 'amendment_1_commit': '27eed6f', 'monitors_frozen_commit': 'dcde188',
            'frozen_monitors_sha256': files['frozen_monitors.json'],
            'model_sha256': 'b252c5610a42ca82d20fe2a12813e9d069eed89292907e26c783eeb0bc961bc7',
            'oracle_vault': 'none: the runtime is the oracle; test family identities live only in the protocol and the auditor files',
            'files_sha256': files}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + chr(10), encoding='utf8', newline=chr(10))
print(json.dumps({'files': len(files)}))
