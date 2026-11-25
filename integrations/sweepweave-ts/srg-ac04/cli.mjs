import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {analyze,subsetAudit} from './benchmark.mjs';
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
const receipt=k=>JSON.parse(read('output/evaluation_storyworld_reasoning/srg_ac04_'+k+'.json').toString('utf8'));
const [cmd='verify',...extra]=process.argv.slice(2);assert.equal(extra.length,0);
assert.ok(['verify','primary','subsets'].includes(cmd),'usage: cli.mjs verify|primary|subsets');
const output={replay:'pass'};
if(cmd!=='subsets'){
 const a=analyze(source);assert.deepEqual(a,receipt('shortcut_resistance'),'primary drift');
 output.primary={counts:a.counts,flags:Object.fromEntries(Object.entries(a.upstream).map(([k,v])=>[k,v.review_flag]))};
}
if(cmd!=='primary'){
 const b=subsetAudit(source);assert.deepEqual(b,receipt('ledger_subsets'),'subset drift');
 output.subsets={counts:b.counts,min_records_95:b.min_records_95,minimal:b.minimal};
}
console.log(JSON.stringify(output,null,2));
