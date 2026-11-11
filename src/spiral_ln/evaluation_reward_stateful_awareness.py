from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction as Q
from functools import lru_cache
from spiral_ln.evaluation_reward_training_awareness import _rational, _distribution
State = tuple[Q, Q, Q, Q]

def _state(values) -> State:
    try:
        v = tuple((_rational(x, 'hidden state mass') for x in values))
    except (TypeError, ValueError) as exc:
        raise ValueError('hidden state mass must be a four-component rational vector') from exc
    if len(v) != 4 or any((x < 0 for x in v)) or sum(v) > 1:
        raise ValueError('hidden state mass must be four nonnegative rationals of total at most one')
    return v

def _mass(b: State) -> Q:
    return sum(b, Q(0))

def _integrity_mass(b: State) -> Q:
    return b[1] + b[3]

def _tv(a, b) -> Q:
    return sum((abs(x - y) for x, y in zip(a, b)), Q(0)) / 2

@dataclass(frozen=True)
class IntegrityProbe:
    name: str
    outcomes: tuple[str, ...]
    kernel: tuple[tuple[tuple[Q, Q], ...], ...]
    cost: Q = Q(0)
    future_influence: Q = Q(0)

    def __post_init__(self):
        if type(self.name) is not str or not self.name:
            raise ValueError('probe requires a name')
        if type(self.outcomes) is not tuple or not self.outcomes or any((type(o) is not str or not o for o in self.outcomes)) or (len(set(self.outcomes)) != len(self.outcomes)):
            raise ValueError('probe outcomes must be unique nonempty strings')
        if len(self.kernel) != 4:
            raise ValueError('joint kernel must have four previous hidden states')
        kernel = []
        for row in self.kernel:
            if len(row) != len(self.outcomes):
                raise ValueError('joint kernel outcome dimensions disagree')
            newrow = []
            for pair in row:
                if len(pair) != 2:
                    raise ValueError('joint kernel next integrity must be binary')
                newrow.append(tuple((_rational(x, 'kernel probability') for x in pair)))
            if any((x < 0 or x > 1 for pair in newrow for x in pair)) or sum((x for pair in newrow for x in pair), Q(0)) != 1:
                raise ValueError('joint kernel rows must be normalized probabilities')
            kernel.append(tuple(newrow))
        c = _rational(self.cost, 'probe cost')
        f = _rational(self.future_influence, 'probe future influence')
        if c < 0:
            raise ValueError('probe cost must be nonnegative')
        object.__setattr__(self, 'kernel', tuple(kernel))
        object.__setattr__(self, 'cost', c)
        object.__setattr__(self, 'future_influence', f)

    def observed_law(self, world: int, integrity: int) -> tuple[Q, ...]:
        if type(world) is not int or world not in (0, 1) or type(integrity) is not int or (integrity not in (0, 1)):
            raise ValueError('world/integrity index must be binary')
        return tuple((sum(pair, Q(0)) for pair in self.kernel[2 * world + integrity]))

    def conditional_world_tv(self) -> Q:
        return max((_tv(tuple((x for pair in self.kernel[i] for x in pair)), tuple((x for pair in self.kernel[i + 2] for x in pair))) for i in range(2)), default=Q(0))

def memoryless_probe(name: str, outcomes: tuple[str, ...], evaluation: tuple[Q, ...], deployment: tuple[Q, ...], *, cost: Q=Q(0), future_influence: Q=Q(0)) -> IntegrityProbe:
    e = _distribution(evaluation, 'evaluation probe law')
    d = _distribution(deployment, 'deployment probe law')
    if len(e) != len(outcomes) or len(d) != len(outcomes):
        raise ValueError('outcome roster and probability dimensions disagree')
    rows = []
    for w in range(2):
        probs = e if w == 0 else d
        for i in range(2):
            rows.append(tuple((tuple((p if j == i else Q(0) for j in range(2))) for p in probs)))
    return IntegrityProbe(name, outcomes, tuple(rows), cost, future_influence)

