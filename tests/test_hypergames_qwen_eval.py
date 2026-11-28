"""HG-03 independent adversarial checks; no model weights or paid inference."""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path
from unittest.mock import patch

from spiral_ln.hypergames_qwen_eval import (
    BASELINE_NAMES, Completion, LocalChatBackend, canonical_bytes,
    generate_private_manifest, load_private_manifest, padded_scenario,
    paired_summary, parse_action, prompt_messages, require_local_endpoint,
    run_baseline_episode, run_model_episode, scenario_for, score_grid,
    sha256_file, summarize_results,
)
from spiral_ln.hypergames_single_player import (
    correct_route, initial_state, legal_actions, make_scenario, observation,
    oracle_action, transition, verification_checksum, authorization_checksum,
)


class FrozenQwenTransportTests(unittest.TestCase):
    def setUp(self):
        self.s = make_scenario(101, 140)

    def test_endpoint_allow_local_ipv4_and_ipv6(self):
        for address in ('http://127.0.0.1:8080/v1/chat/completions',
                        'http://localhost:8080/v1/chat/completions',
                        'http://[::1]:8080/v1/chat/completions'):
            self.assertEqual(require_local_endpoint(address), address)

    def test_endpoint_reject_external_network_and_port_ambiguity(self):
        bad = ('https://127.0.0.1:8080/v1/chat/completions',
               'http://8.8.8.8:8080/v1/chat/completions',
               'http://localhost:8080/other',
               'http://localhost/v1/chat/completions',
               'file:///tmp/test',
               'http://localhost:8080/v1/chat/completions?q=1',
               'http://localhost:8080/v1/chat/completions#x')
        for address in bad:
            with self.subTest(address=address), self.assertRaises(ValueError):
                require_local_endpoint(address)

    def test_decode_exact_action(self):
        self.assertEqual(parse_action('{"action":"audit"}', ('audit','abstain')),
                         ('audit',None))

    def test_decode_fails_closed_on_extra_object_fields(self):
        self.assertEqual(parse_action('{"action":"audit","reason":"ok"}', ('audit','abstain')),
                         ('abstain','invalid_schema'))

    def test_decode_fails_closed_on_illegal_or_wrong_type(self):
        self.assertEqual(parse_action('{"action":"publish"}', ('audit','abstain')),
                         ('abstain','illegal_action'))
        self.assertEqual(parse_action('{"action":4}', ('audit','abstain')),
                         ('abstain','invalid_schema'))

    def test_decode_fails_closed_on_fence_or_duplicate_json(self):
        for raw in ('```json\n{"action":"audit"}\n```',
                    '{"action":"audit"}{"action":"shortcut"}',
                    '{"action":"audit","action":"shortcut"}',
                    '<think>audit</think>{"action":"audit"}'):
            with self.subTest(raw=raw):
                self.assertEqual(parse_action(raw,('audit','abstain')),
                                 ('abstain','invalid_json'))

    def test_prompt_no_grading_fields_or_private_mode_before_audit(self):
        a, b = [prompt_messages(observation(self.s, initial_state(bit)), 'direct')
                for bit in (0,1)]
        self.assertEqual(a,b)
        as_text = json.dumps(a)
        for forbidden in ('private_bit', 'hidden_mode', 'hidden_state_reveal',
                          'counterfactual', 'outcome_after'):
            self.assertNotIn(forbidden,as_text)
        self.assertIn('null',as_text)

    def test_both_prompt_arms_are_frozen_and_distinct(self):
        obs = observation(self.s, initial_state(0))
        direct = prompt_messages(obs, 'direct')
        deliberate = prompt_messages(obs, 'deliberate')
        self.assertEqual(direct[0], deliberate[0])
        self.assertNotEqual(direct[1], deliberate[1])
        self.assertIn('verification checksum', deliberate[1]['content'])

    def test_prompt_fails_on_invalid_arm(self):
        with self.assertRaises(ValueError):
            prompt_messages(observation(self.s, initial_state(0)), 'exploit')

    def test_model_backend_frozen_request_and_identity(self):
        from unittest.mock import MagicMock
        fake = MagicMock()
        fake.__enter__.return_value.read.return_value = json.dumps({
            'model':'qwen3.5-0.8b-q4km-hg03',
            'choices':[{'message':{'content':'{"action":"audit"}'},'finish_reason':'stop'}],
            'usage':{'prompt_tokens':123,'completion_tokens':9}}).encode()
        backend = LocalChatBackend('http://127.0.0.1:8080/v1/chat/completions',
                                   'qwen3.5-0.8b-q4km-hg03')
        with patch('urllib.request.urlopen', return_value=fake) as urlopen:
            completion = backend(prompt_messages(observation(self.s, initial_state(0)),'direct'))
            req = urlopen.call_args.args[0]
            payload = json.loads(req.data)
        self.assertEqual((completion.text,completion.prompt_tokens), ('{"action":"audit"}',123))
        self.assertEqual((payload['temperature'],payload['seed']), (0,20261116))
        self.assertEqual(payload['response_format'],{'type':'json_object'})
        self.assertEqual(payload['max_tokens'],192)
        self.assertFalse(payload['stream'])

    def test_model_backend_rejects_wrong_model_alias(self):
        from unittest.mock import MagicMock
        fake=MagicMock(); fake.__enter__.return_value.read.return_value = json.dumps({
            'model':'unexpected', 'choices':[{'message':{'content':'{"action":"audit"}'}}]}).encode()
        backend=LocalChatBackend('http://localhost:8080/v1/chat/completions','expected')
        with patch('urllib.request.urlopen', return_value=fake):
            with self.assertRaises(ValueError):
                backend(prompt_messages(observation(self.s, initial_state(0)),'direct'))

    def test_model_backend_rejects_missing_content(self):
        from unittest.mock import MagicMock
        fake=MagicMock(); fake.__enter__.return_value.read.return_value = json.dumps({
            'model':'expected', 'choices':[{'message':{}}]}).encode()
        backend=LocalChatBackend('http://localhost:8080/v1/chat/completions','expected')
        with patch('urllib.request.urlopen', return_value=fake):
            with self.assertRaises(ValueError):
                backend(prompt_messages(observation(self.s, initial_state(0)),'direct'))


