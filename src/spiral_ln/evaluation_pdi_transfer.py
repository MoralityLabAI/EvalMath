"""PDI-08: exact, family-paired proof-transfer receipt scoring.

This validates a supplied public manifest and receipt structure. Independent
kernel replay, custody, provenance, and completeness of cost logs are external
requirements; a structurally valid receipt is not a proof of their truth.
"""
from fractions import Fraction as F
from hashlib import sha256
from math import comb
import json

ARMS = ('no_reuse', 'verified_reuse', 'matched_retrieval', 'sham_reuse', 'revoked_version')
COSTS = ('tokens', 'kernel_calls', 'elapsed_ms')
STATUS = ('pass', 'fail', 'unverified')


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                             ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def is_digest(value):
    return isinstance(value, str) and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def exact_cost(value):
    if not isinstance(value, dict) or set(value) != set(COSTS) or any(type(v) is not int or v < 0 for v in value.values()):
        raise ValueError('invalid nonnegative integer cost counters')
    return tuple(value[k] for k in COSTS)


def manifest_index(manifest):
    if manifest.get('schema') != 'PDI-transfer-pilot-v1' or tuple(manifest.get('arms', ())) != ARMS:
        raise ValueError('unknown manifest schema or arm set')
    if not is_digest(manifest.get('model_sha256')) or not is_digest(manifest.get('runner_sha256')):
        raise ValueError('model and runner commitments required')
    if type(manifest.get('seed')) is not int or manifest.get('family_count') != 32:
        raise ValueError('pilot requires fixed seed and 32 families')
    families = manifest.get('families', [])
    if len(families) != 32:
        raise ValueError('need exactly 32 held-out families')
    index = {}
    roots, statements = set(), set()
    for family in families:
        name, root = family['family_id'], family['construction_sha256']
        targets = family['targets']
        if not isinstance(name, str) or not name or name in index or not is_digest(root) or root in roots:
            raise ValueError('nonunique family or construction commitment')
        if not is_digest(family.get('environment_sha256')) or family.get('split') != 'heldout':
            raise ValueError('missing held-out environment commitment')
        if len(targets) != 4 or len({t['target_id'] for t in targets}) != 4:
            raise ValueError('four unique targets per family required')
        roots.add(root)
        for target in targets:
            if not isinstance(target['target_id'], str) or not target['target_id']:
                raise ValueError('invalid target identity')
            h = target['statement_sha256']
            if not is_digest(h) or h in statements:
                raise ValueError('duplicate or invalid statement commitment')
            statements.add(h)
        index[name] = (family, exact_cost(family['budget']))
    return index


def summarize(manifest, rows):
    """Score complete paired runs. Costs include overhead and all logged attempts.

    Counts an authorized target as true only when closure and independent
    dependency checks are both reported PASS. Failed or unknown evidence stays
    separate. The conservative false weight counts both invalid and unverified.
    """
    index = manifest_index(manifest)
    h = digest(manifest)
    runs = {}
    for row in rows:
        name, arm = row['family_id'], row['arm']
        key = (name, arm)
        if name not in index or arm not in ARMS or key in runs or row.get('manifest_sha256') != h:
            raise ValueError('unexpected, duplicate or unbound run')
        family, budget = index[name]
        if row.get('environment_sha256') != family['environment_sha256'] or not is_digest(row.get('trace_sha256')):
            raise ValueError('wrong environment or missing trace commitment')
        if row.get('model_sha256') != manifest['model_sha256'] or row.get('runner_sha256') != manifest['runner_sha256']:
            raise ValueError('wrong model or runner')
        if row.get('seed') != manifest['seed']:
            raise ValueError('wrong seed')
        costs = list(exact_cost(row['overhead']))
        true = false = unknown = attempts = 0
        seen = set()
        expected = {t['target_id']: t['statement_sha256'] for t in family['targets']}
        for target in row['targets']:
            tid = target['target_id']
            if tid in seen or tid not in expected or target.get('statement_sha256') != expected[tid]:
                raise ValueError('wrong or duplicate target')
            seen.add(tid)
            closed, dep, authorized = target['kernel'], target['dependency'], target['authorized']
            if closed not in STATUS or dep not in STATUS or type(authorized) is not bool:
                raise ValueError('invalid reported verdict')
            logs = target['attempts']
            if not isinstance(logs, list) or (authorized and not logs):
                raise ValueError('missing attempt logs')
            if closed == 'pass' and not logs:
                raise ValueError('closure requires attempt')
            for log in logs:
                if not is_digest(log.get('artifact_sha256')):
                    raise ValueError('missing attempt commitment')
                costs = [a+b for a,b in zip(costs, exact_cost(log['cost']))]
                attempts += 1
            if authorized:
                if closed == dep == 'pass':
                    true += 1
                elif 'fail' in (closed, dep):
                    false += 1
                else:
                    unknown += 1
        if seen != set(expected) or any(c > b for c,b in zip(costs,budget)):
            raise ValueError('incomplete target coverage or family budget exceeded')
        runs[key] = {'true': true, 'false': false, 'unknown': unknown, 'attempts': attempts, 'cost': tuple(costs)}
    if set(runs) != {(f,a) for f in index for a in ARMS}:
        raise ValueError('incomplete paired arm coverage')
    return runs


def paired_statistics(runs, arm='verified_reuse', baseline='no_reuse'):
    """Exact descriptive pilot statistics. Sign test assumes independent families.

    No alpha, margin, or inferential acceptance criterion is defined for the pilot.
    Missing evidence is charged as possible false authorization.
    """
    families = sorted({f for f,a in runs})
    if not families or arm == baseline:
        raise ValueError('empty or identical comparison')
    deltas = [runs[f,arm]['true'] - runs[f,baseline]['true'] for f in families]
    risk = [runs[f,arm]['false']+runs[f,arm]['unknown']-runs[f,baseline]['false']-runs[f,baseline]['unknown'] for f in families]
    n = len(deltas)
    mean = F(sum(deltas), n)
    var = sum((F(d)-mean)**2 for d in deltas)/(n-1) if n>1 else F(0)
    pos, neg = sum(d>0 for d in deltas), sum(d<0 for d in deltas)
    k = pos+neg
    sign_p = min(F(1), 2*sum(F(comb(k,i), 2**k) for i in range(min(pos,neg)+1)))
    return {'families': n, 'true_delta': mean, 'sample_variance': var,
            'conservative_risk_delta': F(sum(risk), n), 'wins': pos, 'losses': neg,
            'ties': n-k, 'two_sided_sign_p': sign_p}
