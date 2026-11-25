import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import * as R from '../srg18/benchmark.mjs';
import * as G from '../srg21/benchmark.mjs';
import * as F from './frozen-features.mjs';
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
import {freeze,audit,stage,score} from './benchmark.mjs';
const read=p=>JSON.parse(fs.readFileSync(new URL('../../../output/evaluation_storyworld_reasoning/'+p,import.meta.url),'utf8'));
const frozen=read('srg23_authoring_freeze.json'),expected=read('srg23_authoring_audit.json'),[cmd,dir,c,t,sub]=process.argv.slice(2);
const jsonl=a=>a.map(x=>JSON.stringify(x)).join('\n')+'\n';
const hash=x=>crypto.createHash('sha256').update(x).digest('hex');
const cmp=(a,b,k='root')=>{if(typeof a==='number'&&typeof b==='number'&&(!Number.isInteger(a)||!Number.isInteger(b))){assert.ok(Math.abs(a-b)<=1e-8*Math.max(1,Math.abs(b)),k);return}if(a&&b&&typeof a==='object'&&typeof b==='object'){assert.deepEqual(Object.keys(a),Object.keys(b));for(const key of Object.keys(a))cmp(a[key],b[key],k+'.'+key)}else assert.deepEqual(a,b,k)};
if(cmd==='verify'){const f=freeze(R,G,F);cmp(f,frozen);const e=audit(frozen,R,runtime);e.scorer={};for(const tier of ['low','mid','high']){const rows=stage(frozen,R,0,tier),full=score(frozen,R,0,tier,rows.map(r=>({id:r.gold.id,action:r.gold.winners[0]}))),bad=score(frozen,R,0,tier,[]);assert.equal(full.earned,full.opt);assert.equal(full.valid,full.rows);assert.equal(bad.valid,0);assert.equal(bad.earned,0);e.scorer[tier]={rows:rows.length,oracle:'pass',missing:'pass'}}cmp(e,expected);console.log(JSON.stringify({status:'pass',promote:e.promote,gates:e.cohorts.map(c=>c.gates)}));}
else if(cmd==='stage'){const cohort=Number(c),tier=t,data=jsonl(stage(frozen,R,cohort,tier).map(r=>r.task));fs.mkdirSync(dir,{mode:0o700});fs.mkdirSync(dir+'/model_input',{mode:0o700});fs.mkdirSync(dir+'/verifier',{mode:0o700});fs.writeFileSync(dir+'/model_input/planning.jsonl',data,{flag:'wx',mode:0o600});fs.writeFileSync(dir+'/verifier/manifest.json',JSON.stringify({cohort,tier,hash:hash(data)},null,2),{flag:'wx',mode:0o600});}
else if(cmd==='score'){const m=JSON.parse(fs.readFileSync(dir+'/verifier/manifest.json','utf8')),data=jsonl(stage(frozen,R,m.cohort,m.tier).map(r=>r.task));assert.equal(hash(data),m.hash);assert.equal(hash(fs.readFileSync(dir+'/model_input/planning.jsonl')),m.hash);const rows=fs.readFileSync(c,'utf8').split(/\r?\n/).filter(x=>x.trim()).map(x=>{try{return JSON.parse(x)}catch{return null}});console.log(JSON.stringify(score(frozen,R,m.cohort,m.tier,rows),null,2));}else throw Error('verify | stage <new-dir> <cohort 0|1> <low|mid|high> | score <dir> <submissions.jsonl>');
