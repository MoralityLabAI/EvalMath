import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {evaluate} from '../srg04/swmd-runtime.mjs';
import {runSuite} from './optimizer.mjs';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const expected=JSON.parse(fs.readFileSync(path.join(root,'output/evaluation_storyworld_reasoning/srg12.json'),'utf8'));
for(const [p,sha] of Object.entries(expected.source_blobs)){
 const b=fs.readFileSync(path.join(root,p));
 if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('blob drift '+p);
}
const source=fs.readFileSync(path.join(root,'integrations/sweepweave-ts/srg05/fixtures/reservoir-dogs.swmd.srg.md'),'utf8');
const r=runSuite({api,evaluate,source}),{source_blobs,...rest}=expected;
if(JSON.stringify(r.receipt)!==JSON.stringify(rest))throw Error('receipt drift');
if(r.candidate!==fs.readFileSync(new URL('./fixtures/reservoir-dogs-causal-candidate.swmd.md',import.meta.url),'utf8'))throw Error('candidate drift');
if(JSON.stringify(r.patches)!==JSON.stringify(JSON.parse(fs.readFileSync(new URL('./fixtures/causal-patches.json',import.meta.url),'utf8'))))throw Error('patch drift');
console.log(JSON.stringify({source_blobs_verified:true,receipt_reproduced:true,candidate_reproduced:true,grid:r.receipt.grid_size,feasible:r.receipt.feasible_count,outcome:r.receipt.outcome},null,2));
