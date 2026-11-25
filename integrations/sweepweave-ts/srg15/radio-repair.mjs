// SRG-15A: narrow radio-effect authoring intervention on the frozen SRG-13 candidate.
// Keep all source evidence, routes, gates, reaction scores, prose and other fields fixed.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
const RADIO="page_cadillac_trunk",GOAL="page_secret_undercover_truce",SIRENS="page_sirens_at_the_rollup_door",TRUCE="opt_page_sirens_at_the_rollup_door_2";
const S="char_pink.Rat_Suspicion",B="char_blonde.Sadistic_Escalation",L="char_white.Crew_Loyalty",T="char_pink.Timeline_Record";
const REACTION="rxn_page_cadillac_trunk_2_0";
const fail=m=>{throw Error("SRG15A: "+m);},same=(a,b)=>JSON.stringify(a)===JSON.stringify(b),bit=x=>Number(Boolean(x)),sum=(a,f)=>a.reduce((n,x)=>n+f(x),0);
const C=x=>"C("+Number(x.toFixed(8))+")",P=x=>"P("+x+")";
export const CONTRACT=Object.freeze({
 development:[{seed:0x53521411,n:96},{seed:0x53521412,n:96}],
 validation:[{seed:0x53521511,n:128},{seed:0x53521512,n:128}],
 grid:{retention:[0,.04,.08,.12],restraint:[0,.04,.08]},
 targets:{h3_gain_min:0,unique_truce_gain_min:.05,random_goal_gain_min:0,max_delta:.12,max_step_energy_ratio:1.75,max_reaction_edit:1},
 scope:"only the existing suspicion and escalation effects in the radio-inspection reaction 2_0; modifiers require previously recorded timeline. No unconditioned guilt claim or new evidence, unchanged reaction scores, narrative, gates and routes.",
 selection:"maximize full development cohorts, then passed individual constraints, then smallest normalized edit; freeze before validation; diagnostic fallback if no feasible edit."
});
function seqs(c){let x=c.seed>>>0;const r=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};return Array.from({length:c.n},()=>Array.from({length:24},r));}
const terminal=(w,s)=>Object.keys(w.pages[s.encounter].options).length===0;
const menu=(api,w,s)=>api.observeV2(w,s).actions.map(a=>a.id);
function choose(api,w,s,n){const a=menu(api,w,s);if(!a.length)fail("empty menu");return a[Math.floor(n*a.length/4294967296)];}
function step(api,w,s,a){return api.stepV2(w,s,a);}
export function patchRadio(source,p){
 const lines=source.split("\n"),i=lines.findIndex(x=>x.startsWith("ORX opt_"+RADIO+"_2/"+REACTION+" "));
 if(i<0)fail("target reaction missing");
 const before=lines[i],m=before.match(/ \| E:(.*?) \| D:/);
 if(!m)fail("effects");
 const es=m[1].split("; "),j=es.findIndex(x=>x.startsWith("SET "+S+" = ")),k=es.findIndex(x=>x.startsWith("SET "+B+" = "));
 if(j<0||k<0||es[j].split("C(-0.05)").length!==2||es[k].split("C(0.11)").length!==2)fail("unexpected original coefficients");
 // Timeline credit is normalized. The radio observes exposure rather than
 // a culprit; retention preserves unresolved suspicion conditional on the
 // already-recorded timeline. Restraint is a separate author hypothesis.
 const warrant="MIN(C(1),MUL(C(8),"+P(T)+"))";
 if(p.retention)es[j]=es[j].replace("C(-0.05)","ADD(C(-0.05),MUL("+C(p.retention)+","+warrant+"))");
 if(p.restraint)es[k]=es[k].replace("C(0.11)","SUB(C(0.11),MUL("+C(p.restraint)+","+warrant+"))");
 const after=before.replace(" | E:"+m[1]+" | D:"," | E:"+es.join("; ")+" | D:");
 lines[i]=after;
 return {source:lines.join("\n"),patch:before===after?null:{line:i+1,before,after}};
}
function firstRadio(api,w,words){
 let s=api.initialV2(w);
 for(let j=0;j<words.length;j++){
   if(s.encounter===RADIO)return {s,j,words};
   if(terminal(w,s)||s.encounter===SIRENS)return null;
   s=step(api,w,s,choose(api,w,s,words[j])).next;
 }
 return null;
}
function reach(api,w,s,h){
 if(terminal(w,s))return s.encounter===GOAL;
 if(!h)return false;
 return menu(api,w,s).some(a=>reach(api,w,step(api,w,s,a).next,h-1));
}
function audit(api,w,s,h){
 if(!s)return {attainable:0,unique_truce:0};
 const win=menu(api,w,s).filter(a=>reach(api,w,step(api,w,s,a).next,h-1));
 return {attainable:bit(win.length),unique_truce:bit(win.length===1&&win[0]===TRUCE)};
}
function dist(v){return (v[L]-Math.max(-.53,Math.min(.77,v[L])))**2+Math.max(0,.08-v[S])**2+Math.max(0,v[B]-.35)**2;}
function arm(api,w,r,a){
 let b=step(api,w,r.s,a),s=b.next,first=b,root=null;
 for(let j=r.j+1;j<r.words.length;j++){
   if(s.encounter===SIRENS&&!root)root=s;
   if(terminal(w,s))break;
   s=step(api,w,s,choose(api,w,s,r.words[j])).next;
 }
 const h1=audit(api,w,root,1),h3=audit(api,w,root,3);
 return {h1:h1.attainable,h3:h3.attainable,unique_truce:h1.unique_truce,random_goal:bit(s.encounter===GOAL),complete:bit(terminal(w,s)),reached:bit(root),gate_distance:root?dist(root.values):null,first,root};
}
function cache(api,w,c){
 const roots=seqs(c).map(words=>firstRadio(api,w,words)).filter(Boolean);
 return roots.map(r=>{
   const a=menu(api,w,r.s);
   if(a.length!==3||a.some((x,i)=>x!=="opt_"+RADIO+"_"+i))fail("radio menu");
   return {r,arms:a.map(id=>arm(api,w,r,id))};
 });
}
const METRICS=["h1","h3","unique_truce","random_goal","complete","reached"];
function score(api,base,w,rows,p){
 const o={prefixes:rows.length,edited:0,selected_radio_reaction:{},contrast:Object.fromEntries(METRICS.map(k=>[k,0])),on:Object.fromEntries(METRICS.map(k=>[k,0])),off:Object.fromEntries(METRICS.map(k=>[k,0])),
 max_delta:0,max_energy_ratio:1,max_step_effect_error:0,unchanged_non_target:0,zero_warrant_checks:0,route_changes:0,off_replay_checks:0};
 for(const {r,arms} of rows){
   // Other options cannot trigger the changed reaction at this first site.
   // They may revisit the site later; therefore replay *all* arms in candidate.
   const next=menu(api,w,r.s).map((id,i)=>p.retention||p.restraint?arm(api,w,r,id):arms[i]);
   for(let i=0;i<3;i++){
     const x=arms[i].first,y=next[i].first;
     if(x.id!==y.id||x.next.encounter!==y.next.encounter)fail("initial reaction or route changed");
     const keys=Object.keys(x.next.values);
     if(x.id!==REACTION){
       if(!same(x.next.values,y.next.values)||x.squared_step_energy!==y.squared_step_energy)fail("out-of-scope numeric change");
       o.unchanged_non_target++;
     }else{
       o.edited+=bit(!same(x.next.values,y.next.values));
       for(const k of keys)if(k!==S&&k!==B&&x.next.values[k]!==y.next.values[k])fail("unexpected write");
       const warrant=Math.min(1,8*r.s.values[T]);
       const nudge=(x,a)=>Math.max(-1,Math.min(1,x*(1-Math.abs(a))+a));
       const predB=nudge(r.s.values[B],.11+.08*r.s.values[S]-p.restraint*warrant);
       const predS=Math.max(-.95,Math.min(.95,r.s.values[S]-.05+p.retention*warrant+.06*predB));
       const err=Math.max(Math.abs(predB-y.next.values[B]),Math.abs(predS-y.next.values[S]));
       o.max_step_effect_error=Math.max(o.max_step_effect_error,err);
       if(err>1e-12)fail("independent effect disagreement");
       if(!warrant){if(!same(x.next.values,y.next.values))fail("zero warrant changed");o.zero_warrant_checks++;}
       o.max_delta=Math.max(o.max_delta,...keys.map(k=>Math.abs(x.next.values[k]-y.next.values[k])));
       o.max_energy_ratio=Math.max(o.max_energy_ratio,x.squared_step_energy?y.squared_step_energy/x.squared_step_energy:Infinity);
     }
   }
   const x=next[2];o.selected_radio_reaction[x.first.id]=(o.selected_radio_reaction[x.first.id]??0)+1;
   for(const k of METRICS){const off=(next[0][k]+next[1][k])/2;o.on[k]+=x[k];o.off[k]+=off;o.contrast[k]+=x[k]-off;}
 }
 const t=CONTRACT.targets,den=o.prefixes;
 o.mean_delta=Object.fromEntries(METRICS.map(k=>[k,o.contrast[k]/den]));
 o.checks={h3:o.mean_delta.h3>=t.h3_gain_min,unique_truce:o.mean_delta.unique_truce>=t.unique_truce_gain_min,random_goal:o.mean_delta.random_goal>=t.random_goal_gain_min,
 displacement:o.max_delta<=t.max_delta+1e-12,energy:o.max_energy_ratio<=t.max_step_energy_ratio,complete:o.on.complete===den&&o.off.complete===den,reached:o.on.reached===den&&o.off.reached===den};
 o.pass=Object.values(o.checks).every(Boolean);
 return o;
}
export function selectRepair({api=runtime,source}){
 const base=api.compileV2(source),dev=CONTRACT.development.map(c=>({cohort:c,rows:cache(api,base,c)})),grid=[];
 for(const retention of CONTRACT.grid.retention)for(const restraint of CONTRACT.grid.restraint){
   const params={retention,restraint},p=patchRadio(source,params),w=api.compileV2(p.source);
   const metrics=dev.map(d=>score(api,base,w,d.rows,params));
   grid.push({params,metrics,full:sum(metrics,m=>bit(m.pass)),checks:sum(metrics,m=>Object.values(m.checks).filter(Boolean).length),cost:Math.round(retention/.04)+Math.round(restraint/.04)});
 }
 const ranked=[...grid].sort((a,b)=>b.full-a.full||b.checks-a.checks||a.cost-b.cost||a.params.retention-b.params.retention||a.params.restraint-b.params.restraint);
 const selected=ranked[0],p=patchRadio(source,selected.params);
 return {receipt:{contract:CONTRACT,grid,selected,feasible_count:grid.filter(r=>r.full===dev.length).length},candidate:p.source,patch:p.patch};
}
export function validateRepair({api=runtime,source,params,cohort}){
 const base=api.compileV2(source),rows=cache(api,base,cohort),p=patchRadio(source,params),w=api.compileV2(p.source);
 return {cohort,baseline:score(api,base,base,rows,{retention:0,restraint:0}),selected:score(api,base,w,rows,params)};
}