@dataclass(frozen=True)
class StatefulAwarenessGame:
    prior_evaluation: Q
    protect_reward: Q
    exploit_gain: Q
    compromised_proxy_bonus: Q
    horizon: int
    probes: tuple[IntegrityProbe, ...]
    initial_integrity_e: tuple[Q, Q] = (Q(1), Q(0))
    initial_integrity_d: tuple[Q, Q] = (Q(1), Q(0))
    terminal_future_delta: Q = Q(0)
    max_states: int = 40000

    def __post_init__(self):
        p = _rational(self.prior_evaluation, 'prior')
        r = _rational(self.protect_reward, 'reward')
        g = _rational(self.exploit_gain, 'gain')
        b = _rational(self.compromised_proxy_bonus, 'proxy bonus')
        f = _rational(self.terminal_future_delta, 'future delta')
        if not Q(0) <= p <= Q(1) or r <= 0 or g <= 0 or (b < 0):
            raise ValueError('invalid world prior or terminal subjective utilities')
        if type(self.horizon) is not int or not 0 <= self.horizon <= 8:
            raise ValueError('horizon must be an integer between zero and eight')
        if type(self.max_states) is not int or self.max_states <= 0:
            raise ValueError('state cap must be positive integer')
        if type(self.probes) is not tuple or any((not isinstance(a, IntegrityProbe) for a in self.probes)):
            raise ValueError('probes must be a tuple of registered IntegrityProbe objects')
        if len(set((a.name for a in self.probes))) != len(self.probes):
            raise ValueError('probe names must be distinct')
        ie = _distribution(self.initial_integrity_e, 'evaluation initial integrity')
        id_ = _distribution(self.initial_integrity_d, 'deployment initial integrity')
        if len(ie) != 2 or len(id_) != 2:
            raise ValueError('initial integrity is binary')
        for name, value in (('prior_evaluation', p), ('protect_reward', r), ('exploit_gain', g), ('compromised_proxy_bonus', b), ('terminal_future_delta', f), ('initial_integrity_e', ie), ('initial_integrity_d', id_)):
            object.__setattr__(self, name, value)

    def initial_belief(self) -> State:
        p = self.prior_evaluation
        return (p * self.initial_integrity_e[0], p * self.initial_integrity_e[1], (1 - p) * self.initial_integrity_d[0], (1 - p) * self.initial_integrity_d[1])

    def projection_closed(self) -> bool:
        if self.compromised_proxy_bonus:
            return False
        return all((a.observed_law(w, 0) == a.observed_law(w, 1) for a in self.probes for w in range(2)))

def posterior(b) -> tuple[Q | None, Q | None]:
    b = _state(b)
    n = _mass(b)
    return ((b[0] + b[1]) / n, _integrity_mass(b) / n) if n else (None, None)

def step(b, probe: IntegrityProbe, outcome_index: int) -> State:
    b = _state(b)
    if not isinstance(probe, IntegrityProbe) or type(outcome_index) is not int or (not 0 <= outcome_index < len(probe.outcomes)):
        raise ValueError('unknown probe or observation index')
    out = [Q(0)] * 4
    for w in range(2):
        for i in range(2):
            for j in range(2):
                out[2 * w + j] += b[2 * w + i] * probe.kernel[2 * w + i][outcome_index][j]
    return tuple(out)

def terminal_values(game: StatefulAwarenessGame, b: State) -> tuple[Q, Q]:
    return ((b[0] + b[1]) * game.protect_reward + _mass(b) * game.terminal_future_delta, (b[2] + b[3]) * game.exploit_gain + _integrity_mass(b) * game.compromised_proxy_bonus)

@dataclass(frozen=True)
class PolicyNode:
    action: str
    probe_index: int | None = None
    children: tuple['PolicyNode', ...] = ()
