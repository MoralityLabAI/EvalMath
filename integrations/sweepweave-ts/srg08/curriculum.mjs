// SRG-08: formula synthesis, temporal cue memory and belief-dependent planning.
import * as runtime from '../srg05/swmd-runtime-v2.mjs';
import {evaluate as evalExpr} from '../srg04/swmd-runtime.mjs';
export const SPLITS=Object.freeze({train_public:"linear",calibration_public:"metric",evaluation_private:"interaction"});
const K=[4,8,16], H=[2,3,5];
const C=x=>"C("+x+")",P=x=>"P("+x+")",op=(n,a)=>n+"("+a.join(",")+")",q=JSON.stringify;
const fail=m=>{throw Error("SRG08: "+m);};
const own=(x,k)=>Object.hasOwn(x,k);
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function rng(seed){if(!Number.isInteger(seed)||seed<1||seed>0xffffffff)fail("nonzero uint32 seed");let x=seed;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return x>>>0;};}
function identity(r){let n=0;return p=>p+"_"+(++n)+"_"+r().toString(16).padStart(8,"0");}
function varline(k,v=0,visible="hidden"){return "VAR "+k+" = "+v+" | "+visible;}
function header(id,vars,start,pages){return ["# SWMD-SRG/2","id: "+id,"title: "+q("Council dossier "+id),"about: "+q("A bounded civic reasoning exercise."),"start: "+start,"turn-base: 0","tie: first","direct: strict",...vars,"SPOOL main | A:TRUE | E:"+pages.join(",")];}
function enc(id,t,i,text,hi=t){return "ENC "+id+" turn="+t+".."+hi+" | I:"+i+" | A:TRUE | Q:C(0) | N:"+q("Ledger")+" | T:"+q(text);}
function opt(id,t){return "OPT "+id+" | V:TRUE | P:TRUE | T:"+q(t);}
function rx(o,id,to,e="NONE",g="TRUE",d="C(1)",t="The record advances."){return "ORX "+o+"/"+id+" -> "+to+" | E:"+e+" | D:"+d+" | G:"+g+" | T:"+q(t);}
function set(k,x){return "SET "+k+" = "+x;}
function src(lines){return lines.join("\n")+"\n";}
function randomSigns(k,r){return Array.from({length:k},()=>r()&1?1:-1);}
function state(api,w,values){const s=api.initialV2(w);for(const [k,v] of Object.entries(values)){if(!own(s.values,k))fail("undeclared root");s.values[k]=v;}return s;}
function observe(api,w,s){return api.observeV2(w,s);}
function rootKey(o){return JSON.stringify(o);}
function splitBy(xs,key){const m=new Map();for(const x of xs){const k=key(x);if(!m.has(k))m.set(k,[]);m.get(k).push(x);}return [...m.values()];}

