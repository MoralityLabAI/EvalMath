"""Exact one-time compression of observed certificate-catalog evidence."""
from functools import lru_cache
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path
import argparse
import hashlib
import json
import sys

import mic16_reference as ref

HERE = Path(__file__).resolve().parent
PRIMARY_ORDER = (0, 1, 2)
MODES = ("optimal_1", "optimal_2", "optimal_4", "optimal_8", "window_1", "window_2")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def raw_transitions(p, s, m, b, a):
    """All physically legal actions, including dominated information-free delays."""
    kind, i = p.actions[a]
    if kind != "probe" and (s >> i) & 1:
        return ()
    if kind == "compose" and s & p.d.supports[i] != p.d.supports[i]:
        return ()
    out = []
    for (ok, cost, signal), worlds in p.parts[a]:
        post = m & worlds
        if not post:
            continue
        if cost > b:
            return ()
        acquired = s | (1 << i) if ok and kind != "probe" else s
        reward = p.d.reward[i] if acquired != s else 0
        out.append((acquired, post, b - cost, reward))
    return tuple(out)


def best_partitions(values, max_codes=8):
    """Subset DP for an optimal deterministic partition into at most K cells."""
    full = len(values) - 1
    assert full and full & (full + 1) == 0

    @lru_cache(None)
    def solve(mask, k):
        if not mask:
            return 0, ()
        if k == 0:
            return None
        least = mask & -mask
        best = None
        cell = mask
        while cell:
            if cell & least:
                rest = solve(mask ^ cell, k - 1)
                if rest is not None:
                    value = values[cell] + rest[0]
                    cells = tuple(sorted((cell,) + rest[1]))
                    if best is None or value > best[0] or (
                        value == best[0] and (len(cells), cells) < (len(best[1]), best[1])
                    ):
                        best = value, cells
            cell = (cell - 1) & mask
        return best

    return {k: solve(full, k) for k in range(1, max_codes + 1)}


def window_partition(order, k):
    assert tuple(sorted(order)) == (0, 1, 2) and 0 <= k <= 3
    cells = {}
    for world in range(ref.WORLD):
        code = tuple((world >> bit) & 1 for bit in order[-k:]) if k else ()
        cells[code] = cells.get(code, 0) | (1 << world)
    return tuple(sorted(cells.values()))


def prefix_histories(p, order=PRIMARY_ORDER):
    histories = []
    for world in range(ref.WORLD):
        mask = ref.FULL
        path = []
        for bit in order:
            observation = p.observation("probe", bit, world)
            post = sum(1 << z for z in ref.bits(mask)
                       if p.observation("probe", bit, z) == observation)
            path.append(["probe", bit, list(observation), mask, post])
            mask = post
        assert mask == 1 << world
        histories.append(path)
    return histories


def rollout(p, world, budget, initial_mask):
    assert initial_mask & (1 << world)
    acquired = 0
    mask = initial_mask
    total = 0
    path = []
    while budget:
        action = p.policy("bayes", acquired, mask, budget)
        if action < 0:
            break
        kind, i = p.actions[action]
        observation = p.observation(kind, i, world)
        nxt = next(t for t in p.transitions(acquired, mask, budget, action)
                   if t[1] & (1 << world))
        q, post, remaining, reward = nxt
        path.append([kind, i, list(observation), mask, post])
        acquired, mask, budget = q, post, remaining
        total += reward
    return {"reward": total, "remaining": budget, "acquired": acquired,
            "posterior": mask, "initial_mask": initial_mask, "path": path}


def first_action_alias(p, values, budget, u, v):
    mask = (1 << u) | (1 << v)
    full_value = values[1 << u] + values[1 << v]
    common_value, common_action = 0, -1
    optimal_sets = {}
    for world in (u, v):
        scores = {-1: 0}
        for action in range(len(p.actions)):
            transitions = raw_transitions(p, 0, 1 << world, budget, action)
            if transitions:
                q, post, left, reward = transitions[0]
                scores[action] = p.mass[post] * reward + p.choice(q, post, left, left)[0]
        assert max(scores.values()) == values[1 << world]
        optimal_sets[str(world)] = sorted(a for a, value in scores.items()
                                          if value == values[1 << world])
    for action in range(len(p.actions)):
        if not raw_transitions(p, 0, mask, budget, action):
            continue
        value = 0
        for world in (u, v):
            q, post, left, reward = raw_transitions(p, 0, 1 << world, budget, action)[0]
            value += p.mass[post] * reward + p.choice(q, post, left, left)[0]
        if value > common_value:
            common_value, common_action = value, action
    assert 0 <= full_value - common_value <= full_value - values[mask]
    assert (common_value < full_value) == not_intersection(optimal_sets.values())
    return {"worlds": [u, v], "full_value": full_value,
            "common_first_value": common_value, "belief_value": values[mask],
            "common_first_action": common_action, "optimal_first_actions": optimal_sets,
            "shares_primary_window_1": (u >> 2) == (v >> 2),
            "shares_primary_window_2": ((u >> 1) & 3) == ((v >> 1) & 3)}


def not_intersection(sets):
    return not set.intersection(*(set(s) for s in sets))


