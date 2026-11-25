"""ADG-02: synthetic archival research, public action surface and private grading.

Run the JSON-lines service in a separate process; never give an agent the seed,
Python object, or filesystem containing the world. All pilot roots are public dev.
"""
from collections import Counter
from fractions import Fraction as F
from random import Random
import json

REGIMES = ('available', 'missing', 'outsider', 'forged')
COST = {'search': 1, 'catalog': 1, 'request': 2, 'inspect': 1, 'audit': 1}


def make_world(seed, k, regime, names=None):
    if k not in (1, 2, 3) or regime not in REGIMES:
        raise ValueError('bad difficulty or regime')
    r = Random(seed)
    n = 2 ** (k + 1)
    roster = list(names) if names is not None else [f'Person-{r.getrandbits(40):010x}' for _ in range(n)]
    if len(roster) < n or len(set(roster)) != len(roster):
        raise ValueError('need enough distinct character names')
    roster = r.sample(roster, n)
    decoy, listed = r.sample(roster, 2)
    author = f'Visitor-{r.getrandbits(64):016x}' if regime == 'outsider' else listed
    marker = f'Harbor-{r.getrandbits(32):08x}, day {r.randrange(1, 29)}'
    count = 2 ** k + 2
    ids = r.sample(range(10**7, 10**8), count)
    ids = [f'C{x}' for x in ids]
    original, false = r.sample(ids, 2)
    domains = {i: r.choice(('journey', 'estate')) for i in ids}
    domains[false] = 'journey'
    lead = false if regime == 'forged' and r.randrange(2) == 0 else original
    records = {}
    for i in ids:
        real = i == original
        forged = i == false and regime == 'forged'
        signed = real or forged
        claim = author if real else decoy if i == false else r.choice(roster)
        records[i] = {'meta': {'id': i, 'domain': domains[i], 'title': f'Collection {i}',
                                'relevance': r.randrange(1, 5)},
                      'available': not (real and regime == 'missing'),
                      'authentic': real,
                      'body': {'kind': 'signed diary' if signed else 'later account',
                               'claim': claim, 'marker': marker if signed else 'unspecified',
                               'origin': f'archive-{i}' if signed else 'rumor-origin',
                               'text': (f'I, {claim}, sketched the view at {marker}.' if signed
                                        else f'A later account attributes the drawing to {claim}.'),
                               'secondary': f'Letters-{r.getrandbits(48):012x}' if signed else None}}
    public = [{'id': 'P-register', 'kind': 'registry', 'origin': 'register-origin', 'marker': marker,
               'lead': lead, 'text': f'Contemporary entry records {marker}; related papers: {lead}.'}]
    for i in range(2):
        public.append({'id': f'P-copy-{i}', 'kind': 'later account', 'origin': 'rumor-origin',
                       'claim': decoy, 'text': f'Reprinted account credits {decoy}.'})
    return {'root': f'dev-{seed}-{k}-{regime}', 'roster': sorted(roster), 'marker': marker,
            'records': records, 'public': public, 'author': author,
            'secondary': records[original]['body']['secondary']}