// Synthetic synthesis tasks. There is no reference or complementary formula
// in the editable source. The only classification gate is the FALSE hole.
function synthesis(f,k,r,make){
 const id=make("sw"),keys=Array.from({length:k},()=> "ledger."+make("v")),signs=randomSigns(k,r);
 const start=make("page"),yes=make("page"),no=make("page"),act=make("act"),target=make("rx"),fallback=make("rx");
 let gate,rule,reference;
 if(f==="linear"){
   const weights=signs.map((s,i)=>s*(i%2?1:2)),threshold=(r()%3-1)*.25;
   gate=op("GE",[op("ADD",keys.map((x,i)=>op("MUL",[C(weights[i]),P(x)]))),C(threshold)]);
   rule="Classify positive iff the weighted sum "+keys.map((x,i)=>weights[i]+"*"+x).join(" + ")+" is >= "+threshold+". Equality is positive.";
   reference=x=>x.reduce((a,v,i)=>a+weights[i]*v,0)>=threshold;
 }else if(f==="metric"){
   const centers=signs.map(s=>s*.25),radius=k*.25;
   const ds=keys.map((x,i)=>op("SUB",[P(x),C(centers[i])]));
   gate=op("LE",[op("ADD",ds.map(t=>op("MUL",[t,t]))),C(radius)]);
   rule="Classify positive iff squared Euclidean distance from the center ("+keys.map((x,i)=>x+"="+centers[i]).join(", ")+") is <= "+radius+". Equality is positive. Square each coordinate residual before summing.";
   reference=x=>x.reduce((a,v,i)=>a+(v-centers[i])**2,0)<=radius;
 }else if(f==="interaction"){
   const pairs=Array.from({length:k/2},(_,i)=>[2*i,2*i+1,signs[i]]);
   const terms=pairs.map(([i,j,s])=>op("MUL",[C(s),P(keys[i]),P(keys[j])]));
   gate=op("GE",[op("ADD",terms),C(0)]);
   rule="Classify positive iff "+pairs.map(([i,j,s])=>s+"*"+keys[i]+"*"+keys[j]).join(" + ")+" is >= 0. Equality is positive.";
   reference=x=>pairs.reduce((a,[i,j,s])=>a+s*x[i]*x[j],0)>=0;
 }else fail("unknown synthesis family");
 const lines=[...header(id,keys.map(k=>varline(k)),start,[start,yes,no]),enc(start,0,0,rule),opt(act,"Classify the ledger."),
   rx(act,target,yes,"NONE","FALSE","C(1)","Positive classification."),rx(act,fallback,no,"NONE","TRUE","C(0)","Negative classification."),
   enc(yes,1,1,"Positive result."),enc(no,1,2,"Negative result.")];
 const source=src(lines),line=lines.findIndex(s=>s.startsWith("ORX "+act+"/"+target))+1;
 const before=lines[line-1],after=before.replace(" | G:FALSE |"," | G:"+gate+" |");
 const binary=m=>keys.map((_,j)=>m>>>j&1?.5:-.5),n=2**k;
 const truth=Array.from({length:n},(_,m)=>reference(binary(m))),witness=[];
 for(let j=0;j<k;j++){
   let first=-1;for(let m=0;m<n;m++)if(!(m>>>j&1)&&truth[m]!==truth[m^(1<<j)]){first=m;break;}
   if(first<0)fail("synthesis inactive key "+f+"/"+k+"/"+j);
   witness.push(first,first^(1<<j));
 }
 const values=[-.75,-.5,-.25,0,.25,.5,.75],probes=[];
 // independently sampled multilevel inputs, plus one-coordinate witnesses
 // and exact zero/center boundary probes. Public examples are disjoint indices.
 for(let i=0;i<64;i++)probes.push(keys.map(()=>values[r()%values.length]));
 probes.push(...[...new Set(witness)].map(binary),keys.map(()=>0));
 const examples=probes.splice(0,6).map(x=>({inputs:Object.fromEntries(keys.map((key,j)=>[key,x[j]])),positive:reference(x)}));
 const task={id,kind:"synthesis",source,intent:rule,allowed_edit:{reaction_id:target,field:"G",line,before},examples,output_contract:"Return one boolean SWMD expression for G; allowed operators C, P, ADD, SUB, MUL, DIV, ABS, MIN, MAX, GE, GT, LE, LT, EQ, NE, AND, OR, NOT, IF. Do not alter other records."};
 return {task,id,f,k,keys,act,target,yes,no,gate,line,before,after,reference,binary,truth,probes,witness};
}
function installGate(api,c,expr){
 if(typeof expr!=="string"||!expr.trim()||expr.length>16000||/[\r\n|;]/.test(expr)||/\b(SEEN|ACTIVE)\s*\(|__srg\./.test(expr))fail("invalid formula scope");
 const after=c.before.replace(" | G:FALSE |"," | G:"+expr+" |");
 if(after===c.before)fail("no formula inserted");
 const source=api.applyLinePatch(c.task.source,{line:c.line,before:c.before,after});
 const w=api.compileV2(source),g=w.pages[w.start].options[c.act].reactions.find(x=>x.id===c.target).gate;
 return {w,g};
}
export function scoreFormula(api,evaluate,c,expr,exhaustive=true){
 const {w,g}=installGate(api,c,expr);
 let grid=0,binary=0,runtime=0,errors=0;
 const toValues=x=>Object.fromEntries(c.keys.map((k,j)=>[k,x[j]]));
 for(const x of c.probes){
   try{
     const v=toValues(x),y=c.reference(x),a=evaluate(g,v);
     grid+=Number(a===y);
     const b=api.stepV2(w,state(api,w,v),c.act);runtime+=Number(b.next.encounter===(y?c.yes:c.no));
   }catch{errors++;}
 }
 if(exhaustive)for(let m=0;m<c.truth.length;m++){
   try{binary+=Number(evaluate(g,toValues(c.binary(m)))===c.truth[m]);}catch{errors++;}
 }
 return {grid,grid_total:c.probes.length,runtime,runtime_total:c.probes.length,binary,binary_total:exhaustive?c.truth.length:0,errors};
}

// Temporal cue register. The static hidden input vector is only revealed one
// cue per forced step; the final report clears the public cue register.
function memory(f,k,r,make){
 const id=make("sw"),keys=Array.from({length:k},()=> "ledger."+make("v")),cue="ledger.cue",index="ledger.query",hiddenIndex="ledger.hidden_query";
 const pages=Array.from({length:k+1},()=>make("page")),yes=make("page"),no=make("page"),a=make("act"),b=make("act");
 const taskRule=f==="parity"?"Report true iff the number of positive cues was odd.":"At the final report, query*"+k+" specifies the one-based cue number. Report true iff that earlier cue was positive.";
 const vars=[...keys.map(k=>varline(k)),varline(cue,0,"public"),varline(index,0,"public"),varline(hiddenIndex)];
 const lines=header(id,vars,pages[0],[...pages,yes,no]);
 for(let t=0;t<k;t++){
   const act=make("act");
   lines.push(enc(pages[t],t,t,t===0?"Begin reading the ordered cues. "+taskRule:"The cue register displays cue "+t+"."),
     opt(act,"Read the next cue."),rx(act,make("rx"),pages[t+1],set(cue,P(keys[t]))));
 }
 // Report stage still has cue K until the clear action. Add a separate
 // forced clear transition so CURRENT observation contains no cue bit.
 const report=make("page"),clear=make("act");
 lines[lines.findIndex(x=>x.startsWith("SPOOL "))]+=","+report;
 lines.push(enc(pages[k],k,k,"The cue register displays cue "+k+"."),
   opt(clear,"Archive the cue register."),rx(clear,make("rx"),report,set(cue,C(0))+"; "+set(index,P(hiddenIndex))));
 const pred=f==="parity"?op("LT",[op("MUL",keys.map(P)),C(0)]):
   op("OR",keys.map((key,i)=>op("AND",[op("EQ",[P(index),C((i+1)/k)]),op("GT",[P(key),C(0)])])));
 lines.push(enc(report,k+1,k+1,taskRule),
   opt(a,"Report true."),rx(a,make("rx"),yes,"NONE",pred),rx(a,make("rx"),no,"NONE","TRUE","C(0)"),
   opt(b,"Report false."),rx(b,make("rx"),yes,"NONE",op("NOT",[pred])),rx(b,make("rx"),no,"NONE","TRUE","C(0)"),
   enc(yes,k+2,k+2,"Correct report."),enc(no,k+2,k+3,"Incorrect report."));
 return {id,f,k,keys,cue,index,hiddenIndex,report,a,b,yes,no,source:src(lines),taskRule};
}
function memoryRows(api,c,r){
 const w=api.compileV2(c.source),rows=[],gold=[],tests={traces:0,reports:0,hidden_absent:0},masks=[];
 for(let i=0;i<16;i++)masks.push(r()%(2**c.k));
 for(let j=0;j<masks.length;j++){
   const m=masks[j],query=(j%c.k)+1,values=Object.fromEntries(c.keys.map((key,i)=>[key,m>>>i&1?.5:-.5]));
   values[c.hiddenIndex]=c.f==="index"?query/c.k:0;
   let s=state(api,w,values);const hist=[observe(api,w,s)];
   while(s.encounter!==c.report){const o=observe(api,w,s);if(o.actions.length!==1)fail("nonforced cue step");s=api.stepV2(w,s,o.actions[0].id).next;hist.push(observe(api,w,s));}
   const ob=hist.at(-1);
   if(hist.length!==c.k+2||ob.values[c.cue]!==0||Object.keys(ob.values).sort().join(",")!==[c.cue,c.index].sort().join(","))fail("temporal observation leakage");
   const observed=hist.slice(1,-1).map(o=>Number(o.values[c.cue]>0));
   if(observed.length!==c.k||observed.some((v,i)=>v!==((m>>>i)&1)))fail("cue sequence mismatch");
   const expected=c.f==="parity"?observed.reduce((a,b)=>a^b,0)===1:Boolean(observed[query-1]);
   const action=expected?c.a:c.b,other=expected?c.b:c.a;
   if(api.stepV2(w,s,action).next.encounter!==c.yes||api.stepV2(w,s,other).next.encounter!==c.no)fail("memory runtime mismatch");
   tests.traces++;tests.reports+=2;tests.hidden_absent++;
   for(const mode of ["history","current"]){
     const id=c.id+"_"+j+"_"+mode;
     rows.push({id,world_id:c.id,kind:"memory",mode,task:c.taskRule,observation:ob,...(mode==="history"?{history:hist.slice(0,-1)}:{}),output_contract:"Return one legal action ID."});
     gold.push({id,action,family:c.f,k:c.k,query,mode});
   }
 }
 const bounds={family:c.f,k:c.k,uniform_current_accuracy:[1,2],full_history_accuracy:[1,1],
   bits_for_perfect_deterministic_memory:c.f==="parity"?1:c.k,
   explicit_prefix_memory_policy:Array.from({length:c.k+1},(_,b)=>({bits:b,accuracy:c.f==="parity"?(b?[1,1]:[1,2]):[c.k+b,2*c.k]}))};
 return {rows,gold,tests,bounds};
}

// Exact finite deterministic belief-state planning. States carry equal unit
// prior mass. Observation histories are represented by recursive cells;
// all action menus within a cell must agree. Terminal reward is paid once.
export function beliefOracle(api,w,roots,payoff,budget){
 let nodes=0;
 function rec(states,h){
   nodes++;
   if(states.every(s=>own(payoff,s.encounter)))return states.reduce((a,s)=>a+payoff[s.encounter],0);
   if(h===0)return states.reduce((a,s)=>a+(payoff[s.encounter]??0),0);
   if(states.some(s=>own(payoff,s.encounter)))fail("mixed terminal observation");
   const menu=observe(api,w,states[0]).actions.map(x=>x.id);
   if(!menu.length||states.some(s=>!same(menu,observe(api,w,s).actions.map(x=>x.id))))fail("inconsistent legal menu");
   return Math.max(...menu.map(a=>value(states,a,h)));
 }
 function value(states,a,h){
   const next=states.map(s=>api.stepV2(w,s,a).next);
   return splitBy(next,s=>rootKey(observe(api,w,s))).reduce((n,cell)=>n+rec(cell,h-1),0);
 }
 const cells=splitBy(roots,s=>rootKey(observe(api,w,s))),out=[];
 for(const states of cells){
   const observation=observe(api,w,states[0]),menu=observation.actions.map(x=>x.id),scores=Object.fromEntries(menu.map(a=>[a,value(states,a,budget)])),max=Math.max(...Object.values(scores));
   out.push({observation,denominator:states.length,values:scores,winners:menu.filter(a=>scores[a]===max),numerator:max});
 }
 return {numerator:out.reduce((a,b)=>a+b.numerator,0),denominator:roots.length,cells:out,nodes};
}
function planning(h,mode,r,make){
 const id=make("sw"),start=make("page"),stages=Array.from({length:h-1},()=>make("page"));
 const direct=make("end"),scouted=make("end"),wrong=make("end"),settled=make("end");
 const survey=make("act"),settle=make("act"),positive=make("act"),negative=make("act");
 const regime="ledger.regime",cue="ledger.cue",plus=op("GT",[P(regime),C(0)]),minus=op("LT",[P(regime),C(0)]);
 const rule="The hidden regime is equally likely positive or negative. At the opening, direct correct commitment pays 8, wrong pays 0, settlement pays 5. Survey followed by a correct informed commitment pays 6, wrong pays 0; completion takes "+h+" actions total. Unfinished plans pay 0. The public cue is the regime when available, otherwise 0. Survey "+(mode==="missing"?"does not reveal":"reveals")+" the regime. Maximize expected utility within the action budget.";
 const lines=[...header(id,[varline(regime),varline(cue,0,"public")],start,[start,...stages,direct,scouted,wrong,settled]),enc(start,0,0,rule)];
 const groups=[
   [opt(survey,"Survey the regime."),rx(survey,make("rx"),stages[0],set(cue,mode==="missing"?C(0):P(regime)))],
   [opt(settle,"Accept settlement."),rx(settle,make("rx"),settled)],
   [opt(positive,"Commit to positive regime now."),rx(positive,make("rx"),direct,"NONE",plus),rx(positive,make("rx"),wrong,"NONE","TRUE","C(0)")],
   [opt(negative,"Commit to negative regime now."),rx(negative,make("rx"),direct,"NONE",minus),rx(negative,make("rx"),wrong,"NONE","TRUE","C(0)")]
 ];
 // Randomize root order without changing the action semantics.
 for(let i=groups.length-1;i>0;i--){const j=r()%(i+1);[groups[i],groups[j]]=[groups[j],groups[i]];}for(const g of groups)lines.push(...g);
 for(let i=0;i<stages.length;i++){
   lines.push(enc(stages[i],i+1,i+1,"Survey underway. The public cue is recorded if the survey provides it."));
   if(i<stages.length-1){const a=make("act");lines.push(opt(a,"Complete the next survey step."),rx(a,make("rx"),stages[i+1]));}
   else{
     for(const [t,g] of [["Commit to the positive regime.",plus],["Commit to the negative regime.",minus]]){
       const a=make("act");lines.push(opt(a,t),rx(a,make("rx"),scouted,"NONE",g),rx(a,make("rx"),wrong,"NONE","TRUE","C(0)"));
     }
   }
 }
 lines.push(enc(direct,1,h,"Direct correct commitment.",h),enc(scouted,h,h+1,"Survey correct commitment."),enc(wrong,1,h+2,"Wrong commitment.",h),enc(settled,1,h+3,"Settlement.",h));
 return {id,h,mode,source:src(lines),regime,cue,survey,settle,positive,negative,payoff:{[direct]:8,[scouted]:6,[wrong]:0,[settled]:5},rule};
}
function planningRows(api,c){
 const w=api.compileV2(c.source),roots=[-.5,.5].map(v=>state(api,w,{[c.regime]:v,[c.cue]:c.mode==="visible"?v:0}));
 const rows=[],gold=[],checks=[];
 for(const budget of [1,c.h]){
   const result=beliefOracle(api,w,roots,c.payoff,budget);
   const expected=c.mode==="visible"?8:budget===1||c.mode==="missing"?5:6;
   if(result.numerator!==expected*result.denominator)fail("belief oracle control");
   result.cells.forEach((cell,i)=>{
     const wanted=c.mode==="visible"?(cell.observation.values[c.cue]>0?c.positive:c.negative):budget===1||c.mode==="missing"?c.settle:c.survey;
     if(cell.winners.length!==1||cell.winners[0]!==wanted)fail("branch planning action mismatch");
     const id=c.id+"_h"+budget+"_c"+i;
     rows.push({id,world_id:c.id,kind:"planning",action_budget:budget,task:c.rule,observation:cell.observation,output_contract:"Return the optimal legal first action ID assuming optimal continuation."});
     gold.push({id,actions:cell.winners,numerator:cell.numerator,denominator:cell.denominator,values:cell.values,h:c.h,mode:c.mode,budget});
   });
   checks.push({h:c.h,mode:c.mode,budget,numerator:result.numerator,denominator:result.denominator,cells:result.cells.length,nodes:result.nodes});
 }
 // Explicit check: hidden survey creates two distinct observation cells and
 // their optimal next reports depend on the actual regime.
 const successors=roots.map(s=>api.stepV2(w,s,c.survey).next),after=beliefOracle(api,w,successors,c.payoff,c.h-1);
 if(after.numerator!== (c.mode==="missing"?6:12)||after.cells.length!==(c.mode==="missing"?1:2))fail("survey information control");
 return {rows,gold,checks,after_survey:{h:c.h,mode:c.mode,numerator:after.numerator,denominator:after.denominator,cells:after.cells.length}};
}
export function makeSuite({split,seed,replicates=1,api=runtime,evaluate=evalExpr,verify=true}){
 if(!own(SPLITS,split)||!Number.isInteger(replicates)||replicates<1||replicates>16)fail("invalid suite");
 const r=rng(seed),make=identity(r),cases=[],author=[],authorGold=[],player=[],playerGold=[],plan=[],planGold=[];
 const receipt={split,replicates,synthesis:[],memory:[],planning:[],after_survey:[]};
 for(let rep=0;rep<replicates;rep++){
   for(const k of K){
     const c=synthesis(SPLITS[split],k,r,make);cases.push(c);author.push(c.task);authorGold.push({id:c.id,formula:c.gate,family:c.f,k});
     if(verify){
       const score=scoreFormula(api,evaluate,c,c.gate),neg=scoreFormula(api,evaluate,c,"NOT("+c.gate+")");
       const raw=api.compileV2(c.task.source);let baseline=0;
       for(const x of c.probes){const v=Object.fromEntries(c.keys.map((key,j)=>[key,x[j]]));baseline+=Number((api.stepV2(raw,state(api,raw,v),c.act).next.encounter===c.yes)===c.reference(x));}
       if(score.grid!==score.grid_total||score.runtime!==score.runtime_total||score.binary!==score.binary_total||score.errors||neg.grid||neg.binary||neg.runtime)fail("synthesis controls");
       let rejected=false;try{scoreFormula(api,evaluate,c,c.gate+" | G:TRUE",false);}catch{rejected=true;}if(!rejected)fail("scope injection");
       receipt.synthesis.push({id:c.id,family:c.f,k,positive_binary:c.truth.filter(Boolean).length,relevance_coordinates:c.k,baseline_grid:baseline,...score,inverted_grid:neg.grid,inverted_binary:neg.binary,scope_rejected:rejected});
     }
     for(const f of ["parity","index"]){const m=memory(f,k,r,make),out=memoryRows(api,m,r);player.push(...out.rows);playerGold.push(...out.gold);receipt.memory.push({id:m.id,...out.tests,...out.bounds});}
   }
   for(const h of H)for(const mode of ["hidden","visible","missing"]){
     const c=planning(h,mode,r,make),out=planningRows(api,c);plan.push(...out.rows);planGold.push(...out.gold);receipt.planning.push(...out.checks);receipt.after_survey.push(out.after_survey);
   }
 }
 return {split,seed,cases,author,authorGold,player,playerGold,planning:plan,planningGold:planGold,receipt};
}
