// SRG-10: observer-specific adaptive evidence and temporal source dependencies.
// All uncertainty is represented by finite integer-weighted latent tapes.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';

export const FAMILIES=Object.freeze(["specialist","common_cause","temporal"]);
const VIEWS=["analyst","reviewer","blind","joint"];
const SIGNS=[-1,1],QS=["x","y","q"],DEN=131072;
const fail=m=>{throw Error("SRG10: "+m);};
const q=JSON.stringify,C=x=>"C("+x+")",P=k=>"P("+k+")";
const sum=(a,f)=>a.reduce((n,x)=>n+f(x),0);
function group(a,f){const m=new Map();for(const x of a){const k=f(x);if(!m.has(k))m.set(k,[]);m.get(k).push(x);}return [...m.values()];}
const best=s=>{const value=Math.max(...Object.values(s));return {value,winners:Object.keys(s).filter(k=>s[k]===value)};};
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const own=(x,k)=>Object.hasOwn(x,k);
export const CONFIGS=Object.freeze([
 {family:"specialist",a:7,b:6,strong:7,weak:4,aux:7,cost:1,settle:9},
 {family:"common_cause",a:7,b:6,strong:7,weak:4,aux:7,cost:1,settle:9},
 {family:"temporal",a:7,b:6,strong:7,weak:4,aux:7,cost:1,settle:9}
]);
const key={t:"world.truth",z:"world.context",a:"analyst.context[reviewer][source]",b:"reviewer.report[analyst]",x:"source.x",y:"source.y",q:"source.q"};
const pub={a:"analyst.initial",b:"reviewer.initial",x:"public.x",y:"public.y",q:"public.q"};

