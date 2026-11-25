// Standalone replay of the pinned public calibration and public smoke controls.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {runSuite} from './curriculum.mjs';
import {scoreRows} from './local.mjs';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const expected=JSON.parse(fs.readFileSync(path.join(root,'output/evaluation_storyworld_reasoning/srg10.json'),'utf8'));
const scorer=JSON.parse(fs.readFileSync(path.join(root,'output/evaluation_storyworld_reasoning/srg10_scorer.json'),'utf8'));
for(const [p,sha] of Object.entries({...expected.source_blobs,...scorer.source_blobs})){
 const b=fs.readFileSync(path.join(root,p));
 if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('source blob drift '+p);
}
const jsonl=a=>a.map(x=>JSON.stringify(x)).join('\n')+'\n';
let total=0;
for(let i=0;i<expected.configurations.length;i++){
 const s=runSuite({...expected.configurations[i],api}),{role,...r}=expected.cohorts[i];
 if(JSON.stringify(r)!==JSON.stringify(s.receipt))throw Error('reference receipt drift '+role);
 total+=s.tasks.length;
 if(i===0){
   for(const [p,a] of [['public/planning_tasks.jsonl',s.tasks],['public/planning_gold.jsonl',s.gold]])if(fs.readFileSync(new URL('./'+p,import.meta.url),'utf8')!==jsonl(a))throw Error('public corpus drift '+p);
   const gold=scoreRows(s,s.gold.map(g=>({id:g.id,action:g.actions[0]})));
   const settle=scoreRows(s,s.tasks.map(t=>({id:t.id,action:t.observation.actions.find(a=>a.id.startsWith('settle_')).id})));
   const first=scoreRows(s,s.tasks.map(t=>({id:t.id,action:t.observation.actions[0].id})));
   if(gold.correct!==scorer.oracle.correct||gold.regret_numerator!==0||settle.utility_numerator!==scorer.always_settle.utility_numerator||first.utility_numerator!==scorer.first_legal_action.utility_numerator)throw Error('scorer drift');
 }
}
console.log(JSON.stringify({source_blobs_verified:true,reference_receipts_reproduced:true,public_corpus_reproduced:true,decision_rows:total},null,2));
