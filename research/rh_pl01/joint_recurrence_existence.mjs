// RH-PL-18: construct the joint exact numerator/denominator recurrence
// block in the frozen target's original clauses and variable slots.
import {numeratorExistence} from './numerator_existence.mjs';
import {denominatorBridge} from './denominator_bridge.mjs';
import {makeNumeratorPredicates} from './numerator_predicates.mjs';

function prepare(raw,sharedCtx=null){
 const numerator=numeratorExistence.prepare(raw,sharedCtx);
 const {ctx,predicates:d,recurrence}=numerator;
 const {p,t,ar,ns,pack,witness,allP,and}=ctx;
 const {inst,nest,move,empty}=t;
 const {X,mp,left,right,exIntro}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const denominator=denominatorBridge.prepare(raw,ctx);
 const premiseIndices=[0,1,2,3,4,5,6],clauseIndices=[13,14,18,19,20,21];
 const premises=premiseIndices.map(i=>d.clause(i));
 const block=and(clauseIndices.map(i=>d.clause(i)));
 const innerGoal=X(d.G,block),goal=X(d.B,innerGoal);
 const result=pack(premises,(omega,mz,ez,mo,successorOne,addTotal,mulTotal)=>{
   const normalizedDenominator=mp(nest(omega,mo,mulTotal),recurrence.result);
   return witness(normalizedDenominator,d.B,hd=>{
     const denExact=mp(nest(omega,mz,move(ez,empty(d.Z)),mo,
       move(hd,denominator.predicates.normalized(d.B))),denominator.result);
     const denTotal=left(denExact),denBase=left(right(denExact)),denUpdate=right(right(denExact));
     const numeratorExists=mp(nest(omega,mz,ez,addTotal,mulTotal,denTotal),numerator.result);
     return witness(numeratorExists,d.G,hn=>{
       const numTotal=left(hn),numBase=left(right(hn)),numUpdate=right(right(hn));
       const exactBlock=nest(numTotal,denTotal,numBase,denBase,numUpdate,denUpdate);
       assert(exactBlock.f===block,'exact joint frozen recurrence block');
       return exIntro(goal,d.B,exIntro(innerGoal,d.G,exactBlock));
     });
   });
 });
 assert(ns[result.f].y===goal&&result.deps.size===0,'joint exact recurrence existence');

 const source=makeNumeratorPredicates(ctx,raw,{W:0,Z:1,C0:2,ADD:3,MUL:4,G:7,B:8});
 const sourcePremises=premiseIndices.map(i=>source.sourceClauses[i]);
 const sourceGoal=X(8,X(7,and(clauseIndices.map(i=>source.sourceClauses[i]))));
 const sourceResult=move(inst(allP([37,60,6,7,8],result),0,1,2,3,4),ar.imp(and(sourcePremises),sourceGoal));
 assert(ns[sourceResult.f].x===and(sourcePremises)&&ns[sourceResult.f].y===sourceGoal,'original-slot joint recurrence existence');

 function run(){
   return [['joint_exact_numerator_denominator_graphs_exist',result,d.slots],
     ['frozen_joint_numerator_denominator_clauses_exist',sourceResult,source.slots]].map(([name,proof,slots])=>{
     const row=ctx.get(name,proof);
     Object.assign(row.receipt,{source_premise_indices:premiseIndices,source_clause_indices:clauseIndices,
       source_slots:slots,denominator_graph_witness_eliminated:true,numerator_graph_witness_eliminated:true,
       joint_recurrence_existence:true,arithmetic_semantics_still_conditional:true,
       actual_rh_proof:false,finite_rh_upper_bound:false});
     return row;
   });
 }
 return {ctx,numerator,denominator,predicates:d,premiseIndices,clauseIndices,premises,block,goal,result,
   source,sourcePremises,sourceGoal,sourceResult,run};
}
export const jointRecurrenceExistence={prepare};
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/joint_recurrence_existence.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(jointRecurrenceExistence.prepare(raw).run().map(x=>x.receipt),null,2));
}
