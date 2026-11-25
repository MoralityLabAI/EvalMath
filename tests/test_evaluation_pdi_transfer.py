from copy import deepcopy
from fractions import Fraction as F
import pytest
from spiral_ln.evaluation_pdi_transfer import ARMS, COSTS, digest, summarize, paired_statistics


def fixture():
    # Synthetic public receipt; no actual proof, inference, or held-out data.
    h = digest
    budget = dict(zip(COSTS, (100, 20, 1000)))
    m = {'schema':'PDI-transfer-pilot-v1','arms':list(ARMS),'family_count':32,'seed':271125,
         'model_sha256':h('model'),'runner_sha256':h('runner'),'families':[]}
    for i in range(32):
        m['families'].append({'family_id':str(i),'construction_sha256':h(['root',i]),
          'environment_sha256':h(['env',i]),'split':'heldout','budget':budget,
          'targets':[{'target_id':str(j),'statement_sha256':h(['statement',i,j])} for j in range(4)]})
    rows=[]
    for f in m['families']:
        for arm in ARMS:
            row={k:m[k] for k in ('model_sha256','runner_sha256','seed')}
            row.update(family_id=f['family_id'],arm=arm,manifest_sha256=h(m),environment_sha256=f['environment_sha256'],
                       trace_sha256=h(['trace',f['family_id'],arm]),overhead=dict(zip(COSTS,(10,2,100))),targets=[])
            for j,t in enumerate(f['targets']):
                success=j < (2 if arm=='verified_reuse' else 1)
                row['targets'].append(dict(t,kernel='pass' if success else 'fail',dependency='pass' if success else 'unverified',
                      authorized=success,attempts=[{'artifact_sha256':h(['attempt',f['family_id'],arm,j]),'cost':dict(zip(COSTS,(10,1,100)))}]))
            rows.append(row)
    return m,rows


def test_public_fixture():
    m, rows=fixture(); r=summarize(m,rows)
    assert len(r)==160
    assert r['0','verified_reuse']['cost']==(50,6,500)
    s=paired_statistics(r)
    assert s['true_delta']==1 and s['sample_variance']==0 and s['conservative_risk_delta']==0
    assert s['wins']==32 and s['two_sided_sign_p']==F(1,2**31)


def test_unknown_charged():
    m, rows=fixture(); row=next(r for r in rows if r['arm']=='verified_reuse')
    row['targets'][0]['dependency']='unverified'
    r=summarize(m,rows)
    assert r[row['family_id'],row['arm']]['unknown']==1
    assert paired_statistics(r)['conservative_risk_delta']==F(1,32)


@pytest.mark.parametrize('mutation', ['missing_arm','missing_target','over_budget','bad_manifest','bad_env','bad_model','duplicate_run','bad_seed','no_log'])
def test_reject_malformed(mutation):
    m, rows=fixture(); r=rows[0]
    if mutation=='missing_arm': rows.pop()
    elif mutation=='missing_target': r['targets'].pop()
    elif mutation=='over_budget': r['overhead']['tokens']=101
    elif mutation=='bad_manifest': r['manifest_sha256']='0'*64
    elif mutation=='bad_env': r['environment_sha256']='0'*64
    elif mutation=='bad_model': r['model_sha256']='0'*64
    elif mutation=='duplicate_run': rows.append(deepcopy(r))
    elif mutation=='bad_seed': r['seed']+=1
    elif mutation=='no_log': r['targets'][0]['attempts']=[]
    with pytest.raises(ValueError): summarize(m,rows)
