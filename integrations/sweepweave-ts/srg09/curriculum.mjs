// SRG-09: exact weighted belief oracle and observer-owned interaction margins.
// Finite deterministic tapes encode noise; the player never sees the tapes.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
import {evaluate as evalExpr} from '../srg04/swmd-runtime.mjs';

const C=x=>"C("+x+")",P=k=>"P("+k+")",op=(n,a)=>n+"("+a.join(",")+")",q=JSON.stringify;
const fail=m=>{throw Error("SRG09: "+m);};
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const own=(o,k)=>Object.hasOwn(o,k);
const V=(k,v=0,visibility="hidden")=>"VAR "+k+" = "+v+" | "+visibility;
const enc=(id,t,i,text,hi=t)=>"ENC "+id+" turn="+t+".."+hi+" | I:"+i+" | A:TRUE | Q:C(0) | N:"+q("Council record")+" | T:"+q(text);
const opt=(id,text)=>"OPT "+id+" | V:TRUE | P:TRUE | T:"+q(text);
const rx=(o,id,to,e="NONE",g="TRUE",d="C(1)",text="Record updated.")=>"ORX "+o+"/"+id+" -> "+to+" | E:"+e+" | D:"+d+" | G:"+g+" | T:"+q(text);
const set=(k,e)=>"SET "+k+" = "+e;
const header=(id,vars,start,pages)=>["# SWMD-SRG/2","id: "+id,"title: "+q("Council evidence ledger"),"about: "+q("Finite evidence and belief experiment."),"start: "+start,"turn-base: 0","tie: first","direct: strict",...vars,"SPOOL main | A:TRUE | E:"+pages.join(",")];
const source=lines=>lines.join("\n")+"\n";
function root(api,w,values){const s=api.initialV2(w);for(const [k,v] of Object.entries(values)){if(!own(s.values,k))fail("unknown root coordinate "+k);s.values[k]=v;}return s;}
function groups(rows,key){const out=new Map();for(const row of rows){const k=key(row);if(!out.has(k))out.set(k,[]);out.get(k).push(row);}return [...out.values()];}
const sum=(rows,f)=>rows.reduce((n,x)=>n+f(x),0);
const obsKey=(api,w,s)=>JSON.stringify(api.observeV2(w,s));
function best(scores){const v=Math.max(...Object.values(scores));return {value:v,actions:Object.keys(scores).filter(k=>scores[k]===v)};}
const SIGNS=[-1,1];

export const KEYS=Object.freeze({
 truth:"council.regime",type:"bob.stance",
 a:"analyst.claim[alice]",b:"analyst.claim[bob]",c:"analyst.repeat[bob]",
 meta:"analyst.stance[reviewer][bob]",
 wrong_owner:"observer.stance[reviewer][bob]",wrong_depth:"analyst.stance[bob]",
 A:"analyst.A",B:"analyst.B",D:"analyst.D",M:"analyst.M",audit:"analyst.audit"
});
const k=KEYS;

