// SRG-AC04: fixed-script and information/lookahead resistance audit.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
const ck=(v,m)=>{if(!v)throw Error("AC04: "+m);};
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),sum=(a,f)=>a.reduce((s,x)=>s+f(x),0);
const S="page_sirens_at_the_rollup_door",G="page_secret_undercover_truce",T="opt_"+S+"_2";
const sites=["page_start","page_pink_ambush_theory","page_cadillac_trunk","page_eddie_and_blonde_story"];
const ledger=["char_pink.Timeline_Record","char_pink.Radio_Record","char_pink.Review_Request"];
const goals=["char_pink.Rat_Suspicion","char_blonde.Sadistic_Escalation","char_white.Crew_Loyalty"];
export const DESIGN={cal:{seed:0x53522401,n:96},val:[{seed:0x53522411,n:128},{seed:0x53522412,n:128}],budget:24,H:3,cap:262144,modes:["menu","ledger","goal1","goal2","goal4","goal8","public"],depths:[1,2,3],upstream:{baseline:["r","r","r","r"],all:["r",0,2,2],frozen:[0,0,1,2]}};
function tapes(c){
 let x=c.seed>>>0;const rand=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};
 return Array.from({length:c.n},()=>Array.from({length:DESIGN.budget},rand));
}
function observe(api,w,s){return api.observeV2(w,s);}
function random(o,v){return o.actions[Math.floor(v*o.actions.length/4294967296)].id;}
function step(api,w,s,a,c){c.transitions++;return api.stepV2(w,s,a);}
function tree(api,w,s,h,c){
 const o=observe(api,w,s),n={o,terminal:o.status==="terminal",reward:Number(o.status==="terminal"&&s.encounter===G),children:{},full:0};
 c.nodes++;
 if(n.terminal){n.full=n.reward;return n;}
 if(!h||o.status!=="decision")return n;
 for(const a of o.actions)n.children[a.id]=tree(api,w,step(api,w,s,a.id,c).next,h-1,c);
 n.full=Math.max(0,...Object.values(n.children).map(x=>x.full));return n;
}
function roots(api,w,c,p,ct){
 const out=[],bad=[];
 for(const [i,words] of tapes(c).entries()){
  try{
   let s=api.initialV2(w),mask=0,history=[];
   for(let j=0;j<words.length&&s.encounter!==S;j++){
    const o=observe(api,w,s);if(o.status!=="decision")break;
    let a=random(o,words[j]),idx=sites.indexOf(s.encounter);
    if(idx>=0&&!(mask&(1<<idx))){
     mask|=1<<idx;
     if(p[idx]!=="r"){const want="opt_"+sites[idx]+"_"+p[idx];ck(o.actions.some(a=>a.id===want),"unavailable fixed action");a=want;}
    }
    const b=step(api,w,s,a,ct);history.push([a,b.id]);s=b.next;
   }
   ck(s.encounter===S,"missed first sirens");out.push({rep:i,history,n:tree(api,w,s,3,ct)});
  }catch(e){bad.push({rep:i,error:String(e).slice(0,250)});}
 }
 ck(out.length===c.n,"root coverage "+JSON.stringify(bad.slice(0,3)));return out;
}
function projection(n,mode){
 const o=n.o,v={};
 if(mode.startsWith("sub")||mode.startsWith("pres")){const present=mode.startsWith("pres"),mask=Number(mode.slice(present?4:3));ck(Number.isInteger(mask)&&mask>=0&&mask<8,"mask");for(const [i,k] of ledger.entries())if(mask&(1<<i)){ck(Object.hasOwn(o.values,k),"nonpublic ledger");v[k]=present?Number(o.values[k]>0):o.values[k];}}
 else if(mode!=="menu")for(const k of ledger){ck(Object.hasOwn(o.values,k),"nonpublic ledger");v[k]=o.values[k];}
 if(mode.startsWith("goal")){
  const b=Number(mode.slice(4)),m=2**b;
  for(const k of goals){ck(Object.hasOwn(o.values,k),"nonpublic goal");v[k]=Math.min(m-1,Math.floor((o.values[k]+1)*m/2));}
 }
 if(mode==="public")for(const k of Object.keys(o.values).sort())v[k]=o.values[k];
 return JSON.stringify([o.encounter,o.turn,o.status,o.actions,v]);
}
function group(ns,mode){
 const m=new Map();for(const n of ns){const k=projection(n,mode),a=m.get(k)??[];a.push(n);m.set(k,a);}return m;
}
function ids(xs){const a=Object.keys(xs[0].children);ck(xs.every(n=>eq(Object.keys(n.children),a)),"inconsistent menu");return a;}
function key(h,hist){return JSON.stringify([h,hist]);}
function fit(ns,mode,d){
 const policy=new Map(),stat={cells:0,informative:0,rootCells:0,rootInfo:0};
 // Value with depth h, exact integer mass. Conditional next observation groups
 // retain full history implicitly because recursion never merges sibling paths.
 function val(xs,h){
  if(xs.every(n=>n.terminal))return sum(xs,n=>n.reward);
  if(h===0||xs.every(n=>n.o.status==="dead_end"))return 0;
  const as=ids(xs);if(!as.length)return 0;
  return Math.max(...as.map(a=>sum([...group(xs.map(n=>n.children[a]),mode).values()],g=>val(g,h-1))));
 }
 function walk(xs,h,hist){
  if(!h||xs.every(n=>n.terminal||n.o.status==="dead_end"))return 0;
  const as=ids(xs);if(!as.length)return 0;
  const scores=as.map(a=>sum([...group(xs.map(n=>n.children[a]),mode).values()],g=>val(g,Math.min(d,h)-1)));
  const hi=Math.max(...scores),inf=hi>Math.min(...scores);stat.cells++;stat.informative+=Number(inf);
  if(h===3){stat.rootCells++;stat.rootInfo+=Number(inf);}
  const selected=as[scores.indexOf(hi)],k=key(h,hist);ck(!policy.has(k),"history collision");policy.set(k,selected);
  for(const a of as)for(const [o,g] of group(xs.map(n=>n.children[a]),mode))walk(g,h-1,[...hist,a,o]);
  return hi;
 }
 let rootValue=0;for(const [o,g] of group(ns,mode))rootValue+=walk(g,3,[o]);
 return {policy,rootValue,...stat};
}
function metrics(ns,pick){
 let successes=0,steps=0,info=0,infoCorrect=0,regret=0,fallback=0;
 for(const root of ns){
  let n=root;const state={};
  for(let h=3;h>0&&!n.terminal;h--){
   const as=Object.keys(n.children);if(!as.length)break;
   const {action,fall}=pick(n,h,state),q=as.map(a=>n.children[a].full);
   ck(as.includes(action),"illegal policy action");fallback+=Number(!!fall);
   if(h===3){const hi=Math.max(...q),lo=Math.min(...q),correct=n.children[action].full===hi;regret+=hi-n.children[action].full;if(hi>lo){info++;infoCorrect+=Number(correct);}}
   n=n.children[action];steps++;
  }
  successes+=n.terminal?n.reward:0;
 }
 const full=sum(ns,n=>n.full);
 ck(successes<=full,"policy exceeds full ceiling");
 return {roots:ns.length,full,successes,steps,informative:info,informative_correct:infoCorrect,first_action_regret:regret,total_regret:full-successes,fallback};
}
function replay(ns,p,mode,menu=null){
 let hits=0,menuHits=0,firstHits=0,rootHits=0;
 const m=metrics(ns,(n,h,s)=>{
  const o=projection(n,mode),m=projection(n,"menu");
  s.hist=s.hist?[...s.hist,s.a,o]:[o];s.menu=s.menu?[...s.menu,s.a,m]:[m];
  const as=Object.keys(n.children);let a=p.get(key(h,s.hist)),fall=false;
  if(a&&as.includes(a)){hits++;rootHits+=Number(h===3);}else{
   fall=true;a=menu?.get(key(h,s.menu));if(a&&as.includes(a))menuHits++;else{a=as[0];firstHits++;}
  }
  s.a=a;return {action:a,fall};
 });
 return {...m,hits,menuHits,firstHits,rootHits};
}
function rankAction(n,k){const as=Object.keys(n.children);return {action:as[k]??as[0],fall:k>=as.length};}
function seqScore(ns,s){return metrics(ns,(n,h)=>rankAction(n,s[3-h]));}
function pageScore(ns,map){return metrics(ns,n=>rankAction(n,map[n.o.encounter]??0));}
function scriptFit(ns){
 let sequence=null,seqMetric=null;
 for(let i=0;i<64;i++){
  const s=[i>>4&3,i>>2&3,i&3],m=seqScore(ns,s);
  if(!seqMetric||m.successes>seqMetric.successes){sequence=s;seqMetric=m;}
 }
 const widths=new Map();
 function visit(n,h){
  if(!h||n.terminal)return;
  const as=Object.keys(n.children);if(!as.length)return;
  widths.set(n.o.encounter,Math.max(widths.get(n.o.encounter)??0,as.length));
  for(const x of Object.values(n.children))visit(x,h-1);
 }
 for(const n of ns)visit(n,3);
 const pages=[...widths].sort((a,b)=>a[0].localeCompare(b[0])),space=pages.reduce((s,x)=>s*x[1],1);
 let best=null,bestMap=null,checked=0;
 if(space<=DESIGN.cap){
  function search(i,map){
   if(i===pages.length){const m=pageScore(ns,map);checked++;if(!best||m.successes>best.successes){best=m;bestMap={...map};}return;}
   const [p,k]=pages[i];for(let j=0;j<k;j++){map[p]=j;search(i+1,map);}
  }
  search(0,{});ck(checked===space,"mapping count");
 }
 return {sequence:{rule:sequence,metrics:seqMetric,checked:64},page:{rule:bestMap,metrics:best,pages,space,checked,resolved:!!best}};
}
function simple(ns){
 return {first:seqScore(ns,[0,0,0]),last:metrics(ns,n=>rankAction(n,Object.keys(n.children).length-1)),truce:metrics(ns,n=>{const as=Object.keys(n.children);return {action:n.o.encounter===S&&as.includes(T)?T:as[0],fall:false};})};
}
function unique(n){
 const win=Object.entries(n.children).filter(([a,x])=>x.full).map(([a])=>a);
 return win.length===1?win[0]:null;
}
function reversals(ns,mode){
 const groups=new Map();
 for(const [i,n] of ns.entries()){
  const a=unique(n);if(!a)continue;
  const k=mode==="page"?n.o.encounter:projection(n,mode),g=groups.get(k)??[];g.push({i,a});groups.set(k,g);
 }
 let pairs=0,cells=0;const witnesses=[];
 for(const g of groups.values()){
  let count=0;
  for(let i=0;i<g.length;i++)for(let j=0;j<i;j++)if(g[i].a!==g[j].a){
   count++;if(witnesses.length<8)witnesses.push({roots:[g[j].i,g[i].i],actions:[g[j].a,g[i].a]});
  }
  pairs+=count;cells+=Number(count>0);
 }
 return {pairs,cells,witnesses};
}
function oracleTable(ns,train=null){
 const local={},transfer={},fits={};let prev=-1;
 for(const mode of DESIGN.modes){
  local[mode]={};transfer[mode]={};fits[mode]={};
  for(const d of DESIGN.depths){
   const f=fit(ns,mode,d),m=replay(ns,f.policy,mode);
   ck(m.firstHits===0&&m.menuHits===0,"self policy miss");
   if(d===3){ck(m.successes===f.rootValue,"oracle self replay");ck(m.successes>=prev,"channel nesting");prev=m.successes;}
   local[mode][d]={...m,objective_at_root:f.rootValue,cells:f.cells,informative_cells:f.informative,root_cells:f.rootCells,informative_root_cells:f.rootInfo};
   fits[mode][d]=f;
   if(train)transfer[mode][d]=replay(ns,train[mode][d].policy,mode,train.menu[d].policy);
  }
 }
 ck(local.public[3].successes<=sum(ns,n=>n.full),"public ceiling");
 const threshold=Math.ceil(.95*sum(ns,n=>n.full)),min=(t)=>Object.fromEntries(DESIGN.modes.map(m=>[m,DESIGN.depths.find(d=>t[m]?.[d]?.successes>=threshold)??null]));
 return {local,transfer:train?transfer:null,min_depth_95:{local:min(local),transfer:train?min(transfer):null,threshold},fits};
}
function compact(r){const {fits,...v}=r;return v;}
export function analyze(source,api=runtime){
 const w=api.compileV2(source),ct={transitions:0,nodes:0},out={};
 for(const [name,p] of Object.entries(DESIGN.upstream)){
  const cal=roots(api,w,DESIGN.cal,p,ct).map(x=>x.n),calT=oracleTable(cal),calScript=scriptFit(cal),calSimple=simple(cal);
  const cohorts=[];
  for(const c of DESIGN.val){
   const raw=roots(api,w,c,p,ct),ns=raw.map(x=>x.n),t=oracleTable(ns,calT.fits),s=scriptFit(ns),controls=simple(ns);
   const transferred={sequence:seqScore(ns,calScript.sequence.rule),page:calScript.page.resolved?pageScore(ns,calScript.page.rule):null};
   const ceil=t.local.goal4[3].successes;
   const rev=Object.fromEntries(["page",...DESIGN.modes].map(m=>[m,reversals(ns,m)]));
   const shortcut={sequence_fraction:ceil?s.sequence.metrics.successes/ceil:null,page_fraction:ceil&&s.page.resolved?s.page.metrics.successes/ceil:null,transferred_best_absolute:Math.max(transferred.sequence.successes,transferred.page?.successes??0)/ns.length};
   cohorts.push({cohort:c,full:sum(ns,n=>n.full),table:compact(t),scripts:s,transferred,controls,reversals:rev,shortcut});
  }
  const flag=cohorts.every(c=>c.shortcut.sequence_fraction!==null&&c.shortcut.sequence_fraction>=.9)||(name==="frozen"&&cohorts.every(c=>c.shortcut.transferred_best_absolute>=.8));
  out[name]={p,cal:{cohort:DESIGN.cal,full:sum(cal,n=>n.full),table:compact(calT),scripts:calScript,controls:calSimple},cohorts,review_flag:flag};
 }
 return {schema:"srg-ac04.v1",evidence:"source-executed actual SWMD runtime and finite empirical policy controls, no model calls",design:DESIGN,counts:ct,upstream:out};
}

