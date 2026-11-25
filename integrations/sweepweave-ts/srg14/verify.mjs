// Reproduce one cohort or the complete joint policy factorial from pinned files.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {CONTRACT,evaluateWorld} from './counterfactual.mjs';
import {runFactorial} from './factorial.mjs';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const output='output/evaluation_storyworld_reasoning/';
const sources={original_srg05:'integrations/sweepweave-ts/srg05/fixtures/reservoir-dogs.swmd.srg.md',srg13_candidate:'integrations/sweepweave-ts/srg13/fixtures/reservoir-dogs-evidence-chain-candidate.swmd.md'};
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const json=p=>JSON.parse(read(p)),eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function pin(blobs){for(const [p,sha] of Object.entries(blobs)){const b=fs.readFileSync(path.join(root,p));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('blob drift '+p);}}
const summary=json(output+'srg14.json');pin(summary.receipt_blobs);
const mode=process.argv[2]??'all';
const cohorts=['original_a','original_b','candidate_a','candidate_b'];
if(!['all','factorial',...cohorts].includes(mode))throw Error('unknown replay selection');
for(const name of cohorts)if(mode==='all'||mode===name){
 const expected=json(output+'srg14_'+name+'.json');
 pin(expected.source_blobs);const {source_blobs,contract,...result}=expected;
 if(!eq(contract,CONTRACT))throw Error('contract drift');
 const actual=evaluateWorld({api,source:read(sources[result.world]),cohort:result.cohort,worldLabel:result.world}).result;
 if(!eq(actual,result))throw Error('cohort drift '+name);
 console.log(JSON.stringify({cohort:name,reproduced:true,arms:actual.counts.arms}));
}
if(mode==='all'||mode==='factorial'){
 const expected=json(output+'srg14_factorial.json');pin(expected.source_blobs);
 for(const w of expected.worlds){const actual=runFactorial({api,source:read(sources[w.world]),world:w.world});if(!eq(actual,w))throw Error('factorial drift '+w.world);console.log(JSON.stringify({factorial:w.world,reproduced:true,rollouts:w.counts.rollouts}));}
}
