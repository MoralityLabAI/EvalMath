// RH-PL-16: reconstruct exact frozen clauses 14, 19 and 21 from the
// normalized denominator graph supplied by the PL-15 construction.
import {pairs} from './pairs.mjs';
import {makeDenominatorPredicates} from './denominator_predicates.mjs';

function prepare(raw,sharedCtx=null){
 const ctx=sharedCtx??pairs.prepare(raw),{p,t,ar,ns,pack,witness,allP,and,refl}=ctx;
 const {apply,inst,nest,move,empty,succ}=t;
 const {E,A,split,qAt,exAt,hyp,mp,generalize,abs,left,right,conj,ui,exIntro}=p.logic;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const d=makeDenominatorPredicates(ctx,raw),{W,Z,C0,G,nat,at,total,functional,base,update,normalized,exact,clause}=d;
 const [exactTotal,exactBase,exactUpdate]=[clause(14),clause(19),clause(21)];

 // The totality half differs only in bound names. The functionality half
 // groups its natural-domain assumptions and its two graph applications.
 const totalPremises=[total(G),functional(G)];
 const totalResult=pack(totalPremises,(tot,fun)=>{
   const [tgtTotal,tgtFun]=split(exactTotal),[x,a,b]=[70,71,72];
   const body=d.qform(tgtFun,x,a,b),hNat=hyp(ns[body].x),hApp=hyp(ns[ns[body].y].x);
   const mx=left(hNat),ma=left(right(hNat)),mb=right(right(hNat));
   const ga=move(left(hApp),at(G,x,a)),gb=move(right(hApp),at(G,x,b));
   const eq=apply(inst(fun,x,a,b),mx,ma,mb,ga,gb);
   const funProof=move(allP([x,a,b],abs(hNat,abs(hApp,eq))),tgtFun);
   return conj(move(tot,tgtTotal),funProof)
 });
 assert(ns[totalResult.f].y===exactTotal,'exact denominator totality');

 // Totality supplies a natural output at the designated empty set;
 // the normalized base equation identifies it with the initial value.
 const basePremises=[nat(Z),empty(Z),total(G),base(G)];
 const baseResult=pack(basePremises,(mz,ez,tot,bs)=>{
   const val=mp(mz,ui(tot,Z));
   return witness(val,70,hv=>{
     const mv=left(hv),app=right(hv),eq=apply(inst(bs,Z,70),ez,mz,mv,app);
     const [,tail]=split(exAt(exactBase,70)),[tgtApp,tgtEq]=split(tail);
     assert(eq.f===tgtEq,'exact denominator initial equality');
     return exIntro(exactBase,70,nest(mv,move(app,tgtApp),eq))
   })
 });
 assert(ns[baseResult.f].y===exactBase,'exact denominator base');

 // Both successor terms in clause 21 use the same successor witness.
 // The outer value and product value use the same graph output, making
 // the final equality an instance of equality reflexivity.
 const updatePremises=[d.omega,total(G),update(G)];
 const updateResult=pack(updatePremises,(omega,tot,step)=>{
   const [x,y,a,b]=[70,71,72,73],mx=hyp(nat(x));
   const targetAt=qAt(exactUpdate,x),target=ns[targetAt].y;
   const next=mp(mx,ui(right(left(omega)),x));
   const out=witness(next,y,hy=>{
     const my=left(hy),sy=move(right(hy),succ(x,y));
     return witness(mp(mx,ui(tot,x)),a,ha=>witness(mp(my,ui(tot,y)),b,hb=>{
       const ma=left(ha),mb=left(hb),gx=right(ha),gy=right(hb);
       const product=apply(inst(step,x,y,a,b),mx,my,ma,mb,sy,gx,gy);
       const [,kTail]=split(exAt(target,y)),[sk,aExists]=split(kTail);
       const [,aTail]=split(exAt(aExists,b)),[appY,lExists]=split(aTail);
       const [,lTail]=split(exAt(lExists,y)),[sl,bExists]=split(lTail);
       const [,bTail]=split(exAt(bExists,a)),[appX,cExists]=split(bTail);
       const [,cTail]=split(exAt(cExists,b)),[prod,equal]=split(cTail);
       assert(equal===E(b,b),'same output/product witness');
       const cProof=exIntro(cExists,b,nest(mb,move(product,prod),refl(b)));
       const bProof=exIntro(bExists,a,nest(ma,move(gx,appX),cProof));
       const lProof=exIntro(lExists,y,nest(my,move(sy,sl),bProof));
       const aProof=exIntro(aExists,b,nest(mb,move(gy,appY),lProof));
       return exIntro(target,y,nest(my,move(sy,sk),aProof))
     }))
   });
   return move(generalize(x,abs(mx,out)),exactUpdate)
 });
 assert(ns[updateResult.f].y===exactUpdate,'exact denominator recurrence');

 const premises=[d.omega,nat(Z),empty(Z),nat(C0),normalized(G)];
 const result=pack(premises,(omega,mz,ez,mc,norm)=>{
   const tot=left(norm),fn=left(right(norm)),bs=left(right(right(norm))),st=right(right(right(norm)));
   const pTotal=mp(nest(tot,fn),totalResult);
   const pBase=mp(nest(mz,ez,tot,bs),baseResult);
   const pUpdate=mp(nest(omega,tot,st),updateResult);
   return nest(pTotal,pBase,pUpdate)
 });
 const goal=exact(G);
 assert(ns[result.f].x===and(premises)&&ns[result.f].y===goal,'aggregate exact denominator bridge');
 const components=[
   {name:'normalized_denominator_totality_to_exact_clause_14',result:totalResult,premises:totalPremises,goal:exactTotal,source_clauses:[14]},
   {name:'normalized_denominator_base_to_exact_clause_19',result:baseResult,premises:basePremises,goal:exactBase,source_clauses:[19]},
   {name:'normalized_denominator_update_to_exact_clause_21',result:updateResult,premises:updatePremises,goal:exactUpdate,source_clauses:[21]}
 ];
 function run(cap=48000000){
   const rows=[...components,{name:'normalized_denominator_to_exact_frozen_clauses',result,premises,goal,source_clauses:[14,19,21]}].map(c=>{
     const row=ctx.get(c.name,c.result,cap);
     Object.assign(row.receipt,{source_clauses:c.source_clauses,source_slot_mapping:d.slots,exact_frozen_consequent:true,actual_rh_proof:false});
     return row
   });
   return rows
 }
 return {ctx,predicates:d,result,premises,goal,clauses:d.clauses,sourceClauses:d.sourceClauses,slots:d.slots,normalized,exact,components,run};
}
export const denominatorBridge={prepare};
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/denominator_bridge.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(denominatorBridge.prepare(raw).run().map(x=>x.receipt),null,2));
}
