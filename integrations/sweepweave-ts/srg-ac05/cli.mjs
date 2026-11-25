import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {developmentCohort,select,validation,pairAudit,DESIGN} from './hardening.mjs';
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
const receipt=k=>JSON.parse(read('output/evaluation_storyworld_reasoning/srg_ac05_'+k+'.json').toString('utf8'));
const [cmd='select',...extra]=process.argv.slice(2);assert.equal(extra.length,0);
const runDev=(i,k)=>{const d=developmentCohort(source,DESIGN.dev[i]);assert.deepEqual(d,receipt(k),'development drift '+k);return d;};
const choose=ds=>{const s=select(ds);assert.deepEqual(s,receipt('selection'),'selection drift');return s;};
const validate=s=>{const v=validation(source,s);assert.deepEqual(v,receipt('validation'),'validation drift');return v;};
const pairs=()=>{const p=pairAudit(source);assert.deepEqual(p,receipt('pairs'),'pair drift');return p;};
let output;
if(cmd==='dev_a'||cmd==='dev_b'){const d=runDev(cmd==='dev_a'?0:1,cmd);output={cohort:d.cohort,counts:d.counts,candidates:d.candidates.length,baseline:d.baseline.full,mixed_gap:d.mixed.gap};}
else if(cmd==='pairs'){const p=pairs();output={counts:p.counts,cohorts:p.cohorts.map(x=>({cohort:x.cohort,pairs:x.pairs,ceiling:x.ceiling}))};}
else if(['select','validation','all'].includes(cmd)){
 const ds=cmd==='all'?[runDev(0,'dev_a'),runDev(1,'dev_b')]:[receipt('dev_a'),receipt('dev_b')],s=choose(ds);
 output={total:s.total,feasible:s.feasible,hardening_feasible:s.hardening_feasible,frozen:s.frozen};
 if(cmd!=='select'){const v=validate(s);output.validation={pass:v.pass,cohorts:v.cohorts.map(x=>({cohort:x.cohort,full:x.candidate.full,weak_gap:x.candidate.gap,mixed_gap:x.mixed.gap,mixed_pairs:x.mixed.strict.pairs}))};}
 if(cmd==='all')output.pairs=pairs().cohorts.map(x=>({cohort:x.cohort,pairs:x.pairs,ceiling:x.ceiling}));
}else throw Error('usage: cli.mjs dev_a|dev_b|select|validation|pairs|all');
console.log(JSON.stringify({replay:'pass',...output},null,2));
