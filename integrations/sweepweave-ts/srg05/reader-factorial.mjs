import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import * as api from './swmd-runtime-v2.mjs';
import {migrateReservoir} from './migrate-reservoir.mjs';
function factorial(api,migrate,d,readerText){
 const start=readerText.indexOf("class StoryworldEngine"),end=readerText.indexOf("// ========== UI CONTROLLER",start);
 if(start<0||end<0)throw Error("reader source not found");
 const Reader=new Function(readerText.slice(start,end)+"\nreturn StoryworldEngine;")();
 const w=api.compileV2(migrate(d).source),coords=Object.keys(w.coordinates);
 const keys=coords.map(k=>{const [owner,rest]=k.split(".");return [owner,[rest.split("[")[0],...Array.from(rest.matchAll(/\[([^\]]+)\]/g),m=>m[1])]];});
 const modes=[["reader",false,false],["signed_only",true,false],["minmax_only",false,true],["both",true,true]];
 function make(signed,minmax){
   const e=new Reader().load(d),orig=e.evalScript;
   e.evalScript=function(s){
     if(s&&typeof s==="object"&&s.operator_type==="Nudge"&&signed){
       const a=this.evalScript(s.operands[0]),b=this.evalScript(s.operands[1]);
       if(!Number.isFinite(a)||!Number.isFinite(b)||Math.abs(a)>1||Math.abs(b)>1)throw Error("invalid signed nudge");
       return Math.max(-1,Math.min(1,a*(1-Math.abs(b))+b));
     }
     if(s&&typeof s==="object"&&minmax&&["Minimum","Maximum"].includes(s.operator_type)){
       const a=s.operands.map(x=>this.evalScript(x));
       if(!a.length||a.some(x=>!Number.isFinite(x)))throw Error("invalid min/max");
       return s.operator_type==="Minimum"?Math.min(...a):Math.max(...a);
     }
     return orig.call(this,s);
   };
   return e;
 }
 let rng=0x53524705;const random=()=>{rng=(Math.imul(rng,1664525)+1013904223)>>>0;return rng;};
 const count=(o,k)=>o[k]=(o[k]||0)+1,results={},pairwise={},n=64;
 for(const [name] of modes)results[name]={};
 results.swmd={};
 const labels=Object.keys(results);
 for(let i=0;i<labels.length;i++)for(let j=i+1;j<labels.length;j++)pairwise[labels[i]+"__"+labels[j]]=0;
 const parity={trials:0,matched_steps:0,route_disagreements:0,menu_disagreements:0,reaction_disagreements:0,numeric_disagreements:0,max_coordinate_delta:0,first_mismatch:null};
 function readerMove(e,seq,t){
   const p=e.getCurrentEncounter();if(!p||!p.options.length)return {end:p?.id??"dead_end"};
   const opts=e.getVisibleOptions(p);if(!opts.length)return {end:"dead_end"};
   const a=opts[seq[t]%opts.length],r=e.selectReaction(a);
   if(!r)return {end:"no_reaction"};
   e.selectOption(a.id);const old=e.state.turn;e.continueToNext();
   if(e.state.turn===old)return {end:"no_wild_destination"};
   return {menu:opts.map(x=>x.id),reaction:r.id,next:e.state.currentEncounterId};
 }
 function rolloutReader(signed,minmax,seq){const e=make(signed,minmax);
   for(let t=0;t<seq.length;t++){const r=readerMove(e,seq,t);if(r.end)return r.end;}
   return "timeout";
 }
 function pairedBoth(seq){
   let s=api.initialV2(w),e=make(true,true),lastReader=null,lastSW=null;
   parity.trials++;
   for(let t=0;t<seq.length;t++){
     const obs=api.observeV2(w,s),r=readerMove(e,seq,t);
     if(r.end||obs.status!=="decision"){
       lastReader=r.end??"premature_swmd_end";lastSW=obs.status==="terminal"?s.encounter:obs.status;
       if(lastReader!==lastSW)parity.route_disagreements++;break;
     }
     const action=obs.actions[seq[t]%obs.actions.length],b=api.stepV2(w,s,action.id);
     parity.matched_steps++;
     const menuMismatch=r.menu.join(",")!==obs.actions.map(x=>x.id).join(",");
     const routeMismatch=r.next!==b.next.encounter,reactionMismatch=r.reaction!==b.id;
     const delta=Math.max(...coords.map((k,j)=>Math.abs(b.next.values[k]-e.getBNumber(keys[j][0],keys[j][1]))));
     parity.menu_disagreements+=Number(menuMismatch);parity.route_disagreements+=Number(routeMismatch);parity.reaction_disagreements+=Number(reactionMismatch);parity.numeric_disagreements+=Number(delta>1e-12);parity.max_coordinate_delta=Math.max(parity.max_coordinate_delta,delta);
     if((menuMismatch||routeMismatch||reactionMismatch||delta>1e-12)&&!parity.first_mismatch)parity.first_mismatch={turn:s.turn,encounter:s.encounter,menuMismatch,routeMismatch,reactionMismatch,delta};
     if(routeMismatch||menuMismatch){lastReader="diverged";lastSW="diverged";break;}
     s=b.next;
   }
   if(lastReader===null)lastReader="timeout";if(lastSW===null)lastSW="timeout";
   return {reader:lastReader,swmd:lastSW};
 }
 function rolloutSW(seq){let s=api.initialV2(w);for(let t=0;t<seq.length;t++){const o=api.observeV2(w,s);if(o.status!=="decision")return o.status==="terminal"?s.encounter:o.status;s=api.stepV2(w,s,o.actions[seq[t]%o.actions.length].id).next;}return "timeout";}
 for(let i=0;i<n;i++){
   const seq=Array.from({length:24},random),out={};
   for(const [name,signed,minmax] of modes){out[name]=rolloutReader(signed,minmax,seq);count(results[name],out[name]);}
   const p=pairedBoth(seq);out.swmd=p.swmd==="diverged"?rolloutSW(seq):p.swmd;count(results.swmd,out.swmd);
   for(let j=0;j<labels.length;j++)for(let k=j+1;k<labels.length;k++)pairwise[labels[j]+"__"+labels[k]]+=Number(out[labels[j]]!==out[labels[k]]);
 }
 return {evidence:"finite paired policy-index replay; isolated reader arithmetic mutations; no model inference",policy_sequences:n,results,pairwise_ending_disagreements:pairwise,reader_both_vs_swmd_prefix_parity:parity};
}
const root=process.argv[2];if(!root)throw Error('Usage: node reader-factorial.mjs <pinned GPTStoryworld checkout> [receipt]');
const files={"storyworlds/bonsai27_reservoir_dogs/reservoir_dogs_bonsai27.json":"f735f6198f2c7c1810d3feef13459632867cf1d9","storyworld_reader.html":"d43d9ab729206f1594ea7cee98918bc9ec92f267"};
const contents=Object.entries(files).map(([p,sha])=>{const b=fs.readFileSync(path.join(root,p));if(crypto.createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==sha)throw Error('blob mismatch '+p);return b.toString('utf8');});
const receipt={source_revision:'ee1c6918db77d1e0924877f59eca819bae3f1c8c',source_blobs:files,...factorial(api,migrateReservoir,JSON.parse(contents[0]),contents[1])};
const out=JSON.stringify(receipt,null,2)+'\n';if(process.argv[3])fs.writeFileSync(process.argv[3],out);else process.stdout.write(out);
