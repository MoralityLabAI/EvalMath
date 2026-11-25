// SRG-AC05: bounded contextual effects, legal-history reversal witnesses.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
import {evaluate} from '../srg04/swmd-runtime.mjs';
const ck=(v,m)=>{if(!v)throw Error("AC05: "+m);},eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),sum=(a,f)=>a.reduce((s,x)=>s+f(x),0);
const S="page_sirens_at_the_rollup_door",G="page_secret_undercover_truce",T="opt_"+S+"_2",L="char_white.Crew_Loyalty",O="char_orange.Diamond_Leverage";
const sites=["page_start","page_pink_ambush_theory","page_cadillac_trunk","page_eddie_and_blonde_story"],ledger=["char_pink.Timeline_Record","char_pink.Radio_Record","char_pink.Review_Request"];
const goals=["char_pink.Rat_Suspicion","char_blonde.Sadistic_Escalation",L],modes=["menu","weak","ledger","goal4","public"],upstream={baseline:["r","r","r","r"],all:["r",0,2,2],frozen:[0,0,1,2]};
const eps=1e-10;
export const DESIGN={dev:[{seed:0x53522501,n:48},{seed:0x53522502,n:48}],val:[{seed:0x53522511,n:96},{seed:0x53522512,n:96}],budget:24,H:3,adjust:.12,ratio:1.35,share:.025,lossDivisor:24,upstream,modes};
export const BASE={action:null,feature:null,c:0};
export function grid(){const out=[BASE];for(const action of [1,2])for(const feature of goals.slice(0,2))for(const c of [-.12,-.08,-.04,.04,.08,.12])out.push({action,feature,c});return out;}
export function patch(src,g){
 ck(grid().some(x=>eq(x,g)),"unknown candidate");if(!g.c)return src;
 const target="ORX opt_"+S+"_"+g.action+"/",lines=src.split("\n");let n=0;
 const out=lines.map(l=>{
  if(!l.startsWith(target))return l;
  const old=l.match(/SET char_white\.Crew_Loyalty = CLAMP\(NUDGE\(P\(char_white\.Crew_Loyalty\),ADD\(C\((-?0\.11)\),MUL\(P\(char_orange\.Diamond_Leverage\),C\(0\.08\)\)\)\)\)/);
  ck(old&&l.split(old[0]).length===2,"stale loyalty expression");n++;
  const neu="SET "+L+" = CLAMP(NUDGE(P("+L+"),ADD(C("+old[1]+"),MUL(P("+O+"),C(0.08)),MUL(C("+g.c+"),P("+g.feature+"),MIN(C(1),MUL(C(8),P("+ledger[0]+")))))))";
  return l.replace(old[0],neu);
 });
 ck(n===3,"expected three edits");return out.join("\n");
}
function tapes(c){
 let x=c.seed>>>0;const r=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};
 return Array.from({length:c.n},()=>Array.from({length:DESIGN.budget},r));
}
function counts(){return {prefix_steps:0,suffix_steps:0,nodes:0,scope_actions:0,ordered_writes:0,invalid:0};}
function roots(api,w,co,p,ct){
 const out=[];
 for(const [rep,words] of tapes(co).entries()){
  let s=api.initialV2(w),seen=0,history=[],energy=[];
  for(let i=0;i<words.length&&s.encounter!==S;i++){
   const o=api.observeV2(w,s);if(o.status!=="decision")break;
   let a=o.actions[Math.floor(words[i]*o.actions.length/4294967296)].id,idx=sites.indexOf(s.encounter);
   if(idx>=0&&!(seen&(1<<idx))){seen|=1<<idx;if(p[idx]!=="r"){a="opt_"+sites[idx]+"_"+p[idx];ck(o.actions.some(x=>x.id===a),"unavailable override");}}
   const b=api.stepV2(w,s,a);ct.prefix_steps++;history.push({action:a,reaction:b.id});energy.push(b.squared_step_energy);s=b.next;
  }
  ck(s.encounter===S,"missed sirens");out.push({rep,s,history,energy,upstream:p});
 }
 return out;
}
function tree(api,w,s,h,ct,branches=null){
 const o=api.observeV2(w,s),n={o,terminal:o.status==="terminal",reward:Number(o.status==="terminal"&&s.encounter===G),children:{},full:0};
 ct.nodes++;
 if(n.terminal){n.full=n.reward;return n;}
 if(!h||o.status!=="decision")return n;
 for(const a of o.actions){const b=api.stepV2(w,s,a.id);ct.suffix_steps++;if(branches)branches[a.id]=b;n.children[a.id]=tree(api,w,b.next,h-1,ct);}
 n.full=Math.max(0,...Object.values(n.children).map(x=>x.full));return n;
}
function project(n,mode){
 const o=n.o,v={};
 if(mode==="weak"){ck(Object.hasOwn(o.values,ledger[2]),"hidden review");v[ledger[2]]=Number(o.values[ledger[2]]>0);}
 else if(mode!=="menu")for(const k of ledger){ck(Object.hasOwn(o.values,k),"hidden ledger");v[k]=o.values[k];}
 if(mode==="goal4")for(const k of goals){ck(Object.hasOwn(o.values,k),"hidden goal");v[k]=Math.min(15,Math.floor((o.values[k]+1)*8));}
 if(mode==="public")for(const k of Object.keys(o.values).sort())v[k]=o.values[k];
 return JSON.stringify([o.encounter,o.turn,o.status,o.actions,v]);
}
function group(ns,mode){const m=new Map();for(const n of ns){const k=project(n,mode),a=m.get(k)??[];a.push(n);m.set(k,a);}return m;}
function fit(ns,mode){
 const policy=new Map();let cells=0,info=0;
 function solve(xs,h,hist){
  if(xs.every(n=>n.terminal))return sum(xs,n=>n.reward);
  if(!h||xs.every(n=>n.o.status==="dead_end"))return 0;
  const as=Object.keys(xs[0].children);ck(as.length&&xs.every(n=>eq(Object.keys(n.children),as)),"menu mismatch");
  const v=as.map(a=>sum([...group(xs.map(n=>n.children[a]),mode).entries()],([o,g])=>solve(g,h-1,[...hist,a,o])));
  const hi=Math.max(...v);info+=Number(hi>Math.min(...v));cells++;
  const k=JSON.stringify([h,hist]);ck(!policy.has(k),"history key");policy.set(k,as[v.indexOf(hi)]);return hi;
 }
 const value=sum([...group(ns,mode).entries()],([o,g])=>solve(g,3,[o])),full=sum(ns,n=>n.full);
 ck(value<=full,"oracle bound");return {policy,value,full,cells,informative_cells:info,gap:full-value};
}
function deploy(ns,fit,mode,menu=null){
 let successes=0,hits=0,menuHits=0,firstHits=0,steps=0;
 for(const root of ns){
  let n=root,hist=[project(n,mode)],m=[project(n,"menu")];
  for(let h=3;h>0&&!n.terminal;h--){
   const as=Object.keys(n.children);if(!as.length)break;
   let a=fit.get(JSON.stringify([h,hist]));
   if(a&&as.includes(a))hits++;else{a=menu?.get(JSON.stringify([h,m]));if(a&&as.includes(a))menuHits++;else{a=as[0];firstHits++;}}
   n=n.children[a];steps++;hist.push(a,project(n,mode));m.push(a,project(n,"menu"));
  }
  successes+=n.terminal?n.reward:0;
 }
 return {successes,hits,menuHits,firstHits,steps};
}
function q(n){return Object.fromEntries(Object.entries(n.children).map(([a,x])=>[a,x.full]));}
function strict(n){const wins=Object.keys(q(n)).filter(a=>n.children[a].full);return wins.length===1?wins[0]:null;}
function informative(n){const vs=Object.values(q(n));return vs.length>1&&Math.max(...vs)>Math.min(...vs);}
function script(ns){
 let best=-1,rule=null;
 for(let i=0;i<64;i++){
  const p=[i>>4&3,i>>2&3,i&3];let value=0;
  for(const root of ns){let n=root;for(let h=3;h>0&&!n.terminal;h--){const as=Object.keys(n.children);if(!as.length)break;n=n.children[as[p[3-h]]??as[0]];}value+=n.terminal?n.reward:0;}
  if(value>best){best=value;rule=p;}
 }
 return {value:best,rule};
}
function reverseWitnesses(rows,mode){
 const groups=new Map();
 for(const x of rows){const a=strict(x.n);if(!a)continue;const k=project(x.n,mode),g=groups.get(k)??[];g.push({...x,a});groups.set(k,g);}
 let pairs=0,cells=0;const examples=[];
 for(const [k,g] of groups){
  let p=0;for(let i=0;i<g.length;i++)for(let j=0;j<i;j++)if(g[i].a!==g[j].a){
   p++;
   if(examples.length<6){
    const describe=x=>({rep:x.rep,upstream:x.upstream,history:x.history,q:q(x.n),unique:x.a,public_context:Object.fromEntries([...ledger,...goals].map(k=>[k,x.n.o.values[k]]))});
    examples.push({projection:JSON.parse(k),left:describe(g[j]),right:describe(g[i])});
   }
  }pairs+=p;cells+=Number(p>0);
 }
 return {pairs,cells,examples};
}
function share(es,e){const t=sum(es,x=>x)+e;return t?Math.max(e,...es)/t:0;}
function replayWrites(w,s,r,b,oldR,g,evalExpr){
 // Evaluate the original ordered effects on the actual edited intermediate
 // state. Independently implement the one changed NUDGE.
 const v={...s.values};for(const id of w.events)v["__srg.SEEN_"+id]=Number(s.seen.includes(id));
 for(const [k,x] of Object.entries(s.spools))v["__srg.ACTIVE_"+k]=Number(x);
 ck(r.effects.length===oldR.effects.length&&b.writes.length===r.effects.length,"write count");
 let edits=0;
 for(const [i,e] of r.effects.entries()){
  const old=oldR.effects[i];ck(e.kind==="number"&&old.kind===e.kind&&old.key===e.key,"write target");
  let expected;
  if(e.key===L){
   const ast=old.value.args[0],amount=evalExpr(ast.args[1],v),extra=g.c*v[g.feature]*Math.min(1,8*v[ledger[0]]),z=amount+extra;
   ck(Math.abs(z)<=1,"nudge domain");expected=Math.max(-1,Math.min(1,v[L]*(1-Math.abs(z))+z));edits++;
  }else{ck(eq(old.value,e.value),"other AST changed");expected=evalExpr(old.value,v);}
  ck(Math.abs(expected-b.writes[i].after)<=eps&&Math.abs(v[e.key]-b.writes[i].before)<=eps,"ordered write mismatch");
  v[e.key]=expected;
 }
 ck(edits===1,"one loyalty write");
 for(const k of Object.keys(s.values))ck(Math.abs(v[k]-b.next.values[k])<=eps,"successor replay");
 return r.effects.length;
}
function measure(api,world,baseline,rs,g,ct,base=null,evalExpr=evaluate){
 const rows=[],scope={actions:0,ordered_writes:0,invalid:0,unchanged:0,warrant_zero:0,max_adjust:0,max_ratio:1,max_share_increase:0},errors=[];
 for(const r of rs){
  try{
   const branches={},n=tree(api,world,r.s,3,ct,branches);
   if(base){
    const old=base.rows.find(x=>x.rep===r.rep);ck(old&&eq(Object.keys(branches),Object.keys(old.branches)),"root menu");
    for(const [a,b] of Object.entries(branches)){
     const z=old.branches[a];scope.actions++;ct.scope_actions++;
     if(!g.c||a!=="opt_"+S+"_"+g.action){ck(eq(z,b),"untouched action drift");scope.unchanged++;continue;}
     ck(z.id===b.id&&z.next.turn===b.next.turn&&eq(z.next.spools,b.next.spools),"selected reaction/spools drift");
     const rr=world.pages[S].options[a].reactions.find(x=>x.id===b.id),oo=baseline.pages[S].options[a].reactions.find(x=>x.id===b.id);
     const check=replayWrites(world,r.s,rr,b,oo,g,evalExpr);scope.ordered_writes+=check;ct.ordered_writes+=check;
     if(r.s.values[ledger[0]]===0){ck(eq(z,b),"zero-warrant drift");scope.warrant_zero++;}
     const adj=Math.max(...Object.keys(r.s.values).map(k=>Math.abs(z.next.values[k]-b.next.values[k]))),ratio=z.squared_step_energy?b.squared_step_energy/z.squared_step_energy:b.squared_step_energy?Infinity:1;
     scope.max_adjust=Math.max(scope.max_adjust,adj);scope.max_ratio=Math.max(scope.max_ratio,ratio);scope.max_share_increase=Math.max(scope.max_share_increase,share(r.energy,b.squared_step_energy)-share(r.energy,z.squared_step_energy));
    }
   }
   rows.push({...r,n,branches});
  }catch(e){scope.invalid++;ct.invalid++;errors.push({rep:r.rep,error:String(e).slice(0,300)});}
 }
 const ns=rows.map(r=>r.n),full=sum(ns,n=>n.full),info=sum(ns,n=>Number(informative(n))),oracles={},fits={};let prev=-1;
 for(const mode of modes){const f=fit(ns,mode),d=deploy(ns,f.policy,mode);ck(d.successes===f.value&&d.firstHits===0,"oracle replay");ck(f.value>=prev,"nested ceiling");prev=f.value;fits[mode]=f;const {policy,...rest}=f;oracles[mode]=rest;}
 const result={roots:rs.length,valid:rows.length,full,info,oracles,gap:oracles.goal4.value-oracles.weak.value,strict:reverseWitnesses(rows,"weak"),script:script(ns),scope,errors,rows,fits};
 if(base){
  const lookup=new Map(rows.map(x=>[x.rep,x.n.full])),lost=sum(base.rows,x=>Number(x.n.full>(lookup.get(x.rep)??0))),gain=sum(rows,x=>Number(x.n.full>base.rows.find(y=>y.rep===x.rep).n.full));
  const lim=Math.floor(rs.length/DESIGN.lossDivisor);
  result.lost=lost;result.gain=gain;
  ck(full-base.full===gain-lost,"paired gains identity");
  result.checks={valid:scope.invalid===0&&rows.length===rs.length,scope:scope.invalid===0,adjust:scope.max_adjust<=DESIGN.adjust+eps,energy:scope.max_ratio<=DESIGN.ratio+eps,concentration:scope.max_share_increase<=DESIGN.share+eps,full:full>=base.full-lim,paired_loss:lost<=lim,goal4:oracles.goal4.value>=Math.ceil(.95*full),info:info>=base.info};
  result.pass=Object.values(result.checks).every(Boolean);
  result.hardens=result.gap>=Math.max(2,Math.ceil(.05*full))&&result.strict.pairs>0;
 }
 return result;
}
function brief(x){const {rows,fits,...v}=x;return v;}
export function developmentCohort(src,co,api=runtime,evalExpr=evaluate){
 const w=api.compileV2(src),ct=counts(),rs=roots(api,w,co,upstream.frozen,ct),baseline=measure(api,w,w,rs,BASE,ct);
 ck(baseline.valid===co.n,"baseline coverage");
 const candidates=[];
 for(const g of grid()){
  const model=api.compileV2(patch(src,g));
  candidates.push({g,...brief(measure(api,model,w,rs,g,ct,baseline,evalExpr))});
 }
 const mixed=Object.entries(upstream).flatMap(([k,p])=>roots(api,w,co,p,ct)),m=measure(api,w,w,mixed,BASE,ct);
 return {cohort:co,counts:ct,baseline:brief(baseline),mixed:brief(m),candidates};
}
export function select(ds){
 const rows=ds[0].candidates.map((x,i)=>{const y=ds[1].candidates[i];ck(eq(x.g,y.g),"candidate order");return {g:x.g,cohorts:[x,y],pass:x.pass&&y.pass,hardens:x.hardens&&y.hardens};});
 const rank=x=>[Math.min(...x.cohorts.map(y=>y.gap)),sum(x.cohorts,y=>y.gap),Math.min(...x.cohorts.map(y=>y.strict.pairs)),sum(x.cohorts,(y)=>y.info),-Math.abs(x.g.c)];
 const better=(a,b)=>{const x=rank(a),y=rank(b);for(let i=0;i<x.length;i++)if(x[i]!==y[i])return x[i]>y[i];return false;};
 let best=rows[0];for(const x of rows)if(x.pass&&better(x,best))best=x;
 return {total:rows.length,feasible:rows.filter(x=>x.pass).length,hardening_feasible:rows.filter(x=>x.pass&&x.hardens).length,best,frozen:best.pass&&best.hardens?best.g:BASE,improved:best.pass&&best.hardens&&!eq(best.g,BASE)};
}
export function validation(src,selection,api=runtime,evalExpr=evaluate){
 const w=api.compileV2(src),g=selection.frozen,model=api.compileV2(patch(src,g)),ct=counts();
 const train=DESIGN.dev.flatMap(c=>roots(api,w,c,upstream.frozen,ct)),ns=train.map(r=>tree(api,model,r.s,3,ct));
 const fits=Object.fromEntries(modes.map(m=>[m,fit(ns,m)]));
 for(const m of modes)ck(deploy(ns,fits[m].policy,m).successes===fits[m].value,"training fit replay");
 const out=[];
 for(const co of DESIGN.val){
  const rs=roots(api,w,co,upstream.frozen,ct),replayed=roots(api,model,co,upstream.frozen,ct);ck(eq(rs,replayed),"prefix drift");
  const base=measure(api,w,w,rs,BASE,ct),candidate=measure(api,model,w,rs,g,ct,base,evalExpr);
  const transfer=Object.fromEntries(modes.map(m=>[m,deploy(candidate.rows.map(x=>x.n),fits[m].policy,m,fits.menu.policy)]));
  for(const m of modes)ck(transfer[m].successes<=candidate.oracles[m].value,"transfer above ceiling");
  const mixed=measure(api,w,w,Object.values(upstream).flatMap(p=>roots(api,w,co,p,ct)),BASE,ct);
  out.push({cohort:co,baseline:brief(base),candidate:brief(candidate),mixed:brief(mixed),transfer,pass:candidate.pass&&candidate.hardens});
 }
 return {frozen:g,counts:ct,training:Object.fromEntries(modes.map(m=>[m,fits[m].value])),cohorts:out,pass:selection.improved&&out.every(x=>x.pass)};
}

