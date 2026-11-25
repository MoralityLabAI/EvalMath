// SRG-09: standalone replay of pinned public diagnostic controls.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {evaluate} from '../srg04/swmd-runtime.mjs';
import {runSuite,KEYS} from './curriculum.mjs';
import {scoreEvidence,scoreRepairs} from './local.mjs';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const receipt=JSON.parse(fs.readFileSync(path.join(root,'output/evaluation_storyworld_reasoning/srg09.json'),'utf8'));
const scorer=JSON.parse(fs.readFileSync(path.join(root,'output/evaluation_storyworld_reasoning/srg09_scorer.json'),'utf8'));
for(const [p,sha] of Object.entries({...receipt.source_blobs,...scorer.source_blobs})){
 const b=fs.readFileSync(path.join(root,p));
 if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('source blob mismatch '+p);
}
const suite=runSuite({api,evaluate,seed:receipt.seed}),{source_blobs,...expected}=receipt;
if(JSON.stringify(suite.receipt)!==JSON.stringify(expected))throw Error('receipt drift');
const gold=scoreEvidence(suite,suite.gold.map(g=>({id:g.id,action:g.actions[0]})));
const majority=scoreEvidence(suite,suite.tasks.map(t=>({id:t.id,action:t.observation.values[KEYS.A]+t.observation.values[KEYS.B]+t.observation.values[KEYS.D]>0?'positive':'negative'})));
const author=scoreRepairs(suite,suite.repairs.map(r=>({id:r.id,...r.patch})));
const sham=scoreRepairs(suite,suite.repairs.map(r=>({id:r.id,...r.sham})));
if(gold.correct!==scorer.gold.correct||gold.utility_numerator!==scorer.gold.utility_numerator||gold.regret_numerator!==0||majority.utility_numerator!==scorer.majority.utility_numerator||author.passed!==288||author.intervention_passed!==2304||author.counts.pass!==6||sham.counts.fail!==6||sham.intervention_passed!==768)throw Error('scorer drift');
const jsonl=a=>a.map(x=>JSON.stringify(x)).join('\n')+'\n';
for(const [file,content] of [['public/evidence_tasks.jsonl',jsonl(suite.tasks)],['public/evidence_gold.jsonl',jsonl(suite.gold)],['public/author_tasks.jsonl',jsonl(suite.repairs.map(r=>r.task))],['public/author_gold.jsonl',jsonl(suite.repairs.map(r=>({id:r.id,...r.patch})))]]){
 if(fs.readFileSync(new URL('./'+file,import.meta.url),'utf8')!==content)throw Error('corpus drift '+file);
}
console.log(JSON.stringify({source_blobs_verified:true,reference_receipt_reproduced:true,public_corpus_reproduced:true,optimal_action_rows:gold.correct,provenance_interventions:author.intervention_passed},null,2));