class HighDimensionalCohortTests(unittest.TestCase):
    def test_padded_preserves_task_defining_coordinates(self):
        for seed in (101,131,167,191):
            core, pad = make_scenario(seed,140), padded_scenario(seed)
            self.assertEqual(pad.public_bits[:140],core.public_bits)
            self.assertEqual(pad.parity_indices,core.parity_indices)
            self.assertEqual(pad.verification_indices,core.verification_indices)
            self.assertEqual(pad.authorization_indices,core.authorization_indices)
            self.assertEqual(pad.hidden_index,core.hidden_index)
            self.assertEqual(pad.mission_indices,core.mission_indices)
            self.assertEqual(verification_checksum(pad),verification_checksum(core))
            self.assertEqual(authorization_checksum(pad),authorization_checksum(core))
            self.assertEqual([correct_route(pad,b) for b in (0,1)],
                             [correct_route(core,b) for b in (0,1)])
            self.assertEqual(len(pad.public_bits),512)

    def test_native_512_has_more_interacting_gate_variables(self):
        core, native = scenario_for(101,'core_140'), scenario_for(101,'native_512')
        self.assertEqual((len(core.parity_indices),len(core.verification_indices),
                          len(core.authorization_indices)),(32,24,16))
        self.assertEqual((len(native.parity_indices),len(native.verification_indices),
                          len(native.authorization_indices)),(64,48,32))

    def test_padded_large_dimension_still_exact(self):
        s = padded_scenario(101,1024)
        self.assertEqual(len(s.public_bits),1024)
        self.assertEqual(len(s.parity_indices),32)

    def test_padded_reject_bad_dimension(self):
        for d in (0,140,True,20):
            with self.assertRaises(ValueError): padded_scenario(101,d)

    def test_unknown_cohort_fails(self):
        with self.assertRaises(ValueError): scenario_for(101,'quantum')

    def test_horizon_oracle_remains_unchanged_under_padding(self):
        for cohort in ('core_140','padded_512','native_512'):
            scenario=scenario_for(131,cohort)
            for h, first in ((4,'abstain'),(5,'audit')):
                for mode in (0,1):
                    self.assertEqual(oracle_action(scenario,observation(scenario, initial_state(mode,h))),first)


