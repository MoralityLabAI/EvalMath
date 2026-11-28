import unittest
from fractions import Fraction as F
from itertools import product
from temporal import (WORLDS, PROBES, MODES, POLICIES, PASSIVE, INITIAL,
                      rows, simulate, posterior, predict, extend, rank, parity,
                      certificate, target_rank, options, goal_trace, value, receipt)


class TemporalTests(unittest.TestCase):
    def test_independent_transition_rows(self):
        for w, q, mode in product(WORLDS, PROBES, MODES):
            self.assertEqual(simulate(w, q, mode), tuple(parity(w & r) for r in rows(q, mode)))

    def test_passive_aliases(self):
        fibres = {}
        for w in WORLDS:
            fibres.setdefault(simulate(w, PASSIVE, "trajectory"), []).append(w)
        self.assertEqual(len(fibres), 4)
        self.assertEqual(rank(INITIAL), 2)
        self.assertEqual(target_rank(INITIAL), 0)
        for ws in fibres.values():
            self.assertEqual(len(ws), 16)
            self.assertEqual({w & 3 for w in ws}, {0,1,2,3})

    def test_rowspace_certificate_and_collision_oracle(self):
        for obs in product(range(2), repeat=2):
            h = [(PASSIVE, "trajectory", obs)]
            ws = posterior(h)
            for mode, q in product(MODES, PROBES):
                nxt = extend(INITIAL, rows(q, mode))
                d = rank(nxt) - rank(INITIAL)
                p = predict(ws, q, mode)
                self.assertEqual(len(p), 2**d)
                self.assertEqual(set(p.values()), {F(1,2**d)})
                self.assertEqual(1-sum(v*v for v in p.values()), 1-F(1,2**d))
                for o in p:
                    w2 = posterior(h + [(q, mode, o)])
                    targets = {w & 3 for w in w2}
                    self.assertEqual(len(targets), 2**(2-target_rank(nxt)))
                    self.assertEqual(certificate(nxt), len(targets)==1)

    def test_action_pulse_and_delayed_effect(self):
        # These two worlds differ only in whether action or exogenous u has
        # a delayed effect. Passive trajectories coincide.
        w, z = 2, 8
        self.assertEqual(simulate(w, PASSIVE, "trajectory"), simulate(z, PASSIVE, "trajectory"))
        self.assertEqual(simulate(w, (1,0), "trajectory"), (0,1))
        self.assertEqual(simulate(z, (1,0), "trajectory"), (0,0))
        self.assertTrue(certificate(extend(INITIAL, rows((1,0), "trajectory"))))
        self.assertFalse(certificate(extend(INITIAL, rows((1,0), "terminal"))))

    def test_exact_policy_order_and_budget(self):
        for mode in MODES:
            for policy in POLICIES:
                self.assertEqual(value(INITIAL, mode, 0, policy), 0)
                self.assertLessEqual(value(INITIAL, mode, 1, policy), value(INITIAL, mode, 2, policy))
                self.assertLessEqual(value(INITIAL, mode, 2, policy), value(INITIAL, mode, 2, "optimal"))
        self.assertEqual(value(INITIAL,"trajectory",1,"goal"), 1)
        self.assertEqual(value(INITIAL,"trajectory",1,"fixed"), 0)
        self.assertEqual(value(INITIAL,"trajectory",2,"fixed"), 1)
        self.assertEqual(value(INITIAL,"terminal",1,"optimal"), 0)
        self.assertEqual(value(INITIAL,"terminal",2,"goal"), 1)
        self.assertEqual(value(INITIAL,"terminal",2,"optimal"), 1)

    def test_independent_two_episode_goal_oracle(self):
        for w, mode in product(WORLDS, MODES):
            t = goal_trace(w, mode, 2)
            self.assertTrue(t["certified"])
            self.assertEqual(t["response"], w & 3)
            self.assertLessEqual(t["active_transitions"], 4)
            if mode == "terminal":
                self.assertEqual(t["active_transitions"], 4)

    def test_randomized_policy_against_independent_enumeration(self):
        # Independently use literal world-set partitions, with a fixed passive
        # observation. Certification counts are the same on all four fibres.
        ws = posterior([(PASSIVE,"trajectory",(0,0))])
        for mode in MODES:
            def brute(current, remaining, collision):
                if len({w & 3 for w in current}) == 1:
                    return F(1)
                if not remaining:
                    return F(0)
                arms = []
                for q in PROBES:
                    groups = {}
                    for w in current:
                        groups.setdefault(simulate(w,q,mode), []).append(w)
                    if len(groups)>1:
                        arms.append(groups)
                if not arms:
                    return F(0)
                if collision:
                    best = max(1-sum(F(len(g),len(current))**2 for g in x.values()) for x in arms)
                    arms = [x for x in arms if 1-sum(F(len(g),len(current))**2 for g in x.values())==best]
                return sum(sum(F(len(g),len(current))*brute(g,remaining-1,collision)
                               for g in x.values()) for x in arms)/len(arms)
            # One-episode independent enumeration. Two-episode goal checks above
            # separately exercise the multi-step oracle.
            for policy in ("uniform","collision"):
                self.assertEqual(value(INITIAL,mode,1,policy), brute(ws,1,policy=="collision"))

    def test_receipt(self):
        r = receipt()
        self.assertEqual(len(r["rows"]),384)
        self.assertEqual(r,receipt())


if __name__ == "__main__":
    unittest.main()
