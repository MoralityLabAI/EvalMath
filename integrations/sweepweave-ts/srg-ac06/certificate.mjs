// SRG-AC06: exact finite observation-subset sufficiency.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
const ck=(v,m)=>{if(!v)throw Error("AC06: "+m);};
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b),sum=(a,f)=>a.reduce((s,x)=>s+f(x),0);
const pop=m=>{let n=0;for(;m;m>>>=1)n+=m&1;return n;};
const S="page_sirens_at_the_rollup_door",G="page_secret_undercover_truce";
const sites=["page_start","page_pink_ambush_theory","page_cadillac_trunk","page_eddie_and_blonde_story"];
export const FEATURES=["char_pink.Timeline_Record","char_pink.Radio_Record","char_pink.Review_Request","char_pink.Rat_Suspicion","char_blonde.Sadistic_Escalation","char_white.Crew_Loyalty"];
export const DESIGN={cal:{seed:0x53522601,n:96},val:[{seed:0x53522611,n:128},{seed:0x53522612,n:128}],budget:24,H:3,upstream:{baseline:["r","r","r","r"],all:["r",0,2,2],frozen:[0,0,1,2]},features:FEATURES};
const fresh=()=>({prefix_steps:0,suffix_steps:0,nodes:0,subset_fits:0,subset_edges:0,policy_replays:0,conflict_checks:0});
function tapes(c){
 let x=c.seed>>>0;ck(x!==0,"zero seed");
 const r=()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};
 return Array.from({length:c.n},()=>Array.from({length:DESIGN.budget},r));
}
function tree(api,w,s,h,ct,goal=G){
 const o=api.observeV2(w,s),n={o,terminal:o.status==="terminal",reward:Number(o.status==="terminal"&&s.encounter===goal),children:{},full:0};
 ct.nodes++;
 if(n.terminal){n.full=n.reward;return n;}
 if(!h||o.status!=="decision")return n;
 for(const a of o.actions){const b=api.stepV2(w,s,a.id);ct.suffix_steps++;n.children[a.id]=tree(api,w,b.next,h-1,ct,goal);}
 n.full=Math.max(0,...Object.values(n.children).map(x=>x.full));return n;
}
function population(api,w,c,ct){
 const out=[],ts=tapes(c),seen=new Map();let raw=0;
 for(const [arm,p] of Object.entries(DESIGN.upstream))for(const [rep,words] of ts.entries()){
  let s=api.initialV2(w),visits=0,history=[];
  for(let i=0;i<words.length&&s.encounter!==S;i++){
   const o=api.observeV2(w,s);ck(o.status==="decision"&&o.actions.length,"blocked prefix");
   let a=o.actions[Math.floor(words[i]*o.actions.length/4294967296)].id,idx=sites.indexOf(s.encounter);
   if(idx>=0&&!(visits&(1<<idx))){
    visits|=1<<idx;if(p[idx]!=="r"){a="opt_"+sites[idx]+"_"+p[idx];ck(o.actions.some(x=>x.id===a),"override unavailable");}
   }
   const b=api.stepV2(w,s,a);ct.prefix_steps++;history.push([a,b.id]);s=b.next;
  }
  ck(s.encounter===S,"missed first sirens");raw++;
  const key=JSON.stringify(history),n=tree(api,w,s,3,ct);
  if(seen.has(key)){const old=seen.get(key);ck(eq(old.s,s)&&eq(q(old.n),q(n)),"duplicate history mismatch");old.multiplicity++;continue;}
  const row={arm,rep,history,key,s,n,multiplicity:1};seen.set(key,row);out.push(row);
 }
 return {raw,rows:out};
}
function q(n){return Object.fromEntries(Object.entries(n.children).map(([a,t])=>[a,t.full]));}
function strict(n){const a=Object.keys(n.children).filter(a=>n.children[a].full);return a.length===1?a[0]:null;}
function inf(n){const v=Object.values(q(n));return v.length>1&&Math.max(...v)>Math.min(...v);}
function menu(n){const o=n.o;return [o.encounter,o.turn,o.status,o.actions];}
function feature(n,i){const k=FEATURES[i];ck(Object.hasOwn(n.o.values,k),"hidden feature");const x=n.o.values[k];return i<3?x:Math.min(15,Math.floor((x+1)*8));}
function presence(n){ck(Object.hasOwn(n.o.values,FEATURES[2]),"hidden review");return Number(n.o.values[FEATURES[2]]>0);}
function project(n,mask,weak=false){
 const m=menu(n),v=[];
 if(weak||mask==="weak")v.push(presence(n));
 if(mask==="public")v.push(Object.entries(n.o.values).sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:0));
 else if(Number.isInteger(mask))for(let i=0;i<FEATURES.length;i++)if(mask&(1<<i))v.push(feature(n,i));
 return JSON.stringify([m,v]);
}
function groups(xs,proj){const m=new Map();for(const n of xs){const k=proj(n),a=m.get(k)??[];a.push(n);m.set(k,a);}return m;}
function actions(xs){const a=Object.keys(xs[0].children);ck(xs.every(n=>eq(Object.keys(n.children),a)),"unequal menu");return a;}
function fit(ns,proj,H,ct){
 const policy=new Map();let cells=0,info=0;
 function go(xs,h,hist){
  if(xs.every(n=>n.terminal))return sum(xs,n=>n.reward);
  if(h===0||xs.every(n=>n.o.status==="dead_end"))return 0;
  const as=actions(xs);ck(as.length,"empty decision");
  const vals=as.map(a=>sum([...groups(xs.map(n=>n.children[a]),proj)],([k,g])=>go(g,h-1,[...hist,a,k])));
  const best=Math.max(...vals),key=JSON.stringify([h,hist]);ck(!policy.has(key),"history collision");policy.set(key,as[vals.indexOf(best)]);
  cells++;info+=Number(best>Math.min(...vals));return best;
 }
 const v=sum([...groups(ns,proj)],([k,g])=>go(g,H,[k])),full=sum(ns,n=>n.full);
 let first=0;
 for(const g of groups(ns,proj).values()){
  if(g.every(n=>n.terminal)){first+=sum(g,n=>n.reward);continue;}
  const as=actions(g);first+=Math.max(0,...as.map(a=>sum(g,n=>n.children[a].full)));
 }
 ck(v<=first&&first<=full,"oracle bounds");
 ct.subset_fits++;
 return {policy,value:v,privileged:first,full,cells,informative_cells:info,initial_gap:full-first,continuation_gap:first-v};
}
function replay(ns,fit,proj,H,ct,fallback=null){
 let successes=0,hits=0,menuHits=0,firstHits=0,steps=0;
 for(const root of ns){
  let n=root,hist=[proj(n)],m=[project(n,0)];
  for(let h=H;h>0&&!n.terminal;h--){
   const as=Object.keys(n.children);if(!as.length)break;
   let a=fit.get(JSON.stringify([h,hist]));
   if(a&&as.includes(a))hits++;else{a=fallback?.get(JSON.stringify([h,m]));if(a&&as.includes(a))menuHits++;else{a=as[0];firstHits++;}}
   n=n.children[a];steps++;hist.push(a,proj(n));m.push(a,project(n,0));
  }
  successes+=n.terminal?n.reward:0;
 }
 ct.policy_replays++;ck(successes<=sum(ns,n=>n.full),"rollout bound");return {roots:ns.length,successes,hits,menuHits,firstHits,steps};
}
function firstLegal(ns,H){let v=0;for(const root of ns){let n=root;for(let h=H;h>0&&!n.terminal;h--){const a=Object.values(n.children);if(!a.length)break;n=a[0];}v+=n.terminal?n.reward:0;}return v;}
function minimal(masks){
 const set=new Set(masks);return masks.filter(m=>{for(let i=0;i<31;i++)if((m&(1<<i))&&set.has(m^(1<<i)))return false;return true;});
}
function summarize(rows,target){
 const masks=rows.filter(x=>x.value>=target).map(x=>x.mask),k=masks.length?Math.min(...masks.map(pop)):null;
 return {target,min_cardinality:k,minimum_masks:k===null?[]:masks.filter(m=>pop(m)===k),inclusion_minimal:minimal(masks)};
}
function subsetAudit(ns,ct,{weak=false}={}){
 const rows=[],fits=[];
 for(let m=0;m<64;m++){
  const proj=n=>project(n,m,weak),f=fit(ns,proj,3,ct),d=replay(ns,f.policy,proj,3,ct);
  ck(d.successes===f.value&&d.firstHits===0,"oracle self replay");
  const {policy,...v}=f;rows.push({mask:m,k:pop(m),...v});fits.push(f);
 }
 for(let m=0;m<64;m++)for(let j=0;j<6;j++)if(!(m&(1<<j))){
  const a=rows[m],b=rows[m|(1<<j)];ck(a.value<=b.value&&a.privileged<=b.privileged,"subset monotonicity");ct.subset_edges++;
 }
 const full=rows[0].full,all=rows[63].value;
 const frontier=Array.from({length:7},(_,k)=>{const r=rows.filter(x=>x.k===k),max=Math.max(...r.map(x=>x.value));return {k,value:max,masks:r.filter(x=>x.value===max).map(x=>x.mask)};});
 return {rows,fits,full,all,frontier,full_min:summarize(rows,full),all_min:summarize(rows,all),near_min:summarize(rows,Math.ceil(.95*full))};
}
function conflictAudit(ns,ct,weak=false){
 const stricts=ns.filter(n=>strict(n)),base=n=>project(n,0,weak),by=groups(stricts,base),hist=Array(64).fill(0);
 for(const xs of by.values())for(let i=0;i<xs.length;i++)for(let j=0;j<i;j++){
  if(strict(xs[i])===strict(xs[j]))continue;
  let diff=0;for(let k=0;k<6;k++)if(feature(xs[i],k)!==feature(xs[j],k))diff|=1<<k;
  hist[diff]++;
 }
 const masks=[],nonzero=[],collisions=[];
 for(let m=0;m<64;m++){
  const predicted=sum(hist,(n,d)=>0); // independent calculation below
  let miss=0;for(let d=0;d<64;d++)if(!(m&d))miss+=hist[d];
  let actual=0;
  for(const g of groups(stricts,n=>project(n,m,weak)).values()){
   const a=new Map();for(const n of g){const x=strict(n);a.set(x,(a.get(x)??0)+1);}
   const counts=[...a.values()];for(let i=0;i<counts.length;i++)for(let j=0;j<i;j++)actual+=counts[i]*counts[j];
  }
  ck(actual===miss,"conflict mask equivalence");ct.conflict_checks++;
  collisions.push(miss);if(miss===0)masks.push(m);if(miss===hist[0])nonzero.push(m);
 }
 return {strict_roots:stricts.length,total_pairs:sum(hist,x=>x),unseparable:hist[0],conflict_masks:hist.map((n,mask)=>({mask,count:n})).filter(x=>x.count),collisions,collision_free:minimal(masks),hits_all_separable:minimal(nonzero),min_cardinality:masks.length?Math.min(...masks.map(pop)):null};
}
function paired(rows,ct){
 const g=new Map();
 for(const r of rows){const a=strict(r.n);if(!a)continue;const k=project(r.n,0,true),by=g.get(k)??new Map(),xs=by.get(a)??[];xs.push(r);by.set(a,xs);g.set(k,by);}
 const pairs=[],used=new Set();let capacity=0;
 for(const by of g.values()){
  const sizes=[...by.values()].map(x=>x.length),N=sum(sizes,x=>x),cap=Math.min(Math.floor(N/2),N-Math.max(...sizes)),before=pairs.length;capacity+=cap;
  for(;;){
   const b=[...by].filter(([,xs])=>xs.length).sort((a,b)=>b[1].length-a[1].length||(a[0]<b[0]?-1:1));
   if(b.length<2)break;
   const a=b[0][1].shift(),c=b[1][1].shift();ck(!used.has(a.key)&&!used.has(c.key)&&strict(a.n)!==strict(c.n)&&project(a.n,0,true)===project(c.n,0,true),"pair invariant");
   used.add(a.key);used.add(c.key);pairs.push([a,c]);
  }
  ck(pairs.length-before===cap,"pair capacity");
 }
 const ns=pairs.flatMap(p=>p.map(r=>r.n));
 if(!ns.length)return {pairs:0,capacity,roots:0,subset:null,conflicts:null};
 const a=subsetAudit(ns,ct,{weak:true}),conflicts=conflictAudit(ns,ct,true);
 ck(a.full===2*pairs.length&&a.rows[0].value<=pairs.length,"weak pair upper bound");
 const {fits,...subset}=a;
 const describe=r=>({arm:r.arm,rep:r.rep,history:r.history,q:q(r.n),values:FEATURES.map((_,i)=>feature(r.n,i))});
 return {pairs:pairs.length,capacity,roots:ns.length,subset,conflicts,examples:pairs.slice(0,8).map(([a,b])=>({projection:JSON.parse(project(a.n,0,true)),a:describe(a),b:describe(b)}))};
}
function getFit(ns,mask,ct){
 const proj=n=>project(n,mask),f=fit(ns,proj,3,ct),r=replay(ns,f.policy,proj,3,ct);ck(r.successes===f.value&&r.firstHits===0,"extra oracle replay");return f;
}
function strip(f){const {policy,...v}=f;return v;}
function cohortAudit(p,ct){
 const ns=p.rows.map(r=>r.n),a=subsetAudit(ns,ct),weak=getFit(ns,"weak",ct),pub=getFit(ns,"public",ct),conflicts=conflictAudit(ns,ct),pairs=paired(p.rows,ct);
 ck(pub.value>=a.all&&weak.value>=a.rows[0].value,"extra nesting");
 const {fits,...summary}=a;
 return {fits,weak,pub,receipt:{raw_roots:p.raw,distinct_histories:p.rows.length,informative_roots:sum(ns,n=>Number(inf(n))),subset:summary,weak:strip(weak),public:strip(pub),conflicts,pairs,first_legal:firstLegal(ns,3)}};
}
export function calibration(src,api=runtime){
 const w=api.compileV2(src),ct=fresh(),p=population(api,w,DESIGN.cal,ct),a=cohortAudit(p,ct),s=a.receipt.subset;
 const selected=Math.min(...s.all_min.minimum_masks);ck(Number.isInteger(selected),"selection");
 return {schema:"ac06.cal.v1",cohort:DESIGN.cal,counts:ct,selected,selected_features:FEATURES.filter((_,i)=>selected&(1<<i)),...a.receipt};
}
export function validation(src,frozen,api=runtime){
 const w=api.compileV2(src),ct=fresh(),cal=population(api,w,DESIGN.cal,ct),train=cal.rows.map(r=>r.n),f=cohortAudit(cal,ct);
 const selected=Math.min(...f.receipt.subset.all_min.minimum_masks);ck(selected===frozen.selected,"frozen mask drift");
 const calKeys=new Set(cal.rows.map(r=>r.key)),cohorts=[],prev=new Set();
 for(const co of DESIGN.val){
  const p=population(api,w,co,ct),a=cohortAudit(p,ct),ns=p.rows.map(r=>r.n),novel=p.rows.filter(r=>!calKeys.has(r.key)),nns=novel.map(r=>r.n);
  const full= sum(nns,n=>n.full),transfers={},novelTransfers={};
  for(const [name,mask,fit] of [["frozen",selected,f.fits[selected]],["all6",63,f.fits[63]],["weak","weak",f.weak],["public","public",f.pub],["menu",0,f.fits[0]]]){
   const proj=n=>project(n,mask),d=replay(ns,fit.policy,proj,3,ct,f.fits[0].policy),nd=replay(nns,fit.policy,proj,3,ct,f.fits[0].policy);
   const oracle=mask==="weak"?a.receipt.weak.value:mask==="public"?a.receipt.public.value:a.receipt.subset.rows[mask].value;ck(d.successes<=oracle,"transfer exceeds cohort oracle");
   transfers[name]=d;novelTransfers[name]=nd;
  }
  const localNovel={};for(const [name,mask] of [["frozen",selected],["all6",63],["weak","weak"],["public","public"],["menu",0]])localNovel[name]=strip(getFit(nns,mask,ct));
  const shared_previous=p.rows.filter(r=>prev.has(r.key)).length;
  for(const r of p.rows)prev.add(r.key);
  cohorts.push({cohort:co,...a.receipt,overlap_calibration:p.rows.length-novel.length,overlap_previous_evaluation:shared_previous,novel:{roots:novel.length,full,first_legal:firstLegal(nns,3),local:localNovel,transfer:novelTransfers},transfer:transfers});
 }
 return {schema:"ac06.validation.v1",selected,counts:ct,cohorts};
}