// Post-hoc diagnostic: deduplicate actual legal histories before pairing.
// Pair within each weak cell by two largest remaining unique-optimum labels.
// No model-facing corpus or privately held-out selection is implied.
export function pairAudit(src,api=runtime){
 const w=api.compileV2(src),ct=counts(),cohorts=[];
 for(const co of [...DESIGN.dev,...DESIGN.val]){
  const rs=Object.values(upstream).flatMap(p=>roots(api,w,co,p,ct)),raw=rs.map(r=>({...r,n:tree(api,w,r.s,3,ct)}));
  const histories=new Map();
  for(const x of raw){
   const k=JSON.stringify(x.history),old=histories.get(k);
   if(old){ck(eq(x.s,old.s)&&eq(q(x.n),q(old.n)),"duplicate history mismatch");continue;}
   histories.set(k,x);
  }
  const unique=[...histories.values()],groups=new Map();
  for(const x of unique){
   const a=strict(x.n);if(!a)continue;
   const k=project(x.n,"weak"),g=groups.get(k)??new Map(),b=g.get(a)??[];b.push(x);g.set(a,b);groups.set(k,g);
  }
  const pairs=[],used=new Set();let capacity=0;
  for(const [k,g] of groups){
   const sizes=[...g.values()].map(x=>x.length),total=sum(sizes,x=>x),cap=Math.min(Math.floor(total/2),total-Math.max(...sizes));capacity+=cap;
   const before=pairs.length;
   for(;;){
    const buckets=[...g.entries()].filter(([,xs])=>xs.length).sort((a,b)=>b[1].length-a[1].length||(a[0]<b[0]?-1:1));
    if(buckets.length<2)break;
    const a=buckets[0][1].shift(),b=buckets[1][1].shift(),keyA=JSON.stringify(a.history),keyB=JSON.stringify(b.history);
    ck(!used.has(keyA)&&!used.has(keyB)&&strict(a.n)!==strict(b.n)&&project(a.n,"weak")===project(b.n,"weak"),"pair invariant");
    used.add(keyA);used.add(keyB);pairs.push({a,b});
   }
   ck(pairs.length-before===cap,"max disjoint pair count");
  }
  const ns=pairs.flatMap(p=>[p.a.n,p.b.n]);
  const weak=fit(ns,"weak"),led=fit(ns,"ledger"),goal4=fit(ns,"goal4"),pub=fit(ns,"public");
  ck(weak.value===pairs.length&&weak.full===2*pairs.length,"balanced pair ceiling");
  for(const [mode,f] of [["weak",weak],["ledger",led],["goal4",goal4],["public",pub]])ck(deploy(ns,f.policy,mode).successes===f.value,"pair replay");
  const describe=x=>({rep:x.rep,upstream:x.upstream,history:x.history,action:strict(x.n),q:q(x.n),context:Object.fromEntries([...ledger,...goals].map(k=>[k,x.n.o.values[k]]))});
  const examples=pairs.slice(0,6).map(({a,b})=>({projection:JSON.parse(project(a.n,"weak")),a:describe(a),b:describe(b),ledger_equal:project(a.n,"ledger")===project(b.n,"ledger")}));
  const ledgerSeparates=sum(pairs,p=>Number(project(p.a.n,"ledger")!==project(p.b.n,"ledger")));
  const goal4Separates=sum(pairs,p=>Number(project(p.a.n,"goal4")!==project(p.b.n,"goal4")));
  cohorts.push({cohort:co,raw_roots:raw.length,distinct_histories:unique.length,strict_histories:sum(unique,x=>Number(!!strict(x.n))),capacity,pairs:pairs.length,roots:ns.length,ledgerSeparates,goal4Separates,ceiling:{weak:weak.value,ledger:led.value,goal4:goal4.value,public:pub.value,full:weak.full},examples});
 }
 return {scope:"post-hoc balanced witness extraction on registered mixed-policy tapes, deduplicated within cohort; conditional diagnostic only",counts:ct,cohorts};
}