def evaluate_root(family, seed, total_budget=12):
    assert total_budget > 3
    d = ref.make(family, seed)
    p = ref.Planner(d)
    budget = total_budget - 3
    values = [0] + [p.choice(0, mask, budget, budget)[0] for mask in range(1, 256)]
    optimum = best_partitions(values)
    full_value = sum(values[1 << world] for world in range(ref.WORLD))
    assert optimum[1][0] == values[ref.FULL]
    assert optimum[8][0] == full_value
    assert all(optimum[k][0] <= optimum[k + 1][0] for k in range(1, 8))
    optimal = {str(k): {"value": value, "partition": list(cells)}
               for k, (value, cells) in optimum.items()}
    windows = {}
    for order in permutations(range(3)):
        assert all(h[-1][-1] == 1 << w for w, h in enumerate(prefix_histories(p, order)))
        for k in (1, 2):
            partition = window_partition(order, k)
            value = sum(values[mask] for mask in partition)
            assert value <= optimum[2 ** k][0]
            windows[''.join(map(str, order)) + ':k' + str(k)] = {
                "value": value, "partition": list(partition)}
    trajectories = {}
    for mode in MODES:
        cells = (optimal[mode.split('_')[1]] if mode.startswith("optimal")
                 else windows["012:k" + mode.split('_')[1]])["partition"]
        paths = [rollout(p, world, budget, next(m for m in cells if m & (1 << world)))
                 for world in range(ref.WORLD)]
        assert sum(d.weights[w] * r["reward"] for w, r in enumerate(paths)) == sum(values[m] for m in cells)
        trajectories[mode] = paths
    pairs = [first_action_alias(p, values, budget, u, v) for u, v in combinations(range(8), 2)]
    result = {"family": family, "seed": seed, "total_budget": total_budget,
              "continuation_budget": budget, "prior": list(d.weights),
              "values": values, "full_value": full_value, "optimal": optimal,
              "windows": windows, "pair_aliasing": pairs,
              "prefix_histories": prefix_histories(p), "trajectories": trajectories,
              "minimum_lossless_codes": next(k for k in range(1, 9) if optimum[k][0] == full_value)}
    p.choice.cache_clear()
    return result


def summary(rows):
    n = len(rows)
    assert n
    means = {}
    for k in range(1, 9):
        means['optimal_' + str(k)] = str(sum((Fraction(r['optimal'][str(k)]['value'], r['full_value'])
                                             for r in rows), Fraction()) / n)
    for k in (1, 2):
        means['window_' + str(k)] = str(sum((Fraction(r['windows']['012:k' + str(k)]['value'], r['full_value'])
                                            for r in rows), Fraction()) / n)
    losses = [1 - Fraction(r['optimal']['2']['value'], r['full_value']) for r in rows]
    loss = sum(losses, Fraction()) / n
    hard = sum(g >= Fraction(1, 10) for g in losses)
    headroom = loss >= Fraction(1, 20) and Fraction(hard, n) >= Fraction(1, 5)
    minimum = {str(k): sum(r['minimum_lossless_codes'] == k for r in rows) for k in range(1, 9)}
    return {"roots": n, "mean_reward_ratio": means,
            "primary_mean_relative_loss": str(loss), "primary_hard_roots": hard,
            "headroom_gate": "PASS_FUTURE_DESIGN_ONLY" if headroom else "FAIL_NO_FITS",
            "minimum_lossless_codes_counts": minimum,
            "positive_alias_pairs": sum(p['full_value'] > p['common_first_value'] for r in rows for p in r['pair_aliasing']),
            "roots_with_positive_alias_pair": sum(any(p['full_value'] > p['common_first_value'] for p in r['pair_aliasing']) for r in rows),
            "roots_with_window_1_alias_pair": sum(any(p['full_value'] > p['common_first_value'] and p['shares_primary_window_1'] for p in r['pair_aliasing']) for r in rows),
            "root_count_is_not_certified_independent_units": True}


def run(phase):
    protocol = json.loads((HERE / 'protocol.json').read_text())
    assert digest(HERE / 'mic16_reference.py') == protocol['reference_sha256']
    first, last = protocol['pilot_seeds_inclusive' if phase == 'pilot' else 'development_seeds_inclusive']
    rows = []
    for family in protocol['families']:
        for seed in range(first, last + 1):
            rows.append(evaluate_root(family, seed, protocol['total_budget']))
        print(f'{phase}: {family} complete', file=sys.stderr, flush=True)
    return {"schema": "MIC-17/exact-handoff-compression/v1", "phase": phase,
            "protocol_sha256": digest(HERE / 'protocol.json'),
            "source_sha256": {name: digest(HERE / name) for name in ('mic17.py', 'mic16_reference.py')},
            "rows": rows, "summary": summary(rows)}


def preflight_input(pilot):
    groups = []
    for family in ref.FAMILIES:
        rows = [r for r in pilot['rows'] if r['family'] == family]
        effect = sum((1 - Fraction(r['optimal']['2']['value'], r['full_value']) for r in rows), Fraction()) / len(rows)
        groups.append({"unit_id": family, "paired_effect": str(effect), "sham_effects": ["0"]})
    return {"schema_version": 1, "experiment_id": "MIC-17-public-handoff-headroom",
            "independent_unit": "generator lineage (independence unverified)",
            "alpha": "1/20", "scientific_min_effect": "1/20", "target_effect": "1/10",
            "measurement_resolution": "0", "sham_quantile": "19/20", "sham_confidence": "19/20",
            "planned_comparisons": 1, "confirm_units_planned": 128,
            "pilot_from_development_only": True, "heldout_sealed": False,
            "units_independent": False, "pilot": groups}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('pilot', 'development'), default='development')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = run(args.phase)
    args.out.write_text(json.dumps(report, sort_keys=True, separators=(',', ':')) + '\n')
    if args.phase == 'pilot':
        (HERE / 'preflight_input.json').write_text(json.dumps(preflight_input(report), sort_keys=True, indent=2) + '\n')
    print(json.dumps(report['summary'], sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
