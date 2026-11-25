import fs from 'node:fs';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import * as api from '../srg05/swmd-runtime-v2.mjs';
import * as scoped from './scoped-admission.mjs';
function robust(api,sc,source,order){
 const {compileV2,initialV2,observeV2,stepV2}=api, w=compileV2(source);
 const manifest=sc.directWindowManifest(w),scopedStep=sc.makeScopedStepper(w,manifest);
 const strict=compileV2(source.replace("direct: explicit","direct: strict"));
 let widened=source.replace("direct: explicit","direct: strict");
 for(const x of manifest.windows)widened=widened.replace(`ENC ${x.id} turn=${x.original_earliest}..${x.latest} |`,`ENC ${x.id} turn=${x.direct_earliest}..${x.latest} |`);
 const wide=compileV2(widened);
 const terminal=p=>Object.keys(w.pages[p].options).length===0;
 const endings=Object.values(w.pages).filter(p=>terminal(p.id)).map(p=>p.id),sirens="page_sirens_at_the_rollup_door";
 const add=(o,k,n=1)=>o[k]=(o[k]??0)+n;
 function roll(world,words,mode,keep=false){
   let s=initialV2(world);const trace=[],roots=[];let exceptions=0;
   for(const word of words){
     const ob=observeV2(world,s);
     if(ob.status!=="decision")return {end:ob.status==="terminal"?s.encounter:ob.status,trace,roots,exceptions};
     if(keep&&s.encounter===sirens)roots.push(s);
     const a=ob.actions[Math.floor(word*ob.actions.length/4294967296)].id;
     try{
       const b=mode==="scoped"?scopedStep(s,a):stepV2(world,s,a);
       trace.push([s.encounter,a,b.id,b.next.encounter,b.next.turn]);
       if(b.scoped_admission?.exception)exceptions++;
       s=b.next;
     }catch(e){if(!/blocked_destination|no_wild_destination|scoped admission blocked|no eligible reaction/.test(String(e)))throw e;
       return {end:String(e).split(": ").at(-1),trace,roots,exceptions};}
   }
   return {end:"timeout",trace,roots,exceptions};
 }
 function cohort(seed,n){
   let x=seed>>>0;const random=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};
   const m={seed,n,original:{},strict:{},global_window:{},scoped:{},path_changes_global:0,path_changes_scoped:0,ending_changes_global:0,ending_changes_scoped:0,scoped_exceptions:0,scoped_terminal:0,strict_terminal:0,original_terminal:0,global_terminal:0,selected_steps:0};
   const roots=[];
   for(let i=0;i<n;i++){
     const words=Array.from({length:24},random),o=roll(w,words,"original",true),s=roll(strict,words,"strict"),g=roll(wide,words,"wide"),r=roll(w,words,"scoped");
     roots.push(...o.roots);m.selected_steps+=o.trace.length;
     for(const [k,v] of [["original",o],["strict",s],["global_window",g],["scoped",r]])add(m[k],v.end);
     const term=v=>Number(Object.hasOwn(w.pages,v.end)&&terminal(v.end));
     m.original_terminal+=term(o);m.strict_terminal+=term(s);m.global_terminal+=term(g);m.scoped_terminal+=term(r);
     m.path_changes_global+=Number(JSON.stringify(o.trace)!==JSON.stringify(g.trace));
     m.path_changes_scoped+=Number(JSON.stringify(o.trace)!==JSON.stringify(r.trace));
     m.ending_changes_global+=Number(o.end!==g.end);m.ending_changes_scoped+=Number(o.end!==r.end);
     m.scoped_exceptions+=r.exceptions;
   }
   return {metrics:m,roots};
 }
 const cal=cohort(0x5e412ac7,64),val=cohort(0x91e10da5,64);
 // Deterministic finite lookahead for all six declared goal endpoints.
 // Goal is provided externally, not an inferred narrative utility.
 function outcomeSets(s,h){
   if(terminal(s.encounter))return new Set([s.encounter]);
   if(h===0)return new Set();
   const out=new Set();
   for(const a of observeV2(w,s).actions){
     let b;try{b=stepV2(w,s,a.id);}catch(e){if(/blocked_destination|no_wild_destination|no eligible reaction/.test(String(e)))continue;throw e;}
     for(const t of outcomeSets(b.next,h-1))out.add(t);
   }return out;
 }
 function labels(roots,h){
   return roots.map(s=>{
     const actions=observeV2(w,s).actions.map(a=>a.id),sets={};
     for(const a of actions){
       try{sets[a]=[...outcomeSets(stepV2(w,s,a).next,h-1)];}
       catch(e){if(!/blocked_destination|no_wild_destination|no eligible reaction/.test(String(e)))throw e;sets[a]=[];}
     }
     return {state:s,actions,sets};
   });
 }
 function expand(rows){return rows.flatMap(r=>endings.map(goal=>({state:r.state,actions:r.actions,goal,wins:r.actions.filter(a=>r.sets[a].includes(goal))})));}
 function cell(r,keys,bits){
   const bins=2**bits;return JSON.stringify([r.goal,r.state.turn,r.actions,...keys.map(k=>Math.min(bins-1,Math.floor((r.state.values[k]+1)*bins/2)))]);
 }
 function group(rows,keys,bits){
   const m=new Map();
   for(const r of rows){const key=cell(r,keys,bits);if(!m.has(key))m.set(key,{actions:r.actions,counts:Object.fromEntries(r.actions.map(a=>[a,0]))});const g=m.get(key);for(const a of r.wins)g.counts[a]++;}
   return m;
 }
 const best=g=>[...g.actions].sort((a,b)=>g.counts[b]-g.counts[a]||a.localeCompare(b))[0];
 function table(c,v,keys,bits){
   const cg=group(c,keys,bits),vg=group(v,keys,bits),fallback=group(c,[],bits);let oracle=0,lookup=0,unseen=0,random=0;
   for(const g of vg.values())oracle+=Math.max(...Object.values(g.counts),0);
   for(const r of v){const g=cg.get(cell(r,keys,bits));if(!g)unseen++;const f=g??fallback.get(cell(r,[],bits));const a=f?best(f):[...r.actions].sort()[0];lookup+=Number(r.wins.includes(a));random+=r.actions.length?r.wins.length/r.actions.length:0;}
   const feasible=v.filter(r=>r.wins.length).length;
   return {k:keys.length,bits,validation_pairs:v.length,full_information_opportunities:feasible,validation_partition_oracle:oracle,calibration_lookup:lookup,random_first_action_expected_successes:Number(random.toFixed(9)),unseen,cal_cells:cg.size,val_cells:vg.size};
 }
 const multi=[];
 for(const h of [1,2,3]){
   const c=expand(labels(cal.roots,h)),v=expand(labels(val.roots,h)),full=v.filter(r=>r.wins.length).length;
   const rows=[0,1,2,4,8,16,32,50].map(k=>table(c,v,order.slice(0,k),2));
   const by_goal={};for(const g of endings){const rr=v.filter(r=>r.goal===g);by_goal[g]={roots:rr.length,opportunity:rr.filter(r=>r.wins.length).length,unique_winning_first_action:rr.filter(r=>r.wins.length===1).length};}
   multi.push({horizon:h,validation_root_goal_pairs:v.length,full_information_opportunities:full,by_goal,curve:rows,public_only:table(c,v,Object.keys(w.coordinates).filter(k=>w.coordinates[k].visibility==="public"),2)});
 }
 return {evidence:"additional deterministic xorshift32 paired replay; bounded full-state continuation oracle on real source",policy:"xorshift32 with floor(u*n), 24 draws per campaign",manifest,calibration:cal.metrics,validation:val.metrics,root_counts:[cal.roots.length,val.roots.length],multi_goal:multi};
}
const root=fileURLToPath(new URL('../../../',import.meta.url));
const blobs={"integrations/sweepweave-ts/srg04/swmd-runtime.mjs":"ba4401a824f8cfdb4ae25525973a989c0047168e","integrations/sweepweave-ts/srg05/swmd-runtime-v2.mjs":"a687ad75e3c88683936b4b3d24324ced3f4cf874","integrations/sweepweave-ts/srg05/fixtures/reservoir-dogs.swmd.srg.md":"cb174a3efb031eaa046b01a2acc526ef7d122345","output/evaluation_storyworld_reasoning/srg06.json":"6cfa2f07351026b63147d95e22a37f7b38b22808","integrations/sweepweave-ts/srg06/scoped-admission.mjs":"bf07eb3ade9b1deecd86aff45297f39e8459400c"};
for(const [p,sha] of Object.entries(blobs)){const b=fs.readFileSync(path.join(root,p));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('source blob mismatch '+p);}
const src=fs.readFileSync(path.join(root,"integrations/sweepweave-ts/srg05/fixtures/reservoir-dogs.swmd.srg.md"),'utf8');
const prior=JSON.parse(fs.readFileSync(path.join(root,"output/evaluation_storyworld_reasoning/srg06.json"),'utf8'));
const receipt=JSON.stringify({source_blobs:blobs,...robust(api,scoped,src,prior.difficulty.static_feature_order)},null,2)+'\n';
if(process.argv[2])fs.writeFileSync(process.argv[2],receipt);else process.stdout.write(receipt);