// Post-hoc exact subset audit on the same public seeds. No new policy selection.
export function subsetAudit(source,api=runtime){
 const w=api.compileV2(source),counts={transitions:0,nodes:0},p=DESIGN.upstream.frozen;
 const ns=roots(api,w,DESIGN.cal,p,counts).map(x=>x.n),val=DESIGN.val.map(c=>roots(api,w,c,p,counts).map(x=>x.n));
 const fits={},rows=[],calMenu=fit(ns,"menu",1);
 for(const kind of ["pres","sub"])for(let mask=0;mask<8;mask++){
  const m=kind+mask,f=fit(ns,m,1);fits[m]=f;
  const cohorts=val.map(xs=>{
   const local=fit(xs,m,1),actual=replay(xs,f.policy,m,calMenu.policy),opt=fit(xs,m,3),optReplay=replay(xs,opt.policy,m);
   ck(optReplay.successes===opt.rootValue,"subset oracle replay");
   return {roots:xs.length,full:sum(xs,n=>n.full),local1:replay(xs,local.policy,m).successes,local3:optReplay.successes,transfer1:actual.successes,transfer:actual,rootCells:local.rootCells,strict_reversals:reversals(xs,m).pairs};
  });
  rows.push({kind,mask,records:ledger.filter((_,i)=>mask&(1<<i)),calibration:replay(ns,f.policy,m).successes,cohorts});
 }
 for(const kind of ["pres","sub"])for(let a=0;a<8;a++)for(let b=0;b<8;b++)if((a&b)===a){
  const x=rows.find(r=>r.kind===kind&&r.mask===a),y=rows.find(r=>r.kind===kind&&r.mask===b);
  ck(x.cohorts.every((c,i)=>c.local3<=y.cohorts[i].local3),"subset nesting");
 }
 for(let mask=0;mask<8;mask++){
  const x=rows.find(r=>r.kind==="pres"&&r.mask===mask),y=rows.find(r=>r.kind==="sub"&&r.mask===mask);
  ck(x.cohorts.every((c,i)=>c.local3<=y.cohorts[i].local3),"presence nesting");
 }
 const good=rows.filter(r=>r.cohorts.every(c=>c.transfer1>=Math.ceil(.95*c.full)));
 const min=good.length?Math.min(...good.map(r=>r.records.length)):null;
 return {scope:"post-hoc subset diagnostic, same public evaluation tapes, not fresh selected-policy validation",counts,rows,min_records_95:min,minimal:good.filter(r=>r.records.length===min).map(r=>({kind:r.kind,mask:r.mask,records:r.records,transfer:r.cohorts.map(c=>c.transfer1)}))};
}
