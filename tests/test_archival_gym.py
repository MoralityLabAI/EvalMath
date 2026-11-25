from spiral_ln.evaluation_archival_gym import Session, make_world, policy, serve, storyworld_names
from io import StringIO
import json
import pytest


def test_gate_and_budget():
    w = make_world(1, 1, 'available')
    i = next(iter(w['records']))
    s = Session(w)
    assert 'error' in s.act('request', i)
    assert 'error' in s.act('catalog', i)
    assert 'error' in s.act('inspect', 'R-0')
    assert s.budget == 3
    with pytest.raises(ValueError):
        s.act('request', i) if s.budget < 2 else Session(w, 0).act('search', 'journey')


def test_copy_cannot_certify_even_correct_guess():
    w = make_world(2, 2, 'available')
    s = Session(w)
    x = s.act('search', 'journey')['public_records']
    assert x[0]['origin'] == x[1]['origin']
    score = s.submit(w['author'], [p['id'] for p in x])
    assert score['correct'] and not score['certified'] and score['unsupported']


def test_known_regimes():
    for regime in ('available', 'missing', 'outsider'):
        w = make_world(3, 2, regime)
        s = Session(w)
        score = s.submit(*policy(s, 'lead'))
        assert score['certified'] == int(regime != 'missing')
        assert score['outside_roster'] == int(regime == 'outsider')
        assert score['secondary'] == score['certified']
        assert score['abstain'] == int(regime == 'missing')


def test_forged_and_unread():
    for seed in range(20):
        w = make_world(seed, 2, 'forged')
        if not w['records'][w['public'][0]['lead']]['authentic']:
            s = Session(w)
            score = s.submit(*policy(s, 'lead'))
            assert score['false_assertion'] and not score['certified'] and not score['secondary']
            break
    else:
        pytest.fail('no forged witness')
    s = Session(w)
    assert not s.submit(w['author'], ['R-0', 'P-register'])['certified']


def test_service_private_and_terminal():
    w = make_world(3, 1, 'outsider')
    sink = StringIO()
    score = serve(Session(w), StringIO('{"action":"submit","name":null}\n'), sink)
    messages = [json.loads(x) for x in sink.getvalue().splitlines()]
    assert w['author'] not in sink.getvalue() and 'records' not in messages[0]
    assert messages[-1] == {'terminal': True} and score['abstain']
    assert storyworld_names({'characters': [{'name': 'A'}]}) == ['A']


def test_authentication_and_order_sham():
    for seed in range(20):
        w = make_world(seed, 2, 'forged')
        a, b = Session(w), Session(w, reverse=True)
        x, y = a.submit(*policy(a, 'auth')), b.submit(*policy(b, 'auth'))
        assert x == y and not x['false_assertion']
        assert x['spent'] <= 7
        if not w['records'][w['public'][0]['lead']]['authentic']:
            assert x['abstain']


def test_swmd_projection():
    from spiral_ln.evaluation_archival_gym import swmd_cast
    text = '---\n---\n# SWMD-0\nid: test\ncast: a, b, c, d\n## ENC e | Scene | turn=0..1 | spools=[]\nT: private scene\n'
    names = swmd_cast(text)
    w = make_world(2, 1, 'available', names)
    assert sorted(names) == w['roster']
    with pytest.raises(ValueError):
        swmd_cast('# SWMD-0-MIN\nid: test')


def test_invalid_submission_recoverable():
    s = Session(make_world(7, 1, 'available'))
    with pytest.raises(ValueError):
        s.submit(None, evidence=[{}])
    assert not s.done
    sink = StringIO()
    score = serve(s, StringIO('{"action":"submit","confidence":"1/0"}\n{"action":"submit","name":null}\n'), sink)
    assert score['abstain'] == 1
    assert [json.loads(x) for x in sink.getvalue().splitlines()][1]['error'] == 'invalid action'
