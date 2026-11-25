import fs from 'node:fs';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {evaluate} from '../srg04/swmd-runtime.mjs';
import {makeSuite} from './curriculum.mjs';
function exhaustive(suite,api,evaluate){
 const checks=[];
 for(const c of suite.cases.filter(c=>c.h===1)){
   const t=suite.tables.get(c.family+"/"+c.k),w=api.compileV2(c.render()),p=w.pages[c.pages[0]];
   const a=p.options[c.trueAction].reactions.find(r=>r.to===c.success).gate;
   const b=p.options[c.falseAction].reactions.find(r=>r.to===c.success).gate;
   const v=Object.create(null);
   let correct=0;
   for(let m=0;m<t.n;m++){
     for(let j=0;j<c.k;j++)v[c.keys[j]]=(m>>>j)&1?c.amplitude:-c.amplitude;
     const x=evaluate(a,v),y=evaluate(b,v);
     correct+=Number(x===Boolean(t.labels[m])&&y===!Boolean(t.labels[m]));
   }
   if(correct!==t.n)throw Error("full truth table mismatch "+c.family+"/"+c.k);
   checks.push({family:c.family,k:c.k,amplitude:c.amplitude,rows:t.n,matched:correct});
 }
 return checks;
}
const configs=[{"split":"train_public","seed":1397884673},{"split":"calibration_public","seed":1397884674},{"split":"evaluation_private","seed":1397884675}];
const checks=configs.flatMap(c=>exhaustive(makeSuite({...c,verify:false,api}),api,evaluate));
const receipt={evidence:"exhaustive compiled reaction-gate truth tables, one amplitude and one renamed case per family/K; public smoke",source_blobs:{"integrations/sweepweave-ts/srg04/swmd-runtime.mjs":"ba4401a824f8cfdb4ae25525973a989c0047168e","integrations/sweepweave-ts/srg05/swmd-runtime-v2.mjs":"a687ad75e3c88683936b4b3d24324ced3f4cf874","integrations/sweepweave-ts/srg07/curriculum.mjs":"037bf16dbfcb6f789a09cf2227387ede2f6c22e0"},checks,total:checks.reduce((n,c)=>n+c.rows,0),matched:checks.reduce((n,c)=>n+c.matched,0)};
const output=JSON.stringify(receipt,null,2)+'\n';if(process.argv[2])fs.writeFileSync(process.argv[2],output);else process.stdout.write(output);
