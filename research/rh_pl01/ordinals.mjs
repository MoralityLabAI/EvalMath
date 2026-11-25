// RH-PL-15: natural ordinal facts derived from the frozen least-inductive Omega.
// Every helper returns a derivation in the unchanged Hilbert kernel.
import {pairs} from './pairs.mjs';
import {kernel} from './kernel.mjs';

function buildOrdinals(ps,k){
 function prepare(raw,sharedCtx=null){
  const ctx=sharedCtx||ps.prepare(raw);
  const {p,t,ar,ns,cases,pack,all,allP,and,chain,explode,orLeft,orRight,refl}=ctx;
  const {apply,inst,move,symmetric,replace,empty,succ}=t;
  const {imp,gen,neg}=ar;
  const {E,M,A,O,X,sub,hyp,mp,generalize,abs,left,right,conj,ui,introAt,exIntro,contra}=p.logic;
  const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
  const omega=w=>sub(p.omegaW,1,w);
  const transitive=x=>all([90,91],chain([M(90,91),M(91,x)],M(90,x)));
  const le=(x,n)=>O(E(x,n),M(x,n));
  const memberOfOmega=x=>gen(90,imp(M(90,x),M(90,1)));
  const predecessor=(x,w)=>O(empty(x),X(89,A(M(89,w),succ(89,x))));
  const assume=(fs,fn)=>{const hs=fs.map(hyp);return hs.reduceRight((q,h)=>abs(h,q),fn(...hs))};

  // A checked instance of the existing separation-to-induction compiler.
  // The base and step callbacks may depend on the displayed Omega assumption.
  function inductionProof(phi,baseFn,stepFn){
   const scheme=p.prove(phi),hw=hyp(p.omegaW);
   const hb=hyp(ns[ns[scheme.base].y].x);
   const base=introAt(abs(hb,baseFn(left(hb),right(hb),hw)),20,scheme.base);
   const stepBody=ns[ns[scheme.step].y].y,hs=hyp(ns[stepBody].x);
   const nx=left(hs),tail=right(hs),ny=left(tail),last=right(tail),ss=left(last),ih=right(last);
   const step=allP([21,22],abs(hs,stepFn(nx,ny,ss,ih,hw)));
   assert(step.f===scheme.step,'ordinal induction step');
   const result=abs(hw,apply(scheme.result,hw,base,step));
   assert(result.deps.size===0,'ordinal induction dependencies');
   return result;
  }

  const omegaTransitive=inductionProof(memberOfOmega(0),(e,n)=>{
   const a=90,h=hyp(M(a,20));
   return generalize(a,abs(h,explode(h,ui(e,a),M(a,1))));
  },(nx,ny,ss,ih)=>{
   const a=90,h=hyp(M(a,22)),d=mp(h,left(ui(ss,a)));
   const q=cases(d,M(a,21),E(a,21),m=>mp(m,ui(ih,a)),eq=>replace(nx,symmetric(eq),M(99,1),99));
   return generalize(a,abs(h,q));
  });

  const naturalTransitive=inductionProof(transitive(0),(e,n)=>{
   return allP([90,91],assume([M(90,91),M(91,20)],(ab,bn)=>explode(bn,ui(e,91),M(90,20))));
  },(nx,ny,ss,ih)=>{
   return allP([90,91],assume([M(90,91),M(91,22)],(ab,by)=>{
    const d=mp(by,left(ui(ss,91)));
    const ax=cases(d,M(91,21),E(91,21),bx=>apply(inst(ih,90,91),ab,bx),eq=>replace(ab,eq,M(90,99),99));
    return mp(orLeft(ax,E(90,21)),right(ui(ss,90)));
   }));
  });
  const transClosed=generalize(1,naturalTransitive);
  function theoremAt(closed,hOmega,n,hNat){
   const atom=ns[hNat.f];assert(atom.tag==='m'&&atom.x===n,'ordinal membership parameter');
   const w=atom.y,q=ui(closed,w);
   assert(ns[q.f].x===hOmega.f,'ordinal Omega parameter');
   return mp(hNat,ui(mp(hOmega,q),n));
  }
  const transAt=(hOmega,n,hNat)=>theoremAt(transClosed,hOmega,n,hNat);
  function successorMember(hSucc,x){
   return mp(orRight(M(x,x),refl(x)),right(ui(hSucc,x)));
  }

  // Transitivity plus induction proves natural irreflexivity without Foundation.
  const naturalIrreflexive=inductionProof(neg(M(0,0)),(e,n)=>ui(e,20),(nx,ny,ss,ih,hw)=>{
   const self=hyp(M(22,22)),d=mp(self,left(ui(ss,22))),xy=successorMember(ss,21);
   const tr=transAt(hw,21,nx);
   const xx=cases(d,M(22,21),E(22,21),yx=>apply(inst(tr,21,22),xy,yx),eq=>replace(xy,eq,M(21,99),99));
   return mp(ih,contra(abs(self,xx)));
  });
  const irreflClosed=generalize(1,naturalIrreflexive);
  const noSelfAt=(hOmega,n,hNat)=>theoremAt(irreflClosed,hOmega,n,hNat);

  const predecessorClassification=inductionProof(predecessor(0,1),(e,n)=>orLeft(e,X(89,A(M(89,1),succ(89,20)))),(nx,ny,ss,ih)=>{
   return orRight(empty(22),exIntro(X(89,A(M(89,1),succ(89,22))),21,conj(nx,ss)));
  });
  const predecessorClosed=generalize(1,predecessorClassification);
  const classifyAt=(hOmega,n,hNat)=>theoremAt(predecessorClosed,hOmega,n,hNat);

  // If next <= last and next is succ(prev), then prev is a member of last.
  function down(hOmega,last,hn,prev,next,hSucc,orderNext){
   assert(orderNext.f===le(next,last),'predecessor initial-segment premise');
   const pn=successorMember(move(hSucc,succ(prev,next)),prev),tr=transAt(hOmega,last,hn);
   return cases(orderNext,E(next,last),M(next,last),eq=>replace(pn,eq,M(prev,99),99),nl=>apply(inst(tr,prev,next),pn,nl));
  }
  function fresh(hOmega,n,hn,s,hSucc){
   const hs=move(hSucc,succ(n,s)),inside=successorMember(hs,n),tr=transAt(hOmega,n,hn);
   const h=hyp(le(s,n));
   const self=cases(h,E(s,n),M(s,n),eq=>replace(inside,eq,M(n,99),99),sn=>apply(inst(tr,n,s),inside,sn));
   return mp(noSelfAt(hOmega,n,hn),contra(abs(h,self)));
  }
  function succInjectAt(hOmega,x,y,s,natx,naty,succx,succy){
   const sx=move(succx,succ(x,s)),sy=move(succy,succ(y,s));
   const xs=successorMember(sx,x),ys=successorMember(sy,y);
   const dx=mp(xs,left(ui(sy,x))),dy=mp(ys,left(ui(sx,y)));
   return cases(dx,M(x,y),E(x,y),xy=>cases(dy,M(y,x),E(y,x),yx=>{
    const self=apply(inst(transAt(hOmega,x,natx),x,y),xy,yx);
    return explode(self,noSelfAt(hOmega,x,natx),E(x,y));
   },eq=>symmetric(eq)),eq=>eq);
  }

  const w=37,n=60,s=61,x=62,y=63;
  const successorInjectivity=pack([omega(w),M(n,w),M(x,w),succ(n,s),succ(x,s)],(hw,hn,hx,sn,sx)=>succInjectAt(hw,n,x,s,hn,hx,sn,sx));
  const successorFresh=pack([omega(w),M(n,w),succ(n,s)],(hw,hn,hs)=>fresh(hw,n,hn,s,hs));
  const predecessorInitialSegment=pack([omega(w),M(n,w),succ(x,y),le(y,n)],(hw,hn,ss,hy)=>down(hw,n,hn,x,y,ss,hy));

  const named=[
   ['omega_transitive',omegaTransitive],
   ['natural_members_transitive',naturalTransitive],
   ['natural_members_irreflexive',naturalIrreflexive],
   ['natural_zero_or_successor',predecessorClassification],
   ['natural_successor_injective',successorInjectivity],
   ['successor_outside_previous_initial_segment',successorFresh],
   ['successor_predecessor_in_initial_segment',predecessorInitialSegment]
  ];
  function run(cap=32000000){return named.map(([name,q])=>({...ctx.get(name,q,cap),predicate_origin:'frozen_least_inductive_omega'}))}
  return {...ctx,ctx,omega,transitive,le,predecessor,omegaTransitive,naturalTransitive,naturalIrreflexive,predecessorClassification,successorInjectivity,successorFresh,predecessorInitialSegment,transAt,noSelfAt,classifyAt,down,fresh,succInjectAt,successorMember,run};
 }
 return {prepare};
}
export const ordinals=buildOrdinals(pairs,kernel);
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/ordinals.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(ordinals.prepare(raw).run().map(x=>x.receipt),null,2));
}
