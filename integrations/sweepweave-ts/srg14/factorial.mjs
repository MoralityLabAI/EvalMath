// SRG-14B: 2^3 dynamic-policy factorial on the frozen original/candidate.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
export const DESIGN=Object.freeze({
 seed:0x53521431,campaigns:64,maxActions:24,
 sites:[
   {page:"page_pink_ambush_theory",off:2,on:0},
   {page:"page_cadillac_trunk",off:1,on:2},
   {page:"page_eddie_and_blonde_story",off:0,on:2}
 ],
 goal:"page_secret_undercover_truce",sirens:"page_sirens_at_the_rollup_door",
 truce:"opt_page_sirens_at_the_rollup_door_2",
 ledger:["char_pink.Timeline_Record","char_pink.Radio_Record","char_pink.Review_Request"],
 semantics:"Each bit selects an off/on policy at the first reached registered site before first sirens. Unvisited sites receive no intervention. Later choices use the same absolute-index exogenous words. All eight masks are evaluated per campaign. Public diagnostic."
});
const G=DESIGN.goal,F=DESIGN.sirens,T=DESIGN.truce;
const fail=m=>{throw Error("SRG14B: "+m);};
const sum=(a,f)=>a.reduce((n,x)=>n+f(x),0),bit=x=>Number(Boolean(x));
const term=(w,s)=>Object.keys(w.pages[s.encounter].options).length===0;
function words(){let x=DESIGN.seed>>>0;const r=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};return Array.from({length:DESIGN.campaigns},()=>Array.from({length:DESIGN.maxActions},r));}
function actions(api,w,s){return api.observeV2(w,s).actions.map(x=>x.id);}
function step(api,w,s,a){return api.stepV2(w,s,a).next;}
function reached(api,w,s,h,counts){
 counts.nodes++;if(term(w,s))return s.encounter===G;if(!h)return false;
 let win=false;for(const a of actions(api,w,s))win=reached(api,w,step(api,w,s,a),h-1,counts)||win;return win;
}
function audit(api,w,s,h,counts){
 const win=actions(api,w,s).filter(a=>reached(api,w,step(api,w,s,a),h-1,counts));
 return {attainable:bit(win.length),unique_truce:bit(win.length===1&&win[0]===T)};
}
function ablate(s){const v={...s.values};for(const k of DESIGN.ledger)if(Object.hasOwn(v,k))v[k]=0;return {...s,values:v};}
function roll(api,w,seq,mask,counts){
 let s=api.initialV2(w),applied=0,first=null,unavailable=0;
 for(let j=0;j<seq.length;j++){
   if(term(w,s))break;
   if(s.encounter===F&&!first)first=s;
   const menu=actions(api,w,s);
   if(!menu.length)fail("empty menu");
   let a=menu[Math.floor(seq[j]*menu.length/4294967296)];
   if(!first){const i=DESIGN.sites.findIndex(p=>p.page===s.encounter);
     if(i>=0&&!(applied&(1<<i))){
       const p=DESIGN.sites[i],id="opt_"+p.page+"_"+((mask>>i&1)?p.on:p.off);
       if(menu.includes(id))a=id;else{unavailable|=1<<i;}
       applied|=1<<i;
     }
   }
   s=step(api,w,s,a);
 }
 const h1=first?audit(api,w,first,1,counts):{attainable:0,unique_truce:0},h3=first?audit(api,w,first,3,counts):{attainable:0,unique_truce:0},abl=first?audit(api,w,ablate(first),1,counts):{attainable:0,unique_truce:0};
 if(h1.attainable>h3.attainable)fail("horizon monotonicity");
 return {mask,applied,unavailable,reached:bit(first),complete:bit(term(w,s)),random_goal:bit(s.encounter===G),
   h1:h1.attainable,h3:h3.attainable,unique_truce:h1.unique_truce,unique_truce_deleted:abl.unique_truce};
}
// Exact Harsanyi/Mobius dividends on each finite 8-arm potential-outcome
// table, and permutation-averaged Shapley credit. Sixth-units are integers.
const names=["timeline","radio","review"];
function pop(m){let n=0;for(;m;m>>>=1)n+=m&1;return n;}
function effect(values){
 const div=values.map((v,m)=>{let d=0;for(let sub=m;;sub=(sub-1)&m){d+=((pop(m)-pop(sub))%2?-1:1)*values[sub];if(!sub)break;}return d;});
 const shapley6=names.map(()=>0);
 for(let i=0;i<3;i++)shapley6[i]=sum(div.map((v,m)=>({v,m})),x=>x.m&(1<<i)?x.v*6/pop(x.m):0);
 if(sum(shapley6,x=>x)!==6*(values[7]-values[0]))fail("Shapley efficiency");
 return {div,shapley6};
}
export function runFactorial({api=runtime,source,world}){
 const w=api.compileV2(source),counts={nodes:0},seqs=words(),metrics=["h1","h3","unique_truce","unique_truce_deleted","random_goal"];
 const tables=Array.from({length:8},(_,mask)=>({mask,arms:0,complete:0,reached:0,unavailable:0,applied_counts:[0,0,0],...Object.fromEntries(metrics.map(k=>[k,0]))}));
 const effects=Object.fromEntries(metrics.map(k=>[k,{dividends:Array(8).fill(0),shapley6:[0,0,0],efficiency_checks:0,positive_interaction_campaigns:0,negative_interaction_campaigns:0}]));
 for(const seq of seqs){
   const arms=Array.from({length:8},(_,mask)=>roll(api,w,seq,mask,counts));
   for(const a of arms){const t=tables[a.mask];t.arms++;t.complete+=a.complete;t.reached+=a.reached;t.unavailable+=bit(a.unavailable);for(let j=0;j<3;j++)t.applied_counts[j]+=bit(a.applied&(1<<j));for(const k of metrics)t[k]+=a[k];}
   for(const k of metrics){const r=effect(arms.map(a=>a[k])),e=effects[k];r.div.forEach((x,i)=>e.dividends[i]+=x);r.shapley6.forEach((x,i)=>e.shapley6[i]+=x);e.efficiency_checks++;
     const interaction=sum(r.div.filter((_,m)=>pop(m)>1),x=>x);e.positive_interaction_campaigns+=bit(interaction>0);e.negative_interaction_campaigns+=bit(interaction<0);}
 }
 for(const k of metrics){
   const e=effects[k],v=tables.map(t=>t[k]),direct=effect(v);
   if(JSON.stringify(e.dividends)!==JSON.stringify(direct.div)||JSON.stringify(e.shapley6)!==JSON.stringify(direct.shapley6))fail("factorial aggregation");
   e.shapley=e.shapley6.map(x=>x/(6*DESIGN.campaigns));
   e.total_change=(v[7]-v[0])/DESIGN.campaigns;
   e.interaction_dividends=e.dividends.map((x,m)=>pop(m)>1?x/DESIGN.campaigns:null);
 }
 return {world,design:DESIGN,counts:{campaigns:seqs.length,rollouts:8*seqs.length,reachability_nodes:counts.nodes},tables,effects};
}