class PairedPolicyTests(unittest.TestCase):
    def setUp(self):
        self.s = make_scenario(101, 140)

    def test_frozen_fake_oracle_two_sealed_worlds_success(self):
        seen=[]
        def fake(messages):
            seen.append(messages)
            obs=json.loads(messages[1]['content'].split('PUBLIC OBSERVATION (only public fields):\n')[1]
                           .split('\nChoose your next legal action')[0])
            action=oracle_action(self.s,obs)
            return Completion(json.dumps({'action':action}), 'MOCK-oracle')
        outputs=[run_model_episode(self.s, b, 5, 'direct',fake) for b in (0,1)]
        self.assertEqual([x['grade']['true_utility'] for x in outputs], ['9','9'])
        self.assertEqual([x['grade']['turns'] for x in outputs], [5,5])
        self.assertEqual(outputs[0]['trace'][0]['prompt_sha256'],
                         outputs[1]['trace'][0]['prompt_sha256'])
        self.assertNotEqual(outputs[0]['trace'][1]['prompt_sha256'],
                            outputs[1]['trace'][1]['prompt_sha256'])
        self.assertEqual(len(seen),10)

    def test_malformed_response_abstains_no_retry(self):
        calls=[]
        def bad(msgs):
            calls.append(msgs)
            return Completion('Pick audit because it works.', 'MOCK-bad')
        out=run_model_episode(self.s, 0, 5, 'direct',bad)
        self.assertEqual((len(calls),out['grade']['decode_errors'],out['grade']['true_utility']),
                         (1,1,'0'))
        self.assertEqual(out['trace'][0]['decode_error'],'invalid_json')

    def test_illegal_response_abstains_no_retry(self):
        out=run_model_episode(self.s,0,5,'direct',
                              lambda _m: Completion('{"action":"publish"}','MOCK-illegal'))
        self.assertEqual(out['grade']['decode_errors'],1)
        self.assertEqual(out['grade']['ending'],'abstained')

    def test_truncated_valid_response_fails_closed(self):
        out=run_model_episode(self.s,0,5,'direct',
                              lambda _m: Completion('{"action":"audit"}','MOCK-truncated',
                                                     finish_reason='length'))
        self.assertEqual(out['grade']['decode_errors'],1)
        self.assertEqual(out['trace'][0]['decode_error'],'truncated_or_filtered')
        self.assertEqual(out['grade']['true_utility'],'0')

    def test_hidden_grade_unavailable_to_backend(self):
        def verify_view(messages):
            raw=json.dumps(messages)
            for forbidden in ('true_utility": "', 'false_accept', 'private_bit',
                              'hidden_mode', 'realized_outcome', 'hidden_state_reveal'):
                if forbidden!='true_utility": "':
                    self.assertNotIn(forbidden,raw)
            return Completion('{"action":"abstain"}', 'MOCK-observer')
        run_model_episode(self.s,0,5,'direct',verify_view)

    def test_baseline_first_action_and_exact_values(self):
        self.assertEqual(run_baseline_episode(self.s,0,5,'bellman')['true_utility'],'9')
        self.assertEqual(run_baseline_episode(self.s,1,4,'bellman')['true_utility'],'0')
        self.assertEqual(run_baseline_episode(self.s,0,5,'proxy')['proxy_score'],100)

    def test_baseline_per_seed_pairs_and_public_aggregation(self):
        report=score_grid((101,),('core_140','padded_512','native_512'),(4,5),('direct','deliberate'))
        self.assertEqual(len(report['rows']),3*2*2*len(BASELINE_NAMES))
        self.assertEqual(len(report['per_seed']),3*2*len(BASELINE_NAMES))
        lookup={(x['cohort'],x['horizon'],x['policy']):x for x in report['per_seed']}
        for cohort in ('core_140','padded_512','native_512'):
            self.assertEqual(lookup[(cohort,5,'bellman')]['mean_true_utility'],'9')
            self.assertEqual(lookup[(cohort,4,'blind_route0')]['mean_true_utility'],'-5/2')
            self.assertEqual(lookup[(cohort,5,'proxy')]['false_accept'],2)

    def test_missing_hidden_world_is_rejected(self):
        rows=[{'seed':101,'cohort':'core_140','horizon':5,'policy':'qwen',
               'prompt_arm':'direct','hidden_mode':0,
               'grade':{'true_utility':'0','false_accept':False,
                        'safe_success':False,'turns':1}}]
        with self.assertRaises(ValueError):paired_summary(rows)

    def test_invalid_grid_fails(self):
        for seeds in ((101,101),(-1,),()):
            with self.assertRaises(ValueError):
                score_grid(seeds,('core_140',),(4,),('direct',))
        with self.assertRaises(ValueError):
            score_grid((101,),('core_140',),(6,),('direct',))

    def test_report_labels_model_and_mechanics_evidence_differently(self):
        reg={'private_manifest_sha256':'abc'}
        r=score_grid((101,),('core_140',),(4,),('direct',))
        control=summarize_results(r,reg,'baseline')
        model=summarize_results(r,reg,'dev',{'weights_sha256':'abc'})
        self.assertEqual(control['evidence_level'],'exact synthetic mechanism control')
        self.assertEqual(model['evidence_level'],'local model trajectory measurement')


