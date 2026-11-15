"""Independent Lean kernel/axiom audit of all six generated BPD-LG-02 files.

A successful exit requires 192 positive and 192 negative declarations, and
requires Lean to report an empty axiom inventory for every one of them.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys

POSITIVES = {'train': 128, 'dev': 32, 'test': 32}
FORBIDDEN = re.compile(r'\b(sorry|admit|native_decide|axiom|unsafe)\b')


def audit(root: Path, executable: str = 'lean') -> dict:
    version = subprocess.check_output([executable, '--version'], text=True).strip()
    if 'version 4.19.0' not in version:
        raise RuntimeError(f'unsupported Lean version: {version}')
    receipt = {'schema':'BPD-LG-02-KERNEL-v1', 'lean_version': version,
               'by_split':{},'positive_proofs':0,'negative_refutations':0,
               'axiom_free':0,'all_passed':False}
    try:
        allnames=set()
        for split, size in POSITIVES.items():
            for polarity,suffix in (('positive','positives'),('negative','refutations')):
                count=size
                original=root/f'{split}_{suffix}.lean'
                source=original.read_text()
                names=re.findall(r'^theorem (\w+)',source,re.M)
                if len(names)!=count or len(set(names))!=count or allnames.intersection(names):
                    raise RuntimeError(f'{split} {suffix}: declaration count or duplicate failure: {len(names)}')
                if FORBIDDEN.search(source):
                    raise RuntimeError(f'{split} {suffix}: forbidden proof declaration')
                allnames.update(names)
                audited=root/f'{split}_{suffix}_axioms.lean'
                audited.write_text(source+'\n'+'\n'.join(f'#print axioms {n}' for n in names)+'\n')
                run=subprocess.run([executable,str(audited)],capture_output=True,text=True,timeout=300)
                (root/f'{split}_{suffix}_stdout.log').write_text(run.stdout)
                (root/f'{split}_{suffix}_stderr.log').write_text(run.stderr)
                if run.returncode!=0:
                    raise RuntimeError(f'{split} {suffix} failed kernel elaboration: '\
                                       f'exit {run.returncode}\n{run.stdout[-7000:]}\n{run.stderr[-7000:]}')
                empty=run.stdout.count('does not depend on any axioms')
                if empty != count:
                    raise RuntimeError(f'{split} {suffix}: empty axiom count {empty}/{count}; output {run.stdout[-3000:]}')
                receipt['by_split'][f'{split}_{polarity}']={
                    'declarations': count,'axiom_free':empty,
                    'sha256':sha256(original.read_bytes()).hexdigest()}
                receipt['positive_proofs' if polarity=='positive' else 'negative_refutations']+=count
                receipt['axiom_free']+=empty
        if receipt['positive_proofs'] != 192 or receipt['negative_refutations'] != 192:
            raise RuntimeError('incomplete signed certificate coverage')
        receipt['all_passed']=True
    finally:
        (root/'kernel_receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    return receipt


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-dir',type=Path,required=True)
    parser.add_argument('--lean',default='lean')
    args=parser.parse_args()
    report=audit(args.source_dir,args.lean)
    print(json.dumps(report,sort_keys=True))

if __name__=='__main__':main()