PROTECT = PolicyNode('protect')
EXPLOIT = PolicyNode('exploit')

@dataclass(frozen=True)
class OptimalPolicy:
    root: PolicyNode
    value: Q
    belief_states: int

def optimize(game: StatefulAwarenessGame) -> OptimalPolicy:
    count = 0

    @lru_cache(maxsize=None)
    def best(h: int, b: State):
        nonlocal count
        count += 1
        if count > game.max_states:
            raise ValueError('belief-state cap exceeded')
        c, x = terminal_values(game, b)
        value, node = (c, PROTECT) if c > x else (x, EXPLOIT)
        if h:
            for i, a in enumerate(game.probes):
                children = tuple((best(h - 1, step(b, a, j)) for j in range(len(a.outcomes))))
                trial = _mass(b) * (a.future_influence - a.cost) + sum((val for val, _ in children), Q(0))
                if trial > value:
                    value, node = (trial, PolicyNode('probe', i, tuple((n for _, n in children))))
        return (value, node)
    value, root = best(game.horizon, game.initial_belief())
    return OptimalPolicy(root, value, count)

@dataclass(frozen=True)
class TerminalTrace:
    history: tuple[tuple[int, int], ...]
    terminal_action: str
    evaluation_probability: Q
    deployment_probability: Q
    evaluation_compromised: Q
    deployment_compromised: Q
    accumulated_net_cost: Q

def terminal_traces(game: StatefulAwarenessGame, root: PolicyNode) -> tuple[TerminalTrace, ...]:
    if not isinstance(root, PolicyNode):
        raise ValueError('policy root must be typed')
    e_start = (game.initial_integrity_e[0], game.initial_integrity_e[1], Q(0), Q(0))
    d_start = (Q(0), Q(0), game.initial_integrity_d[0], game.initial_integrity_d[1])
    traces = []

    def visit(node, b_e, b_d, h, history, net_cost):
        if node.action in ('protect', 'exploit'):
            if node.probe_index is not None or node.children:
                raise ValueError('terminal actions cannot have children')
            traces.append(TerminalTrace(history, node.action, _mass(b_e), _mass(b_d), b_e[1], b_d[3], net_cost))
            return
        if node.action != 'probe' or h <= 0:
            raise ValueError('unknown policy action or probe beyond horizon')
        i = node.probe_index
        if type(i) is not int or not 0 <= i < len(game.probes):
            raise ValueError('unregistered probe index')
        a = game.probes[i]
        if len(node.children) != len(a.outcomes):
            raise ValueError('probe branch count differs from registered outcomes')
        for j, child in enumerate(node.children):
            visit(child, step(b_e, a, j), step(b_d, a, j), h - 1, history + ((i, j),), net_cost + a.cost - a.future_influence)
    visit(root, e_start, d_start, game.horizon, (), Q(0))
    if sum((t.evaluation_probability for t in traces), Q(0)) != 1 or sum((t.deployment_probability for t in traces), Q(0)) != 1:
        raise AssertionError('a valid policy must have normalized terminal transcript laws')
    return tuple(traces)

@dataclass(frozen=True)
class StatefulCertificate:
    subjective_value: Q
    evaluation_protection: Q
    deployment_protection: Q
    evaluation_exploit_compromised: Q
    deployment_exploit_compromised: Q
    transcript_tv: Q
    initial_integrity_tv: Q
    conditional_joint_tv_cap: Q
    adaptive_tv_bound: Q
    deployment_protection_floor: Q
    evaluation_expected_probes: Q
    deployment_expected_probes: Q
    terminal_transcripts: int

