// Node 20+, split modes for bounded replay. The world and runtime are pinned.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {developmentCohort,choose,validate,DESIGN} from './optimizer.mjs';
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
const receipt=k=>JSON.parse(read('output/evaluation_storyworld_reasoning/srg_ac03_'+k+'.json').toString('utf8'));
const [cmd='select',...extra]=process.argv.slice(2);
assert.equal(extra.length,0);
const runDev=(i,k)=>{const d=developmentCohort(source,DESIGN.dev[i]);assert.deepEqual(d,receipt(k),'development drift '+k);return d;};
const select=ds=>{const s=choose(ds);assert.deepEqual(s,receipt('selection'),'selection drift');return s;};
const checkVal=(ds,s)=>{const v=validate(source,ds,s);assert.deepEqual(v,receipt('validation'),'validation drift');return v;};
let result;
if(cmd==='dev_a'||cmd==='dev_b'){const i=cmd==='dev_a'?0:1,d=runDev(i,cmd);result={cohort:d.cohort,counts:d.counts,policies:d.results.length,baseline:d.baseline,envelope:d.envelope};}
else if(cmd==='select'||cmd==='validation'||cmd==='all'){
 const ds=cmd==='all'?[runDev(0,'dev_a'),runDev(1,'dev_b')]:[receipt('dev_a'),receipt('dev_b')],s=select(ds);
 if(cmd==='select')result=s;
 else{const v=checkVal(ds,s);result={frozen:v.frozen,pass:v.pass,counts:v.counts,cohorts:v.cohorts.map(c=>({seed:c.cohort.seed,pass:c.pass,oracle:c.metrics.frozen.goal4.value,transfer:c.metrics.frozen.transfer.successes,losses:c.metrics.frozen.losses}))};}
}else throw Error('usage: cli.mjs dev_a|dev_b|select|validation|all');
console.log(JSON.stringify({replay:'pass',...result},null,2));
