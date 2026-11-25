// RH-PL-16: construct a denominator graph satisfying the literal frozen
// totality, initial-value, and recurrence clauses.
import {ordinals} from './ordinals.mjs';
import {prefixRecursion} from './prefix_recursion.mjs';
import {denominatorBridge} from './denominator_bridge.mjs';
import {makeDenominatorPredicates} from './denominator_predicates.mjs';
import {kernel} from './kernel.mjs';

function prepare(raw,sharedCtx=null){
 const ctx=sharedCtx??ordinals.prepare(raw),{p,t,ar,ns,pack,witness,allP,and}=ctx;
 const {inst,nest,move,empty}=t;
 const {X,mp,exIntro}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const d=makeDenominatorPredicates(ctx,raw),bridge=denominatorBridge.prepare(raw,ctx);
 const recurrence=prefixRecursion.prepare(raw,ctx);
 const indices=[0,1,2,3,6],premises=indices.map(i=>d.clause(i));
 const goal=X(d.G,d.exact(d.G));
 const result=pack(premises,(omega,mz,ez,mc,mt)=>{
   const normalizedExists=mp(nest(omega,mc,mt),recurrence.result);
   return witness(normalizedExists,d.G,hn=>{
     const normalized=move(hn,d.normalized(d.G));
     const exact=mp(nest(omega,mz,move(ez,empty(d.Z)),mc,normalized),bridge.result);
     return exIntro(goal,d.G,exact);
   });
 });
 assert(ns[result.f].y===goal&&result.deps.size===0,'exact denominator existence');

 // Recover the original source slots, including the existential denominator
 // slot8. The source theorem records the full zero/one definition block.
 const source=makeDenominatorPredicates(ctx,raw,{W:0,Z:1,C0:2,MUL:4,G:8});
 const sourceIndices=[0,1,2,3,4,6],sourcePremises=sourceIndices.map(i=>source.sourceClauses[i]);
 const sourceGoal=X(8,and([14,19,21].map(i=>source.sourceClauses[i])));
 const specialized=inst(allP([37,60,6,8],result),0,1,2,4);
 const sourceResult=pack(sourcePremises,(omega,mz,ez,mo,successorOne,mt)=>{
   return move(mp(nest(omega,mz,ez,mo,mt),specialized),sourceGoal);
 });
 assert(ns[sourceResult.f].y===sourceGoal&&sourceResult.deps.size===0,'literal frozen denominator existence');

 const names=['exact_denominator_exists_from_omega_and_multiplication','frozen_denominator_clauses_exist'];
 const target_specs={
   [names[0]]:{kind:'existence',slots:d.slots,premise_indices:indices,clause_indices:[14,19,21],exists_graph:d.G},
   [names[1]]:{kind:'existence',slots:source.slots,premise_indices:sourceIndices,clause_indices:[14,19,21],exists_graph:8}
 };
 function run(){
   return [[names[0],result],[names[1],sourceResult]].map(([name,proof])=>{
     const row=ctx.get(name,proof);
     Object.assign(row.receipt,{frozen_denominator_clauses:[14,19,21],construction_from_pl15:true,
       exact_clause_21_bridge:true,source_premise_indices:target_specs[name].premise_indices,
       normalized_graph_witness_eliminated:true,actual_rh_proof:false});
     return row;
   });
 }
 return {ctx,predicates:d,result,premises,goal,sourceResult,sourcePremises,sourceGoal,run,
   frozen_slots:d.slots,source_slots:d.slots,target_specs};
}
export const denominatorExistence={prepare};
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/denominator_existence.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(denominatorExistence.prepare(raw).run().map(row=>row.receipt),null,2));
}
