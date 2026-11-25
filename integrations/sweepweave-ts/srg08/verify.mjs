// SRG-08 reproducible public smoke verifier, no model/network calls.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {evaluate} from '../srg04/swmd-runtime.mjs';
import {makeSuite} from './curriculum.mjs';
import {scoreRows} from './local.mjs';
import {runTask,promptFor} from './run-local.mjs';
import {exportTrain} from './export-dg.mjs';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const expected=JSON.parse(fs.readFileSync(path.join(root,'output/evaluation_storyworld_reasoning/srg08.json'),'utf8'));
const runnerExpected=JSON.parse(fs.readFileSync(path.join(root,'output/evaluation_storyworld_reasoning/srg08_runner.json'),'utf8'));
const manifest=JSON.parse(fs.readFileSync(new URL('./public/datagoblin-ingestion.json',import.meta.url),'utf8'));
for(const [p,sha] of Object.entries({...expected.source_blobs,...runnerExpected.source_blobs,...manifest.source_git_blobs})){
 const bytes=fs.readFileSync(path.join(root,p));
 if(crypto.createHash('sha1').update('blob '+bytes.length+'\0').update(bytes).digest('hex')!==sha)throw Error('source blob mismatch '+p);
}
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
let done=0,streamCount=0;
for(const conf of expected.configurations){
 const s=makeSuite({split:conf.split,seed:conf.seed,api,evaluate,verify:true});
 const recorded=expected.cohorts.find(x=>x.split===s.split),{role,...rest}=recorded;
 if(!same(rest,s.receipt))throw Error('reference receipt mismatch '+s.split);
 const author=scoreRows(s,'author',s.authorGold.map(({id,formula})=>({id,formula})),api,evaluate);
 const player=scoreRows(s,'player',s.playerGold.map(({id,action})=>({id,action})),api,evaluate);
 const plan=scoreRows(s,'planning',s.planningGold.map(({id,actions})=>({id,action:actions[0]})),api,evaluate);
 const labels=new Map(s.playerGold.map(x=>[x.id,x])),submissions=[];
 for(const t of s.player.filter(x=>x.mode==='history')){
   const g=labels.get(t.id),width=g.family==='parity'?1:g.k;
   const cb=async messages=>{
     const p=JSON.parse(messages[1].content);
     if('cue' in p){
       if(Object.keys(p).sort().join(',')!=='cue,cue_number,memory,memory_bits,memory_max,memory_min,rule,total_cues')throw Error('memory packet leakage');
       const b=Number(p.cue>0);return {content:JSON.stringify({memory:g.family==='parity'?p.memory^b:p.memory|(b<<(p.cue_number-1))})};
     }
     if(Object.keys(p).sort().join(',')!=='memory,memory_bits,observation,rule,total_cues')throw Error('final packet leakage');
     const b=g.family==='parity'?p.memory:(p.memory>>(Math.round(p.observation.values['ledger.query']*g.k)-1))&1;
     return {content:JSON.stringify({action:p.observation.actions.find(a=>a.text===(b?'Report true.':'Report false.')).id})};
   };
   const out=await runTask('stream',t,cb,width);if(!out.submission||out.events.length!==g.k+1)throw Error('stream protocol failure');submissions.push(out.submission);
 }
 const stream=scoreRows(s,'stream',submissions,api,evaluate);
 if(author.correct!==3||player.correct!==192||plan.correct!==24||stream.correct!==96)throw Error('scorer failure '+s.split);
 const t=s.player.find(x=>x.mode==='history');
 const invalid=await runTask('stream',t,async()=>({content:'{"memory":2}'}),1);
 const zero=await runTask('stream',t,async msgs=>({content:JSON.stringify({action:JSON.parse(msgs[1].content).observation.actions[0].id})}),0);
 const malformed=await runTask('author',s.author[0],async()=>({content:'{"formula":"TRUE","extra":1}'}));
 if(invalid.submission||zero.events.length!==1||malformed.submission)throw Error('runner rejection control');
 if(s.split==='train_public'){
   const corpus=exportTrain(s,promptFor).map(x=>JSON.stringify(x)).join('\n')+'\n';
   const checked=fs.readFileSync(new URL('./public/srg08_train.jsonl',import.meta.url),'utf8');
   if(corpus!==checked)throw Error('Data Goblin corpus drift');
 }
 done++;streamCount+=stream.correct;
}
console.log(JSON.stringify({public_smoke_cohorts:done,stream_reference_correct:streamCount,source_blobs_verified:true,reference_receipts_reproduced:true,corpus_reproduced:true},null,2));
