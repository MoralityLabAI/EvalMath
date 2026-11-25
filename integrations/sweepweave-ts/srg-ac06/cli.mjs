import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {calibration,validation} from './certificate.mjs';
import {build,pilot,score,receipt as ladderReceipt} from './ladder.mjs';
const root=new URL('../../../',import.meta.url),read=f=>fs.readFileSync(new URL(f,root));
const pins=[
  {
    "path": "integrations/sweepweave-ts/srg04/swmd-runtime.mjs",
    "sha": "ba4401a824f8cfdb4ae25525973a989c0047168e"
  },
  {
    "path": "integrations/sweepweave-ts/srg05/swmd-runtime-v2.mjs",
    "sha": "a687ad75e3c88683936b4b3d24324ced3f4cf874"
  },
  {
    "path": "integrations/sweepweave-ts/srg13/fixtures/reservoir-dogs-evidence-chain-candidate.swmd.md",
    "sha": "64d40ef2d0953a6034a92c4250c006f59f533fb2"
  }
];
for(const {path,sha} of pins){
 const b=read(path),h=crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex');
 assert.equal(h,sha,'source drift '+path);
}
const source=read(pins[2].path).toString('utf8');
const expected=k=>JSON.parse(read('output/evaluation_storyworld_reasoning/srg_ac06_'+k+'.json').toString('utf8'));
const [cmd='verify',a,b,c,...extra]=process.argv.slice(2);assert.equal(extra.length,0);
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const jsonl=rows=>rows.map(x=>JSON.stringify(x)).join('\n')+'\n';
const generators=()=>Object.fromEntries(['certificate.mjs','ladder.mjs','cli.mjs'].map(f=>[f,sha(fs.readFileSync(new URL(f,import.meta.url)))]));
function corpus(mode){assert.ok(['pilot','full'].includes(mode),'mode');const e=build();return mode==='pilot'?pilot(e):e;}
let out;
if(cmd==='calibration'||cmd==='validation'||cmd==='ladder'||cmd==='verify'){
 assert.equal(a,undefined);
 out={replay:'pass'};
 if(cmd==='calibration'||cmd==='verify'){const d=calibration(source);assert.deepEqual(d,expected('calibration'),'calibration drift');out.calibration={selected:d.selected,minimum:d.subset.full_min};}
 if(cmd==='validation'||cmd==='verify'){const d=validation(source,expected('calibration'));assert.deepEqual(d,expected('validation'),'validation drift');out.validation={selected:d.selected,cohorts:d.cohorts.map(x=>({cohort:x.cohort,minimum:x.subset.full_min,novel:x.novel.roots,transfer:x.transfer.frozen.successes}))};}
 if(cmd==='ladder'||cmd==='verify'){const d=ladderReceipt();assert.deepEqual(d,expected('ladder'),'ladder drift');out.ladder={counts:d.counts,pilot:d.corpus.pilot.rows,full:d.corpus.rows};}
}else if(cmd==='stage'&&a&&!c){
 const mode=b??'pilot',e=corpus(mode),dir=path.resolve(a),files={'model_input/planning.jsonl':jsonl(e.tasks),'verifier/gold.jsonl':jsonl(e.gold)};
 fs.mkdirSync(dir,{mode:0o700});fs.mkdirSync(path.join(dir,'model_input'),{mode:0o700});fs.mkdirSync(path.join(dir,'verifier'),{mode:0o700});
 const m={schema:'ac06.ladder.stage.v1',mode,rows:e.tasks.length,pins,generators:generators(),files:{}};
 for(const [f,s] of Object.entries(files)){fs.writeFileSync(path.join(dir,f),s,{flag:'wx',mode:0o600});m.files[f]={sha256:sha(s),bytes:Buffer.byteLength(s)};}
 fs.writeFileSync(path.join(dir,'verifier/manifest.json'),JSON.stringify(m,null,2)+'\n',{flag:'wx',mode:0o600});out={mode,rows:e.tasks.length,output:dir};
}else if(cmd==='score'&&a&&b&&!c){
 const dir=path.resolve(a),m=JSON.parse(fs.readFileSync(path.join(dir,'verifier/manifest.json'),'utf8'));
 assert.equal(m.schema,'ac06.ladder.stage.v1');assert.deepEqual(m.pins,pins);assert.deepEqual(m.generators,generators());
 const e=corpus(m.mode);assert.equal(e.tasks.length,m.rows);
 for(const [f,s] of Object.entries({'model_input/planning.jsonl':jsonl(e.tasks),'verifier/gold.jsonl':jsonl(e.gold)})){
  const raw=fs.readFileSync(path.join(dir,f));assert.equal(raw.length,m.files[f].bytes);assert.equal(sha(raw),m.files[f].sha256);assert.equal(sha(s),m.files[f].sha256);
 }
 const sub=fs.readFileSync(b,'utf8').split(/\r?\n/).filter(x=>x.trim()).map(x=>{try{return JSON.parse(x);}catch{return null;}});
 out={mode:m.mode,...score(e,sub)};
}else throw Error('usage: cli.mjs calibration|validation|ladder|verify | stage <new-dir> [pilot|full] | score <staged-dir> <submissions.jsonl>');
console.log(JSON.stringify(out,null,2));