function validate(c){
 if(!FAMILIES.includes(c.family))fail("family");
 for(const k of ["a","b","strong","weak","aux"])if(!Number.isInteger(c[k])||c[k]<4||c[k]>8)fail("invalid reliability "+k);
 if(c.strong<c.weak||!Number.isInteger(c.cost)||c.cost<0||c.cost>3||!Number.isInteger(c.settle)||c.settle<0||c.settle>16)fail("invalid payoff");
}
export function tapes(c){
 validate(c);const out=[],weight=(v,truth,p)=>v===truth?p:8-p;
 for(const t of SIGNS)for(const z of SIGNS)for(const a of SIGNS)for(const b of SIGNS)for(const x of SIGNS)for(const y of SIGNS)for(const q of SIGNS){
   let m;
   if(c.family==="specialist")m=weight(a,z,c.a)*weight(b,t,c.b)*weight(x,t,z===1?c.strong:c.weak)*weight(y,t,z===-1?c.strong:c.weak)*weight(q,z,c.aux);
   else if(c.family==="common_cause")m=weight(a,z,c.a)*weight(b,t,c.b)*weight(x,t*z,c.strong)*(y===x?8:0)*weight(q,t,c.aux);
   else m=weight(a,t*z,c.a)*weight(b,z,c.b)*weight(x,t*z,c.strong)*weight(y,t,c.weak)*weight(q,z,c.aux);
   if(m)out.push({t,z,a,b,x,y,q,m});
 }
 if(sum(out,x=>x.m)!==DEN)fail("mass");
 return out;
}
function description(c,view){
 const p=(k)=>c[k]+"/8";
 const rules=c.family==="specialist"
 ? "T and Z are independent uniform signs. Analyst initial report estimates Z with reliability "+p("a")+"; reviewer initial report estimates T with reliability "+p("b")+". X estimates T with reliability "+p("strong")+" when Z is positive and "+p("weak")+" otherwise. Y swaps those reliabilities. Q estimates Z with reliability "+p("aux")+". Reports are conditionally independent given T,Z."
 : c.family==="common_cause"
 ? "T and Z are independent uniform signs. Analyst estimates Z with reliability "+p("a")+"; reviewer estimates T with reliability "+p("b")+". X estimates T*Z with reliability "+p("strong")+". Y is an exact copy of X, carrying no new evidence once X is known. Q estimates T with reliability "+p("aux")+". Distinct source noises are independent given T,Z."
 : "T is the current truth, Z is the change sign, and earlier truth is T*Z. T,Z are independent uniform signs. Analyst estimates earlier truth with reliability "+p("a")+"; reviewer estimates Z with reliability "+p("b")+". X estimates earlier truth with reliability "+p("strong")+", Y estimates current truth with reliability "+p("weak")+", Q estimates Z with reliability "+p("aux")+". Reports are conditionally independent given T,Z.";
 return rules+" Observer access: "+view+" (analyst sees analyst.initial; reviewer sees reviewer.initial; joint sees both; blind sees neither). Query registers are public, zero means unqueried. Each query costs "+c.cost+" utility, can be used once and consumes one action. A correct commitment pays 16, an incorrect one 0, settlement "+c.settle+", less incurred query cost. An unfinished horizon pays negative incurred cost. Choose a first action maximizing expected utility with optimal later decisions.";
}
const vr=(k,v)=>"VAR "+k+" = 0 | "+(v?"public":"hidden");
const en=(id,t,i,text,hi=t)=>"ENC "+id+" turn="+t+".."+hi+" | I:"+i+" | A:TRUE | Q:C(0) | N:"+q("Evidence council")+" | T:"+q(text);
const opt=(id,t,gate="TRUE")=>"OPT "+id+" | V:"+gate+" | P:TRUE | T:"+q(t);
const rx=(o,r,to,e="NONE",g="TRUE",d="C(1)")=>"ORX "+o+"/"+r+" -> "+to+" | E:"+e+" | D:"+d+" | G:"+g+" | T:"+q("The council records the result.");
export function compileSource(c,view,id){
 validate(c);if(!VIEWS.includes(view))fail("view");
 const pages=["decision0","decision1","decision2","correct","incorrect","settled"];
 const text=description(c,view),vars=[...Object.values(key).map(k=>vr(k,false)),
   vr(pub.a,view==="analyst"||view==="joint"),vr(pub.b,view==="reviewer"||view==="joint"),...QS.map(k=>vr(pub[k],true))];
 const lines=["# SWMD-SRG/2","id: "+id,"title: "+q("Adaptive evidence council"),"about: "+q("Observer-specific finite evidence model."),"start: decision0","turn-base: 0","tie: first","direct: strict",...vars,"SPOOL main | A:TRUE | E:"+pages.join(",")];
 for(let t=0;t<3;t++){
   lines.push(en("decision"+t,t,t,text));
   for(const [a,sign] of [["positive",1],["negative",-1]]){
     const o=a+"_"+t;lines.push(opt(o,"Commit "+a+"."),rx(o,"r_"+o+"_ok","correct","NONE","EQ("+P(key.t)+","+C(sign)+")"),rx(o,"r_"+o+"_bad","incorrect","NONE","TRUE","C(0)"));
   }
   lines.push(opt("settle_"+t,"Accept settlement."),rx("settle_"+t,"r_settle_"+t,"settled"));
   if(t<2)for(const k of QS){
     const o=k+"_"+t;lines.push(opt(o,"Query "+k.toUpperCase()+".","EQ("+P(pub[k])+",C(0))"),rx(o,"r_"+o,"decision"+(t+1),"SET "+pub[k]+" = "+P(key[k])));
   }
 }
 lines.push(en("correct",1,3,"Correct commitment.",3),en("incorrect",1,4,"Incorrect commitment.",3),en("settled",1,5,"Settlement.",3));
 return lines.join("\n")+"\n";
}
function initial(api,w,t){
 const s=api.initialV2(w);
 for(const k of Object.keys(key))s.values[key[k]]=t[k];
 s.values[pub.a]=t.a;s.values[pub.b]=t.b;return s;
}
const observe=(api,w,s)=>api.observeV2(w,s);
function semantic(a){return a.slice(0,a.lastIndexOf("_"));}
function payoff(c,s){
 if(s.encounter==="correct")return 16-(s.turn-1)*c.cost;
 if(s.encounter==="incorrect")return -(s.turn-1)*c.cost;
 if(s.encounter==="settled")return c.settle-(s.turn-1)*c.cost;
 return null;
}
// Exact weighted belief-state Bellman. Restrict queries to a predetermined
// order in fixed mode, while permitting observation-dependent early stopping.
function runtimeOracle(api,w,c,roots,h,fixed=null){
 let nodes=0;
 function step(rs,a,budget,order){
   const ns=rs.map(r=>({m:r.m,s:api.stepV2(w,r.s,a).next}));
   return sum(group(ns,r=>q(observe(api,w,r.s))),g=>rec(g,budget-1,order));
 }
 function scores(rs,h,order){
   const a=observe(api,w,rs[0].s).actions.map(a=>a.id);
   if(rs.some(r=>!same(observe(api,w,r.s).actions.map(a=>a.id),a)))fail("menu mismatch");
   const vals={};
   for(const id of a){
     const act=semantic(id),query=QS.includes(act);
     if(query&&(h<=1||(order!==null&&order[0]!==act)))continue;
     vals[id]=step(rs,id,h,query&&order!==null?order.slice(1):order);
   }
   return vals;
 }
 function rec(rs,h,order){
   nodes++;
   const term=rs.map(r=>payoff(c,r.s));
   if(term.every(x=>x!==null))return sum(rs,r=>r.m*payoff(c,r.s));
   if(term.some(x=>x!==null))fail("terminal mixed");
   if(!h)return sum(rs,r=>-r.m*r.s.turn*c.cost);
   return best(scores(rs,h,order)).value;
 }
 const cells=group(roots,r=>q(observe(api,w,r.s))).map(rs=>{
   const s=rs[0].s,o=observe(api,w,s),sc=scores(rs,h,fixed),b=best(sc);
   return {observation:o,mass:sum(rs,r=>r.m),positive_mass:sum(rs,r=>r.s.values[key.t]===1?r.m:0),scores:sc,...b};
 });
 return {numerator:sum(cells,c=>c.value),denominator:sum(cells,c=>c.mass),nodes,cells};
}
// Independent reference: no compiler, state transitions, AST, or runtime
// observations. Condition only on the selected tape fields.
function directReference(c,view,t,h,order=null){
 function recurse(rs,used,budget,seq){
   const n=sum(rs,x=>x.m),p=sum(rs,x=>x.t===1?x.m:0),cost=used.length*c.cost;
   const scores={positive:16*p-cost*n,negative:16*(n-p)-cost*n,settle:(c.settle-cost)*n};
   if(budget>1)for(const k of QS.filter(k=>!used.includes(k)&&(seq===null||seq[0]===k))){
     scores[k]=sum(group(rs,x=>x[k]),g=>recurse(g,[...used,k],budget-1,seq===null?null:seq.slice(1)).value);
   }
   return {scores,...best(scores)};
 }
 return group(t,x=>view==="analyst"?x.a:view==="reviewer"?x.b:view==="joint"?x.a+","+x.b:"blind").map(rs=>{
   const v=recurse(rs,[],h,order);return {key:[view==="analyst"||view==="joint"?rs[0].a:null,view==="reviewer"||view==="joint"?rs[0].b:null],mass:sum(rs,x=>x.m),...v};
 });
}
const ORDERS=QS.flatMap(a=>QS.filter(b=>b!==a).map(b=>[a,b]));
export function evaluateConfig(api,c,tag){
 const tapeset=tapes(c),out=[],tasks=[],gold=[],sources={},checks={root_cells:0,fixed_policy_cells:0,observer_leak_checks:0,copy_zero_information_checks:0};
 for(const view of VIEWS){
   const id="sw_"+tag+"_"+view,src=compileSource(c,view,id),w=api.compileV2(src);
   sources[view]=src;const roots=tapeset.map(t=>({m:t.m,s:initial(api,w,t)}));
   for(const r of roots){
     const o=observe(api,w,r.s),expected=[pub.x,pub.y,pub.q,...(view==="analyst"||view==="joint"?[pub.a]:[]),...(view==="reviewer"||view==="joint"?[pub.b]:[])].sort();
     if(!same(Object.keys(o.values).sort(),expected))fail("observer leak");
     checks.observer_leak_checks++;
     if(c.family==="common_cause"){
       const x=api.stepV2(w,r.s,"x_0").next,y=api.stepV2(w,x,"y_1").next;
       if(x.values[pub.x]!==y.values[pub.y])fail("copy mismatch");
       checks.copy_zero_information_checks++;
     }
   }
   for(const h of [1,2,3]){
     const r=runtimeOracle(api,w,c,roots,h),ref=directReference(c,view,tapeset,h);
     function crosscheck(a,b){
       for(const cell of a.cells){
         const v=cell.observation.values,match=b.find(x=>same(x.key,[v[pub.a]??null,v[pub.b]??null]));
         const scores=Object.fromEntries(Object.entries(cell.scores).map(([id,n])=>[semantic(id),n]));
         if(!match||cell.mass!==match.mass||cell.value!==match.value||!same(scores,match.scores))fail("independent oracle mismatch "+id+"/"+h);
       }
       if(a.cells.length!==b.length)fail("cell count");
     }
     crosscheck(r,ref);checks.root_cells+=r.cells.length;
     let fixed=-Infinity,fixedOrder=null;
     // H=1 requires no queries; one representative order suffices.
     for(const order of h===1?[ORDERS[0]]:ORDERS){
       const f=runtimeOracle(api,w,c,roots,h,order),ref=directReference(c,view,tapeset,h,order);
       crosscheck(f,ref);checks.fixed_policy_cells+=f.cells.length;
       if(f.numerator>fixed){fixed=f.numerator;fixedOrder=order;}
     }
     if(r.numerator<fixed)fail("adaptive below fixed");
     out.push({family:c.family,tag,view,h,numerator:r.numerator,denominator:r.denominator,fixed_numerator:fixed,fixed_order:fixedOrder,adaptive_gain_numerator:r.numerator-fixed,nodes:r.nodes,
       cells:r.cells.map(cell=>({initial:[cell.observation.values[pub.a]??null,cell.observation.values[pub.b]??null],mass:cell.mass,positive_mass:cell.positive_mass,scores:cell.scores,winners:cell.winners}))});
     r.cells.forEach((cell,i)=>{
       const id=w.id+"_h"+h+"_c"+i;
       // Runtime observes a wider menu at shortened horizons. Query with
       // no remaining commitment turn is scored as unfinished negative cost.
       const scores={...cell.scores};
       for(const a of cell.observation.actions)if(!own(scores,a.id))scores[a.id]=-cell.mass*c.cost;
       tasks.push({id,world_id:w.id,kind:"adaptive_evidence",action_budget:h,observation:cell.observation,output_contract:"Return one legal action ID maximizing expected utility within the budget."});
       gold.push({id,family:c.family,view,h,mass:cell.mass,actions:cell.winners,scores});
     });
   }
 }
 return {out,tasks,gold,sources,checks};
}
function rng(seed){if(!Number.isSafeInteger(seed)||seed<1||seed>0xffffffff)fail("seed");let x=seed;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};}
export function configsFor(split,seed,replicates){
 if(!["calibration_public","evaluation_private"].includes(split)||!Number.isInteger(replicates)||replicates<1||replicates>8)fail("suite config");
 const r=rng(seed),out=[];
 for(let j=0;j<replicates;j++)for(const family of FAMILIES){
   const c=split==="calibration_public"&&j===0?{...CONFIGS.find(c=>c.family===family)}:
   {family,a:5+r()%4,b:5+r()%3,strong:6+r()%3,weak:4+r()%3,aux:5+r()%4,cost:1+r()%2,settle:8+r()%3};
   out.push({c,tag:"case_"+j+"_"+family+"_"+r().toString(16)});
 }
 return out;
}
export function runSuite({split="calibration_public",seed=0x53521001,replicates=1,api=runtime}={}){
 const configs=configsFor(split,seed,replicates),results=[],tasks=[],gold=[],sources={},checks={root_cells:0,fixed_policy_cells:0,observer_leak_checks:0,copy_zero_information_checks:0};
 for(const {c,tag} of configs){
   const r=evaluateConfig(api,c,tag);
   results.push(...r.out);tasks.push(...r.tasks);gold.push(...r.gold);sources[tag]=r.sources;
   for(const k of Object.keys(checks))checks[k]+=r.checks[k];
 }
 // Adding initial observations or budget cannot reduce optimal value.
 for(const {tag} of configs)for(const h of [1,2,3]){
   const find=(v,t=h)=>results.find(x=>x.tag===tag&&x.view===v&&x.h===t);
   if(find("joint").numerator<Math.max(find("analyst").numerator,find("reviewer").numerator)||Math.min(find("analyst").numerator,find("reviewer").numerator)<find("blind").numerator)fail("access monotonicity");
   if(h>1)for(const v of VIEWS)if(find(v).numerator<find(v,h-1).numerator)fail("budget monotonicity");
 }
 return {receipt:{evidence:"exact weighted finite SWMD/reference adaptive and fixed-order oracle; no model inference",split,seed,replicates,configs,checks,results,task_rows:tasks.length},tasks,gold,sources};
}
