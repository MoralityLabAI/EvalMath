// RH-PL-18: realize the affine numerator step as a total binary graph,
// apply the checked finite-prefix recursion constructor, and recover the
// literal frozen numerator clauses.
import {ordinals} from './ordinals.mjs';
import {numeratorStep} from './numerator_step.mjs';
import {binaryGraph} from './binary_graph.mjs';
import {prefixRecursion} from './prefix_recursion.mjs';
import {numeratorBridge} from './numerator_bridge.mjs';
import {makeNumeratorPredicates} from './numerator_predicates.mjs';
import {makeDenominatorPredicates} from './denominator_predicates.mjs';

function prepare(raw,sharedCtx=null){
 const ctx=sharedCtx??ordinals.prepare(raw),{p,t,ar,ns,pack,witness,allP,and}=ctx;
 const {apply,inst,nest,move,empty,succ}=t;
 const {X,hyp,mp,abs,left,right,exIntro}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const d=makeNumeratorPredicates(ctx,raw),{G,B,Z,nat,at}=d;
 const step=numeratorStep.prepare(raw,ctx);
 const graph=binaryGraph.prepare(raw,ctx,{W:d.W,T:64,relation:step.relation});
 assert(graph.totalRelation===step.totalRelation&&graph.functionalRelation===step.functionalRelation,'affine graph input contract');
 const recurrence=prefixRecursion.prepare(raw,ctx);
 const specialized=inst(allP([6,8],recurrence.result),Z,graph.T);
 const rec=makeDenominatorPredicates(ctx,raw,{W:d.W,Z,C0:Z,MUL:graph.T,G});
 const normalizedPremiseIndices=[0,1,5,6,14];
 const normalizedPremises=normalizedPremiseIndices.map(i=>d.clause(i));
 const normalizedGoal=X(G,d.normalized(G,B));
 const normalizedResult=pack(normalizedPremises,(omega,mz,addTotal,mulTotal,denTotal)=>{
   const relationLaws=mp(nest(omega,denTotal,mulTotal,addTotal),step.result);
   const graphExists=mp(relationLaws,graph.result);
   return witness(graphExists,graph.T,hgraph=>{
     const total2=left(hgraph),spec=right(hgraph);
     const recurrenceExists=mp(nest(omega,mz,move(total2,rec.mt)),specialized);
     return witness(recurrenceExists,G,hrec=>{
       const normalized=move(hrec,rec.normalized(G));
       const total=left(normalized),functional=left(right(normalized));
       const base=left(right(right(normalized))),update=right(right(right(normalized)));
       const [x,y,a,b,dv]=[40,49,42,43,44];
       const hs=[nat(x),nat(y),nat(a),nat(b),nat(dv),succ(x,y),at(G,x,a),at(G,y,b),at(B,x,dv)].map(hyp);
       const [mx,my,ma,mb,md,sx,gx,gy,dx]=hs;
       const application=apply(inst(update,x,y,a,b),mx,my,ma,mb,sx,gx,gy);
       const equivalence=mp(nest(my,ma,mb),inst(spec,y,a,b));
       const relation=mp(move(application,graph.app(graph.T,y,a,b)),left(equivalence));
       const operation=step.successorUpdateAt(omega,denTotal,x,y,a,b,dv,mx,my,ma,mb,md,sx,relation,dx);
       const normalizedOperation=move(operation,d.updateGoal(y,a,dv,b));
       const updateProof=allP([x,y,a,b,dv],hs.reduceRight((r,h)=>abs(h,r),normalizedOperation));
       assert(updateProof.f===d.update(G,B),'normalized numerator update');
       const output=nest(total,functional,base,updateProof);
       assert(output.f===d.normalized(G,B),'normalized numerator graph');
       return exIntro(normalizedGoal,G,output);
     });
   });
 });
 assert(ns[normalizedResult.f].y===normalizedGoal&&normalizedResult.deps.size===0,'normalized numerator existence');

 const bridge=numeratorBridge.prepare(raw,ctx);
 const premiseIndices=[0,1,2,5,6,14],premises=premiseIndices.map(i=>d.clause(i));
 const goal=X(G,d.exact(G,B));
 const result=pack(premises,(omega,mz,ez,addTotal,mulTotal,denTotal)=>{
   const normalizedExists=mp(nest(omega,mz,addTotal,mulTotal,denTotal),normalizedResult);
   return witness(normalizedExists,G,hn=>{
     const exact=mp(nest(omega,mz,move(ez,empty(Z)),denTotal,hn),bridge.result);
     return exIntro(goal,G,exact);
   });
 });
 assert(ns[result.f].y===goal&&result.deps.size===0,'exact numerator existence');

 // Generalize before changing arithmetic and graph slots, so all
 // simultaneous parameter changes are checked universal instantiations.
 const source=makeNumeratorPredicates(ctx,raw,{W:0,Z:1,C0:2,ADD:3,MUL:4,G:7,B:8});
 const sourcePremises=premiseIndices.map(i=>source.sourceClauses[i]);
 const sourceGoal=X(7,and([13,18,20].map(i=>source.sourceClauses[i])));
 const sourceResult=move(inst(allP([37,60,7,8,61],result),0,1,3,4,8),ar.imp(and(sourcePremises),sourceGoal));
 assert(ns[sourceResult.f].x===and(sourcePremises)&&ns[sourceResult.f].y===sourceGoal,'literal frozen numerator existence');

 const rows=[
   ['normalized_numerator_graph_exists',normalizedResult,normalizedPremiseIndices,'normalized'],
   ['exact_numerator_exists_given_total_denominator',result,premiseIndices,'exact'],
   ['frozen_numerator_clauses_exist_given_total_denominator',sourceResult,premiseIndices,'source']
 ];
 function run(){
   return rows.map(([name,proof,indices,kind])=>{
     const row=ctx.get(name,proof);
     Object.assign(row.receipt,{source_premise_indices:indices,source_slots:kind==='source'?source.slots:d.slots,
       normalized_numerator_existence:true,exact_frozen_numerator_clauses:kind==='normalized'?[]:[13,18,20],
       affine_binary_graph_witness_eliminated:true,finite_prefix_recursion_construction:true,
       denominator_totality_is_explicit:true,denominator_recurrence_premise_required:false,
       actual_rh_proof:false});
     return row;
   });
 }
 return {ctx,predicates:d,step,graph,recurrence,bridge,normalizedPremises,normalizedGoal,normalizedResult,
   premises,goal,result,source,sourcePremises,sourceGoal,sourceResult,run};
}
export const numeratorExistence={prepare};
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/numerator_existence.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(numeratorExistence.prepare(raw).run().map(x=>x.receipt),null,2));
}
