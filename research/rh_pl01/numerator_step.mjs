// RH-PL-18: the affine numerator step is a total, single-valued relation
// on the naturals of the frozen least-inductive Omega.
import {ordinals} from './ordinals.mjs';
import {makeNumeratorPredicates} from './numerator_predicates.mjs';
import {kernel} from './kernel.mjs';

function prepare(raw,sharedCtx=null){
 const ctx=sharedCtx?.classifyAt&&sharedCtx?.succInjectAt?sharedCtx:ordinals.prepare(raw,sharedCtx);
 const {p,t,ar,ns,pack,witness,cases,all,allP,and,explode,orLeft,orRight,refl}=ctx;
 const {inst,nest,move,symmetric,trans,replace,empty,succ}=t;
 const {E,A,O,X,split,exAt,hyp,mp,abs,left,right,conj,ui,exIntro}=p.logic;
 const {imp}=ar;
 const d=makeNumeratorPredicates(ctx,raw),{nat,gb,mul,add,B}=d;
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const [y,a,b,c,mark]=[70,71,72,73,99];
 const zeroBranch=(y,a,b)=>A(empty(y),E(a,b));
 const successorBranch=(y,a,b)=>X(110,A(nat(110),X(111,A(nat(111),X(112,A(nat(112),
   and([succ(110,y),gb(B,110,111),mul(y,a,112),add(112,111,b)])))))));
 const relation=(y,a,b)=>O(zeroBranch(y,a,b),successorBranch(y,a,b));
 const totalRelation=all([y,a],imp(A(nat(y),nat(a)),X(b,A(nat(b),relation(y,a,b)))));
 const functionalRelation=all([y,a,b,c],imp(and([nat(y),nat(a),nat(b),nat(c)]),
   imp(A(relation(y,a,b),relation(y,a,c)),E(b,c))));
 const premises=[d.omega,d.clause(14),d.mt,d.addTotal];

 function withNat(q,x,fn){return witness(q,x,h=>fn(left(h),right(h)))}
 function functional1(total,x,u,v,mx,mu,mv,gu,gv){
   const q=mp(nest(mx,mu,mv),inst(right(total),x,u,v));
   const [l,r]=split(ns[q.f].x);
   return mp(conj(move(gu,l),move(gv,r)),q)
 }
 function functional2(total,x,y,u,v,mx,my,mu,mv,gu,gv){
   const q=mp(nest(mx,my,mu,mv),inst(right(total),x,y,u,v));
   const [l,r]=split(ns[q.f].x);
   return mp(conj(move(gu,l),move(gv,r)),q)
 }
 function introduceSuccessor(y,a,b,x,dv,u,mx,md,mu,sx,dx,product,sum){
   const target=successorBranch(y,a,b),atX=exAt(target,x),existsD=split(atX)[1];
   const atD=exAt(existsD,dv),existsU=split(atD)[1];
   const body=nest(move(sx,succ(x,y)),move(dx,gb(B,x,dv)),move(product,mul(y,a,u)),move(sum,add(u,dv,b)));
   const eu=exIntro(existsU,u,conj(mu,body));
   const ed=exIntro(existsD,dv,conj(md,eu));
   return exIntro(target,x,conj(mx,ed))
 }
 function withSuccessor(q,[x,dv,u],fn){
   return withNat(q,x,(mx,ed)=>withNat(ed,dv,(md,eu)=>withNat(eu,u,(mu,body)=>{
     const sx=left(body),tail=right(body),dx=left(tail),last=right(tail);
     return fn({x,d:dv,u,mx,md,mu,sx,dx,product:left(last),sum:right(last)})
   })))
 }
 function emptySuccessor(emptyY,existsStep,goal,x=120){
   return withNat(existsStep,x,(mx,ed)=>
     withNat(ed,x+1,(md,eu)=>withNat(eu,x+2,(mu,body)=>{
       const member=ctx.successorMember(left(body),x);
       return explode(member,ui(emptyY,x),goal)
     })))
 }
 // A fresh output binder keeps this interface usable when the caller has
 // argument 70, which is the fixed binder of the older updateGoal helper.
 function successorUpdateGoal(y,a,dv,b){
   let u=113;while([y,a,dv,b,d.W,d.ADD,d.MUL].includes(u))u++;
   return X(u,A(nat(u),A(mul(y,a,u),add(u,dv,b))))
 }
 function freshVariables(count){
   let next=113;
   for(const n of ns){
     if(!n)continue;
     if(n.tag==='e'||n.tag==='m')next=Math.max(next,n.x+1,n.y+1);
     else if(n.tag==='a')next=Math.max(next,n.x+1)
   }
   return Array.from({length:count},(_,i)=>next+i)
 }
 // Arguments after the set variables are the five natural-membership
 // proofs, followed by Succ(x,y), R(y,a,b), and DEN(x,dv).
 function successorUpdateAt(hw,denTotal,x,y,a,b,dv,mx,my,ma,mb,md,hs,hr,hd){
   for(const [v,h] of [[x,mx],[y,my],[a,ma],[b,mb],[dv,md]])
     assert(h.f===nat(v),'successor update natural parameter');
   assert(hw.f===d.omega&&denTotal.f===d.clause(14),'successor update source parameters');
   assert(hr.f===relation(y,a,b),'successor update relation parameter');
   hs=move(hs,succ(x,y));hd=move(hd,gb(B,x,dv));
   const target=successorUpdateGoal(y,a,dv,b),[xp,dp,up,m]=freshVariables(4);
   return cases(hr,zeroBranch(y,a,b),successorBranch(y,a,b),zero=>
     explode(ctx.successorMember(hs,x),ui(left(zero),x),target),step=>
     withSuccessor(step,[xp,dp,up],r=>{
       const xx=ctx.succInjectAt(hw,r.x,x,y,r.mx,mx,r.sx,hs);
       const atX=replace(move(r.dx,gb(B,r.x,r.d)),xx,gb(B,m,r.d),m);
       const dd=functional1(denTotal,x,r.d,dv,mx,r.md,md,atX,hd);
       const sum=replace(move(r.sum,add(r.u,r.d,b)),dd,add(r.u,m,b),m);
       return exIntro(target,r.u,nest(r.mu,move(r.product,mul(y,a,r.u)),sum))
     }))
 }

 const totalResult=pack(premises,(hw,denTotal,mulTotal,addTotal)=>{
   const hn=hyp(A(nat(y),nat(a))),my=left(hn),ma=right(hn);
   const existsOutput=X(b,A(nat(b),relation(y,a,b)));
   const classification=ctx.classifyAt(hw,y,my);
   const predecessor=X(89,A(nat(89),succ(89,y)));
   const output=cases(classification,empty(y),predecessor,ey=>{
     const r=orLeft(conj(ey,refl(a)),successorBranch(y,a,a));
     return exIntro(existsOutput,a,conj(ma,r))
   },pred=>withNat(pred,120,(mx,sx)=>
     withNat(mp(mx,ui(left(denTotal),120)),121,(md,dx)=>
       withNat(mp(conj(my,ma),inst(left(mulTotal),y,a)),122,(mu,product)=>
         withNat(mp(conj(mu,md),inst(left(addTotal),122,121)),123,(mb,sum)=>{
           const step=introduceSuccessor(y,a,123,120,121,122,mx,md,mu,sx,dx,product,sum);
           const r=orRight(zeroBranch(y,a,123),step);
           return exIntro(existsOutput,123,conj(mb,r))
         })))));
   return allP([y,a],abs(hn,output))
 });
 assert(ns[totalResult.f].y===totalRelation,'affine step totality target');

 const functionalResult=pack(premises,(hw,denTotal,mulTotal,addTotal)=>{
   const hn=hyp(and([nat(y),nat(a),nat(b),nat(c)]));
   const my=left(hn),ma=left(right(hn)),mb=left(right(right(hn))),mc=right(right(right(hn)));
   const hr=hyp(A(relation(y,a,b),relation(y,a,c))),rb=left(hr),rc=right(hr);
   const same=cases(rb,zeroBranch(y,a,b),successorBranch(y,a,b),zb=>
     cases(rc,zeroBranch(y,a,c),successorBranch(y,a,c),zc=>
       trans(symmetric(right(zb)),right(zc)),sc=>emptySuccessor(left(zb),sc,E(b,c))),sb=>
     cases(rc,zeroBranch(y,a,c),successorBranch(y,a,c),zc=>
       emptySuccessor(left(zc),sb,E(b,c)),sc=>
       withSuccessor(sb,[120,121,122],l=>withSuccessor(sc,[124,125,126],r=>{
         const xx=ctx.succInjectAt(hw,l.x,r.x,y,l.mx,r.mx,l.sx,r.sx);
         const rightDen=replace(move(r.dx,gb(B,r.x,r.d)),symmetric(xx),gb(B,mark,r.d),mark);
         const dd=functional1(denTotal,l.x,l.d,r.d,l.mx,l.md,r.md,l.dx,rightDen);
         const uu=functional2(mulTotal,y,a,l.u,r.u,my,ma,l.mu,r.mu,l.product,r.product);
         let rightSum=move(r.sum,add(r.u,r.d,c));
         rightSum=replace(rightSum,symmetric(uu),add(mark,r.d,c),mark);
         rightSum=replace(rightSum,symmetric(dd),add(l.u,mark,c),mark);
         return functional2(addTotal,l.u,l.d,b,c,l.mu,l.md,mb,mc,l.sum,rightSum)
       }))));
   return allP([y,a,b,c],abs(hn,abs(hr,same)))
 });
 assert(ns[functionalResult.f].y===functionalRelation,'affine step functionality target');

 const goal=A(totalRelation,functionalRelation);
 const result=pack(premises,(...hs)=>{
   const source=nest(...hs);
   return conj(mp(source,totalResult),mp(source,functionalResult))
 });
 assert(ns[result.f].y===goal&&result.deps.size===0,'affine step joint target');
 const [sx,sy,sa,sb,sd]=[80,81,82,83,84];
 const successorUpdatePremises=[d.omega,d.clause(14),nat(sx),nat(sy),nat(sa),nat(sb),nat(sd),
   succ(sx,sy),relation(sy,sa,sb),gb(B,sx,sd)];
 const successorUpdateTarget=successorUpdateGoal(sy,sa,sd,sb);
 const successorUpdateResult=pack(successorUpdatePremises,(hw,dt,mx,my,ma,mb,md,ss,r,den)=>
   successorUpdateAt(hw,dt,sx,sy,sa,sb,sd,mx,my,ma,mb,md,ss,r,den));
 assert(ns[successorUpdateResult.f].y===successorUpdateTarget&&successorUpdateResult.deps.size===0,
   'affine successor normalization target');
 function run(){
   return [
     ['affine_numerator_step_total_on_naturals',totalResult],
     ['affine_numerator_step_single_valued_on_naturals',functionalResult],
     ['affine_numerator_step_total_and_single_valued',result],
     ['affine_numerator_successor_step_to_normalized_update',successorUpdateResult]
   ].map(([name,pf])=>{
     const row=ctx.get(name,pf);
     Object.assign(row.receipt,{source_clauses:pf===successorUpdateResult?[0,14]:[0,14,6,5],source_slots:d.slots,
       relation_parameters:{omega:37,denominator:61,multiplication:8,addition:7},
       arbitrary_total_operations:true,denominator_recurrence_premise_required:false,
       graph_set_existence_included:false,actual_rh_proof:false});
     return row
   })
 }
 return {ctx,predicates:d,relation,zeroBranch,successorBranch,totalRelation,functionalRelation,
   totalResult,functionalResult,result,premises,goal,run,source_slots:d.slots,
   successorUpdateAt,successorUpdateGoal,successorUpdateResult,successorUpdatePremises,successorUpdateTarget,
   relation_source:kernel.encode(ar.ast(relation(y,a,b)))};
}
export const numeratorStep={prepare};
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/numerator_step.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(numeratorStep.prepare(raw).run().map(x=>x.receipt),null,2));
}
