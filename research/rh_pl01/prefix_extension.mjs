// RH-PL-15: a bounded graph satisfying the exact Good predicate extends
// through its next natural index. Ordinal facts are derived from Omega.
import {ordinals} from './ordinals.mjs';
import {append} from './append.mjs';
import {makePrefixPredicates} from './prefix_predicates.mjs';
import {kernel} from './kernel.mjs';

function prepare(raw,sharedCtx){
 const ctx=sharedCtx||ordinals.prepare(raw);
 const {p,t,ar,ns,cases,pack,witness,allP,all,and,chain,explode,orLeft,orRight,refl}=ctx;
 const {apply,inst,nest,move,symmetric,trans,replace,empty,succ}=t,{imp,gen,neg}=ar;
 const {E,M,A,F,O,X,hyp,mp,generalize,abs,left,right,conj,ui,introAt,exIntro,contra}=p.logic;
 const d=makePrefixPredicates(ctx,raw),{nat,at,mul,subset,power,dom,domain,prefixDomain,functional,base,step,good}=d;
 const ap=append.prepare(raw,ctx),[s,b,G,n,a,U,P,Q]=[60,61,62,63,64,68,50,51],mark=99;
 const [i,j,c,e,v]=[70,73,71,72,75],le=(x,y)=>O(E(x,y),M(x,y));
 const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
 const premises=[d.omega,nat(n),nat(s),succ(n,s),nat(a),at(G,n,a),nat(b),mul(s,a,b),power(37,P),power(P,Q),subset(G,Q),good(G),domain(G,n)];
 const body=u=>and([subset(u,Q),good(u),domain(u,s),ap.relation(u)]);
 const goal=X(U,body(U));
 const result=pack(premises,(om,mn,ms,sns,ma,ga,mb,next,pw,pq,bg,gg,dg)=>{
   const oldFunc=left(right(gg)),oldBase=left(right(right(gg))),oldStep=right(right(right(gg)));
   const fresh=ctx.fresh(om,n,mn,s,sns);
   assert(fresh.f===neg(le(s,n)),'fresh successor interface');
   const oldOrder=(x,y,mx,my,gxy)=>mp(exIntro(dom(G,x),y,conj(my,gxy)),left(mp(mx,ui(dg,x))));
   function orderMember(x,order){
     const swapped=cases(order,E(x,n),M(x,n),eq=>orRight(M(x,n),eq),mem=>orLeft(mem,E(x,n)));
     return mp(swapped,right(ui(sns,x)))
   }
   // A natural output at the new endpoint would put that endpoint in the
   // old initial segment, contradicting its proved freshness.
   const mv=hyp(nat(c)),atNew=hyp(at(G,s,c));
   const forbidden=abs(atNew,oldOrder(s,c,ms,mv,atNew));
   const absent=move(generalize(c,abs(mv,mp(fresh,contra(forbidden)))),ap.absent);
   const appended=mp(nest(ms,mb,pw,pq,bg,move(oldFunc,ap.func(G)),absent),ap.boundedFunctional);
   return witness(appended,U,hu=>{
     const rel=left(hu),bounded=left(right(hu)),newFunc=move(right(right(hu)),functional(U));
     const relAt=(x,y)=>inst(rel,x,y);
     const oldInto=(x,y,gxy)=>mp(orLeft(gxy,A(E(x,s),E(y,b))),right(relAt(x,y)));
     const newInto=(x,y,eqx,eqy)=>mp(orRight(at(G,x,y),conj(eqx,eqy)),right(relAt(x,y)));
     // Establish both directions of the exact enlarged domain.
     const mi=hyp(nat(i)),du=hyp(dom(U,i));
     const forward=witness(du,v,hv=>{
       const mv=left(hv),av=right(hv),dis=mp(av,left(relAt(i,v)));
       return cases(dis,at(G,i,v),A(E(i,s),E(v,b)),old=>{
         return orRight(E(i,s),orderMember(i,oldOrder(i,v,mi,mv,old)))
       },eqs=>orLeft(left(eqs),M(i,s)))
     });
     const hi=hyp(le(i,s));
     const backward=cases(hi,E(i,s),M(i,s),eq=>{
       return exIntro(dom(U,i),b,conj(mb,newInto(i,b,eq,refl(b))))
     },mem=>{
       const dis=mp(mem,left(ui(sns,i)));
       const oldLe=cases(dis,M(i,n),E(i,n),m=>orRight(E(i,n),m),eq=>orLeft(eq,M(i,n)));
       const oldDom=mp(oldLe,right(mp(mi,ui(dg,i))));
       return witness(oldDom,v,hv=>exIntro(dom(U,i),v,conj(left(hv),oldInto(i,v,right(hv)))))
     });
     const domainProof=move(generalize(i,abs(mi,conj(abs(du,forward),abs(hi,backward)))),domain(U,s));
     const prefix=exIntro(prefixDomain(U),s,conj(ms,domainProof));
     // The appended input is a successor, so it cannot be an empty set.
     const bh=[empty(i),nat(i),nat(c),at(U,i,c)].map(hyp);
     const baseDis=mp(bh[3],left(relAt(i,c)));
     const nsMember=mp(orRight(M(n,n),refl(n)),right(ui(sns,n)));
     const baseValue=cases(baseDis,at(G,i,c),A(E(i,s),E(c,b)),old=>apply(inst(oldBase,i,c),bh[0],bh[1],bh[2],old),eqs=>{
       const ni=replace(nsMember,symmetric(left(eqs)),M(n,mark),mark);
       return explode(ni,ui(bh[0],n),E(c,d.C0))
     });
     const baseProof=move(allP([i,c],bh.reduceRight((r,h)=>abs(h,r),baseValue)),base(U));
     // Check all four old/new combinations in the successor recurrence.
     const sh=[nat(i),nat(j),nat(c),nat(e),succ(i,j),at(U,i,c),at(U,j,e)].map(hyp);
     const [mii,mjj,mcc,mee,sij,uic,uje]=sh;
     const di=mp(uic,left(relAt(i,c))),dj=mp(uje,left(relAt(j,e))),out=mul(j,c,e);
     const stepValue=cases(di,at(G,i,c),A(E(i,s),E(c,b)),oldi=>{
       return cases(dj,at(G,j,e),A(E(j,s),E(e,b)),oldj=>apply(inst(oldStep,i,j,c,e),mii,mjj,mcc,mee,sij,oldi,oldj),eqj=>{
         const sis=replace(sij,left(eqj),succ(i,mark),mark);
         const same=ctx.succInjectAt(om,i,n,s,mii,mn,sis,sns);
         const gnc=replace(oldi,same,at(G,mark,c),mark);
         const ca=apply(inst(oldFunc,n,c,a),mn,mcc,ma,gnc,ga);
         let value=replace(next,symmetric(ca),mul(s,mark,b),mark);
         value=replace(value,symmetric(right(eqj)),mul(s,c,mark),mark);
         return replace(value,symmetric(left(eqj)),mul(mark,c,e),mark)
       })
     },eqi=>{
       return cases(dj,at(G,j,e),A(E(j,s),E(e,b)),oldj=>{
         const ord=oldOrder(j,e,mjj,mee,oldj);
         const inn=ctx.down(om,n,mn,i,j,sij,ord);
         const sn=replace(inn,left(eqi),M(mark,n),mark);
         return explode(orRight(E(s,n),sn),fresh,out)
       },eqj=>{
         const ij=mp(orRight(M(i,i),refl(i)),right(ui(sij,i)));
         let ss=replace(ij,left(eqi),M(mark,j),mark);
         ss=replace(ss,left(eqj),M(s,mark),mark);
         const dis=mp(ss,left(ui(sns,s)));
         const oldLe=cases(dis,M(s,n),E(s,n),mem=>orRight(E(s,n),mem),eq=>orLeft(eq,M(s,n)));
         return explode(oldLe,fresh,out)
       })
     });
     const stepProof=move(allP([i,j,c,e],sh.reduceRight((r,h)=>abs(h,r),stepValue)),step(U));
     const goodProof=nest(prefix,newFunc,baseProof,stepProof);
     assert(goodProof.f===good(U),'literal Good extension');
     return exIntro(goal,U,nest(bounded,goodProof,domainProof,rel))
   })
 });
 assert(ns[result.f].y===goal,'extension conclusion');
 const run=()=>{
   const out=ctx.get('bounded_exact_good_prefix_extension',result);
   return [{...out,receipt:{...out.receipt,good_predicate_bytes:ns[good(0)].u,ordinal_lemmas_derived_from_omega:true,omega_is_explicit_premise:true,full_good_extension:true,actual_rh_proof:false}}]
 };
 return {ctx,predicates:d,result,premises,goal,run,good_predicate:kernel.encode(ar.ast(good(0))),famSpec:kernel.encode(ar.ast(d.famSpec(Q,53))),good_instances:[{graph:G,omega:37},{graph:U,omega:37}]};
}
export const prefixExtension={prepare};
if(typeof process!=='undefined'&&process.argv[1]?.endsWith('/prefix_extension.mjs')){
 const {readFileSync}=await import('node:fs');
 const raw=readFileSync(new URL('./rh_target.txt',import.meta.url),'utf8');
 console.log(JSON.stringify(prefixExtension.prepare(raw).run().map(x=>x.receipt),null,2));
}
