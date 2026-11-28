"""Generate deterministic prompt/gold exports and a reproducible source receipt."""
import argparse
import hashlib
import json
from pathlib import Path
from spiral_ln.evaluation_cpf03 import exports, summary, abstract_countermodels

ROOT = Path(__file__).resolve().parents[1]
FILES = ('src/spiral_ln/evaluation_cpf03.py', 'tests/test_evaluation_cpf03.py',
         'scripts/verify_evaluation_cpf03.py', 'paper/cpf03_semantic_mutations.md',
         'lean/FeedbackChannel/CPF03.lean')


def jsonl(rows):
    return ''.join(json.dumps(r, sort_keys=True, ensure_ascii=False) + '\n' for r in rows)


def report():
    prompts, gold = exports()
    assert len(prompts) == len(gold) == 42
    assert len({r['id'] for r in prompts}) == 42
    assert {r['id'] for r in prompts} == {r['id'] for r in gold}
    assert all(not abstract_countermodels(k, False) and abstract_countermodels(k, True)
               for k in ('bound','absence','existence'))
    for group in {r['group'] for r in gold}:
        assert len({r['split'] for r in gold if r['group'] == group}) == 1
    result = {"schema":"CPF-03.0", "scope":"curriculum fixture; public held-out split; no model runs or upstream rebuild",
              "checks":{"unique_ids":True,"group_disjoint":True,"abstract_logic":True},
              "summary":summary(), "export_sha256":{name:hashlib.sha256(jsonl(rows).encode()).hexdigest()
               for name,rows in (("prompts",prompts),("gold",gold))},
              "source_sha256":{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES}}
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path)
    p.add_argument('--export-dir', type=Path)
    args = p.parse_args()
    if args.export_dir:
        args.export_dir.mkdir(parents=True, exist_ok=True)
        for name, rows in zip(('prompts','gold'), exports()):
            (args.export_dir / (name+'.jsonl')).write_text(jsonl(rows), encoding='utf-8')
    data = json.dumps(report(), indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding='utf-8')
    else:
        print(data, end='')