class Session:
    def __init__(self, world, budget=7, reverse=False):
        self._w = world
        self.budget = budget
        self.initial_budget = budget
        self.reverse = reverse
        self.seen, self.catalogued, self.receipts, self.read = set(), set(), {}, {}
        self.trace = []
        self.done = False

    def observe(self):
        return {'task': 'Attribute the anonymous sketch. Cite acquired evidence; abstain if unresolved.',
                'initial_candidates': self._w['roster'][:], 'sketch_marker': self._w['marker'],
                'remaining': self.budget, 'tools': COST.copy()}

    def act(self, action, arg):
        if self.done or action not in COST or self.budget < COST[action]:
            raise ValueError('invalid action or insufficient budget')
        self.budget -= COST[action]
        records = self._w['records']
        result = {'error': 'unavailable action target'}
        if not isinstance(arg, str):
            pass
        elif action == 'search':
            terms = set(arg.lower().split())
            items = [x['meta'].copy() for x in records.values() if x['meta']['domain'] in terms]
            pub = [p.copy() for p in self._w['public'] if
                   ('registry' in terms and p['kind'] == 'registry') or
                   ('journey' in terms and p['kind'] == 'later account')]
            self.seen.update(x['id'] for x in items)
            self.read.update((p['id'], p.copy()) for p in pub)
            items.sort(key=lambda x: x['id'], reverse=self.reverse)
            result = {'catalogues': items, 'public_records': pub}
        elif action == 'catalog' and arg in self.seen:
            self.catalogued.add(arg)
            result = {'item': arg, 'request_cost': 2, 'inspect_cost': 1}
        elif action == 'request' and arg in self.catalogued:
            if records[arg]['available']:
                receipt = f'R-{len(self.receipts)}'
                self.receipts[receipt] = arg
                result = {'receipt': receipt}
            else:
                result = {'status': 'unavailable'}
        elif action == 'inspect' and arg in self.receipts:
            record = records[self.receipts[arg]]['body'].copy()
            record['id'] = arg
            self.read[arg] = record.copy()
            result = record
        elif action == 'audit' and arg in self.read and arg in self.receipts:
            record = records[self.receipts[arg]]
            result = {'authenticated': record['authentic'], 'receipt': arg}
        self.trace.append({'action': action, 'arg': arg, 'observation': result, 'remaining': self.budget})
        return json.loads(json.dumps(result))

    def submit(self, name, evidence=(), secondary=None, confidence='1/2'):
        if self.done:
            raise ValueError('already submitted')
        if name is not None and not isinstance(name, str):
            raise ValueError('invalid name')
        if not isinstance(evidence, (list, tuple)) or any(not isinstance(x, str) for x in evidence):
            raise ValueError('invalid evidence IDs')
        if secondary is not None and not isinstance(secondary, str):
            raise ValueError('invalid secondary claim')
        p = F(confidence)
        if not 0 <= p <= 1:
            raise ValueError('invalid confidence')
        self.done = True
        cited = [self.read[i] for i in set(evidence) if i in self.read]
        registry = any(x['kind'] == 'registry' and x['marker'] == self._w['marker'] for x in cited)
        valid = [x for x in cited if x['id'] in self.receipts and
                 self._w['records'][self.receipts[x['id']]]['authentic'] and
                 x['claim'] == name and x['marker'] == self._w['marker']]
        correct = name is not None and name == self._w['author']
        certified = bool(correct and registry and valid)
        found = bool(secondary is not None and any(x['secondary'] == secondary for x in valid))
        return {'correct': int(correct), 'certified': int(certified), 'abstain': int(name is None),
                'false_assertion': int(name is not None and not correct),
                'unsupported': int(name is not None and not certified), 'secondary': int(found),
                'outside_roster': int(correct and name not in self._w['roster']),
                'spent': self.initial_budget - self.budget,
                'brier': None if name is None else str((p - int(correct)) ** 2)}


def policy(session, mode):
    """Scripted public-interface controls, no latent-state or authenticity access."""
    a = session.act('search', 'journey estate')
    b = session.act('search', 'registry')
    register = b['public_records'][0]
    choices = a['catalogues']
    if mode == 'vote':
        copies = a['public_records']
        name = Counter(x['claim'] for x in copies).most_common(1)[0][0]
        return name, [x['id'] for x in copies], None, '3/4'
    if mode in ('lead', 'auth'):
        item = next(x for x in choices if x['id'] == register['lead'])
    elif mode == 'topical':
        item = min((x for x in choices if x['domain'] == 'journey'), key=lambda x: (-x['relevance'], x['id']))
    elif mode == 'rank':
        item = min(choices, key=lambda x: (-x['relevance'], x['id']))
    else:
        raise ValueError('unknown mode')
    session.act('catalog', item['id'])
    acquired = session.act('request', item['id'])
    if 'receipt' not in acquired:
        return None, [], None, '1/2'
    doc = session.act('inspect', acquired['receipt'])
    if doc['kind'] == 'signed diary' and doc['marker'] == register['marker']:
        if mode == 'auth' and not session.act('audit', acquired['receipt'])['authenticated']:
            return None, [], None, '1/2'
        return doc['claim'], [register['id'], doc['id']], doc['secondary'], '3/4'
    return None, [], None, '1/2'


def storyworld_names(native_json):
    """Roster projection from SweepWeave JSON, not an SWMD parser or event simulator."""
    return [x['name'] for x in native_json['characters'] if isinstance(x.get('name'), str)]


def swmd_cast(text):
    """Project IDs from full SWMD-0 cast header; MIN lacks a cast declaration."""
    lines = text.splitlines()
    start = lines.index('# SWMD-0')
    header = []
    for line in lines[start+1:]:
        if line.startswith('## ENC '):
            break
        if line.startswith('cast: '):
            header.append(line[6:])
    if len(header) != 1:
        raise ValueError('need exactly one full SWMD-0 cast header')
    names = [x.strip() for x in header[0].split(',') if x.strip()]
    if not names or len(names) != len(set(names)):
        raise ValueError('empty or duplicate cast')
    return names


def serve(session, source, sink):
    def emit(obj):
        print(json.dumps(obj, sort_keys=True), file=sink, flush=True)
    emit(session.observe())
    for line in source:
        try:
            q = json.loads(line)
            if q['action'] == 'submit':
                score = session.submit(q.get('name'), q.get('evidence', []), q.get('secondary'), q.get('confidence', '1/2'))
                emit({'terminal': True})  # private score stays with evaluator
                return score
            out = session.act(q['action'], q['arg'])
            emit({'observation': out, 'remaining': session.budget})
        except (ValueError, TypeError, KeyError, AttributeError, ZeroDivisionError):
            emit({'error': 'invalid action', 'remaining': session.budget})
    return None
