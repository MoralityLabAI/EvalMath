from collections import defaultdict
from math import gcd
import random
import unittest

from spiral_ln.evaluation_collatz_quotient import atlas, basin, collision, feedback, full_oracle, quotient, step


class TestCollatzQuotient(unittest.TestCase):
    def test_known_periods(self):
        for d, expected in ((13,{1:5,5:6,13:3}), (73,{3:12,5:28,73:3}),
                            (265,{9:21,21:22,25:22,53:4,265:3}),
                            (577,{3:36,5:34,23:37,39:35,577:3})):
            self.assertEqual(atlas(d)[1], expected)

    def test_independent_full_walk(self):
        for d in range(1, 502, 4):
            if gcd(d,6)!=1: continue
            labels, periods=atlas(d)
            q=quotient(d)
            for n in range(1,2*d,2):
                c=basin(n,d,labels)
                self.assertEqual(full_oracle(n,d),(c,periods[c]))
                self.assertEqual(q[n%d],q[step(n,d)%d])
            self.assertEqual(set(q.values()),{q[c%d] for c in periods})

    def test_feedback(self):
        self.assertEqual(feedback(601)['accuracy'],'547/601')
        self.assertEqual(feedback(7081)['accuracy'],'6805/7081')
        self.assertEqual(feedback(13)['coprime_accuracy'],'7/12')

    def test_constructive_modular_obstruction(self):
        for d in (13,601,7081):
            labels, periods=atlas(d)
            q=quotient(d)
            groups=defaultdict(list)
            for c in sorted(periods): groups[q[c%d]].append(c)
            for cs in groups.values():
                if len(cs)<2: continue
                for m in (1,2,4,8,13,24,73,2*d,3*d):
                    x,y=collision(d,*cs[:2],m)
                    self.assertEqual(x%m,y%m)
                    self.assertEqual(full_oracle(x,d)[0],cs[0])
                    self.assertEqual(full_oracle(y,d)[0],cs[1])

    def test_long_inputs(self):
        rng=random.Random(2601)
        for d in (13,73,265,577,601,7081):
            labels, periods=atlas(d)
            q=quotient(d)
            for bits in (64,256,1024):
                for _ in range(8):
                    n=(1<<(bits-1))|rng.getrandbits(bits-1)
                    c=basin(n,d,labels)
                    self.assertEqual(full_oracle(n,d),(c,periods[c]))
                    self.assertEqual(q[n%d],q[c%d])

if __name__=='__main__': unittest.main()
