"""Independent boundary and corruption checks for MIC-18's memory contract."""
from copy import deepcopy
from fractions import Fraction
from unittest import TestCase, main

import audit18 as audit
import finite_memory as production


def register(width, retained=None, task="query"):
    retained = width if retained is None else retained
    capacity = 2 ** retained
    transitions = [[[((state * 2) + bit) % capacity for bit in (0, 1)]
                    for state in range(capacity)] for _ in range(width)]
    if task == "query":
        outputs = [[((state // (2 ** (width - 1 - query))) % 2
                     if query >= width - retained else 0)
                    for query in range(width)] for state in range(capacity)]
    else:
        outputs = [[state % 2] for state in range(capacity)]
    return {"schema": "MIC-18/controller/v1", "name": "test-register", "task": task,
            "width": width, "capacity": capacity, "initial_state": 0,
            "transitions": transitions, "outputs": outputs}


def replay_report(controller):
    checked = audit.audit_controller(controller)
    return {"score": checked["score"], "total": checked["total"],
            "fraction": str(Fraction(checked["score"], checked["total"])),
            "state_maps": checked["state_maps"],
            "reachable_state_counts": [len(set(m)) for m in checked["state_maps"]],
            "observations": checked["verified_updates"],
            "paths": [{"word": path["word"], "observations": path["observations"],
                       "states": path["states"], "predictions": path["outputs"],
                       "targets": path["targets"]} for path in checked["paths"]]}


class TestFiniteMemoryContract(TestCase):
    def test_full_register_reconstruction_and_counting_bound(self):
        controller = register(4)
        checked = audit.audit_controller(controller)
        self.assertEqual((checked["score"], checked["total"]), (64, 64))
        self.assertEqual(audit.verify_injective_decoding(controller), 16)
        self.assertEqual([len(set(m)) for m in checked["state_maps"]], [1, 2, 4, 8, 16])

    def test_no_memory_has_no_hidden_last_observation_channel(self):
        controller = register(3, retained=0)
        checked = audit.audit_controller(controller)
        self.assertEqual((checked["score"], checked["total"]), (12, 24))
        self.assertTrue(all(path["states"] == [0, 0, 0, 0] for path in checked["paths"]))
        self.assertEqual(checked["paths"][0]["outputs"], checked["paths"][-1]["outputs"])
        leaked = deepcopy(controller)
        leaked["history"] = [0, 1, 1]
        with self.assertRaises(AssertionError):
            audit.audit_controller(leaked)
        with self.assertRaises((AssertionError, ValueError, TypeError)):
            production.evaluate(leaked)
        produced = production.evaluate(controller)
        self.assertEqual((produced["score"], produced["total"]), (12, 24))
        audit.check_evaluation(controller, produced)

    def test_corrupt_state_tables_and_decoder_are_rejected(self):
        original = register(2, retained=1)
        mutations = []
        bad = deepcopy(original)
        bad["transitions"][0][0][0] = 2
        mutations.append(bad)
        bad = deepcopy(original)
        bad["capacity"] = 1
        mutations.append(bad)
        bad = deepcopy(original)
        bad["outputs"][0][0] = True
        mutations.append(bad)
        bad = deepcopy(original)
        bad["outputs"][0].append(1)
        mutations.append(bad)
        bad = deepcopy(original)
        bad["initial_state"] = 1
        mutations.append(bad)
        bad = deepcopy(original)
        bad["width"] = True
        mutations.append(bad)
        for bad in mutations:
            with self.subTest(bad=bad):
                with self.assertRaises(AssertionError):
                    audit.audit_controller(bad)
                with self.assertRaises((AssertionError, ValueError, TypeError)):
                    production.evaluate(bad)

    def test_phasewise_small_codebooks_can_fail_online_update_closure(self):
        # Parity of the first two bits has only two labels. A final majority
        # label cannot be computed from that retained parity and the last bit.
        maps = [[0], [0, 1], [0, 1, 1, 0], [0, 0, 0, 1, 0, 1, 1, 1]]
        self.assertTrue(all(len(set(m)) <= 2 for m in maps))
        with self.assertRaises(AssertionError):
            audit.check_update_closure(maps, 2)

    def test_labeled_search_matches_hand_values_on_small_domain(self):
        self.assertEqual(audit.labeled_optimum(2, 1)["score"], 4)
        self.assertEqual(audit.labeled_optimum(2, 2)["score"], 6)
        self.assertEqual(audit.labeled_optimum(2, 4)["score"], 8)
        self.assertEqual(audit.labeled_optimum(2, 2, "parity")["score"], 4)
        self.assertEqual(audit.handoff_optimum(2, 2)["score"], 6)

    def test_labeled_search_exposes_the_three_observation_handoff_gap(self):
        online = audit.labeled_optimum(3, 2)
        handoff = audit.handoff_optimum(3, 2)
        self.assertEqual((online["score"], online["total"]), (17, 24))
        self.assertEqual((handoff["score"], handoff["total"]), (18, 24))
        self.assertGreater(handoff["score"], online["score"])

    def test_report_corruption_cannot_preserve_a_false_replay(self):
        controller = register(3, retained=1)
        original = replay_report(controller)
        audit.check_evaluation(controller, original)
        mutations = []
        bad = deepcopy(original)
        bad["paths"][3]["targets"][0] ^= 1
        mutations.append(bad)
        bad = deepcopy(original)
        bad["paths"] = bad["paths"][:-1]
        mutations.append(bad)
        bad = deepcopy(original)
        bad["reachable_state_counts"][-1] += 1
        mutations.append(bad)
        bad = deepcopy(original)
        bad["state_maps"][2][0] ^= 1
        mutations.append(bad)
        bad = deepcopy(original)
        bad["score"] += 1
        mutations.append(bad)
        bad = deepcopy(original)
        bad["observations"] -= 1
        mutations.append(bad)
        for bad in mutations:
            with self.subTest(report=bad):
                with self.assertRaises(AssertionError):
                    audit.check_evaluation(controller, bad)

    def test_public_phase_can_change_updates_and_queries_use_msb_order(self):
        controller = register(3, retained=1)
        # Retain the first observation by changing to identity updates later.
        controller["transitions"] = [[[0, 1], [0, 1]], [[0, 0], [1, 1]], [[0, 0], [1, 1]]]
        controller["outputs"] = [[0, 0, 0], [1, 0, 0]]
        checked = audit.check_evaluation(controller, production.evaluate(controller))
        self.assertEqual(checked["score"], 16)
        self.assertEqual(checked["state_maps"][-1], [0, 0, 0, 0, 1, 1, 1, 1])
        for path in checked["paths"]:
            self.assertEqual(path["outputs"][0], path["observations"][0])

    def test_production_compiler_agrees_with_labeled_search(self):
        for width, capacity, task in ((2, 1, "query"), (2, 2, "query"),
                                      (2, 4, "query"), (3, 2, "query"),
                                      (3, 2, "parity")):
            with self.subTest(width=width, capacity=capacity, task=task):
                result = production.compile_exact(width, capacity, task)
                checked = audit.check_evaluation(result["controller"],
                                                 production.evaluate(result["controller"]))
                oracle = audit.labeled_optimum(width, capacity, task)
                self.assertEqual(result["score"], oracle["score"])
                self.assertEqual(result["reachable_partition_counts"],
                                 oracle["reachable_partition_counts"])
                self.assertEqual(checked["score"], oracle["score"])

    def test_partition_guard_aborts_without_an_optimality_certificate(self):
        with self.assertRaises(production.SearchLimitExceeded):
            production.compile_exact(2, 2, max_partitions=1)
        boundary = production.compile_exact(1, 2, max_partitions=2)
        self.assertTrue(boundary["certified_optimal"])
        self.assertEqual(boundary["reachable_partition_counts"], [1, 2])
        constant = production.compile_exact(3, 1, max_partitions=1)
        self.assertEqual(constant["reachable_partition_counts"], [1, 1, 1, 1])


if __name__ == "__main__":
    main()
