// Pinned SRG-13 replay; development and each validation cohort can run separately.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import {runSuite,validateOne} from './optimizer.mjs';
const root=fileURLToPath(new URL('../../../',import.meta.url));
const expected=JSON.parse(fs.readFileSync(path.join(root,'output/evaluation_storyworld_reasoning/srg13.json'),'utf8'));
for(const [p,sha] of Object.entries(expected.source_blobs)){
 const b=fs.readFileSync(path.join(root,p));
 if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('source drift '+p);
}
const source=fs.readFileSync(path.join(root,'integrations/sweepweave-ts/srg05/fixtures/reservoir-dogs.swmd.srg.md'),'utf8');
const args=process.argv.slice(2),mode=args[0]??'all';
if(!['all','development','validation0','validation1'].includes(mode))throw Error('expected all|development|validation0|validation1');
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
if(mode==='all'||mode==='development'){
 const r=runSuite({api,source,validate:false});
 const grid=r.receipt.grid.map(({metrics,...g})=>({...g,metrics:metrics.map(m=>({roots:m.roots,opportunities:m.opportunities,unique:m.unique,unique_truce:m.unique_truce,winning_actions:m.winning_actions,low_margin:m.low_margin,checks:m.checks}))}));
 for(const k of ['contract','provenance','grid_size','feasible_count','selected','development'])if(!eq(r.receipt[k],expected[k]))throw Error('development drift '+k);
 if(!eq(grid,expected.grid))throw Error('grid drift');
 if(r.candidate!==fs.readFileSync(new URL('./fixtures/reservoir-dogs-evidence-chain-candidate.swmd.md',import.meta.url),'utf8'))throw Error('candidate drift');
 if(!eq(r.patch_manifest,JSON.parse(fs.readFileSync(new URL('./fixtures/evidence-chain-patches.json',import.meta.url),'utf8'))))throw Error('patch drift');
 console.log(JSON.stringify({development_reproduced:true,grid:expected.grid_size,selected:expected.selected,feasible:expected.feasible_count}));
}
const {upstream,pair_scale,priority,offset}=expected.selected,params={upstream,pair_scale,priority,offset};
for(let i=0;i<expected.validation.length;i++)if(mode==='all'||mode==='validation'+i){
 const r=validateOne({api,source,params,cohort:expected.validation[i].cohort});
 if(!eq(r,expected.validation[i]))throw Error('validation drift '+i);
 console.log(JSON.stringify({validation:i,reproduced:true,pass:r.selected.pass,unique_truce:r.selected.unique_truce,ablations:r.ablations.probes}));
}
