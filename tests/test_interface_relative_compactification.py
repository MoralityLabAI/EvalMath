"""Independent exact cases for IRC-02 proposed repository module."""
import unittest
import random
from fractions import Fraction as F
from spiral_ln.interface_relative_compactification import (Machine, Branch, normalize, feedback_machine, switch_machine,
                       predictive_signature, independent_cylinder_law, expected_value,
                       class_count, shortest_distinguishing_cylinder, direct_world_cylinders, successors, witnessing_policy)


class IRC02(unittest.TestCase):
    def test_rational_bayes_and_timing(self):
        m=feedback_machine()
        b=(F(1,2),F(1,2))
        self.assertEqual(expected_value(m,b,"q",0),F(0))
        self.assertEqual(expected_value(m,b,"q",1),F(1,2))
        self.assertEqual(expected_value(m,b,"q",2),F(3,4))
        self.assertEqual(expected_value(m,b,"q",3),F(3,4))
        obs=successors(m,b,"q",2,"probe")
        self.assertEqual({e[0]:post for e,p,post in obs},{"y0":(F(3,4),F(1,4)),"y1":(F(1,4),F(3,4))})

    def test_same_optimal_value_distinct_future_test(self):
        m=feedback_machine()
        hi=(F(1,4),F(3,4));lo=(F(3,4),F(1,4))
        self.assertEqual(expected_value(m,hi,"q",1),F(3,4))
        self.assertEqual(expected_value(m,lo,"q",1),F(3,4))
        self.assertNotEqual(predictive_signature(m,hi,"q",1),predictive_signature(m,lo,"q",1))
        self.assertIsNotNone(shortest_distinguishing_cylinder(m,hi,lo,"q",1))

    def test_countdown_changes_quotient(self):
        m=feedback_machine()
        bs=tuple((F(1)-p,p) for p in (F(0),F(1,4),F(1,2),F(3,4),F(1)))
        self.assertEqual(class_count(m,bs,"q",0),1)
        self.assertEqual(class_count(m,bs,"q",1),5)
        self.assertEqual(class_count(m,bs,"q",2),5)
        self.assertEqual(shortest_distinguishing_cylinder(m,bs[0],bs[0],"q",2),None)

    def test_public_camera_mode_and_latency(self):
        m=switch_machine(); b=(F(1),)
        self.assertEqual(expected_value(m,b,"left",1),F(1))
        self.assertEqual(expected_value(m,b,"right",1),F(0))
        self.assertEqual(expected_value(m,b,"right",2),F(1))
        self.assertEqual(m.admissible("right",0),())

    def test_duration_must_fit_budget(self):
        m=feedback_machine(probe_duration=2)
        self.assertEqual(m.admissible("q",1),("guess0","guess1"))
        self.assertEqual(expected_value(m,(F(1,2),F(1,2)),"q",2),F(1,2))
        self.assertEqual(expected_value(m,(F(1,2),F(1,2)),"q",3),F(3,4))

    def test_exact_signature_matches_independent_cylinders(self):
        random_gen=random.Random(20261029)
        comparisons=0
        for _ in range(48):
            accuracy=random_gen.choice((F(1,4),F(1,2),F(3,4)))
            m=feedback_machine(probe_accuracy=accuracy)
            bs=tuple((F(1)-p,p) for p in (F(0),F(1,4),F(1,2),F(3,4),F(1)))
            for time in range(4):
                for left in bs:
                    for right in bs:
                        same_signature=(predictive_signature(m,left,"q",time)==predictive_signature(m,right,"q",time))
                        same_cylinders=(independent_cylinder_law(m,left,"q",time)==independent_cylinder_law(m,right,"q",time))
                        self.assertEqual(same_signature,same_cylinders)
                        comparisons+=1
        self.assertEqual(comparisons,4800)

    def test_direct_hidden_world_oracle(self):
        for accuracy in (F(1,4),F(1,2),F(3,4)):
            m=feedback_machine(probe_accuracy=accuracy)
            for d in range(4):
                for p in (F(0),F(1,4),F(1,2),F(3,4),F(1)):
                    b=(1-p,p)
                    self.assertEqual(direct_world_cylinders(m,b,"q",d),
                                     independent_cylinder_law(m,b,"q",d))

    def test_fail_closed(self):
        m=feedback_machine()
        with self.assertRaises(ValueError):normalize({"0":F(1,3),"1":F(1,3)},m.states)
        with self.assertRaises(ValueError):normalize({"0":F(0),"1":F(-1)},m.states)
        with self.assertRaises(ValueError):m.admissible("q",-1)
        with self.assertRaises(ValueError):m.admissible("q",True)
        bad=dict(m.kernels)
        bad["0","q","probe"]=(Branch(F(1),"y0",0,0,"0","q",False),)
        with self.assertRaises(ValueError):Machine(m.states,m.modes,m.actions,bad)
        bad["0","q","probe"]=(Branch(F(1,2),"y0",0,1,"0","q",False),)
        with self.assertRaises(ValueError):Machine(m.states,m.modes,m.actions,bad)