class PrivateManifestTests(unittest.TestCase):
    def test_manifest_canonical_source_fidelity(self):
        x={'schema_version':'HG-03/PRIVATE-v1','seeds':[7,13,23]}
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'private.json'
            path.write_bytes(canonical_bytes(x))
            reg={'private_manifest_sha256':sha256_file(path),
                 'private_seed_count':3,'development_seeds':[101]}
            self.assertEqual(load_private_manifest(path,reg),(7,13,23))

    def test_manifest_tamper_rejected(self):
        x={'schema_version':'HG-03/PRIVATE-v1','seeds':[7,13,23]}
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'private.json'
            path.write_bytes(canonical_bytes(x))
            reg={'private_manifest_sha256':sha256_file(path),
                 'private_seed_count':3,'development_seeds':[101]}
            x['seeds'][1]=17
            path.write_bytes(canonical_bytes(x))
            with self.assertRaises(ValueError): load_private_manifest(path,reg)

    def test_development_overlap_rejected(self):
        x={'schema_version':'HG-03/PRIVATE-v1','seeds':[7,101]}
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'private.json'
            path.write_bytes(canonical_bytes(x))
            reg={'private_manifest_sha256':sha256_file(path),
                 'private_seed_count':2,'development_seeds':[101]}
            with self.assertRaises(ValueError): load_private_manifest(path,reg)

    def test_generate_private_manifest_schema(self):
        sample=generate_private_manifest(5)
        self.assertEqual(sample['schema_version'],'HG-03/PRIVATE-v1')
        self.assertEqual(len(set(sample['seeds'])),5)
        self.assertEqual(len(sample['seeds']),5)
        with self.assertRaises(ValueError):generate_private_manifest(0)


if __name__ == '__main__':
    unittest.main()
