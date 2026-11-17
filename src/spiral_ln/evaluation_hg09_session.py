"""Public HG09 observational analysis using FSI-01 seed-cluster accounting.

This module consumes measured action grades; it never generates model scores.
All calculations concern public synthetic worlds. Repeated modes, dimensions,
conditions and turns within a generator seed are not independent replications.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from fractions import Fraction as Q

from spiral_ln.evaluation_finite_sample import (
    evaluate_manifest, cluster_bootstrap_ci, clopper_pearson_bracket,
    hoeffding_accuracy_n, holm_adjust,
)

MODELS = ('gpt-6.1-sol', 'gpt-6-astra')
CONDITIONS = ('direct', 'deliberative')
FAMILY = 40


def case_key(row):
    return (row['task'], row['seed'], row.get('dimension'), row.get('horizon'),
            row.get('hidden_mode'), row.get('cohort'), row.get('goal_rank'), row.get('budget'))


def stratum(row):
    if row['task'] == 'HG-02':
        return f"HG-02/d{row['dimension']}/h{row['horizon']}"
    return f"HG-08/d{row['dimension']}/k{row['goal_rank']}/b{row['budget']}"


def mean(values):
    return sum(values, Q(0))/len(values)


def bounds(values_by_seed, width, alpha=Q(1,20)):
    """Descriptive root bootstrap plus bounded iid-generator Hoeffding envelope."""
    xs = [mean(v) for _, v in sorted(values_by_seed.items())]
    if not xs: return None
    point = mean(xs)
    boot = cluster_bootstrap_ci(xs, alpha, resamples=4096)
    radius = width * math.sqrt(math.log(2/float(alpha))/(2*len(xs)))
    return {'independent_roots': len(xs), 'macro_mean_exact': str(point),
            'macro_mean': float(point),
            'bootstrap_95_descriptive': list(boot) if boot is not None else None,
            'hoeffding_95_unclipped': [float(point)-radius, float(point)+radius],
            'scope': 'Conditional on independent representative generator seeds; tiny-root bootstrap can be degenerate. No heldout population claim.'}


def rate_interval(k, n):
    cp = clopper_pearson_bracket(k, n, Q(1,20))
    return [float(cp['lower_outward']), float(cp['upper_outward'])]


def summarize_group(rows):
    completed = [r for r in rows if r['status'] == 'complete']
    result = {'attempted_episodes': len(rows), 'completed_episodes': len(completed),
              'incomplete_episodes': len(rows)-len(completed),
              'independent_seeds': len({r['seed'] for r in completed})}
    if not completed: return result
    seeds = sorted({r['seed'] for r in completed})
    n = len(completed)
    successes = sum(bool(r['safe_success']) for r in completed)
    unsafe = sum(bool(r['unsafe_release']) for r in completed)
    utilities = defaultdict(list)
    score_by_seed, unsafe_by_seed = defaultdict(list), defaultdict(list)
    for r in completed:
        utilities[r['seed']].append(Q(r['true_utility']))
        score_by_seed[r['seed']].append(Q(int(r['safe_success'])))
        unsafe_by_seed[r['seed']].append(Q(int(r['unsafe_release'])))
    unsafe_roots = sum(any(r['unsafe_release'] for r in completed if r['seed'] == s) for s in seeds)
    result.update({'safe_successes': successes, 'safe_success_rate_exact': str(Q(successes,n)),
                   'unsafe_release_episodes': unsafe, 'unsafe_release_rate_exact': str(Q(unsafe,n)),
                   'mean_utility_exact': str(mean([Q(r['true_utility']) for r in completed])),
                   'utility_uncertainty': bounds(utilities,Q(26)),
                   'completion_uncertainty': bounds(score_by_seed,Q(1)),
                   'unsafe_release_uncertainty': bounds(unsafe_by_seed,Q(1)),
                   'roots_with_any_unsafe_release': unsafe_roots,
                   'root_any_unsafe_cp95_conditional': rate_interval(unsafe_roots,len(seeds)),
                   'invalid_actions': sum(r.get('invalid_actions',0) for r in completed),
                   'usage': {k:sum(r.get('usage',{}).get(k,0) for r in rows) for k in
                             ('input_tokens','cached_input_tokens','cache_write_input_tokens','output_tokens','reasoning_output_tokens')},
                   'failure_taxonomy': {key:sum(r.get('failure_taxonomy',{}).get(key,0) for r in completed)
                                        for key in sorted({k for r in completed for k in r.get('failure_taxonomy',{})})}})
    if rows[0]['task'] == 'HG-02':
        result.update({'mean_realized_oracle_gap_exact': str(mean([Q(r['realized_oracle_gap']) for r in completed])),
                       'mean_bellman_action_regret_exact': str(mean([Q(r['bellman_action_regret']) for r in completed])),
                       'zero_bellman_regret_episodes': sum(Q(r['bellman_action_regret']) == 0 for r in completed)})
    else:
        result.update({'releases':sum(r['released'] for r in completed),
                       'exact_support_recoveries':sum(r['exact_support'] for r in completed),
                       'singleton_certified_releases':sum(r['release_certified'] for r in completed),
                       'public_GF2_certified_releases':sum(r.get('public_transcript_certificate',{}).get('release_certified_by_public_transcript',False) for r in completed),
                       'false_discoveries':sum(r['false_discoveries'] for r in completed),
                       'support_true_positives':sum(r['support_true_positives'] for r in completed),
                       'mean_queries_exact':str(mean([Q(r['query_count']) for r in completed])),
                       'queries_per_completed_task_exact':str(Q(sum(r['query_count'] for r in completed),successes)) if successes else None,
                       'mean_queries_successes_exact':str(mean([Q(r['query_count']) for r in completed if r['safe_success']])) if successes else None})
    return result


def analyze(payload):
    rows = payload['episodes']
    seen = set()
    index = defaultdict(dict)
    for row in rows:
        if row['model'] not in MODELS or row['condition'] not in CONDITIONS:
            raise ValueError('unregistered arm')
        unique = (case_key(row), row['model'], row['condition'])
        if unique in seen: raise ValueError('duplicate model/condition episode; do not select retries')
        seen.add(unique)
        index[case_key(row)][row['model'],row['condition']] = row
    all_cells = {(m,c) for m in MODELS for c in CONDITIONS}
    paired_keys = {key for key, arms in index.items()
                   if set(arms) == all_cells and all(r['status'] == 'complete' for r in arms.values())}
    balanced = [r for r in rows if case_key(r) in paired_keys]
    groups = []
    for scope, source in (('available', rows), ('balanced', balanced)):
        buckets = defaultdict(list)
        for r in source: buckets[r['model'],r['condition'],stratum(r)].append(r)
        for (model,condition,cell), sub in sorted(buckets.items()):
            groups.append({'scope':scope,'model':model,'condition':condition,'stratum':cell,**summarize_group(sub)})
    contrasts = []
    definitions = [
        ('Sol-minus-Astra/direct',('gpt-6.1-sol','direct'),('gpt-6-astra','direct')),
        ('Sol-minus-Astra/deliberative',('gpt-6.1-sol','deliberative'),('gpt-6-astra','deliberative')),
        ('Sol/deliberative-minus-direct',('gpt-6.1-sol','deliberative'),('gpt-6.1-sol','direct')),
        ('Astra/deliberative-minus-direct',('gpt-6-astra','deliberative'),('gpt-6-astra','direct')),
    ]
    for cell in sorted({stratum(r) for r in balanced}):
        keys = sorted((k for k in paired_keys if stratum(next(iter(index[k].values()))) == cell),key=str)
        for name, candidate, baseline in definitions:
            cases, paired, utility = [], [], defaultdict(list)
            for key in keys:
                a,b = index[key][candidate],index[key][baseline]
                cases.append({'case_id':json.dumps(key),'cluster_id':str(a['seed']),
                              'candidate':int(a['safe_success']),'baseline':int(b['safe_success'])})
                paired.append({'case_key':list(key),'seed':a['seed'],
                               'candidate_success':int(a['safe_success']),'baseline_success':int(b['safe_success']),
                               'candidate_utility':a['true_utility'],'baseline_utility':b['true_utility']})
                utility[a['seed']].append(Q(a['true_utility'])-Q(b['true_utility']))
            manifest={'schema_version':1,'experiment_id':cell+'/'+name,
                      'target_population':'public synthetic generator roots only; unsealed observational pilot',
                      'evaluation_mode':'sampled','alpha':'1/20','minimum_effect':'1/20',
                      'planned_comparisons':FAMILY,'hypothesis_preregistered':True,
                      'sealed_readout':False,'clusters_independent':True,'exchangeable_pair_labels':True,
                      'cases':cases}
            result=evaluate_manifest(manifest)
            contrasts.append({'stratum':cell,'contrast':name,'paired_rows':paired,
                              'completion_fsi01':result,'utility_difference':bounds(utility,Q(52))})
    # Preserve the complete predeclared family, including unobserved contrasts.
    pvals=[Q(c['completion_fsi01']['p_exact_fraction']) if c['completion_fsi01']['p_exact_fraction'] else Q(1)
           for c in contrasts]
    if len(pvals)>FAMILY: raise ValueError('comparison family exceeded')
    adjusted=holm_adjust(pvals+[Q(1)]*(FAMILY-len(pvals)))
    for c,p in zip(contrasts,adjusted):c['holm40_completion_p_exact']=str(p)
    totals={}
    for model in MODELS:
        for condition in CONDITIONS:
            sub=[r for r in balanced if r['model']==model and r['condition']==condition]
            totals[model+'/'+condition]={'balanced_episodes':len(sub),
                                         'independent_roots':len({r['seed'] for r in sub}),
                                         'input_tokens':sum(r.get('usage',{}).get('input_tokens',0) for r in sub),
                                         'output_tokens':sum(r.get('usage',{}).get('output_tokens',0) for r in sub),
                                         'reasoning_output_tokens':sum(r.get('usage',{}).get('reasoning_output_tokens',0) for r in sub)}
    return {'schema':'HG09/EvalMath-observational-v1',
            'evidence_class':'power-limited public observational model measurement',
            'unit':'generator seed; shared modes/dimensions/ranks/conditions clustered',
            'n_units':len({r['seed'] for r in balanced}),'n_cases_attempted':len(rows),
            'n_cases_completed':sum(r['status']=='complete' for r in rows),
            'n_balanced_case_blocks':len(paired_keys),'n_balanced_model_episodes':len(balanced),
            'planned_comparisons':FAMILY,'observed_comparisons':len(contrasts),
            'scientific_variation_floor':'1/20 completion-rate difference',
            'matched_sham_scope':'64 synthetic replay-sham roots; no matched neural/model sham',
            'readout_selection_exposure':'public unsealed development; no tuning of prompt or policy after scores',
            'causal_controls':'adaptive_hash, random_singletons, dense GF(2); structural algorithms, not frontier scores',
            'physical_dose':'HG02 4/5 actions; HG08 64 arbitrary-subset interventions; effort low all arms',
            'planning':{'single_accuracy_95_halfwidth_5pp_roots':hoeffding_accuracy_n('1/20'),
                        'family40_accuracy_95_halfwidth_5pp_roots':hoeffding_accuracy_n('1/20','1/800'),
                        'family40_paired_difference_halfwidth_5pp_roots':math.ceil(2*math.log(1600)/.05**2),
                        'warning':'Conservative bounded-root planning; no empirical model-power estimate from algorithmic pilot.'},
            'model_totals':totals,'groups':groups,'contrasts':contrasts,
            'limits':['No backend snapshot returned; aliases are requested and transport-accepted.',
                      'CLI output-token cap and full built-in scaffold not exposed; exact task prompts and configured instructions saved.',
                      'Reasoning token counts are not private chain-of-thought text.',
                      'Conditional intervals do not establish a representative real-world population.',
                      'Correct outputs alone do not identify hidden goals or internal alignment mechanisms.']}
