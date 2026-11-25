// SRG-AC02: bounded redistribution of existing evidence pair effects.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
import {evaluate} from '../srg04/swmd-runtime.mjs';
const ck=(v,m)=>{if(!v)throw Error("AC02: "+m);};
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const eps=1e-10,goal="page_secret_undercover_truce",page="page_sirens_at_the_rollup_door",truce="opt_"+page+"_2",ready="char_white.Truce_Coordination";
const ledger=["char_pink.Timeline_Record","char_pink.Radio_Record","char_pink.Review_Request"];
const goalKeys=["char_pink.Rat_Suspicion","char_blonde.Sadistic_Escalation","char_white.Crew_Loyalty"];
const pairs=[[0,1],[0,2],[1,2]];
const unit=[1,1,1];
export const DESIGN={development:[{seed:0x53522201,n:64},{seed:0x53522202,n:64}],validation:[{seed:0x53522211,n:128},{seed:0x53522212,n:128}],prefix_budget:24,H:3,max_energy_ratio:1.25,max_concentration_increase:.025};
export function grid(){
 const out=[];for(const a of [2,3,4,5,6])for(const b of [2,3,4,5,6]){const c=12-a-b;if(c>=2&&c<=6)out.push([a/4,b/4,c/4]);}return out;
}
const rhs=w=>"MUL(C(0.125),MIN(C(1),MUL(C(64),ADD("+pairs.map(([i,j],k)=>"MUL("+ (w[k]===1?"":"C("+w[k]+"),")+"P("+ledger[i]+"),P("+ledger[j]+"))").join(",")+"))))";
export function patch(source,w){
 ck(grid().some(v=>eq(v,w)),"weights outside grid");
 const old="SET "+ready+" = "+rhs(unit),neu="SET "+ready+" = "+rhs(w),lines=source.split("\n");let n=0;
 const out=lines.map(l=>{
  if(!l.startsWith("ORX "+truce+"/"))return l;
  ck(l.split(old).length===2,"stale patch precondition");n++;return l.replace(old,neu);
 });
 ck(n===3,"expected three truce writes");return out.join("\n");
}
function rng(seed){let x=seed>>>0||1;return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};}
function roots(api,w,c){
 const rand=rng(c.seed),out=[],missed=[];
 for(let rep=0;rep<c.n;rep++){
  const words=Array.from({length:DESIGN.prefix_budget},rand);let s=api.initialV2(w),history=[],energy=[];
  for(const word of words){
   if(s.encounter===page){out.push({rep,s,history,energy});break;}
   const o=api.observeV2(w,s);if(o.status!=="decision")break;
   const a=o.actions[Math.floor(word*o.actions.length/4294967296)].id,b=api.stepV2(w,s,a);
   history.push(a);energy.push(b.squared_step_energy);s=b.next;
  }
  if(out.at(-1)?.rep!==rep)missed.push(rep);
 }
 return {out,missed};
}
function tree(api,w,s,h,c){
 const o=api.observeV2(w,s),n={o,terminal:o.status==="terminal",reward:Number(o.status==="terminal"&&s.encounter===goal),children:{},full:0};
 c.nodes++;
 if(n.terminal){n.full=n.reward;return n;}
 if(h===0||o.status!=="decision")return n;
 for(const a of o.actions){
  const step=api.stepV2(w,s,a.id);n.children[a.id]=tree(api,w,step.next,h-1,c);
 }
 n.full=Math.max(0,...Object.values(n.children).map(x=>x.full));return n;
}
function one(n){return Object.fromEntries(Object.entries(n.children).map(([a,t])=>[a,t.terminal?t.reward:0]));}
function three(n){return Object.fromEntries(Object.entries(n.children).map(([a,t])=>[a,t.full]));}
function info(q){const vs=Object.values(q);return vs.length>1&&Math.max(...vs)>Math.min(...vs);}
function projection(n,mode){
 const o=n.o,v={};for(const k of ledger){ck(Object.hasOwn(o.values,k),"ledger visibility");v[k]=o.values[k];}
 if(mode==="goal4")for(const k of goalKeys){ck(Object.hasOwn(o.values,k),"goal visibility");v[k]=Math.min(15,Math.floor((o.values[k]+1)*8));}
 return JSON.stringify([o.encounter,o.turn,o.status,o.actions,v]);
}
function group(ns,mode){const m=new Map();for(const n of ns){const k=projection(n,mode),a=m.get(k)??[];a.push(n);m.set(k,a);}return [...m.values()];}
export function belief(ns,mode,h=3){
 const c={cells:0,informative:0,root_cells:0,root_informative:0};
 function solve(xs,d){
  if(xs.every(n=>n.terminal))return xs.reduce((v,n)=>v+n.reward,0);
  if(d===0||xs.every(n=>n.o.status==="dead_end"))return 0;
  const ids=Object.keys(xs[0].children);
  ck(ids.length&&xs.every(n=>eq(Object.keys(n.children),ids)),"unequal observed menus");
  const scores=ids.map(a=>group(xs.map(n=>n.children[a]),mode).reduce((v,g)=>v+solve(g,d-1),0));
  const inf=Math.max(...scores)>Math.min(...scores);c.cells++;c.informative+=Number(inf);
  if(d===h){c.root_cells++;c.root_informative+=Number(inf);}
  return Math.max(...scores);
 }
 const val=group(ns,mode).reduce((v,g)=>v+solve(g,h),0),full=ns.reduce((v,n)=>v+n.full,0);
 ck(val<=full,"belief ceiling");return {value:val,full,gap:full-val,...c};
}
function energyShare(es,e){const sum=es.reduce((v,x)=>v+x,e);return sum?Math.max(e,...es)/sum:0;}
function readiness(w,v){
 return .125*Math.min(1,64*pairs.reduce((s,[i,j],k)=>s+w[k]*v[i]*v[j],0));
}
function provenance(world,w,evalExpr){
 // The untouched record writes are MAX(old, fixed allowed positive credit).
 const allowed=ledger.map(k=>new Set([0]));
 for(const p of Object.values(world.pages))for(const o of Object.values(p.options))for(const r of o.reactions)for(const e of r.effects){
  if(!ledger.includes(e.key))continue;
  ck(e.value.op==="MAX"&&e.value.args.length===2&&e.value.args[0].op==="pointer"&&e.value.args[0].key===e.key&&e.value.args[1].op==="literal","nonmonotone record write");
  const n=Number(e.value.args[1].literal);ck(n>=0&&n<=.125,"record range");allowed[ledger.indexOf(e.key)].add(n);
 }
 const all=allowed.map(x=>[...x].sort((a,b)=>a-b));let combinations=0,checks=0;
 const exprs=world.pages[page].options[truce].reactions.map(r=>r.effects.find(e=>e.key===ready).value);
 for(const a of all[0])for(const b of all[1])for(const c of all[2]){
  const v=[a,b,c],x=readiness(w,v),env=Object.fromEntries(ledger.map((k,i)=>[k,v[i]]));combinations++;
  ck(x>=0&&x<=.125&&v.filter(t=>t>0).length>=2||x===0,"warrant");
  for(const e of exprs){ck(Math.abs(evalExpr(e,env)-x)<=eps,"formula mismatch");checks++;}
  for(let i=0;i<3;i++)for(const y of all[i].filter(y=>y>=v[i])){
   const u=v.slice();u[i]=y;ck(readiness(w,u)>=x-eps,"monotonicity");checks++;
  }
 }
 return {allowed:all,combinations,checks};
}
function profile(api,w,rs,weights,base=null){
 let nodes=0,invalid=0,lost=0,newTruceUnwarranted=0,scope=0,maxEnergy=1,maxConc=0,maxReady=0,actions=0,forced=0,changed=0,newTruce=0;
 const trees=[],rows=[],witnesses=[];
 for(const r of rs){
  let n,au;
  try{const c={nodes:0};n=tree(api,w,r.s,3,c);nodes+=c.nodes;au=api.auditV2(w,r.s).actions;}
  catch(e){invalid++;rows.push({rep:r.rep,invalid:String(e).slice(0,250)});continue;}
  const h1=one(n),h3=three(n),b=base?.rows.find(x=>x.rep===r.rep),branches={};
  if(b){ck(eq(Object.keys(h3),Object.keys(b.h3)),"root menu drift");lost+=Number(b.full>n.full);}
  const values=ledger.map(k=>r.s.values[k]),warrant=values.filter(x=>x>0).length>=2;
  for(const a of au){
   actions++;ck(a.status==="ok","selected invalid root action");
   const s=a.branches.find(x=>x.id===a.selected);
   const next=s.next,energy=s.squared_step_energy,step={reaction:a.selected,next,energy,route:next.encounter};
   branches[a.id]=step;
   if(a.id===truce){
    for(const z of a.branches){
     forced++;ck(z.status==="ok","invalid forced truce reaction");
     const x=z.next.values[ready];ck(Math.abs(x-readiness(weights,values))<=eps,"ordered readiness");
     maxReady=Math.max(maxReady,x);ck(x>=0&&x<=.125+eps&&4*x<=.5+eps,"readiness cap");
     if(!warrant)ck(x===0,"record warrant");
    }
   }
   if(b){
    const old=b.branches[a.id];
    if(a.id!==truce){if(!eq(step,old))scope++;}
    else{
     const strip=x=>Object.fromEntries(Object.entries(x.next.values).filter(([k])=>k!==ready));
     if(a.selected!==old.reaction||!eq(strip(step),strip(old))||!eq(next.spools,old.next.spools)||next.turn!==old.next.turn)scope++;
     const ratio=old.energy?energy/old.energy:energy?Infinity:1;
     maxEnergy=Math.max(maxEnergy,ratio);
     maxConc=Math.max(maxConc,energyShare(r.energy,energy)-energyShare(r.energy,old.energy));
     if(old.route!==step.route)changed++;
     if(h3[a.id]>b.h3[a.id]){
      newTruce++;if(!warrant)newTruceUnwarranted++;
      if(witnesses.length<12)witnesses.push({rep:r.rep,history:r.history,records:values,old_route:old.route,new_route:step.route,old_h1:b.h1,new_h1:h1,old_h3:b.h3,new_h3:h3,old_readiness:old.next.values[ready],new_readiness:next.values[ready]});
     }
    }
   }
  }
  const win=Object.keys(h3).filter(a=>h3[a]===1),uniqueTruce=win.length===1&&win[0]===truce;
  trees.push(n);rows.push({rep:r.rep,h1,h3,full:n.full,informative:info(h3),uniqueTruce,branches});
 }
 const g=belief(trees,"goal4"),l=belief(trees,"ledger"),n=rows.filter(x=>!x.invalid).length;
 ck(l.value<=g.value,"nested observations");
 const out={roots:rs.length,valid:n,invalid,nodes,actions,forced,full:g.full,h1:rows.filter(x=>x.h1&&Object.values(x.h1).includes(1)).length,informative:rows.filter(x=>x.informative).length,uniqueTruce:rows.filter(x=>x.uniqueTruce).length,goal4:g,ledger:l,lost,newTruce,newTruceUnwarranted,scope,maxEnergy,maxConc,maxReady,changed,witnesses,rows};
 if(base){
  const checks={valid:invalid===0&&n===rs.length,scope:scope===0,provenance:newTruceUnwarranted===0,energy:maxEnergy<=DESIGN.max_energy_ratio+eps,concentration:maxConc<=DESIGN.max_concentration_increase+eps,full:lost===0,goal4:g.value>=base.goal4.value,ledger:l.value>=base.ledger.value,informative:out.informative>=base.informative};
  out.checks=checks;out.pass=Object.values(checks).every(Boolean);out.delta={goal4:g.value-base.goal4.value,ledger:l.value-base.ledger.value,info:out.informative-base.informative,full:g.full-base.full};
 }
 return out;
}
function brief(p){const {rows,...r}=p;return r;}
function rank(a){
 const d=a.cohorts.map(x=>x.delta),w=a.weights;
 return [Math.min(...d.map(x=>x.goal4)),d.reduce((v,x)=>v+x.goal4,0),Math.min(...d.map(x=>x.ledger)),d.reduce((v,x)=>v+x.info,0),-w.reduce((v,x)=>v+Math.abs(x-1),0)];
}
function better(a,b){const x=rank(a),y=rank(b);for(let i=0;i<x.length;i++)if(x[i]!==y[i])return x[i]>y[i];return false;}
export function development(source,api=runtime,evalExpr=evaluate){
 const world=api.compileV2(source),rs=DESIGN.development.map(c=>roots(api,world,c));
 const base=rs.map(x=>profile(api,world,x.out,unit));ck(base.every(x=>x.invalid===0),"baseline invalid");
 const candidates=[];
 for(const w of grid()){
  const patched=patch(source,w),model=api.compileV2(patched),p=provenance(model,w,evalExpr);
  if(eq(w,unit))ck(patched===source,"unit patch differs");
  const cohorts=rs.map((x,i)=>brief(profile(api,model,x.out,w,base[i])));
  candidates.push({weights:w,provenance:p,cohorts,pass:cohorts.every(x=>x.pass)});
 }
 let best=candidates.find(x=>eq(x.weights,unit));for(const a of candidates)if(a.pass&&better(a,best))best=a;
 const improved=best.cohorts.every(x=>x.delta.goal4>0);
 const frozen=improved?best.weights:unit;
 return {design:DESIGN,cohorts:rs.map((x,i)=>({missed:x.missed,...brief(base[i])})),candidates,feasible:candidates.filter(x=>x.pass).length,selected:best.weights,improved,frozen};
}
export function validation(source,frozen,api=runtime,evalExpr=evaluate){
 const a=api.compileV2(source),b=api.compileV2(patch(source,frozen)),prov=provenance(b,frozen,evalExpr),cohorts=[];
 for(const c of DESIGN.validation){
  const x=roots(api,a,c),y=roots(api,b,c);ck(eq(x,y),"candidate prefix drift");
  const p=profile(api,a,x.out,unit),q=profile(api,b,x.out,frozen,p);
  ck(p.invalid===0,"baseline invalid");
  cohorts.push({seed:c.seed,missed:x.missed,matched_prefixes:x.out.length,base:brief(p),candidate:brief(q),pass:q.pass&&q.delta.goal4>0});
 }
 return {frozen,provenance:prov,cohorts,pass:!eq(frozen,unit)&&cohorts.every(x=>x.pass)};
}