def certify(game: StatefulAwarenessGame, root: PolicyNode) -> StatefulCertificate:
    traces = terminal_traces(game, root)
    pe = sum((t.evaluation_probability for t in traces if t.terminal_action == 'protect'), Q(0))
    pd = sum((t.deployment_probability for t in traces if t.terminal_action == 'protect'), Q(0))
    ce = sum((t.evaluation_compromised for t in traces if t.terminal_action == 'exploit'), Q(0))
    cd = sum((t.deployment_compromised for t in traces if t.terminal_action == 'exploit'), Q(0))
    tv = _tv(tuple((t.evaluation_probability for t in traces)), tuple((t.deployment_probability for t in traces)))
    initial_tv = _tv(game.initial_integrity_e, game.initial_integrity_d)
    eps = max((a.conditional_world_tv() for a in game.probes), default=Q(0))
    bound = 1 - (1 - initial_tv) * (1 - eps) ** game.horizon
    if abs(pe - pd) > tv or tv > bound:
        raise AssertionError('adaptive hidden-state transcript TV exceeds coupling certificate')
    value = Q(0)
    for t in traces:
        m = game.prior_evaluation * t.evaluation_probability + (1 - game.prior_evaluation) * t.deployment_probability
        if t.terminal_action == 'protect':
            value += game.prior_evaluation * t.evaluation_probability * game.protect_reward
            value += m * game.terminal_future_delta
        else:
            value += (1 - game.prior_evaluation) * t.deployment_probability * game.exploit_gain
            value += (game.prior_evaluation * t.evaluation_compromised + (1 - game.prior_evaluation) * t.deployment_compromised) * game.compromised_proxy_bonus
        value -= m * t.accumulated_net_cost
    expected_e = sum((len(t.history) * t.evaluation_probability for t in traces), Q(0))
    expected_d = sum((len(t.history) * t.deployment_probability for t in traces), Q(0))
    return StatefulCertificate(value, pe, pd, ce, cd, tv, initial_tv, eps, bound, max(Q(0), pe - tv), expected_e, expected_d, len(traces))

def sharp_relabel(game: StatefulAwarenessGame, root: PolicyNode) -> PolicyNode:
    traces = terminal_traces(game, root)
    maximize = {t.history: t.evaluation_probability > t.deployment_probability for t in traces}

    def walk(node, history):
        if node.action in ('protect', 'exploit'):
            return PROTECT if maximize[history] else EXPLOIT
        return PolicyNode('probe', node.probe_index, tuple((walk(child, history + ((node.probe_index, j),)) for j, child in enumerate(node.children))))
    return walk(root, ())

def visible_trace_distance(game_a: StatefulAwarenessGame, game_b: StatefulAwarenessGame, root: PolicyNode) -> Q:
    if len(game_a.probes) != len(game_b.probes) or any((a.name != b.name or a.outcomes != b.outcomes for a, b in zip(game_a.probes, game_b.probes))):
        raise ValueError('comparison games must share action/outcome grammar')
    aa = terminal_traces(game_a, root)
    bb = terminal_traces(game_b, root)
    if tuple(((t.history, t.terminal_action) for t in aa)) != tuple(((t.history, t.terminal_action) for t in bb)):
        raise AssertionError('fixed policy must have identical public transcript keys')
    return max(_tv(tuple((getattr(t, 'evaluation_probability') for t in aa)), tuple((getattr(t, 'evaluation_probability') for t in bb))), _tv(tuple((getattr(t, 'deployment_probability') for t in aa)), tuple((getattr(t, 'deployment_probability') for t in bb))))

def uniform_public_equivalence(game_a: StatefulAwarenessGame, game_b: StatefulAwarenessGame) -> bool:
    if len(game_a.probes) != len(game_b.probes) or any((a.name != b.name or a.outcomes != b.outcomes for a, b in zip(game_a.probes, game_b.probes))):
        raise ValueError('comparison games must share action/outcome grammar')
    return all((a.observed_law(w, i) == a.observed_law(w, 0) == b.observed_law(w, j) for a, b in zip(game_a.probes, game_b.probes) for w in range(2) for i in range(2) for j in range(2)))
