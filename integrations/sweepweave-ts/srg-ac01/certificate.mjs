// SRG-AC01: authoring certificate on the actual SWMD-SRG/2 semantics.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
const ck=(v,m)=>{if(!v)throw Error("SRG-AC01: "+m);};
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const own=(o,k)=>Object.hasOwn(o,k);
const eps=1e-10;
const keys=o=>Object.keys(o).sort();
const ptr=(n,out=new Set())=>{if(n.op==="pointer")out.add(n.key);for(const a of n.args??[])ptr(a,out);return out;};
const count=n=>1+(n.args??[]).reduce((s,a)=>s+count(a),0);
export function inventory(w){
 const vars=Object.fromEntries(Object.entries(w.coordinates).map(([k,v])=>[k,{visibility:v.visibility,reads:{},writes:0}]));
 const meta={},formulas=[],orderedEdges=[];
 function add(page,action,reaction,role,n,target=null){
  const reads=[...ptr(n)].sort(),id=formulas.length;
  formulas.push({id,page,action,reaction,role,target,nodes:count(n),reads});
  for(const k of reads){const v=vars[k]??(meta[k]??={reads:{}});v.reads[role]=(v.reads[role]??0)+1;}
  if(target&&own(vars,target))vars[target].writes++;
 }
 for(const p of Object.values(w.pages)){
  add(p.id,null,null,"encounter_gate",p.gate);add(p.id,null,null,"wild_priority",p.priority);
  for(const o of Object.values(p.options)){
   add(p.id,o.id,null,"option_visible",o.visible);add(p.id,o.id,null,"option_performable",o.performable);
   for(const r of o.reactions){
    add(p.id,o.id,r.id,"reaction_gate",r.gate);add(p.id,o.id,r.id,"desirability",r.desirability);
    const last=new Map();
    for(const [i,e] of r.effects.entries()){
     const target=e.kind==="spool"?"__srg.ACTIVE_"+e.key:e.key;
     add(p.id,o.id,r.id,"effect",e.value,target);
     for(const k of ptr(e.value))if(last.has(k))orderedEdges.push({reaction:r.id,write:last.get(k),read:i,key:k,target});
     last.set(target,i);
    }
   }
  }
 }
 return {coordinates:vars,meta,formula_count:formulas.length,formulas,ordered_write_edges:orderedEdges,static_unread:keys(vars).filter(k=>!Object.keys(vars[k].reads).length)};
}
function value(api,w,s,h,goal){
 const o=api.observeV2(w,s);
 if(o.status==="terminal")return Number(s.encounter===goal);
 if(h===0||o.status==="dead_end")return 0;
 return Math.max(...o.actions.map(a=>value(api,w,api.stepV2(w,s,a.id).next,h-1,goal)));
}
function qvec(api,w,s,h,goal){
 const o=api.observeV2(w,s);
 if(o.status!=="decision")return {};
 return Object.fromEntries(o.actions.map(a=>[a.id,value(api,w,api.stepV2(w,s,a.id).next,h-1,goal)]));
}
function informative(q){const v=Object.values(q);return v.length>1&&Math.max(...v)>Math.min(...v);}
function audit(api,w,s,goal){
 const a=api.auditV2(w,s).actions,menu=a.map(x=>x.id),all={};
 for(const x of a){
  ck(x.status==="ok","blocked selected branch");
  const b=x.branches.find(b=>b.id===x.selected),score=x.scores.map(t=>[t.id,t.eligible,t.score]);
  const contrasts=[];
  for(let i=0;i<score.length;i++)for(let j=0;j<i;j++)if(score[i][1]&&score[j][1])contrasts.push([score[i][0],score[j][0],score[i][2]-score[j][2]]);
  const writes=Object.fromEntries(Object.entries(b.next.values).map(([k,v])=>[k,v-s.values[k]]).filter(([,v])=>Math.abs(v)>eps));
  all[x.id]={score,contrasts,winners:x.winners,selected:x.selected,route:b.next.encounter,guard:b.guard_admitted,writes,spools:b.next.spools,energy:b.squared_step_energy};
 }
 return {menu,all,q1:qvec(api,w,s,1,goal),q3:qvec(api,w,s,3,goal)};
}
const numEq=(a,b)=>typeof a==="number"&&typeof b==="number"?Math.abs(a-b)<=eps:a===b;
function deepEq(a,b){
 if(a===null||b===null||typeof a!=="object"||typeof b!=="object")return numEq(a,b);
 return same(keys(a),keys(b))&&keys(a).every(k=>deepEq(a[k],b[k]));
}
const FLAGS=["menu","score","eligibility","contrast","winner","selected","route","effect","q1","q3"];
function compare(a,b){
 const f=Object.fromEntries(FLAGS.map(k=>[k,false]));
 f.menu=!same(a.menu,b.menu);
 for(const k of a.menu.filter(k=>own(b.all,k))){
  const x=a.all[k],y=b.all[k];
  f.score||=!deepEq(x.score,y.score);
  f.eligibility||=!same(x.score.map(v=>v.slice(0,2)),y.score.map(v=>v.slice(0,2)));
  f.contrast||=!deepEq(x.contrasts,y.contrasts);
  f.winner||=!same(x.winners,y.winners);f.selected||=x.selected!==y.selected;
  f.route||=x.route!==y.route||x.guard!==y.guard;
  f.effect||=!deepEq(x.writes,y.writes)||!deepEq(x.spools,y.spools);
 }
 f.q1=!same(a.q1,b.q1);f.q3=!same(a.q3,b.q3);
 return f;
}
const zero=()=>({pairs:0,invalid:0,...Object.fromEntries(FLAGS.map(k=>[k,0])),witnesses:{}});
function accumulate(v,f,witness){
 v.pairs++;for(const k of FLAGS)if(f[k]){v[k]++;if(!v.witnesses[k])v.witnesses[k]=witness;}
}
const summary=(a,b)=>({a:{menu:a.menu,q1:a.q1,q3:a.q3,selected:Object.fromEntries(Object.entries(a.all).map(([k,v])=>[k,v.selected]))},b:{menu:b.menu,q1:b.q1,q3:b.q3,selected:Object.fromEntries(Object.entries(b.all).map(([k,v])=>[k,v.selected]))}});
const rng=seed=>{let x=seed>>>0||1;return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};};
export const REAL={seed:0x535221a1,roots:12,budget:24,delta:.125,page:"page_sirens_at_the_rollup_door",goal:"page_secret_undercover_truce"};
function prefixes(api,w,contract){
 const rand=rng(contract.seed),roots=[];
 for(let rep=0;rep<contract.roots;rep++){
  const words=Array.from({length:contract.budget},rand);let s=api.initialV2(w),history=[],energy=[];
  for(const word of words){
   if(s.encounter===contract.page){roots.push({rep,s,history,energy});break;}
   const o=api.observeV2(w,s);if(o.status!=="decision")break;
   const a=o.actions[Math.floor(word*o.actions.length/4294967296)].id,b=api.stepV2(w,s,a);
   history.push(a);energy.push(b.squared_step_energy);s=b.next;
  }
 }
 return roots;
}
export function auditAuthored(source,contract=REAL,api=runtime){
 const w=api.compileV2(source),inv=inventory(w),roots=prefixes(api,w,contract),ks=keys(w.coordinates),stats=Object.fromEntries(ks.map(k=>[k,zero()]));
 const base=roots.map(r=>audit(api,w,r.s,contract.goal)),reachable=Object.fromEntries(ks.map(k=>[k,zero()]));
 let probes=0,invalid=0,exact_state_pairs=0;
 for(let i=0;i<roots.length;i++)for(let j=0;j<i;j++){
  const a=roots[i].s,b=roots[j].s;
  if(!same([a.encounter,a.turn,a.spools,a.seen,a.visited],[b.encounter,b.turn,b.spools,b.seen,b.visited]))continue;
  const diff=ks.filter(k=>a.values[k]!==b.values[k]);
  if(diff.length!==1)continue;
  exact_state_pairs++;const k=diff[0],f=compare(base[i],base[j]);
  accumulate(reachable[k],f,{roots:[roots[i].rep,roots[j].rep],values:[a.values[k],b.values[k]],...summary(base[i],base[j])});
 }
 for(const [i,r] of roots.entries())for(const k of ks)for(const sign of [-1,1]){
  const v=Math.max(-1,Math.min(1,r.s.values[k]+sign*contract.delta));if(v===r.s.values[k])continue;
  probes++;const s={...r.s,values:{...r.s.values,[k]:v}};
  let b;try{b=audit(api,w,s,contract.goal);}catch(e){stats[k].invalid++;invalid++;continue;}
  accumulate(stats[k],compare(base[i],b),{root:r.rep,history:r.history,coordinate:k,from:r.s.values[k],to:v,...summary(base[i],b)});
 }
 const rootRows=roots.map((r,i)=>({rep:r.rep,history:r.history,q1:base[i].q1,q3:base[i].q3,informative1:informative(base[i].q1),informative3:informative(base[i].q3),energy_prefix_sum:r.energy.reduce((s,e)=>s+e,0),max_prefix_energy:Math.max(0,...r.energy),root_max_energy:Math.max(0,...Object.values(base[i].all).map(x=>x.energy))}));
 const totals=Object.fromEntries(FLAGS.map(k=>[k,ks.reduce((s,v)=>s+stats[v][k],0)]));
 const classified=Object.fromEntries(FLAGS.map(k=>[k,ks.filter(v=>stats[v][k]>0)]));
 return {world:w.id,contract,inventory:inv,roots:rootRows,root_count:roots.length,exact_state_pairs,probes,invalid,totals,classified,reachable,interventions:stats,
 interpretation:"Reachable exact-state matches preserve full discrete history. Coordinate perturbations are local structural interventions, not proof of feasible authored histories. Zero observed effect does not establish irrelevance. Utility is existential full-state reachability, not an observation-constrained policy."};
}
// Controlled, legally reached Boolean cubes. Each prefix choice sets a
// single signed coordinate; decision suffix has no history/spool reads.
export function fixture(J,K,hidden=false){
 ck(J>=1&&J<=5&&K>=J+2,"fixture dimensions");
 const bit=j=>"state.bit"+j,common="state.common",effect="state.effect",ledger="state.ledger",dims=J+2,p=i=>"p"+i,lines=["# SWMD-SRG/2","id: AC-cube","title: \"Dock inspection\"","about: \"Set inspection evidence, choose a dock, then finish delivery.\"","start: p0","turn-base: 0","tie: first","direct: strict"];
 for(let j=0;j<J;j++)lines.push("VAR "+bit(j)+" = 0 | "+(hidden&&j===0?"hidden":"public"));
 lines.push("VAR "+common+" = 0 | public","VAR "+effect+" = 0 | public","VAR "+ledger+" = 0 | hidden");
 for(let j=J+2;j<K;j++)lines.push("VAR state.pad"+j+" = 0 | public");
 const pages=[...Array.from({length:dims+1},(_,i)=>p(i)),"good_wait","bad_wait","goal","fail"];
 lines.push("SPOOL all | A:TRUE | E:"+pages.join(","));
 const enc=(id,turn)=>lines.push("ENC "+id+" turn="+turn+".."+turn+" | I:"+turn+" | A:TRUE | Q:C(0) | N:"+JSON.stringify(id)+" | T:\"Inspect the available evidence.\"");
 const opt=(a,text)=>lines.push("OPT "+a+" | V:TRUE | P:TRUE | T:"+JSON.stringify(text));
 const rx=(a,r,to,E,D="C(0)")=>lines.push("ORX "+a+"/"+r+" -> "+to+" | E:"+E+" | D:"+D+" | G:TRUE | T:\"The process continues.\"");
 for(let j=0;j<dims;j++){
  enc(p(j),j);const k=j<J?bit(j):j===J?common:effect;
  for(const s of [-1,1]){const a="set_"+j+"_"+(s===1?"pos":"neg");opt(a,"Set "+k+" to "+s);rx(a,"r_"+a,p(j+1),"SET "+k+" = C("+s+")");}
 }
 enc(p(dims),dims);const prod=J===1?"P("+bit(0)+")":"MUL("+Array.from({length:J},(_,j)=>"P("+bit(j)+")").join(",")+")";
 for(const dock of [-1,1]){
  const a=dock===1?"dock_pos":"dock_neg";opt(a,"Choose dock "+dock);
  const e="SET "+ledger+" = MUL(C(.125),P("+effect+"))";
  for(const win of [true,false]){
   const d="ADD(MUL(C("+(.25*dock*(win?1:-1))+"),"+prod+"),MUL(C(.125),P("+common+")))";
   rx(a,"r_"+a+"_"+Number(win),win?"good_wait":"bad_wait",e,d);
  }
 }
 for(const good of [true,false]){const p=good?"good_wait":"bad_wait";enc(p,dims+1);opt("finish_"+p,"Finish delivery");rx("finish_"+p,"r_finish_"+p,good?"goal":"fail","NONE");}
 enc("goal",dims+2);enc("fail",dims+2);return lines.join("\n")+"\n";
}
function pop(x){let n=0;while(x){n+=x&1;x>>>=1;}return n;}
function degree(a){
 const n=Math.log2(a.length),coef=[];
 for(let mask=0;mask<a.length;mask++){
  let c=0;for(let x=0;x<a.length;x++)c+=((pop(x&mask)&1)?-1:1)*a[x];
  c/=a.length;if(Math.abs(c)>eps)coef.push({mask,degree:pop(mask),coefficient:c});
 }
 return {degree:Math.max(0,...coef.map(x=>x.degree)),coefficients:coef,n};
}
function obsKey(api,w,s){return JSON.stringify(api.observeV2(w,s));}
function observationBound(roots,signature){
 const groups=new Map();for(const r of roots){const k=signature(r),g=groups.get(k)??[];g.push(r);groups.set(k,g);}
 let value=0;for(const g of groups.values())value+=Math.max(...keys(g[0].a.q3).map(k=>g.reduce((s,r)=>s+r.a.q3[k],0)));
 return {cells:groups.size,numerator:value,denominator:roots.length};
}
export function auditCube(J,K,hidden=false,api=runtime){
 const w=api.compileV2(fixture(J,K,hidden)),n=J+2,roots=[];
 for(let mask=0;mask<2**n;mask++){
  let s=api.initialV2(w),history=[];
  for(let j=0;j<n;j++){const a="set_"+j+"_"+((mask>>j)&1?"neg":"pos");history.push(a);s=api.stepV2(w,s,a).next;}
  roots.push({s,history,a:audit(api,w,s,"goal")});
 }
 const names=[...Array.from({length:J},(_,j)=>"state.bit"+j),"state.common","state.effect"],stats=Object.fromEntries(names.map(k=>[k,zero()]));
 for(let j=0;j<n;j++)for(let m=0;m<roots.length;m++)if(!(m&(1<<j))){
  const x=roots[m],y=roots[m|(1<<j)],f=compare(x.a,y.a);
  ck(keys(x.s.values).filter(k=>x.s.values[k]!==y.s.values[k]).join("")===names[j],"cube pair");
  accumulate(stats[names[j]],f,{masks:[m,m|(1<<j)],...summary(x.a,y.a)});
 }
 const inv=inventory(w),suffix=inv.formulas.filter(f=>!/^p[0-9]+$/.test(f.page)||f.page==="p"+n);
 ck(suffix.every(f=>f.reads.every(k=>!k.startsWith("__srg."))),"history-sensitive suffix");
 for(let j=0;j<J;j++){const v=stats[names[j]];ck(v.pairs===v.contrast&&v.pairs===v.selected&&v.pairs===v.route&&v.pairs===v.q3&&v.q1===0,"causal edge");}
 const c=stats["state.common"],e=stats["state.effect"];
 ck(c.score===c.pairs&&c.contrast===0&&c.selected===0&&c.q3===0,"common mode");
 ck(e.effect===e.pairs&&e.score===0&&e.q3===0,"effect only");
 const d=degree(roots.map(r=>r.a.all.dock_pos.score[0][2]-r.a.all.dock_pos.score[1][2]));
 const u=degree(roots.map(r=>r.a.q3.dock_pos));
 ck(d.degree===J&&u.degree===J,"Walsh degree");
 const current=observationBound(roots,r=>obsKey(api,w,r.s)),history=observationBound(roots,r=>JSON.stringify([obsKey(api,w,r.s),r.history]));
 ck(current.numerator===(hidden?roots.length/2:roots.length)&&history.numerator===roots.length,"belief ceiling");
 ck(roots.every(r=>!informative(r.a.q1)&&informative(r.a.q3)),"delayed utility");
 return {J,K,hidden,roots:roots.length,edges:n*roots.length/2,contrast_degree:d,utility_degree:u,current,history,stats,static_unread:inv.static_unread,temporal:{h1_informative:0,h3_informative:roots.length},proof_scope:"Full legal prefix cube, suffix excludes meta pointers. Pairs differ in one numeric coordinate but have different prefix histories. The continuation ignores those history differences; turn, page, active spool and unseen suffix destinations are fixed."};
}
export function verify(api=runtime){
 const rows=[];for(const J of [1,3,5])for(const K of [8,32])for(const hidden of [false,true])rows.push(auditCube(J,K,hidden,api));
 return {fixtures:rows.length,roots:rows.reduce((s,r)=>s+r.roots,0),edges:rows.reduce((s,r)=>s+r.edges,0),rows};
}
