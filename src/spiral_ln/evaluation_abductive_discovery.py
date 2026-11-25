"""ADG-01: exact finite archival query planning, synthetic development only."""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from random import Random


@dataclass(frozen=True)
class Action:
    name: str
    cost: int
    outcomes: tuple[int, ...]
    gate: int = -1
    archive: bool = False


def world(seed, k, ungated=False, sham=False):
    """Known likelihood table, unknown uniform author. -1 means no archive match."""
    r = Random(seed)
    n = 2 ** (k + 1)
    authors = list(range(n))
    r.shuffle(authors)
    actions = []
    for bit in range(k):
        vals = [(a // 2 >> bit) & 1 for a in authors]
        if r.randrange(3) == 0:
            i = r.randrange(n)
            vals[i] ^= 1
        actions.append(Action(f'clue-{bit}', 1, tuple(vals)))
    actions.append(Action('distractor', 1, tuple(r.randrange(2) for _ in authors)))
    groups = list(range(n // 2))
    r.shuffle(groups)
    gates = {}
    for g in groups:
        gates[g] = len(actions)
        actions.append(Action(f'catalog-{g}', 1, (0,) * n))
    if sham:
        # Permute the names/indices of the identical catalogue prerequisites.
        gates = dict(zip(groups, reversed(list(gates.values()))))
    for g in groups:
        actions.append(Action(f'archive-{g}', 2,
            tuple(i if a // 2 == g else -1 for i, a in enumerate(authors)),
            -1 if ungated else gates[g], True))
    return tuple(actions)


def outcomes(actions, mask, i):
    parts = {}
    for h, value in enumerate(actions[i].outcomes):
        if mask & (1 << h):
            parts[value] = parts.get(value, 0) | (1 << h)
    return tuple(parts.items())


def solve(actions, budget, horizon=None):
    """Exact expected (correct, certified) rate. Finite lookahead replans each step.

    Objective (correct + 3*certified)/4; ties stop first, then lowest action index.
    A certificate requires a positive archive outcome; all such outcomes are unique.
    """
    if budget < 0 or (horizon is not None and horizon < 1):
        raise ValueError('invalid budget/horizon')
    n = len(actions[0].outcomes)
    full = (1 << n) - 1

    def utility(pair):
        return (pair[0] + 3 * pair[1]) / 4

    def legal(mask, used, b):
        for i, a in enumerate(actions):
            if used & (1 << i) or a.cost > b or (a.gate >= 0 and not used & (1 << a.gate)):
                continue
            yield i

    def transition(mask, used, b, i, follow):
        a = actions[i]
        total = [F(0), F(0)]
        for value, sub in outcomes(actions, mask, i):
            w = F(sub.bit_count(), mask.bit_count())
            pair = (F(1), F(1)) if a.archive and value >= 0 else follow(sub, used | (1 << i), b - a.cost)
            for j in range(2):
                total[j] += w * pair[j]
        return tuple(total)

    @lru_cache(None)
    def plan(mask, used, b, steps):
        best = (F(1, mask.bit_count()), F(0))
        chosen = -1
        if steps:
            for i in legal(mask, used, b):
                pair = transition(mask, used, b, i, lambda m, u, v: plan(m, u, v, steps - 1)[0])
                if utility(pair) > utility(best):
                    best, chosen = pair, i
        return best, chosen

    @lru_cache(None)
    def execute(mask, used, b):
        best, i = plan(mask, used, b, min(b, horizon) if horizon is not None else b)
        if i < 0:
            return best
        return transition(mask, used, b, i, execute)

    return execute(full, 0, budget)


def witness():
    """A catalogue discloses zero bits but enables an identifying receipt."""
    return (Action('catalogue', 1, (0, 0)), Action('archive', 2, (0, 1), 0, True),
            Action('clue', 1, (0, 1)))
