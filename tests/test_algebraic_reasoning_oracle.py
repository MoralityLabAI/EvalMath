"""ARG-01 independent mathematical reference, leakage and certificate tests."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
import json
import random

from spiral_ln import algebraic_reasoning_oracle as a

HERE=Path(__file__).resolve().parents[1]


class Algebra(TestCase):
    def test_inverse_independent_multiplication(self):
        rng=random.Random(147)
        for _ in range(12):
            f=(1,)+tuple(rng.randint(-3,3) for _ in range(8))
            self.assertEqual(a.convolution(f,a.reciprocal(f)),(1,)+(0,)*8)
            self.assertEqual(a.unary(a.unary(f,'N'),'N'),f)
            self.assertEqual(a.unary(a.unary(f,'R'),'R'),f)

    def test_independent_fork_and_additive(self):
        f=(1,2,1,0,0,0)
        self.assertEqual(a.execute(f,'fork',('I','I','I')),(1,4,6,4,1,0))
        self.assertEqual(a.execute(f,'additive',('I','I','I')),(1,4,2,0,0,0))
        self.assertEqual(a.execute(f,'hadamard',('I','I','I')),(1,4,1,0,0,0))
        self.assertEqual(a.execute(f,'cascade',('I','S','I')),
                         a.convolution(f,a.unary(f,'S')))

    def test_small_degree_independent_manual(self):
        f=(1,2,3,4,5)
        n=a.unary(f,'N')
        s=a.unary(f,'S')
        self.assertEqual(n,(1,-2,3,-4,5))
        self.assertEqual(s,(1,0,2,0,3))
        self.assertEqual(a.first_error(f,f),None)
        self.assertEqual(a.first_error(f,n),1)

    def test_invalid_input_rejected(self):
        for seq in ((2,1),(1,1.0),(1,True),(),(1,'2')):
            with self.assertRaises(ValueError):a.check_series(seq)
        for topology,graph in (('unknown',('I','I','I')),('fork',('Q','N','R'))):
            with self.assertRaises(ValueError):a.execute((1,1,2),topology,graph)
        with self.assertRaises(ValueError):a.search(None,a.PROGRAMS,budget=0)

    def test_generators_unit_integral(self):
        rng=random.Random(42)
        for name in a.ALL_FAMILIES:
            for _ in range(5):
                x=a.source(rng,name)
                self.assertEqual(len(x),a.FUTURE+1)
                self.assertEqual(x[0],1)
                self.assertTrue(all(type(v) is int for v in x))


class Roster(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups=a.roster(calibration_per_family=4,test_per_family=5,negative=4,collision_pairs=3)

    def test_calibration_excludes_test_generators(self):
        original=a.source
        def guarded(rng,family,degree=a.FUTURE):
            if family in a.OOD_FAMILIES:raise AssertionError('test-only source used in calibration')
            return original(rng,family,degree)
        with patch.object(a,'source',side_effect=guarded):
            d=a.roster(include_test=False,calibration_per_family=3)
        self.assertEqual(set(d),{'calibration'})
        self.assertEqual(len(d['calibration']),9)

    def test_visible_has_no_future_label_or_family(self):
        x=self.groups['rational'][0]
        v=x.public
        self.assertEqual(set(v),{'case_id','topology','observed_degree','demos','query'})
        y=replace(x,identifier='different',future=(1,)*len(x.future),source_graph=None,
                  family='changed')
        self.assertEqual(x.signature,y.signature)
        self.assertEqual({k:v for k,v in x.public.items() if k!='case_id'},
                         {k:v for k,v in y.public.items() if k!='case_id'})

    def test_roster_deterministic_and_disjoint(self):
        r=a.roster(calibration_per_family=4,test_per_family=5,negative=4,collision_pairs=3)
        self.assertEqual({k:a.hash_roster(v) for k,v in r.items()},
                         {k:a.hash_roster(v) for k,v in self.groups.items()})
        signatures={}
        for group,cases in self.groups.items():
            for case in cases:
                if case.signature in signatures:
                    self.assertEqual(group,'collision')
                    self.assertEqual(signatures[case.signature],'collision')
                else:signatures[case.signature]=group

    def test_complete_search_accepts_positive_and_rejects_negative(self):
        for name in a.ALL_FAMILIES:
            self.assertTrue(all(a.full_search(c)['graph'] is not None for c in self.groups[name]))
        self.assertTrue(all(a.full_search(c)['graph'] is None for c in self.groups['negative']))

    def test_collision_information_boundary(self):
        x=self.groups['collision']
        for first,second in zip(x[::2],x[1::2]):
            self.assertEqual(first.signature,second.signature)
            self.assertEqual(first.query,second.query)
            self.assertNotEqual(first.future,second.future)
            self.assertEqual(a.full_search(first)['trace'],a.full_search(second)['trace'])
            found=a.full_search(first)
            self.assertEqual(sum(a.grade(case,found)['future_correct'] for case in (first,second)),1)

    def test_one_paid_query_two_demonstrations(self):
        case=self.groups['signed'][0]
        out=a.search(case,(('I','I','I'),),budget=1)
        self.assertEqual(out['queries'],1)
        self.assertEqual(len(out['trace']),1)
        self.assertEqual(a.query_cost(case,('I','I','I'))['demo_executions'],2)
        self.assertEqual(out['integer_loop_proxy'],a.query_cost(case,('I','I','I'))['integer_loop_proxy'])

    def test_complete_receipt_source_and_counts(self):
        result=json.loads((HERE/'fixtures/algebraic_reasoning_oracle_v1.json').read_text())
        self.assertEqual(result['schema'],a.VERSION)
        self.assertEqual(result['dsl_programs'],64)
        self.assertEqual(result['per_split']['negative']['accepted'],0)
        self.assertEqual(result['per_split']['collision']['false_future'],6)
        self.assertEqual(result['overall']['cases'],228)


if __name__=='__main__':
    import unittest;unittest.main()
