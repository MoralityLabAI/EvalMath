import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
import {seed0,worlds,rows,experiment,runtimeCheck} from './benchmark.mjs';
const [cmd,dir,a,b]=process.argv.slice(2);
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const source=()=>hash(fs.readFileSync(new URL('./benchmark.mjs',import.meta.url)));
function corpus(seed,reps){return Array.from(worlds(seed,reps)).flatMap(w=>rows(w).map(r=>r.task)).map(JSON.stringify).join('\n')+'\n';}
if(cmd==='verify'){
 const e=JSON.parse(fs.readFileSync(new URL('../../../output/evaluation_storyworld_reasoning/srg17b_controlled_gap.json',import.meta.url),'utf8'));
 const r=experiment(e.seed,e.reps);r.swmd=runtimeCheck(runtime,e.seed);
 for(const k of ['schema','seed','reps','cells','contracts','tests','controls','swmd'])assert.deepEqual(r[k],e[k]);
 assert.equal(r.groups.length,e.groups.length);
 for(let i=0;i<r.groups.length;i++){assert.deepEqual(r.groups[i].config,e.groups[i].config);for(const [m,v] of Object.entries(e.groups[i].controls))assert.deepEqual(e.group_columns.map(k=>r.groups[i].controls[m][k]),v);}
 console.log(JSON.stringify({status:'pass',cells:r.cells,contracts:r.contracts,tests:r.tests,swmd:r.swmd}));
}else if(cmd==='stage'){
 const seed=a===undefined?seed0:Number(a),reps=b===undefined?1:Number(b),data=corpus(seed,reps);
 fs.mkdirSync(dir,{mode:0o700});fs.mkdirSync(path.join(dir,'model_input'),{mode:0o700});fs.mkdirSync(path.join(dir,'verifier'),{mode:0o700});
 fs.writeFileSync(path.join(dir,'model_input/planning.jsonl'),data,{flag:'wx',mode:0o600});fs.writeFileSync(path.join(dir,'verifier/manifest.json'),JSON.stringify({schema:'srg17b.stage.v1',seed,reps,source:source(),sha256:hash(data)},null,2),{flag:'wx',mode:0o600});
}else if(cmd==='score'){
 const m=JSON.parse(fs.readFileSync(path.join(dir,'verifier/manifest.json'),'utf8'));
 if(m.schema!=='srg17b.stage.v1'||m.source!==source()||m.sha256!==hash(corpus(m.seed,m.reps))||m.sha256!==hash(fs.readFileSync(path.join(dir,'model_input/planning.jsonl'))))throw Error('corpus drift');
 const submissions=fs.readFileSync(a,'utf8').split(/\r?\n/).filter(x=>x.trim()).map(x=>{try{return JSON.parse(x)}catch{return null}});
 console.log(JSON.stringify(experiment(m.seed,m.reps,submissions),null,2));
}else throw Error('verify | stage <new-dir> [seed] [reps] | score <dir> <submissions.jsonl>');
