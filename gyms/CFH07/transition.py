"""CFH-07 fail-closed verifier for public development research transitions.
Env is constructed by a trusted mathematical evaluator, never by a proposer.
Only observations and acquired/cheap predictions may restrict the version set.
"""
from dataclasses import dataclass
from functools import cache


def require(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass(frozen=True, eq=False)
class Env:
    truth: tuple  # probe -> route -> exact residue (evaluator only)
    cheap: tuple  # probe -> route -> residue or None
    groups: tuple  # probe -> route -> acquisition group ID
    moduli: tuple
    n_groups: int

    def validate(self):
        n = len(self.truth[0]) if self.truth else 0
        require(n > 0 and len(self.truth) == len(self.cheap) == len(self.groups) == len(self.moduli), 'shape')
        require(type(self.n_groups) is int and self.n_groups > 0, 'group count')
        for t, c, g, p in zip(self.truth, self.cheap, self.groups, self.moduli):
            require(type(p) is int and p >= 2 and len(t) == len(c) == len(g) == n, 'row shape')
            for v, w, j in zip(t, c, g):
                require(type(v) is int and 0 <= v < p, 'truth residue')
                require(w is None or (type(w) is int and w == v), 'unsound cheap evidence')
                require(type(j) is int and 0 <= j < self.n_groups, 'group id')
        return n

    @cache
    def restrict(self, state, bought, q, answer, symbolic):
        for h, (v, w, j) in enumerate(zip(self.truth[q], self.cheap[q], self.groups[q])):
            if (bought >> j & 1) or (symbolic and w is not None):
                if v != answer:
                    state &= ~(1 << h)
        return state


def verify(env, events, hidden, base_cap, query_cap, symbolic=True):
    """Authenticate observations with evaluator-owned hidden route; never export it as input.
    Claimed masks are checked exactly. Retrospective restriction is mandatory after buys.
    A trace can abstain early; no policy optimality claim is certified.
    Call Env.validate() on the immutable evaluator-owned context before replay.
    """
    n = len(env.truth[0])
    require(type(hidden) is int and 0 <= hidden < n, 'hidden route')
    require(type(base_cap) is int and base_cap >= 0 and type(query_cap) is int and query_cap >= 0, 'caps')
    require(type(symbolic) is bool, 'symbolic flag')
    state, bought, history, terminal = (1 << n)-1, 0, {}, False
    for e in events:
        require(type(e) is dict and not terminal, 'event after terminal')
        kind = e.get('kind')
        require(type(e.get('remaining')) is int, 'mask type')
        if kind == 'buy':
            require(set(e) == {'kind', 'groups', 'remaining'}, 'buy fields')
            gs = e['groups']
            require(type(gs) is list and bool(gs), 'empty purchase')
            for j in gs:
                require(type(j) is int and 0 <= j < env.n_groups and not (bought >> j & 1), 'invalid/repeated purchase')
                bought |= 1 << j
            require(bought.bit_count() <= base_cap, 'base budget')
            for q, a in history.items():
                state = env.restrict(state, bought, q, a, symbolic)
        elif kind == 'observe':
            require(set(e) == {'kind', 'probe', 'reply', 'remaining'}, 'observe fields')
            q, a = e['probe'], e['reply']
            require(type(q) is int and 0 <= q < len(env.truth) and q not in history, 'invalid/repeated probe')
            require(type(a) is int and a == env.truth[q][hidden], 'unauthenticated reply')
            history[q] = a
            require(len(history) <= query_cap, 'query budget')
            state = env.restrict(state, bought, q, a, symbolic)
        elif kind == 'finish':
            require(set(e) == {'kind', 'claim', 'remaining'}, 'finish fields')
            expected = state.bit_length()-1 if state.bit_count() == 1 else None
            claim = e['claim']
            require((claim is None or type(claim) is int) and claim == expected, 'unsupported promotion or abstention')
            terminal = True
        else:
            raise ValueError('unknown event')
        require(state >> hidden & 1, 'true route lost')
        require(e['remaining'] == state, 'incorrect version set')
    require(terminal, 'missing terminal')
    return {'identified': state.bit_count() == 1, 'base_calls': bought.bit_count(),
            'queries': len(history), 'remaining': state.bit_count()}