// Equal prior over truth and source type. Conditional weights are integers
// out of 8. In shared mode the second report is a perfect copy, rather than
// conditionally independent. All positive-weight roots share a denominator.
export function tape(mode){
 if(!["independent","copy"].includes(mode))fail("bad tape mode");
 const out=[];
 for(const truth of SIGNS)for(const type of SIGNS)
 for(const a of SIGNS)for(const b of SIGNS)for(const c of SIGNS)for(const m of SIGNS){
   const aw=a===truth?6:2,bw=b===truth*type?7:1,cw=mode==="copy"?(c===b?8:0):(c===truth*type?7:1),mw=m===type?7:1;
   const mass=aw*bw*cw*mw;
   if(mass)out.push({truth,type,a,b,c,m,mass,values:{[k.truth]:truth,[k.type]:type,[k.a]:a,[k.b]:b,[k.c]:c,[k.meta]:m,[k.wrong_owner]:-m,[k.wrong_depth]:-m}});
 }
 if(sum(out,x=>x.mass)!==16384)fail("prior mass");
 return out;
}
function evidenceWorld(mode,metaMode="correct"){
 if(!["correct","wrong_owner","wrong_depth","missing"].includes(metaMode))fail("meta mode");
 const id="council_"+mode+"_"+metaMode,read=["opening","read_a","read_b","read_c","decision"],ends=["win","loss","settled","audited_win","audited_loss"];
 const vars=[...Object.values(k).slice(0,8).map(x=>V(x)),...Object.values(k).slice(8).map(x=>V(x,0,"public"))];
 const pred=op("GT",[P(k.truth),C(0)]),neg=op("LT",[P(k.truth),C(0)]);
 const text="Truth and Bob's reporting stance are independently uniform signs. Alice matches truth with probability 3/4. Bob matches truth times stance with probability 7/8. "+(mode==="copy"?"The repeated Bob report is a perfect copy, not new evidence.":"Bob's two reports are conditionally independent given truth and stance.")+" The reviewer sign matches Bob's stance with probability 7/8. Reports and reviewer noise are otherwise conditionally independent. "+(metaMode==="missing"?"Reviewer sign unavailable (0).":metaMode==="correct"?"M is the reviewer's report.":"M is an inverted reviewer report due to the declared source substitution.")+" A correct direct decision pays 8, an incorrect one 0, settlement pays 5. Exact audit and correct commitment pays 6 in two actions; an unfinished audit pays 0.";
 const lines=header(id,vars,"opening",[...read,"audited",...ends]);
 const transfers=[[k.A,k.a],[k.B,k.b],[k.D,k.c],[k.M,metaMode==="correct"?k.meta:metaMode==="wrong_owner"?k.wrong_owner:metaMode==="wrong_depth"?k.wrong_depth:null]];
 for(let i=0;i<4;i++){
   const [dest,src]=transfers[i],a="read_"+i;
   lines.push(enc(read[i],i,i,text),opt(a,"Read the next evidence field."),rx(a,"receipt_"+i,read[i+1],set(dest,src?P(src):C(0))));
 }
 lines.push(enc("decision",4,4,text),
   opt("positive","Commit positive."),rx("pwin","invalid","win")); // replace temporary sentinel below
 lines.splice(lines.length-1,1,
   rx("positive","pwin","win","NONE",pred),rx("positive","ploss","loss","NONE","TRUE","C(0)"),
   opt("negative","Commit negative."),rx("negative","nwin","win","NONE",neg),rx("negative","nloss","loss","NONE","TRUE","C(0)"),
   opt("settle","Accept settlement."),rx("settle","swin","settled"),
   opt("audit","Audit truth exactly."),rx("audit","audit_receipt","audited",set(k.audit,P(k.truth))),
   enc("audited",5,5,"The audit reveals the true regime in analyst.audit. Choose the matching sign."),
   opt("final_positive","Commit positive after audit."),rx("final_positive","apwin","audited_win","NONE",pred),rx("final_positive","aploss","audited_loss","NONE","TRUE","C(0)"),
   opt("final_negative","Commit negative after audit."),rx("final_negative","anwin","audited_win","NONE",neg),rx("final_negative","anloss","audited_loss","NONE","TRUE","C(0)"),
   enc("win",5,6,"Direct correct."),enc("loss",5,7,"Direct incorrect."),enc("settled",5,8,"Settlement."),
   enc("audited_win",6,9,"Audit correct."),enc("audited_loss",6,10,"Audit incorrect."));
 return {source:source(lines),payoff:{win:8,loss:0,settled:5,audited_win:6,audited_loss:0}};
}
function reveal(api,w,row){
 let s=root(api,w,row.values);
 for(let i=0;i<4;i++){const o=api.observeV2(w,s);if(o.actions.length!==1)fail("unforced reveal");s=api.stepV2(w,s,o.actions[0].id).next;}
 const o=api.observeV2(w,s);
 if(Object.keys(o.values).sort().join(",")!==[k.A,k.B,k.D,k.M,k.audit].sort().join(",")||o.values[k.audit]!==0)fail("belief/tape leakage");
 return s;
}
function oracle(api,w,rows,payoff,h){
 let nodes=0;
 function rec(rs,budget){
   nodes++;
   if(rs.every(x=>own(payoff,x.s.encounter))||budget===0)return sum(rs,x=>x.mass*(payoff[x.s.encounter]??0));
   if(rs.some(x=>own(payoff,x.s.encounter)))fail("mixed terminal cell");
   const menus=rs.map(x=>api.observeV2(w,x.s).actions.map(a=>a.id));
   if(!menus.every(m=>same(m,menus[0])))fail("unequal menu");
   return best(Object.fromEntries(menus[0].map(a=>[a,advance(rs,a,budget)]))).value;
 }
 function advance(rs,a,budget){
   const ns=rs.map(x=>({mass:x.mass,s:api.stepV2(w,x.s,a).next}));
   return sum(groups(ns,x=>obsKey(api,w,x.s)),g=>rec(g,budget-1));
 }
 const cells=groups(rows,x=>obsKey(api,w,x.s)).map(g=>{
   const observation=api.observeV2(w,g[0].s),scores=Object.fromEntries(observation.actions.map(a=>[a.id,advance(g,a.id,h)]));
   const mass=sum(g,x=>x.mass),pos=sum(g,x=>x.s.values[k.truth]===1?x.mass:0);
   return {observation,mass,positive_mass:pos,scores,...best(scores)};
 });
 return {numerator:sum(cells,c=>c.value),denominator:sum(cells,c=>c.mass),nodes,cells};
}
function likelihoodTable(mode,metaMode){
 const out={};
 for(const r of tape(mode)){
   const m=metaMode==="missing"?0:metaMode==="correct"?r.m:-r.m;
   const key=[r.a,r.b,r.c,m].join(",");
   const c=out[key]??={mass:0,positive:0};c.mass+=r.mass;if(r.truth===1)c.positive+=r.mass;
 }
 return out;
}
function formulaScores(mass,pos,h){return {positive:8*pos,negative:8*(mass-pos),settle:5*mass,audit:h>=2?6*mass:0};}
function actionValue(cell,act){return cell.scores[act];}
function obsTuple(o){return [o.values[k.A],o.values[k.B],o.values[k.D],o.values[k.M]];}
function fromTable(table,t,h){
 const row=table[t.join(",")];if(!row)fail("uncovered likelihood cell");
 return best(formulaScores(row.mass,row.positive,h)).actions[0];
}
function quantizeCells(cells,h,bits){
 // Nested fixed dyadic bins over signed posterior margin [-1,1].
 // Group using integer arithmetic, preserving weighted mass.
 const n=2**bits,group={};
 for(const c of cells){
   const bin=Math.min(n-1,Math.floor(n*c.positive_mass/c.mass)),g=group[bin]??={mass:0,scores:{positive:0,negative:0,settle:0,audit:0}};
   g.mass+=c.mass;for(const a of Object.keys(g.scores))g.scores[a]+=c.scores[a];
 }
 return {bits,cells:Object.keys(group).length,numerator:sum(Object.values(group),g=>best(g.scores).value)};
}
function evidenceRun(api,mode,metaMode){
 const {source:src,payoff}=evidenceWorld(mode,metaMode),w=api.compileV2(src),rows=tape(mode).map(x=>({mass:x.mass,s:reveal(api,w,x)}));
 const prior=likelihoodTable(mode,metaMode),ideal=likelihoodTable(mode,"correct"),wrongCopy=likelihoodTable("independent","correct");
 const results=[],tasks=[],gold=[];
 for(const h of [1,2]){
   const r=oracle(api,w,rows,payoff,h);
   if(r.denominator!==16384)fail("bad oracle denominator");
   let independent=0,ignoreMeta=0,naive=0,wrongOwner=0,conflictMass=0,conflictCells=0,conflictOpt=0;
   const ablated=likelihoodTable(mode,"missing"),counts={};
   for(let i=0;i<r.cells.length;i++){
     const cell=r.cells[i],t=obsTuple(cell.observation),p=prior[t.join(",")];
     if(!p||p.mass!==cell.mass||p.positive!==cell.positive_mass||!same(formulaScores(p.mass,p.positive,h),cell.scores))fail("posterior/runtime oracle disagreement");
     const select=(tab,tuple)=>fromTable(tab,tuple,h);
     const corrected=[t[0],t[1],t[2],metaMode==="missing"?0:metaMode==="correct"?t[3]:-t[3]];
     independent+=actionValue(cell,select(metaMode==="missing"?likelihoodTable("independent","missing"):wrongCopy,corrected));
     ignoreMeta+=actionValue(cell,select(ablated,[t[0],t[1],t[2],0]));
     naive+=actionValue(cell,t[0]+t[1]+t[2]>0?"positive":"negative");
     if(metaMode==="correct")wrongOwner+=actionValue(cell,select(ideal,[t[0],t[1],t[2],-t[3]]));
     if(t[0]!==t[1]||t[1]!==t[2]){conflictMass+=cell.mass;conflictCells++;conflictOpt+=cell.value;}
     const winners=cell.actions.join("+");counts[winners]=(counts[winners]??0)+cell.mass;
     const id=w.id+"_h"+h+"_cell"+i;
     tasks.push({id,world_id:w.id,kind:"evidence",action_budget:h,observation:cell.observation,output_contract:"Return the legal action ID that maximizes expected utility. Use the declared joint evidence model."});
     gold.push({id,mode,meta_mode:metaMode,budget:h,mass:cell.mass,positive_mass:cell.positive_mass,actions:cell.actions,scores:cell.scores});
   }
   const precision=Array.from({length:7},(_,b)=>quantizeCells(r.cells,h,b));
   for(let i=1;i<precision.length;i++)if(precision[i].numerator<precision[i-1].numerator)fail("nonmonotone nested partition");
   if(precision.some(p=>p.numerator>r.numerator))fail("partition exceeds oracle");
   if([independent,ignoreMeta,naive,wrongOwner].some(v=>v>r.numerator))fail("baseline exceeds oracle");
   results.push({mode,meta_mode:metaMode,budget:h,numerator:r.numerator,denominator:r.denominator,cells:r.cells.length,nodes:r.nodes,
     policy_mass:counts,naive_majority_numerator:naive,independence_assumption_numerator:independent,ignore_meta_numerator:ignoreMeta,wrong_owner_as_if_correct_numerator:metaMode==="correct"?wrongOwner:null,
     conflict_mass:conflictMass,conflict_cells:conflictCells,conflict_optimum_numerator:conflictOpt,posterior_precision:precision});
 }
 // Changing an unrelated owner/depth coordinate must be inert in the correct
 // source; changing the selected source is checked separately below.
 let ownershipControls=0;
 if(metaMode==="correct")for(const row of tape(mode)){
   const a=reveal(api,w,row);
   for(const key of [k.wrong_owner,k.wrong_depth]){
     const b=reveal(api,w,{...row,values:{...row.values,[key]:-row.values[key]}});
     if(obsKey(api,w,a)!==obsKey(api,w,b))fail("unrelated owner intervention leaked");
     ownershipControls++;
   }
 }
 return {source:src,results,tasks,gold,ownershipControls,roots:rows.length};
}

