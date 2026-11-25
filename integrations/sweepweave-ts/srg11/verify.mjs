// Standalone SRG-11 replay; pins source and compares the frozen receipt.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {runSuite} from './optimizer.mjs';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const expected=JSON.parse(fs.readFileSync(path.join(root,'output/evaluation_storyworld_reasoning/srg11.json'),'utf8'));
for(const [p,sha] of Object.entries(expected.source_blobs)){
 const bytes=fs.readFileSync(path.join(root,p));
 if(crypto.createHash('sha1').update('blob '+bytes.length+'\0').update(bytes).digest('hex')!==sha)throw Error('source drift '+p);
}
const source=fs.readFileSync(path.join(root,'integrations/sweepweave-ts/srg05/fixtures/reservoir-dogs.swmd.srg.md'),'utf8');
const r=runSuite({api,source}),{source_blobs,...rest}=expected;
if(JSON.stringify(r.receipt)!==JSON.stringify(rest))throw Error('receipt drift');
if(r.patched!==fs.readFileSync(new URL('./fixtures/reservoir-dogs-priority-candidate.swmd.md',import.meta.url),'utf8'))throw Error('candidate drift');
for(let i=0;i<r.economicCases.length;i++)if(r.economicCases[i].source!==fs.readFileSync(new URL('./fixtures/specialist-cal-'+i+'.swmd.md',import.meta.url),'utf8'))throw Error('economics fixture drift');
console.log(JSON.stringify({source_blobs_verified:true,receipt_reproduced:true,candidate_reproduced:true,
 economics_calibration_passes:r.receipt.economics.selected.passed,economics_validation_passes:r.receipt.economics.validation.selected.passed,
 story_validation_passes:r.receipt.story.validation.filter(v=>v.selected.pass).length},null,2));
