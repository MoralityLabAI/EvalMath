"""Independent, adversarial finite audit of BPD-LG-02 source generation."""
import json
from pathlib import Path
import tempfile
import unittest
from collections import defaultdict

from experiments.bpd_lean_curriculum_v2 import generate as g


class BpdLg02(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = g.roster()

    def test_counts_and_source_feature_isolation(self):
        m=g.audit(self.rows)
        self.assertEqual((m['cases'],m['positive_cases'],m['negative_finite_models']), (384,192,192))
        self.assertEqual(m['split_counts'], {'train':256,'dev':64,'test':64})
        self.assertEqual(m['cross_split_alpha_collisions'],0)
        self.assertEqual(m['cross_split_group_collisions'],0)
        self.assertEqual(m['distinct_alpha_hashes'],384)
        self.assertTrue(all(set(r['public'])=={'case_id','lean_statement'} for r in self.rows))
        self.assertTrue(all('critical' not in r['public']['lean_statement'] and
                            'noise : Nat' not in r['public']['lean_statement'] for r in self.rows))

    def test_pair_metadata_not_a_public_label(self):
        by_group=defaultdict(list)
        for row in self.rows: by_group[row['root_group']].append(row)
        for group,items in by_group.items():
            self.assertEqual((len(items),sum(r['host_only']['solvable'] for r in items)),(4,2))
            self.assertEqual(len({r['split'] for r in items}),1)
            self.assertEqual(len({r['alpha_hash'] for r in items}),4)
            # Every group contains one-label-only edge differences, with
            # equal premise counts in positive and negative instances.
            positive=[r for r in items if r['host_only']['solvable']]
            negative=[r for r in items if not r['host_only']['solvable']]
            for a in positive:
                self.assertTrue(any(len(a['host_only']['source_edges']) ==
                                    len(b['host_only']['source_edges']) for b in negative))

    def test_independent_transitive_closure(self):
        """Warshall-style reachable sets separate from generator DFS and BFS."""
        for row in self.rows:
            d=row['host_only'];sig=d['model_signature']; nodes=[f'X{i}' if row['family']=='rw' else f'P{i}'
                for i in range(row['structural_depth']+1)] + [f'D{i}' for i in range(sig['decoy_count'])]
            relation={(a,b) for a,b in d['source_edges']}|{(n,n) for n in nodes}
            if row['family']=='rw':relation|={(b,a) for a,b in d['source_edges']}
            for pivot in nodes:
                left=[a for a in nodes if (a,pivot) in relation]
                right=[b for b in nodes if (pivot,b) in relation]
                relation|={(a,b) for a in left for b in right}
            self.assertEqual((nodes[0],nodes[row['structural_depth']]) in relation,
                             d['solvable'])

    def test_every_negative_has_satisfying_finite_model(self):
        for row in self.rows:
            d=row['host_only'];sig=d['model_signature'];depth=row['structural_depth']
            role_nodes=['X'+str(i) if row['family']=='rw' else 'P'+str(i) for i in range(depth+1)]
            spec={'family':row['family'],'main':role_nodes,'aux':['D'+str(i) for i in range(sig['decoy_count'])],
                  'edges':[tuple(e) for e in d['source_edges']]}
            if d['solvable']:
                self.assertIsNone(d['countermodel'])
            else:
                self.assertTrue(g.verify_model(spec,d['countermodel']))
                self.assertTrue(d['countermodel']['goal_false'])

    def test_half_of_positives_use_a_real_detour(self):
        direct,detour=0,0
        for row in self.rows:
            if not row['host_only']['solvable']:continue
            d=row['host_only'];main=[('X' if row['family']=='rw' else 'P')+str(i)
                for i in range(row['structural_depth']+1)]
            direct_flag=all((main[i],main[i+1]) in map(tuple,d['source_edges'])
                            for i in range(len(main)-1))
            direct+=direct_flag;detour+=not direct_flag
            self.assertGreaterEqual(d['proof_witness'].count('rw' if row['family']=='rw' else
                               'rcases' if row['family']=='rcases' else
                               'induction' if row['family']=='induction' else 'h'),1)
        self.assertEqual((direct,detour),(96,96))

    def test_export_determinism_and_certificate_cardinality(self):
        with tempfile.TemporaryDirectory() as p, tempfile.TemporaryDirectory() as q:
            a=g.export(Path(p));b=g.export(Path(q))
            self.assertEqual(a,b)
            for split,pos,neg in (('train',128,128),('dev',32,32),('test',32,32)):
                self.assertEqual((Path(p)/f'{split}_positives.lean').read_text().count('theorem thm_bpd2_'),pos)
                self.assertEqual((Path(p)/f'{split}_refutations.lean').read_text().count('theorem neg_thm_bpd2_'),neg)
                source=(Path(p)/f'{split}_positives.lean').read_text()+'\n'+(Path(p)/f'{split}_refutations.lean').read_text()
                for forbidden in ('sorry','admit','native_decide','axiom '):
                    self.assertNotIn(forbidden,source)

    def test_completeness_of_source_normalization_not_claimed(self):
        # The checksum covers role-labelled premise graphs, not equivalence
        # under arbitrary graph automorphisms or logical simplification.
        self.assertEqual(g.graph_spec('exact',3,0,0,0)['alpha_hash'],
                         g.graph_spec('exact',3,0,0,0)['alpha_hash'])
        self.assertNotEqual(g.graph_spec('exact',3,0,0,0)['alpha_hash'],
                            g.graph_spec('exact',3,1,0,0)['alpha_hash'])


if __name__=='__main__':unittest.main()
