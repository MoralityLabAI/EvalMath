import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
import {SEED,worlds,rows,experiment,runtimeCheck,scorerCheck} from './benchmark.mjs';
const [cmd,dir,a,b]=process.argv.slice(2);
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const source=()=>hash(fs.readFileSync(new URL('./benchmark.mjs',import.meta.url)));
function corpus(seed,reps){return Array.from(worlds(seed,reps)).flatMap(w=>rows(w,undefined,undefined,true).map(r=>r.task)).map(JSON.stringify).join('\n')+'\n';}
if(cmd==='verify'){
 const e=JSON.parse(fs.readFileSync(new URL('../../../output/evaluation_storyworld_reasoning/srg19_belief_chains.json',import.meta.url),'utf8'));
 const r=experiment(e.seed,e.reps);r.swmd=runtimeCheck(runtime,e.seed);r.scorer=scorerCheck(e.seed);
 // Math.log2 and hypot are not required to be bitwise identical across JS engines.
 const cmp=(a,b,k='root')=>{if(typeof a==='number'&&typeof b==='number'&&(!Number.isInteger(a)||!Number.isInteger(b))){assert.ok(Math.abs(a-b)<=1e-10*Math.max(1,Math.abs(b)),k);return}if(a&&b&&typeof a==='object'&&typeof b==='object'){assert.deepEqual(Object.keys(a),Object.keys(b));for(const key of Object.keys(a))cmp(a[key],b[key],k+'.'+key)}else assert.deepEqual(a,b,k)};cmp(r,e);
 console.log(JSON.stringify({status:'pass',roots:r.roots,tests:r.tests,swmd:r.swmd,scorer:r.scorer}));
}else if(cmd==='stage'){
 const seed=a===undefined?SEED:Number(a),reps=b===undefined?1:Number(b),data=corpus(seed,reps);
 fs.mkdirSync(dir,{mode:0o700});fs.mkdirSync(path.join(dir,'model_input'),{mode:0o700});fs.mkdirSync(path.join(dir,'verifier'),{mode:0o700});
 fs.writeFileSync(path.join(dir,'model_input/planning.jsonl'),data,{flag:'wx',mode:0o600});fs.writeFileSync(path.join(dir,'verifier/manifest.json'),JSON.stringify({schema:'srg19.stage.v1',seed,reps,source:source(),sha256:hash(data)},null,2),{flag:'wx',mode:0o600});
}else if(cmd==='score'){
 const m=JSON.parse(fs.readFileSync(path.join(dir,'verifier/manifest.json'),'utf8'));
 if(m.schema!=='srg19.stage.v1'||m.source!==source()||m.sha256!==hash(corpus(m.seed,m.reps))||m.sha256!==hash(fs.readFileSync(path.join(dir,'model_input/planning.jsonl'))))throw Error('corpus drift');
 const submissions=fs.readFileSync(a,'utf8').split(/\r?\n/).filter(x=>x.trim()).map(x=>{try{return JSON.parse(x)}catch{return null}});
 console.log(JSON.stringify(experiment(m.seed,m.reps,submissions),null,2));
}else throw Error('verify | stage <new-dir> [seed] [reps] | score <dir> <submissions.jsonl>');