// Post-development analytical envelope. This does not select a new candidate.
function reads(n,k){return n.op==="pointer"&&n.key===k||(n.args??[]).some(x=>reads(x,k));}
export function envelope(source,api=runtime){
 const base=api.compileV2(source),ws=grid(),models=ws.map(w=>api.compileV2(patch(source,w)));
 // In this source, changing readiness can change only the secret ending's
 // wild priority. It cannot change eligibility, reaction selection or others'
 // priorities. Check that the only read is the designated priority.
 let priorityReads=0;
 for(const p of Object.values(base.pages)){
  ck(!reads(p.gate,ready),"ready affects eligibility");
  if(reads(p.priority,ready)){ck(p.id===goal,"unexpected ready priority");priorityReads++;}
  for(const o of Object.values(p.options)){
   ck(!reads(o.visible,ready)&&!reads(o.performable,ready),"ready affects menu");
   for(const r of o.reactions){
    ck(!reads(r.gate,ready)&&!reads(r.desirability,ready),"ready affects reaction");
    ck(r.effects.every(e=>!reads(e.value,ready)),"ready read in ordered effects");
   }
  }
 }
 const q=base.pages[goal].priority;ck(priorityReads===1&&q.op==="ADD"&&q.args.length===2&&!reads(q.args[0],ready)&&q.args[1].op==="MUL"&&q.args[1].args.length===2&&Number(q.args[1].args[0].literal)===4&&q.args[1].args[1].key===ready,"priority slope");
 ck(base.pages[page].options[truce].reactions.every(r=>r.to==="wild"),"expected wild truce routing");
 const out=[];
 for(const cohort of DESIGN.development){
  const rs=roots(api,base,cohort).out;let eligible=0,baseTruce=0,maxTruce=0,minTruce=0,newTruce=0,baseGoal=0,maxGoal=0,constant=0,variable=0,zero=0,saturated=0,interior=0;const witnesses=[],patterns={};
  for(const z of rs){
   const v=ledger.map(k=>z.s.values[k]),vals=ws.map(w=>readiness(w,v)),x=readiness(unit,v),lo=Math.min(...vals),hi=Math.max(...vals);
   if(x===0)zero++;else if(x===.125)saturated++;else interior++;
   if(lo===hi)constant++;else variable++;
   const pat=v.join(",");patterns[pat]=(patterns[pat]??0)+1;
   const menu=api.observeV2(base,z.s).actions.map(a=>a.id);
   const alt=menu.filter(a=>a!==truce).some(a=>api.stepV2(base,z.s,a).next.encounter===goal);
   if(!menu.includes(truce)){baseGoal+=Number(alt);maxGoal+=Number(alt);continue;}
   eligible++;
   const bm=api.stepV2(base,z.s,truce),lm=api.stepV2(models[vals.indexOf(lo)],z.s,truce),hm=api.stepV2(models[vals.indexOf(hi)],z.s,truce);
   ck(Math.abs(lm.next.values[ready]-lo)<=eps&&Math.abs(hm.next.values[ready]-hi)<=eps,"extreme readiness replay");
   const bl=Number(bm.next.encounter===goal),low=Number(lm.next.encounter===goal),high=Number(hm.next.encounter===goal);
   ck(low<=bl&&bl<=high,"monotone immediate goal");
   baseTruce+=bl;minTruce+=low;maxTruce+=high;baseGoal+=Number(alt||bl);maxGoal+=Number(alt||high);
   if(high>bl){newTruce++;witnesses.push({rep:z.rep,records:v,baseline:x,max:hi,weights:ws[vals.indexOf(hi)],baseline_route:bm.next.encounter,max_route:hm.next.encounter});}
  }
  out.push({seed:cohort.seed,roots:rs.length,eligible,zero,saturated,interior,constant,variable,baseTruce,minTruce,maxTruce,newTruce,baseGoal,maxGoal,patterns,witnesses});
 }
 return {scope:"post-development exact immediate-goal upper envelope on sampled reachable roots for continuous weight polytope, not H3 and not a shared feasible coefficient vector",proof:"uncapped weighted sum is linear in weights, extrema on permutations of (.5,1,1.5); cap is monotone. All other eligibility and ranking terms are independent of readiness, and secret priority has positive slope 4. A root's maximum possible immediate truce success is attained by a tested vertex. Rootwise envelope permits different weights for every root.",cohorts:out};
}
export function summarizeDevelopment(d){
 const fail={};for(const c of d.candidates)for(const co of c.cohorts)for(const [k,ok] of Object.entries(co.checks))if(!ok)fail[k]=(fail[k]??0)+1;
 return {grid:d.candidates.length,feasible:d.feasible,any_positive:d.candidates.filter(c=>c.cohorts.some(x=>x.delta.goal4>0)).length,fail_cohort_counts:fail,max_energy:Math.max(...d.candidates.flatMap(c=>c.cohorts.map(x=>x.maxEnergy))),max_concentration:Math.max(...d.candidates.flatMap(c=>c.cohorts.map(x=>x.maxConc))),dev_actions:d.candidates.reduce((s,c)=>s+c.cohorts.reduce((t,x)=>t+x.actions,0),0),dev_forced:d.candidates.reduce((s,c)=>s+c.cohorts.reduce((t,x)=>t+x.forced,0),0),dev_provenance_combinations:d.candidates.reduce((s,c)=>s+c.provenance.combinations,0),dev_provenance_checks:d.candidates.reduce((s,c)=>s+c.provenance.checks,0)};
}
