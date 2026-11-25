// SRG-AC03: restricted legal upstream policy optimization, frozen world.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
const ck=(v,m)=>{if(!v)throw Error("AC03: "+m);};
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),sum=(a,f)=>a.reduce((s,x)=>s+f(x),0);
const S="page_sirens_at_the_rollup_door",G="page_secret_undercover_truce",T="opt_"+S+"_2";
const sites=["page_start","page_pink_ambush_theory","page_cadillac_trunk","page_eddie_and_blonde_story"];
const ledger=["char_pink.Timeline_Record","char_pink.Radio_Record","char_pink.Review_Request"];
const goals=["char_pink.Rat_Suspicion","char_blonde.Sadistic_Escalation","char_white.Crew_Loyalty"];
export const DESIGN={dev:[{seed:0x53522301,n:32},{seed:0x53522302,n:32}],val:[{seed:0x53522311,n:96},{seed:0x53522312,n:96}],budget:24,H:3,lossDivisor:16,sites,ledger};
export const BASE=["r","r","r","r"],ALL=["r",0,2,2];
export function policies(){
 const out=[];
 for(const a of ["r",0,1,2,3])for(const b of ["r",0,1,2])for(const c of ["r",0,1,2,"missing","have"])for(const d of ["r",0,1,2,"one","lt2"])out.push([a,b,c,d]);
 ck(out.length===720,"policy count");return out;
}
function tapes(c){
 let x=c.seed>>>0;ck(x!==0,"zero seed");
 const rand=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};
 return Array.from({length:c.n},()=>Array.from({length:DESIGN.budget},rand));
}
function counts(){return {steps:0,record_checks:0,record_increases:0,tree_nodes:0,branch_nodes:0,leaves:0,invalid_leaves:0,missed_leaves:0};}
function checked(api,w,s,a,c){
 const b=api.stepV2(w,s,a),r=w.pages[s.encounter].options[a].reactions.find(x=>x.id===b.id);
 ck(r,"selected reaction absent");c.steps++;
 for(const k of ledger){
  const old=s.values[k],actual=b.next.values[k],effects=r.effects.filter(e=>e.kind==="number"&&e.key===k);
  ck(typeof old==="number"&&typeof actual==="number"&&old>=0&&old<=.125,"record domain");
  let expected=old;
  for(const e of effects){const f=e.value;
   ck(f.op==="MAX"&&f.args.length===2&&f.args[0].key===k&&f.args[1].op==="literal","record provenance AST");
   const credit=Number(f.args[1].literal);ck(credit>=0&&credit<=.125,"credit cap");expected=Math.max(expected,credit);
  }
  ck(actual===expected&&actual>=old&&actual<=.125,"record provenance replay");c.record_checks++;c.record_increases+=Number(actual>old);
 }
 return b;
}
function obs(api,w,s){return api.observeV2(w,s);}
function randomAction(o,word){ck(o.actions.length>0,"empty legal menu");return o.actions[Math.floor(word*o.actions.length/4294967296)].id;}
function tree(api,w,s,h,c){
 const o=obs(api,w,s),n={o,terminal:o.status==="terminal",reward:Number(o.status==="terminal"&&s.encounter===G),children:{},full:0,s};
 c.tree_nodes++;
 if(n.terminal){n.full=n.reward;return n;}
 if(h===0||o.status!=="decision")return n;
 for(const a of o.actions){const b=checked(api,w,s,a.id,c);n.children[a.id]=tree(api,w,b.next,h-1,c);}
 n.full=Math.max(0,...Object.values(n.children).map(x=>x.full));return n;
}
function suffix(api,w,n,words,j,c){
 let s=n.s,k=n;
 for(;j<words.length;j++){
  const o=k?k.o:obs(api,w,s);if(o.status!=="decision")break;
  const a=randomAction(o,words[j]),next=k?.children[a];
  if(next){k=next;s=k.s;}else{k=null;s=checked(api,w,s,a,c).next;}
 }
 const o=obs(api,w,s);
 return {complete:Number(o.status==="terminal"),success:Number(o.status==="terminal"&&s.encounter===G)};
}
function finish(api,w,s,words,j,mask,history,energies,c){
 c.leaves++;
 if(s.encounter!==S){c.missed_leaves++;return {leaf:true,valid:true,reached:false,mask,history};}
 const n=tree(api,w,s,3,c),q1=Object.fromEntries(Object.entries(n.children).map(([a,x])=>[a,x.terminal?x.reward:0])),q3=Object.fromEntries(Object.entries(n.children).map(([a,x])=>[a,x.full]));
 const values=ledger.map(k=>s.values[k]),wins=Object.keys(q3).filter(k=>q3[k]===1),es=sum(energies,x=>x),max=Math.max(0,...energies);
 const result=suffix(api,w,n,words,j,c);
 return {leaf:true,valid:true,reached:true,mask,history,records:values,active:Number(values.filter(v=>v>0).length>=2),h1:Number(Object.values(q1).includes(1)),h3:n.full,
  info:Number(wins.length>0&&wins.length<Object.keys(q3).length),unique:Number(wins.length===1&&wins[0]===T),q1,q3,n,random:result.success,complete:result.complete,share:es?max/es:0,maxEnergy:max};
}
function buildTape(api,w,words,c){
 let serial=0;const leaves=[];
 function go(s,j,mask,history,es){
  try{
   while(j<words.length&&s.encounter!==S){
    const o=obs(api,w,s);if(o.status!=="decision")break;
    const idx=sites.indexOf(s.encounter),fallback=randomAction(o,words[j]);
    if(idx>=0&&!(mask&(1<<idx))){
     c.branch_nodes++;
     const node={leaf:false,idx,default:fallback,records:ledger.map(k=>{ck(Object.hasOwn(o.values,k),"nonpublic record");return o.values[k];}),children:{}};
     for(const a of o.actions){
      try{const b=checked(api,w,s,a.id,c);node.children[a.id]=go(b.next,j+1,mask|1<<idx,[...history,[a.id,b.id]],[...es,b.squared_step_energy]);}
      catch(e){throw e;}
     }
     return node;
    }
    const b=checked(api,w,s,fallback,c);history=[...history,[fallback,b.id]];es=[...es,b.squared_step_energy];s=b.next;j++;
   }
   const leaf=finish(api,w,s,words,j,mask,history,es,c);leaf.serial=serial++;leaves.push(leaf);return leaf;
  }catch(e){
   c.invalid_leaves++;const leaf={leaf:true,valid:false,reached:false,mask,history,error:String(e).slice(0,250),serial:serial++};leaves.push(leaf);return leaf;
  }
 }
 const root=go(api.initialV2(w),0,0,[],[]);
 return {root,leaves};
}
function desired(idx,rule,records){
 if(rule==="r")return null;
 let k=rule;
 if(idx===2&&rule==="missing")k=records[0]===0?2:1;
 if(idx===2&&rule==="have")k=records[0]>0?2:1;
 if(idx===3&&rule==="one")k=records.filter(v=>v>0).length===1?2:0;
 if(idx===3&&rule==="lt2")k=records.filter(v=>v>0).length<2?2:0;
 ck(Number.isInteger(k),"bad rule");return "opt_"+sites[idx]+"_"+k;
}
function select(root,p){
 let x=root,fallback=0;
 while(!x.leaf){const a=desired(x.idx,p[x.idx],x.records);if(a&&!Object.hasOwn(x.children,a))fallback++;x=x.children[a&&Object.hasOwn(x.children,a)?a:x.default];ck(x,"missing branch");}
 return {x,fallback};
}
function direct(api,w,words,p,c){
 let s=api.initialV2(w),mask=0,history=[],es=[],j=0,fallback=0;
 try{
  for(;j<words.length&&s.encounter!==S;j++){
   const o=obs(api,w,s);if(o.status!=="decision")break;
   let a=randomAction(o,words[j]);const idx=sites.indexOf(s.encounter);
   if(idx>=0&&!(mask&(1<<idx))){
    mask|=1<<idx;const want=desired(idx,p[idx],ledger.map(k=>{ck(Object.hasOwn(o.values,k),"nonpublic record");return o.values[k];}));
    if(want){if(o.actions.some(x=>x.id===want))a=want;else fallback++;}
   }
   const b=checked(api,w,s,a,c);history.push([a,b.id]);es.push(b.squared_step_energy);s=b.next;
  }
  return {x:finish(api,w,s,words,j,mask,history,es,c),fallback};
 }catch(e){c.invalid_leaves++;return {x:{valid:false,reached:false,mask,history,error:String(e).slice(0,250)},fallback};}
}
function project(n,mode){
 const o=n.o,v={};
 for(const k of ledger){ck(Object.hasOwn(o.values,k),"nonpublic projection");v[k]=o.values[k];}
 if(mode==="goal4")for(const k of goals){ck(Object.hasOwn(o.values,k),"nonpublic goal");v[k]=Math.min(15,Math.floor((o.values[k]+1)*8));}
 return JSON.stringify([o.encounter,o.turn,o.status,o.actions,v]);
}
function group(ns,mode){const m=new Map();for(const n of ns){const key=project(n,mode),a=m.get(key)??[];a.push(n);m.set(key,a);}return m;}
function oracle(ns,mode,fit=false,H=3){
 const policy=fit?new Map():null;let cells=0,informative=0,rootCells=0,rootInfo=0;
 function solve(xs,d,hist){
  if(xs.every(n=>n.terminal))return sum(xs,n=>n.reward);
  if(d===0||xs.every(n=>n.o.status==="dead_end"))return 0;
  const ids=Object.keys(xs[0].children);ck(ids.length&&xs.every(n=>eq(Object.keys(n.children),ids)),"inconsistent menu");
  const values=ids.map(a=>{let v=0;for(const [o,g] of group(xs.map(n=>n.children[a]),mode))v+=solve(g,d-1,fit?[...hist,a,o]:null);return v;});
  const hi=Math.max(...values),inf=hi>Math.min(...values);cells++;informative+=Number(inf);
  if(d===H){rootCells++;rootInfo+=Number(inf);}
  if(fit){const key=JSON.stringify([d,hist]);ck(!policy.has(key),"policy key collision");policy.set(key,ids[values.indexOf(hi)]);}
  return hi;
 }
 let value=0;for(const [o,g] of group(ns,mode))value+=solve(g,H,fit?[o]:null);
 const full=sum(ns,x=>x.full);ck(value<=full,"belief ceiling");
 return {value,full,gap:full-value,cells,informative,rootCells,rootInfo,...(fit?{policy}:{})};
}
function deploy(ns,primary,fallback=null,mode="goal4"){
 let successes=0,decisions=0,hits=0,ledgerHits=0,firstHits=0,stopped=0,rootHits=0;
 for(const start of ns){
  let n=start,h1=[project(n,mode)],h2=[project(n,"ledger")];
  for(let d=3;d>0&&!n.terminal;d--){
   const ids=Object.keys(n.children);if(!ids.length){stopped++;break;}
   let a=primary.get(JSON.stringify([d,h1]));
   if(a&&ids.includes(a)){hits++;rootHits+=Number(d===3);}else{
    a=fallback?.get(JSON.stringify([d,h2]));if(a&&ids.includes(a))ledgerHits++;else{a=ids[0];firstHits++;}
   }
   decisions++;n=n.children[a];h1.push(a,project(n,mode));h2.push(a,project(n,"ledger"));
  }
  successes+=n.terminal?n.reward:0;
 }
 return {roots:ns.length,successes,decisions,hits,ledgerHits,firstHits,stopped,rootHits};
}
function profile(xs,base=null,beliefCache=null){
 const leaves=xs.map(r=>r.x),ok=leaves.filter(x=>x.valid&&x.reached),ns=ok.map(x=>x.n);
 const memoKey=beliefCache?leaves.map(x=>x.serial).join(","):null;
 let b=beliefCache?.get(memoKey);
 if(!b){b={goal4:oracle(ns,"goal4"),ledger:oracle(ns,"ledger")};if(beliefCache)beliefCache.set(memoKey,b);}
 ck(b.ledger.value<=b.goal4.value&&b.goal4.value<=sum(ok,x=>x.h3),"nested ceilings");
 const o={roots:xs.length,reached:ok.length,invalid:leaves.filter(x=>!x.valid).length,fallback:sum(xs,x=>x.fallback),
 h1:sum(ok,x=>x.h1),h3:sum(ok,x=>x.h3),info:sum(ok,x=>x.info),unique:sum(ok,x=>x.unique),active:sum(ok,x=>x.active),
 random:sum(ok,x=>x.random),complete:sum(ok,x=>x.complete),visits:sites.map((_,i)=>sum(ok,x=>Number(!!(x.mask&(1<<i))))),
 energy:{mean_share:ok.length?sum(ok,x=>x.share)/ok.length:0,max_share:Math.max(0,...ok.map(x=>x.share)),max_step:Math.max(0,...ok.map(x=>x.maxEnergy))},...b};
 if(base){
  const old=base.leaves,newH=leaves.map(x=>x.reached&&x.valid?x.h3:0);
  o.gains=sum(newH,(v)=>0);o.losses=0;for(let i=0;i<newH.length;i++){const v=old[i].reached&&old[i].valid?old[i].h3:0;o.gains+=Number(newH[i]>v);o.losses+=Number(newH[i]<v);}
  const p=base.metrics;o.delta={goal4:o.goal4.value-p.goal4.value,ledger:o.ledger.value-p.ledger.value,info:o.info-p.info,active:o.active-p.active,h3:o.h3-p.h3,random:o.random-p.random};
  ck(o.h3-p.h3===o.gains-o.losses,"paired effect identity");
  o.checks={coverage:o.reached===o.roots&&o.invalid===0&&o.complete===o.roots,fallback:o.fallback===0,goal4:o.delta.goal4>=0,ledger:o.delta.ledger>=0,info:o.delta.info>=0,active:o.delta.active>=0,loss:o.losses<=Math.floor(o.roots/DESIGN.lossDivisor)};
  o.pass=Object.values(o.checks).every(Boolean);o.strict=o.pass&&o.losses===0;
 }
 return o;
}
function compact(x){return {valid:x.valid,reached:x.reached,history:x.history,mask:x.mask,...(x.reached&&x.valid?{records:x.records,h1:x.h1,h3:x.h3,q1:x.q1,q3:x.q3,info:x.info,unique:x.unique,active:x.active,random:x.random,complete:x.complete,share:x.share,maxEnergy:x.maxEnergy}:{error:x.error??null})};}
export function developmentCohort(source,c,api=runtime){
 const w=api.compileV2(source),ts=tapes(c),ct=counts(),forest=ts.map(t=>buildTape(api,w,t,ct));
 const baseline=forest.map(x=>select(x.root,BASE)),cache=new Map(),bp=profile(baseline,null,cache),bs={leaves:baseline.map(x=>x.x),metrics:bp};
 ck(bp.reached===c.n&&bp.invalid===0&&bp.complete===c.n,"baseline coverage");
 const results=policies().map(p=>({p,...profile(forest.map(x=>select(x.root,p)),bs,cache)}));
 const envelope={h3:sum(forest,f=>Number(f.leaves.some(x=>x.valid&&x.reached&&x.h3))),active:sum(forest,f=>Number(f.leaves.some(x=>x.valid&&x.reached&&x.active))),
 joint:sum(forest,f=>Number(f.leaves.some(x=>x.valid&&x.reached&&x.active&&x.h3))),all_reached:forest.filter(f=>f.leaves.every(x=>x.valid&&x.reached)).length};
 const dc=counts();for(let i=0;i<ts.length;i++){
  const replay=direct(api,w,ts[i],BASE,dc);ck(eq(compact(replay.x),compact(baseline[i].x))&&replay.fallback===baseline[i].fallback,"cached/direct baseline drift");
 }
 return {cohort:c,counts:ct,baseline:bp,unique_leaf_vectors:cache.size,envelope,baseline_direct_checks:ts.length,direct_counts:dc,results};
}
export function choose(dev){
 ck(dev.length===2&&dev.every(d=>d.results.length===720),"development shape");
 const candidates=dev[0].results.map((a,i)=>{const b=dev[1].results[i];ck(eq(a.p,b.p),"policy alignment");return {p:a.p,cohorts:[a,b],pass:a.pass&&b.pass,strict:a.strict&&b.strict};});
 const base=candidates.find(x=>eq(x.p,BASE));ck(base.pass,"baseline feasibility");
 const rank=x=>[Math.min(...x.cohorts.map(y=>y.delta.goal4)),sum(x.cohorts,y=>y.delta.goal4),Math.min(...x.cohorts.map(y=>y.delta.ledger)),sum(x.cohorts,y=>y.delta.info),sum(x.cohorts,y=>y.active),-x.p.filter(v=>v!=="r").length];
 const better=(a,b)=>{const x=rank(a),y=rank(b);for(let i=0;i<x.length;i++)if(x[i]!==y[i])return x[i]>y[i];return false;};
 let best=base;for(const x of candidates)if(x.pass&&better(x,best))best=x;
 const improved=best.cohorts.every(x=>x.delta.goal4>0),strict=candidates.filter(x=>x.strict),feasible=candidates.filter(x=>x.pass);
 let strictBest=base;for(const x of strict)if(better(x,strictBest))strictBest=x;
 return {policies:candidates.length,feasible:feasible.length,strict:strict.length,positive_both:feasible.filter(x=>x.cohorts.every(y=>y.delta.goal4>0)).length,strict_positive_both:strict.filter(x=>x.cohorts.every(y=>y.delta.goal4>0)).length,best,strictBest,improved,frozen:improved?best.p:BASE,all:candidates.find(x=>eq(x.p,ALL)),baseline:base};
}
export function validate(source,dev,selection,api=runtime){
 const w=api.compileV2(source),ps=[["baseline",BASE],["frozen",selection.frozen],["all",ALL]],ct=counts(),fits={};
 for(const [name,p] of ps){
  const ds=DESIGN.dev.flatMap(c=>tapes(c).map(t=>direct(api,w,t,p,ct))),ns=ds.filter(x=>x.x.valid&&x.x.reached).map(x=>x.x.n);
  ck(ns.length===sum(DESIGN.dev,c=>c.n),"training coverage");
  const a=oracle(ns,"goal4",true),b=oracle(ns,"ledger",true);
  const ra=deploy(ns,a.policy,null,"goal4"),rb=deploy(ns,b.policy,null,"ledger");
  ck(ra.successes===a.value&&ra.firstHits===0&&rb.successes===b.value&&rb.firstHits===0,"fitted policy self replay");
  fits[name]={a,b,train:profile(ds),trainGoal4:ra,trainLedger:rb};
 }
 // Refit direct replay must reproduce all registered development numerators.
 for(const [name,p] of ps){
  const want=sum(dev,d=>d.results.find(x=>eq(x.p,p)).h3);ck(fits[name].train.h3===want,"development direct policy mismatch");
 }
 const cohorts=[];
 for(const c of DESIGN.val){
  const ts=tapes(c),all=Object.fromEntries(ps.map(([name,p])=>[name,ts.map(t=>direct(api,w,t,p,ct))]));
  const bp=profile(all.baseline),bs={metrics:bp,leaves:all.baseline.map(x=>x.x)},metrics={};
  for(const [name,p] of ps){
   const xs=all[name],ns=xs.filter(x=>x.x.valid&&x.x.reached).map(x=>x.x.n),m=profile(xs,bs);
   const fit=oracle(ns,"goal4",true),replay=deploy(ns,fit.policy);
   ck(replay.successes===m.goal4.value&&replay.firstHits===0,"validation oracle replay");
   const transfer=deploy(ns,fits[name].a.policy,fits[name].b.policy);
   ck(transfer.successes<=m.goal4.value,"transfer beats empirical ceiling");
   metrics[name]={p,...m,oracle_replay:replay,transfer,rows:xs.map(x=>({...compact(x.x),fallback:x.fallback}))};
  }
  cohorts.push({cohort:c,metrics,pass:metrics.frozen.pass&&metrics.frozen.delta.goal4>0});
 }
 const train=Object.fromEntries(Object.entries(fits).map(([k,v])=>[k,{metrics:v.train,goal4_cells:v.a.policy.size,ledger_cells:v.b.policy.size,replay:v.trainGoal4,ledger_replay:v.trainLedger}]));
 return {frozen:selection.frozen,pass:selection.improved&&cohorts.every(c=>c.pass),train,cohorts,counts:ct};
}