function rng(seed){if(!Number.isSafeInteger(seed)||seed<1||seed>0xffffffff)fail("seed");let x=seed;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};}
function interactionFixture(K){
 const n=K/2,p=Array.from({length:n},(_,i)=>"analyst.p"+i+"[source]"),r=Array.from({length:n},(_,i)=>"analyst.r"+i+"[reviewer][source]"),wrong=r.map(x=>x.replace("analyst.","observer."));
 const common="analyst.common",goal="analyst.goal";
 const terms=p.map((key,i)=>op("MUL",[C(i%2?-1:1),P(key),P(r[i])]));
 const contrast=op("ADD",[...terms,...p.map(key=>op("MUL",[C(.25),P(key)]))]);
 const plus=op("ADD",[P(common),op("MUL",[C(.5),contrast])]);
 const minus=op("ADD",[P(common),op("MUL",[C(-.5),contrast])]);
 const lines=header("interaction_"+K,[...p.map(x=>V(x)),...r.map(x=>V(x)),...wrong.map(x=>V(x)),V(common),V(goal)],"decision",["decision","positive","negative"]);
 lines.push(enc("decision",0,0,"The signed score contrast is a sum of observer-owned pairwise interactions and linear terms."),
   opt("act","Request a ruling."),rx("act","rp","positive",set(goal,C(.25)),"TRUE",plus),rx("act","rn","negative",set(goal,C(-.25)),"TRUE",minus),enc("positive",1,1,"Positive."),enc("negative",1,2,"Negative."));
 return {K,p,r,wrong,common,goal,source:source(lines)};
}
function interactionRun(api,evaluate,K,seed){
 const f=interactionFixture(K),w=api.compileV2(f.source),r=rng(seed),n=K/2,levels=[-.875,-.625,-.375,-.125,.125,.375,.625,.875];
 const reference=(x,y)=>sum(x,(u)=>.25*u)+sum(x,(u,i)=>0); // separate independent loop below
 function contrast(x,y){let v=0;for(let i=0;i<n;i++)v+=(i%2?-1:1)*x[i]*y[i]+.25*x[i];return v;}
 const classify=d=>d>=0;
 const stats={K,seed,probes:512,exact_runtime:0,common_mode_invariant:0,unrelated_owner_invariant:0,wrong_owner_formula_flips:0,linear_only_flips:0,precision:[]};
 const rows=[];
 for(let j=0;j<stats.probes;j++){
   const x=f.p.map(()=>levels[r()%levels.length]),y=f.r.map(()=>levels[r()%levels.length]),c=levels[r()%levels.length];
   const values={...Object.fromEntries(f.p.map((key,i)=>[key,x[i]])),...Object.fromEntries(f.r.map((key,i)=>[key,y[i]])),...Object.fromEntries(f.wrong.map((key,i)=>[key,-y[i]])),[f.common]:c};
   const s=root(api,w,values),a=api.stepV2(w,s,"act"),d=contrast(x,y),want=classify(d)?"positive":"negative";
   if(a.next.encounter!==want||a.squared_step_energy!==.0625)fail("interaction runtime");
   stats.exact_runtime++;
   const c2=root(api,w,{...values,[f.common]:-c});
   if(api.stepV2(w,c2,"act").next.encounter!==want)fail("common mode");
   stats.common_mode_invariant++;
   const o2=root(api,w,{...values,...Object.fromEntries(f.wrong.map((key,i)=>[key,y[i]]))});
   if(api.stepV2(w,o2,"act").next.encounter!==want)fail("owner isolation");
   stats.unrelated_owner_invariant++;
   stats.wrong_owner_formula_flips+=Number(classify(contrast(x,y.map(v=>-v)))!==classify(d));
   stats.linear_only_flips+=Number(classify(sum(x,v=>.25*v))!==classify(d));
   rows.push({x,y,d});
 }
 for(const bits of [1,2,3,4,5]){
   const bins=2**bits,eps=1/bins;
   const quant=v=>-1+(Math.min(bins-1,Math.floor((v+1)*bins/2))+.5)*2/bins;
   let flips=0,certified=0,violations=0,maxError=0,uncertifiedFlips=0;
   for(const row of rows){
     const x=row.x.map(quant),y=row.y.map(quant),d=contrast(x,y),error=Math.abs(d-row.d);
     const bound=sum(row.x,(v)=>Math.abs(v)*eps+.25*eps)+sum(row.y,v=>Math.abs(v)*eps)+n*eps*eps;
     const safe=Math.abs(row.d)>bound;
     const flip=classify(d)!==classify(row.d);
     if(error>bound+1e-12||safe&&flip)violations++;
     flips+=Number(flip);certified+=Number(safe);uncertifiedFlips+=Number(flip&&!safe);maxError=Math.max(maxError,error);
   }
   if(violations)fail("margin bound violated");
   stats.precision.push({bits,flips,certified,violations,uncertified_flips:uncertifiedFlips,max_error:maxError});
 }
 return {stats,source:f.source};
}
export function runSuite({api=runtime,evaluate=evalExpr,seed=0x53520901}={}){
 const evidence=[],tasks=[],gold=[],sources={},ownership={controls:0,roots:0};
 for(const mode of ["independent","copy"])for(const metaMode of ["correct","wrong_owner","wrong_depth","missing"]){
   const e=evidenceRun(api,mode,metaMode);
   evidence.push(...e.results);tasks.push(...e.tasks);gold.push(...e.gold);sources[mode+"_"+metaMode]=e.source;
   ownership.controls+=e.ownershipControls;ownership.roots+=e.roots;
 }
 for(const mode of ["independent","copy"])for(const h of [1,2]){
   const get=m=>evidence.find(r=>r.mode===mode&&r.meta_mode===m&&r.budget===h);
   if(get("correct").numerator!==get("wrong_owner").numerator||get("correct").numerator!==get("wrong_depth").numerator||get("missing").numerator>get("correct").numerator)fail("ownership relabel or missing-info bound");
 }
 const interactions=[4,8,16].map(K=>interactionRun(api,evaluate,K,seed^K));
 for(const i of interactions)sources["interaction_"+i.stats.K]=i.source;
 return {receipt:{evidence:"finite exact integer mass belief oracle; binary64 dyadic margin controls; no model calls",seed,evidence_worlds:8,evidence,ownership,interactions:interactions.map(x=>x.stats),task_rows:tasks.length},tasks,gold,sources};
}
