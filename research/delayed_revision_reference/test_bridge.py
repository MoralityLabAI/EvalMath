"""Independent checks for delayed-revision posterior and scoring reference."""
import sys
import unittest
from pathlib import Path
from itertools import combinations, product
from fractions import Fraction as Q
sys.path.insert(0, str(Path(__file__).resolve().parent))
from bridge import analytic, independent_raw_oracle, raw_population, information_capacity


class DelayedRevisionTests(unittest.TestCase):
    def test_analytic_equals_raw_for_all_reachable_small_observations(self):
        checked=0
        for n in (2,3,4):
            for j in range(1,n):
                for slots in combinations(range(n),j):
                    for old in product((0,1),repeat=n):
                        for new in product((0,1),repeat=j):
                            for r in range(j+1):
                                prefix=tuple(old[i] for i in slots[:r])
                                a=analytic(n,slots,sum(old),new,prefix)
                                b=independent_raw_oracle(n,slots,sum(old),new,prefix)
                                self.assertEqual(a,b)
                                checked+=1
        self.assertGreater(checked,200)

    def test_full_reveal_and_variance_decomposition(self):
        for n,slots in ((3,(1,)),(4,(0,2))):
            rows=[raw_population(n,slots,r) for r in range(len(slots)+1)]
            self.assertEqual(rows[-1]["regret"],Q(0))
            for a,b in zip(rows,rows[1:]):
                self.assertGreaterEqual(a["regret"],b["regret"])
                self.assertEqual(a["mass"],Q(1))
                self.assertEqual(b["mass"],Q(1))
            self.assertGreater(rows[0]["regret"],0)

    def test_exact_capacity_contract(self):
        result=information_capacity(12,6)
        self.assertEqual(result,{"histories":4096,
            "initial_posterior_labels":13, "self_contained_bits":12,
            "max_label_fiber":924, "extra_fixed_tag_bits":10,
            "verified_old_sum_message_bits":3, "early_count_field_bits":4})
        for args in ((12,0),(12,12),(13,6),(1,1)):
            with self.assertRaises(ValueError):
                information_capacity(*args)

    def test_invalid_evidence_rejected(self):
        for call in (lambda:analytic(4,(0,0),2,(1,0),()),
                     lambda:analytic(4,(1,),2,(3,),()),
                     lambda:analytic(4,(1,),2,(1,),(1,1)),
                     lambda:independent_raw_oracle(2,(0,),0,(1,),(1,))):
            with self.assertRaises(ValueError):
                call()


if __name__=="__main__":
    unittest.main()
