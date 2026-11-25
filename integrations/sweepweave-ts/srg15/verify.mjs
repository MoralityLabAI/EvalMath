// SRG-15 standalone replay, split by cohort for bounded execution.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {evaluateGridCohort,selectFromCohorts,validateRepair} from './radio-repair.mjs';
import {analyze,scorePolicy} from './belief-policy.mjs';
import {informativeScore} from './local.mjs';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const out='output/evaluation_storyworld_reasoning/';
const read=p=>fs.readFileSync(path.join(root,p),'utf8'),json=p=>JSON.parse(read(p));
const source=read('integrations/sweepweave-ts/srg13/fixtures/reservoir-dogs-evidence-chain-candidate.swmd.md');
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function pin(blobs){for(const [p,sha] of Object.entries(blobs)){const b=fs.readFileSync(path.join(root,p));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('source drift '+p);}}
const mode=process.argv[2]??'all';
if(!['all','radio_a','radio_b','radio_validation','belief'].includes(mode))throw Error('unknown replay mode');
for(const suffix of ['a','b'])if(mode==='all'||mode==='radio_'+suffix){
 const expected=json(out+'srg15_radio_grid_'+suffix+'.json');pin(expected.source_blobs);
 const actual=evaluateGridCohort({api,source,cohort:expected.cohort}),{source_blobs,...rest}=expected;
 if(!eq(actual,rest))throw Error('development grid drift '+suffix);
 console.log(JSON.stringify({radio_grid:suffix,reproduced:true,candidates:actual.grid.length}));
}
if(mode==='all'||mode==='radio_validation'){
 const d=json(out+'srg15_radio_development.json'),v=json(out+'srg15_radio_validation.json');pin(d.source_blobs);pin(v.source_blobs);
 const grids=['a','b'].map(s=>json(out+'srg15_radio_grid_'+s+'.json'));
 const selected=selectFromCohorts(source,grids);
 const {source_blobs,evidence,...rest}=d;if(!eq(selected.receipt,rest))throw Error('selection drift');
 if(selected.candidate!==fs.readFileSync(new URL('./fixtures/radio-repair-candidate.swmd.md',import.meta.url),'utf8'))throw Error('candidate drift');
 if(!eq(selected.patch,JSON.parse(fs.readFileSync(new URL('./fixtures/radio-patch.json',import.meta.url),'utf8'))))throw Error('patch drift');
 for(const row of v.validation){
   const actual=validateRepair({api,source,params:v.params,cohort:row.cohort});if(!eq(actual,row))throw Error('validation drift');
   console.log(JSON.stringify({radio_validation:row.cohort.seed,reproduced:true,pass:actual.selected.pass}));
 }
}
if(mode==='all'||mode==='belief'){
 const prior=json(out+'srg15_belief_policy.json'),sc=json(out+'srg15_policy_scorer.json');pin(prior.source_blobs);pin(sc.source_blobs);
 const {source_blobs,scorer,...rest}=prior,s=analyze({api,source});if(!eq(s.receipt,rest))throw Error('belief oracle drift');
 const e=s.exported,j=a=>a.map(x=>JSON.stringify(x)).join('\n')+'\n';
 if(j(e.tasks)!==fs.readFileSync(new URL('./public/planning_tasks.jsonl',import.meta.url),'utf8')||j(e.gold)!==fs.readFileSync(new URL('./public/planning_gold.jsonl',import.meta.url),'utf8'))throw Error('policy corpus drift');
 const results={oracle:informativeScore(e,e.gold.map(g=>({id:g.id,action:g.winners[0]})),scorePolicy),first_legal:informativeScore(e,e.tasks.map(t=>({id:t.id,action:t.observation.actions[0].id})),scorePolicy),malformed:informativeScore(e,[{id:e.tasks[0].id,action:'bad'},{id:e.tasks[1].id,action:'bad'},{id:e.tasks[1].id,action:'bad'}],scorePolicy)};
 if(!eq(results,sc.results))throw Error('scorer drift');
 console.log(JSON.stringify({belief_reproduced:true,tasks:e.tasks.length,oracle_successes:results.oracle.actual_rollout.successes,first_legal_successes:results.first_legal.actual_rollout.successes}));
}
