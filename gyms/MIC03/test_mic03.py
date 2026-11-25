from itertools import permutations, product
from run import (FAMILIES, make, initial, score, action, schedule_oracle,
                 certificate_oracle, rollout, teacher, Ranker)
import torch


def test_exact_schedule_oracles():
    for f in FAMILIES:
        for seed in range(5):
            d = make(f, seed, 4)
            p = initial(f, d)
            values = []
            for order in permutations(range(4)):
                q = p
                for i in order:
                    v = action(f, d, q, i)
                    assert score(f, d, v) <= score(f, d, q)
                    q = v
                values.append(score(f, d, q))
            assert schedule_oracle(f, d)(p, 15) == min(values)
            assert certificate_oracle(f, d) <= min(values)
            if f == 'dag':
                assert rollout(f, d, 'dependency')['score'] == certificate_oracle(f, d)
            if f.startswith('cover'):
                candidates = []
                for q in product(range(5), repeat=4):
                    try:
                        candidates.append(score(f, d, q))
                    except ValueError:
                        pass
                assert certificate_oracle(f, d) == min(candidates)


def test_teacher_labels_and_mask():
    for f in FAMILIES:
        d = make(f, 7, 5)
        xs, masks, labels = teacher(f, d)
        p = initial(f, d)
        val = schedule_oracle(f, d)
        mask = 31
        for t in range(5):
            assert any(labels[t])
            assert all(not y or m for y, m in zip(labels[t], masks[t]))
            i = labels[t].index(True)
            nxt = action(f,d,p,i)
            assert val(p,mask) == val(nxt,mask^(1<<i))
            p = nxt
            mask ^= 1<<i


def test_ranker_budget():
    torch.manual_seed(2)
    for f in FAMILIES:
        d = make(f, 12, 6)
        a = rollout(f,d,'greedy')
        b = rollout(f,d,'dependency')
        c = rollout(f,d,'recurrent',Ranker(True))
        e = rollout(f,d,'stateless',Ranker(False))
        assert a['score_calls'] == b['score_calls'] == c['score_calls'] == e['score_calls'] == 49
        for r in (a,b,c,e):
            assert sorted(r['order']) == list(range(6))


def test_infeasible_rejected():
    for f in FAMILIES:
        d = make(f, 0, 5)
        for p in ((0,)*5, (-1,)*5, (0,)*4):
            try:
                score(f,d,p)
            except ValueError:
                pass
            else:
                raise AssertionError('accepted invalid certificate')
