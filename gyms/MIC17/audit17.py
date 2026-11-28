"""Independent finite audit of MIC-17's one-time memory handoff.

The environment generator is shared with the pinned MIC-16 reference. Bellman
enumeration, partition enumeration, history reconstruction, and receipt replay
are implemented here without using mic17 or the reference Planner.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations
from pathlib import Path
import argparse
import hashlib
import json
import sys

import mic16_reference as ref


REFERENCE_SHA256 = "350d22fe4ed8f0a769bfec2ea40a3447a1b1cc09f2c385777448f30ea36f8190"
FAMILIES = ("local", "shared", "parity", "mixed")
ACTIONS = tuple((k, i) for k in ("direct", "cached") for i in range(7)) + tuple(
    ("compose", i) for i in range(3, 7)
) + tuple(("probe", i) for i in range(3))


def worlds_from_mask(mask):
    return tuple(w for w in range(8) if mask // (2 ** w) % 2)


def world_mask(worlds):
    return sum(2 ** w for w in worlds)


def observation(d, action, world):
    kind, i = action
    if kind == "probe":
        assert 0 <= i < 3
        return False, 1, (world // (2 ** i)) % 2
    assert 0 <= i < 7
    if kind == "cached":
        success, cost = d.catalog[i][world]
        return bool(success), cost, -1
    if kind == "direct":
        return True, sum(len(row) for j, row in enumerate(d.entries)
                         if d.supports[i] // (2 ** j) % 2), -1
    assert kind == "compose" and i >= 3
    return True, 1 + sum(d.supports[i] // (2 ** j) % 2 for j in range(3)) // 2, -1


def structurally_legal(d, acquired, action):
    kind, i = action
    if kind == "probe":
        return 0 <= i < 3
    if not 0 <= i < 7 or i in acquired:
        return False
    return kind != "compose" or (i >= 3 and all(
        j in acquired for j in range(3) if d.supports[i] // (2 ** j) % 2
    ))


def independent_oracle(d):
    """Return a tuple/frozenset Bellman solver and its action-value function.

    All physically legal actions are retained, including known failed checks
    and redundant probes. Positive costs make the recursion finite. This also
    prevents a pruned action from disappearing from a first-action tie.
    """
    observations = {a: tuple(observation(d, a, w) for w in range(8)) for a in ACTIONS}

    @lru_cache(None)
    def groups(worlds, action):
        split = defaultdict(list)
        for world in worlds:
            split[observations[action][world]].append(world)
        return tuple((obs, tuple(sub)) for obs, sub in sorted(split.items()))

    @lru_cache(None)
    def value(acquired, worlds, budget):
        if budget <= 0:
            return 0
        best = 0
        for action in ACTIONS:
            q = action_value(acquired, worlds, budget, action)
            if q is not None:
                best = max(best, q)
        return best

    def action_value(acquired, worlds, budget, action):
        if not structurally_legal(d, acquired, action):
            return None
        parts = groups(worlds, action)
        if any(obs[1] > budget for obs, _ in parts):
            return None
        result = 0
        for (success, cost, _), sub in parts:
            new = acquired | {action[1]} if success else acquired
            reward = d.reward[action[1]] if success else 0
            result += sum(d.weights[w] for w in sub) * reward
            result += value(new, sub, budget - cost)
        return result

    return value, action_value


@lru_cache(None)
def all_partitions(n):
    """Enumerate unordered partitions using restricted growth, not subset DP."""
    if n == 0:
        return ((),)
    result = []
    groups = [1]

    def visit(world):
        if world == n:
            result.append(tuple(groups))
            return
        bit = 2 ** world
        for j in range(len(groups)):
            groups[j] += bit
            visit(world + 1)
            groups[j] -= bit
        groups.append(bit)
        visit(world + 1)
        groups.pop()

    visit(1)
    return tuple(result)


def partition_optima(values):
    n = (len(values) - 1).bit_length()
    assert len(values) == 2 ** n
    best = [None] * (n + 1)
    best[0] = 0 if n == 0 else None
    for partition in all_partitions(n):
        score = sum(values[cell] for cell in partition)
        for cap in range(len(partition), n + 1):
            if best[cap] is None or score > best[cap]:
                best[cap] = score
    return best


def validate_partition(partition, max_codes=8):
    assert 1 <= len(partition) <= max_codes
    covered = set()
    for mask in partition:
        assert type(mask) is int and 1 <= mask <= 255
        cell = set(worlds_from_mask(mask))
        assert not covered.intersection(cell)
        covered.update(cell)
    assert covered == set(range(8))


def suffix_partition(order, length):
    assert sorted(order) == [0, 1, 2] and 0 <= length <= 3
    if length == 0:
        return (255,)
    cells = defaultdict(list)
    for world in range(8):
        key = tuple((world // (2 ** bit)) % 2 for bit in order[-length:])
        cells[key].append(world)
    return tuple(sorted(world_mask(cell) for cell in cells.values()))


def check_prefix(histories, total_budget):
    assert len(histories) == 8
    for world, history in enumerate(histories):
        assert len(history) == 3
        possible = set(range(8))
        budget = total_budget
        for bit, step in enumerate(history):
            kind, i, obs, prior, posterior = step
            assert (kind, i) == ("probe", bit)
            assert prior == world_mask(possible)
            expected = (False, 1, (world // (2 ** bit)) % 2)
            assert tuple(obs) == expected
            possible = {w for w in possible if (w // (2 ** bit)) % 2 == expected[2]}
            assert posterior == world_mask(possible)
            budget -= 1
        assert possible == {world} and budget == total_budget - 3
    # All orders have the same final sufficient statistic and fixed cost.
    for order in permutations(range(3)):
        for world in range(8):
            possible = set(range(8))
            for bit in order:
                signal = (world // (2 ** bit)) % 2
                possible = {w for w in possible if (w // (2 ** bit)) % 2 == signal}
            assert possible == {world}
    return 8 * 6


def check_receipt(d, world, budget, partition, receipt, oracle=None, choices=None):
    """Replay after the declared erasure boundary, including Bayes optimality."""
    validate_partition(partition)
    cell = next(mask for mask in partition if world in worlds_from_mask(mask))
    assert receipt["initial_mask"] == cell
    possible = set(worlds_from_mask(cell))
    acquired = frozenset()
    reward = 0
    if choices is None:
        choices = {}
    if oracle is None:
        oracle = independent_oracle(d)
    value, action_value = oracle
    for kind, i, obs, prior, posterior in receipt["path"]:
        action = (kind, i)
        assert action in ACTIONS and structurally_legal(d, acquired, action)
        state = acquired, tuple(sorted(possible)), budget
        assert choices.setdefault(state, action) == action
        assert prior == world_mask(possible) and world in possible
        assert max(observation(d, action, w)[1] for w in possible) <= budget
        assert action_value(*state, action) == value(*state)
        expected = observation(d, action, world)
        assert tuple(obs) == expected
        success, cost, _ = expected
        possible = {w for w in possible if observation(d, action, w) == expected}
        assert posterior == world_mask(possible) and world in possible
        budget -= cost
        if success:
            entries = [entry for group, row in enumerate(d.entries)
                       if d.supports[i] // (2 ** group) % 2 for entry in row]
            bound_improvement = 10 * len(entries) - sum(entries)
            if i >= 3:
                assert bound_improvement > 0
                assert d.reward[i] % bound_improvement == 0
                assert 1 <= d.reward[i] // bound_improvement <= 4
            else:
                assert d.reward[i] == 0
            acquired |= {i}
            reward += d.reward[i]
    state = acquired, tuple(sorted(possible)), budget
    assert choices.setdefault(state, None) is None
    assert value(*state) == 0
    assert receipt["reward"] == reward
    assert receipt["remaining"] == budget
    assert receipt["acquired"] == sum(2 ** i for i in acquired)
    assert receipt["posterior"] == world_mask(possible)
    return reward


def pair_alias_values(d, pair, budget, oracle):
    value, action_value = oracle
    acquired = frozenset()
    full = sum(value(acquired, (w,), budget) for w in pair)
    choices = {-1: 0}
    for index, action in enumerate(ACTIONS):
        values = [action_value(acquired, (w,), budget, action) for w in pair]
        if all(v is not None for v in values):
            choices[index] = sum(values)
    best = max(choices.values())
    belief = value(acquired, tuple(pair), budget)
    assert 0 <= full - best <= full - belief
    return full, best, belief, choices


def audit_root(row):
    assert row["family"] in FAMILIES
    d = ref.make(row["family"], row["seed"])
    assert list(d.weights) == row["prior"]
    assert row["total_budget"] == 12
    budget = row["continuation_budget"]
    assert budget == row["total_budget"] - 3 == 9
    assert len(row["values"]) == 256 and row["values"][0] == 0
    oracle = independent_oracle(d)
    value, _ = oracle
    values = [0] + [value(frozenset(), worlds_from_mask(mask), budget)
                    for mask in range(1, 256)]
    assert values == row["values"]
    best = partition_optima(values)
    assert len(all_partitions(8)) == 4140
    full = sum(values[2 ** w] for w in range(8))
    assert row["full_value"] == full
    assert best[1] == values[255] and best[8] == full
    assert all(best[k] <= best[k + 1] for k in range(1, 8))
    assert set(row["optimal"]) == {str(k) for k in range(1, 9)}
    for k in range(1, 9):
        reported = row["optimal"][str(k)]
        validate_partition(reported["partition"], k)
        assert reported["value"] == sum(values[cell] for cell in reported["partition"])
        assert reported["value"] == best[k]
    expected_window_keys = set()
    for order in permutations(range(3)):
        for length in (1, 2):
            key = "".join(map(str, order)) + ":k" + str(length)
            expected_window_keys.add(key)
            expected = suffix_partition(order, length)
            reported = row["windows"][key]
            assert tuple(sorted(reported["partition"])) == expected
            assert reported["value"] == sum(values[cell] for cell in expected)
            assert reported["value"] <= best[2 ** length]
    assert set(row["windows"]) == expected_window_keys
    order_checks = check_prefix(row["prefix_histories"], row["total_budget"])
    expected_modes = {"optimal_1", "optimal_2", "optimal_4", "optimal_8", "window_1", "window_2"}
    assert set(row["trajectories"]) == expected_modes
    trajectory_count = state_count = step_count = 0
    for mode, receipts in row["trajectories"].items():
        assert len(receipts) == 8
        kind, count = mode.split("_")
        entry = row["optimal"][count] if kind == "optimal" else row["windows"]["012:k" + count]
        partition = entry["partition"]
        choices = {}
        score = 0
        for world, receipt in enumerate(receipts):
            score += d.weights[world] * check_receipt(d, world, budget, partition, receipt, oracle, choices)
            trajectory_count += 1
            step_count += len(receipt["path"])
        assert score == entry["value"]
        state_count += len(choices)
    seen_pairs = set()
    positive_pairs = shared_suffix_pairs = 0
    for reported in row["pair_aliasing"]:
        pair = tuple(reported["worlds"])
        assert len(pair) == 2 and tuple(sorted(pair)) == pair and pair not in seen_pairs
        assert pair in set(combinations(range(8), 2))
        seen_pairs.add(pair)
        full_pair, common, belief, action_values = pair_alias_values(d, pair, budget, oracle)
        assert reported["full_value"] == full_pair
        assert reported["common_first_value"] == common
        assert reported["belief_value"] == belief
        assert action_values[reported["common_first_action"]] == common
        assert set(reported["optimal_first_actions"]) == {str(w) for w in pair}
        optimal_sets = []
        for world in pair:
            single = {-1: 0}
            for index, action in enumerate(ACTIONS):
                q = oracle[1](frozenset(), (world,), budget, action)
                if q is not None:
                    single[index] = q
            best_single = value(frozenset(), (world,), budget)
            optimal = sorted(index for index, score in single.items() if score == best_single)
            assert reported["optimal_first_actions"][str(world)] == optimal
            optimal_sets.append(set(optimal))
        assert (full_pair > common) == (not optimal_sets[0].intersection(optimal_sets[1]))
        assert reported["shares_primary_window_1"] == (pair[0] // 4 == pair[1] // 4)
        assert reported["shares_primary_window_2"] == (pair[0] // 2 == pair[1] // 2)
        positive_pairs += full_pair > common
        shared_suffix_pairs += full_pair > common and pair[0] // 4 == pair[1] // 4
    assert seen_pairs == set(combinations(range(8), 2))
    minimum_codes = next(k for k in range(1, 9) if best[k] == full)
    assert row["minimum_lossless_codes"] == minimum_codes
    return dict(family=row["family"], seed=row["seed"], full_value=full,
                optimal_two_value=best[2], two_code_relative_regret=str(Fraction(full - best[2], full)),
                minimum_lossless_codes=minimum_codes, verified_mask_values=255,
                enumerated_partitions=4140, verified_capacity_optima=8,
                verified_windows=12, verified_trajectories=trajectory_count,
                nonanticipation_state_checks=state_count, verified_steps=step_count,
                probe_order_identity_checks=order_checks, pair_alias_checks=28,
                positive_pair_aliases=positive_pairs, positive_last_bit_aliases=shared_suffix_pairs,
                independent_bellman_states=value.cache_info().currsize)


def audit(raw):
    assert hashlib.sha256(Path(ref.__file__).read_bytes()).hexdigest() == REFERENCE_SHA256
    here = Path(__file__).resolve().parent
    protocol_bytes = (here / "protocol.json").read_bytes()
    protocol = json.loads(protocol_bytes)
    assert raw["schema"] == "MIC-17/exact-handoff-compression/v1"
    assert raw["phase"] in ("pilot", "development")
    assert raw["protocol_sha256"] == hashlib.sha256(protocol_bytes).hexdigest()
    assert set(raw["source_sha256"]) == {"mic17.py", "mic16_reference.py"}
    for name, digest in raw["source_sha256"].items():
        assert digest == hashlib.sha256((here / name).read_bytes()).hexdigest()
    seed_key = "pilot_seeds_inclusive" if raw["phase"] == "pilot" else "development_seeds_inclusive"
    first, last = protocol[seed_key]
    expected_roots = {(family, seed) for family in FAMILIES for seed in range(first, last + 1)}
    rows = []
    seen = set()
    for row in raw["rows"]:
        key = row["family"], row["seed"]
        assert key not in seen
        seen.add(key)
        rows.append(audit_root(row))
        print("audited", *key, file=sys.stderr, flush=True)
    assert rows
    assert seen == expected_roots
    counts = {key: sum(row[key] for row in rows) for key in (
        "verified_mask_values", "enumerated_partitions", "verified_capacity_optima",
        "verified_windows", "verified_trajectories", "nonanticipation_state_checks",
        "verified_steps", "probe_order_identity_checks", "pair_alias_checks",
        "positive_pair_aliases", "positive_last_bit_aliases", "independent_bellman_states")}
    regrets = [Fraction(row["two_code_relative_regret"]) for row in rows]
    mean_regret = sum(regrets, Fraction()) / len(regrets)
    hard = sum(x >= Fraction(1, 10) for x in regrets)
    gate = mean_regret >= Fraction(1, 20) and Fraction(hard, len(rows)) >= Fraction(1, 5)
    verdict = "PASS_FUTURE_DESIGN_ONLY" if gate else "FAIL_NO_FITS"
    summary = raw["summary"]
    assert summary["roots"] == len(rows)
    assert Fraction(summary["primary_mean_relative_loss"]) == mean_regret
    assert summary["primary_hard_roots"] == hard and summary["headroom_gate"] == verdict
    assert summary["root_count_is_not_certified_independent_units"] is True
    assert summary["positive_alias_pairs"] == counts["positive_pair_aliases"]
    assert summary["roots_with_positive_alias_pair"] == sum(row["positive_pair_aliases"] > 0 for row in rows)
    assert summary["roots_with_window_1_alias_pair"] == sum(row["positive_last_bit_aliases"] > 0 for row in rows)
    assert summary["minimum_lossless_codes_counts"] == {
        str(k): sum(row["minimum_lossless_codes"] == k for row in rows) for k in range(1, 9)
    }
    expected_ratios = {}
    for k in range(1, 9):
        expected_ratios["optimal_" + str(k)] = sum(
            (Fraction(row["optimal"][str(k)]["value"], row["full_value"]) for row in raw["rows"]), Fraction()
        ) / len(rows)
    for k in (1, 2):
        expected_ratios["window_" + str(k)] = sum(
            (Fraction(row["windows"]["012:k" + str(k)]["value"], row["full_value"]) for row in raw["rows"]), Fraction()
        ) / len(rows)
    assert {key: Fraction(val) for key, val in summary["mean_reward_ratio"].items()} == expected_ratios
    return dict(schema="MIC-17/independent-handoff-audit/v1", roots=len(rows),
                counts=counts, rows=rows, mean_two_code_relative_regret=str(mean_regret),
                hard_roots=hard, headroom_gate=verdict,
                minimum_lossless_code_histogram=dict(sorted(Counter(row["minimum_lossless_codes"] for row in rows).items())),
                evidence="exact finite synthetic domain; no independence or neural claim",
                audit_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                reference_sha256=REFERENCE_SHA256)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("results.json"))
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("audit_results.json"))
    args = parser.parse_args()
    contents = args.input.read_bytes()
    report = audit(json.loads(contents))
    report["input_sha256"] = hashlib.sha256(contents).hexdigest()
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: val for key, val in report.items() if key != "rows"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