# Additional independent oracles and boundary counterexamples. These use raw
# hidden-state masses and whole policy trees, never the predictive signature.
from itertools import product
from math import ceil, log2
from functools import lru_cache


def all_policy_trees(machine, q, d):
    """Enumerate complete deterministic observation-adaptive policies."""
    trees = [None]  # stop
    for action in machine.admissible(q, d):
        events = sorted({(r.signal, r.reward, r.duration, r.next_mode, r.done)
                         for s in machine.states for r in machine.kernels[s, q, action]})
        menus = [([None] if e[-1] else all_policy_trees(machine, e[3], d - e[2]))
                 for e in events]
        for subtrees in product(*menus):
            trees.append((action, tuple(zip(events, subtrees))))
    return tuple(trees)


def whole_policy_law(machine, belief, q, d, policy):
    """Independently accumulate raw state masses for one whole policy tree."""
    def go(masses, mode, time, node, path):
        if node is None:
            return {path: sum(masses, F(0))}
        a, cases = node
        assert a in machine.admissible(mode, time)
        out = {}
        for event, child in cases:
            nxt = [F(0)] * len(machine.states)
            for i, s in enumerate(machine.states):
                for row in machine.kernels[s, mode, a]:
                    if (row.signal, row.reward, row.duration, row.next_mode, row.done) == event:
                        nxt[machine.states.index(row.next_state)] += masses[i] * row.probability
            if sum(nxt, F(0)):
                if event[-1]:
                    assert child is None
                for k,v in go(tuple(nxt), event[3], time - event[2], child, path+((a,event),)).items():
                    out[k] = out.get(k,F(0)) + v
        return out
    return go(belief,q,d,policy,())


def delayed_machine():
    states = ('0','1'); modes = ('raw','armed')
    actions = {'raw':('arm',),'armed':('read',)}
    table = {}
    for state in states:
        table[state,'raw','arm']=(Branch(F(1),'armed',0,1,state,'armed',False),)
        table[state,'armed','read']=(Branch(F(1),'observed',int(state),1,state,'armed',True),)
    return Machine(states,modes,actions,table)


class IRC02Extended(unittest.TestCase):
    def test_full_adaptive_policy_enumeration(self):
        machine = feedback_machine()
        policies = all_policy_trees(machine,'q',2)
        self.assertGreater(len(policies), 10)
        beliefs = tuple((F(1)-p,p) for p in (F(0),F(1,4),F(1,2),F(3,4),F(1)))
        for b in beliefs:
            best = F(0)
            for tree in policies:
                law = whole_policy_law(machine,b,'q',2,tree)
                self.assertEqual(sum(law.values(),F(0)),F(1))
                reward = sum(mass * sum(event[1] for _,event in trace)
                             for trace,mass in law.items())
                best=max(best,reward)
            self.assertEqual(best,expected_value(machine,b,'q',2))
        for left in beliefs:
            for right in beliefs:
                equivalent = predictive_signature(machine,left,'q',2)==predictive_signature(machine,right,'q',2)
                all_equal = all(whole_policy_law(machine,left,'q',2,t)==
                                whole_policy_law(machine,right,'q',2,t)
                                for t in policies)
                self.assertEqual(equivalent,all_equal)

    def test_hidden_state_readout_delayed_two_steps(self):
        m=delayed_machine(); beliefs=((F(1),F(0)),(F(0),F(1)))
        self.assertEqual(class_count(m,beliefs,'raw',1),1)
        self.assertEqual(class_count(m,beliefs,'raw',2),2)
        witness=shortest_distinguishing_cylinder(m,*beliefs,'raw',2)
        self.assertEqual(tuple(action for action,_ in witness[0]),('arm','read'))
        self.assertIsNotNone(witness)

    def test_deterministic_hc01_quotient_crosscheck(self):
        states=('00','01','10','11'); actions={'q':('hold','swap')}
        table={}
        for bits in states:
            for action in actions['q']:
                next_bits=bits if action=='hold' else bits[::-1]
                table[bits,'q',action]=(Branch(F(1),'ok',int(next_bits[0]),1,next_bits,'q',False),)
        m=Machine(states,('q',),actions,table)
        beliefs=tuple(tuple(F(int(s==s0)) for s in states) for s0 in states)
        self.assertEqual(class_count(m,beliefs,'q',0),1)
        self.assertEqual(class_count(m,beliefs,'q',1),4)
        hold_only=Machine(states,('q',),{'q':('hold',)},
                          {k:v for k,v in table.items() if k[2]=='hold'})
        self.assertEqual(class_count(hold_only,beliefs,'q',1),2)

    def test_rank_is_not_fixed_code_bits(self):
        m=feedback_machine();bs=tuple((F(k,10),F(10-k,10)) for k in range(11))
        self.assertEqual(class_count(m,bs,'q',1),11)
        self.assertEqual(ceil(log2(class_count(m,bs,'q',1))),4)
        # Hidden-state vector has just two coordinates, hence linear test rank <= 2.
        self.assertLessEqual(len(m.states),2)

    def test_zero_support_event_removed(self):
        states=('0','1');table={}
        for s in states:
            table[s,'q','read']=(Branch(F(1),s,int(s),1,s,'q',True),)
        m=Machine(states,('q',),{'q':('read',)},table)
        ev=successors(m,(F(1),F(0)),'q',1,'read')
        self.assertEqual(len(ev),1)
        self.assertEqual(ev[0][0][0],'0')
        self.assertEqual(ev[0][2],(F(1),F(0)))

    def test_mixed_terminal_and_variable_duration(self):
        states=('0','1');table={}
        table['0','q','go']=(Branch(F(1),'x',0,1,'0','q',True),)
        table['1','q','go']=(Branch(F(1),'x',0,2,'1','q',False),)
        m=Machine(states,('q',),{'q':('go',)},table)
        self.assertEqual(m.admissible('q',1),())
        self.assertEqual(m.admissible('q',2),('go',))
        observations=successors(m,(F(1,2),F(1,2)),'q',2,'go')
        self.assertEqual(set((e[2],e[4]) for e,_,_ in observations),{(1,True),(2,False)})

    def test_random_small_kernel_direct_world_comparisons(self):
        rng = random.Random(8022026)
        beliefs=((F(1),F(0)),(F(1,2),F(1,2)),(F(0),F(1)))
        for _ in range(40):
            states=('0','1');modes=('q','r');actions={'q':('a','b'),'r':('a','b')}
            kernels={}
            for s in states:
                for q in modes:
                    for a in actions[q]:
                        rows=[]
                        for weight in (F(1,3),F(2,3)):
                            rows.append(Branch(weight,str(rng.randrange(2)),rng.randrange(2),
                                rng.randrange(1,3),rng.choice(states),rng.choice(modes),bool(rng.randrange(2))))
                        kernels[s,q,a]=tuple(rows)
            machine=Machine(states,modes,actions,kernels)
            for d in range(3):
                for b in beliefs:
                    self.assertEqual(independent_cylinder_law(machine,b,'q',d),
                                     direct_world_cylinders(machine,b,'q',d))
                for b in beliefs:
                    for c in beliefs:
                        self.assertEqual(predictive_signature(machine,b,'q',d)==
                            predictive_signature(machine,c,'q',d),
                            direct_world_cylinders(machine,b,'q',d)==
                            direct_world_cylinders(machine,c,'q',d))


class IRC02Witness(unittest.TestCase):
    def test_adaptive_witness_replay_and_legality(self):
        m=delayed_machine()
        left=(F(1),F(0)); right=(F(0),F(1))
        result=witnessing_policy(m,left,right,'raw',2)
        self.assertIsNotNone(result)
        tree,path,p_left,p_right=result
        self.assertEqual(len(path),2)
        self.assertNotEqual(p_left,p_right)
        self.assertNotEqual(whole_policy_law(m,left,'raw',2,tree),
                            whole_policy_law(m,right,'raw',2,tree))
        self.assertIsNone(witnessing_policy(m,left,left,'raw',2))

if __name__ == "__main__":
    unittest.main()
